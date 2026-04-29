---
id: slp-common-rpc-core-learning
label: slp-common-rpc 核心学习
source: curated/projects/slp-common-rpc/CORE_LEARNING.md
project: slp-common-rpc
compiled: 2026-04-25
links: []
---

# slp-common-rpc 核心学习

## 项目定位

| 职责 | 说明 |
|------|------|
| 统一消费入口 | 所有消费请求通过 `ConsumeStage1` 统一处理 |
| 事务保障 | 二段事务确保扣钱与业务处理一致性 |
| 场景封装 | 59 种消费类型（`P_Type_*`）的场景化封装 |
| 异步解耦 | 通过 Kafka/NSQ 解耦后置处理逻辑 |

## 三阶段消费模型

| 阶段 | 职责 | 锁 |
|------|------|-----|
| Stage0: 预处理 | 参数校验、权限检查、库存预占 | `xs_consume_stage1_{requestId}` |
| Stage1: 核心处理 | 扣减余额、写子事务表、写流水表、发 Kafka | 同上 |
| Stage2: 后置处理 | 消费 Kafka、调用场景处理器、执行业务逻辑 | `xs_consume_stage2_{requestId}` |

## 二段事务

| 一段事务 | 二段事务 |
|----------|----------|
| 扣钱 + 写子事务 | 业务处理 |
| 同步、原子性 | 异步、幂等性 |
| 单事务完成 | Kafka 触发 |

## 59 种消费类型

| 分类 | Type | 场景 |
|------|------|------|
| 基础消费 | `money_add/reduce` | 充值、扣钻 |
| 礼物打赏 | `chat_gift_inc`, `group_chat_gift_inc` | 聊天室/群聊礼物 |
| 房间套餐 | `room_package_inc` | 开通房间守护 |
| 商品购买 | `commodity_add` | 购买虚拟商品 |
| 抽奖 | `open_box_upd` | 开启宝箱 |

## Stage2 后置处理

| 操作类型 | 数量 | 说明 |
|----------|------|------|
| RPC 调用 | 4+ | UserProfile、CommonCache、UserGrowth 等 |
| NSQ 消息 | 11+ | xs.push、xs.mission、xs.cmd 等 |
| DB 表 | 10+ | xs_user_experience、xs_achievement 等 |

## RPC 客户端

| 服务 | 客户端 | 常用方法 |
|------|--------|----------|
| User.Profile | `client.UserProfile` | Get、Mget、MgetMap |
| Common.Cache | `client.CommonCache` | MgetGifts、GetGiftEntity |
| User.Growth | `client.UserGrowth` | GetNobilityLevel、GetMentorShip |
| Room.Info | `client.RoomInfo` | GetRoomInfo、Mget |

## NSQ 消息 Topic

| Topic | 用途 |
|-------|------|
| `xs.push` | APP 推送 |
| `xs.mission` | 任务触发 |
| `xs.cmd` | 前端命令 |
| `slp.delay.message.collector` | 延迟消息 |

## 关键数据表

| 表名 | 用途 |
|------|------|
| `xs_sub_transaction` | 子事务表 |
| `xs_user_money` | 用户余额表 |
| `xs_pay_change` | 流水表 |

## 分布式锁

| 阶段 | 锁 Key | 说明 |
|------|--------|------|
| Stage1 | `xs_consume_stage1_{requestId}` | 防止重复提交 |
| Stage2 | `xs_consume_stage2_{requestId}` | 保证幂等性 |

## 学习检查清单

- 理解三阶段模型各阶段的职责
- 理解二段事务的设计动机
- 能画出 Stage1 → Kafka → Stage2 的流程图
- 了解 59 种消费类型的分类
- 理解 RPC 客户端的单例模式
- 了解 NSQ 消息的几种 Topic
- 理解分布式锁的使用场景
- 了解核心数据表结构 |

## 相关知识

- [[patterns/project-learning-framework]]
- [[projects/slp-go/01-structure]]
