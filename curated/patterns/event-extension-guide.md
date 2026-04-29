# 事件能力拓展指南

> SLP 项目统一的事件能力拓展规范 - 适用于所有 Go 项目

**最后更新**: 2026-04-11

---

## 核心理念

**一个事件，多个响应；业务解耦，自由拓展**

当新增业务能力时，不应修改原有事件处理逻辑，而是通过**注册新观察者**或**新事件 handler**的方式无缝接入。

---

## 事件处理三种模式

根据业务场景选择合适的事件处理模式：

| 模式 | 适用场景 | 拓展方式 | 参考文档 |
|------|---------|---------|---------|
| **观察者模式** | 一个事件触发多个业务响应（如充值、钻石消耗） | 新增 Observer 实现 | 本文 附录 B |
| **HandleEventMap 路由** | 一个事件路由到单一处理器（如关系事件、心情值） | 新增 Handler 实现 | 本文 附录 A |
| **switch-case 直接处理** | 简单、固定的事件处理（如房间事件） | 新增 case 分支 | [[nsq-usage.md]] |

---

## 事件能力拓展流程

### 第一步：判断事件类型

```
                    ┌─────────────────┐
                    │  新增事件能力    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
    ┌─────────────────┐ ┌───────────┐ ┌─────────────┐
    │ 一个事件多个响应？│ │ 一个事件  │ │ 简单固定       │
    │ 如充值→多个业务  │ │ →一个处理？│ │ 的事件处理？   │
    └────────┬────────┘ └─────┬─────┘ └──────┬──────┘
             │                │               │
             │ YES            │ YES           │ YES
             │                │               │
             ▼                ▼               ▼
    ┌─────────────────┐ ┌───────────┐ ┌─────────────┐
    │ 观察者模式       │ │ HandleEvent│ │ switch-case │
    │ Observer        │ │ Map 路由   │ │ 直接处理    │
    └─────────────────┘ └───────────┘ └─────────────┘
```

**快速判断**：
- 充值、钻石消耗、礼物打赏 → **观察者模式**
- 关系事件、心情值、广场事件 → **HandleEventMap 路由**
- 房间事件、简单固定逻辑 → **switch-case**

---

## 第二步：按模式实现

### 模式 A：观察者模式

**核心代码**：
```go
// app/service/<module>/event/base.go
type <Module>Observer interface {
    <Module>Event(ctx context.Context, param *pb.Req<Module>Fn) error
}

var <module>Observers []<Module>Observer

func <Module>Event(ctx context.Context, param *pb.Req<Module>Fn) {
    for _, observer := range <module>Observers {
        _ = g.Try(func() {
            _ = observer.<Module>Event(ctx, param)
        })
    }
}
```

**观察者实现**：
```go
// app/service/<module>/event/<business>_observer.go
func init() {
    <module>Observers = append(<module>Observers, &<Business>Observer{})
}

type <Business>Observer struct{}

func (b *<Business>Observer) <Module>Event(ctx context.Context, param *pb.Req<Module>Fn) error {
    // 业务逻辑
    return nil
}
```

👉 **完整规范**: 本文 附录 B

---

### 模式 B：HandleEventMap 路由

**核心代码**：
```go
// app/service/<module>/event/base.go
type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var HandleEventMap = map[consts.ModuleEvent]HandleEvent{}
```

**Handler 实现**：
```go
// app/service/<module>/event/event_<action>.go
func init() {
    HandleEventMap[consts.MyActionEvent] = &myActionEvent{}
}

type myActionEvent struct{}

func (s *myActionEvent) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

👉 **完整规范**: 本文 附录 A

---

### 模式 C：switch-case 直接处理

**核心代码**：
```go
// cmd/internal/<module>/consumer.go
func (s *Service) Consumer(msg *nsq.Message) error {
    nsqMsg, _ := s.ParseNsqMsg(msg)
    
    switch nsqMsg.Cmd {
    case "event.action.a":
        return s.handleActionA(nsqMsg)
    case "event.action.b":
        return s.handleActionB(nsqMsg)
    }
    return nil
}
```

👉 **完整规范**: [`nsq-usage.md`](./nsq-usage.md)

---

## 第三步：发送事件

**NSQ 发送标准格式**：

```go
// JSON 格式（推荐）
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

