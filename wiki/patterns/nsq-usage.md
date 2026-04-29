---
id: patterns/nsq-usage
label: nsq-usage
source: /Users/hugh/project/my-wiki/curated/patterns/nsq-usage.md
role: 规范
compiled: 2026-04-28
source_hash: fe56ae6ea0c341ae3d405e83ff77713c
---

> SLP 项目统一的 NSQ 事件发送与消费标准

**最后更新**: 2026-04-11

---

## 发送格式

### 格式 1: JSON 格式（推荐，新项目默认）

**适用场景**: 新业务、跨项目事件、需要人类可读的事件

```go
type NsqEventData struct {
    Cmd  string `json:"cmd"`
    Data any    `json:"data"`
}

// 发送事件
nsqData, _ := json.Marshal(&NsqEventData{
    Cmd:  "room_gift_send",
    Data: data,
})
_ = library.NsqClient().SendBytes("xs.room.event", nsqData, 2*time.Second)
```

**完整示例**：

```go
// 1. 定义事件数据结构
type RoomGiftSendData struct {
    Rid      uint32 `json:"rid"`
    Uid      uint32 `json:"uid"`
    GiftId   uint32 `json:"giftId"`
    GiftNum  uint32 `json:"giftNum"`
    Dataline uint32 `json:"dateline"`
}

// 2. 发送
func sendRoomGiftEvent(ctx context.Context, rid, uid, giftId uint32) {
    data := &RoomGiftSendData{
        Rid:      rid,
        Uid:      uid,
        GiftId:   giftId,
        GiftNum:  1,
        Dataline: uint32(time.Now().Unix()),
    }
    
    nsqData, _ := json.Marshal(&NsqEventData{
        Cmd:  "room_gift_send",
        Data: data,
    })
    
    _ = library.NsqClient().SendBytes("xs.room.event", nsqData, 2*time.Second)
}
```

---

### 格式 2: PHP 序列化格式（仅兼容老代码）

**适用场景**: 兼容 PHP 时代的代码、与老消费者对接

```go
import "github.com/yvasiyarov/php_session_decoder/php_serialize"

// 发送 PHP 序列化数据
data := g.Map{"uid": uid, "rid": rid}
dataBytes, _ := php_serialize.Serialize(data)
_ = library.NsqClient().SendBytes("xs.mission", dataBytes)
```

---

## 常用 Topic 清单

### 跨项目通用 Topic

| Topic | 用途 | 典型事件 |
|-------|------|---------|
| `xs.common.room.event` | 房间事件 | enter_room, leave_room |
| `xs.full.screen` | 全站飘屏 | cmd.online.room |
| `xs.mission` | 任务中心 | room_stay_times, send_gift |
| `xs.mysql_to_es` | MySQL → ES 同步 | update_room_hot |
| `slp.user.mood` | 心情值系统 | chat, marry, game |
| `xs.relation` | 关系系统 | send_gift, defend_update |

### 项目特有 Topic

| Topic | 项目 | 用途 |
|-------|------|------|
| `slp.room.recommend.event` | slp-room | 信息流推荐房间事件 |
| `slp.room.recommend.more` | slp-room | 推荐房间扩展事件 |
| `xs.hour.rank` | slp-go | 小时榜事件 |

---

## 消费模式

根据业务复杂度选择合适的消费模式：

| 模式 | 适用场景 | 参考文档 |
|------|---------|---------|
| **switch-case 直接处理** | 简单事件处理（如房间事件） | 本文下文 |
| **HandleEventMap 路由** | 需动态扩展的复杂业务 | [[event-extension-guide]] 附录 A |
| **观察者模式** | 一个事件触发多个业务响应 | [[event-extension-guide]] 附录 B |

---

### 模式 1: switch-case 直接处理

```go
// cmd/internal/room_event/nsq_handler.go
func (s *RoomEventService) Consumer(msg *nsq.Message) error {
    nsqMsg, _ := s.ParseNsqMsg(msg)
    
    switch nsqMsg.Cmd {
    case "room.enter.pretty":
        return s.handleRoomEnter(nsqMsg, true)
    case "room.leave":
        return s.handleRoomLeave(nsqMsg)
    default:
        return gerror.Newf("cmd=%s 协议暂不支持", nsqMsg.Cmd)
    }
}
```

---

### 模式 2: HandleEventMap 路由

👉 **完整规范**: [[event-extension-guide]] 附录 A

