---
id: slp-go-katouch-isolation
label: slp-go 萌新广场app_id隔离改造
source: curated/projects/slp-go/10-katouch-appid-isolation.md
project: slp-go
role: project
compiled: 2026-04-25
tags:
  - katouch
  - app-isolation
links:
  - slp-go-structure
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

### 2.3 当前 app_id 使用情况

目前已有部分 app_id 使用，但不完整：

1. **userchecker.go** — 检查用户 app_id 是否为 AppSLP(66)，不是则不让进入萌新池（**需要改为按 app_id 分流而非拦截**）
2. **service.go** — Send 接口接收 appId 参数，传给发消息
3. **SendMengXinNotify** — **硬编码 appId = model.AppSLP**（需改为动态传入）

### 2.4 数据库表结构（当前无 app_id 字段）

**表: xs_ka_touch_send_record** — uid, to_uid, send_date, pool_id, is_replied, content_id, ctime, utime

**表: xs_ka_touch_send_sum** — uid, send_date, pool_id, allocat_count, send_count, reply_count, ctime, utime

### 2.5 Redis Key 清单

| Key 模板 | 类型 | 说明 |
|----------|------|------|
| `slp_go:katouch.newpool.{sex}.{date}` | ZSET | 新人池 |
| `slp_go:katouch.ptpool.{sex}.{date}` | ZSET | 高潜池 |
| `slp.kaTouch.fly.back.pool.user.sex.{sex}` | ZSET | 荣耀回归池 |
| `slp.kaTouch.pool.new.user.tab.sex.{sex}` | ZSET | 新人 Tab 池 |

## 三、改造方案

### 3.1 Redis Key 改造

```
# 旧格式
slp_go:katouch.newpool.{sex}.{date}

# 新格式
slp_go:katouch.newpool.{app_id}.{sex}.{date}
```

### 3.2 数据库改造

需要给以下表添加 app_id 字段：
- `xs_ka_touch_send_record`
- `xs_ka_touch_send_sum`
- `xs_ka_touch_allocate_log`

### 3.3 代码改造要点

1. **userchecker.go** - 改为按 app_id 分流
2. **service.go** - 移除硬编码 AppSLP
3. **SendMengXinNotify** - 动态传入 appId