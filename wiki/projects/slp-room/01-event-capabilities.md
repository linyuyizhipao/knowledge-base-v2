---
id: slp-room-event-capabilities
label: slp-room 事件能力清单
source: curated/projects/slp-room/01-event-capabilities.md
project: slp-room
compiled: 2026-04-25
links:
  - slp-room-structure
---

# slp-room 事件能力清单

## 事件能力总览

| 业务领域 | Topic | 处理方式 | 事件数量 |
|---------|-------|---------|---------|
| 房间推荐 | `slp.room.recommend.more` | HandleEventMap | 40+ |
| 房间 PK | `room.pk.topic` | switch-case | 5 |
| 大哥房间 | `slp.big.brother` | HandleEventMap | 4 |
| 抢麦事件 | `grabmic.TopicGrabMic` | switch-case | 12 |
| CP 连线 | `cplink.TopicCplinkV2` | switch-case | 7 |
| 房间进入 | `xs.room.enter` | switch-case | 3 |
| 拍卖事件 | `slp.auction` | HandleEventMap | - |
| 心跳竞抢 | `heartrace.TopicHeartRace` | switch-case | - |
| 领唱事件 | `leadsing.LEAD_SING_TOPIC` | switch-case | - |
| 狼人杀 | `guess_song.GUESS_SONG_TOPIC` | switch-case | - |

## 房间推荐事件

| 事件 Cmd | 说明 |
|---------|------|
| `boss_change` | 老板位变更 |
| `enter_room` | 用户进入房间 |
| `send_gift` | 赠送礼物 |
| `exposure_room` | 房间曝光 |
| `refresh_score` | 刷新推荐分数 |
| `lucky_draw_event_mic_room` | 幸运抽奖麦位房 |
| `lucky_draw_event_enter_room` | 幸运抽奖进房 |
| `starship_home_recommend_enter_room` | 星舰首页进房 |
| `recharge_user_group_enter_room` | 369 观光团进房 |

## 房间 PK 事件

| 事件 Cmd | 说明 |
|---------|------|
| `xs_room_pk.next` | PK 下一轮 |
| `xs_room_pk` | PK Binlog |
| `xs_live_pk` | 直播 PK Binlog |
| `xs_live_pk_match` | PK 匹配 |
| `xs_live_pk_match_cancel` | PK 取消匹配 |

## 大哥房间事件

| 事件 Cmd | 说明 |
|---------|------|
| `send_gift` | 赠送礼物 |
| `try_status_change` | 试用状态变更 |
| `pet_status_change` | 宠物状态变更 |

## 抢麦事件

| 事件 Cmd | 说明 |
|---------|------|
| `start` | 开始 |
| `play` | 播放 |
| `start_grab` | 开始抢麦 |
| `grab` | 抢麦 |
| `sing` | 唱歌 |
| `over` | 结束 |
| `recognize` | 识别 |
| `next` | 下一轮 |
| `end` | 结束 |

## CP 连线事件

| 事件 Cmd | 说明 |
|---------|------|
| `diy_emit` | 自定义发送 |
| `diy_reply` | 自定义回复 |
| `diy_expire` | 自定义过期 |
| `gift_send` | 赠送礼物 |
| `score_increased` | 分数增加 |
| `defend_value_modify` | 守护值修改 |
| `chose_relation` | 选择关系 |

## 房间进入事件

| 事件 Cmd | 说明 |
|---------|------|
| `change.room` | 换房事件 |
| `forbidden` | 禁言事件 |
| `config.after` | 配置后置 |

## 事件处理器模式

| 模式 | 优点 | 适用场景 |
|------|------|---------|
| switch-case | 简单直接 | 抢麦、CP 连线、房间进入 |
| HandleEventMap | 动态扩展 | 房间推荐、大哥房间、拍卖 |

## 跨项目事件协调

| 方向 | Topic | 说明 |
|------|-------|------|
| slp-room → slp-go | `xs.room.enter` | mood 模块消费 |
| slp-room → slp-go | `xs.user.gift` | 礼物模块消费 |
| slp-go → slp-room | `slp.user.mood` | 心情值相关功能 |
| slp-go → slp-room | `xs.relation.event` | 关系相关功能 |

## 相关知识

- [[patterns/event-extension-guide]]
- [[projects/slp-room/01-structure]]
