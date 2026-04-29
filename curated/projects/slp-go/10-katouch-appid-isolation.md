---
name: katouch app_id 隔离改造计划
description: 萌新广场功能按 app_id 全链路隔离改造，兼容存量数据
type: project
created: 2026-04-25
status: planning
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

**需求确认**：
- 隔离范围：全链路（Redis 池、DB 记录、统计、发消息）
- app_id 范围：SLP (66) + 其他已知 app
- 存量数据：兼容，老数据归属到 app_id=66 (SLP)

## 二、现状分析

### 2.1 调用链路

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
Redis Keys:      13 种 Key 模板 (见 2.5)
```

### 2.2 涉及的文件清单

| 文件 | 职责 | 是否改动 |
|------|------|---------|
| `app/api/katouch.go` | API 入口，5 个接口 | 是 |
| `app/service/katouch/service.go` | 核心业务逻辑 | 是 |
| `app/service/katouch/userprocessor.go` | Redis 池操作 | 是 |
| `app/service/katouch/userchecker.go` | 用户资格校验 | 是 |
| `app/service/katouch/userdata.go` | 定时任务(白名单/高潜) | 是 |
| `app/service/katouch/userstats.go` | 定时任务(统计) | 是 |
| `app/domain/katouch.go` | 荣耀回归池维护 | 是 |
| `app/consts/katouch.go` | Redis key 定义 | 是 |
| `cmd/internal/katouch/nsq_consumer.go` | NSQ 消费者(池维护) | 是 |
| `cmd/internal/katouch/cron.go` | 定时任务注册 | 否 |

### 2.3 当前 app_id 使用情况

目前已有部分 app_id 使用，但不完整：

1. **userchecker.go:41,45** — 检查用户 app_id 是否为 AppSLP(66)，不是则不让进入萌新池（**需要改为按 app_id 分流而非拦截**）
2. **service.go:238** — Send 接口接收 appId 参数，传给发消息
3. **service.go:375** — senMsg 中获取用户 profile 包含 app_id
4. **service.go:448** — sendMsgSingle 将 appId 传入 IM 发消息
5. **service.go:626** — SendMengXinNotify **硬编码 appId = model.AppSLP**（需改为动态传入）
6. **domain/katouch.go:24** — HandleOnlineByFyFlyBack 获取 profile 包含 app_id（未使用）
7. **api/katouch.go:88** — Send 接口从 user.AppID 传入

**结论**：Redis 池和 DB 均未做 app_id 隔离。存在硬编码 AppSLP 的情况。

### 2.4 数据库表结构（当前无 app_id 字段）

**表: xs_ka_touch_send_record** — uid, to_uid, send_date, pool_id, is_replied, content_id, ctime, utime

**表: xs_ka_touch_send_sum** — uid, send_date, pool_id, allocat_count, send_count, reply_count, ctime, utime

**表: xs_ka_touch_allocate_log** — allocate_date, pool_id, gs_uid, to_uid, create_time

### 2.5 Redis Key 清单

| Key 模板 | 类型 | 说明 | 示例 |
|----------|------|------|------|
| `slp_go:katouch.newpool.{sex}.{date}` | ZSET | 新人池 | `slp_go:katouch.newpool.2.20260425` |
| `slp_go:katouch.ptpool.{sex}.{date}` | ZSET | 高潜池 | `slp_go:katouch.ptpool.2.20260425` |
| `slp_go:katouch.pool.usercount.{uid}.{date}` | INT | 单用户入池次数 | |
| `slp_go:katouch.pool.gs.new.{uid}.{date}` | SET | GS 新人池 | |
| `slp_go:katouch.pool.gs.pt.{uid}.{date}` | SET | GS 高潜池 | |
| `slp.kaTouch.fly.back.pool.user.sex.{sex}` | ZSET | 荣耀回归池 | 100天 TTL |
| `slp.kaTouch.fly.back.expire.user.{uid}` | STRING | 回归池过期 | 15天 TTL |
| `slp.kaTouch.pool.new.user.tab.sex.{sex}` | ZSET | 新人 Tab 池 | 100天 TTL |
| `slp.kaTouch.user.{uid}.private.day.{day}.statics` | SET | 单用户私聊统计 | 25小时 TTL |
| `slp.kaTouch.private.day.{day}.all.user.statics` | HASH | 全局私聊统计 | 25小时 TTL |
| `slp-go:katouch:ds:{code}:{date}` | STRING | OSS 数据路径 | |
| `slp-go:katouch:gs:white:{date}` | SET | GS 白名单 | 7天 TTL |
| `slp_go:katouch:mengxin_first:{from}:{to}` | STRING | 萌新首次提示 | 30天 TTL |

## 三、改造方案

### 3.1 原则

- **存量兼容**：所有存量数据默认归属 app_id=66 (SLP)
- **向后兼容**：未传 app_id 的场景默认按 SLP 处理
- **最小侵入**：尽量复用已有逻辑，增加 app_id 维度参数

### 3.2 Redis Key 改造

**方案**：在所有 Redis Key 中增加 `{appId}` 维度

| 原 Key | 新 Key |
|--------|--------|
| `slp_go:katouch.newpool.{sex}.{date}` | `slp_go:katouch.{appId}.newpool.{sex}.{date}` |
| `slp_go:katouch.ptpool.{sex}.{date}` | `slp_go:katouch.{appId}.ptpool.{sex}.{date}` |
| `slp_go:katouch.pool.usercount.{uid}.{date}` | `slp_go:katouch.{appId}.pool.usercount.{uid}.{date}` |
| `slp_go:katouch.pool.gs.new.{uid}.{date}` | `slp_go:katouch.{appId}.pool.gs.new.{uid}.{date}` |
| `slp_go:katouch.pool.gs.pt.{uid}.{date}` | `slp_go:katouch.{appId}.pool.gs.pt.{uid}.{date}` |
| `slp.kaTouch.fly.back.pool.user.sex.{sex}` | `slp.kaTouch.{appId}.fly.back.pool.user.sex.{sex}` |
| `slp.kaTouch.fly.back.expire.user.{uid}` | `slp.kaTouch.{appId}.fly.back.expire.user.{uid}` |
| `slp.kaTouch.pool.new.user.tab.sex.{sex}` | `slp.kaTouch.{appId}.pool.new.user.tab.sex.{sex}` |
| `slp.kaTouch.user.{uid}.private.day.{day}.statics` | `slp.kaTouch.{appId}.user.{uid}.private.day.{day}.statics` |
| `slp.kaTouch.private.day.{day}.all.user.statics` | `slp.kaTouch.{appId}.private.day.{day}.all.user.statics` |
| `slp_go:katouch:mengxin_first:{from}:{to}` | `slp_go:katouch.{appId}:mengxin_first:{from}:{to}` |

### 3.3 数据库表改造

**方案**：给 3 张表新增 `app_id` 字段（`INT UNSIGNED NOT NULL DEFAULT 66`）

```sql
ALTER TABLE xs_ka_touch_send_record ADD COLUMN app_id INT UNSIGNED NOT NULL DEFAULT 66 AFTER uid;
ALTER TABLE xs_ka_touch_send_sum ADD COLUMN app_id INT UNSIGNED NOT NULL DEFAULT 66 AFTER uid;
ALTER TABLE xs_ka_touch_allocate_log ADD COLUMN app_id INT UNSIGNED NOT NULL DEFAULT 66 AFTER allocate_date;
```

- 默认值 66 (SLP) 保证存量数据自动归属
- 新增数据时写入正确的 app_id
- 查询时增加 `app_id` 条件

### 3.4 代码改动详情

#### Step 1: consts/katouch.go — Redis Key 模板增加 appId

所有 RedisKey 增加 appId 占位符，`.Key(...)` 调用点传入 appId。

#### Step 2: service/katouch/userchecker.go — 去掉 app_id 硬编码限制

- `UserChecker` 结构体新增 `AppId uint32` 字段
- `Check` 方法中 `profile.GetAppId() != int32(model.AppSLP)` 的判断改为记录 appId，不再拦截
- `NewUserChecker` 改为接收 appId 或在 Check 中从 profile 获取

#### Step 3: service/katouch/userprocessor.go — 池操作传入 appId

- `UserProcessor` 结构体新增 `AppId uint32` 字段
- `NewUserProcessor` 增加 appId 参数
- 所有 Redis 操作（`GsGetNewPoolV2`/`GsGetNewPoolV3`/`GsGetPTPool`/`EnterNewPool`/`AddUser2Pool`/`DeleteNewPool`/`GsSetNewPool`）使用带 appId 的 Key
- `AddPoolLog` 写入 allocate_log 时带 appId

#### Step 4: service/katouch/service.go — 核心逻辑传入 appId

- `List` / `Tabs` — 增加 appId 参数，传给 UserProcessor
- `Send` — 已有 appId，`markSent` 写入 DB 时增加 app_id
- `markSent` — INSERT 增加 app_id 字段
- `wrapSendStatus` — 查询 send_record 增加 app_id 条件
- `StatDaily` / `StatHistory` — 查询 DB 增加 app_id 条件
- `getStateRecord` — 查询 send_record 增加 app_id 条件
- `SendMengXinNotify` — appId 改为参数传入，不再硬编码 AppSLP

#### Step 5: domain/katouch.go — 荣耀回归池

- `HandleOnlineByFyFlyBack` — 从 profile 获取 appId，Redis Key 带 appId

#### Step 6: cmd/internal/katouch/nsq_consumer.go — NSQ 消费者

- `handleOnline` / `handleOnlineByFyFlyBack` / `handleOnlineByNewUserTabPool` / `handleOnlineChangeKaTabPool` — 从 profile 获取 appId
- `handleNewUserTabPool` — Redis Key 带 appId
- `handleChat` — 查询 send_record 增加 app_id 条件
- `handleMengXinChatNotify` — mengxin_first key 带 appId

#### Step 7: service/katouch/userdata.go — 定时任务

- `DealGsLine` — 写入 send_sum 时增加 app_id（需确认白名单 GS 的 app 归属）
- `DealPTLine` — 从 profile 获取 appId，Redis Key 带 appId

#### Step 8: service/katouch/userstats.go — 统计定时任务

- `RunYesterday` — 查询 send_record 和更新 send_sum 时增加 app_id 维度
- `RunHistory` — 查询和更新 send_sum 时增加 app_id 维度

#### Step 9: API 层 — 传入 app_id

`app/api/katouch.go` — 5 个接口全部从 `user.AppID` 获取并传入：
- `Tabs` → 传 appId
- `List` → 传 appId
- `Send` → 已有，不变
- `StatHistory` → 传 appId
- `StatDaily` → 传 appId

### 3.5 关键问题待确认

1. **GS 白名单数据源**：OSS 中的 GS 白名单是否按 app 区分？一个 GS 是否同时服务多个 app？
2. **高潜池数据源**：OSS 中的高潜用户数据是否按 app 区分？
3. **跨 app 用户**：一个 uid 是否可能同时在多个 app 有账号？

## 四、影响范围评估

### 4.1 风险等级

| 改动点 | 风险 | 说明 |
|--------|------|------|
| Redis Key 格式变更 | **高** | 上线瞬间老 Key 失效，池子变空 |
| DB 表加字段 | **中** | 有默认值兜底，不影响已有查询 |
| NSQ 消费者逻辑变更 | **中** | 影响在线用户入池逻辑 |
| userchecker 去掉 app_id 拦截 | **低** | 改为按 appId 分流 |

### 4.2 Redis Key 迁移策略

**推荐方案：一次性切割**

Redis 池数据有 TTL（最长100天），且池中用户会通过 NSQ 在线事件自动重新入池。在凌晨非高峰期上线，老 Key 自然过期即可。

- **不推荐灰度迁移**：代码复杂度翻倍，需要同时读写新老 Key
- **推荐一次性切换**：稳定后老 Key 自然过期清除

### 4.3 DB 数据兼容

三张表加 `app_id` 字段，默认值 66，存量数据自动归属 SLP，无需数据迁移脚本。

### 4.4 上下游影响

| 系统 | 影响 |
|------|------|
| GS | 不受影响，仅通过 NSQ 传递事件 |
| IM | 不受影响，Send 接口已传 appId |
| 数据统计/报表 | 需确认下游是否按 app_id 消费数据 |
| OSS 数据源 | 需确认是否按 app 区分 |

## 五、执行步骤

1. **DB 变更**：执行 DDL，3 张表加 app_id 字段（默认 66）
2. **consts 层**：Redis Key 模板加 appId 占位
3. **UserChecker**：结构体加 AppId，去掉硬编码 SLP 拦截
4. **UserProcessor**：结构体加 AppId，Redis 操作带 appId
5. **Service**：核心方法传入/使用 appId
6. **Domain**：HandleOnlineByFyFlyBack 带 appId
7. **NSQ Consumer**：handler 从 profile 获取 appId
8. **UserData**：DealGsLine/DealPTLine 带 appId
9. **UserStats**：统计任务加 app_id 维度
10. **API 层**：5 个接口传入 user.AppID
11. **测试**：单测 + 集成测试
12. **上线**：先 DDL → 再代码发布

## 六、回滚方案

- **Redis Key**：回滚代码后使用老 Key 格式，新 Key 自然过期
- **DB**：app_id 字段保留，不影响回滚后的代码（默认值兜底）
