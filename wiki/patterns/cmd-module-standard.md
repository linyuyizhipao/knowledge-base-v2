---
id: patterns/cmd-module-standard
label: cmd-module-standard
source: /Users/hugh/project/my-wiki/curated/patterns/cmd-module-standard.md
role: 规范
compiled: 2026-04-28
source_hash: 4153ff12fc7004eb479dc148a5eff9b7
---

> SLP Go 项目新增 cmd 模块的统一规范

## 标准目录结构

```
cmd/internal/<module_name>/
├── service.go          # NSQ 消费者启动 + Cron 任务注册
├── consumer.go         # NSQ 消息消费入口（可选）
├── handler/            # 业务处理器
│   ├── base.go         # HandleEventMap + 公共方法
│   └── event_xxx.go    # 各事件处理器
└── consts/             # 模块常量（建议放到全局 consts）
```

## 核心组件

### 1. 事件常量（全局 consts/）

```go
type ModuleEvent string
func (s ModuleEvent) ToString() string { return string(s) }
const ( ModuleEnterEvent ModuleEvent = "module_enter"; ModuleTopicName = "xs.module.event" )
```

### 2. HandleEventMap 路由

```go
type HandleEvent interface { Handle(ctx context.Context, data *cmd.NsqEventMsg) error }
var HandleEventMap = map[consts.ModuleEvent]HandleEvent{}

// 注册：在 handler/event_enter.go 的 init() 中
func init() { HandleEventMap[consts.ModuleEnterEvent] = &moduleEnterEvent{} }
```

### 3. NSQ 消费者

```go
func (s *Service) consume() error {
    return library.NewNsqWorker(consts.ModuleTopicName, library.NsqGroupDefault, s.NsqMessageHandler).ConnectWithConcurrency(100)
}
```

## Checklist

- [ ] 在 `cmd/internal/` 下创建模块目录
- [ ] 定义事件常量（`consts/` 目录）
- [ ] 创建 `handler/base.go` 定义 HandleEventMap
- [ ] 创建事件处理器，在 `init()` 中注册
- [ ] 创建 `service.go` 启动 NSQ 消费者
- [ ] 实现 `NsqMessageHandler` 统一分发
- [ ] 在 `main.go` 注册新服务
