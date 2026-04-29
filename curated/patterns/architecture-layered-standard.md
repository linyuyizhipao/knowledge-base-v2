# 分层架构共识

> 明确 HTTP、RPC、CMD、Service、Domain(Data 层) 的职责边界与调用规则

**版本**: 2.1 | **最后更新**: 2026-04-09

---

## 🎯 核心问题

当前项目存在的架构一致性问题：

1. **RPC 层可以直接调 DAO** - 业务逻辑分散在 RPC Handler 中
2. **CMD 层可以直接调 DAO** - 数据访问逻辑不统一
3. **依赖方向混乱** - 没有明确的分层边界

---

## 📐 目标架构

### 分层调用规则（严格）

```
┌─────────────────────────────────────────────────────────────┐
│              HTTP / RPC / CMD                                │
│                   （接入层）                                 │
│  • HTTP: app/api/ - 处理 HTTP 请求                              │
│  • RPC:  rpc/server/internal/ - 处理 RPC 调用                   │
│  • CMD:  cmd/internal/ - 处理 NSQ 消费者/定时任务                │
└────────────────────────┬────────────────────────────────────┘
                         │ 只能调用
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   app/service/                               │
│                  （业务逻辑层）                               │
│  • 封装完整的业务逻辑                                         │
│  • 封装事务操作                                               │
│  • 调用 domain 层获取数据                                       │
│  • 发送领域事件（NSQ/Kafka）                                  │
└────────────────────────┬────────────────────────────────────┘
                         │ 只能调用
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    app/domain/                               │
│             （数据访问层 + 事件发送）                          │
│  • 封装 DAO 操作（数据库 CRUD）                                  │
│  • 封装 RPC 调用（跨服务数据获取）                              │
│  • 数据组装（多个 DAO/RPC 组合成一个数据结构）                   │
│  • 发送 NSQ/Kafka 事件                                         │
│  • 不包含复杂业务逻辑，主要做数据获取和组装                       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                DAO / RPC Client                              │
│                 （底层依赖）                                 │
│  • app/dao/ - 数据库访问封装                                   │
│  • rpc/client/ - RPC 客户端封装                                │
└─────────────────────────────────────────────────────────────┘
```

### 各层职责定义

| 层级 | 职责 | 禁止事项 | 文件位置 |
|------|------|----------|----------|
| **HTTP/RPC/CMD** | 协议转换、参数校验、响应输出 | 不可直接调用 DAO/domain | `app/api/`, `rpc/server/internal/`, `cmd/internal/` |
| **Service** | 业务逻辑、事务、事件发送 | 不可直接调用 DAO，必须通过 domain 层 | `app/service/<business>/` |
| **Domain** | 数据访问、RPC 调用、数据组装、事件发送 | 不可包含复杂业务逻辑，不可被 RPC 直接调用 | `app/domain/<business>/` |
| **DAO/RPC Client** | 底层数据访问 | 不可包含任何逻辑 | `app/dao/`, `rpc/client/` |

---

## 💡 关于 Domain 层的说明

**命名历史原因**：虽然名字叫 `domain`，但实际职责是**数据访问层 + 事件发送**，不是 DDD 意义上的领域层。

**未来可能重构**：考虑到代码迁移成本，暂时保留 `app/domain/` 目录名，后续可逐步迁移到 `app/data/`。

**当前职责**：
1. 封装 DAO 操作（数据库 CRUD）
2. 封装 RPC 调用（跨服务数据获取）
3. 数据组装（组合多个 DAO/RPC 的数据）
4. 发送 NSQ/Kafka 事件

**不包含**：
- 复杂业务规则验证（这是 Service 层的职责）
- 事务操作（这是 Service 层的职责）

---

## ✅ 分层规则详解

### 规则 1：接入层（HTTP/RPC/CMD）只调用 Service

