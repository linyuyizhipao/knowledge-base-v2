# slp-go 事件能力清单

> slp-go 项目的事件能力注册表，按业务领域组织

**最后更新**: 2026-04-05

---

## 事件能力总览

| 业务领域 | Topic | 事件处理器位置 | 事件数量 |
|---------|-------|---------------|---------|
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

---

## 1. 充值回调事件

**Topic**: `slp.recharge.after.topic`  
**消费者**: `cmd/internal/pay/pay_callback/service.go`  
**处理方式**: `RechargeCallBackMap` 路由

| 事件 Cmd | 说明 | 处理器 | 位置 |
|---------|------|--------|------|
| `recharge_369` | 369 元观光团充值 | `RechargeType369Callback` | `app/service/recharge/recharge369V2.go` |
| `user_back` | 用户返利充值 | `RechargeUserBackCallback` | `cmd/internal/pay/pay_callback/internal/user_back.go` |

**新增事件**: 在 `cmd/internal/pay/pay_callback/internal/` 创建新文件，注册到 `RechargeCallBackMap`

---

## 2. 关系事件

**Topic**: `xs.relation.event`  
**消费者**: `cmd/internal/relation/consume.go`  
**处理方式**: `HandleEventMap` 路由

| 事件 Cmd | 说明 | 处理器 | 位置 |
|---------|------|--------|------|
| `send_gift` | 赠送关系礼物 | `sendGiftEvent` | `app/service/relation/event/send_gift_event.go` |
| `relieve_relation` | 解除关系 | `relieveEvent` | `app/service/relation/event/relieve_event.go` |
| `divorce` | 离婚 | `divorceEvent` | `app/service/relation/event/divorce_event.go` |
| `xs_relation_defend` | 守护值更新 | `xsRelationDefendEvent` | `app/service/relation/event/xs_relation_defend.go` |
| `xs_relation_level` | 关系等级变化 | `xsRelationLevelEvent` | `app/service/relation/event/xs_relation_level.go` |
| `relation_pretend_switch_change` | 关系装扮切换 | `relationPretendSwitchEvent` | `app/service/relation/event/relation_pretend_switch.go` |
| `xs_relation_box_process` | 关系盲盒进度 | `xsRelationBoxProcess` | `app/service/relation/event/blind_xs_relation_box_process.go` |
| `relation_box_delay_im` | 盲盒延时通知 | `relationBlindXsRelationBoxDelay` | `app/service/relation/event/blind_delay_im.go` |
| `star_enter_alveolus_task` | 星愿进入小窝任务 | `starEnterAlveolusTask` | `app/service/relation/event/star_wish_enter_alveolus_task.go` |
| `star_game_times_day_task` | 星愿游戏任务 | `starGameTimesDayTask` | `app/service/relation/event/star_wish_game_times_day_task.go` |
| `star_send_love_token_gift_task` | 星愿赠送誓约信物 | `starSendLoveTokenMateGiftTask` | `app/service/relation/event/star_wish_send_love_token_gift_task.go` |
| `star_add_relation_task` | 星愿新增/续期关系 | `starAddRelationGiftTask` | `app/service/relation/event/star_wish_add_relation_gift_task.go` |
| `xs_relation_star_user_wish` | 星愿用户许愿 | `xsRelationStarUserWishEvent` | `app/service/relation/event/xs_relation_star_user_wish.go` |

**相关 Topic**:
- `xs.relation.keepsake.alveolus` - 关系小窝信物
- `xs.relation.defend` - 守护值榜单

**新增事件**: 在 `app/service/relation/event/` 创建 `xxx_event.go`，在 `init()` 中注册到 `HandleEventMap`

---

## 3. 心情值事件

**Topic**: `slp.user.mood`  
**消费者**: `cmd/internal/mood/service.go`  
**处理方式**: `HandleEventMap` 路由

| 事件 Cmd | 说明 | 处理器 | 位置 |
|---------|------|--------|------|
| `online` | 用户上线 | `OnlineEvent` | `app/service/mood/event_online.go` |
| `chat` | 聊天 | `ChatEvent` | `app/service/mood/event_chat.go` |
| `marry` | 结婚 | `MarryEvent` | `app/service/mood/event_marry.go` |
| `marry_in_room` | 与伴侣同房间 | `MarryInRoomEvent` | `app/service/mood/event_marry_inroom.go` |
| `relation` | 关系事件 | `RelationEvent` | `app/service/mood/event_relation.go` |
| `circle` | 发朋友圈 | `CircleEvent` | `app/service/mood/event_circle.go` |
| `add_score` | 加分事件 | `AddScoreEvent` | `app/service/mood/event_add_score.go` |
| `reduce_score` | 减分事件 | `ReduceScoreEvent` | `app/service/mood/event_reduce_score.go` |
| `game` | 游戏 | `GameEvent` | `app/service/mood/event_game.go` |
| `room_message` | 房间消息 | `RoomMessageEvent` | `app/service/mood/event_room_message.go` |

