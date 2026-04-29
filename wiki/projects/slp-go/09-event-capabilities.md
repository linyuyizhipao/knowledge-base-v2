---
id: slp-go-event-capabilities
label: slp-go 事件能力清单
source: curated/projects/slp-go/09-event-capabilities.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-structure
---

# slp-go 事件能力清单

## 事件能力总览

| 业务领域 | Topic | 位置 | 事件数量 |
|---------|-------|------|---------|
| 充值回调 | `slp.recharge.after.topic` | `cmd/internal/pay/pay_callback/` | 2 |
| 关系事件 | `xs.relation.event` | `app/service/relation/event/` | 14 |
| 心情值 | `slp.user.mood` | `app/service/mood/` | 9 |
| 礼物打赏 | `xs.user.gift` | `cmd/internal/user_gift/` | - |
| 通用礼物 | `slp.common.gift.send` | `cmd/internal/common_gift_send/` | 8 |
| 房间事件 | `xs.common.room.event` | `cmd/internal/room_event/` | - |
| 功能地图 | `function_map` | `cmd/internal/function_map/` | - |
| 装扮系统 | `pretend.event.topic` | `cmd/internal/pretend/` | 4 |
| 小时榜 | `xs.hour.rank` | `cmd/internal/hour_rank/` | - |
| 广场事件 | `xs.square.circle` | `cmd/internal/square/` | 6 |

## 充值回调事件

| 事件 Cmd | 说明 | 处理器 |
|---------|------|--------|
| `recharge_369` | 369 元观光团充值 | `RechargeType369Callback` |
| `user_back` | 用户返利充值 | `RechargeUserBackCallback` |

## 关系事件

| 事件 Cmd | 说明 |
|---------|------|
| `send_gift` | 赠送关系礼物 |
| `relieve_relation` | 解除关系 |
| `divorce` | 离婚 |
| `xs_relation_defend` | 守护值更新 |
| `xs_relation_level` | 关系等级变化 |
| `relation_pretend_switch_change` | 关系装扮切换 |
| `xs_relation_box_process` | 关系盲盒进度 |
| `relation_box_delay_im` | 盲盒延时通知 |

## 心情值事件

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

## 装扮系统事件

| 事件 Cmd | 说明 |
|---------|------|
| `mic.leave` | 下麦事件 |
| `room.leave` | 离开房间 |
| `pretend.expire` | 装扮过期 |
| `send.relation.pretend` | 赠送关系装扮 |

## 其他事件 Topic

| Topic | 业务 |
|-------|------|
| `xs.room.red.packet` | 房间红包 |
| `xs.world.red.packet` | 世界红包 |
| `xs.achieve.wall` | 成就墙 |
| `xs.mission` | 任务中心 |
| `xs.full.screen` | 全站飘屏 |
| `xs.user.sign.in` | 用户签到 |
| `starship.event.topic` | 星舰事件 |

## 事件处理器模式

| 模式 | 优点 | 适用场景 |
|------|------|---------|
| switch-case | 简单直接 | 房间事件、礼物事件 |
| HandleEventMap | 动态扩展 | 关系事件、心情值 |
| 观察者模式 | 多业务响应 | 充值回调、钻石消耗 |

## 相关知识

- [[patterns/event-extension-guide]]
- [[patterns/nsq-usage]]
