---
name: check
description: Wiki 健康检查：孤立节点、断链、冲突、过期内容。用户说"检查wiki"、"健康检查"时调用。
---

# /check Skill

## 触发关键词

- "检查wiki"
- "健康检查"
- "wiki有没有问题"
- "check"
- "验证知识库"

---

## 工作流程

### Phase 1: 结构检查

#### 1.1 断链检查

```python
broken_links = []

for md_file in wiki_files:
    wikilinks = extract_wikilinks(md_file)
    
    for link in wikilinks:
        target_file = find_wiki_file(link)
        if not target_file.exists():
            broken_links.append({
                "source": md_file,
                "broken_link": link,
                "severity": "high"
            })
```

#### 1.2 孤立节点检查

```python
isolated_nodes = []

for node in nodes:
    incoming_links = count_incoming_links(node)
    outgoing_links = count_outgoing_links(node)
    
    if incoming_links + outgoing_links == 0:
        isolated_nodes.append({
            "node": node,
            "issue": "无任何连接",
            "action": "创建引用或删除"
        })
```

### Phase 2: 内容检查

#### 2.1 冲突检测

同一概念在不同文件中有不同定义：

```python
concept_definitions = defaultdict(list)

for entity_file in wiki/entities/*.md:
    concept = entity_file.frontmatter.get("concept")
    definition = extract_definition(content)
    
    concept_definitions[concept].append({
        "file": entity_file,
        "definition": definition
    })

# 检测冲突
for concept, defs in concept_definitions.items():
    if len(defs) > 1 and definitions_differ(defs):
        conflicts.append({
            "concept": concept,
            "definitions": defs,
            "action": "合并或明确区分"
        })
```

#### 2.2 重复内容检测

```python
# 使用内容相似度检测
for pair in file_pairs:
    similarity = calculate_similarity(file1, file2)
    if similarity > 0.8:
        duplicates.append({
            "files": [file1, file2],
            "similarity": similarity,
            "action": "合并或删除"
        })
```

#### 2.3 过期内容检测

```python
stale_content = []

for node in nodes:
    compiled_date = node.get("compiled")
    if is_stale(compiled_date, days=30):
        stale_content.append({
            "node": node,
            "last_updated": compiled_date,
            "days_stale": days_since(compiled_date),
            "action": "检查源文件是否更新"
        })
```

### Phase 3: 图谱检查

#### 3.1 节点一致性

```python
# nodes.jsonl 中的节点是否都有对应 wiki 文件
for node in nodes_jsonl:
    wiki_file = Path(node["path"])
    if not wiki_file.exists():
        missing_files.append(node)
```

#### 3.2 边有效性

```python
# edges.jsonl 中的 from/to 是否存在
for edge in edges_jsonl:
    if edge["from"] not in valid_nodes:
        invalid_edges.append(edge)
    if edge["to"] not in valid_nodes:
        invalid_edges.append(edge)
```

### Phase 4: Frontmatter 规范检查

```python
required_fields = ["id", "type", "source_file", "compiled", "tags"]

for wiki_file in wiki_files:
    frontmatter = parse_frontmatter(wiki_file)
    
    missing_fields = [f for f in required_fields if f not in frontmatter]
    
    if missing_fields:
        frontmatter_issues.append({
            "file": wiki_file,
            "missing": missing_fields,
            "action": "补充 frontmatter"
        })
```

---

## 输出格式

```
Wiki 健康检查报告
==================

✓ 结构检查
  断链: 2 处
    wiki/sources/abc.md → [[missing-concept]] (不存在)
    wiki/topics/xyz.md → [[deleted-node]] (不存在)
  
  孤立节点: 3 个
    wiki/entities/concept-a (无连接)
    wiki/sources/article-123 (无连接)
    wiki/topics/topic-x (无连接)

✓ 内容检查
  冲突定义: 1 处
    "事件处理" 在 2 个文件中有不同定义
      - wiki/entities/event-handler.md
      - wiki/patterns/event-extension-guide.md
  
  重复内容: 0 处
  
  过期内容: 5 个 (>30天)
    wiki/sources/old-article.md (45 天)
    wiki/entities/deprecated.md (60 天)

✓ 图谱检查
  节点一致性: ✓ 全部有对应文件
  边有效性: ✓ 全部有效

✓ Frontmatter 检查
  缺失字段: 2 个文件
    wiki/sources/new.md 缺少 "type"
    wiki/entities/x.md 缺少 "source_file"

总结: 2 断链, 3 孤立, 1 冲突, 5 过期, 2 frontmatter 问题
建议运行: /discover 获取详细修复建议
```

---

## 自动修复

用户确认后，可自动修复部分问题：

| 问题 | 自动修复 |
|------|----------|
| 断链 | 创建占位实体页 |
| 孤立节点 | 标记待处理，不自动删除 |
| 冲突定义 | 提示用户选择保留哪个 |
| 过期内容 | 检查源文件 hash，有更新则重新编译 |
| frontmatter 缺失 | 自动补充默认值 |

---

## 相关 Skills

- [/discover](discover) - 详细缺口分析
- [/ingest](ingest) - 更新过期内容