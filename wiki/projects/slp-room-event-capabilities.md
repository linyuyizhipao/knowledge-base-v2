---
id: slp-room-event-capabilities
label: slp-room 事件能力清单
source: curated/projects/slp-room/01-event-capabilities.md
project: slp-room
role: event-capabilities
compiled: 2026-04-25
tags:
  - event
  - topic
  - consumer
links:
  - slp-room-structure
  - slp-room-architecture
---

# slp-room 事件能力清单

> slp-room 项目的事件能力注册表，按业务领域组织

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
    BossChangeRoomRecommend   RoomRecommendEvent = "boss_change"
    EnterRoomRoomRecommend    RoomRecommendEvent = "enter_room"
    SendGiftRoomRecommend     RoomRecommendEvent = "send_gift"
    ExposureRoomRecommend     RoomRecommendEvent = "exposure_room"
    RefreshScoreRoomRecommend RoomRecommendEvent = "refresh_score"
)
```

### HandleEventMap 结构

```go
// cmd/internal/room_recommend_more/event/base.go
type HandleEvent interface {
    RoomRecommendEvent(ctx context.Context, data *cmd.NsqEventMsg) (err error)
}

var HandleEventMap = map[consts.RoomRecommendEvent]HandleEvent{}
```

### 事件处理器列表

| 事件 Cmd | 说明 |
|---------|------|
| `boss_change` | 老板位变更 |
| `enter_room` | 用户进入房间 |
| `send_gift` | 赠送礼物 |
| `exposure_room` | 房间曝光 |
| `refresh_score` | 刷新推荐分数 |
| `lucky_draw_event_mic_room` | 幸运抽奖麦位房 |
| `lucky_draw_event_enter_room` | 幸运抽奖进房 |
| `recharge_user_group_enter_room` | 369 观光团进房 |
| `recharge_user_group_leave_room` | 369 观光团离开 |

---

## 2. 房间 PK 事件

**Topic**: `room.pk.topic`  
**消费者**: `cmd/internal/room_pk/`  
**处理方式**: switch-case

| 事件 Cmd | 说明 |
|---------|------|
| `pk_start` | PK 开始 |
| `pk_end` | PK 结束 |
| `pk_score` | PK 分数变化 |
| `pk_gift` | PK 礼物 |
| `pk_close` | PK 关闭 |

---

## 3. 大哥房间事件

**Topic**: `slp.big.brother`  
**消费者**: `cmd/internal/big_brother/`  
**处理方式**: HandleEventMap

| 事件 Cmd | 说明 |
|---------|------|
| `big_brother_enter` | 大哥进入房间 |
| `big_brother_leave` | 大哥离开房间 |
| `big_brother_gift` | 大哥送礼 |
| `big_brother_upgrade` | 大哥升级 |

---

## 新增事件方式

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