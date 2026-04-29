---
id: slp-go-infra
label: slp-go 基础设施
source: curated/projects/slp-go/07-infra.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-structure
---

# slp-go 基础设施

## 中间件

| 中间件 | 用途 |
|--------|------|
| Consul | 服务发现 |
| Redis | 缓存/会话 |
| Kafka | 消息队列 (新业务默认) |
| NSQ | 消息队列 (存量业务) |
| MySQL | 主数据库 |

## Redis 使用

| 模式 | 代码 |
|------|------|
| 只读 | `library.RedisClient(library.RedisPassive)` |
| 可写 | `library.RedisClient(library.RedisMaster)` |

## 配置

| 配置项 | 说明 |
|--------|------|
| `[server]` | 服务地址、运行模式 |
| `[database]` | 数据库连接 |
| `[rpc.discover]` | 服务发现配置 |

## 服务发现

| 命令 | 用途 |
|------|------|
| `consul agent -dev -ui -client 0.0.0.0` | 启动 Consul |

## 相关知识

- [[projects/slp-go/01-structure]]
