#!/usr/bin/env python3
"""
知识发现模块 - 4-Signal 相关性模型 + Louvain 社区发现

功能:
1. 计算节点相关性（4-Signal）
2. Louvain 社区发现
3. 发现知识缺口（孤立节点、低密度社区）
4. 发现桥节点（连接多个社区）
5. 发现惊讶连接（跨社区边缘）
"""

import json
import math
from pathlib import Path
from collections import defaultdict
from datetime import datetime

try:
    import networkx as nx
    HAS_NETWORKX = True
except ImportError:
    HAS_NETWORKX = False
    print("提示: 安装 networkx 进行完整图谱分析: pip install networkx")

try:
    from community import community_louvain
    HAS_LOUVAIN = True
except ImportError:
    HAS_LOUVAIN = False
    print("提示: 安装 python-louvain 进行社区发现: pip install python-louvain")

BASE_DIR = Path(__file__).parent.parent
GRAPH_DIR = BASE_DIR / "graph"


# ============== 数据加载 ==============

def load_jsonl(filepath):
    """加载 JSONL 文件"""
    records = []
    with open(filepath) as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            records.append(json.loads(line))
    return records


def load_graph_data():
    """加载所有图谱数据"""
    nodes = load_jsonl(GRAPH_DIR / "nodes.jsonl")
    edges = load_jsonl(GRAPH_DIR / "edges.jsonl")
    citations = load_jsonl(GRAPH_DIR / "citations.jsonl")
    co_occurrence = load_jsonl(GRAPH_DIR / "co-occurrence.jsonl")

    return {
        "nodes": nodes,
        "edges": edges,
        "citations": citations,
        "co_occurrence": co_occurrence
    }


# ============== NetworkX 图构建 ==============

def build_networkx_graph(data):
    """构建 NetworkX 图"""
    if not HAS_NETWORKX:
        return None

    G = nx.Graph()

    # 添加节点
    for node in data["nodes"]:
        G.add_node(
            node["id"],
            label=node.get("label", ""),
            type=node.get("role", node.get("category", "unknown")),
            path=node.get("path", "")
        )

    # 添加边（edges.jsonl）
    for edge in data["edges"]:
        weight = edge.get("weight", 1.0)
        # 根据类型调整权重
        type_weight = {
            "must_read": 3.0,
            "depends_on": 2.0,
            "builds_on": 2.0,
            "relates_to": 1.0
        }
        weight *= type_weight.get(edge.get("type", ""), 1.0)

        G.add_edge(
            edge["from"],
            edge["to"],
            weight=weight,
            type=edge.get("type", "semantic")
        )

    # 添加 wikilinks（权重较低）
    for cite in data["citations"]:
        G.add_edge(
            cite["from"],
            cite["to"],
            weight=0.5,
            type="wikilink"
        )

    return G


# ============== 4-Signal 相关性模型 ==============

def calculate_4signal_relevance(G, node_id, target_id, data):
    """
    4-Signal 相关性计算

    Signal 1: Direct link (×3.0) - 直接连接
    Signal 2: Source overlap (×4.0) - 共用源文件
    Signal 3: Adamic-Adar (×1.5) - 共同邻居
    Signal 4: Type affinity (×1.0) - 同类型
    """
    score = 0.0

    if not HAS_NETWORKX:
        return {"total": 0, "signals": {}}

    # Signal 1: Direct link
    if G.has_edge(node_id, target_id):
        score += 3.0
        signals = {"direct_link": 3.0}
    else:
        signals = {"direct_link": 0}

    # Signal 2: Source overlap
    node_sources = get_node_sources(node_id, data["nodes"])
    target_sources = get_node_sources(target_id, data["nodes"])
    overlap = len(set(node_sources) & set(target_sources))
    if overlap > 0:
        signals["source_overlap"] = 4.0 * overlap
        score += signals["source_overlap"]
    else:
        signals["source_overlap"] = 0

    # Signal 3: Adamic-Adar
    try:
        common_neighbors = set(G.neighbors(node_id)) & set(G.neighbors(target_id))
        aa_score = sum(1.0 / math.log(G.degree(n) + 1) for n in common_neighbors)
        signals["adamic_adar"] = min(aa_score * 1.5, 3.0)
        score += signals["adamic_adar"]
    except:
        signals["adamic_adar"] = 0

    # Signal 4: Type affinity
    node_type = G.nodes[node_id].get("type", "")
    target_type = G.nodes[target_id].get("type", "")
    if node_type == target_type and node_type != "":
        signals["type_affinity"] = 1.0
        score += 1.0
    else:
        signals["type_affinity"] = 0

    return {"total": score, "signals": signals}


def get_node_sources(node_id, nodes):
    """获取节点的源文件列表"""
    for node in nodes:
        if node["id"] == node_id:
            return node.get("sources", [])
    return []


# ============== Louvain 社区发现 ==============

def detect_communities(G):
    """Louvain 社区发现"""
    if not HAS_LOUVAIN or not HAS_NETWORKX:
        return None

    partition = community_louvain.best_partition(G, weight="weight")

    # 按 community 分组
    communities = defaultdict(list)
    for node, comm_id in partition.items():
        communities[comm_id].append(node)

    return communities, partition


def calculate_community_cohesion(G, community_nodes):
    """计算社区内聚度"""
    if len(community_nodes) < 2:
        return 0

    subG = G.subgraph(community_nodes)
    actual_edges = subG.number_of_edges()
    possible_edges = len(community_nodes) * (len(community_nodes) - 1) / 2

    return actual_edges / possible_edges if possible_edges > 0 else 0


