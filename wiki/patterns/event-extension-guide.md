---
id: patterns/event-extension-guide
label: 事件能力拓展指南
type: guide
source: curated/patterns/event-extension-guide.md
sources: [curated/patterns/event-extension-guide.md]
role: 规范
compiled: 2026-04-29
source_hash: a479d76457fa95f5ddd66ab7b36bc5e2
tags: [事件, 观察者, NSQ, HandleEventMap, 异步]
links_to:
  - patterns/nsq-usage
  - patterns/cmd-module-standard
  - CODING_STANDARDS
  - projects/slp-go/09-event-capabilities
---

# 事件能力拓展指南

> SLP 项目统一的事件拓展规范

## 核心理念

**一个事件，多个响应；业务解耦，自由拓展**

## 三种模式速查

| 模式 | 适用场景 | 拓展方式 | 典型使用 |
|------|---------|---------|---------|
| 观察者模式 | 一事件多响应（充值、钻石消耗） | 新增 Observer | 充值→多个业务 |
| HandleEventMap | 一事件一处理（关系事件、心情值） | 新增 Handler | 签到、任务 |
| switch-case | 简单固定（房间事件） | 新增 case | 状态变更 |

## 判断流程

```
新增事件能力
    ↓
┌─ 一事件多响应？ ── YES → 观察者模式
│
├─ 一事件一处理？ ── YES → HandleEventMap
│
└─ 简单固定？    ── YES → switch-case
```

## 观察者模式核心代码

```go
// 定义接口
type DiamondObserver interface {
    DiamondEvent(ctx, param) error
}
var diamondObservers []DiamondObserver

// 注册（init 中）
func init() {
    diamondObservers = append(diamondObservers, &RechargeObserver{})
}

// 触发
func DiamondEvent(ctx, param) {
    for _, o := range diamondObservers {
        _ = gutil.Try(func() { o.DiamondEvent(ctx, param) })
    }
}
```

## HandleEventMap 核心代码

```go
// 定义路由
var HandleEventMap = map[consts.ModuleEvent]HandleEvent{}

// 注册
func init() {
    HandleEventMap[consts.MyActionEvent] = &myActionEvent{}
}

// 处理
func (s *Service) NsqMessageHandler(msg) {
    handler := HandleEventMap[nsqMsg.Cmd]
    return handler.Handle(ctx, nsqMsg)
}
```

## NSQ 发送标准格式

```go
nsqData, _ := json.Marshal(&NsqEventData{
    Cmd:  "my.event.action",
    Data: eventData,
})
_ = library.NsqClient().SendBytes("xs.my.topic", nsqData, 2*time.Second)
```

## 新增事件 Checklist

- [ ] 明确模式类型
- [ ] 确定 Topic 名称
- [ ] 定义事件常量
- [ ] 创建处理器/观察者
- [ ] init() 注册
- [ ] 本地测试发送
- [ ] 验证处理日志

## 相关知识

- [[patterns/nsq-usage]] - NSQ使用规范
- [[patterns/cmd-module-standard]] - CMD模块标准
- [[CODING_STANDARDS]] - 核心禁令
- [[projects/slp-go/09-event-capabilities]] - 已支持事件列表