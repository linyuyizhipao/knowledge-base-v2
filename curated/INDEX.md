# 知识库索引

> **AI 写文档前必查**: 先搜索本文档，确认是否已有相关内容
>
> **版本**: 2.1 | **更新**: 2026-04-25
>
> **知识图谱**: [knowledge-graph.json](./knowledge-graph.json) - AI 可直接读取获取关联关系

---

## 📋 已有文档清单

### 核心文档

| 文档 | 路径 | 说明 |
|------|------|------|
| AI 统一入口 | [../AGENTS.md](../AGENTS.md) | 所有 AI 工具必读 |
| 核心禁令 | [../CODING_STANDARDS.md](../CODING_STANDARDS.md) | 编码禁止事项 |
| 开发流程 | [../AI_WORKFLOW.md](../AI_WORKFLOW.md) | 5阶段开发流程 |
| 快速参考 | [../QUICK_REFERENCE.md](../QUICK_REFERENCE.md) | 命令速查 |

### 项目知识 (projects/)

| 项目 | 入口 | 已有文档 |
|------|------|----------|
| **slp-go** | [projects/slp-go/](projects/slp-go/) | 01-structure, 02-architecture, 03-development, 04-api, 05-service, 06-dao, 07-infra, 08-business-369-recharge, 09-event-capabilities |
| **slp-room** | [projects/slp-room/](projects/slp-room/) | 01-structure, 02-architecture, 01-event-capabilities |
| **slp-starship** | [projects/slp-starship/](projects/slp-starship/) | 01-structure, 01-event-capabilities |
| **slp-common-rpc** | [projects/slp-common-rpc/](projects/slp-common-rpc/) | CORE_LEARNING |

### 跨项目业务 (cross-projects/)

| 业务 | 入口 | 涉及项目 |
|------|------|----------|
| **369元观光团** | [cross-projects/369-recharge/overview.md](cross-projects/369-recharge/overview.md) | slp-room, slp-go |
| **聊天室房型** | [cross-projects/chatroom/](cross-projects/chatroom/) | slp-room, slp-go, slp-common-rpc |
| **不夜支付** | [cross-projects/buye-payment/overview.md](cross-projects/buye-payment/overview.md) | slp-php, slp-ee-config |
| **飞行棋** | [cross-projects/fly-chess/overview.md](cross-projects/fly-chess/overview.md) | slp-room, slp-gateway, slp-go, slp-php |
| **祈福活动** | [cross-projects/prayer-activity/](cross-projects/prayer-activity/) | slp-starship, slp-go |
| **装扮物品** | [cross-projects/decorate-commodity-use/](cross-projects/decorate-commodity-use/) | slp-php, slp-go |
| **礼包套装** | [cross-projects/gift-suit/](cross-projects/gift-suit/) | slp-go |
| **大哥管理** | [cross-projects/big-brother/](cross-projects/big-brother/) | slp-go |

### 通用模式 (patterns/)

| 模式 | 路径 | 说明 |
|------|------|------|
| 业务开发规范 | [patterns/slp-business-development-standard.md](patterns/slp-business-development-standard.md) | 全链路开发指南 |
| 事件拓展指南 | [patterns/event-extension-guide.md](patterns/event-extension-guide.md) | 事件处理三种模式 |
| NSQ使用规范 | [patterns/nsq-usage.md](patterns/nsq-usage.md) | NSQ发送/消费标准 |
| CMD模块标准 | [patterns/cmd-module-standard.md](patterns/cmd-module-standard.md) | CMD模块结构 |
| 代码规模标准 | [patterns/code-scale-standard.md](patterns/code-scale-standard.md) | 函数文件规模 |
| 分层架构共识 | [patterns/architecture-layered-standard.md](patterns/architecture-layered-standard.md) | 层次职责边界 |
| 业务模块标准 | [patterns/business-module-standard.md](patterns/business-module-standard.md) | 常量/Service规范 |
| 业务代码示例 | [patterns/business-code-example.md](patterns/business-code-example.md) | 完整业务模块示例 |
| 数据库命名 | [patterns/database-naming-conventions.md](patterns/database-naming-conventions.md) | 数据库命名规范 |
| 开发部署流程 | [patterns/dev-to-dev-deployment.md](patterns/dev-to-dev-deployment.md) | 部署流程 |
| 项目学习框架 | [patterns/project-learning-framework.md](patterns/project-learning-framework.md) | 新项目学习方法论 |

### 工具文档 (tools/)

| 工具 | 路径 | 说明 |
|------|------|------|
| slpctl | [tools/slpctl.md](tools/slpctl.md) | 完整命令参考 |
| slpctl使用指南 | [tools/slpctl-usage-guide.md](tools/slpctl-usage-guide.md) | 8步开发流程 |
| gh PR分析 | [tools/gh-pr-analysis.md](tools/gh-pr-analysis.md) | PR分析命令 |
| diff-impact | [tools/diff-impact-user-guide.md](tools/diff-impact-user-guide.md) | 变更影响分析工具 |
| diff-impact脚本 | [../scripts/diff-impact.sh](../scripts/diff-impact.sh) | 主脚本 |
| diff-impact验证 | [../scripts/validate-diff-impact.sh](../scripts/validate-diff-impact.sh) | 验证脚本 |

---

## 🔍 写文档前的检查流程

```
步骤 1: 确认文档类型
        ├── 单项目知识 → projects/<project>/
        ├── 跨项目业务 → cross-projects/<business>/
        ├── 通用模式 → patterns/
        └── 反模式 → anti-patterns/

步骤 2: 搜索是否已存在
        在本文档中搜索关键词

步骤 3: 确认文档命名
        ├── 项目知识: 01-structure, 02-architecture, 03-development...
        ├── 跨项目业务: overview.md, <project>.md
        └── 模式/反模式: <descriptive-name>.md

步骤 4: 使用标准模板（见 AGENTS.md）

步骤 5: 更新本文档索引
```

---

## 📝 文档命名规范

### 项目知识文档编号

| 编号 | 用途 |
|------|------|
| 01 | 项目结构 (structure) |
| 02 | 架构分层 (architecture) |
| 03 | 开发流程 (development) |
| 04 | API 模式 (api) |
| 05 | Service 模式 (service) |
| 06 | DAO 模式 (dao) |
| 07 | 基础设施 (infra) |
| 08 | 业务案例 (business-*) |
| 09 | 事件能力 (event-capabilities) |

---

## ⚠️ 常见错误

| 错误 | 正确做法 |
|------|----------|
| 在项目目录创建知识文档 | 在 `${HARNESS_HOME}/knowledge/` 创建 |
| 使用自定义文档命名 | 遵循本文档命名规范 |
| 不更新索引 | 写完文档后更新本文档 |
| 重复创建已存在文档 | 先搜索本文档确认 |

---

**维护说明**: 每次新增/删除文档后，必须更新本文档索引