👉 **完整规范**: [`nsq-usage.md`](./nsq-usage.md)

---

## 新增事件能力 Checklist

### 设计阶段

- [ ] 明确事件类型（观察者 / HandleEventMap / switch-case）
- [ ] 确定 Topic 名称（复用或新建）
- [ ] 定义事件常量

### 实现阶段

- [ ] 创建事件处理器/观察者
- [ ] 在 init() 中注册
- [ ] 实现业务逻辑
- [ ] 添加单元测试

### 验证阶段

- [ ] 本地测试发送事件
- [ ] 验证消费者启动日志
- [ ] 验证事件处理日志
- [ ] 验证错误处理

---

## 项目级事件能力清单

每个项目应维护自己的事件能力清单：

```
projects/<project-name>/
└── XX-event-capabilities.md  # 事件能力清单
```

**内容包含**:
- 所有 Topic 列表
- 每个 Topic 的事件 Cmd 列表
- 事件处理器位置
- 新增事件示例

👉 **参考模板**: [`projects/slp-go/09-event-capabilities.md`](./projects/slp-go/09-event-capabilities.md)

---

## 事件调试指南

### 查看 NSQ Topic 状态

```bash
# 查看 Topic 信息
curl http://nsqadmin:4171/api/topic?topic=xs.relation.event

# 查看消费者连接
curl http://nsqadmin:4171/api/channel?topic=xs.relation.event&channel=default
```

### 本地测试发送事件

```bash
curl -X POST http://localhost:4151/pub?topic=xs.relation.event \
  -d '{"cmd":"send_gift","data":{"uid":123,"to_uid":456,"giftId":789}}'
```

---

## 最佳实践

### 1. 命名规范

| 类型 | 命名规则 | 示例 |
|------|---------|------|
| Topic | `xs.<module>.<event>` | `xs.relation.event` |
| 事件 Cmd | `<action>_<target>` | `send_gift` |
| 观察者 | `<Business>Observer` | `Recharge369Observer` |
| Handler | `<action>Event` | `sendGiftEvent` |

### 2. 错误处理

```go
// 推荐：记录错误但不中断
func (o *myObserver) Event(ctx context.Context, param) error {
    if err := doSomething(); err != nil {
        g.Log().Ctx(ctx).Error("msg", "doSomething failed", "err", err)
        return err
    }
    return nil
}
```

### 3. 超时控制

```go
// 推荐：设置超时
func (o *myObserver) Event(ctx context.Context, param) error {
    ctx, cancel := context.WithTimeout(ctx, 500*time.Millisecond)
    defer cancel()
    return o.doWithTimeout(ctx, param)
}
```

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [[cmd-module-standard.md]] | CMD 模块标准结构 |
| [[nsq-usage.md]] | NSQ 使用规范 |

---

## 附录 A：HandleEventMap 模式完整示例

### A.1 完整代码结构

```
cmd/internal/signin/
├── service.go          # 启动消费者 + 主处理逻辑
├── constants.go        # Topic 常量
└── handler.go          # 可选：复杂逻辑拆分
```

### A.2 完整实现代码

**constants.go** - Topic 常量定义：
```go
package signin

const Topic = "slp.signin.topic"
```

