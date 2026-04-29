#!/usr/bin/env python3
"""
修复知识库断链问题

主要问题:
1. wikilink 带 .md 后缀 (如 [[event-extension-guide.md]] 应为 [[event-extension-guide]])
2. wikilink 目标不存在 (如 [[素材摘要]] 不存在)

修复策略:
1. 去掉 .md 后缀
2. 创建缺失的目标文件（占位页面）
3. 更新 graph/citations.jsonl
"""

import json
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
WIKI_DIR = BASE_DIR / "wiki"
GRAPH_DIR = BASE_DIR / "graph"

# 断链类型分析
BROKEN_TYPES = {
    ".md_suffix": [],      # 带 .md 后缀
    "missing_file": [],    # 目标文件不存在
    "wrong_path": []       # 路径错误
}

def find_all_wikilinks():
    """从所有 wiki 文件提取 wikilinks"""
    all_links = []

    for md_file in WIKI_DIR.rglob("*.md"):
        content = md_file.read_text()
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

        for link in links:
            all_links.append({
                "source_file": md_file,
                "source_path": str(md_file.relative_to(WIKI_DIR)),
                "link": link,
                "normalized": link.replace(".md", "").strip()
            })

    return all_links

def check_link_target(link_normalized):
    """检查链接目标是否存在"""
    # 可能的路径
    possible_paths = [
        WIKI_DIR / f"{link_normalized}.md",
        WIKI_DIR / "patterns" / f"{link_normalized}.md",
        WIKI_DIR / "core" / f"{link_normalized}.md",
        WIKI_DIR / "tools" / f"{link_normalized}.md",
        WIKI_DIR / "projects" / f"{link_normalized}.md",
        WIKI_DIR / "cross-projects" / f"{link_normalized}.md",
        WIKI_DIR / "entities" / f"{link_normalized}.md",
        WIKI_DIR / "topics" / f"{link_normalized}.md",
        WIKI_DIR / "sources" / f"{link_normalized}.md",
    ]

    for path in possible_paths:
        if path.exists():
            return path

    return None

def fix_md_suffix_issues():
    """修复带 .md 后缀的 wikilink"""
    fixed = []

    for md_file in WIKI_DIR.rglob("*.md"):
        content = md_file.read_text()

        # 替换 [[xxx.md]] → [[xxx]]
        new_content = re.sub(
            r'\[\[([^\]|]+)\.md(?:\|[^\]]+)?\]\]',
            r'[[\1]]',
            content
        )

        if new_content != content:
            md_file.write_text(new_content)
            fixed.append(str(md_file.relative_to(WIKI_DIR)))

    return fixed

def create_placeholder_pages(missing_targets):
    """为缺失的目标创建占位页面"""
    created = []

    for target in missing_targets:
        # 确定目标目录
        # 简单规则：根据名称判断
        if any(x in target.lower() for x in ["standard", "guide", "pattern", "规范", "指南"]):
            target_dir = WIKI_DIR / "patterns"
        elif any(x in target.lower() for x in ["project", "项目", "slp-"]):
            target_dir = WIKI_DIR / "projects"
        elif any(x in target.lower() for x in ["tool", "工具", "slpctl", "gh-"]):
            target_dir = WIKI_DIR / "tools"
        elif any(x in target.lower() for x in ["素材", "摘要", "source"]):
            target_dir = WIKI_DIR / "sources"
        elif any(x in target.lower() for x in ["实体", "entity"]):
            target_dir = WIKI_DIR / "entities"
        elif any(x in target.lower() for x in ["主题", "topic"]):
            target_dir = WIKI_DIR / "topics"
        else:
            target_dir = WIKI_DIR / "entities"

        target_file = target_dir / f"{target}.md"

        if not target_file.exists():
            # 创建占位页面
            placeholder = f"""---
id: {target}
type: placeholder
created: {datetime.now().isoformat()}
status: needs_content
---

# {target}

> 此页面为占位页面，需要补充内容。

## 待补充

- 内容概述
- 关键概念
- 相关链接

## 引用来源

此页面被以下文档引用：
- (待补充)
"""
            target_file.write_text(placeholder)
            created.append(str(target_file.relative_to(WIKI_DIR)))

    return created

def update_citations_jsonl():
    """更新 citations.jsonl"""
    # 重新提取 wikilinks
    citations = []

    for md_file in WIKI_DIR.rglob("*.md"):
        content = md_file.read_text()
        links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

        from_path = str(md_file.relative_to(WIKI_DIR)).replace(".md", "")

        for link in links:
            citations.append({
                "from": from_path,
                "to": link.replace(".md", "").strip(),
                "type": "wikilink",
                "weight": 0.5,
                "source_file": str(md_file.relative_to(BASE_DIR)),
                "created": datetime.now().isoformat()
            })

    # 写入 citations.jsonl
    citations_file = GRAPH_DIR / "citations.jsonl"
    with open(citations_file, "w") as f:
        f.write(f"# citations.jsonl - wikilink 引用关系\n")
        f.write(f"# 更新时间: {datetime.now().isoformat()}\n")
        f.write(f"# 总计: {len(citations)} 条\n")
        f.write("#\n")

        for cite in citations:
            f.write(json.dumps(cite, ensure_ascii=False) + "\n")

    return len(citations)

def main():
    print("=== 断链修复 ===\n")

    # Step 1: 修复 .md 后缀问题
    print("Step 1: 修复 .md 后缀...")
    fixed_suffix = fix_md_suffix_issues()
    print(f"  修复了 {len(fixed_suffix)} 个文件")

    # Step 2: 检查所有链接目标
    print("\nStep 2: 检查链接目标...")
    all_links = find_all_wikilinks()
    missing_targets = set()

    for link_info in all_links:
        target = link_info["normalized"]
        target_file = check_link_target(target)

        if target_file is None:
            missing_targets.add(target)

    print(f"  发现 {len(missing_targets)} 个缺失目标")

    # 过滤掉明显不需要创建的目标（如中文名称、概念性链接）
    need_create = []
    skip_create = []

    for target in missing_targets:
        # 检查是否是有效的节点 ID 格式
        if re.match(r'^[a-zA-Z0-9_-]+(/[a-zA-Z0-9_-]+)*$', target):
            need_create.append(target)
        elif target in ["素材摘要", "实体页", "主题页", "对比分析", "综合分析"]:
            # 这些是概念性链接，跳过
            skip_create.append(target)
        else:
            skip_create.append(target)

    print(f"  需创建: {len(need_create)} 个")
    print(f"  跳过: {len(skip_create)} 个")

    # Step 3: 创建占位页面
    if need_create:
        print("\nStep 3: 创建占位页面...")
        created = create_placeholder_pages(need_create)
        print(f"  创建了 {len(created)} 个占位页面")

        for path in created[:10]:
            print(f"    - {path}")
        if len(created) > 10:
            print(f"    ... 共 {len(created)} 个")

    # Step 4: 更新 citations.jsonl
    print("\nStep 4: 更新 citations.jsonl...")
    count = update_citations_jsonl()
    print(f"  写入 {count} 条引用关系")

    print("\n=== 修复完成 ===")
    print(f"修复: {len(fixed_suffix)} 文件 (.md 后缀)")
    print(f"创建: {len(created if need_create else 0)} 占位页面")
    print(f"更新: {count} citations")

if __name__ == "__main__":
    main()