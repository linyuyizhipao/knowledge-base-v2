---
id: slp-starship-structure
label: slp-starship 项目结构
source: curated/projects/slp-starship/01-structure.md
project: slp-starship
role: project-structure
compiled: 2026-04-25
links:
  - slp-starship-event-capabilities
---

# slp-starship 项目结构

> 家族（星舰）系统：家族管理、领地战、农场、商城等玩法

## 核心架构

两层服务形态：

```
┌─────────────┐   ┌─────────────┐
│ HTTP Server │   │ CMD Workers │
│  (main.go)  │   │  (cmd/)     │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └─────────────────┼─────────────────┐
                         │                 │
                         ▼                 ▼
                    ┌─────────┐     ┌──────────┐
                    │  API    │────▶│ Service  │
                    │ Layer   │     │  Layer   │
                    └─────────┘     └────┬─────┘
                                         │
                                         ▼
                                    ┌──────────┐
                                    │   DAO    │
                                    └────┬─────┘
                                         │
                                ┌────────┴────────┐
                                │                 │
                                ▼                 ▼
                           ┌────────┐     ┌──────────┐
                           │ MySQL  │     │  Redis   │
                           └────────┘     └──────────┘
```

**与 slp-go/slroom 的区别**:
- 没有独立的 RPC 服务层
- 使用 `commonsrv/` 共享服务模块
- 事件处理统一使用 HandleEventMap 模式

## 目录结构

| 目录 | 说明 | 文件数 |
|------|------|--------|
| `app/api/` | HTTP 请求处理器 | 28 模块 |
| `app/service/` | 服务层 | 14 模块 |
| `app/dao/` | 数据访问层 | 104 文件 |
| `app/model/` | 数据模型 | 108 文件 |
| `app/pb/` | Protobuf 定义 | 149 文件 |
| `app/query/` | 查询组合层 | 14 文件 |
| `cmd/internal/` | 命令行后台任务 | 7 模块 |
| `commonsrv/` | 共享服务模块 (独有) | - |
| `consts/` | 常量定义 | 31 文件 |
| `library/` | 基础设施库 | 28 包 |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `main.go` | `./bin/http` |
| CMD | `cmd/main.go` | `./bin/cmd --name=<module>` |