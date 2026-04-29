#!/usr/bin/env python3
"""
知识图谱初始化 - 从 knowledge-graph.json 转换到 JSONL 格式
JSONL 格式优势：追加式写入、流式读取、易于维护

三种关系文件：
- edges.jsonl: 语义关系（builds_on, uses_concept, relates_to 等）
- citations.jsonl: 引用关系（从 wikilinks 提取）
- co-occurrence.jsonl: 共现关系（同一文档中出现的实体）
"""

import json
import os
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
GRAPH_DIR = BASE_DIR / "graph"
SOURCE_JSON = BASE_DIR / "knowledge-graph.json"

# 关系类型映射（从旧格式到新格式）
EDGE_TYPE_MAP = {
    "必读": "must_read",
    "索引": "index",
    "导航": "navigate",
    "参考": "reference",
    "流程": "process",
    "工具": "tool",
    "核心规范": "core_standard",
    "事件": "event",
    "队列": "queue",
    "部署": "deploy",
    "依赖": "depends_on",
    "约束": "constrains",
    "业务": "business",
    "规范": "standard",
    "项目": "project"
}


def init_graph():
    """初始化知识图谱目录和文件"""
    GRAPH_DIR.mkdir(exist_ok=True)

    # 创建空文件（带注释头）
    for fname in ["edges.jsonl", "citations.jsonl", "co-occurrence.jsonl"]:
        fpath = GRAPH_DIR / fname
        if not fpath.exists():
            with open(fpath, "w") as f:
                f.write(f"# {fname} - 知识图谱关系存储\n")
                f.write(f"# 格式: JSONL (每行一个 JSON 对象)\n")
                f.write(f"# 创建时间: {datetime.now().isoformat()}\n")
                f.write("#\n")

    print(f"graph/ 目录已初始化")


def migrate_edges():
    """从 knowledge-graph.json 迁移 edges 到 JSONL"""
    if not SOURCE_JSON.exists():
        print("knowledge-graph.json 不存在，跳过迁移")
        return

    with open(SOURCE_JSON) as f:
        data = json.load(f)

    edges = data.get("edges", [])

    edges_file = GRAPH_DIR / "edges.jsonl"

    # 追加模式，不覆盖已有数据
    with open(edges_file, "a") as f:
        for edge in edges:
            from_id = edge.get("from", "")
            to_id = edge.get("to", "")
            old_type = edge.get("type", "relates_to")

            # 映射关系类型
            new_type = EDGE_TYPE_MAP.get(old_type, "relates_to")

            record = {
                "from": from_id,
                "to": to_id,
                "type": new_type,
                "weight": 1.0,
                "source": "migrated",
                "created": datetime.now().isoformat()
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"迁移 {len(edges)} 条边关系到 edges.jsonl")


def extract_citations_from_wiki():
    """从 wiki 文件提取 [[wikilinks]] 作为引用关系"""
    wiki_dir = BASE_DIR / "wiki"

    citations_file = GRAPH_DIR / "citations.jsonl"

    count = 0
    with open(citations_file, "a") as f:
        for md_file in wiki_dir.rglob("*.md"):
            try:
                content = md_file.read_text()

                # 提取 wikilinks: [[some-id]] 或 [[some-id|显示文本]]
                import re
                links = re.findall(r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]', content)

                # 获取当前文档 ID（从路径）
                rel_path = md_file.relative_to(wiki_dir)
                from_id = str(rel_path).replace(".md", "").replace("/", "/")

                for link in links:
                    record = {
                        "from": from_id,
                        "to": link,
                        "type": "wikilink",
                        "weight": 1.0,
                        "source_file": str(md_file.relative_to(BASE_DIR)),
                        "created": datetime.now().isoformat()
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1

            except Exception as e:
                print(f"处理 {md_file} 失败: {e}")

    print(f"提取 {count} 条 wikilink 到 citations.jsonl")


def create_node_index():
    """创建节点索引文件（供快速查询）"""
    nodes_file = GRAPH_DIR / "nodes.jsonl"

    if not SOURCE_JSON.exists():
        return

    with open(SOURCE_JSON) as f:
        data = json.load(f)

    nodes = data.get("nodes", [])

    with open(nodes_file, "w") as f:  # 覆盖，因为这是完整索引
        for node in nodes:
            record = {
                "id": node.get("id", ""),
                "label": node.get("label", ""),
                "path": node.get("path", ""),
                "category": node.get("category", ""),
                "role": node.get("role", ""),
                "desc": node.get("desc", ""),
                "sources": [],  # 待填充
                "created": datetime.now().isoformat()
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    print(f"创建 {len(nodes)} 个节点索引到 nodes.jsonl")


if __name__ == "__main__":
    print("=== 知识图谱初始化 ===\n")

    init_graph()
    migrate_edges()
    extract_citations_from_wiki()
    create_node_index()

    print("\n=== 完成 ===")
    print(f"graph/ 目录内容:")
    for f in GRAPH_DIR.iterdir():
        lines = len(open(f).readlines())
        print(f"  {f.name}: {lines} 行")