**service.go** - 完整实现（含二次路由）：
```go
package signin

import (
    "context"
    "encoding/json"
    "slp-go/cmd"
    "slp-go/app/service/signin"
    "github.com/gogf/gf/v2/frame/g"
    "github.com/nsqio/go-nsq"
)

type Service struct{}

func NewService() *Service {
    return &Service{}
}

// Run 启动消费者（在 cmd/main.go 中调用）
func (s *Service) Run() error {
    return library.NewNsqWorker(
        Topic,
        library.NsqGroupDefault,
        s.NsqMessageHandler,
    ).ConnectWithConcurrency(10)
}

// NsqMessageHandler 主路由（HandleEventMap 模式核心）
func (s *Service) NsqMessageHandler(msg *nsq.Message) error {
    var nsqMsg cmd.NsqEventMsg
    if err := json.Unmarshal(msg.Body, &nsqMsg); err != nil {
        g.Log().Ctx(msg.Ctx).Error("msg", "UnmarshalFailed", "err", err)
        return nil // 丢弃坏消息，避免重试循环
    }
    
    g.Log().Ctx(msg.Ctx).Info("msg", "SigninEvent", "cmd", nsqMsg.Cmd)
    
    // 二次路由：根据 cmd 分发到具体 handler
    switch nsqMsg.Cmd {
    case "daily_signin":
        return s.handleDailySignin(msg.Ctx, &nsqMsg)
    case "continuous_signin":
        return s.handleContinuousSignin(msg.Ctx, &nsqMsg)
    case "signin_reward":
        return s.handleSigninReward(msg.Ctx, &nsqMsg)
    default:
        g.Log().Ctx(msg.Ctx).Warning("msg", "UnknownCmd", "cmd", nsqMsg.Cmd)
        return nil
    }
}

// handleDailySignin 签到事件处理
func (s *Service) handleDailySignin(ctx context.Context, data *cmd.NsqEventMsg) error {
    var req struct {
        Uid      uint32 `json:"uid"`
        ClientIp string `json:"client_ip"`
    }
    if err := json.Unmarshal(data.Data, &req); err != nil {
        g.Log().Ctx(ctx).Error("msg", "UnmarshalFailed", "err", err)
        return nil
    }
    
    // 调用 Service 层执行业务逻辑
    return signin.DailySignin(ctx, req.Uid, req.ClientIp)
}

// handleContinuousSignin 连续签到事件处理
func (s *Service) handleContinuousSignin(ctx context.Context, data *cmd.NsqEventMsg) error {
    var req struct {
        Uid uint32 `json:"uid"`
    }
    if err := json.Unmarshal(data.Data, &req); err != nil {
        g.Log().Ctx(ctx).Error("msg", "UnmarshalFailed", "err", err)
        return nil
    }
    
    return signin.CheckContinuousSignin(ctx, req.Uid)
}

// handleSigninReward 签到奖励事件处理
func (s *Service) handleSigninReward(ctx context.Context, data *cmd.NsqEventMsg) error {
    var req struct {
        Uid      uint32 `json:"uid"`
        ActivityId uint32 `json:"activity_id"`
    }
    if err := json.Unmarshal(data.Data, &req); err != nil {
        g.Log().Ctx(ctx).Error("msg", "UnmarshalFailed", "err", err)
        return nil
    }
    
    return signin.GrantSigninReward(ctx, req.Uid, req.ActivityId)
}
```

### A.3 二次路由场景判断

使用 HandleEventMap + switch-case 二次路由的条件：

```go
// ✅ 需要二次路由：同一个 Topic 包含多个不同业务事件
// 示例：signin.topic 包含 daily_signin, continuous_signin, signin_reward
switch nsqMsg.Cmd {
case "daily_signin":
    return s.handleDailySignin(ctx, nsqMsg)
case "continuous_signin":
    return s.handleContinuousSignin(ctx, nsqMsg)
}

// ❌ 不需要二次路由：一个 Topic 只对应一种事件
// 示例：diamond.topic 只处理 consume_diamond
return s.handleConsumeDiamond(ctx, nsqMsg)
```

### A.4 约束条件（必须遵守）

1. **init() 注册**：所有观察者必须在 init() 中注册，确保早于事件发布
2. **常量集中定义**：Topic 常量统一在 `app/consts/` 或各模块 `constants.go`
3. **gutil.Try 包裹**：所有异步回调必须用 gutil.Try 包裹，防止 panic 导致进程崩溃
4. **NSQ 消费者启动**：在 `cmd/main.go` 中调用 `NewService().Run()`

---

## 附录 B：观察者模式完整示例

### B.1 DiamondObserver 完整实现