```go
// ✅ 正确：HTTP Handler 调用 Service
// app/api/user_pet_api.go
func (a *userPetApi) GetPet(r *ghttp.Request) {
    var req *query.ReqUserPetGet
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.UserPetInfo{Success: false, Message: err.Error()})
        return
    }
    
    // 调用 Service 层
    info, err := service_user_pet.GetPet(r.Context(), req.Uid)
    response.Output(r, info)
}

// ✅ 正确：RPC Handler 调用 Service
// rpc/server/internal/user_pet/user_pet.go
func (s *userPetHandler) GetPet(ctx context.Context, req *pb.GetUserPetReq, reply *pb.GetUserPetResp) error {
    info, err := service_user_pet.GetPet(ctx, req.Uid)
    if err != nil {
        reply.Success = false
        reply.Message = err.Error()
        return nil
    }
    reply.Success = true
    reply.PetInfo = info
    return nil
}

// ✅ 正确：CMD 消费者调用 Service
// cmd/internal/user_pet_decay/consumer.go
func (c *Consumer) Consume(ctx context.Context, msg *nsq.Message) error {
    var event DecayEvent
    json.Unmarshal(msg.Body, &event)
    
    // 调用 Service 层处理
    return service_user_pet.ProcessDecay(ctx, event.Uid, event.Hours)
}
```

```go
// ❌ 错误：接入层直接调用 DAO
// rpc/server/internal/relation/relation.go
func (r *relation) Follow(ctx context.Context, req, reply) error {
    // 错误：直接调用 DAO
    exist, err := dao.XsUserFriend.Ctx(ctx).One("uid = ? and `to` = ?", uid, to)
}

// ❌ 错误：接入层直接调用 data 层
// cmd/internal/xxx/consumer.go
func (c *Consumer) Consume(ctx context.Context, msg *nsq.Message) error {
    // 错误：绕过 Service 层
    pet := data_user_pet.GetPet(ctx, uid)
}
```

---

### 规则 2：Service 层封装业务逻辑

Service 层是业务逻辑的唯一承载者，负责：

1. **业务规则验证** - 检查业务条件是否满足
2. **事务操作** - 数据库事务封装
3. **调用 domain 层** - 获取/持久化数据
4. **发送领域事件** - NSQ/Kafka 消息发送

**Service 标准结构**：

```go
// app/service/user_pet/user_pet.go
package service_user_pet

import (
    "context"
    "slp/app/domain/user_pet"    // 调用 domain 层
    "slp/app/consts"
    "slp/app/domain"           // 事件发送
    "slp/app/model"
)

// GetPet 获取宠物信息
func GetPet(ctx context.Context, uid uint32) (*pb.UserPetInfo, error) {
    // 1. 调用 domain 层获取数据
    pet, err := domain_user_pet.GetPetByUid(ctx, uid)
    if err != nil {
        return nil, err
    }
    
    // 2. 业务规则验证（Service 层的职责）
    if pet.Status != consts.PetStatusActive {
        return nil, errors.New("宠物未激活")
    }
    
    // 3. 返回业务视图
    return &pb.UserPetInfo{
        Uid:      pet.Uid,
        PetType:  uint32(pet.PetType),
        Level:    uint32(pet.Level),
        Exp:      pet.Exp,
        Status:   uint32(pet.Status),
    }, nil
}

// ClaimPet 领取宠物（包含事务）
func ClaimPet(ctx context.Context, uid uint32, petType uint8) (*model.UserPet, error) {
    // 1. 分布式锁
    lockKey := consts.UserPetClaimLockKey.Key(uid)
    if !redis.SetNX(ctx, lockKey, 1, 5*time.Second) {
        return nil, errors.New("领取中，请稍后重试")
    }
    defer redis.Del(ctx, lockKey)
    
    var pet *model.UserPet
    
    // 2. 开启事务（Service 层的职责）
    err := db.Transaction(ctx, func(ctx context.Context, tx gdb.TX) error {
        // 3. 调用 data 层（带事务）
        existing, _ := data_user_pet.GetPetByUidTx(ctx, tx, uid)
        if existing != nil {
            return errors.New("宠物已领取")
        }
        
        // 4. 创建宠物记录
        pet = &model.UserPet{
            Uid:          uid,
            PetType:      petType,
            Level:        1,
            Exp:          0,
            Status:       consts.PetStatusActive,
            LastFeedTime: uint32(time.Now().Unix()),
        }
        
        // 5. 调用 data 层持久化（带事务）
        return data_user_pet.CreatePetTx(ctx, tx, pet)
    })
    
    if err != nil {
        return nil, err
    }
    
    // 6. 发送领域事件（Service 层的职责）
    domain.SendEvent(ctx, consts.PetTopic, "pet.claim", map[string]interface{}{
        "uid": uid,
        "pet_type": petType,
    })
    
    return pet, nil
}
```

