---
name: katouch app_id 隔离改造计划
description: 萌新广场功能按 app_id 全链路隔离改造，兼容存量数据
type: project
created: 2026-04-25
status: implemented
updated: 2026-04-26
links:
  - 01-structure.md
  - 05-service.md
tags:
  - slp-go
  - katouch
  - app-isolation
---

# 萌新广场 app_id 全链路隔离改造计划

## 一、背景

萌新广场（katouch）当前未对 app_id 做隔离，所有 app 用户共享同一套资源池和统计数据。需要将萌新广场按 app_id 做全链路隔离，使不同 app 的用户各自有独立的萌新广场。

**核心策略**：
- UserChecker 改为白名单模式，不在白名单的 app_id 直接拦截
- Redis Key 一次切换为新格式（含 appId），但 app_id=66 读新 Key 为空时**降级兜底读老 Key**
- **不双写，仅读侧兜底，写侧只写新 Key**
- **DB 表不改**：uid 全局唯一，天然隔离，不需要 app_id 字段

## 二、架构

```
API Layer:       app/api/katouch.go               (5 个接口: Tabs/List/Send/StatHistory/StatDaily)
    ↓
Service Layer:   app/service/katouch/service.go   (核心业务: List池读取/发送消息/统计)
    ↓
UserProcessor:   app/service/katouch/userprocessor.go  (Redis 池操作核心)
UserChecker:     app/service/katouch/userchecker.go    (用户资格校验)
UserData:        app/service/katouch/userdata.go       (定时任务: 白名单/高潜池入池)
UserStats:       app/service/katouch/userstats.go      (定时任务: 发送统计)
Domain:          app/domain/katouch.go                 (荣耀回归池维护)
NSQ Consumer:    cmd/internal/katouch/nsq_consumer.go  (在线事件/聊天事件处理)
    ↓
DAO Layer:       app/dao/xs_ka_touch_*.go
    ↓
DB Tables:       xs_ka_touch_send_record / xs_ka_touch_send_sum / xs_ka_touch_allocate_log
Redis Keys:      11 种 Key 模板（见 2.2）
```

## 三、Redis Key 变更

### 3.1 新 Key 模板（含 appId）

| 用途 | 新 Key | 实例 |
|------|--------|------|
| 荣耀回归用户池 | `slp.kaTouch.{appId}.fly.back.pool.user.sex.{sex}` | RedisPassive |
| 荣耀回归过期时间 | `slp.kaTouch.{appId}.fly.back.expire.user.{uid}` | RedisPassive |
| 新人 Tab 池 | `slp.kaTouch.{appId}.pool.new.user.tab.sex.{sex}` | RedisCache |
| 私信统计(用户) | `slp.kaTouch.{appId}.user.{uid}.private.day.{day}.statics` | RedisPassive |
| 私信统计(全局) | `slp.kaTouch.{appId}.private.day.{day}.all.user.statics` | RedisPassive |
| GS 新人池 | `slp_go:katouch.{appId}.pool.gs.new.{uid}.{date}` | RedisCache |
| GS 新贵池 | `slp_go:katouch.{appId}.ptpool.{sex}.{date}` | RedisCache |
| GS 高潜池 | `slp_go:katouch.{appId}.pool.gs.pt.{uid}.{date}` | RedisCache |
| 新人池 | `slp_go:katouch.{appId}.newpool.{sex}.{date}` | RedisCache |
| 用户入池计数 | `slp_go:katouch.{appId}.pool.usercount.{uid}.{date}` | RedisCache |
| 萌新首次提示 | `slp_go:katouch:mengxin_first:{from}:{to}` | RedisPassive (不需要 appId) |

### 3.2 老 Key 格式（仅兜底用）

| 新 Key 模板 | 老 Key 格式 |
|------------|------------|
| `slp_go:katouch.{appId}.newpool.{sex}.{date}` | `slp_go:katouch.newpool.{sex}.{date}` |
| `slp_go:katouch.{appId}.ptpool.{sex}.{date}` | `slp_go:katouch.ptpool.{sex}.{date}` |
| `slp.kaTouch.{appId}.pool.new.user.tab.sex.{sex}` | `slp_go:katouch.pool.new.user.tab.sex.{sex}` |
| `slp.kaTouch.{appId}.fly.back.pool.user.sex.{sex}` | `slp_go:katouch.fly.back.pool.user.sex.{sex}` |

### 3.3 读侧兜底策略

**逻辑**：读新 Key → 结果为空 且 appId=66 → 读老 Key 兜底

