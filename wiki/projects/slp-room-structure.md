---
id: slp-room-structure
label: slp-room 项目结构
source: curated/projects/slp-room/01-structure.md
project: slp-room
role: project-structure
compiled: 2026-04-25
links:
  - slp-room-architecture
  - slp-room-event-capabilities
---

# slp-room 项目结构

> 房间服务：多人房、PK、抢麦等实时互动功能

## 核心架构

三层服务形态：

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ HTTP Server │   │ RPC Server  │   │ CMD Workers │
│  (main.go)  │   │ (rpc/server)│   │  (cmd/)     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
  ┌─────────┐     ┌──────────┐     ┌──────────┐
  │  API    │────▶│  Busi    │────▶│   DAO    │
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
| `app/api/` | HTTP 请求处理器 | 18+ 模块 |
| `app/busi/` | 业务逻辑层 | 60+ 模块 |
| `app/service/` | 服务层 | 97 模块 |
| `app/dao/` | 数据访问层 | 500+ 文件 |
| `app/model/` | 数据模型 | 500+ 文件 |
| `app/pb/` | Protobuf 定义 | 750+ 文件 |
| `app/query/` | 查询组合层 | 103 文件 |
| `cmd/internal/` | 命令行后台任务 | 100+ 模块 |
| `consts/` | 常量定义 | 36 文件 |
| `library/` | 基础设施库 | 33 包 |
| `module/` | 模块封装 | 15 模块 |
| `plugin/` | 插件系统 | 17 插件 |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `main.go` | `./bin/http` |
| CMD | `cmd/main.go` | `./bin/cmd --name=<module>` |