---

### 规则 3：Domain 层封装数据访问

Domain 层是数据访问的统一入口，负责：

1. **封装 DAO 操作** - 把 `dao.Xxx.Ctx().Where()` 封装成语义化的方法
2. **封装 RPC 调用** - 把 `client.Xxx.Get()` 封装成统一的数据获取方法
3. **数据组装** - 组合多个 DAO/RPC 的数据成一个完整结构
4. **发送事件** - NSQ/Kafka 消息发送
5. **不包含复杂业务逻辑** - 只做数据获取、组装和事件发送，不做业务规则验证

**Domain 层标准结构**：

```go
// app/domain/user_pet/user_pet.go
package domain_user_pet

import (
    "context"
    "slp/app/dao"
    "slp/rpc/client"
    "slp/app/model"
    "slp/app/pb"
    "slp/app/domain"  // 基础 Domain 包（事件发送）
)

// UserPetData 宠物数据结构（组装后的完整数据）
type UserPetData struct {
    Pet       *model.UserPet
    User      *pb.EntityXsUserProfile  // 通过 RPC 获取
    OwnerInfo *UserInfo                // 组合数据
}

// GetPetByUid 根据 UID 获取宠物（封装 DAO）
func GetPetByUid(ctx context.Context, uid uint32) (*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).Where("uid", uid).One()
}

// GetPetByUidTx 根据 UID 获取宠物（带事务）
func GetPetByUidTx(ctx context.Context, tx gdb.TX, uid uint32) (*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).TX(tx).Where("uid", uid).One()
}

// CreatePetTx 创建宠物记录（带事务）
func CreatePetTx(ctx context.Context, tx gdb.TX, pet *model.UserPet) error {
    _, err := dao.UserPet.Ctx(ctx).TX(tx).Insert(pet)
    return err
}

// GetPetWithOwner 获取宠物及主人信息（数据组装）
func GetPetWithOwner(ctx context.Context, uid uint32) (*UserPetData, error) {
    // 1. 获取宠物（DAO）
    pet, err := dao.UserPet.Ctx(ctx).Where("uid", uid).One()
    if err != nil {
        return nil, err
    }
    
    // 2. 获取主人信息（RPC 调用）
    user, err := client.User.Profile.Get(ctx, &pb.ReqUserProfile{Uid: uid})
    if err != nil {
        return nil, err
    }
    
    // 3. 数据组装（Domain 层的职责）
    return &UserPetData{
        Pet:  pet,
        User: user,
        OwnerInfo: &UserInfo{
            Uid:  uid,
            Name: user.Nickname,
        },
    }, nil
}

// SendPetEvent 发送宠物事件（Domain 层也可以发送事件）
func SendPetEvent(ctx context.Context, uid uint32, event string, data map[string]interface{}) {
    domain.SendEvent(ctx, consts.PetTopic, event, data)
}
```

---

### 规则 4：Domain 层不能被 RPC 直接调用

**依赖方向**：

```
// ✅ 正确：单向依赖
rpc/server/internal/user_pet/  →  app/service/user_pet/  →  app/domain/user_pet/
                                                                    ↓
                                                              rpc/client/

// ❌ 错误：循环依赖
rpc/server/internal/user_pet/  →  app/domain/user_pet/
       ↑                                    ↓
       └────────────── rpc/client/ ←────────┘
```

**解释**：
- `app/domain/` 层调用 `rpc/client/` 是为了获取跨服务的数据
- 如果 `rpc/server/` 直接调用 `app/domain/`，而 `app/domain/` 又调用了 `rpc/client/`
- 当 RPC Handler 和 RPC Client 在同一个服务中时，可能形成循环依赖

