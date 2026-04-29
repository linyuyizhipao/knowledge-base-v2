---
id: patterns/project-learning-framework
label: project-learning-framework
source: /Users/hugh/project/my-wiki/curated/patterns/project-learning-framework.md
role: 规范
compiled: 2026-04-28
source_hash: b35ab3a6cd70bcbbf60832b788b2ba2f
---

> 可复用的新项目学习方法论

## 学习目标

1. **理解项目结构** - 目录组织、入口点、模块引用关系
2. **掌握技术栈** - 核心库、框架、基础设施
3. **梳理业务能力** - 事件处理、API、定时任务
4. **沉淀知识文档** - 可复用的参考文档

## 通用学习阶段

| 阶段 | 时间 | 目标 | 关键命令 |
|------|------|------|---------|
| 0. 分支确认 | 5min | 明确学习哪个分支 | `git branch`, `git checkout` |
| 1. 项目结构 | 1-2h | 建立全景认知 | `find . -name "main.go"`, `ls app/` |
| 2. 技术栈 | 1-2h | 理解框架和技术 | `cat go.mod`, grep 框架关键字 |
| 3. 业务能力 | 2-4h | 梳理核心业务 | `ls cmd/internal/`, `ls app/api/` |
| 4. 知识沉淀 | 1-2h | 创建参考文档 | 输出 01-structure.md ~ 08-event.md |

## 输出文档结构

```
knowledge/projects/<project-name>/
├── 01-structure.md      # 项目结构
├── 02-architecture.md   # 架构分层
├── 03-development.md    # 开发流程
├── 04-api.md            # API 清单
├── 05-service.md        # Service 清单
├── 06-dao.md            # DAO 模式
├── 07-infra.md          # 基础设施
└── 08-event-capabilities.md  # 事件能力
```

## 项目特定学习重点

### slp-common-rpc（支付消费中台）

**重点**：三阶段消费模型 + 二段事务
- Stage0：预处理 → Stage1：扣钱+写子事务 → Stage2：业务处理（Kafka 触发）

### slp-go / slp-room（HTTP + CMD）

**重点**：事件驱动架构 + NSQ 消费者
- 每个 CMD 模块监听一个 Topic
- 事件处理：HandleEventMap 或 switch-case

## 工具命令速查

```bash
find . -name "*.go" | wc -l          # Go 文件数
find ./cmd/internal -type d | wc -l  # cmd 模块数
grep -r "HandleEventMap" app/        # 查找事件路由
grep -r "NewNsqWorker" cmd/          # 查找 NSQ 消费者
```
