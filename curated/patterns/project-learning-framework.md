# 项目学习框架

> 一套可复用的方法论，用于快速学习并沉淀任何新项目的知识

**版本**: 1.1 | **最后更新**: 2026-04-06

---

## 学习目标

1. **理解项目结构** - 目录组织、入口点、模块引用关系
2. **掌握技术栈** - 核心库、框架、基础设施
3. **梳理业务能力** - 事件处理、API、定时任务
4. **沉淀知识文档** - 可复用的参考文档

---

## 项目特定学习指引

不同项目有不同的学习重点，以下是已学习项目的定制化指引：

### slp-common-rpc：支付消费中台

**学习重点**：三段消费模型 + 二段事务 + 部署流程

| 学习主题 | 关键文件 | 学习方式 |
|----------|---------|---------|
| 三阶段消费模型 | `rpc/server/internal/consume/stage1/server.go`<br>`rpc/server/internal/consume/stage2/consume_stage2.go` | 阅读代码 + 画流程图 |
| 二段事务 | `rpc/server/internal/consume/stage1/server.go:200-250`<br>`rpc/server/internal/consume/stage2/handler_stage2.go` | 对比一段事务方案 |
| 场景处理器 | `rpc/server/internal/consume/stage2/chat_gift.go` | 复杂度分析（RPC/NSQ/DB 数量） |
| RPC 客户端 | `rpc/client/*.go` | 理解单例模式 + 适配器封装 |
| 59 种消费类型 | `app/pb/rpc.pay.consume/consume_param.pb.go` | 分类整理 |
| 部署流程 | `deploy/helm_dev/`, `deploy/deploy_rpc.sh` | 本地部署实践 |

**核心概念**：
- Stage0：预处理（校验、锁）
- Stage1：扣钱 + 写子事务（同步）
- Stage2：业务处理（异步，Kafka 触发）
- 分支管理：`hu/<需求名>` → PR → `master` → 测试服务器

**架构问题**：
- 当前代码违反开闭原则（新增业务需修改 `handler_stage2.go`）
- `ChatGiftScene` 复杂度极高（1000+ 行代码）
- 解决方案：Pipeline 配置化引擎

**学习产出**：
- [CORE_LEARNING.md](../projects/slp-common-rpc/CORE_LEARNING.md) - 核心学习文档
- [slpctl ci 构建命令](../tools/slpctl-ci.md) - 完整部署指南

---

### slp-go / slp-room：HTTP + CMD 项目

**学习重点**：事件驱动架构 + NSQ 消费者

| 学习主题 | 关键文件 | 学习方式 |
|----------|---------|---------|
| 项目结构 | `app/`, `cmd/internal/`, `rpc/` | 目录扫描 |
| 事件处理 | `app/service/*/service.go` | 查找 `HandleEventMap` |
| NSQ 消费者 | `cmd/internal/*/service.go` | 统计 Topic |
| API 模块 | `app/api/` | 路由分析 |

**核心概念**：
- 事件驱动：通过 NSQ 消息触发业务逻辑
- 消费者模式：每个 CMD 模块监听一个 Topic
- 并发控制：通过 `concurrent` 参数控制协程数

**学习产出**：
- [structure.md](../projects/slp-go/structure.md) - 项目结构
- [event-capabilities.md](../projects/slp-go/event-capabilities.md) - 事件能力清单

---

## 通用学习流程

### 阶段 0：分支确认（5 分钟）

**目标**：明确学习哪个分支的代码

#### 步骤 0.1：查看当前分支

```bash
# 查看当前分支
git branch

# 查看远程分支
git branch -r
```

#### 步骤 0.2：确认学习目标

| 场景 | 分支选择 |
|------|---------|
| 学习生产代码 | `master` / `main` |
| 学习开发中功能 | `develop` / `feature-xxx` |
| 学习最新代码 | `develop` |
| 稳定版本参考 | `release/*` |

#### 步骤 0.3：切换到目标分支

```bash
# 切换到目标分支
git checkout master

# 拉取最新代码
git pull origin master
```

**记录要点**：
- [ ] 当前分支：`________`
- [ ] 分支说明：（可选）为什么学习这个分支
- [ ] 代码版本：`git rev-parse HEAD`（用于文档记录）

---

### 阶段 1：项目结构（1-2 小时）

**目标**：建立项目全景认知

#### 步骤 1.1：根目录扫描

```bash
# 查看根目录结构
ls -la <project-root>/

# 查看一级目录
find <project-root>/ -maxdepth 1 -type d | sort
```

**记录要点**：
- [ ] 项目类型（HTTP/RPC/CMD）
- [ ] 主要目录及其用途
- [ ] 配置文件位置
- [ ] 构建脚本（Makefile, *.sh）

#### 步骤 1.2：入口点识别

```bash
# 查找所有 main.go
find <project-root>/ -name "main.go" | head -20
```

**记录要点**：
- [ ] HTTP 入口：`<project-root>/main.go` 或 `app/main.go`
- [ ] RPC 入口：`rpc/server/main.go`
- [ ] CMD 入口：`cmd/main.go`

#### 步骤 1.3：目录深度统计

```bash
# 统计各目录文件数
find <project-root>/app -type d | wc -l
find <project-root>/cmd/internal -type d | wc -l

# 查看关键目录
ls -la <project-root>/app/
ls -la <project-root>/cmd/internal/ | head -30
```

**记录要点**：
- [ ] API 模块数量
- [ ] Service 模块数量
- [ ] DAO 层规模
- [ ] CMD 模块数量

#### 步骤 1.4：模块引用关系

阅读 `go.mod` 了解依赖：

```bash
cat <project-root>/go.mod | head -50
```

**记录要点**：
- [ ] 核心框架（如 github.com/gogf/gf）
- [ ] 内部模块依赖
- [ ] 第三方依赖