```go
// 定义接口和注册表
type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var HandleEventMap = map[consts.ModuleEvent]HandleEvent{}

// 消费者统一分发
func (s *Service) NsqMessageHandler(message *nsq.Message) error {
    nsqMsg, _ := s.ParseNsqMsg(message)
    topicCmd := consts.ModuleEvent(nsqMsg.Cmd)
    
    handle, ok := HandleEventMap[topicCmd]
    if !ok {
        return gerror.Newf("cmd=%s 协议暂不支持", nsqMsg.Cmd)
    }
    
    return handle.Handle(ctx, nsqMsg)
}
```

---

### 模式 3: 观察者模式

👉 **完整规范**: [[event-extension-guide]] 附录 B

```go
// 定义观察者接口
type RechargeObserver interface {
    RechargeEvent(ctx context.Context, req *pb.ReqUserRechargeFn) error
}

var rechargeObservers []RechargeObserver

// 事件触发（遍历所有观察者）
func RechargeEvent(ctx context.Context, req *pb.ReqUserRechargeFn) {
    for _, observer := range rechargeObservers {
        _ = g.Try(func() {
            _ = observer.RechargeEvent(ctx, req)
        })
    }
}
```

---

## 消费者启动标准

```go
func (s *Service) StartConsumer() error {
    return library.NewNsqWorker(
        "xs.common.room.event",  // Topic
        "common",                 // Channel 名称
        s.Consumer,               // 消费函数
    ).ConnectWithConcurrency(100) // 并发度
}
```

**参数说明**：

| 参数 | 说明 | 建议值 |
|------|------|--------|
| Topic | 事件主题 | 按业务划分 |
| Channel | 消费者组名称 | 同组消费者共享消息 |
| Concurrency | 并发消费数 | 50-200（根据业务） |

---

## 事件常量管理

**推荐做法：集中定义**

```go
// consts/events.go
type RoomEvent string

func (s RoomEvent) ToString() string {
    return string(s)
}

const (
    RoomEnterEvent RoomEvent = "room_enter"
    RoomLeaveEvent RoomEvent = "room_leave"
    RoomHotChangeEvent RoomEvent = "room_hot_change"
)
```

**使用时**：

```go
// 发送
nsqData, _ := json.Marshal(&NsqEventData{
    Cmd:  consts.RoomEnterEvent.ToString(),
    Data: data,
})

// 消费
switch nsqMsg.Cmd {
case consts.RoomEnterEvent.ToString():
    // 处理
}
```

---

## 最佳实践

### 1. 错误处理

```go
// 带超时的发送（推荐）
err := library.NsqClient().SendBytes("xs.topic", nsqData, 2*time.Second)
if err != nil {
    g.Log().Ctx(ctx).Error("msg", "send nsq failed", "err", err)
}
```

### 2. 幂等性保证

```go
// 使用 Redis 去重
key := fmt.Sprintf("slp.my.event.%d.%d", uid, time.Now().Unix()/3600)
if !redis.SetNX(ctx, key, 1, time.Hour).Val() {
    return // 已处理
}
```

### 3. 事务性考虑

```go
// 先落库，再发事件（事务提交后）
err := dao.XsMyTable.DB.Transaction(func(tx *gdb.TX) error {
    // 1. 先写数据库
    if err := dao.XsMyTable.TX(tx).Data(data).Insert(); err != nil {
        return err
    }
    // 2. 事务提交后再发事件
    tx.OnCommit(func() {
        sendNsqEvent(data)
    })
    return nil
})
```

### 4. 事件日志

```go
// 关键事件记录日志（异步，避免阻塞）
g.Log().Async(true).Ctx(ctx).Info(
    "msg", "event.sent",
    "topic", topic,
    "cmd", cmd,
    "data", data,
)
```

---

## 事件调试

### 本地测试：手动发送事件

```bash
curl -X POST http://localhost:4151/pub?topic=xs.common.room.event \
  -d '{"cmd":"room.enter","data":{"uid":123,"rid":456}}'
```

### 日志排查

```go
// 消费者日志
g.Log().Ctx(ctx).Info(
    "msg", "NsqMessageHandler",
    "nsqMsg.Cmd", nsqMsg.Cmd,
    "data", nsqMsg.Data,
)
```

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [[event-extension-guide]] | 事件拓展总纲（含完整示例） |
| [[cmd-module-standard]] | CMD 模块标准结构 |

---

**版本**: 1.0 | **最后更新**: 2026-04-11
