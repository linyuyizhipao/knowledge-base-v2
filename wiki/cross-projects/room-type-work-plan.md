---
id: room-type-work-plan
label: 房间类型拓展工作计划
source: curated/cross-projects/chatroom/room-type-work-plan.md
business: chatroom
compiled: 2026-04-25
links:
  - room-type-concept
  - room-type-development
---

# 房间类型拓展工作计划

> 按工作日拆分的可执行计划（以大哥房为例）

## 开发流程

| 天数 | 阶段 | 任务 |
|------|------|------|
| 第 1 天 | 数据库 + DAO | DDL 编写 → slpctl gen -t → 验证 DAO |
| 第 2 天 | Proto + Service | Proto 定义 → make proto → Service 框架 |
| 第 3-4 天 | Service 业务 | 核心业务实现 + 单元测试 |
| 第 5 天 | API 层 | API 编写 → 路由注册 → 测试 |
| 第 6-7 天 | CMD 消费者 | NSQ 消费者 → 事件 Handler |
| 第 8 天 | 配置注册 | SQL 配置 → NSQ Topic 配置 |
| 第 9-10 天 | 跨服务协调 | slp-room、slp-common-rpc、slp-php、slp-gateway |
| 第 11 天 | 部署配置 | Helm 配置 → 测试环境部署 |
| 第 12 天 | 测试 + 文档 | 功能测试 → 文档沉淀 |

## 验收标准

| 阶段 | 验收项 |
|------|--------|
| DAO 生成 | 编译通过，DAO 方法可正常调用 |
| Service | 单元测试覆盖率 > 60% |
| API | 参数校验生效，响应格式正确 |
| CMD | NSQ 消息可正常消费 |
| 配置 | 房间类型可正常创建 |
| 部署 | 所有服务正常启动，日志无报错 |

## 参考文档

- room-type-concept.md - 房间类型概念介绍
- room-type-development.md - 房间类型开发完全指南