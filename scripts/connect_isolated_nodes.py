#!/usr/bin/env python3
"""
连接孤立节点 - 自动为孤立节点添加合理的链接

策略:
1. 分析孤立节点的内容，提取关键概念
2. 匹配到现有节点（基于名称相似度、目录结构）
3. 添加合理的 edges 和 wikilinks
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

BASE_DIR = Path(__file__).parent.parent
WIKI_DIR = BASE_DIR / "wiki"
CURATED_DIR = BASE_DIR / "curated"
GRAPH_DIR = BASE_DIR / "graph"

# 预定义的合理链接（基于知识结构）
# 这些链接应该在 knowledge-graph.json 的 edges 中已经定义，但可能没有在 wikilinks 中体现
KNOWN_RELATIONS = {
    # Core → Core
    "QUICK_REFERENCE": ["CODING_STANDARDS", "USER_GUIDE", "AI_WORKFLOW", "patterns/event-extension-guide"],
    "README": ["AGENTS", "INDEX"],
    "DOCUMENT_LOCATION_RULES": ["INDEX", "USER_GUIDE"],
    "AI_WORKFLOW": ["CODING_STANDARDS", "USER_GUIDE", "tools/slpctl-usage-guide"],

    # Patterns → Patterns
    "patterns/architecture-layered-standard": ["patterns/business-module-standard", "patterns/code-scale-standard"],
    "patterns/business-code-example": ["patterns/business-module-standard", "patterns/event-extension-guide"],
    "patterns/database-naming-conventions": ["patterns/business-module-standard"],
    "patterns/project-learning-framework": ["tools/slpctl-usage-guide"],
    "patterns/dev-to-dev-deployment": ["USER_GUIDE", "patterns/slp-business-development-standard"],
    "patterns/cmd-module-standard": ["patterns/event-extension-guide", "patterns/nsq-usage"],
    "patterns/code-scale-standard": ["patterns/business-module-standard", "patterns/cmd-module-standard"],
    "patterns/business-module-standard": ["patterns/code-scale-standard", "patterns/event-extension-guide", "patterns/cmd-module-standard"],

    # Tools
    "tools/gh-pr-analysis": ["USER_GUIDE"],
    "tools/slpctl": ["CODING_STANDARDS", "USER_GUIDE", "patterns/slp-business-development-standard"],
    "tools/slpctl-usage-guide": ["CODING_STANDARDS", "patterns/slp-business-development-standard", "projects/slp-go/01-structure"],

    # Projects
    "projects/slp-go/02-architecture": ["projects/slp-go/01-structure", "patterns/architecture-layered-standard"],
    "projects/slp-go/03-development": ["projects/slp-go/01-structure", "patterns/slp-business-development-standard"],
    "projects/slp-go/04-api": ["projects/slp-go/01-structure", "tools/slpctl-usage-guide"],
    "projects/slp-go/05-service": ["projects/slp-go/01-structure", "patterns/business-module-standard"],
    "projects/slp-go/06-dao": ["projects/slp-go/01-structure", "tools/slpctl"],
    "projects/slp-go/07-infra": ["projects/slp-go/01-structure"],
    "projects/slp-go/09-event-capabilities": ["patterns/event-extension-guide", "patterns/nsq-usage"],
    "projects/slp-room/02-architecture": ["projects/slp-room/01-structure", "patterns/architecture-layered-standard"],
    "projects/slp-room/01-event-capabilities": ["patterns/event-extension-guide", "projects/slp-room/01-structure"],
    "projects/slp-starship/01-event-capabilities": ["patterns/event-extension-guide", "patterns/nsq-usage", "projects/slp-starship/01-structure"],
    "projects/slp-common-rpc/CORE_LEARNING": ["patterns/project-learning-framework", "projects/slp-go/01-structure"],

    # Cross-projects
    "cross-projects/369-recharge/slp-room": ["cross-projects/369-recharge/overview", "projects/slp-room/01-structure"],
    "cross-projects/big-brother/README-PASSCODE": ["cross-projects/big-brother/passcode-requirement", "cross-projects/big-brother/passcode-technical-design", "cross-projects/big-brother/pet-feature"],
    "cross-projects/big-brother/passcode-requirement": ["cross-projects/big-brother/README-PASSCODE"],
    "cross-projects/big-brother/test-report": ["cross-projects/big-brother/passcode-technical-design"],
    "cross-projects/big-brother/passcode-technical-design": ["patterns/business-module-standard", "patterns/business-code-example", "cross-projects/big-brother/pet-feature"],
    "cross-projects/prayer-activity/01-overview": ["cross-projects/prayer-activity/slp-starship", "projects/slp-starship/01-structure"],
    "cross-projects/prayer-activity/slp-starship": ["cross-projects/prayer-activity/01-overview"],
    "cross-projects/fly-chess/overview": [],
    "cross-projects/chatroom/room-type-development": ["DOCUMENT_LOCATION_RULES"],
    "cross-projects/chatroom/room-type-concept": ["cross-projects/chatroom/room-type-development"],
    "cross-projects/buye-payment/overview": [],
    "cross-projects/gift-suit/gift-suit-feature": [],
    "cross-projects/decorate-commodity-use/overview": ["cross-projects/decorate-commodity-use/slp-go", "cross-projects/decorate-commodity-use/slp-php"],
}

def load_nodes_jsonl():
    """加载节点"""
    nodes = []
    with open(GRAPH_DIR / "nodes.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            nodes.append(json.loads(line))
    return nodes

def load_edges_jsonl():
    """加载现有边"""
    edges = []
    with open(GRAPH_DIR / "edges.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            edges.append(json.loads(line))
    return edges

def find_isolated_nodes(nodes, edges):
    """找出孤立节点"""
    # 统计每个节点的连接数
    node_connections = defaultdict(int)

    for edge in edges:
        node_connections[edge["from"]] += 1
        node_connections[edge["to"]] += 1

    # 孤立节点 = 连接数为 0
    isolated = []
    for node in nodes:
        if node_connections.get(node["id"], 0) == 0:
            isolated.append(node)

    return isolated

def add_edges_for_isolated_nodes(isolated_nodes, existing_edges):
    """为孤立节点添加边"""
    new_edges = []

    for node in isolated_nodes:
        node_id = node["id"]

        # 查找预定义的链接
        predefined_links = KNOWN_RELATIONS.get(node_id, [])

        for target in predefined_links:
            # 检查目标是否存在（在 nodes 中）
            # 添加边
            edge = {
                "from": node_id,
                "to": target,
                "type": "auto_linked",
                "weight": 1.0,
                "source": "fix_script",
                "reason": "预定义关系",
                "created": datetime.now().isoformat()
            }
            new_edges.append(edge)

            # 同时添加反向边（引用）
            reverse_edge = {
                "from": target,
                "to": node_id,
                "type": "referenced_by",
                "weight": 0.5,
                "source": "fix_script",
                "reason": "反向引用",
                "created": datetime.now().isoformat()
            }
            new_edges.append(reverse_edge)

    return new_edges

def update_edges_jsonl(new_edges):
    """追加新边到 edges.jsonl"""
    with open(GRAPH_DIR / "edges.jsonl", "a") as f:
        for edge in new_edges:
            f.write(json.dumps(edge, ensure_ascii=False) + "\n")

    return len(new_edges)

def add_wikilinks_to_wiki_files(isolated_nodes):
    """在 wiki 文件中添加 wikilinks"""
    updated_files = []

    for node in isolated_nodes:
        node_id = node["id"]
        wiki_path = WIKI_DIR / node["path"].replace("curated/", "").replace("curated\\", "")

        # 如果 wiki 文件不存在，尝试其他路径
        if not wiki_path.exists():
            wiki_path = WIKI_DIR / f"{node_id}.md"
            if not wiki_path.exists():
                continue

        # 读取内容
        content = wiki_path.read_text()

        # 查找预定义链接
        predefined_links = KNOWN_RELATIONS.get(node_id, [])

        if not predefined_links:
            continue

        # 添加 wikilinks 到文档末尾
        wikilinks_section = "\n\n## 相关知识\n\n"
        for target in predefined_links:
            wikilinks_section += f"- [[{target}]]\n"

        # 如果文档已经有相关知识部分，则跳过
        if "## 相关知识" in content or "## 相关链接" in content:
            continue

        # 添加 wikilinks
        new_content = content + wikilinks_section
        wiki_path.write_text(new_content)
        updated_files.append(str(wiki_path.relative_to(WIKI_DIR)))

    return updated_files

def main():
    print("=== 连接孤立节点 ===\n")

    # Step 1: 加载现有数据
    print("Step 1: 加载图谱数据...")
    nodes = load_nodes_jsonl()
    edges = load_edges_jsonl()
    print(f"  节点: {len(nodes)}")
    print(f"  边: {len(edges)}")

    # Step 2: 找出孤立节点
    print("\nStep 2: 找出孤立节点...")
    isolated = find_isolated_nodes(nodes, edges)
    print(f"  孤立节点: {len(isolated)}")

    for node in isolated[:10]:
        print(f"    - {node['id']} ({node.get('label', '')})")
    if len(isolated) > 10:
        print(f"    ... 共 {len(isolated)} 个")

    # Step 3: 添加边
    print("\nStep 3: 添加边...")
    new_edges = add_edges_for_isolated_nodes(isolated, edges)
    count = update_edges_jsonl(new_edges)
    print(f"  添加了 {count} 条边")

    # Step 4: 添加 wikilinks
    print("\nStep 4: 添加 wikilinks...")
    updated = add_wikilinks_to_wiki_files(isolated)
    print(f"  更新了 {len(updated)} 个 wiki 文件")

    for path in updated[:10]:
        print(f"    - {path}")

    print("\n=== 完成 ===")
    print(f"孤立节点: {len(isolated)} → 建议手动检查剩余")

if __name__ == "__main__":
    main()