**独立 Topic**: `slp.room.message` - 房间消息（专用消费者）

**新增事件**: 在 `app/service/mood/` 创建 `event_xxx.go`，在 `init()` 中注册到 `HandleEventMap`

---

## 4. 礼物打赏事件

**Topic**: `xs.user.gift`  
**消费者**: `cmd/internal/user_gift/consumer.go`  
**处理方式**: switch-case 直接处理

| 事件 Cmd | 说明 | 处理逻辑 |
|---------|------|---------|
| `xs_pay_change_new` | 支付订单变更 | `nsqMsgHandler` - 处理礼物打赏、商城购买、头衔升级 |
| `user_first_recharge_delay_event` | 首次充值延时 | 发送 IM 通知 |
| `gift_msg_by_manual_trigger` | 手动触发礼物 | `nsqGiftMsgByManualTrigger` |

**业务逻辑**:
- 礼物图鉴点亮
- 师徒打赏任务
- 星座拍拍拍
- 缘分 AI 聊天触发
- 礼物图鉴黑名单处理
- 帝王套赠送通知

---

## 5. 通用礼物事件

**Topic**: `slp.common.gift.send`  
**消费者**: `cmd/internal/common_gift_send/`  
**处理方式**: 多 Channel 分发

| Channel | 说明 | 处理器 |
|--------|------|--------|
| `go-default` | 默认礼物处理 | `CommonGiftSend.Handle` |
| `goddess-car` | 女神车礼物 | `CommonGiftSend.GoddessCarHandle` |
| `go-guild-revenue-rank` | 家族收入榜 | `HandleGuildRevenueRank` |

**独立 Channel 的 Topic**:
| Topic | Channel | 说明 | 处理器 |
|------|---------|------|--------|
| `slp.healer.ticket` | `default` | 治愈系门票 | `CommonGiftSend.HandleHealerTicket` |
| `slp.emoji.gift` | `default` | 表情包礼物 | `CommonGiftSend.HandleEmoji` |
| `slp.surprise.box` | `default` | 惊喜盒子 | `CommonGiftSend.HandleSurpriseBox` |
| `slp.leap.leap` | `default` | 跳一跳 | `CommonGiftSend.HandleLeap` |
| `slp.big.brother` | `default` | 大哥房 | `CommonGiftSend.HandleBigBrother` |

---

## 6. 房间事件

**Topic**: `xs.common.room.event`  
**消费者**: `cmd/internal/room_event/nsq_handler.go`  
**处理方式**: switch-case 路由

| 事件 Cmd | 说明 | 处理器 |
|---------|------|--------|
| `room.enter.pretty` | 进入靓号房 | `handleRoomEnter` |
| `room.leave` | 离开房间 | `handleRoomLeave` |
| `room.enter` | 通用进房 | `handleRoomEnterCommon` |
| `room.reception.on.mic` | 接待上麦 | `handleRoomReceptionOnMic` |
| `room.hot.change` | 房间热度变化 | `handleRoomHotChange` |

**进房事件触发的子业务**:
- `handleActGodWarPush` - 诸神神王飘屏
- `handleRookieBenefit` - 新人福利
- `handleFunctionMap` - 功能地图
- `handleMood` - 心情值处理

---

## 7. 功能地图事件

**Topic**: `function_map`、`game.game_round_result`  
**消费者**: `cmd/internal/function_map/consumer.go`  
**处理方式**: Kafka + NSQ 混合

| 事件 Cmd | 来源 | 说明 |
|---------|------|------|
| `check_in` | 游戏结果 | 用户游戏签到 |
| `report` | 功能地图 | 解锁进度上报 |
| `cmd.handle.imprint.game` | 游戏印象 | 狼人杀印象标记 |

---

## 8. 装扮系统事件

**Topic**: `pretend.event.topic`  
**消费者**: `cmd/internal/pretend/consume.go`  
**处理方式**: 自定义事件解码 + switch-case

| 事件 Cmd | 说明 | 处理器 |
|---------|------|--------|
| `mic.leave` | 下麦事件 | `onLeaveMic` - 随机切换麦序装扮 |
| `room.leave` | 离开房间 | `onLeaveRoom` - 随机切换房间装扮 |
| `pretend.expire` | 装扮过期 | `onPretendExpire` - 取消装扮 |
| `send.relation.pretend` | 赠送关系装扮 | `onSendRelationPretend` |