**解决方案**：
- RPC Handler 必须通过 Service 层间接调用 Domain 层
- Service 层作为业务逻辑的隔离层，避免循环依赖

---

## 💡 Domain 层职责说明

**当前职责**（实际做法）：
1. 封装 DAO 操作（数据库 CRUD）
2. 封装 RPC 调用（跨服务数据获取）
3. 数据组装（组合多个 DAO/RPC 的数据）
4. 发送 NSQ/Kafka 事件

**不包含**：
- 复杂业务规则验证（这是 Service 层的职责）
- 事务操作（这是 Service 层的职责）

**命名说明**：
虽然名字叫 `domain`，但实际职责更接近**数据访问层 + 事件发送**。考虑到代码迁移成本，暂时保留 `app/domain/` 目录名。

---

## 📁 完整示例：宠物喂养功能

### 目录结构

```
<project>/
├── consts/
│   └── user_pet.go              # 常量定义（状态、Topic、配置）
│
├── app/
│   ├── domain/
│   │   └── user_pet/
│   │       ├── user_pet.go      # 宠物数据访问
│   │       └── cache.go         # 缓存操作
│   │
│   ├── service/
│   │   └── user_pet/
│   │       ├── user_pet.go      # 业务入口
│   │       ├── feed.go          # 喂养逻辑
│   │       └── event.go         # 事件发送
│   │
│   ├── dao/
│   │   └── user_pet.go          # 数据访问（代码生成）
│   │
│   └── api/
│       └── user_pet_api.go      # HTTP Handler
│
├── rpc/server/internal/
│   └── user_pet/
│       └── user_pet.go          # RPC Handler
│
└── cmd/internal/
    └── user_pet_decay/
        └── consumer.go          # CMD 消费者
```

---

### consts/user_pet.go

```go
package consts

// 宠物状态
const (
    PetStatusUnclaimed = 0
    PetStatusActive    = 1
    PetStatusFrozen    = 2
)

// NSQ Topic
const (
    PetTopic       = "xs.user.pet"
    PetFeedTopic   = "xs.user.pet.feed"
    PetDecayTopic  = "xs.user.pet.decay"
)

// Redis Key
var (
    UserPetDataKey = &RedisKey{
        key: "user:pet:data:%d",
        ttl: 24 * time.Hour,
    }
)

// 等级配置
var PetLevelConfigMap = map[int]*PetLevelConfig{
    1: {Level: 1, Name: "灵月狐", HatchThreshold: 100},
    2: {Level: 2, Name: "幻羽鹿", HatchThreshold: 300},
}

type PetLevelConfig struct {
    Level          int
    Name           string
    HatchThreshold int
}

// 工具函数（无 IO，纯计算）
func GetPetLevelByExp(exp int) int {
    for level := 10; level >= 1; level-- {
        if exp >= PetLevelConfigMap[level].HatchThreshold {
            return level
        }
    }
    return 1
}
```

---

### app/domain/user_pet/user_pet.go

```go
package domain_user_pet

import (
    "context"
    "slp/app/dao"
    "slp/app/model"
)

// GetPetByUid 根据 UID 获取宠物（封装 DAO）
func GetPetByUid(ctx context.Context, uid uint32) (*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).Where("uid", uid).One()
}

// GetPetByUidTx 根据 UID 获取宠物（带事务）
func GetPetByUidTx(ctx context.Context, tx gdb.TX, uid uint32) (*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).TX(tx).Where("uid", uid).One()
}

// CreatePetTx 创建宠物记录（带事务）
func CreatePetTx(ctx context.Context, tx gdb.TX, pet *model.UserPet) error {
    _, err := dao.UserPet.Ctx(ctx).TX(tx).Insert(pet)
    return err
}

// UpdatePetTx 更新宠物记录（带事务）
func UpdatePetTx(ctx context.Context, tx gdb.TX, uid uint32, data map[string]interface{}) error {
    _, err := dao.UserPet.Ctx(ctx).TX(tx).Where("uid", uid).Update(data)
    return err
}

// GetPetBatch 批量获取宠物（批量查询优化）
func GetPetBatch(ctx context.Context, uids []uint32) ([]*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).Where("uid", uids).All()
}
```

---

