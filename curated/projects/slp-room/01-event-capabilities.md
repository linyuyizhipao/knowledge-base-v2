# slp-room 事件能力清单

> slp-room 项目的事件能力注册表，按业务领域组织

**最后更新**: 2026-04-05

---

## 事件能力总览

| 业务领域 | Topic | 消费者位置 | 处理方式 | 事件数量 |
|---------|-------|-----------|---------|---------|
| 房间推荐 | `slp.room.recommend.more` | `cmd/internal/room_recommend_more/` | HandleEventMap | 40+ |
| 房间 PK | `room.pk.topic` | `cmd/internal/room_pk/` | switch-case | 5 |
| 大哥房间 | `slp.big.brother` | `cmd/internal/big_brother/` | HandleEventMap | 4 |
| 抢麦事件 | `grabmic.TopicGrabMic` | `cmd/internal/grabmic/` | switch-case | 12 |
| CP 连线 | `cplink.TopicCplinkV2` | `cmd/internal/cplink/` | switch-case | 7 |
| 房间进入 | `xs.room.enter` | `cmd/internal/enter/` | switch-case | 3 |
| 拍卖事件 | `slp.auction` | `cmd/internal/auction/` | HandleEventMap | - |
| 心跳竞抢 | `heartrace.TopicHeartRace` | `cmd/internal/heartrace/` | switch-case | - |
| 领唱事件 | `leadsing.LEAD_SING_TOPIC` | `cmd/internal/lead_sing/` | switch-case | - |
| 狼人杀 | `guess_song.GUESS_SONG_TOPIC` | `cmd/internal/guess_song/` | switch-case | - |

---

## 1. 房间推荐事件

**Topic**: `slp.room.recommend.more`  
**消费者**: `cmd/internal/room_recommend_more/service.go`  
**处理方式**: HandleEventMap 路由 (100 并发)

### 事件常量定义

```go
// consts/room_recommend_more.go
const RoomRecommendMoreTopicName = "slp.room.recommend.more"

type RoomRecommendEvent string

const (
    BossChangeRoomRecommend   RoomRecommendEvent = "boss_change"           // 老板位变更
    EnterRoomRoomRecommend    RoomRecommendEvent = "enter_room"            // 进入房间
    SendGiftRoomRecommend     RoomRecommendEvent = "send_gift"             // 赠送礼物
    ExposureRoomRecommend     RoomRecommendEvent = "exposure_room"         // 房间曝光
    RefreshScoreRoomRecommend RoomRecommendEvent = "refresh_score"         // 刷新分数
)
```

### 事件处理器列表

| 事件 Cmd | 说明 | 处理器 | 位置 |
|---------|------|--------|------|
| `boss_change` | 老板位变更 | `bossChangeEvent` | `event/event_boss_change.go` |
| `enter_room` | 用户进入房间 | `enterRoomEvent` | `event/event_enter_room.go` |
| `send_gift` | 赠送礼物 | `sendGiftEvent` | `event/event_send_gift.go` |
| `exposure_room` | 房间曝光 | `exposureRoomEvent` | `event/event_exposure_room.go` |
| `refresh_score` | 刷新推荐分数 | `refreshScoreEvent` | `event/event_refresh_score_room.go` |
| `lucky_draw_event_mic_room` | 幸运抽奖麦位房 | `luckyDrawEventMicRoom` | `event/lucky_draw_event_mic_room.go` |
| `lucky_draw_event_enter_room` | 幸运抽奖进房 | `luckyDrawEventEnterRoom` | `event/lucky_draw_event_enter_room.go` |
| `lucky_draw_event_recommend_pool` | 幸运抽奖推荐池 | `luckyDrawEventRecommendPool` | `event/lucky_draw_event_recommend_pool.go` |
| `male_room_info_event_enter_room` | 男宾信息进房 | `maleRoomInfoEventEnterRoom` | `event/male_room_info_event_enter_room.go` |
| `male_room_info_event_leave_room` | 男宾信息离开 | `maleRoomInfoEventLeaveRoom` | `event/male_room_info_event_leave_room.go` |
| `male_room_info_event_send_im` | 男宾信息发 IM | `maleRoomInfoEventSendIm` | `event/male_room_info_event_send_im.go` |
| `user_statics_send_gift` | 用户统计打赏 | `userStaticsSendGiftEvent` | `event/user_statics_send_gift_event.go` |
| `user_statics_refresh_score` | 用户统计刷新分数 | `userStaticsRefreshScoreEvent` | `event/user_statics_refresh_score_event.go` |
| `starship_home_recommend_enter_room` | 星舰首页进房 | `starshipHomeRecommendEnterRoom` | `event/starship_home_recommend_enter_room.go` |
| `starship_home_recommend_leave_room` | 星舰首页离开 | `starshipHomeRecommendLeaveRoom` | `event/starship_home_recommend_leave_room.go` |
| `recharge_user_group_enter_room` | 369 观光团进房 | `recharge369GroupEnterRoom` | `event/recharge_369_group_enter_room.go` |
| `recharge_user_group_leave_room` | 369 观光团离开 | `recharge369GroupLeaveRoom` | `event/recharge_369_group_leave_room.go` |

