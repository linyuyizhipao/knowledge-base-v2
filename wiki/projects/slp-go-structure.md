---
id: slp-go-structure
label: slp-go 项目结构
source: curated/projects/slp-go/01-structure.md
project: slp-go
role: project-structure
compiled: 2026-04-25
links:
  - slp-go-architecture
  - slp-go-development
  - slp-go-api
---

# slp-go 项目结构

## 核心架构

三层服务形态：

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ HTTP Server │   │ RPC Server  │   │ CMD Workers │
│   (app/)    │   │ (rpc/ser)   │   │  (cmd/)     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
  ┌─────────┐     ┌──────────┐     ┌──────────┐
  │  API    │────▶│ Service  │────▶│   DAO    │
  │ Layer   │     │  Layer   │     │  Layer   │
  └─────────┘     └──────────┘     └────┬─────┘
                                        │
                                ┌───────┴───────┐
                                │               │
                                ▼               ▼
                           ┌────────┐     ┌──────────┐
                           │ MySQL  │     │  Redis   │
                           └────────┘     └──────────┘
```

## 目录结构

| 目录 | 说明 | 文件数 |
|------|------|--------|
| `app/api/` | HTTP 请求处理器 | 160+ 模块 |
| `app/service/` | 业务逻辑和中间件 | - |
| `app/dao/` | 数据访问层 | 968 文件 |
| `app/pb/` | Protobuf 定义 | 1309 文件 |
| `app/query/` | 查询组合层 | 160 文件 |
| `app/model/` | 数据模型 | 967 文件 |
| `rpc/server/` | RPC 服务实现 | 23 服务类型 |
| `rpc/client/` | RPC 客户端封装 | 84 类型 |
| `cmd/internal/` | 命令行后台任务 | 219 模块 |
| `library/` | 基础设施库 | 38 包 |
| `proto/` | Protobuf 源文件 | 681 目录 |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `app/main.go` | `./bin/http` |
| RPC | `rpc/server/main.go` | `./bin/rpc --name=user` |
| CMD | `cmd/main.go` | `./bin/cmd --name=cache --action=Main` |

## 模块引用关系

```
app/api      → app/service, app/query, app/dao, app/model
app/service  → app/dao, app/model, library
app/dao      → app/model (内部调用)
library      → 第三方服务 (Redis, Kafka, MySQL 等)

严格禁止：
- 任何层不可调用 app/api
- library 不可调用 app/service
```