# slp-common-rpc 核心学习

> 三阶段消费模型与二段事务架构

**最后更新**: 2026-04-06  
**版本**: v1.0 (精简版)

---

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

// Stage2: 二段事务（业务处理）
func ConsumeStage2(msg *sarama.ConsumerMessage) error {
    // 1. 获取子事务
    st := dao.XsSubTransaction.Get(msg.RequestId)
    
    // 2. 根据类型调用场景处理器
    switch st.Type {
    case chat_gift_inc:
        ChatGiftScene.Stage2HandlerAfter()
    case room_package_inc:
        RoomPackageScene.Stage2HandlerAfter()
    }
    
    // 3. 标记完成
    dao.XsSubTransaction.UpdateStatus(msg.RequestId, STATUS_DONE)
}
```

### 为什么需要二段事务

| 问题 | 一段事务方案 | 二段事务方案 |
|------|-------------|-------------|
| 事务时间长 | 扣钱 + 所有业务逻辑在一个事务，锁表时间长 | 仅扣钱在事务，业务逻辑异步 |
| 耦合严重 | 新增业务需要修改扣钱逻辑 | 新增业务只需监听 Kafka |
| 失败影响 | 业务逻辑失败导致扣钱回滚 | 业务逻辑失败可重试，不影响扣钱 |
| 扩展性差 | 每次新增业务都要改核心代码 | 新增消费者即可 |

---

## 四、59 种消费类型

消费类型定义在 `consume_param.pb.go`：

```go
type SubTxnType int32

const (
    SubTxnType_money_add              SubTxnType = 1   // 充值
    SubTxnType_money_reduce           SubTxnType = 2   // 扣减
    SubTxnType_commodity_add          SubTxnType = 3   // 商品
    SubTxnType_room_package_inc       SubTxnType = 4   // 房间套餐
    SubTxnType_consume_msg            SubTxnType = 5   // 消费消息
    SubTxnType_open_box_upd           SubTxnType = 6   // 开箱
    SubTxnType_chat_package_inc       SubTxnType = 7   // 聊天室套餐
    SubTxnType_chat_gift_inc          SubTxnType = 8   // 聊天室礼物
    SubTxnType_group_chat_gift_inc    SubTxnType = 9   // 群聊礼物
    // ... 共 59 种
)
```

### 核心场景分类

| 分类 | Type | 场景 |
|------|------|------|
| 基础消费 | money_add/reduce | 充值、扣钻 |
| 礼物打赏 | chat_gift_inc、group_chat_gift_inc | 聊天室/群聊礼物 |
| 房间套餐 | room_package_inc | 开通房间守护 |
| 商品购买 | commodity_add | 购买虚拟商品 |
| 抽奖 | open_box_upd | 开启宝箱 |

---

## 五、Stage2 后置处理流程

### 核心代码结构

```
rpc/server/internal/consume/stage2/
├── consume_stage2.go          # Stage2 入口，Kafka 消费
├── handler_stage2.go          # 分发处理器
│   ├── handlerSub()           # 根据 Type 分发
│   ├── handlerAfter()         # 后置处理入口
│   └── GetHandleAfterInstance() # 获取场景处理器
├── chat_gift.go               # 聊天室礼物场景
│   └── ChatGiftScene.Stage2HandlerAfter()
├── room_package.go            # 房间套餐场景
└── group_chat_gift.go         # 群聊礼物场景
```

### handler_stage2.go 核心逻辑

```go
// 1. 根据 Type 分发到具体处理函数
func (c *ConsumeStage2) handlerSub(tx *sql.Tx, param *SubTxnParam) error {
    switch param.Type {
    case SubTxnType_chat_gift_inc:
        return chatGiftInc(tx, param)
    case SubTxnType_room_package_inc:
        return roomPackageInc(tx, param)
    }
}

// 2. 后置处理（Kafka 发送、NSQ 消息）
func (c *ConsumeStage2) handlerAfter(aftParam *AfterParam) {
    // 发送子事务 Kafka
    for _, st := range aftParam.Sts {
        go c.kfkSendSubTransaction(st)
    }
    
    // 发送 NSQ 惩罚/通知
    for _, uid := range aftParam.PunishUids {
        go c.nsqSendPunishExec(uid)
    }
    
    // 调用场景处理器
    instance := c.GetHandleAfterInstance(aftParam)
    if instance != nil {
        instance.Stage2HandlerAfter(aftParam)
    }
}
```

### ChatGiftScene 复杂度分析

`chat_gift.go` 是最复杂的场景处理器：

| 操作类型 | 数量 | 说明 |
|----------|------|------|
| RPC 调用 | 4+ | UserProfile、CommonCache、UserGrowth 等 |
| NSQ 消息 | 11+ | xs.push、xs.mission、xs.cmd 等 |
| DB 表 | 10+ | xs_user_experience、xs_achievement、xs_nobility_exp 等 |
| 业务逻辑 | 成就、任务、经验、贵族、师徒、舰队等 |

这正是需要配置化重构的原因——每次新增业务都要修改这个文件，违反开闭原则。

---

## 六、RPC 客户端模式

### 单例模式

```go
// rpc/client/user_client.go
var UserProfile *userProfile = &userProfile{
    &base{name: "User.Profile"},
}

type userProfile struct {
    *base
}

func (serv *userProfile) Mget(ctx context.Context, uids []uint32, fields []string) ([]*EntityXsUserProfile, error) {
    req := &pb.ReqUserProfiles{Uids: uids, Fields: fields}
    reply := &pb.RepUserProfiles{}
    err := serv.call(ctx, "Mget", req, reply)
    return reply.Data, err
}
```

### 调用方式

```go
// 1. 直接使用单例
userInfo, err := client.UserProfile.Mget(ctx, []uint32{uid}, fields)