### app/service/user_pet/user_pet.go

```go
package service_user_pet

import (
    "context"
    "errors"
    "slp/app/consts"
    "slp/app/domain/user_pet"
    "slp/app/domain"
    "slp/app/model"
    "slp/app/pb"
)

// GetPet 获取宠物信息
func GetPet(ctx context.Context, uid uint32) (*pb.UserPetInfo, error) {
    // 1. 调用 domain 层获取数据
    pet, err := domain_user_pet.GetPetByUid(ctx, uid)
    if err != nil {
        return nil, err
    }
    if pet == nil {
        return nil, errors.New("宠物不存在")
    }
    
    // 2. 业务规则验证（Service 层职责）
    if pet.Status != consts.PetStatusActive {
        return nil, errors.New("宠物未激活")
    }
    
    // 3. 返回业务视图
    return &pb.UserPetInfo{
        Uid:      pet.Uid,
        PetType:  uint32(pet.PetType),
        Level:    uint32(pet.Level),
        Exp:      pet.Exp,
        Status:   uint32(pet.Status),
        LastFeed: pet.LastFeedTime,
    }, nil
}

// ClaimPet 领取宠物
func ClaimPet(ctx context.Context, uid uint32, petType uint8) (*model.UserPet, error) {
    // 分布式锁
    lockKey := consts.UserPetClaimLockKey.Key(uid)
    if !redis.SetNX(ctx, lockKey, 1, 5*time.Second) {
        return nil, errors.New("领取中，请稍后重试")
    }
    defer redis.Del(ctx, lockKey)
    
    var pet *model.UserPet
    
    // 事务操作（Service 层职责）
    err := db.Transaction(ctx, func(ctx context.Context, tx gdb.TX) error {
        // 检查已领取
        existing, _ := domain_user_pet.GetPetByUidTx(ctx, tx, uid)
        if existing != nil {
            return errors.New("宠物已领取")
        }
        
        // 创建记录
        pet = &model.UserPet{
            Uid:          uid,
            PetType:      petType,
            Level:        1,
            Exp:          0,
            Status:       consts.PetStatusActive,
            LastFeedTime: uint32(time.Now().Unix()),
        }
        
        return domain_user_pet.CreatePetTx(ctx, tx, pet)
    })
    
    if err != nil {
        return nil, err
    }
    
    // 发送领域事件（Service 层职责）
    domain.SendEvent(ctx, consts.PetTopic, "pet.claim", map[string]interface{}{
        "uid": uid,
        "pet_type": petType,
    })
    
    return pet, nil
}
```

---

### app/service/user_pet/feed.go

```go
package service_user_pet

import (
    "context"
    "slp/app/consts"
    "slp/app/domain/user_pet"
    "slp/app/domain"
)

// FeedPet 喂养宠物
func FeedPet(ctx context.Context, uid uint32, giftId uint32) (expAdd int, isLevelUp bool, newLevel int, err error) {
    // 1. 获取宠物
    pet, err := domain_user_pet.GetPetByUid(ctx, uid)
    if err != nil {
        return 0, false, 0, err
    }
    
    // 2. 业务规则验证（Service 层职责）
    if pet.Status != consts.PetStatusActive {
        return 0, false, 0, errors.New("宠物未激活")
    }
    
    // 3. 计算经验（调用 consts 工具函数）
    expAdd = calcExpAdd(giftId)
    newExp := pet.Exp + expAdd
    oldLevel := pet.Level
    newLevel = consts.GetPetLevelByExp(newExp)
    isLevelUp = newLevel > oldLevel
    
    // 4. 更新宠物（Service 层职责：事务）
    err = domain_user_pet.UpdatePetTx(ctx, nil, uid, map[string]interface{}{
        "exp":            newExp,
        "level":          newLevel,
        "last_feed_time": uint32(time.Now().Unix()),
    })
    if err != nil {
        return 0, false, 0, err
    }
    
    // 5. 发送事件（Service 层职责）
    domain.SendEvent(ctx, consts.PetFeedTopic, "pet.feed", map[string]interface{}{
        "uid":         uid,
        "gift_id":     giftId,
        "exp_add":     expAdd,
        "is_level_up": isLevelUp,
        "new_level":   newLevel,
    })
    
    if isLevelUp {
        domain.SendEvent(ctx, consts.PetTopic, "pet.levelup", map[string]interface{}{
            "uid":       uid,
            "old_level": oldLevel,
            "new_level": newLevel,
        })
    }
    
    return expAdd, isLevelUp, newLevel, nil
}

func calcExpAdd(giftId uint32) int {
    switch giftId {
    case 1001:
        return 10
    case 1002:
        return 50
    default:
        return 5
    }
}
```

