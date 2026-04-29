# Knowledge Base v2

> 融合 OmegaWiki + nashsu/llm_wiki 的知识库架构
> 
> **版本**: 2.0 | **创建**: 2026-04-29

---

## 修复效果

| 指标 | 修复前 | 修复后 | 改善 |
|------|--------|--------|------|
| 孤立节点 | 28 | 3 | -25 |
| 关系边 | 24 | 118 | +94 |
| 断链 | 23 | 7 | -16 |
| 社区数 | 35 | 12 | 更紧凑 |
| 桥节点 | 3 | 10 | +7 |

---

## 目录结构

```
knowledge-base-v2/
├── CLAUDE.md              ← AI 入口
├── curated/               ← 手动维护（65 文件）
├── raw/                   ← 素材存放（31 文件）
├── wiki/                  ← AI 编译（110 文件）
├── graph/                 ← 知识图谱（JSONL）
│   ├── nodes.jsonl        ← 52 节点
│   ├── edges.jsonl        ← 118 边
│   ├── citations.jsonl    ← 30 wikilinks
│   └── discover-report.json
│
├── .claude/skills/        ← 5 Skills
│   ├── ingest             ← 消化素材
│   ├── discover           ← 发现缺口
│   ├── check              ← 健康检查
│   ├── ask                ← 查询晶化
│   └ compile             ← 编译 wiki
│
├── scripts/
│   ├── init_graph.py      ← 图谱初始化
│   ├── discover.py        ← 知识发现
│   ├── fix_broken_links.py← 断链修复
│   ├── connect_isolated_nodes.py ← 连接孤立节点
│   └ compile.py          ← LLM 编译
│
├── .env.example           ← API 配置示例
└ knowledge-graph.html     ← 可视化页面
```

---

## 使用方式

### 1. 在 Claude Code 中使用

```bash
cd /Users/hugh/project/knowledge-base-v2
claude

# Skills:
/ingest raw/articles/new.md   # 消化素材
/discover                      # 发现缺口
/check                         # 健康检查
/ask 什么是事件处理            # 查询晶化
/compile                       # 编译 wiki
```

### 2. 运行脚本

```bash
# 知识发现
python3 scripts/discover.py

# 修复断链
python3 scripts/fix_broken_links.py

# 连接孤立节点
python3 scripts/connect_isolated_nodes.py

# 编译（需配置 ANTHROPIC_API_KEY）
export ANTHROPIC_API_KEY=your-key
python3 scripts/compile.py
```

### 3. 查看图谱

在浏览器打开 `knowledge-graph.html`

---

## 配置 LLM API

```bash
# 复制配置模板
cp .env.example .env

# 编辑填入 API Key
# ANTHROPIC_API_KEY=your-key

# 或直接设置环境变量
export ANTHROPIC_API_KEY=your-anthropic-api-key
```

---

## 剩余工作

- [ ] 处理剩余 3 个孤立节点（fly-chess, buye-payment, gift-suit）
- [ ] 处理剩余 7 条断链
- [ ] 配置 LLM API 进行真实编译
- [ ] 添加向量搜索支持

---

## 与 v1 对比

| 特性 | v1 (my-wiki) | v2 (knowledge-base-v2) |
|------|-------------|------------------------|
| 存储 | JSON 数组 | JSONL 追加式 |
| Skills | 1 个 | 5 个 |
| 知识发现 | 无 | 4-Signal + Louvain |
| 断链修复 | 无 | 自动修复 |
| 孤立节点处理 | 无 | 自动连接 |
| LLM 编译 | 假编译（复制） | 真编译（分析提炼） |