// 2. 批量查询避免 N+1
userInfos, err := client.UserProfile.MgetMap(ctx, uids, fields)
```

### 支持的 RPC 服务

| 服务 | 客户端 | 常用方法 |
|------|--------|----------|
| User.Profile | `client.UserProfile` | Get、Mget、MgetMap |
| Common.Cache | `client.CommonCache` | MgetGifts、GetGiftEntity |
| User.Growth | `client.UserGrowth` | GetNobilityLevel、GetMentorShip |
| Room.Info | `client.RoomInfo` | GetRoomInfo、Mget |

---

## 七、NSQ 消息推送

### Topic 分类

| Topic | 用途 | 消息格式 |
|-------|------|----------|
| xs.push | APP 推送 | `{"cmd":"xxx","data":{}}` |
| xs.mission | 任务触发 | `{"uid":123,"mission_type":"xxx"}` |
| xs.cmd | 前端命令 | PHP 序列化数据 |
| slp.delay.message.collector | 延迟消息 | `{"topic":"xxx","delay_sec":60,"data":"{}"}` |

### 发送方式

```go
// 直接发送
c.nsqClient.SendBytes("xs.push", data)

// 延迟发送
c.nsqClient.SendBytes("slp.delay.message.collector", delayData)

// CMD 类型（PHP 序列化）
cmdData := php_serialize.Serialize(map[string]interface{}{
    "cmd": "achievement.update",
    "data": result,
})
c.nsqClient.SendBytes("xs.cmd", cmdData)
```

---

## 八、分布式锁

### Redis 锁

```go
// 位置：rpc/server/internal/consume/common/redis_lock.go
type RedisLock struct {
    redis *redis.Client
}

func (l *RedisLock) Lock(key string, expire int64) bool {
    success, _ := l.redis.SetNX(ctx, key, 1, time.Duration(expire)*time.Second).Result()
    return success
}

func (l *RedisLock) UnLock(key string) {
    l.redis.Del(ctx, key)
}
```

### 使用场景

| 阶段 | 锁 Key | 说明 |
|------|--------|------|
| Stage1 | `xs_consume_stage1_{requestId}` | 防止重复提交 |
| Stage2 | `xs_consume_stage2_{requestId}` | 保证幂等性 |

---

## 九、关键数据表

### xs_sub_transaction（子事务表）

```sql
CREATE TABLE `xs_sub_transaction` (
  `request_id` bigint(20) unsigned NOT NULL,
  `uid` int(10) unsigned NOT NULL,
  `type` tinyint(4) NOT NULL,
  `status` tinyint(4) DEFAULT 0,  -- 0:待处理 1:处理中 2:已完成
  `data` blob,
  `dateline` int(10) unsigned NOT NULL,
  PRIMARY KEY (`request_id`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### xs_user_money（用户余额表）

```sql
CREATE TABLE `xs_user_money` (
  `uid` int(10) unsigned NOT NULL,
  `money` int(10) unsigned NOT NULL DEFAULT 0,  -- 钻石
  `gold` int(10) unsigned NOT NULL DEFAULT 0,   -- 金币
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### xs_pay_change（流水表）

```sql
CREATE TABLE `xs_pay_change` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `request_id` bigint(20) unsigned NOT NULL,
  `uid` int(10) unsigned NOT NULL,
  `change_type` tinyint(4) NOT NULL,  -- 1:充值 2:消费
  `money` int(10) NOT NULL,           -- 正数增加，负数减少
  `balance` int(10) NOT NULL,         -- 变更后余额
  `reason` varchar(100) DEFAULT '',
  `dateline` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `idx_request_id` (`request_id`),
  KEY `idx_uid_dateline` (`uid`, `dateline`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

---

## 十、配置化扩展方案（设计方向）

### 问题

当前 `ChatGiftScene.Stage2HandlerAfter()` 包含 1000+ 行代码，每次新增业务需要：
1. 修改 `handler_stage2.go` 添加新 case
2. 修改 `ChatGiftScene` 添加新逻辑
3. 违反开闭原则

### 设计方向

通过 Pipeline 引擎实现配置化扩展：

```yaml
business_extensions:
  - name: "打赏成就系统"
    trigger_type: "chat_gift"
    pipeline:
      - step: "check_money"
        type: "condition"
        condition: "${req.Money} >= 10000"
      - step: "insert_achievement"
        type: "db_insert"
        table: "xs_achievement"
        data:
          uid: "${req.Uid}"
          achieve_type: "chat_gift_10000"
```

**详细设计参考**：ARCHITECTURE.md（待创建）

---

## 学习检查清单

- [ ] 理解三阶段模型各阶段的职责
- [ ] 理解二段事务的设计动机
- [ ] 能画出 Stage1 → Kafka → Stage2 的流程图
- [ ] 了解 59 种消费类型的分类
- [ ] 理解 RPC 客户端的单例模式
- [ ] 了解 NSQ 消息的几种 Topic
- [ ] 理解分布式锁的使用场景
- [ ] 了解核心数据表结构
- [ ] 理解当前代码结构的问题（开闭原则）

---

## 相关文档

- [PROJECT_CONTEXT.md](./PROJECT_CONTEXT.md) - 项目背景
- [ARCHITECTURE.md](./ARCHITECTURE.md) - 架构设计
- [CODING_STANDARDS.md](./CODING_STANDARDS.md) - 开发规范
