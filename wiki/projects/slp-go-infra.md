---
id: slp-go-infra
label: slp-go 基础设施
source: curated/projects/slp-go/07-infra.md
project: slp-go
role: infrastructure
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

```go
// 只读
rds := library.RedisClient(library.RedisPassive)
val, _ := rds.Get(ctx, key).String()

// 可写
rds := library.RedisClient(library.RedisMaster)
rds.Set(ctx, key, value, 3600)
```

## 配置

```toml
# config/config.toml
[server]
Address = ":9091"
RunMode = "dev"

[database]
[[database.default]]
type = "bmsql"
link = "user:pass@tcp(127.0.0.1:3306)/db"
```

## 服务发现

```bash
consul agent -dev -ui -client 0.0.0.0
```

配置：
```toml
[rpc.discover]
Type = "consul"
Addr = ["127.0.0.1:8500"]
```