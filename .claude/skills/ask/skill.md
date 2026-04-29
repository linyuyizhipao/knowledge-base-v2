---
name: ask
description: 查询知识库并晶化答案回 wiki。用户问知识库问题时调用，答案会被保存。
---

# /ask Skill

## 触发关键词

- 用户问任何关于知识库的问题
- "查询 xxx"
- "xxx 是什么"
- "帮我找 xxx"

---

## 工作流程

### Phase 1: 检索 Pipeline

```
用户问题 → Tokenized Search → Vector Search (可选) → Graph Expansion → Budget Control → Context Assembly
```

#### 1.1 Tokenized Search

```python
def tokenize_search(query, wiki_dir):
    """关键词搜索"""
    
    # 中文: CJK bigram
    # 英文: word splitting + stop word removal
    
    results = []
    for md_file in wiki_dir.rglob("*.md"):
        content = md_file.read_text()
        
        # 标题匹配加分
        title = extract_title(content)
        if query in title:
            score += 10
        
        # 内容匹配
        matches = count_matches(content, query_tokens)
        score += matches
        
        if score > 0:
            results.append({
                "file": md_file,
                "score": score,
                "title": title
            })
    
    return sorted(results, key=lambda x: x["score"], reverse=True)
```

#### 1.2 Graph Expansion (2-hop)

```python
def expand_by_graph(seed_nodes, edges, depth=2):
    """基于知识图谱扩展相关节点"""
    
    expanded = set(seed_nodes)
    
    for _ in range(depth):
        new_nodes = set()
        for node in expanded:
            # 找相连节点
            for edge in edges:
                if edge["from"] == node:
                    new_nodes.add(edge["to"])
                if edge["to"] == node:
                    new_nodes.add(edge["from"])
        
        expanded.update(new_nodes)
    
    return expanded
```

#### 1.3 Budget Control

```python
def budget_control(nodes, max_tokens=8000):
    """Token 预算控制"""
    
    # 分配: 60% wiki, 20% chat history, 5% index, 15% system
    
    wiki_budget = max_tokens * 0.6
    
    selected = []
    total_tokens = 0
    
    for node in sorted(nodes, key=lambda x: x["score"], reverse=True):
        content = node["content"]
        tokens = count_tokens(content)
        
        if total_tokens + tokens < wiki_budget:
            selected.append(node)
            total_tokens += tokens
        else:
            break
    
    return selected
```

### Phase 2: Context Assembly

```python
def assemble_context(selected_nodes, query):
    """组装 LLM 上下文"""
    
    context = []
    
    # System prompt
    context.append("你是 SLP 知识库助手。基于以下知识回答问题。")
    context.append("引用格式: [1], [2] 等，引用编号对应下方文档。")
    context.append("")
    
    # 引用文档（编号）
    for i, node in enumerate(selected_nodes):
        context.append(f"[{i+1}] {node['title']}")
        context.append(f"    路径: {node['path']}")
        context.append(node["content"])
        context.append("")
    
    return "\n".join(context)
```

### Phase 3: LLM 回答

```
LLM(context + query) → 回答（带引用）
```

### Phase 4: 晶化回 Wiki

**关键创新**：有价值的问题和答案会被保存到 wiki：

```markdown
---
id: queries/question-2026-04-28-001
type: query
question: 什么是事件处理的三种模式？
compiled: 2026-04-28
cited_pages:
  - wiki/patterns/event-extension-guide.md
  - wiki/patterns/nsq-usage.md
tags: [event, nsq, async]
---

# 什么是事件处理的三种模式？

> 问于 2026-04-28

## 回答

SLP 项目中有三种事件处理模式:

1. **同步处理** [1]
   - 直接在 Handler 中处理
   - 适用于耗时 <100ms 的操作

2. **异步队列** [1]
   - 通过 NSQ 消息队列
   - 适用于耗时 >100ms 的操作

3. **事件总线** [2]
   - 发布事件解耦模块
   - 适用于跨模块通信

## 引用

[1] wiki/patterns/event-extension-guide.md
[2] wiki/patterns/nsq-usage.md
```

---

## 输出格式

```
查询: 什么是事件处理的三种模式？

检索命中:
  [1] wiki/patterns/event-extension-guide.md (score: 15)
  [2] wiki/patterns/nsq-usage.md (score: 8)
  [3] wiki/projects/slp-go/09-event-capabilities.md (score: 5)

图谱扩展 (+2 相关):
  [4] wiki/patterns/business-module-standard.md
  [5] wiki/core/coding-standards.md

回答:
  ... (带引用 [1], [2], [3])

已晶化到 wiki/queries/event-modes-question.md
```

---

## 特点

| vs RAG | /ask |
|--------|------|
| 一次性答案 | 答案保存回 wiki |
| 无知识积累 | 知识持续增长 |
| 相同问题重复计算 | 已问答直接查询 |
| 无引用追踪 | 明确记录 cited_pages |

---

## 相关 Skills

- [/discover](discover) - 发现新问题（知识缺口）
- [/check](check) - 检查 queries 文件是否有过期答案