---

## 9. 小时榜事件

**Topic**: `xs.hour.rank`  
**消费者**: `cmd/internal/hour_rank/consumer.go`  
**处理方式**: 自定义事件解码

| 事件 Cmd | 说明 |
|---------|------|
| `room_gift_send` | 房间礼物发送 |
| `incr_rank_user_rank_req` | 排行榜用户分数更新 |

---

## 10. 广场事件

**Topic**: `xs.square.circle`  
**消费者**: `cmd/internal/square/`  
**处理方式**: HandleEventMap 路由

| 事件 Cmd | 说明 |
|---------|------|
| `publish_circle` | 发布动态 |
| `follow_topic` | 关注话题 |
| `unfollow_topic` | 取关话题 |
| `comment_audit` | 评论审核 |
| `circle_audit` | 动态审核 |
| `like_circle` | 点赞动态 |

---

## 其他事件 Topic

| Topic | 业务 | 位置 |
|-------|------|------|
| `xs.room.red.packet` | 房间红包 | `cmd/internal/room_red_packet/` |
| `xs.world.red.packet` | 世界红包 | `cmd/internal/world_red_packet/` |
| `xs.achieve.wall` | 成就墙 | `cmd/internal/achieve/` |
| `xs.mission` | 任务中心 | `cmd/internal/mission/` |
| `xs.full.screen` | 全站飘屏 | `cmd/internal/full_screen/` |
| `xs.user.sign.in` | 用户签到 | `cmd/internal/signin/` |
| `slp.room.recommend.event` | 推荐房间 | `cmd/internal/room_pur_recommend/` |
| `starship.event.topic` | 星舰事件 | `cmd/internal/starship/` |

---

## 新增事件 Checklist

### 步骤 1: 确定事件类型

- [ ] 是否需要新建 Topic？
- [ ] 是否可以复用现有 Topic？
- [ ] 事件处理方式（switch-case / HandleEventMap / 观察者模式）

**观察者模式**: 如果一个事件需要触发多个业务响应，使用观察者模式。
👉 **完整规范**: [[event-extension-guide.md]] 附录 B

### 步骤 2: 定义事件常量

```go
// app/consts/<module>.go
const (
    MyEventTopic = "xs.my.topic"
)

type MyEvent string
const (
    MyEventAction MyEvent = "my_action"
)
```

### 步骤 3: 创建事件处理器

```go
// cmd/internal/<module>/consumer.go 或 app/service/<module>/event/
func init() {
    HandleEventMap[consts.MyEventAction] = &myEventHandler{}
}

type myEventHandler struct{}

func (s *myEventHandler) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

### 步骤 4: 注册消费者

```go
// cmd/internal/<module>/service.go
func (s *Service) consume() error {
    return library.NewNsqWorker(
        consts.MyEventTopic,
        library.NsqGroupDefault,
        s.NsqMessageHandler,
    ).ConnectWithConcurrency(50)
}
```

### 步骤 5: 发送事件

```go
// NSQ 发送
domain.SendEvent(ctx, consts.MyEventTopic, consts.MyEventAction.ToString(), php_serialize.PhpArray{
    "uid": uid,
    "rid": rid,
})
```

---

## 事件调试

### 查看事件消费者状态

```bash
# 查看 NSQ Topic 信息
curl http://nsqadmin:4171/api/topic?topic=xs.relation.event

# 查看消费者连接
curl http://nsqadmin:4171/api/channel?topic=xs.relation.event&channel=default
```

### 本地测试发送事件

```bash
# 发送 NSQ 事件
curl -X POST http://localhost:4151/pub?topic=xs.relation.event \
  -d '{"cmd":"send_gift","data":{"uid":123,"to_uid":456,"giftId":789}}'
```

### 日志排查

```go
// 所有事件处理都有统一日志
g.Log().Ctx(ctx).Info("msg", "NsqMessageHandler", "nsqMsg.Cmd", nsqMsg.Cmd)
```

---

## 事件处理器模式对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|---------|
| switch-case | 简单直接 | 不支持动态扩展 | 房间事件、礼物事件 |
| HandleEventMap | 支持动态扩展、符合开闭原则 | 需要额外的注册步骤 | 关系事件、心情值 |
| 观察者模式 | 一个事件多业务响应、完全解耦 | 需要统一的触发函数 | 充值回调、钻石消耗 |

👉 **完整规范**: [[event-extension-guide.md]]

---

**维护说明**:
- 新增事件能力时，在对应章节追加记录
- 废弃事件时，在事件后标注 `@deprecated` 和废弃日期
- 每季度审查一次事件列表，清理无用事件