# ============== 知识缺口发现 ==============

def find_knowledge_gaps(G, data):
    """发现知识缺口"""
    gaps = {
        "isolated_nodes": [],      # degree = 0
        "peripheral_nodes": [],    # degree = 1
        "sparse_communities": [],  # cohesion < 0.15
        "bridge_nodes": [],        # 连接 3+ 社区
        "broken_links": []         # wikilink 目标不存在
    }

    if not HAS_NETWORKX:
        return gaps

    # 1. 孤立/边缘节点
    for node in data["nodes"]:
        node_id = node["id"]
        try:
            degree = G.degree(node_id)
        except:
            degree = 0

        if degree == 0:
            gaps["isolated_nodes"].append({
                "node": node,
                "issue": "无任何连接",
                "action": "添加引用或删除"
            })
        elif degree == 1:
            gaps["peripheral_nodes"].append({
                "node": node,
                "issue": "只有一个连接",
                "action": "检查是否需要更多引用"
            })

    # 2. 社区发现 + 低密度社区
    if HAS_LOUVAIN:
        communities, partition = detect_communities(G)

        for comm_id, comm_nodes in communities.items():
            if len(comm_nodes) < 3:
                continue

            cohesion = calculate_community_cohesion(G, comm_nodes)

            if cohesion < 0.15:
                gaps["sparse_communities"].append({
                    "community_id": comm_id,
                    "nodes": comm_nodes,
                    "cohesion": cohesion,
                    "action": "创建主题页整合，添加交叉引用"
                })

        # 3. 桥节点
        for node_id in G.nodes():
            connected_comms = set()
            for neighbor in G.neighbors(node_id):
                connected_comms.add(partition.get(neighbor, -1))

            if len(connected_comms) >= 3:
                gaps["bridge_nodes"].append({
                    "node_id": node_id,
                    "connected_communities": list(connected_comms),
                    "importance": "连接多个知识领域的关键节点"
                })

    # 4. 断链检查
    wiki_dir = BASE_DIR / "wiki"
    for cite in data["citations"]:
        target = cite["to"]
        # 检查目标是否存在
        target_path = wiki_dir / f"{target}.md"
        if not target_path.exists():
            # 尝试其他路径
            found = False
            for possible in wiki_dir.rglob("*.md"):
                if possible.stem == target or possible.stem.endswith(target):
                    found = True
                    break
            if not found:
                gaps["broken_links"].append({
                    "source": cite["from"],
                    "broken_target": target,
                    "action": "创建目标页面或修复链接"
                })

    return gaps


# ============== 惊讶连接发现 ==============

def find_surprising_connections(G, partition):
    """发现跨社区连接（惊讶连接）"""
    surprising = []

    if not HAS_NETWORKX or partition is None:
        return surprising

    for edge in G.edges():
        from_node, to_node = edge
        from_comm = partition.get(from_node, -1)
        to_comm = partition.get(to_node, -1)

        if from_comm != to_comm:
            # 跨社区连接
            surprising.append({
                "from": from_node,
                "to": to_node,
                "from_community": from_comm,
                "to_community": to_comm,
                "weight": G.edges[edge].get("weight", 1.0),
                "surprise_level": "high" if abs(from_comm - to_comm) > 5 else "medium"
            })

    return surprising


# ============== 主入口 ==============

def discover_all():
    """执行完整发现流程"""
    print("=== 知识发现 ===\n")

    # 加载数据
    data = load_graph_data()
    print(f"节点: {len(data['nodes'])}")
    print(f"边: {len(data['edges'])}")
    print(f"Wikilinks: {len(data['citations'])}")

    # 构建图
    G = build_networkx_graph(data)

    if G is None:
        print("\n缺少 networkx，跳过图谱分析")
        return

    print(f"\n图构建完成: {G.number_of_nodes()} 节点, {G.number_of_edges()} 边")

    # 发现缺口
    gaps = find_knowledge_gaps(G, data)

    print(f"\n=== 知识缺口 ===")
    print(f"孤立节点: {len(gaps['isolated_nodes'])}")
    print(f"边缘节点: {len(gaps['peripheral_nodes'])}")
    print(f"低密度社区: {len(gaps['sparse_communities'])}")
    print(f"桥节点: {len(gaps['bridge_nodes'])}")
    print(f"断链: {len(gaps['broken_links'])}")

    # 社区发现
    if HAS_LOUVAIN:
        communities, partition = detect_communities(G)
        print(f"\n=== 社区结构 ===")
        print(f"发现 {len(communities)} 个社区")

        for comm_id, nodes in sorted(communities.items(), key=lambda x: -len(x[1]))[:5]:
            cohesion = calculate_community_cohesion(G, nodes)
            print(f"  社区 {comm_id}: {len(nodes)} 节点, cohesion={cohesion:.2f}")

        # 惊讶连接
        surprising = find_surprising_connections(G, partition)
        print(f"\n=== 惊讶连接 ===")
        print(f"跨社区连接: {len(surprising)} 条")

        for conn in surprising[:5]:
            print(f"  {conn['from']} → {conn['to']} (跨社区)")

    # 输出报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "nodes": len(data["nodes"]),
            "edges": len(data["edges"]),
            "citations": len(data["citations"])
        },
        "gaps": gaps,
        "communities": {str(k): v for k, v in communities.items()} if HAS_LOUVAIN else {},
        "surprising_connections": surprising if HAS_LOUVAIN else []
    }

    report_path = GRAPH_DIR / "discover-report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n报告已保存: {report_path}")

    return gaps


if __name__ == "__main__":
    discover_all()