### HandleEventMap 结构

```go
// cmd/internal/room_recommend_more/event/base.go
type HandleEvent interface {
    RoomRecommendEvent(ctx context.Context, data *cmd.NsqEventMsg) (err error)
}

var HandleEventMap = map[consts.RoomRecommendEvent]HandleEvent{}
```

### 新增事件

在 `cmd/internal/room_recommend_more/event/` 创建新文件，在 `init()` 中注册到 `HandleEventMap`：

```go
package event

func init() {
    HandleEventMap[consts.NewEventCmd] = &newEventHandler{}
}

type newEventHandler struct{}

func (h *newEventHandler) RoomRecommendEvent(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

---

## 2. 房间 PK 事件

**Topic**: `room.pk.topic`  
**消费者**: `cmd/internal/room_pk/consumer.go`  
**处理方式**: switch-case (50 并发)

### 事件常量定义

```go
// consts/room_pk.go
const (
    TopicRoomPkTopic = "room.pk.topic"
    RoomPkChannel    = "default"
)

const (
    RoomPkNextCmd            = "xs_room_pk.next"
    RoomPkBingLogCmd         = "xs_room_pk"
    RoomLivePkBingLogCmd     = "xs_live_pk"
    RoomLivePkMatchCmd       = "xs_live_pk_match"
    RoomLivePkCancelMatchCmd = "xs_live_pk_match_cancel"
)

const (
    RoomPkOnMic            = "match.on.mic"
    RoomPkOffMic           = "match.off.mic"
    RoomPkSetScore         = "match.set.score"
    RoomPkMatchAgreeInvite = "match.agree.invite"
    RoomPkMatchSuccess     = "match.success"
    RoomPkMatchRefuse      = "match.refuse"
    RoomPkMatchLoopInvite  = "match.loop.invite"
    RoomRefreshMultiPk     = "refresh.multi.pk"
)

const (
    RoomPkConsume       = "xs_room_pk.consume"
    RoomPkDefendConsume = "xs_room_pk.defend.consume"
)
```

### 事件处理

```go
// cmd/internal/room_pk/consumer.go
func (c *RoomPkConsumer) ConsumeHandler(message *nsq.Message) error {
    event := &RoomPkEvent{}
    if err := event.Unmarshal(message.Body); err != nil {
        return err
    }
    
    switch event.Cmd {
    case consts.RoomPkNextCmd:
        return c.onNext(event)
    case consts.RoomPkBingLogCmd:
        return c.onBinlog(event)
    case consts.RoomLivePkMatchCmd:
        return c.onMatch(event)
    // ... 更多 case
    }
    return nil
}
```

---

## 3. 大哥房间事件

**Topic**: `slp.big.brother`  
**消费者**: `cmd/internal/big_brother/service.go`  
**处理方式**: HandleEventMap (10 并发)

### 事件常量

```go
// consts/big_brother.go
const BigBrotherTopicName = "slp.big.brother"
```

### 事件处理器

| 事件 Cmd | 说明 | 处理器 | 位置 |
|---------|------|--------|------|
| `send_gift` | 赠送礼物 | `sendGiftHandler` | `event/send_gift.go` |
| `try_status_change` | 试用状态变更 | `tryStatusChangeHandler` | `event/try_status_change.go` |
| `pet_status_change` | 宠物状态变更 | `petStatusChangeHandler` | `event/pet_status_change.go` |

### HandleEventMap 结构

```go
// cmd/internal/big_brother/event/base.go
type BigBrotherEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var BigBrotherEventMap = map[string]BigBrotherEvent{}
```

---

## 4. 抢麦事件

**Topic**: `grabmic.TopicGrabMic`  
**消费者**: `cmd/internal/grabmic/event_consumer.go`  
**处理方式**: switch-case + 状态机

### 事件常量

```go
// app/service/grabmic/const.go
const TopicGrabMic = "grabmic.topic"

