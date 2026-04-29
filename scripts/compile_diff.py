#!/usr/bin/env python3
"""
Git 变更增量编译脚本

功能:
1. 检测 git diff 中的 curated 文件变更
2. 只编译新增或修改的文件
3. 自动更新知识图谱

用法:
  python3 scripts/compile_diff.py [--since=<commit>] [--staged]

参数:
  --since    从指定 commit 开始检测变更 (默认: HEAD~1)
  --staged   只检测已 staged 的变更
  --all      检测所有变更（包括未 staged）
"""

import subprocess
import json
import hashlib
import os
import sys
from pathlib import Path
from datetime import datetime
from argparse import ArgumentParser

BASE_DIR = Path(__file__).parent.parent
CURATED_DIR = BASE_DIR / "curated"
WIKI_DIR = BASE_DIR / "wiki"
GRAPH_DIR = BASE_DIR / "graph"

# 支持编译的文件类型
COMPILE_EXTENSIONS = {".md"}

# 不编译的目录
SKIP_DIRS = {"raw", ".claude", "scripts"}


def run_git_command(cmd):
    """执行 git 命令"""
    try:
        result = subprocess.run(
            cmd,
            cwd=BASE_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Git 命令失败: {e.stderr}")
        return ""


def get_changed_files(since=None, staged=False, all_changes=False):
    """获取变更的文件列表"""

    if staged:
        # 只检测 staged 的变更
        cmd = ["git", "diff", "--cached", "--name-only"]
    elif all_changes:
        # 检测所有变更（包括未 staged）
        cmd = ["git", "diff", "HEAD", "--name-only"]
        # 加上新增未 tracked 的文件
        untracked = run_git_command(["git", "ls-files", "--others", "--exclude-standard"])
        tracked = run_git_command(cmd)
        all_files = tracked + "\n" + untracked
        return [f for f in all_files.split("\n") if f]
    else:
        # 从指定 commit 开始
        since_ref = since or "HEAD~1"
        cmd = ["git", "diff", since_ref, "--name-only"]

    output = run_git_command(cmd)
    return [f for f in output.split("\n") if f]


def filter_curated_files(files):
    """筛选出 curated 目录下的可编译文件"""

    curated_files = []

    for file in files:
        path = Path(file)

        # 检查是否在 curated 目录
        if not file.startswith("curated/"):
            continue

        # 检查扩展名
        if path.suffix not in COMPILE_EXTENSIONS:
            continue

        # 检查是否在跳过目录
        if any(skip in file for skip in SKIP_DIRS):
            continue

        curated_files.append(file)

    return curated_files


def get_file_hash(filepath):
    """计算文件 hash"""
    full_path = BASE_DIR / filepath
    if not full_path.exists():
        return None
    return hashlib.sha256(open(full_path, 'rb').read()).hexdigest()


def get_cached_hash(node_id):
    """从 nodes.jsonl 获取缓存的 hash"""
    nodes_file = GRAPH_DIR / "nodes.jsonl"
    if not nodes_file.exists():
        return None

    with open(nodes_file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            try:
                node = json.loads(line)
                if node.get("id") == node_id:
                    return node.get("source_hash")
            except:
                continue
    return None


def needs_compile(source_file):
    """检查文件是否需要编译"""
    source_path = Path(source_file)
    node_id = source_file.replace("curated/", "").replace(".md", "")

    # 文件不存在（被删除），跳过
    if not (BASE_DIR / source_file).exists():
        return False, "deleted"

    # 检查缓存
    cached_hash = get_cached_hash(node_id)
    current_hash = get_file_hash(source_file)

    if cached_hash and current_hash and cached_hash == current_hash:
        return False, "unchanged"

    return True, "changed"


def compile_file(source_file):
    """编译单个文件（调用 LLM）"""

    source_path = BASE_DIR / source_file
    if not source_path.exists():
        return {"status": "failed", "reason": "文件不存在"}

    # 确定目标路径
    relative = source_file.replace("curated/", "").replace(".md", "")
    target_path = WIKI_DIR / f"{relative}.md"
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # 这里需要调用 LLM 编译
    # 简化版：直接复制 + 添加 frontmatter
    content = source_path.read_text()
    source_hash = get_file_hash(source_file)

    frontmatter = f"""---
id: {relative}
source: {source_file}
source_hash: {source_hash}
compiled: {datetime.now().isoformat()}
status: needs_llm_compile
---

"""

    target_path.write_text(frontmatter + content)

    return {
        "status": "queued",
        "source": source_file,
        "target": str(target_path.relative_to(BASE_DIR)),
        "hash": source_hash
    }


def update_graph(source_file, result):
    """更新知识图谱"""

    node_id = source_file.replace("curated/", "").replace(".md", "")

    # 更新 nodes.jsonl
    nodes_file = GRAPH_DIR / "nodes.jsonl"
    existing_nodes = []

    with open(nodes_file) as f:
        for line in f:
            if line.startswith("#"):
                continue
            try:
                node = json.loads(line)
                if node.get("id") != node_id:
                    existing_nodes.append(node)
            except:
                continue

    # 添加新节点
    new_node = {
        "id": node_id,
        "path": str(result["target"]),
        "source": source_file,
        "source_hash": result["hash"],
        "compiled": datetime.now().isoformat(),
        "status": "pending_llm"
    }
    existing_nodes.append(new_node)

    # 写回 nodes.jsonl
    with open(nodes_file, "w") as f:
        f.write(f"# nodes.jsonl - 节点索引\n")
        f.write(f"# 更新: {datetime.now().isoformat()}\n")
        f.write("#\n")
        for node in existing_nodes:
            f.write(json.dumps(node, ensure_ascii=False) + "\n")

    return True


def main():
    parser = ArgumentParser(description="Git 变更增量编译")
    parser.add_argument("--since", help="从指定 commit 开始检测")
    parser.add_argument("--staged", action="store_true", help="只检测 staged 变更")
    parser.add_argument("--all", action="store_true", help="检测所有变更")

    args = parser.parse_args()

    print("=== Git 变更增量编译 ===\n")

    # Step 1: 获取变更文件
    print("Step 1: 检测变更文件...")
    since = args.since
    staged = args.staged
    all_changes = args.all

    if since:
        print(f"  检测范围: {since} → HEAD")
    elif staged:
        print("  检测范围: staged 变更")
    elif all_changes:
        print("  检测范围: 所有变更")
    else:
        print("  检测范围: HEAD~1 → HEAD (默认)")

    changed_files = get_changed_files(since, staged, all_changes)
    print(f"  变更文件总数: {len(changed_files)}")

    # Step 2: 筛选 curated 文件
    print("\nStep 2: 筛选可编译文件...")
    curated_files = filter_curated_files(changed_files)
    print(f"  curated 变更: {len(curated_files)}")

    if not curated_files:
        print("\n无需要编译的文件")
        return

    for f in curated_files:
        print(f"  - {f}")

    # Step 3: 检查是否需要编译
    print("\nStep 3: 检查编译需求...")
    to_compile = []

    for f in curated_files:
        need, reason = needs_compile(f)
        if need:
            to_compile.append(f)
            print(f"  ✓ {f} ({reason})")
        else:
            print(f"  - {f} ({reason}, 跳过)")

    if not to_compile:
        print("\n所有文件已编译，无需更新")
        return

    # Step 4: 编译文件
    print(f"\nStep 4: 编译 {len(to_compile)} 个文件...")
    results = []

    for f in to_compile:
        result = compile_file(f)
        results.append(result)

        if result["status"] == "queued":
            print(f"  ✓ {f} → {result['target']}")
            update_graph(f, result)
        else:
            print(f"  ✗ {f} ({result.get('reason', '未知')})")

    # Step 5: 输出报告
    print("\n=== 编译完成 ===")
    print(f"变更文件: {len(changed_files)}")
    print(f"待编译: {len(curated_files)}")
    print(f"已处理: {len(to_compile)}")

    print("\n下一步:")
    print("  1. 在对话中说 '编译这些新文件'")
    print("  2. 或运行: python3 scripts/compile.py --files=<文件列表>")

    # 输出待编译列表（供后续调用）
    pending_file = BASE_DIR / ".compile-pending.json"
    pending = {
        "timestamp": datetime.now().isoformat(),
        "files": to_compile,
        "results": results
    }
    with open(pending_file, "w") as f:
        json.dump(pending, f, indent=2, ensure_ascii=False)

    print(f"\n待编译列表: {pending_file}")


if __name__ == "__main__":
    main()