---

### 阶段 2：技术栈分析（1-2 小时）

**目标**：理解项目使用的技术和框架

#### 步骤 2.1：Web 框架

查看路由定义和启动逻辑：

```bash
# 查找路由定义
grep -r "router\|route\|Register" app/app.go 2>/dev/null

# 查看启动入口
cat app/app.go
```

**记录要点**：
- [ ] Web 框架（Gin, Echo, GoFrame 等）
- [ ] 启动流程
- [ ] 中间件注册

#### 步骤 2.2：数据库/缓存

```bash
# 查找 Redis 使用
grep -r "redis\." app/service/ | head -10

# 查找 MySQL 使用
grep -r "gorm\|sql\." app/service/ | head -10
```

**记录要点**：
- [ ] ORM 框架（GORM, Ent, 手写 SQL）
- [ ] Redis 客户端
- [ ] 连接池配置

#### 步骤 2.3：消息队列

```bash
# 查找 NSQ 使用
grep -r "NewNsqWorker\|nsq\." cmd/ | head -20

# 查找 Kafka 使用
grep -r "kafka\." cmd/ | head -10
```

**记录要点**：
- [ ] 消息队列类型（NSQ, Kafka）
- [ ] 消费者模式
- [ ] Topic 命名规范

#### 步骤 2.4：RPC 通信

```bash
# 查找 RPC 定义
ls -la rpc/

# 查找 RPC 客户端
ls -la rpc/client/
```

**记录要点**：
- [ ] RPC 框架（gRPC, rpcx）
- [ ] 服务定义位置
- [ ] 客户端封装方式

---

### 阶段 3：业务能力梳理（2-4 小时）

**目标**：理解项目处理的核心业务

#### 步骤 3.1：事件能力（CMD 模块）

```bash
# 查看所有 CMD 模块
ls cmd/internal/

# 查看每个模块的 Topic
grep -rh "Topic\|topic" cmd/internal/*/service.go cmd/internal/*/consumer.go 2>/dev/null | head -50
```

**记录要点**：
- [ ] 所有 Topic 列表
- [ ] 事件处理方式（HandleEventMap / switch-case）
- [ ] 事件常量定义位置

#### 步骤 3.2：API 能力

```bash
# 查看 API 模块
ls app/api/

# 查看路由定义
cat app/route.go | head -100
```

**记录要点**：
- [ ] API 模块列表
- [ ] 路由分组
- [ ] 核心 API

#### 步骤 3.3：Service 能力

```bash
# 查看 Service 模块
ls app/service/ | head -30

# 查看核心 Service 实现
cat app/service/<module>/service.go | head -50
```

**记录要点**：
- [ ] Service 模块列表
- [ ] 核心业务逻辑
- [ ] 跨 Service 调用

---

### 阶段 4：知识沉淀（1-2 小时）

**目标**：创建可复用的参考文档

#### 输出文档结构

```
knowledge/projects/<project-name>/
├── 01-structure.md         # 项目结构（目录、入口、依赖）
├── 02-architecture.md      # 架构分层（API/Service/DAO）
├── 03-development.md       # 开发流程（启动、调试、部署）
├── 04-api.md               # API 模块清单
├── 05-service.md           # Service 模块清单
├── 06-dao.md               # DAO 模式
├── 07-infra.md             # 基础设施（Redis/Kafka/NSQ）
└── 08-event-capabilities.md # 事件能力清单（如有 CMD）
```

#### 文档模板

每个文档包含：
- **概述** - 1-2 句话说明
- **核心内容** - 列表/表格/代码示例
- **位置指引** - 文件路径
- **最佳实践** - 注意事项/约束

---

## 快速检查清单

### 项目结构
- [ ] 已识别所有入口点（HTTP/RPC/CMD）
- [ ] 已绘制目录结构图
- [ ] 已统计模块数量

### 技术栈
- [ ] 已确定 Web 框架
- [ ] 已确定 ORM/数据库访问方式
- [ ] 已确定消息队列使用方式
- [ ] 已确定 RPC 通信方式

### 业务能力
- [ ] 已列出所有 CMD 模块
- [ ] 已列出所有 API 模块
- [ ] 已列出所有 Topic 和事件

### 知识沉淀
- [ ] 已创建结构文档
- [ ] 已创建架构文档
- [ ] 已创建事件能力清单
- [ ] 已更新全局知识索引

---

## 工具命令速查

```bash
# 项目统计
find . -name "*.go" | wc -l           # Go 文件数
find ./app -type d | wc -l            # app 目录数
find ./cmd/internal -type d | wc -l   # cmd 模块数

# 代码搜索
grep -r "HandleEventMap" app/         # 查找 HandleEventMap 模式
grep -r "NewNsqWorker" cmd/           # 查找 NSQ 消费者
grep -r "type.*struct" app/service/   # 查找 Service 定义

# 依赖分析
go mod graph | head -50               # 查看依赖图
```

---

## 项目对比矩阵

学习多个项目后，可创建对比矩阵：

| 维度 | slp-go | slp-room | 新项目 |
|------|--------|----------|--------|
| **入口** | HTTP + RPC + CMD | HTTP + CMD | |
| **框架** | GoFrame | GoFrame | |
| **事件模式** | HandleEventMap | HandleEventMap + switch-case | |
| **NSQ 并发** | 50-100 | 10-100 | |
| **DAO 生成** | 代码生成 | 代码生成 | |

---

## 附录：学习笔记模板

```markdown
# <project-name> 学习笔记

## 第一印象

- 项目规模：XX 个 Go 文件，XX 个模块
- 核心功能：XXX
- 技术特点：XXX

## 关键发现

1. ...
2. ...

## 待深入

1. ...
2. ...
```
