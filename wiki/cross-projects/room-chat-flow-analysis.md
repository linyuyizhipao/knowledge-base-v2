---
id: room-chat-flow-analysis
label: 公屏消息流转深度分析
source: curated/cross-projects/chatroom/room-chat-flow-analysis.md
business: chatroom
compiled: 2026-04-25
links: []
---

# 公屏消息流转深度分析

> 公屏消息发送流转链路分析

## 消息流转流程

| 层级 | 函数 | 文件 | 说明 |
|------|------|------|------|
| 1 | ClientSendMessage | ClientHandle.go:385 | 消息入口，从 Redis 获取 uid/rid |
| 2 | RoomMessageHandler | room_message.go:92 | 解析 extra、表情处理、内容校验 |
| 3 | WorkManager.RevMsg | work_pool.go:54 | 通过 id % workCount 选择任务线程 |
| 4 | TaskLimiter.AddTask | work.go:71 | 阻塞发送到 infoChan (cap=1000) |
| 5 | TaskLimiter.run | work.go:86 | 异步处理循环 |
| 6 | allowMsg | work.go:143 | Redis 限流查询 |
| 7 | WrapSendMessage | room_message.go:208 | 限流检查 + 用户信息查询 + sendToGate |
| 8 | GateClientImp.SendMessageToGroup | - | RPC 调用 room_gate |

## 性能瓶颈

| 问题 | 位置 | 影响 |
|------|------|------|
| 单线程 RevMsg 可能阻塞 | work_pool.go:54 | 部分线程过载 |
| Goroutine 无限增长风险 | work.go:105-110 | 资源耗尽 |
| 每条消息 4-5 次 MySQL 查询 | WrapSendMessage | 高延迟 |
| 每条消息 1 次 Redis 限流查询 | allowMsg | Redis QPS 高 |
| 200 个 TaskLimiter 内存开销 | DefWorkCnt=200 | 内存占用大 |

## 限流规则

| 条件 | 是否限流 |
|------|----------|
| 超管 | 不限流 |
| VIP 等级 >= cfg.MinUlimitVipLevel | 不限流 |
| EmotePosition > 0 | 不限流 |
| 其他 | Redis 令牌桶限流 |

## 消息丢失场景

| 场景 | 原因 |
|------|------|
| TaskLimiter.infoChan 溢出 | cap=1000，消费者慢时阻塞 |
| 限流器拒绝 | 静默丢弃，gLImitMsgCnt++ |
| 用户被封禁 | Deleted > 1 |
| 表情白名单过滤 | 非法表情丢弃 |
| Content 过长 | len(content) >= MaxDanmuSize |

## 关键缺失

- 无可见敏感词过滤实现
- 无消息追踪 ID
- 无限流丢弃日志