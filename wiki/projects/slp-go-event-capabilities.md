---
id: slp-go-event-capabilities
label: slp-go 事件能力清单
source: curated/projects/slp-go/09-event-capabilities.md
project: slp-go
role: event-capabilities
compiled: 2026-04-25
tags:
  - event
  - topic
  - consumer
links:
  - slp-go-structure
  - slp-go-infra
---

# slp-go 事件能力清单

> slp-go 项目的事件能力注册表，按业务领域组织

## 事件能力总览

| 业务领域 | Topic | 事件处理器位置 | 事件数量 |
|---------|-------|---------------|---------|
| 充值回调 | `slp.recharge.after.topic` | `cmd/internal/pay/pay_callback/` | 2 |
| 关系事件 | `xs.relation.event` | `app/service/relation/event/` | 14 |
| 心情值 | `slp.user.mood` | `app/service/mood/` | 9 |
| 礼物打赏 | `xs.user.gift` | `cmd/internal/user_gift/` | - |
| 通用礼物 | `slp.common.gift.send` | `cmd/internal/common_gift_send/` | 8 |
| 房间事件 | `xs.common.room.event` | `cmd/internal/room_event/` | - |
| 装扮系统 | `pretend.event.topic` | `cmd/internal/pretend/` | 4 |
| 小时榜 | `xs.hour.rank` | `cmd/internal/hour_rank/` | - |
| 广场事件 | `xs.square.circle` | `cmd/internal/square/` | 6 |

---

## 1. 充值回调事件

**Topic**: `slp.recharge.after.topic`  
**消费者**: `cmd/internal/pay/pay_callback/service.go`  
**处理方式**: `RechargeCallBackMap` 路由

| 事件 Cmd | 说明 | 处理器 |
|---------|------|--------|
| `recharge_369` | 369 元观光团充值 | `RechargeType369Callback` |
| `user_back` | 用户返利充值 | `RechargeUserBackCallback` |

---

## 2. 关系事件

**Topic**: `xs.relation.event`  
**消费者**: `cmd/internal/relation/consume.go`  
**处理方式**: `HandleEventMap` 路由

| 事件 Cmd | 说明 |
|---------|------|
| `send_gift` | 赠送关系礼物 |
| `relieve_relation` | 解除关系 |
| `divorce` | 离婚 |
| `xs_relation_defend` | 守护值更新 |
| `xs_relation_level` | 关系等级变化 |
| `relation_pretend_switch_change` | 关系装扮切换 |
| `xs_relation_box_process` | 关系盲盒进度 |

---

## 3. 心情值事件

**Topic**: `slp.user.mood`  
**消费者**: `cmd/internal/mood/service.go`  
**处理方式**: `HandleEventMap` 路由

| 事件 Cmd | 说明 |
|---------|------|
| `online` | 用户上线 |
| `chat` | 聊天 |
| `marry` | 结婚 |
| `marry_in_room` | 与伴侣同房间 |
| `relation` | 关系事件 |
| `circle` | 发朋友圈 |
| `add_score` | 加分事件 |
| `reduce_score` | 减分事件 |
| `game` | 游戏 |

---

## 4. 礼物打赏事件

**Topic**: `xs.user.gift`  
**消费者**: `cmd/internal/user_gift/consumer.go`  
**处理方式**: switch-case 直接处理

---

## 新增事件方式

### 充值回调事件
在 `cmd/internal/pay/pay_callback/internal/` 创建新文件，注册到 `RechargeCallBackMap`

### 关系事件
在 `app/service/relation/event/` 创建 `xxx_event.go`，在 `init()` 中注册到 `HandleEventMap`

### 心情值事件
在 `app/service/mood/` 创建 `event_xxx.go`，在 `init()` 中注册到 `HandleEventMap`