const (
    CmdStart       = "start"
    CmdPlay        = "play"
    CmdStartGrab   = "start_grab"
    CmdPublishGrab = "publish_grab"
    CmdGrab        = "grab"
    CmdSing        = "sing"
    CmdLight       = "light"
    CmdOver        = "over"
    CmdRecognize   = "recognize"
    CmdPublishSing = "publish_sing"
    CmdNext        = "next"
    CmdEnd         = "end"
)
```

### 事件处理

```go
// cmd/internal/grabmic/event_consumer.go
func (s *Service) ConsumeGrabMicEvent(message *nsq.Message) error {
    event := &grabmic.Event{}
    if err := event.UnMarshal(message.Body); err != nil {
        return err
    }
    
    switch event.Cmd {
    case grabmic.CmdStart:
        return s.OnGrabMicStart(&event.Event)
    case grabmic.CmdPlay:
        return s.OnGrabMicPlay(&event.Event)
    case grabmic.CmdStartGrab:
        return s.OnGrabMicStartGrab(&event.Event)
    case grabmic.CmdPublishGrab:
        return s.OnGrabMicGrabPublish(&event.Event)
    case grabmic.CmdGrab:
        return s.OnGrabMicGrab(&event.Event)
    case grabmic.CmdSing:
        return s.OnGrabMicSing(&event.Event)
    case grabmic.CmdLight:
        return s.OnGrabMicLight(&event.Event)
    case grabmic.CmdOver:
        return s.OnGrabMicSingOver(&event.Event)
    case grabmic.CmdRecognize:
        return s.OnGrabMicRecognize(&event.Event)
    case grabmic.CmdPublishSing:
        return s.OnGrabMicSingPublish(&event.Event)
    case grabmic.CmdNext:
        return s.OnGrabMicNext(&event.Event)
    case grabmic.CmdEnd:
        return s.OnGrabMicEnd(&event.Event)
    }
    return nil
}
```

### 状态机

使用 `extend.State` 和 `extend.NextState` 进行状态流转控制，Redis 锁保护：

```go
extend, room, err := s.checkEvent(event)
if extend.NextState != grabmic.StateStart {
    return nil // 状态不符，忽略
}
```

---

## 5. CP 连线事件

**Topic**: `cplink.TopicCplinkV2`  
**消费者**: `cmd/internal/cplink/cplink_consumer.go`  
**处理方式**: switch-case + 事件解析

### 事件常量

```go
// consts/cplink_v2.go
const TopicCplinkV2 = "cplink.v2.topic"

const (
    CmdDiyEmit         = "diy_emit"
    CmdDiyReply        = "diy_reply"
    CmdDiyExpire       = "diy_expire"
    CmdGiftSend        = "gift_send"
    CmdScoreIncreased  = "score_increased"
    CmdDefendValueModify = "defend_value_modify"
    CmdChoseRelation   = "chose_relation"
    CmdHelpRelation    = "help_relation"
)
```

### 事件处理

```go
// cmd/internal/cplink/cplink_consumer.go
func (s *cpLinkCmdServer) NsqMessageHandle(message *nsq.Message) error {
    e := &cplink.Event{}
    if err := e.Unmarshal(message.Body); err != nil {
        return nil
    }
    
    switch e.Cmd {
    case cplink.CmdDiyEmit:
        return s.onDiyEmit(ctx, e)
    case cplink.CmdDiyReply:
        return s.onDiyReply(ctx, e)
    case cplink.CmdDiyExpire:
        return s.onDiyExpire(ctx, e)
    case cplink.CmdGiftSend:
        return s.onGiftSend(ctx, e)
    case cplink.CmdScoreIncreased:
        return s.onDirty(ctx, e)
    case cplink.CmdDefendValueModify:
        return s.onDefendValueModify(ctx, e)
    case cplink.CmdChoseRelation:
        return s.onChoseRelation(ctx, e)
    case cplink.CmdHelpRelation:
        return s.onHelpSendGift(ctx, e)
    }
    return nil
}
```

---

## 6. 房间进入事件

**Topic**: `xs.room.enter`  
**消费者**: `cmd/internal/enter/consumer.go`  
**处理方式**: switch-case (PHP 序列化格式)

### 事件 Cmd

| 事件 Cmd | 说明 | 处理器 |
|---------|------|--------|
| `change.room` | 换房事件 | `onChangeRoom` |
| `forbidden` | 禁言事件 | `onForbidden` |
| `config.after` | 配置后置 | `onConfigAfter` |

### 事件处理

```go
// cmd/internal/enter/consumer.go
func (srv *enterServer) NsqHandle(message *nsq.Message) error {
    val, err := php_serialize.UnSerialize(string(message.Body))
    if err != nil {
        return err
    }
    
    info := val.(php_serialize.PhpArray)
    cmd, ok := info["cmd"]
    data, ok := info["data"]
    
    switch gconv.String(cmd) {
    case "change.room":
        err = srv.onChangeRoom(data)
    case "forbidden":
        err = srv.onForbidden(data)
    case "config.after":
        err = srv.onConfigAfter(data)
    }
    return nil
}
```

---

## 7. 其他事件消费者

### 7.1 拍卖事件

**Topic**: `slp.auction`  
**消费者**: `cmd/internal/auction/consumer.go`  
**处理方式**: HandleEventMap

### 7.2 心跳竞抢

**Topic**: `heartrace.TopicHeartRace`  
**消费者**: `cmd/internal/heartrace/consumer.go`  
**处理方式**: switch-case

### 7.3 领唱事件

**Topic**: `leadsing.LEAD_SING_TOPIC`  
**消费者**: `cmd/internal/lead_sing/consumer.go`  
**处理方式**: switch-case

### 7.4 狼人杀猜歌

**Topic**: `guess_song.GUESS_SONG_TOPIC`  
**消费者**: `cmd/internal/guess_song/consumer.go`  
**处理方式**: switch-case (100 并发)

### 7.5 房间热度

**Topic**: `slp.room.hot.update`  
**消费者**: `cmd/internal/room_hot/service.go`  
**处理方式**: switch-case (100 并发)

### 7.6 Bump 事件

**Topic**: `consts.TopicBumpTopic`  
**消费者**: `cmd/internal/bump/consumer.go`  
**处理方式**: switch-case (50 并发)

### 7.7 宠物事件

**Topic**: `pet.TopicPet`  
**消费者**: `cmd/internal/pet/nsq_consumer.go`  
**处理方式**: switch-case (20 并发)

---

## 跨项目事件协调

### slp-room → slp-go

| 事件 | Topic | 说明 |
|------|-------|------|
| 房间进入 | `xs.room.enter` | slp-go mood 模块消费 |
| 房间礼物 | `xs.user.gift` | slp-go 礼物模块消费 |
| 房间热度 | `xs.room.hot` | slp-go 热度模块消费 |

### slp-go → slp-room

| 事件 | Topic | 说明 |
|------|-------|------|
| 心情值更新 | `slp.user.mood` | slp-room 心情值相关功能 |
| 关系事件 | `xs.relation.event` | slp-room 关系相关功能 |

---

## 新增事件 Checklist

### 步骤 1: 确定事件类型

- [ ] 是否需要新建 Topic？
- [ ] 是否可以复用现有 Topic？
- [ ] 事件处理方式（switch-case / HandleEventMap / 观察者模式）

**HandleEventMap**: 适用于需要动态扩展的场景（如房间推荐、大哥房间）
**switch-case**: 适用于简单、固定的事件处理（如抢麦、CP 连线、房间进入）

### 步骤 2: 定义事件常量

```go
// consts/<module>.go
const (
    MyEventTopic = "xs.my.topic"
)

