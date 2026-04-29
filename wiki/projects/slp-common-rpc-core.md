---
id: slp-common-rpc-core
label: slp-common-rpc 核心学习
source: curated/projects/slp-common-rpc/CORE_LEARNING.md
project: slp-common-rpc
role: core-learning
compiled: 2026-04-25
tags:
  - consume
  - two-phase-transaction
  - kafka
links:
  - slp-go-infra
---

# slp-common-rpc 核心学习

> 三阶段消费模型与二段事务架构

## 一、项目定位

slp-common-rpc 是一个**支付消费中台**，处理所有与虚拟货币（钻、金币）相关的消费场景。

### 核心职责

| 职责 | 说明 |
|------|------|
| 统一消费入口 | 所有消费请求通过 `ConsumeStage1` 统一处理 |
| 事务保障 | 二段事务确保扣钱与业务处理一致性 |
| 场景封装 | 59 种消费类型（`P_Type_*`）的场景化封装 |
| 异步解耦 | 通过 Kafka/NSQ 解耦后置处理逻辑 |

---

## 二、三阶段消费模型

```
┌─────────────────────────────────────────────────────────────┐
│                      消费请求入口                            │
│                   ConsumeStage1.Stage1()                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage0: 预处理                                              │
│  - 参数校验、权限检查、库存预占                              │
│  - 分布式锁：xs_consume_stage1_{requestId}                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage1: 核心处理（同步）                                    │
│  - 扣减用户余额（xs_user_money）                             │
│  - 写子事务表（xs_sub_transaction）                          │
│  - 写流水表（xs_pay_change）                                 │
│  - Kafka 消息：sub_transaction_send（触发 Stage2）          │
└─────────────────────────────────────────────────────────────┘
                              │
                    Kafka 消息触发
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  Stage2: 后置处理（异步）                                    │
│  - 消费 Kafka 消息：sub_transaction_send                     │
│  - 根据 Type 调用场景处理器（chat_gift、room_package 等）    │
│  - 执行 N+ 业务逻辑：RPC 调用、NSQ 消息、DB 操作              │
│  - 分布式锁：xs_consume_stage2_{requestId}                  │
└─────────────────────────────────────────────────────────────┘
```

### 关键设计点

1. **Stage1 原子性**：单事务完成扣钱 + 写子事务，要么全成功要么全失败
2. **Stage2 幂等性**：通过 `request_id` 唯一索引保证重复消费不产生副作用
3. **异步解耦**：Stage2 通过 Kafka 触发，支持削峰填谷
4. **重试机制**：Stage2 失败后通过 `xs_consume_todo` 表延迟重试

---

## 三、二段事务（Two-Phase Transaction）

### 什么是二段事务

一段事务扣钱，二段事务做业务处理。通过 Kafka 消息连接两个阶段。

```go
// Stage1: 一段事务（扣钱 + 写子事务）
func Stage1(param *SubTxnParam) (*Stage1Result, error) {
    // 1. 开启事务
    tx := db.Begin()
    
    // 2. 扣减余额
    dao.XsUserMoney.Where("uid=?", uid).Update("money", money-param.Money)
    
    // 3. 写子事务表
    dao.XsSubTransaction.Insert(SubTransaction{
        RequestId: param.RequestId,
        Type:      param.Type,
        Data:      param,
    })
    
    // 4. 写流水表
    dao.XsPayChange.Insert(payChange)
    
    // 5. 提交事务
    tx.Commit()
    
    // 6. 发送 Kafka 消息（触发 Stage2）
    kafka.Send("sub_transaction_send", param.RequestId)
}
```

### Stage2 处理

```go
// Stage2: 后置处理（异步）
func Stage2(requestId string) error {
    // 1. 获取子事务
    subTxn := dao.XsSubTransaction.Get(requestId)
    
    // 2. 根据 Type 调用场景处理器
    handler := GetHandler(subTxn.Type)
    return handler.Handle(subTxn)
}
```