```go
// app/service/diamond/observer.go
package diamond

import (
    "context"
    "slp-go/app/dao"
    "slp-go/app/model"
    "github.com/gogf/gf/v2/frame/g"
)

// DiamondObserver 钻石消耗观察者（单例）
type DiamondObserver struct{}

var diamondObserverInstance *DiamondObserver

func init() {
    diamondObserverInstance = &DiamondObserver{}
    // 注册到事件总线
    eventbus.RegisterObserver("diamond.consume", diamondObserverInstance)
}

// OnEvent 实现 Observer 接口
func (o *DiamondObserver) OnEvent(ctx context.Context, event *Event) error {
    return gutil.Try(ctx, func(ctx context.Context) error {
        var req ConsumeDiamondReq
        if err := json.Unmarshal(event.Data, &req); err != nil {
            g.Log().Ctx(ctx).Error("msg", "UnmarshalFailed", "err", err)
            return nil
        }
        
        // 1. 记录钻石流水
        err := dao.XsDiamondLog.Insert(ctx, &model.XsDiamondLog{
            Uid:      req.Uid,
            Amount:   req.Amount,
            Type:     req.Type,
            Dateline: uint32(time.Now().Unix()),
        })
        if err != nil {
            g.Log().Ctx(ctx).Error("msg", "InsertLogFailed", "err", err)
            return err
        }
        
        // 2. 更新用户钻石余额
        _, err = dao.User.DecDiamond(ctx, req.Uid, req.Amount)
        if err != nil {
            g.Log().Ctx(ctx).Error("msg", "DecDiamondFailed", "err", err)
            return err
        }
        
        // 3. 异步记录行为日志（不阻塞主流程）
        go func() {
            defer gutil.TryRecover(ctx)
            recordBehaviorLog(ctx, req.Uid, req.Type)
        }()
        
        return nil
    }, func(ctx context.Context, rec *gutil.Recovery) error {
        g.Log().Ctx(ctx).Error("msg", "ObserverPanic", "rec", rec)
        return rec.Error
    })
}

// recordBehaviorLog 异步记录行为日志
func recordBehaviorLog(ctx context.Context, uid uint32, diamondType string) {
    // 实现细节...
}
```

### B.2 观察者模式 6 大约束（必须遵守）

1. **无状态设计**：观察者不能保存状态，所有数据通过事件传递
2. **init() 注册**：所有观察者必须在 init() 中完成注册
3. **gutil.Try 包裹**：所有回调函数必须用 gutil.Try 包裹
4. **异步日志**：非关键日志使用 goroutine 异步记录
5. **错误处理**：返回 error 给事件总线，由总线决定是否重试
6. **禁止直接调用**：观察者之间通过事件解耦，不能直接调用

### B.3 命名规范

```go
// ✅ 推荐：清晰的职责命名
type DiamondObserver struct{}      // 观察者类
type SigninService struct{}        // Service 类
type OrderObserver struct{}        // 订单观察者

// ❌ 避免：模糊的命名
type Observer struct{}             // 职责不明确
type Handler struct{}              // 是 Observer 还是 Service?
```

### B.4 调试技巧

**问题 1：观察者未触发**
```bash
# 检查 Topic 配置
cat config/slp-nsq-dev.json | grep diamond

# 检查消费者启动日志
tail -f logs/cmd.log | grep "DiamondObserver"
```

**问题 2：事件处理顺序**
```go
// 添加日志追踪
g.Log().Ctx(ctx).Info("msg", "OnEventStart", "uid", req.Uid)
defer g.Log().Ctx(ctx).Info("msg", "OnEventEnd", "uid", req.Uid)
```

---

## 附录 C：事件处理模式对比表

| 维度 | 观察者模式 | HandleEventMap 模式 | switch-case 模式 |
|------|-----------|-------------------|-----------------|
| **适用场景** | 一个事件多个响应者 | 一个事件一个响应者（复杂逻辑） | 一个事件一个响应者（简单逻辑） |
| **代码量** | 中（接口 + 注册） | 少（map 自动路由） | 少（switch-case） |
| **扩展性** | 高（新增观察者无需修改现有代码） | 中（需修改 map） | 低（需修改 switch） |
| **典型使用** | 钻石消耗、礼物发送 | 签到、任务完成 | 简单状态变更 |

---

**版本**: 2.0 | **最后更新**: 2026-04-11
