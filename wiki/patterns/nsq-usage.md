---
id: patterns/nsq-usage
label: nsq-usage
source: curated/patterns/nsq-usage.md
role: 规范
compiled: 2026-04-28
source_hash: fe56ae6ea0c341ae3d405e83ff77713c
---

> SLP 项目统一的 NSQ 事件发送与消费标准

## 发送格式

### JSON 格式（推荐，新项目默认）

```go
type NsqEventData struct { Cmd string `json:"cmd"`; Data any `json:"data"` }

nsqData, _ := json.Marshal(&NsqEventData{ Cmd: "room_gift_send", Data: data })
_ = library.NsqClient().SendBytes("xs.room.event", nsqData, 2*time.Second)
```

### PHP 序列化格式（仅兼容老代码）

```go
dataBytes, _ := php_serialize.Serialize(data)
_ = library.NsqClient().SendBytes("xs.mission", dataBytes)
```

## 常用 Topic

| Topic | 用途 | 典型事件 |
|-------|------|---------|
| `xs.common.room.event` | 房间事件 | enter_room, leave_room |
| `xs.full.screen` | 全站飘屏 | cmd.online.room |
| `xs.mission` | 任务中心 | room_stay_times, send_gift |
| `xs.mysql_to_es` | MySQL → ES 同步 | update_room_hot |
| `slp.user.mood` | 心情值系统 | chat, marry, game |

## 消费模式

| 模式 | 适用场景 |
|------|---------|
| switch-case | 简单事件处理 |
| HandleEventMap 路由 | 需动态扩展的复杂业务 |
| 观察者模式 | 一个事件触发多个业务响应 |

### switch-case 模式

```go
switch nsqMsg.Cmd {
case "room.enter.pretty": return s.handleRoomEnter(nsqMsg, true)
case "room.leave": return s.handleRoomLeave(nsqMsg)
default: return gerror.Newf("cmd=%s 不支持", nsqMsg.Cmd)
}
```

### 消费者启动

```go
library.NewNsqWorker("xs.common.room.event", "common", s.Consumer).ConnectWithConcurrency(100)
```

## 最佳实践

| 实践 | 做法 |
|------|------|
| 错误处理 | `SendBytes` 带超时 `2*time.Second` |
| 幂等性 | Redis SetNX 去重 |
| 事务性 | 先落库，事务 OnCommit 后再发事件 |
| 事件常量 | 集中定义在 `consts/events.go` |

## 本地调试

```bash
curl -X POST http://localhost:4151/pub?topic=xs.common.room.event \
  -d '{"cmd":"room.enter","data":{"uid":123,"rid":456}}'
```