type MyEvent string
const (
    MyEventAction MyEvent = "my_action"
)
```

### 步骤 3: 创建事件处理器

**HandleEventMap 模式**:
```go
// cmd/internal/<module>/event/xxx_event.go
func init() {
    HandleEventMap[consts.MyEventAction] = &myEventHandler{}
}

type myEventHandler struct{}

func (h *myEventHandler) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

**switch-case 模式**:
```go
// cmd/internal/<module>/consumer.go
func (s *Service) ConsumeHandler(message *nsq.Message) error {
    event := &MyEvent{}
    if err := event.Unmarshal(message.Body); err != nil {
        return err
    }
    
    switch event.Cmd {
    case "my_action":
        return s.onMyAction(event)
    }
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
// NSQ 发送 (JSON 格式)
type NsqEventData struct {
    Cmd  string `json:"cmd"`
    Data any    `json:"data"`
}

nsqData, _ := json.Marshal(&NsqEventData{
    Cmd:  "my.event.action",
    Data: eventData,
})
_ = library.NsqClient().SendBytes("xs.my.topic", nsqData, 2*time.Second)
```

---

## 事件调试

### 查看 NSQ Topic 状态

```bash
# 查看 Topic 信息
curl http://nsqadmin:4171/api/topic?topic=slp.room.recommend.more

# 查看消费者连接
curl http://nsqadmin:4171/api/channel?topic=slp.room.recommend.more&channel=default
```

### 本地测试发送事件

```bash
# 发送 NSQ 事件
curl -X POST http://localhost:4151/pub?topic=slp.room.recommend.more \
  -d '{"cmd":"enter_room","data":{"rid":123,"uid":456}}'
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
| switch-case | 简单直接 | 不支持动态扩展 | 抢麦、CP 连线、房间进入 |
| HandleEventMap | 支持动态扩展、符合开闭原则 | 需要额外的注册步骤 | 房间推荐、大哥房间、拍卖 |

---

**维护说明**:
- 新增事件能力时，在对应章节追加记录
- 废弃事件时，在事件后标注 `@deprecated` 和废弃日期
- 每季度审查一次事件列表，清理无用事件
