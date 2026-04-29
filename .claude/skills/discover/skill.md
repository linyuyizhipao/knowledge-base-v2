---
name: discover
description: 发现知识缺口、孤立节点、低密度社区。用户说"发现缺口"、"有什么需要补充"时调用。
---

# /discover Skill

## 触发关键词

- "发现缺口"
- "有什么需要补充"
- "知识盲区"
- "discover"
- "检查知识完整性"

---

## 工作流程

### Phase 1: 加载图谱

读取 graph/ 目录所有 JSONL 文件：

- nodes.jsonl - 所有节点
- edges.jsonl - 语义关系
- citations.jsonl - wikilink 关系
- co-occurrence.jsonl - 共现关系

### Phase 2: 计算图指标

#### 2.1 度分布分析

```python
for node in nodes:
    degree = count_edges(node)  # 入度 + 出度
    
    if degree == 0:
        isolated_nodes.append(node)  # 孤立节点
    elif degree == 1:
        peripheral_nodes.append(node)  # 边缘节点
    elif degree >= 10:
        hub_nodes.append(node)  # 核心节点
```

#### 2.2 Louvain 社区发现

使用 `graphology-communities-louvain` 或 Python `networkx`：

```python
import networkx as nx
from community import community_louvain

G = nx.Graph()
# 添加节点和边

communities = community_louvain.best_partition(G)

for comm_id, nodes in group_by_community(communities):
    cohesion = calculate_cohesion(nodes)  # 内部边密度
    if cohesion < 0.15:
        sparse_communities.append({
            "id": comm_id,
            "nodes": nodes,
            "cohesion": cohesion,
            "reason": "知识碎片化，缺乏交叉引用"
        })
```

#### 2.3 桥节点识别

```python
for node in nodes:
    connected_comms = get_connected_communities(node)
    if len(connected_comms) >= 3:
        bridge_nodes.append(node)  # 连接多个社区的关键节点
```

#### 2.4 知识缺口识别

| 缺口类型 | 检测方法 | 优先级 |
|----------|----------|--------|
| 孤立节点 | degree = 0 | 🔴 高 |
| 低密度社区 | cohesion < 0.15 | 🔴 高 |
| 断链 | wikilink 目标不存在 | 🟡 中 |
| 缺失实体 | 同一概念有多个定义 | 🟡 中 |
| 过期内容 | 超过 30 天未更新 | 🟢 低 |

### Phase 3: 4-Signal 相关性分析

为每个缺口推荐相关素材：

| Signal | 权重 | 说明 |
|--------|------|------|
| Direct link | ×3.0 | 直接 [[wikilink]] 连接 |
| Source overlap | ×4.0 | 共用 raw 素材 |
| Adamic-Adar | ×1.5 | 共同邻居加权 |
| Type affinity | ×1.0 | 同类型节点 |

### Phase 4: Deep Research 建议

对每个缺口，生成研究建议：

```json
{
  "gap_type": "isolated_node",
  "node": "wiki/entities/new-concept",
  "suggested_research": {
    "topic": "new-concept 的应用场景",
    "search_queries": [
      "new-concept best practices",
      "new-concept implementation guide"
    ],
    "priority": "high"
  }
}
```

---

## 输出格式

```
知识缺口发现报告

=== 孤立节点 (degree = 0) ===
  1. wiki/entities/pet-feature (无连接)
     建议: 搜索 "pet feature implementation"
  
  2. wiki/sources/article-123 (无连接)
     建议: 添加到相关主题页

=== 低密度社区 ===
  社区 A (cohesion: 0.08)
    节点: concept-1, concept-2, source-3
    问题: 3 个节点间无交叉引用
    建议: 创建 wiki/topics/社区A主题.md 综合页

=== 桥节点 (连接 3+ 社区) ===
  CODING_STANDARDS - 连接 5 个社区
    → 需要重点维护，影响面大

=== 断链 ===
  wiki/sources/xxx.md → [[missing-node]] (目标不存在)
    建议: 创建 missing-node 实体页

总计: 2 孤立, 1 低密度社区, 1 桥节点, 1 断链
```

---

## Python 实现

```python
#!/usr/bin/env python3
"""知识缺口发现模块"""

import json
from pathlib import Path
from collections import defaultdict
import networkx as nx

GRAPH_DIR = Path("graph")

def load_graph():
    G = nx.Graph()
    
    # 加载节点
    nodes = []
    with open(GRAPH_DIR / "nodes.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            nodes.append(json.loads(line))
    
    for n in nodes:
        G.add_node(n["id"])
    
    # 加载边
    with open(GRAPH_DIR / "edges.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            edge = json.loads(line)
            G.add_edge(edge["from"], edge["to"], weight=edge.get("weight", 1.0))
    
    # 加载 wikilinks
    with open(GRAPH_DIR / "citations.jsonl") as f:
        for line in f:
            if line.startswith("#"):
                continue
            cite = json.loads(line)
            G.add_edge(cite["from"], cite["to"], weight=0.5)
    
    return G, nodes

def find_gaps(G, nodes):
    gaps = {
        "isolated": [],
        "peripheral": [],
        "sparse_communities": [],
        "bridge_nodes": [],
        "broken_links": []
    }
    
    # 1. 孤立节点
    for n in nodes:
        degree = G.degree(n["id"])
        if degree == 0:
            gaps["isolated"].append(n)
        elif degree == 1:
            gaps["peripheral"].append(n)
    
    # 2. Louvain 社区发现
    try:
        from community import community_louvain
        communities = community_louvain.best_partition(G)
        
        comm_groups = defaultdict(list)
        for node, comm_id in communities.items():
            comm_groups[comm_id].append(node)
        
        for comm_id, comm_nodes in comm_groups.items():
            if len(comm_nodes) < 3:
                continue
            # 计算内密度
            subG = G.subgraph(comm_nodes)
            actual_edges = subG.number_of_edges()
            possible_edges = len(comm_nodes) * (len(comm_nodes) - 1) / 2
            cohesion = actual_edges / possible_edges if possible_edges > 0 else 0
            
            if cohesion < 0.15:
                gaps["sparse_communities"].append({
                    "id": comm_id,
                    "nodes": comm_nodes,
                    "cohesion": cohesion
                })
    except ImportError:
        print("提示: 安装 python-louvain 进行社区发现")
    
    return gaps

if __name__ == "__main__":
    G, nodes = load_graph()
    gaps = find_gaps(G, nodes)
    
    print(f"孤立节点: {len(gaps['isolated'])}")
    print(f"边缘节点: {len(gaps['peripheral'])}")
    print(f"低密度社区: {len(gaps['sparse_communities'])}")
```

---

## 相关 Skills

- [/check](check) - 健康检查（包含 discover 的部分功能）
- [/ingest](ingest) - 消化素材填补缺口