---
id: patterns/cmd-module-standard
label: cmd-module-standard
source: /Users/hugh/project/my-wiki/curated/patterns/cmd-module-standard.md
role: 规范
compiled: 2026-04-28
source_hash: 4153ff12fc7004eb479dc148a5eff9b7
---

> SLP Go 项目新增 cmd 模块的统一规范（参照 room_recommend_more 模式）

## 为什么需要标准结构

**问题**：各业务模块随意组织代码，导致：
- 新人上手成本高（每个模块结构都不一样）
- 代码难以复用
- 事件处理逻辑分散，不好排查

**解决**：统一采用 **room_recommend_more** 模式，所有 cmd 模块结构一致。

---

## 标准目录结构

```
cmd/internal/<module_name>/
├── service.go          # NSQ 消费者启动 + Cron 任务注册
├── consumer.go         # NSQ 消息消费入口（可选，简单场景可合入 service.go）
├── handler/            # 业务处理器（按功能细分）
│   ├── base.go         # HandleEventMap 定义 + 公共方法
│   ├── event_enter.go  # 进房事件处理
│   ├── event_leave.go  # 离房事件处理
│   └── event_send.go   # 发送事件处理
└── consts/             # 模块常量定义（可选，建议放到全局 consts）
    └── events.go       # 事件常量
```

---

## 核心组件

### 1. 事件常量定义

**位置**：项目全局 `consts/` 目录

```go
package consts

type ModuleEvent string

func (s ModuleEvent) ToString() string {
    return string(s)
}

const (
    ModuleEnterEvent ModuleEvent = "module_enter"
    ModuleLeaveEvent ModuleEvent = "module_leave"
    ModuleTopicName  = "xs.module.event"
)
```

### 2. HandleEventMap 路由

👉 **完整规范**: [[event-extension-guide]] 附录 A - 包含详细模板和约束

**核心代码**：
```go
// cmd/internal/<module>/handler/base.go
type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var HandleEventMap = map[consts.ModuleEvent]HandleEvent{}
```

**注册方式**：
```go
// cmd/internal/<module>/handler/event_enter.go
func init() {
    HandleEventMap[consts.ModuleEnterEvent] = &moduleEnterEvent{}
}
```

### 3. NSQ 消费者

**标准结构**：
```go
// cmd/internal/<module>/service.go
type Service struct {
    cmd.StartUp
}

func (s *Service) consume() error {
    return library.NewNsqWorker(
        consts.ModuleTopicName,
        library.NsqGroupDefault,
        s.NsqMessageHandler,
    ).ConnectWithConcurrency(100)
}
```

### 4. Cron 任务（可选）

```go
func (s *Service) Cron() error {
    _, _ = scron.Add("0 0 * * *", s.dailyTask, "module.dailyTask")
    _, _ = scron.Add("0 * * * *", s.hourlyTask, "module.hourlyTask")
    scron.Start()
    return nil
}
```

---

## 完整示例：用户签到模块

### 目录结构

```
cmd/internal/signin/
├── service.go
└── handler/
    ├── base.go
    ├── event_enter.go
    └── event_complete.go
```

### consts/signin.go

```go
package consts

type SigninEvent string

func (s SigninEvent) ToString() string {
    return string(s)
}

const (
    SigninEnterEvent    SigninEvent = "signin_enter"
    SigninCompleteEvent SigninEvent = "signin_complete"
    SigninTopicName     = "xs.user.signin"
)
```

### handler/base.go

```go
package handler

import (
    "context"
    "slp/consts"
    "slp/library/cmd"
)

type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var HandleEventMap = map[consts.SigninEvent]HandleEvent{}
```

### handler/event_enter.go

```go
package handler

import (
    "context"
    "github.com/gogf/gf/frame/g"
    "github.com/gogf/gf/util/gconv"
    "slp/consts"
    "slp/library/cmd"
)

func init() {
    HandleEventMap[consts.SigninEnterEvent] = &signinEnterEvent{}
}

type signinEnterEvent struct{}

func (s *signinEnterEvent) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    uid := gconv.Uint32(data.Data["uid"])
    
    g.Log().Ctx(ctx).Info("msg", "SigninEnterEvent", "uid", uid)
    
    // 签到逻辑
    return nil
}
```

### service.go

```go
package signin

import (
    "context"
    "github.com/gogf/gf/errors/gerror"
    "github.com/gogf/gf/frame/g"
    "github.com/gogf/gf/util/gutil"
    "github.com/nsqio/go-nsq"
    "slp/consts"
    "slp/library"
    "slp/library/cmd"
    "slp/cmd/internal/signin/handler"
)

type Service struct {
    cmd.StartUp
}

func NewCmdService() *Service {
    s := &Service{}
    _ = s.Init()
    return s
}

func (s *Service) Run() {
    if err := s.Init(); err != nil {
        g.Log().Errorf("Service Init failed err=%v", err)
        return
    }

    if err := s.consume(); err != nil {
        g.Log().Errorf("Service consume failed err=%v", err)
        panic(err)
    }
    
    if err := s.Start(); err != nil {
        g.Log().Errorf("Service Start failed err=%v", err)
        panic(err)
    }
}

func (s *Service) consume() error {
    return library.NewNsqWorker(
        consts.SigninTopicName,
        library.NsqGroupDefault,
        s.NsqMessageHandler,
    ).ConnectWithConcurrency(50)
}

func (s *Service) NsqMessageHandler(message *nsq.Message) (err error) {
    ctx := context.Background()
    nsqMsg, _ := cmd.ParseNsqMsg(message)
    
    if nsqMsg == nil {
        return gerror.New("错误的解析")
    }
    
    topicCmd := consts.SigninEvent(nsqMsg.Cmd)
    handle, ok := handler.HandleEventMap[topicCmd]
    if !ok {
        return gerror.Newf("cmd=%s 协议暂不支持", nsqMsg.Cmd)
    }
    
    if err = gutil.Try(func() {
        if err = handle.Handle(ctx, nsqMsg); err != nil {
            return
        }
    }); err != nil {
        g.Log().Ctx(ctx).Error("msg", "NsqMessageHandler", "err", err)
        return err
    }
    
    return nil
}
```

---

## Checklist：新增 cmd 模块

- [ ] 在 `cmd/internal/` 下创建模块目录
- [ ] 定义事件常量（`consts/` 目录）
- [ ] 创建 `handler/base.go` 定义 HandleEventMap
- [ ] 创建事件处理器（`handler/event_xxx.go`），在 `init()` 中注册
- [ ] 创建 `service.go` 启动 NSQ 消费者
- [ ] 实现 `NsqMessageHandler` 统一分发逻辑
- [ ] 如有定时任务，在 `Cron()` 中注册
- [ ] 在 `main.go` 或项目入口注册新服务

---

## 参考实现

| 模块 | 位置 | 说明 |
|------|------|------|
| room_recommend_more | `slp-room/cmd/internal/` | 原始参考实现 |
| room_event | `slp-go/cmd/internal/` | 简单 switch-case 模式 |
| relation | `slp-go/cmd/internal/` | HandleEventMap 路由模式 |

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [[event-extension-guide]] | 事件拓展总纲（含完整示例） |
| [[nsq-usage]] | NSQ 使用规范 |

---

**版本**: 1.0 | **最后更新**: 2026-04-11
