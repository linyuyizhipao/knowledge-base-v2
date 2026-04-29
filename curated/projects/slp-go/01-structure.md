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

```
slp-go/
├── app/                          # HTTP 应用主代码
│   ├── main.go                   # HTTP 服务入口
│   ├── app/                      # 应用启动和路由
│   ├── api/                      # HTTP 请求处理器 (160+ 模块)
│   ├── service/                  # 业务逻辑和中间件
│   ├── dao/                      # 数据访问层 (968 文件)
│   ├── pb/                       # Protobuf 定义 (1309 文件)
│   ├── query/                    # 查询组合层 (160 文件)
│   ├── model/                    # 数据模型 (967 文件)
│   └── utils/                    # 工具函数
│
├── rpc/                          # RPC 服务
│   ├── server/                   # RPC 服务实现 (23 服务类型)
│   └── client/                   # RPC 客户端封装 (84 类型)
│
├── cmd/                          # 命令行后台任务
│   └── internal/                 # 任务实现 (219 模块)
│
├── library/                      # 基础设施库 (38 包)
├── proto/                        # Protobuf 源文件 (681 目录)
├── config/                       # 配置文件
└── dao/                          # 独立 DAO 模块
```

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