---

### app/api/user_pet_api.go

```go
package api

import (
    "slp/app/pb"
    "slp/app/query"
    "slp/app/service/user_pet"
    "slp/library/response"
    "github.com/gogf/gf/net/ghttp"
)

var UserPetApi = new(userPetApi)

type userPetApi struct{}

// FeedPet 喂养宠物
// @Tags 用户宠物
// @Summary 喂养宠物
// @Router /go/slp/userPet/feed [post]
func (a *userPetApi) FeedPet(r *ghttp.Request) {
    var req *query.ReqFeedPet
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.RespFeedPet{Success: false, Message: err.Error()})
        return
    }
    
    expAdd, isLevelUp, newLevel, err := service_user_pet.FeedPet(r.Context(), req.Uid, req.GiftId)
    if err != nil {
        response.Output(r, &pb.RespFeedPet{Success: false, Message: err.Error()})
        return
    }
    
    response.Output(r, &pb.RespFeedPet{
        Success:   true,
        ExpAdd:    expAdd,
        IsLevelUp: isLevelUp,
        NewLevel:  uint32(newLevel),
    })
}
```

---

### rpc/server/internal/user_pet/user_pet.go

```go
package user_pet

import (
    "context"
    "slp/app/service/user_pet"
    "slp/rpc/server/internal/pb"
)

type userPetHandler struct{}

// FeedPet RPC 方法
func (h *userPetHandler) FeedPet(ctx context.Context, req *pb.FeedPetReq, reply *pb.FeedPetResp) error {
    // 调用 Service 层（不能直接调用 data 层）
    expAdd, isLevelUp, newLevel, err := service_user_pet.FeedPet(ctx, req.Uid, req.GiftId)
    if err != nil {
        reply.Success = false
        reply.Message = err.Error()
        return nil
    }
    
    reply.Success = true
    reply.ExpAdd = expAdd
    reply.IsLevelUp = isLevelUp
    reply.NewLevel = uint32(newLevel)
    return nil
}
```

---

### cmd/internal/user_pet_decay/consumer.go

```go
package user_pet_decay

import (
    "context"
    "encoding/json"
    "slp/app/service/user_pet"
    "slp/library/nsq"
)

type Consumer struct{}

func (c *Consumer) Consume(ctx context.Context, msg *nsq.Message) error {
    var event DecayEvent
    json.Unmarshal(msg.Body, &event)
    
    // 调用 Service 层处理（不能直接调用 data 层）
    return service_user_pet.ProcessDecay(ctx, event.Uid, event.Hours)
}

type DecayEvent struct {
    Uid   uint32 `json:"uid"`
    Hours uint32 `json:"hours"`
}
```

---

## 📋 检查清单

新业务开发时，确认：

- [ ] 常量定义在 `consts/<business>.go`
- [ ] Domain 层在 `app/domain/<business>/`
- [ ] Service 层在 `app/service/<business>/`
- [ ] HTTP/RPC/CMD 只调用 Service 层
- [ ] Service 层调用 Domain 层，不直接调 DAO
- [ ] Domain 层封装 DAO 和 RPC 调用
- [ ] Domain 层可以发送 NSQ/Kafka 事件
- [ ] Domain 层不包含复杂业务逻辑
- [ ] Domain 层不能被 RPC 直接调用

---

## 🔗 相关文档

- [`business-module-standard.md`](./business-module-standard.md) - 业务模块组织标准
- [`business-code-example.md`](./business-code-example.md) - 完整代码示例

---

**版本**: 2.0 | **基于 slp-go 和 slp-room 项目实际架构**
