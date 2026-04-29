# 缓存使用规范

> Redis 缓存的标准使用模式

**版本**: 1.0 | **创建**: 2026-04-29

---

## 缓存场景分类

| 场景 | 缓存策略 | TTL | 示例 |
|------|---------|------|------|
| 用户 Profile | 读多写少 | 1小时 | `user:profile:{uid}` |
| 配置信息 | 极少变更 | 24小时 | `config:room:{roomId}` |
| 会话状态 | 高频变更 | 30分钟 | `session:{token}` |
| 热点数据 | 实时更新 | 5分钟 | `hot:gifts:top100` |

---

## 核心规范

### 1. Key 命名规范

```
{业务}:{类型}:{唯一标识}

示例:
  user:profile:123456
  room:config:789
  cache:gift:list
```

### 2. 禁止直接 Set

必须使用封装方法，确保一致性：

```go
// ❌ 错误 - 直接调用 Redis
redis.Set("user:profile:123", data)

// ✅ 正确 - 使用封装方法
library.CacheSet(ctx, "user:profile:123", data, 3600)
```

### 3. 缓存穿透防护

```go
// ✅ 正确 - 使用空值缓存
if data == nil {
    library.CacheSet(ctx, key, "NULL", 300) // 缓存空值 5 分钟
    return nil
}
```

### 4. 缓存雪崩防护

```go
// ✅ 正确 - TTL 加随机偏移
ttl := 3600 + rand.Intn(300) // 1小时 + 0~5分钟随机
library.CacheSet(ctx, key, data, ttl)
```

---

## 批量查询规范

```go
// ❌ 错误 - 循环查询缓存
for _, uid := range uids {
    data := library.CacheGet(ctx, "user:profile:" + uid)
}

// ✅ 正确 - 使用 MGet 批量查询
keys := []string{}
for _, uid := range uids {
    keys = append(keys, "user:profile:" + uid)
}
results := library.CacheMGet(ctx, keys)
```

---

## 缓存更新策略

| 策略 | 适用场景 | 实现方式 |
|------|---------|---------|
| Cache Aside | 读多写少 | 先删缓存，再更新 DB |
| Write Through | 写多 | 同步更新缓存和 DB |
| Write Behind | 高吞吐 | 异步批量更新 DB |

---

## 相关文档

- [[patterns/nsq-usage]] - NSQ 使用规范
- [[CODING_STANDARDS]] - 核心禁令
- [[patterns/business-module-standard]] - 模块标准