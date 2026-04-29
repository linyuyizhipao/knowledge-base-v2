---
id: slp-go-structure
label: slp-go 项目结构
source: curated/projects/slp-go/01-structure.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-architecture
  - slp-go-development
  - slp-go-event-capabilities
---

# slp-go 项目结构

## 目录树

| 目录 | 说明 | 数量 |
|------|------|------|
| `app/` | HTTP 应用主代码 | - |
| `app/main.go` | HTTP 服务入口 | 1 |
| `app/api/` | HTTP 请求处理器 | 160+ |
| `app/service/` | 业务逻辑层 | - |
| `app/dao/` | 数据访问层 | 968 |
| `app/pb/` | Protobuf 定义 | 1309 |
| `app/query/` | 查询组合层 | 160 |
| `app/model/` | 数据模型 | 967 |
| `rpc/server/` | RPC 服务实现 | 23 |
| `rpc/client/` | RPC 客户端封装 | 84 |
| `cmd/internal/` | CMD 任务实现 | 219 |
| `library/` | 基础设施库 | 38 |
| `proto/` | Protobuf 源文件 | 681 |
| `config/` | 配置文件 | - |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `app/main.go` | `./bin/http` |
| RPC | `rpc/server/main.go` | `./bin/rpc --name=user` |
| CMD | `cmd/main.go` | `./bin/cmd --name=cache --action=Main` |

## 模块引用关系

| 上层 | 下层 | 说明 |
|------|------|------|
| `app/api` | `app/service`, `app/query`, `app/dao` | API 调用 Service/Query/DAO |
| `app/service` | `app/dao`, `library` | Service 调用 DAO |
| `app/dao` | `app/model` | DAO 调用 Model |
| `library` | Redis, Kafka, MySQL | 基础设施调用第三方 |

**禁止调用**:
- 任何层不可调用 `app/api`
- `library` 不可调用 `app/service`