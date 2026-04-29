---
name: compile
description: 编译 curated 文档到 wiki（带 LLM 真分析）。用户说"编译wiki"、"编译知识库"时调用。
---

# /compile Skill

## 触发关键词

- "编译wiki"
- "编译知识库"
- "compile"
- "更新 wiki"

---

## 核心改进

**旧版本**: 复制文件 + 加 frontmatter（假编译）

**新版本**: LLM 分析 → 精简提炼 → 发现链接 → 更新图谱

---

## 工作流程

### Phase 1: 扫描待编译文件

```python
def scan_source(source_dir):
    """扫描源文件，检查增量缓存"""
    
    to_compile = []
    
    for md_file in source_dir.rglob("*.md"):
        hash = get_file_hash(md_file)
        
        # 检查是否已编译且未变更
        cached = find_cached_hash(md_file)
        if cached and cached == hash:
            continue  # 跳过未变更
        
        to_compile.append({
            "file": md_file,
            "hash": hash,
            "relative_path": md_file.relative_to(source_dir)
        })
    
    return to_compile
```

### Phase 2: LLM 分析（Two-Step Chain-of-Thought）

#### Step 1: 分析

```
LLM 分析输入:
  - 原文档内容
  - 现有 wiki 结构（nodes.jsonl 概览）
  - purpose.md（知识库目标）

LLM 分析输出:
{
  "doc_type": "standard|guide|case|reference",
  
  "key_entities": [
    {"name": "事件总线", "type": "concept", "importance": "high"}
  ],
  
  "key_points": [
    {"point": "禁止阻塞主 goroutine", "code_ref": "示例代码位置"}
  ],
  
  "suggested_links": [
    {"to": "patterns/nsq-usage", "type": "depends_on", "reason": "异步队列是推荐方案"}
  ],
  
  "contradictions": [],  # 与现有知识冲突
  
  "summary_200": "精简摘要",
  
  "tables": [
    {
      "title": "事件模式对比",
      "headers": ["模式", "适用场景", "耗时"],
      "rows": [...]
    }
  ]
}
```

#### Step 2: 生成 Wiki 页面

```
LLM 生成输入:
  - Step 1 分析结果
  - 目标格式模板

LLM 生成输出:
  - wiki 页面 Markdown（带 frontmatter）
  - 精简表格化内容
  - [[wikilinks]] 链接
```

### Phase 3: 写入 Wiki

```python
def write_wiki(analysis, generated_content, source_file):
    """写入 wiki 文件"""
    
    wiki_path = get_wiki_path(source_file)
    
    # Frontmatter
    frontmatter = {
        "id": generate_id(source_file),
        "type": analysis["doc_type"],
        "source_file": str(source_file),
        "sources": [str(source_file)],
        "compiled": datetime.now().isoformat(),
        "hash": get_file_hash(source_file),
        "tags": extract_tags(analysis),
        "links_to": [link["to"] for link in analysis["suggested_links"]]
    }
    
    # 写入
    with open(wiki_path, "w") as f:
        f.write("---\n")
        f.write(yaml.dump(frontmatter))
        f.write("---\n\n")
        f.write(generated_content)
```

### Phase 4: 更新知识图谱

```python
def update_graph(analysis, wiki_path):
    """追加到 graph/"""
    
    # 1. 更新 nodes.jsonl
    append_node({
        "id": frontmatter["id"],
        "path": str(wiki_path),
        "type": frontmatter["type"],
        "tags": frontmatter["tags"]
    })
    
    # 2. 更新 edges.jsonl（发现的链接）
    for link in analysis["suggested_links"]:
        append_edge({
            "from": frontmatter["id"],
            "to": link["to"],
            "type": link["type"],
            "weight": get_link_weight(link["type"]),
            "discovered_by": "compile_llm"
        })
    
    # 3. 更新 co-occurrence.jsonl（实体共现）
    entities = analysis["key_entities"]
    for i, e1 in enumerate(entities):
        for e2 in entities[i+1:]:
            append_co_occurrence({
                "entity1": e1["name"],
                "entity2": e2["name"],
                "source": frontmatter["id"]
            })
```

### Phase 5: 更新 knowledge-index.json

```python
def update_index():
    """更新 shortcuts 和 nodes_index"""
    
    index = load_json("knowledge-index.json")
    
    # 同步 nodes.jsonl 到 nodes_index
    nodes = load_nodes_jsonl()
    index["nodes_index"] = [
        {"id": n["id"], "path": n["path"], "label": n.get("label", "")}
        for n in nodes
    ]
    
    save_json("knowledge-index.json", index)
```

---

## 编译范围选择

询问用户编译哪些目录：

```
你想编译哪些目录？

可选：
[1] core        核心文档（AGENTS, CODING_STANDARDS 等）
[2] patterns    开发规范
[3] tools       工具文档
[4] projects    项目知识
[5] cross-projects 跨项目业务
[6] raw/articles 新文章（如果需要）
[7] all         全部

请输入编号（如 2,3 表示 patterns 和 tools）
```

---

## 输出格式

```
编译开始...

[curated/CODING_STANDARDS.md]
  分析: 发现 5 个关键概念, 3 个建议链接
  生成: wiki/core/coding-standards.md
  图谱: +1 节点, +3 边

[curated/patterns/event-extension-guide.md]
  分析: 发现 2 个关键概念, 与 nsq-usage 强关联
  生成: wiki/patterns/event-extension-guide.md
  图谱: +1 节点, +2 边

编译完成！

统计:
  - 编译文件: 15 个
  - 新增节点: 15 个
  - 发现链接: 28 条
  - 发现冲突: 0 处

图谱更新:
  nodes.jsonl: 52 → 67 行
  edges.jsonl: 28 → 56 行

建议运行: /discover 查看知识缺口
```

---

## Python 实现骨架

```python
#!/usr/bin/env python3
"""知识编译脚本 - Two-Step LLM 分析"""

import json
import hashlib
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent.parent
CURATED = BASE_DIR / "curated"
WIKI = BASE_DIR / "wiki"
GRAPH = BASE_DIR / "graph"

def get_file_hash(fpath):
    return hashlib.sha256(open(fpath, 'rb').read()).hexdigest()

def compile_with_llm(source_file):
    """Two-Step 编译"""
    
    # Step 1: 分析
    content = open(source_file).read()
    existing_nodes = load_nodes_jsonl()
    
    analysis_prompt = f"""
分析以下文档，提取结构化知识：

文档内容:
{content}

现有知识库节点:
{json.dumps(existing_nodes[:20], ensure_ascii=False)}

输出 JSON:
{
  "key_entities": [...],
  "key_points": [...],
  "suggested_links": [...],
  "summary_200": "...",
  "tables": [...]
}
"""
    
    # 调用 LLM (这里需要实际 API 调用)
    # analysis = call_llm(analysis_prompt)
    
    # Step 2: 生成
    # generated = call_llm(f"基于以下分析生成 wiki 页面:\n{analysis}")
    
    return analysis, generated

if __name__ == "__main__":
    import sys
    
    scope = sys.argv[1] if len(sys.argv) > 1 else "all"
    
    print(f"编译范围: {scope}")
    print("提示: 此脚本需要配置 LLM API 才能完整运行")
    
    # 扫描文件
    to_compile = scan_source(CURATED)
    print(f"待编译: {len(to_compile)} 个文件")
```

---

## 相关 Skills

- [/ingest](ingest) - 单文件编译
- [/discover](discover) - 编译后检查缺口
- [/check](check) - 验证编译结果