---
id: DOCUMENT_LOCATION_RULES
label: 文档存放规则
source: curated/DOCUMENT_LOCATION_RULES.md
role: 规则
compiled: 2026-04-27
---

# 文档存放规则

## 快速决策

```
知识涉及范围？
  单个项目 → projects/<project>/
  多个项目 → cross-projects/<business>/
  通用模式 → patterns/
  常见错误 → anti-patterns/
```

## 单需求单文件原则

**禁令：同一需求的知识沉淀、技术设计、实施计划必须聚合在一个文件内，禁止分散到多处。**

| 错误做法 | 正确做法 |
|----------|----------|
| 踩坑在 `projects/`、设计在 `cross-projects/design.md`、计划在 `cross-projects/implementation-plan.md` | 全部内容合并在一个文件，选定**唯一路径** |
| 目录下放 `design.md` + `plan.md` + `knowledge.md` 三件套 | 一个需求一个 `.md`，用章节标题区分 |

**判定标准**：读者只打开一个文件就能理解需求的**全部上下文**（背景、方案、踩坑、计划）。

## 历史案例

| 案例 | 原位置 | 新位置 | 说明 |
|------|--------|--------|------|
| 祈福抽奖 | ~~projects/slp-starship/~~ | `cross-projects/prayer-activity/` | 涉及 slp-go RPC |
| 农场 appid 隔离 | ~~projects/ + cross-projects/ 散 3 文件~~ | `projects/slp-starship/02-farm-appid-isolation.md` | 合并为单文件 |
