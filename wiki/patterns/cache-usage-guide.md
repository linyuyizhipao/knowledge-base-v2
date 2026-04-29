---
id: patterns/cache-usage-guide
label: 缓存使用规范
type: guide
source: curated/patterns/cache-usage-guide.md
sources: [curated/patterns/cache-usage-guide.md]
role: 规范
compiled: 2026-04-29
source_hash: new
tags: [缓存, Redis, 缓存穿透, 批量查询]
links_to:
  - patterns/nsq-usage
  - CODING_STANDARDS
  - patterns/business-module-standard
---

# 缓存使用规范

> Redis 缓存标准使用模式

## 缓存场景速查

| 场景 | TTL | Key 示例 |
|------|-----|----------|
| 用户 Profile | 1小时 | `user:profile:{uid}` |
| 配置信息 | 24小时 | `config:room:{roomId}` |
| 会话状态 | 30分钟 | `session:{token}` |
| 热点数据 | 5分钟 | `hot:gifts:top100` |

## 核心规范（4 条）

| # | 规范 | 正确做法 |
|---|------|----------|
| 1 | Key 命名 | `{业务}:{类型}:{ID}` |
| 2 | 禁止直接 Set | `library.CacheSet(ctx, key, data, ttl)` |
| 3 | 穿透防护 | 空值缓存 `"NULL"` 5分钟 |
| 4 | 雪崩防护 | TTL + 随机偏移 |

## 批量查询

```go
// ❌ 循环查询
for _, uid := range uids { CacheGet(...) }

// ✅ MGet 批量
keys := buildKeys(uids)
results := CacheMGet(ctx, keys)
```

## 缓存更新策略

| 策略 | 场景 | 实现 |
|------|------|------|
| Cache Aside | 读多写少 | 删缓存 → 更新 DB |
| Write Through | 写多 | 同步更新缓存+DB |
| Write Behind | 高吞吐 | 异步批量更新 |

## 相关知识

- [[patterns/nsq-usage]] - NSQ规范
- [[CODING_STANDARDS]] - 核心禁令
- [[patterns/business-module-standard]] - 模块标准