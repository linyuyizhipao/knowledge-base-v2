# Knowledge Base v2 - AI 入口

> **融合 OmegaWiki + nashsu/llm_wiki 的知识库架构**
>
> 版本: 2.0 | 更新: 2026-04-28

---

## 核心改进（vs v1）

| 维度 | v1 (my-wiki) | v2 (knowledge-base-v2) |
|------|-------------|------------------------|
| **存储** | JSON 数组 | JSONL 追加式 |
| **编译** | 复制文件 | LLM Two-Step 分析 |
| **链接** | 手动定义 | 自动发现 (4-Signal) |
| **社区** | 无 | Louvain 自动聚类 |
| **缺口** | 无 | 孤立节点 + 低密度社区 |
| **Skills** | 1 个 | 4 个 (/ingest, /discover, /check, /ask) |

---

## 目录结构

```
knowledge-base-v2/
├── CLAUDE.md              ← AI 入口（本文件）
│
├── curated/               ← 精心准备（手动维护）
│   ├── core/              ← 核心文档
│   ├── patterns/          ← 开发规范
│   ├── tools/             ← 工具文档
│   ├── projects/          ← 项目知识
│   └── cross-projects/    ← 跨项目业务
│
├── raw/                   ← 随意扔入（素材）
│   ├── articles/          ← 网页文章
│   ├── notes/             ← 随手笔记
│   ├── clippings/         ← 浏览器剪藏
│   ├── pdfs/              ← PDF 文件
│   └── curls/             ← curl 命令
│
├── wiki/                  ← AI 编译（自动生成）
│   ├── sources/           ← 素材摘要
│   ├── entities/          ← 概念实体
│   ├── topics/            ← 主题汇总
│   ├── synthesis/         ← 深度报告
│   ├── queries/           ← 已问答问题（晶化）
│   └── curls/             ← curl 命令整理
│
├── graph/                 ← 知识图谱（JSONL）
│   ├── nodes.jsonl        ← 节点索引
│   ├── edges.jsonl        ← 语义关系
│   ├── citations.jsonl    ← wikilink 引用
│   ├── co-occurrence.jsonl← 实体共现
│   └── discover-report.json ← 发现报告
│
├── .claude/
│   └ skills/              ← Claude Code Skills
│   │   ├── ingest/        ← /ingest 消化素材
│   │   ├── discover/      ← /discover 发现缺口
│   │   ├── check/         ← /check 健康检查
│   │   ├── ask/           ← /ask 查询晶化
│   │   └ compile/         ← /compile 编译 wiki
│   └
│   └ settings.json        ← Claude Code 配置
│
└── scripts/
    ├── init_graph.py      ← 图谱初始化
    ├── discover.py        ← 知识发现模块
    └ compile.py           ← 编译脚本
```

---

## AI 使用流程

### 1. 启动加载

```
AI 启动时自动加载:
  1. CLAUDE.md (本文件)
  2. graph/nodes.jsonl (节点概览)
  3. knowledge-index.json (shortcuts)
```

### 2. Skills 调用

| 用户说 | 调用 Skill |
|--------|-----------|
| "消化这个文件" | /ingest |
| "发现知识缺口" | /discover |
| "检查 wiki 健康状况" | /check |
| "xxx 是什么" | /ask |
| "编译 wiki" | /compile |

### 3. 查询流程

```
用户问题
    ↓
Tokenized Search → Vector Search → Graph Expansion
    ↓
Budget Control → Context Assembly
    ↓
LLM 回答（带引用）
    ↓
晶化保存到 wiki/queries/
```

---

## 快速定位 (shortcuts)

| 关键词 | wiki 文件 |
|--------|----------|
| 核心禁令 | wiki/core/coding-standards.md |
| 开发流程 | wiki/patterns/slp-business-development-standard.md |
| 事件开发 | wiki/patterns/event-extension-guide.md |
| slpctl | wiki/tools/slpctl-usage-guide.md |
| slp-go结构 | wiki/projects/slp-go/01-structure.md |
| slp-room结构 | wiki/projects/slp-room/01-structure.md |
| 369业务 | wiki/cross-projects/369-recharge/overview.md |
| 口令功能 | wiki/cross-projects/big-brother/README-PASSCODE.md |

