---
name: compile-diff
description: 基于 git 变更的增量编译。检测 curated 目录下的新增/修改文件，只编译变更的部分。用户说"编译变更"、"增量编译"、"compile diff"时调用。
---

# /compile-diff Skill

## 触发关键词

- "编译变更"
- "增量编译"
- "compile diff"
- "只编译改动的"
- "git diff 编译"

---

## 工作流程

### Step 1: 检测 Git 变更

```bash
# 获取变更文件列表
git diff HEAD~1 --name-only

# 或检测 staged 变更
git diff --cached --name-only

# 或检测所有变更（包括未 staged）
git diff HEAD --name-only
git ls-files --others --exclude-standard
```

### Step 2: 筛选 Curated 文件

只处理 `curated/` 目录下的 `.md` 文件：

```python
def filter_curated_files(files):
    return [
        f for f in files
        if f.startswith("curated/")
        and Path(f).suffix == ".md"
    ]
```

### Step 3: 检查增量缓存

使用 SHA256 hash 检查文件是否真正变更：

```python
def needs_compile(source_file):
    cached_hash = get_cached_hash(node_id)
    current_hash = get_file_hash(source_file)
    
    if cached_hash == current_hash:
        return False  # 未变更，跳过
    
    return True  # 需要编译
```

### Step 4: 编译变更文件

对每个需要编译的文件执行 LLM 分析：

```
输入: curated/patterns/new-guide.md
输出: wiki/patterns/new-guide.md (精简版)
更新: graph/nodes.jsonl, graph/edges.jsonl
```

### Step 5: 更新知识图谱

```python
# 添加新节点
nodes.jsonl += {"id": "patterns/new-guide", ...}

# 添加发现的关系
edges.jsonl += {"from": "patterns/new-guide", "to": "CODING_STANDARDS", ...}
```

---

## 使用方式

### 基本用法

```
用户: 编译变更

AI 执行:
  1. python3 scripts/compile_diff.py
  2. 读取 .compile-pending.json
  3. 对待编译文件执行 LLM 分析
  4. 更新 wiki + graph
  5. 输出报告
```

### 指定检测范围

```
# 从指定 commit 开始
python3 scripts/compile_diff.py --since=abc123

# 只检测 staged 变更（准备提交的）
python3 scripts/compile_diff.py --staged

# 检测所有变更（包括未 staged）
python3 scripts/compile_diff.py --all
```

---

## 输出格式

```
=== Git 变更增量编译 ===

Step 1: 检测变更文件...
  检测范围: HEAD~1 → HEAD
  变更文件总数: 5

Step 2: 筛选可编译文件...
  curated 变更: 2
  - curated/patterns/new-guide.md (新增)
  - curated/core/updated-standard.md (修改)

Step 3: 检查编译需求...
  ✓ curated/patterns/new-guide.md (新增)
  - curated/core/updated-standard.md (unchanged, 跳过)

Step 4: 编译 1 个文件...
  ✓ curated/patterns/new-guide.md → wiki/patterns/new-guide.md

=== 编译完成 ===
变更文件: 5
待编译: 2
已处理: 1

下一步:
  在对话中说 '编译这些新文件'
```

---

## 增量缓存机制

| 文件状态 | 处理方式 |
|----------|---------|
| 新增文件 | 编译 |
| 修改文件 | 编译（hash 变化） |
| 未变更文件 | 跳过（hash 相同） |
| 删除文件 | 从图谱移除 |

---

## 与全量编译的对比

| 维度 | 全量编译 | 增量编译 |
|------|---------|---------|
| 检测范围 | 全部 curated | git diff 变更 |
| 编译文件 | 所有 | 仅变更 |
| Token 消耗 | 高 | 低 |
| 适用场景 | 初始化/大更新 | 日常增量 |

---

## 相关 Skills

- /compile - 全量编译
- /check - 健康检查
- /discover - 知识发现