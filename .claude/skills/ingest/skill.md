---
name: ingest
description: 解析单个素材（raw 文件）→ wiki 页面 + 知识图谱。用户说"消化这个"、"整理这个文件"时调用。
---

# /ingest Skill

## 触发关键词

- "消化这个"
- "整理这个文件"
- "把这个加入知识库"
- "ingest"

---

## 工作流程

### Phase 1: LLM 分析素材

读取用户指定的 raw 文件，执行结构化分析：

```
分析输出 JSON:
{
  "source_file": "raw/articles/xxx.md",
  "source_type": "article|note|pdf|curl",
  
  "key_entities": [
    {"name": "实体名", "type": "concept|person|project|tool", "desc": "简述"}
  ],
  
  "key_concepts": [
    {"name": "概念名", "definition": "定义", "importance": "high|medium|low"}
  ],
  
  "key_points": [
    {"point": "关键点", "evidence": "证据/引用"}
  ],
  
  "suggested_links": [
    {"to": "现有wiki节点ID", "type": "relates_to|builds_on|contradicts", "reason": "理由"}
  ],
  
  "contradictions": [
    {"with": "现有知识节点", "issue": "冲突描述", "resolution": "建议处理方式"}
  ],
  
  "summary": "200字精简摘要",
  
  "tags": ["标签1", "标签2"]
}
```

### Phase 2: LLM 生成 Wiki 页面

基于分析结果，生成 wiki 页面：

```markdown
---
id: sources/xxx
type: source
source_file: raw/articles/xxx.md
sources: [raw/articles/xxx.md]
compiled: 2026-04-28
tags: [标签1, 标签2]
links_to:
  - 现有节点ID
  - 新发现的节点ID
---

# 标题

> 来源: raw/articles/xxx.md

## 核心概念

| 概念 | 定义 |
|------|------|
| ... | ... |

## 关键要点

1. ...
2. ...

## 相关知识

- [[concept-1]] - 相关概念
- [[project-x]] - 相关项目

## 原文精华（可选）

> 引用原文关键段落
```

### Phase 3: 更新知识图谱

追加到 graph/ 目录：

1. **nodes.jsonl** - 添加新节点
2. **edges.jsonl** - 添加新关系（suggested_links）
3. **citations.jsonl** - 添加 wikilinks
4. **co-occurrence.jsonl** - 添加共现关系（key_entities 同时出现）

### Phase 4: 发现实体页

如果分析中发现新实体/概念，创建对应 wiki 页面：

- `wiki/entities/{entity-name}.md`
- `wiki/topics/{concept-name}.md`

---

## 输入格式

用户调用时提供：

```
/ingest raw/articles/xxx.md
```

或

```
消化这个文件: raw/notes/my-note.md
```

---

## 输出

```
素材已消化！

生成文件:
  wiki/sources/xxx.md (摘要页)
  wiki/entities/entity-1.md (新实体)
  wiki/entities/entity-2.md (新实体)

更新图谱:
  nodes.jsonl +1 节点
  edges.jsonl +5 关系
  citations.jsonl +3 wikilinks

发现链接:
  → relates_to: CODING_STANDARDS
  → builds_on: patterns/event-extension-guide
  → relates_to: projects/slp-go/01-structure
```

---

## 增量缓存

使用 SHA256 检查素材是否已处理：

```python
def get_file_hash(filepath):
    return hashlib.sha256(open(filepath, 'rb').read()).hexdigest()

# 检查 nodes.jsonl 中是否已有该 source_file
# 如果 hash 相同，跳过处理
```

---

## 相关 Skills

- [/discover](discover) - 发现知识缺口
- [/check](check) - 健康检查
- [/ask](ask) - 查询 + 晶化