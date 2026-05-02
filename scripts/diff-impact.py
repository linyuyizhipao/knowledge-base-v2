#!/usr/bin/env python3
"""
diff-impact.py - 代码变更影响分析（高性能版 v2）

核心优化：
1. 不预构建全项目索引，改为按需搜索 + 结果缓存
2. 只追踪变更元素，逐步展开
3. 遇到服务入口立即停止，不继续传播

用法：python scripts/diff-impact.py
"""

import os
import re
import json
import subprocess
from pathlib import Path
from collections import defaultdict, deque


class DiffImpactAnalyzer:
    def __init__(self):
        self.module_name = None
        self.project_root = None
        self.max_depth = 50

        # 结果
        self.changed_files = []
        self.changed_elements = []
        self.affected_services = {"http": False, "rpc": [], "cmd": [], "library": False}
        self.circular_references = []

        # 按需缓存（不预构建）
        self._grep_cache = {}  # pattern -> [files]
        self._file_info_cache = {}  # file_path -> {package, imports, functions}
        self._service_cache = {}  # file_path -> (type, name)

    def run(self):
        """主入口"""
        if not self._check_git_repo():
            return self._output_error("当前目录不是 Git 仓库")

        current_branch = self._get_current_branch()
        if current_branch == "master":
            return self._output_error("当前在 master，无法对比")

        self.module_name = self._parse_go_mod()
        if not self.module_name:
            return self._output_error("无法解析 go.mod")

        self.project_root = Path.cwd()

        # 获取变更文件
        self.changed_files = self._get_changed_files()
        if not self.changed_files:
            return self._output_success()

        # 提取变更元素
        print("🔍 分析变更文件...", file=__import__('sys').stderr)
        self.changed_elements = self._extract_changed_elements()

        # BFS 追踪（按需搜索，不预构建）
        print("🔍 追踪引用传播...", file=__import__('sys').stderr)
        self._trace_all_elements()

        # 生成重启命令
        restart_commands = self._generate_restart_commands()

        return self._output_result(current_branch, restart_commands)

    def _check_git_repo(self):
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _get_current_branch(self):
        result = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True)
        return result.stdout.strip()

    def _parse_go_mod(self):
        go_mod = Path("go.mod")
        if not go_mod.exists():
            return None
        with open(go_mod) as f:
            for line in f:
                if line.startswith("module "):
                    return line.split("module ")[1].strip()
        return None

    def _get_changed_files(self):
        result = subprocess.run(
            ["git", "diff", "master", "--name-only", "--diff-filter=ACM"],
            capture_output=True, text=True
        )
        files = []
        for line in result.stdout.strip().split("\n"):
            if line and line.endswith(".go") and "_test.go" not in line and ".pb.go" not in line:
                files.append(line)
        return files

    def _read_file(self, file_path):
        """读取文件内容"""
        full_path = self.project_root / file_path
        if not full_path.exists():
            return None
        try:
            return full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return None

    def _parse_file_info(self, file_path):
        """解析单个文件信息（带缓存）"""
        if file_path in self._file_info_cache:
            return self._file_info_cache[file_path]

        content = self._read_file(file_path)
        if not content:
            return None

        # package 名
        pkg_match = re.search(r'package\s+(\w+)', content)
        package_name = pkg_match.group(1) if pkg_match else Path(file_path).parent.name

        # imports（提取别名）
        import_aliases = {}
        # 单行 import
        for m in re.finditer(r'(\w+)\s+"([^"]+)"', content):
            import_aliases[m.group(1)] = m.group(2)
        # 多行 import
        import_block = re.search(r'import\s*\(([^)]+)\)', content)
        if import_block:
            for m in re.finditer(r'(\w+)\s+"([^"]+)"', import_block.group(1)):
                import_aliases[m.group(1)] = m.group(2)
            for m in re.finditer(r'"([^"]+)"', import_block.group(1)):
                path = m.group(1)
                alias = path.split('/')[-1]
                import_aliases[alias] = path

        # 函数定义（包括方法）
        functions = re.findall(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', content)

        # 缓存（不存 content，节省内存）
        info = {"package_name": package_name, "import_aliases": import_aliases, "functions": functions}
        self._file_info_cache[file_path] = info
        return info

    def _get_service_from_file(self, file_path):
        """获取服务归属（带缓存）"""
        if file_path in self._service_cache:
            return self._service_cache[file_path]

        if "app/api/" in file_path or "app/handler/" in file_path:
            result = ("http", None)
        elif "rpc/server/internal/" in file_path:
            # 两种情况：
            # 1. rpc/server/internal/user.go → 入口文件，服务名从文件名提取
            # 2. rpc/server/internal/user/xxx.go → 服务实现，服务名从目录名提取
            m = re.search(r'rpc/server/internal/([^/]+)/', file_path)
            if m:
                result = ("rpc", m.group(1))
            else:
                # 入口文件：rpc/server/internal/user.go
                m2 = re.search(r'rpc/server/internal/(\w+)\.go$', file_path)
                if m2:
                    result = ("rpc", m2.group(1))
                else:
                    result = (None, None)
        elif "cmd/internal/" in file_path:
            # 两种情况：
            # 1. cmd/internal/anchor.go → 入口文件
            # 2. cmd/internal/anchor/xxx.go → 服务实现
            m = re.search(r'cmd/internal/([^/]+)/', file_path)
            if m:
                result = ("cmd", m.group(1))
            else:
                # 入口文件：cmd/internal/anchor.go
                m2 = re.search(r'cmd/internal/(\w+)\.go$', file_path)
                if m2:
                    result = ("cmd", m2.group(1))
                else:
                    result = (None, None)
        elif "library/" in file_path or "app/consts/" in file_path or "app/dao/" in file_path:
            result = ("library", None)
        else:
            result = (None, None)

        self._service_cache[file_path] = result
        return result

    def _find_instance_callers(self, pkg, method_name, changed_file):
        """查找通过实例调用方法的文件（如 rankScene.GetRank）

        优化策略：直接搜索 .MethodName 调用，再验证是否来自正确的包
        """
        # 直接搜索 .MethodName 调用（所有实例调用）
        call_pattern = f"\\.{method_name}\\("
        all_callers = self._grep_pattern(call_pattern)

        result_files = set()
        for file_path in all_callers:
            # 检查该文件是否导入了变更文件的包
            info = self._parse_file_info(file_path)
            if not info:
                continue

            # 检查导入别名是否指向变更包
            import_aliases = info.get("import_aliases", {})
            pkg_path = self._get_package_path_from_file(changed_file)

            # 如果导入路径匹配变更包路径，则该文件可能调用变更方法
            for alias, import_path in import_aliases.items():
                if import_path == pkg_path or import_path.endswith(f"/{pkg}"):
                    # 该文件导入了变更包，可能是实例调用者
                    # 验证是否真的有 varName.MethodName 模式
                    content = self._read_file(file_path)
                    if content and f".{method_name}(" in content:
                        # 检查是否有从该包获取对象的模式
                        if re.search(rf'{pkg}\.\w+', content):
                            result_files.add(file_path)
                            break

        return result_files

    def _get_package_path_from_file(self, file_path):
        """从文件路径推导包的导入路径"""
        # 例如: app/domain/rank/base.go → slp/app/domain/rank
        parts = Path(file_path).parts
        # 找到 app/rpc/cmd 的位置
        for i, part in enumerate(parts):
            if part in ["app", "rpc", "cmd", "library"]:
                # 组合模块名 + 后续路径
                return f"{self.module_name}/{Path(*parts[i:-1])}"
        return None

    def _grep_pattern(self, pattern, dirs=["app", "rpc", "cmd"]):
        """grep 搜索（带缓存）"""
        cache_key = pattern
        if cache_key in self._grep_cache:
            return self._grep_cache[cache_key]

        files = set()
        for dir_name in dirs:
            dir_path = self.project_root / dir_name
            if not dir_path.exists():
                continue
            try:
                result = subprocess.run(
                    ["grep", "-r", "-l", "-E", "-I", "--include=*.go", pattern, dir_name],
                    capture_output=True, text=True, cwd=self.project_root, timeout=5
                )
                for line in result.stdout.strip().split("\n"):
                    if line and "_test.go" not in line and ".pb.go" not in line:
                        files.add(line)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                continue

        self._grep_cache[cache_key] = files
        return files

    def _extract_changed_elements(self):
        """提取变更元素，并处理私有函数的传播"""
        elements = []
        private_funcs = []

        for file_path in self.changed_files:
            info = self._parse_file_info(file_path)
            if not info:
                continue

            package_name = info["package_name"]
            content = self._read_file(file_path) or ""

            # 分类：公开函数 vs 私有函数
            for name in info["functions"]:
                if name[0].isupper():  # Go 公开函数首字母大写
                    elements.append({"name": name, "type": "func", "file": file_path, "package": package_name})
                else:
                    private_funcs.append({"name": name, "file": file_path, "package": package_name})

            # 变量/常量（只追踪公开的）
            consts = re.findall(r'^const\s+(\w+)\s*=', content, re.MULTILINE)
            vars_ = re.findall(r'^var\s+(\w+)\s*[=\s]', content, re.MULTILINE)
            for name in consts:
                if name[0].isupper():
                    elements.append({"name": name, "type": "const", "file": file_path, "package": package_name})
            for name in vars_:
                if name[0].isupper():
                    elements.append({"name": name, "type": "var", "file": file_path, "package": package_name})

        # 处理私有函数：找同包内调用它的公开函数
        for private_func in private_funcs:
            caller_elements = self._find_public_callers_in_same_package(private_func)
            for caller in caller_elements:
                if caller not in elements:
                    elements.append(caller)

        print(f"   公开元素: {len(elements)} 个（含私有函数传播）", file=__import__('sys').stderr)
        return elements

    def _find_public_callers_in_same_package(self, private_func):
        """找到同包内调用私有函数的公开函数"""
        pkg = private_func["package"]
        func_name = private_func["name"]
        file_path = private_func["file"]

        # 获取包内所有文件（使用绝对路径）
        pkg_dir = self.project_root / Path(file_path).parent
        pkg_files = list(pkg_dir.glob("*.go"))

        callers = []
        for f in pkg_files:
            if "_test.go" in f.name or ".pb.go" in f.name:
                continue
            content = f.read_text(encoding='utf-8', errors='ignore')

            # 检查是否调用了该私有函数
            if func_name not in content:
                continue

            # 提取公开函数定义
            for m in re.finditer(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', content):
                func_def_name = m.group(1)
                if not func_def_name[0].isupper():
                    continue  # 只找公开函数

                # 检查该公开函数是否调用了私有函数
                func_start = m.end()
                func_body_match = re.search(r'\{([^}]*(?:\{[^}]*\}[^}]*)*)\}', content[func_start:])
                if func_body_match:
                    func_body = func_body_match.group(1)
                    if f"{func_name}(" in func_body or f"{func_name} " in func_body:
                        rel_path = str(f.relative_to(self.project_root))
                        callers.append({
                            "name": func_def_name,
                            "type": "func",
                            "file": rel_path,
                            "package": pkg
                        })

        return callers

    def _trace_all_elements(self):
        """BFS 追踪所有变更元素"""
        global_visited = set()

        # 先处理所有变更文件的服务归属（即使没有公开元素）
        for file_path in self.changed_files:
            service_type, service_name = self._get_service_from_file(file_path)
            if service_type == "http":
                self.affected_services["http"] = True
            elif service_type == "rpc" and service_name:
                if service_name not in self.affected_services["rpc"]:
                    self.affected_services["rpc"].append(service_name)
            elif service_type == "cmd" and service_name:
                if service_name not in self.affected_services["cmd"]:
                    self.affected_services["cmd"].append(service_name)

        # 再追踪公开元素的引用传播
        for element in self.changed_elements:
            pkg_name = element.get("package", "")
            self._bfs_trace(element["name"], pkg_name, element["file"], global_visited)

    def _bfs_trace(self, start_element, start_pkg, start_file, global_visited):
        """BFS 追踪（按需搜索）"""
        full_key = f"{start_pkg}.{start_element}" if start_pkg else start_element
        if full_key in global_visited:
            return

        queue = deque([(start_element, start_pkg, start_file, [full_key])])
        global_visited.add(full_key)

        while queue:
            current, pkg, cur_file, path = queue.popleft()

            if len(path) > self.max_depth:
                continue

            # 搜索引用（带包名前缀）
            if pkg:
                pattern = f"{pkg}\\.{current}"
            else:
                pattern = current

            ref_files = self._grep_pattern(pattern)

            # 对于方法，还要搜索实例调用（如 rankScene.GetRank）
            if pkg and current[0].isupper():
                instance_callers = self._find_instance_callers(pkg, current, cur_file)
                ref_files = ref_files | instance_callers

            for ref_file in ref_files:
                # 获取服务归属
                service_type, service_name = self._get_service_from_file(ref_file)

                if service_type == "http":
                    self.affected_services["http"] = True
                    continue
                elif service_type == "rpc" and service_name:
                    if service_name not in self.affected_services["rpc"]:
                        self.affected_services["rpc"].append(service_name)
                    continue
                elif service_type == "cmd" and service_name:
                    if service_name not in self.affected_services["cmd"]:
                        self.affected_services["cmd"].append(service_name)
                    continue

                # 非服务入口，继续追踪该文件的函数（只追踪公开函数）
                if service_type in [None, "library"]:
                    info = self._parse_file_info(ref_file)
                    if info:
                        ref_pkg = info["package_name"]
                        for func_name in info["functions"]:
                            # 只追踪公开函数（首字母大写）
                            if not func_name[0].isupper():
                                continue
                            func_key = f"{ref_pkg}.{func_name}"
                            if func_key in path:
                                cycle = " → ".join(path + [func_key])
                                if cycle not in self.circular_references:
                                    self.circular_references.append(cycle)
                                continue
                            if func_key not in global_visited:
                                global_visited.add(func_key)
                                queue.append((func_name, ref_pkg, ref_file, path + [func_key]))

    def _generate_restart_commands(self):
        commands = []
        if self.affected_services["http"]:
            commands.append("make build && ./bin/http")
        for name in sorted(self.affected_services["rpc"]):
            commands.append(f"make build && ./bin/rpc --name={name}")
        for name in sorted(self.affected_services["cmd"]):
            commands.append(f"make build && ./bin/cmd --name={name}")
        if self.affected_services["library"] and not commands:
            commands.append("make build && # Library 变更影响全部服务")
        return commands

    def _output_error(self, msg):
        return json.dumps({"error": msg}, ensure_ascii=False, indent=2)

    def _output_success(self):
        return json.dumps({
            "current_branch": self._get_current_branch(),
            "base_branch": "master",
            "module_name": self.module_name,
            "changed_files": [],
            "changed_elements": [],
            "affected_services": {"http": False, "rpc": [], "cmd": [], "library": False},
            "circular_references": [],
            "restart_commands": []
        }, ensure_ascii=False, indent=2)

    def _output_result(self, branch, commands):
        return json.dumps({
            "current_branch": branch,
            "base_branch": "master",
            "module_name": self.module_name,
            "changed_files": self.changed_files,
            "changed_elements": self.changed_elements,
            "affected_services": self.affected_services,
            "circular_references": self.circular_references,
            "restart_commands": commands
        }, ensure_ascii=False, indent=2)


def main():
    analyzer = DiffImpactAnalyzer()
    print(analyzer.run())


if __name__ == "__main__":
    main()