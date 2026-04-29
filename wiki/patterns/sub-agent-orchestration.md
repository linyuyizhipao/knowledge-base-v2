---
id: patterns/sub-agent-orchestration
label: sub-agent-orchestration
source: /Users/hugh/project/my-wiki/curated/patterns/sub-agent-orchestration.md
role: 规范
compiled: 2026-04-28
source_hash: a2d14a9d4638ed04f6784b0c55b8fead
---

> AI 自主触发策略 — 无需用户手动指定

## 复杂度分级

| 复杂度 | 触发条件 | 编排方式 | 示例 |
|--------|---------|---------|------|
| **简单** | 单文件，<50行 | 直接写 | 加字段、修 null check |
| **中等** | 多文件，单项目 | Explore → 编写 → code-reviewer | 新增 API + Service + DAO |
| **复杂** | 跨项目/架构级 | Plan → Explore → general-purpose → code-reviewer | 369 跨项目改造 |

## Agent 类型

| Agent | 能力 | 用途 |
|-------|------|------|
| Explore | 只读搜索 | 定位代码、查找定义、调研模式 |
| Plan | 分析设计 | 设计方案、识别架构权衡、拆分任务 |
| general-purpose | 全工具 | 编写代码、创建文件、运行测试 |
| code-reviewer | 全工具 | 审查代码一致性、规范检查 |

## 决策流程

```
来了新任务 → 涉及几个项目？
├─ 0-1个，且 < 50行 → 模式 A（直接写）
├─ 0-1个，且 > 50行 → 模式 B（调研+实现+审查）
└─ 2个以上或架构级 → 模式 C（设计+调研+实现+审查）
```

## 与 AI_WORKFLOW 的对应关系

| AI_WORKFLOW 步骤 | 触发的 agent |
|------------------|-------------|
| 步骤 2：知识检索 | Explore（中/复杂任务） |
| 步骤 3：方案设计 | Plan（复杂任务） |
| 步骤 4：实施开发 | general-purpose（并行实现） |
| 步骤 5：合入部署 | code-reviewer（审查环节） |

用户可通过 `"不用 sub-agent"` 或 `"直接用 sub-agent"` 覆盖默认策略。