---

## 知识图谱结构

### 节点类型

| type | 说明 | 目录 |
|------|------|------|
| source | 素材摘要 | wiki/sources/ |
| entity | 概念实体 | wiki/entities/ |
| topic | 主题汇总 | wiki/topics/ |
| query | 已问答 | wiki/queries/ |
| standard | 开发规范 | wiki/patterns/ |
| project | 项目知识 | wiki/projects/ |
| cross | 跨项目 | wiki/cross-projects/ |

### 关系类型

| type | 权重 | 说明 |
|------|------|------|
| must_read | 3.0 | 必读关联 |
| depends_on | 2.0 | 依赖关系 |
| builds_on | 2.0 | 构建关系 |
| relates_to | 1.0 | 相关关系 |
| wikilink | 0.5 | wiki 引用 |
| source_overlap | 4.0 | 共用素材 |

---

## 4-Signal 相关性模型

| Signal | 权重 | 说明 |
|--------|------|------|
| Direct link | ×3.0 | 直接 [[wikilink]] 连接 |
| Source overlap | ×4.0 | 共用 raw 素材 |
| Adamic-Adar | ×1.5 | 共同邻居加权 |
| Type affinity | ×1.0 | 同类型节点 |

---

## 核心规则 (从 v1 继承)

### 编码禁令

| 禁止 | 正确做法 | 原因 |
|------|----------|------|
| 手写 API | slpctl code -api | 工具自动生成骨架 |
| 循环 IO | 批量查询 + map 组装 | 避免 N+1 查询 |
| 阻塞主 goroutine | 异步任务队列 / NSQ | 防止请求堆积 |
| 绕过事件总线 | 发布事件解耦 | 模块通信规范 |
| 函数过大 | 按功能拆分 | 可维护性 |

---

## 开发任务指南

当用户请求开发任务时，按以下顺序读取：

```
必读:
  1. wiki/core/coding-standards.md (禁令)
  2. wiki/patterns/slp-business-development-standard.md (流程)
  3. wiki/tools/slpctl-usage-guide.md (工具)

按项目补充:
  - slp-go: wiki/projects/slp-go/01-structure.md
  - slp-room: wiki/projects/slp-room/01-structure.md
  - slp-starship: wiki/projects/slp-starship/01-structure.md

按任务类型补充:
  - 新 API: wiki/patterns/slpctl-usage-guide.md
  - 新事件: wiki/patterns/event-extension-guide.md
  - 跨业务: wiki/cross-projects/{业务}/overview.md
```

---

## 使用示例

### 消化新素材

```
用户: 把 raw/articles/new-guide.md 消化一下

AI:
  /ingest raw/articles/new-guide.md
  
  分析完成！
  - 发现 3 个关键概念
  - 建议链接到 5 个现有节点
  - 生成 wiki/sources/new-guide.md
  - 更新 graph/edges.jsonl (+5 条)
```

### 查询知识

```
用户: 什么是 NSQ 的使用规范？

AI:
  /ask NSQ 使用规范
  
  查询命中 3 个文档:
  [1] wiki/patterns/nsq-usage.md
  [2] wiki/patterns/event-extension-guide.md
  [3] wiki/projects/slp-go/08-business-369-recharge.md
  
  回答: ... (带引用)
  
  已晶化到 wiki/queries/nsq-usage-question.md
```

### 发现缺口

```
用户: 知识库有什么需要补充的？

AI:
  /discover
  
  发现缺口:
  - 3 个孤立节点
  - 1 个低密度社区 (cohesion=0.08)
  - 5 条断链
  
  建议研究:
  1. 搜索 "xxx 最佳实践"
  2. 创建 wiki/topics/社区主题.md
```

---

## 与 v1 的关系

- v1 (`my-wiki`) 继续保留使用
- v2 (`knowledge-base-v2`) 是重构版本
- 可逐步迁移 v1 内容到 v2
- 最终 v2 将替代 v1