```
new ?: old（不是 union）
```

不需要求并集的原因：
- 写侧已全量走新 key，老 key 不会再有新数据写入
- 上线当天老 key 有存量数据，新 key 从无到有积累
- 不存在"一部分在新 key、一部分在老 key"的场景

**需要兜底的操作（4 个读池入口）**：

| 方法 | 文件 | 操作 |
|------|------|------|
| `GsSetNewPool` | userprocessor.go | ZRevRange（新人池） |
| `GsGetPTPool` | userprocessor.go | ZRevRangeByScoreWithScores（新贵池） |
| `GsGetNewPoolV2` | userprocessor.go | ZRevRangeByScoreWithScores（新人 Tab 池） |
| `GsGetNewPoolV3` | userprocessor.go | ZRevRangeByScoreWithScores（荣耀回归池） |

## 四、数据库

**3 张表都不加 app_id 字段，代码中去掉了 `app_id` 条件**：

| 表 | 字段 | 说明 |
|---|------|------|
| `xs_ka_touch_send_record` | id, uid, to_uid, send_date, pool_id, is_replied, content_id, ctime, utime | uid 全局唯一，天然隔离 |
| `xs_ka_touch_send_sum` | id, uid, send_date, pool_id, allocat_count, send_count, reply_count, ctime, utime | uid 全局唯一，天然隔离 |
| `xs_ka_touch_allocate_log` | id, allocate_date, pool_id, gs_uid, to_uid, create_time | uid 全局唯一，天然隔离 |

## 五、全局配置

`app/consts/katouch.go` — 白名单配置：

```go
var KaTouchAllowedAppIds = []uint32{
    66, // SLP
    70, // 小拾光
}
```

## 六、上线行为时序

```
上线时刻 (t=0):
  ├─ 写操作 → 只写新 Key
  ├─ 读操作 (app_id=66) → 新 Key，空则兜底读老 Key
  ├─ 读操作 (app_id!=66) → 只读新 Key
  └─ UserChecker → 白名单校验

上线后 (t>0):
  ├─ NSQ 在线事件 → 用户自动进入新 Key 池
  ├─ 新 Key 池逐步填充，兜底逐渐不再触发
  └─ 老 Key 数据自然过期（TTL 最长 100 天）

完全稳定后:
  └─ 可移除兜底逻辑和老 Key 模板代码
```

## 七、改动文件清单

| 文件 | 改动内容 |
|------|---------|
| `app/consts/katouch.go` | 新增 `KaTouchAllowedAppIds` 白名单；新增 V2 Key 模板（含 appId）；新增 `ContainsUint32` 函数 |
| `app/service/katouch/userchecker.go` | `UserChecker` 新增 `AppId`；改为白名单校验；`SetWhiteGs` 中新增 profile 获取 `uc.AppId` |
| `app/service/katouch/userprocessor.go` | `UserProcessor` 新增 `AppId`；4 个读池方法加 fallback 逻辑；`AddPoolLog` 移除 appId 参数 |
| `app/service/katouch/service.go` | `List`/`StatDaily`/`StatHistory`/`Send`/`wrapSendStatus`/`markSent`/`getStateRecord`/`SendMengXinNotify` 均加 appId 参数；DB 查询**不加** app_id（uid 天然隔离） |
| `app/domain/katouch.go` | `HandleOnlineByFyFlyBack` 加 appId 参数，Redis 用新 Key 写入 |
| `app/api/katouch.go` | `List`/`StatDaily`/`StatHistory` 从 `user.AppID` 传入 appId |
| `cmd/internal/katouch/nsq_consumer.go` | handler 从 profile 获取 appId，DB 查询**不加** app_id |
| `app/service/katouch/userdata.go` | `DealGsLine`/`DealPTLine` 从 profile 获取 appId；`AddPoolLog` 调用移除 appId；DB 插入**不加** app_id |
| `app/service/account/online_dateline.go` | 调用 `HandleOnlineByFyFlyBack` 传 appId |
| `app/api/test_tool.go` | `SetKaTouchPrivateNum` 改用 V2 Key 模板 |

## 八、回滚方案

- **Redis Key**：回滚代码后使用老 Key 格式，新 Key 自然过期
- **DB**：不涉及表结构变更，无回滚风险
- **UserChecker**：回滚后恢复 `== AppSLP` 硬编码校验，行为不变

## 九、后续优化

- 上线稳定后，移除 app_id=66 兜底逻辑和老 Key 模板代码
- 白名单从 consts 常量升级为配置中心/DB 动态配置
