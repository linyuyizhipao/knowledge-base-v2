#!/usr/bin/env python3
"""
diff-impact.py - 代码变更影响分析

追踪代码变更的传播路径，找出需要重启的服务。
只负责识别受影响的服务，不涉及 deploy 操作。

用法：python scripts/diff-impact.py
"""

import re
import json
import subprocess
from pathlib import Path
from collections import deque


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
        self._grep_cache = {}
        self._file_info_cache = {}
        self._service_cache = {}

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

        self.changed_files = self._get_changed_files()
        if not self.changed_files:
            return self._output_success()

        print("🔍 分析变更文件...", file=__import__('sys').stderr)
        self.changed_elements = self._extract_changed_elements()

        print("🔍 追踪引用传播...", file=__import__('sys').stderr)
        self._trace_all_elements()

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
        full_path = self.project_root / file_path
        if not full_path.exists():
            return None
        try:
            return full_path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return None

    def _parse_file_info(self, file_path):
        if file_path in self._file_info_cache:
            return self._file_info_cache[file_path]

        content = self._read_file(file_path)
        if not content:
            return None

        pkg_match = re.search(r'package\s+(\w+)', content)
        package_name = pkg_match.group(1) if pkg_match else Path(file_path).parent.name

        import_aliases = {}
        for m in re.finditer(r'(\w+)\s+"([^"]+)"', content):
            import_aliases[m.group(1)] = m.group(2)
        import_block = re.search(r'import\s*\(([^)]+)\)', content)
        if import_block:
            for m in re.finditer(r'(\w+)\s+"([^"]+)"', import_block.group(1)):
                import_aliases[m.group(1)] = m.group(2)
            for m in re.finditer(r'"([^"]+)"', import_block.group(1)):
                path = m.group(1)
                alias = path.split('/')[-1]
                import_aliases[alias] = path

        functions = re.findall(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', content)

        info = {"package_name": package_name, "import_aliases": import_aliases, "functions": functions}
        self._file_info_cache[file_path] = info
        return info

    def _get_service_from_file(self, file_path):
        if file_path in self._service_cache:
            return self._service_cache[file_path]

        if "app/api/" in file_path or "app/handler/" in file_path:
            result = ("http", None)
        elif "rpc/server/internal/" in file_path:
            m = re.search(r'rpc/server/internal/([^/]+)/', file_path)
            if m:
                result = ("rpc", m.group(1))
            else:
                m2 = re.search(r'rpc/server/internal/(\w+)\.go$', file_path)
                if m2:
                    result = ("rpc", m2.group(1))
                else:
                    result = (None, None)
        elif "cmd/internal/" in file_path:
            m = re.search(r'cmd/internal/([^/]+)/', file_path)
            if m:
                result = ("cmd", m.group(1))
            else:
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

        支持两种形式：
        - 直接调用：obj.MethodName(args)
        - 函数引用：callback(obj.MethodName)  ← cron 回调等场景
        """
        call_pattern = f"\\.{method_name}\\b"
        all_callers = self._grep_pattern(call_pattern)

        result_files = set()
        for file_path in all_callers:
            info = self._parse_file_info(file_path)
            if not info:
                continue

            import_aliases = info.get("import_aliases", {})
            pkg_path = self._get_package_path_from_file(changed_file)

            for alias, import_path in import_aliases.items():
                if import_path == pkg_path or import_path.endswith(f"/{pkg}"):
                    content = self._read_file(file_path)
                    if content and re.search(rf'\.{method_name}\b', content):
                        rpc_client_pattern = rf'client\.\w+\.{method_name}\b'
                        if not re.search(rpc_client_pattern, content):
                            result_files.add(file_path)
                        break

        return result_files

    def _get_package_path_from_file(self, file_path):
        parts = Path(file_path).parts
        for i, part in enumerate(parts):
            if part in ["app", "rpc", "cmd", "library"]:
                return f"{self.module_name}/{Path(*parts[i:-1])}"
        return None

    def _grep_pattern(self, pattern, dirs=["app", "rpc", "cmd"]):
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
        elements = []
        private_funcs = []

        for file_path in self.changed_files:
            info = self._parse_file_info(file_path)
            if not info:
                continue

            package_name = info["package_name"]
            changed_funcs = self._get_changed_functions_from_diff(file_path)

            for func_name in changed_funcs:
                if func_name[0].isupper():
                    elements.append({"name": func_name, "type": "func", "file": file_path, "package": package_name})
                else:
                    private_funcs.append({"name": func_name, "file": file_path, "package": package_name})

            changed_consts, changed_vars = self._get_changed_vars_consts_from_diff(file_path)
            for name in changed_consts:
                if name[0].isupper():
                    elements.append({"name": name, "type": "const", "file": file_path, "package": package_name})
            for name in changed_vars:
                if name[0].isupper():
                    elements.append({"name": name, "type": "var", "file": file_path, "package": package_name})

        for private_func in private_funcs:
            caller_elements = self._find_public_callers_via_private_chain(private_func)
            for caller in caller_elements:
                if caller not in elements:
                    elements.append(caller)

        print(f"   变更元素: {len(elements)} 个（从 diff 精确提取）", file=__import__('sys').stderr)
        return elements

    def _get_changed_functions_from_diff(self, file_path):
        result = subprocess.run(
            ["git", "diff", "master", "--no-color", "-U0", file_path],
            capture_output=True, text=True, cwd=self.project_root
        )
        diff_content = result.stdout

        if not diff_content:
            return set()

        changed_funcs = set()
        content = self._read_file(file_path) or ""

        current_line = 0
        for line in diff_content.split('\n'):
            if line.startswith('@@'):
                m = re.search(r'\+(\d+)', line)
                if m:
                    current_line = int(m.group(1))
            elif line.startswith('+') and not line.startswith('+++'):
                func_name = self._find_function_at_line(content, current_line)
                if func_name:
                    changed_funcs.add(func_name)
                current_line += 1
            elif not line.startswith('-') and not line.startswith('@@'):
                current_line += 1

        return changed_funcs

    def _find_function_at_line(self, content, target_line):
        lines = content.split('\n')
        current_func = None
        func_start_line = 0

        for i, line in enumerate(lines, 1):
            m = re.match(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', line)
            if m:
                current_func = m.group(1)
                func_start_line = i

            if current_func and i >= func_start_line:
                if i == target_line:
                    return current_func

                next_m = re.match(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', line)
                if next_m and i > func_start_line:
                    current_func = next_m.group(1)
                    func_start_line = i

        return None

    def _get_changed_vars_consts_from_diff(self, file_path):
        result = subprocess.run(
            ["git", "diff", "master", "--no-color", "-U0", file_path],
            capture_output=True, text=True, cwd=self.project_root
        )
        diff_content = result.stdout

        if not diff_content:
            return set(), set()

        changed_consts = set()
        changed_vars = set()

        for line in diff_content.split('\n'):
            if line.startswith('+') and not line.startswith('+++'):
                m = re.match(r'^\+\s*const\s+(\w+)\s*=', line)
                if m:
                    changed_consts.add(m.group(1))
                m = re.match(r'^\+\s*var\s+(\w+)\s*[=\s]', line)
                if m:
                    changed_vars.add(m.group(1))
                m = re.match(r'^\+\s+(\w+)\s*=\s*', line)
                if m and m.group(1)[0].isupper():
                    changed_consts.add(m.group(1))

        return changed_consts, changed_vars

    def _extract_func_body(self, content, func_start_pos):
        """用大括号计数提取函数体，支持任意嵌套深度"""
        brace_pos = content.find('{', func_start_pos)
        if brace_pos == -1:
            return None
        depth = 0
        for i in range(brace_pos, len(content)):
            if content[i] == '{':
                depth += 1
            elif content[i] == '}':
                depth -= 1
                if depth == 0:
                    return content[brace_pos+1:i]
        return None

    def _find_public_callers_in_same_package(self, private_func):
        pkg = private_func["package"]
        func_name = private_func["name"]
        file_path = private_func["file"]

        pkg_dir = self.project_root / Path(file_path).parent
        pkg_files = list(pkg_dir.glob("*.go"))

        callers = []
        for f in pkg_files:
            if "_test.go" in f.name or ".pb.go" in f.name:
                continue
            content = f.read_text(encoding='utf-8', errors='ignore')

            if func_name not in content:
                continue

            for m in re.finditer(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', content):
                func_def_name = m.group(1)
                if not func_def_name[0].isupper():
                    continue

                func_body = self._extract_func_body(content, m.end())
                if func_body and (f"{func_name}(" in func_body or f"{func_name} " in func_body):
                    rel_path = str(f.relative_to(self.project_root))
                    callers.append({
                        "name": func_def_name,
                        "type": "func",
                        "file": rel_path,
                        "package": pkg
                    })

        return callers

    def _find_public_callers_via_private_chain(self, private_func):
        """通过私有函数传播链追踪到公开函数

        例如: broadcastFeedSuccess(私有) → recordFeedSideEffects(私有) → applyFeed(私有) → OnGiftSend(公开)
        使用 BFS 在同包内追踪私有调用链，直到找到公开函数。
        """
        pkg = private_func["package"]
        func_name = private_func["name"]
        file_path = private_func["file"]
        pkg_dir = self.project_root / Path(file_path).parent

        # 预加载同包所有文件内容
        pkg_files = []
        for f in pkg_dir.glob("*.go"):
            if "_test.go" in f.name or ".pb.go" in f.name:
                continue
            content = f.read_text(encoding='utf-8', errors='ignore')
            pkg_files.append((f, content))

        # BFS: 从变更的私有函数出发，追踪私有→私有→...→公开
        visited_private = {func_name}
        queue = deque([func_name])
        public_callers = []

        while queue:
            current_name = queue.popleft()

            for f, content in pkg_files:
                if current_name not in content:
                    continue

                for m in re.finditer(r'func\s+(?:\([^)]*\)\s+)?(\w+)\s*\(', content):
                    caller_name = m.group(1)
                    func_body = self._extract_func_body(content, m.end())
                    if not func_body:
                        continue
                    if f"{current_name}(" not in func_body and f"{current_name} " not in func_body:
                        continue

                    # 调用者是公开函数 → 记录
                    if caller_name[0].isupper():
                        rel_path = str(f.relative_to(self.project_root))
                        elem = {"name": caller_name, "type": "func", "file": rel_path, "package": pkg}
                        if elem not in public_callers:
                            public_callers.append(elem)
                    else:
                        # 调用者是私有函数 → 继续传播
                        if caller_name not in visited_private:
                            visited_private.add(caller_name)
                            queue.append(caller_name)

        return public_callers

    def _trace_all_elements(self):
        global_visited = set()

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

        for element in self.changed_elements:
            pkg_name = element.get("package", "")
            self._bfs_trace(element["name"], pkg_name, element["file"], global_visited)

    def _bfs_trace(self, start_element, start_pkg, start_file, global_visited):
        full_key = f"{start_pkg}.{start_element}" if start_pkg else start_element
        if full_key in global_visited:
            return

        queue = deque([(start_element, start_pkg, start_file, [full_key])])
        global_visited.add(full_key)

        while queue:
            current, pkg, cur_file, path = queue.popleft()

            if len(path) > self.max_depth:
                continue

            if pkg:
                pattern = f"{pkg}\\.{current}\\(|{pkg}\\.{current}\\b"
            else:
                pattern = current

            ref_files = self._grep_pattern(pattern)

            if pkg and current[0].isupper():
                instance_callers = self._find_instance_callers(pkg, current, cur_file)
                ref_files = ref_files | instance_callers

            for ref_file in ref_files:
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

                if service_type in [None, "library"]:
                    info = self._parse_file_info(ref_file)
                    if info:
                        ref_pkg = info["package_name"]
                        for func_name in info["functions"]:
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
