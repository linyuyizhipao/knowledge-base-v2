# 业务代码编写指南

> 从 0 到 1 实现一个完整业务模块

**版本**: 1.0 | **最后更新**: 2026-04-09

---

## 🎯 场景说明

假设要新增一个「用户宠物」业务模块，需要实现：
- 用户可以领取宠物
- 喂养宠物增加经验
- 宠物升级解锁奖励
- 宠物状态需要持久化（Redis + MySQL）
- 需要发送事件通知其他模块

---

## 📁 完整文件结构

```
<project>/
├── consts/
│   ├── user_pet.go              # 宠物专属常量（RPC/CMD/HTTP 共享）
│   ├── redis.go                 # 全局 Redis Key 模板（已有）
│   └── nsq.go                   # 全局 NSQ Topic（已有）
│
├── app/
│   ├── service/
│   │   └── user_pet/
│   │       ├── service.go       # 主服务（唯一对外接口）
│   │       ├── pet.go           # 宠物核心逻辑
│   │       ├── feed.go          # 喂养逻辑
│   │       ├── level.go         # 等级逻辑
│   │       └── event.go         # 事件发送
│   │
│   ├── dao/                     # 数据访问层（代码生成）
│   │   └── user_pet_dao.go
│   │
│   ├── pb/                      # Protobuf 定义（代码生成）
│   │   └── user_pet.pb.go
│   │
│   └── api/
│       └── user_pet_api.go      # HTTP Handler
│
├── cmd/internal/
│   └── user_pet_decay/          # 宠物饥饿衰减消费者
│       └── consumer.go
│
└── rpc/server/internal/
    └── user_pet/                # RPC 服务实现
        └── service.go
```

---

## 1️⃣ 第一步：定义常量（consts/user_pet.go）

```go
package consts

// ========== 宠物状态 ==========
const (
    PetStatusUnclaimed = 0  // 未领取
    PetStatusActive    = 1  // 激活中
    PetStatusFrozen    = 2  // 冻结
)

// ========== 宠物日志类型 ==========
const (
    PetLogTypeFeed   = 1 // 打赏喂养
    PetLogTypeDecay  = 2 // 饥饿衰减
    PetLogTypeLevel  = 3 // 升级
)

// ========== NSQ Topic ==========
const (
    PetTopic        = "xs.user.pet"
    PetChannel      = "default"
    PetDecayTopic   = "xs.user.pet.decay"
    PetDecayChannel = "decay_consumer"
)

// ========== Redis Key ==========
// 使用全局 RedisKey 结构体
var (
    // 用户宠物数据：key = "user:pet:data:{uid}", TTL = 24h
    UserPetDataKey = &RedisKey{
        key: "user:pet:data:%d",
        ttl: 24 * time.Hour,
    }
    
    // 宠物日志：key = "user:pet:log:{uid}:{date}", TTL = 7d
    UserPetLogKey = &RedisKey{
        key: "user:pet:log:%d:%s",
        ttl: 7 * 24 * time.Hour,
    }
    
    // 领取锁：key = "user:pet:claim:lock:{uid}", TTL = 5s
    UserPetClaimLockKey = &RedisKey{
        key: "user:pet:claim:lock:%d",
        ttl: 5 * time.Second,
    }
)

// ========== 等级配置 ==========
var PetLevelConfigMap = map[int]*PetLevelConfig{
    1: {
        Level:          1,
        Name:           "灵月狐",
        HatchThreshold: 100,
        RewardItems:    []int32{1001, 1002},
    },
    2: {
        Level:          2,
        Name:           "幻羽鹿",
        HatchThreshold: 300,
        RewardItems:    []int32{1003, 1004, 1005},
    },
    // ... 更多等级
}

// PetLevelConfig 等级配置结构
type PetLevelConfig struct {
    Level          int     // 等级
    Name           string  // 宠物名称
    HatchThreshold int     // 孵化所需经验
    RewardItems    []int32 // 升级奖励物品 ID 列表
}

// ========== 工具函数（无 IO，纯计算） ==========

// GetPetLevelByExp 根据经验值计算等级
func GetPetLevelByExp(exp int) int {
    for level := PetMaxLevel; level >= 1; level-- {
        if exp >= PetLevelConfigMap[level].HatchThreshold {
            return level
        }
    }
    return 1
}

// CalcDecayValue 计算饥饿衰减值
func CalcDecayValue(lastFeedTime uint32) int {
    now := uint32(time.Now().Unix())
    hours := (now - lastFeedTime) / 3600
    if hours <= 0 {
        return 0
    }
    return int(hours) * PetDecayPerHour
}

const (
    PetMaxLevel    = 10
    PetDecayPerHour = 5
)
```

---

## 2️⃣ 第二步：实现 Service（app/service/user_pet/）

### service.go - 主服务文件

```go
package user_pet

import (
    "context"
    "slp/app/dao"
    "slp/app/model"
    "slp/app/pb"
    "slp/app/query"
    "slp/library/redis"
    "slp/app/consts"
)

// ========== 全局单例（唯一对外接口） ==========
var UserPetSrv = &userPetService{
    pet:   &petLogic{},
    feed:  &feedLogic{},
    level: &levelLogic{},
    event: &eventLogic{},
}

type userPetService struct {
    pet   *petLogic
    feed  *feedLogic
    level *levelLogic
    event *eventLogic
}

// ========== 主入口方法 ==========

// GetPet 获取用户宠物信息
func (s *userPetService) GetPet(ctx context.Context, uid uint32) (*pb.UserPetInfo, error) {
    return s.pet.GetPetInfo(ctx, uid)
}

// ClaimPet 领取宠物
func (s *userPetService) ClaimPet(ctx context.Context, uid uint32, petType uint8) (*pb.UserPetInfo, error) {
    return s.pet.Claim(ctx, uid, petType)
}

// FeedPet 喂养宠物
func (s *userPetService) FeedPet(ctx context.Context, req *query.ReqFeedPet, user *model.ContextUser) (*pb.RespFeedPet, error) {
    return s.feed.Feed(ctx, req, user)
}

// ========== 内部方法（对外暴露但由主对象统一调用） ==========

// GetPetDataFromCache 从缓存获取宠物数据（供其他模块调用）
func (s *userPetService) GetPetDataFromCache(ctx context.Context, uid uint32) (*model.UserPet, error) {
    return s.pet.getFromCache(ctx, uid)
}
```

### pet.go - 宠物核心逻辑

```go
package user_pet

import (
    "context"
    "encoding/json"
    "errors"
    "slp/app/consts"
    "slp/app/dao"
    "slp/app/model"
    "slp/app/pb"
    "slp/library/redis"
    "github.com/gogf/gf/database/gdb"
)

type petLogic struct{}

// GetPetInfo 获取宠物信息（先缓存后数据库）
func (l *petLogic) GetPetInfo(ctx context.Context, uid uint32) (*pb.UserPetInfo, error) {
    pet, err := l.getFromCache(ctx, uid)
    if err != nil {
        return nil, err
    }
    
    return &pb.UserPetInfo{
        Uid:       pet.Uid,
        PetType:   uint32(pet.PetType),
        Level:     uint32(pet.Level),
        Exp:       pet.Exp,
        Status:    uint32(pet.Status),
        LastFeed:  pet.LastFeedTime,
    }, nil
}

// Claim 领取宠物
func (l *petLogic) Claim(ctx context.Context, uid uint32, petType uint8) (*model.UserPet, error) {
    // 1. 分布式锁
    lockKey := consts.UserPetClaimLockKey.Key(uid)
    if !redis.SetNX(ctx, lockKey, 1, consts.UserPetClaimLockKey.ttl) {
        return nil, errors.New("领取中，请稍后重试")
    }
    defer redis.Del(ctx, lockKey)
    
    // 2. 检查是否已领取
    existing, _ := l.getFromCache(ctx, uid)
    if existing != nil && existing.Status != consts.PetStatusUnclaimed {
        return nil, errors.New("宠物已领取")
    }
    
    // 3. 开启事务
    err := gdb.Transaction(ctx, func(ctx context.Context, tx gdb.TX) error {
        // 4. 创建宠物记录
        pet := &model.UserPet{
            Uid:          uid,
            PetType:      petType,
            Level:        1,
            Exp:          0,
            Status:       consts.PetStatusActive,
            LastFeedTime: uint32(time.Now().Unix()),
            CreatedAt:    uint32(time.Now().Unix()),
        }
        
        _, err := dao.UserPet.Ctx(ctx).TX(tx).Insert(pet)
        if err != nil {
            return err
        }
        
        // 5. 写缓存
        l.writeToCache(ctx, pet)
        
        return nil
    })
    
    if err != nil {
        return nil, err
    }
    
    return l.getFromCache(ctx, uid)
}

// getFromCache 从缓存获取（私有方法）
func (l *petLogic) getFromCache(ctx context.Context, uid uint32) (*model.UserPet, error) {
    key := consts.UserPetDataKey.Key(uid)
    data, err := redis.Get(ctx, key).Bytes()
    if err == nil && len(data) > 0 {
        pet := &model.UserPet{}
        json.Unmarshal(data, pet)
        return pet, nil
    }
    
    // 缓存未命中，读数据库
    pet, err := dao.UserPet.Ctx(ctx).Where("uid", uid).One()
    if err != nil {
        return nil, err
    }
    if pet != nil {
        l.writeToCache(ctx, pet)
        return pet, nil
    }
    
    return nil, errors.New("宠物不存在")
}

// writeToCache 写入缓存（私有方法）
func (l *petLogic) writeToCache(ctx context.Context, pet *model.UserPet) {
    key := consts.UserPetDataKey.Key(pet.Uid)
    data, _ := json.Marshal(pet)
    redis.Set(ctx, key, data, consts.UserPetDataKey.ttl)
}
```

### feed.go - 喂养逻辑

```go
package user_pet

import (
    "context"
    "slp/app/consts"
    "slp/app/dao"
    "slp/app/model"
    "slp/app/pb"
    "slp/app/query"
    "slp/library/redis"
)

type feedLogic struct{}

// Feed 喂养宠物
func (l *feedLogic) Feed(ctx context.Context, req *query.ReqFeedPet, user *model.ContextUser) (*pb.RespFeedPet, error) {
    // 1. 获取宠物
    pet, err := UserPetSrv.pet.getFromCache(ctx, user.UID)
    if err != nil {
        return nil, err
    }
    
    // 2. 检查状态
    if pet.Status != consts.PetStatusActive {
        return nil, &pb.RespFeedPet{
            Success: false,
            Message: "宠物未激活",
        }
    }
    
    // 3. 增加经验
    expAdd := l.calcExpAdd(req.GiftId)
    newExp := pet.Exp + expAdd
    
    // 4. 检查是否升级
    oldLevel := pet.Level
    newLevel := consts.GetPetLevelByExp(newExp)
    isLevelUp := newLevel > oldLevel
    
    // 5. 开启事务
    err = dao.UserPet.Ctx(ctx).Where("uid", user.UID).Update(&model.UserPet{
        Exp:          newExp,
        Level:        newLevel,
        LastFeedTime: uint32(time.Now().Unix()),
    })
    if err != nil {
        return nil, err
    }
    
    // 6. 更新缓存
    pet.Exp = newExp
    pet.Level = newLevel
    pet.LastFeedTime = uint32(time.Now().Unix())
    UserPetSrv.pet.writeToCache(ctx, pet)
    
    // 7. 记录日志
    l.logFeed(ctx, user.UID, req.GiftId, expAdd)
    
    // 8. 发送事件
    if isLevelUp {
        UserPetSrv.event.SendLevelUpEvent(ctx, user.UID, uint8(oldLevel), uint8(newLevel))
    }
    
    var rewardItems []int32
    if isLevelUp {
        rewardItems = consts.PetLevelConfigMap[newLevel].RewardItems
    }
    
    return &pb.RespFeedPet{
        Success:   true,
        PetExp:    newExp,
        PetLevel:  uint32(newLevel),
        IsLevelUp: isLevelUp,
        Rewards:   rewardItems,
    }, nil
}

// calcExpAdd 计算经验增加值
func (l *feedLogic) calcExpAdd(giftId uint32) int {
    // 根据礼物类型返回不同经验值
    switch giftId {
    case 1001:
        return 10
    case 1002:
        return 50
    default:
        return 5
    }
}

// logFeed 记录喂养日志
func (l *feedLogic) logFeed(ctx context.Context, uid uint32, giftId uint32, exp int) {
    // 异步记录，不阻塞主流程
    go func() {
        date := time.Now().Format("20060102")
        key := consts.UserPetLogKey.Key(uid, date)
        redis.HIncrBy(ctx, key, string(giftId), int64(exp))
        redis.Expire(ctx, key, consts.UserPetLogKey.ttl)
    }()
}
```

### event.go - 事件发送

```go
package user_pet

import (
    "context"
    "encoding/json"
    "slp/app/consts"
    "slp/library/nsq"
)

type eventLogic struct{}

// SendLevelUpEvent 发送升级事件
func (l *eventLogic) SendLevelUpEvent(ctx context.Context, uid uint32, oldLevel, newLevel uint8) {
    data := &PetLevelUpEvent{
        Uid:      uid,
        OldLevel: oldLevel,
        NewLevel: newLevel,
    }
    
    jsonData, _ := json.Marshal(data)
    nsq.Publish(consts.PetTopic, &consts.NsqData{
        Cmd:  "pet.levelup",
        Data: string(jsonData),
    })
}

// PetLevelUpEvent 宠物升级事件
type PetLevelUpEvent struct {
    Uid      uint32 `json:"uid"`
    OldLevel uint8  `json:"old_level"`
    NewLevel uint8  `json:"new_level"`
}
```

---

## 3️⃣ 第三步：实现 API Handler（app/api/user_pet_api.go）

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

// GetPet 获取宠物信息
// @Tags 用户宠物
// @Summary 获取宠物信息
// @Router /go/slp/userPet/get [post]
func (a *userPetApi) GetPet(r *ghttp.Request) {
    var req *query.ReqUserPetGet
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.UserPetInfo{Success: false, Message: err.Error()})
        return
    }
    
    info, err := user_pet.UserPetSrv.GetPet(r.Context(), req.Uid)
    if err != nil {
        response.Output(r, &pb.UserPetInfo{Success: false, Message: err.Error()})
        return
    }
    
    response.Output(r, info)
}

// ClaimPet 领取宠物
// @Tags 用户宠物
// @Summary 领取宠物
// @Router /go/slp/userPet/claim [post]
func (a *userPetApi) ClaimPet(r *ghttp.Request) {
    var req *query.ReqClaimPet
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.RespClaimPet{Success: false, Message: err.Error()})
        return
    }
    
    pet, err := user_pet.UserPetSrv.ClaimPet(r.Context(), req.Uid, req.PetType)
    if err != nil {
        response.Output(r, &pb.RespClaimPet{Success: false, Message: err.Error()})
        return
    }
    
    response.Output(r, &pb.RespClaimPet{
        Success: true,
        PetInfo: &pb.UserPetInfo{
            Uid:     pet.Uid,
            PetType: uint32(pet.PetType),
            Level:   uint32(pet.Level),
        },
    })
}

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
    
    resp, err := user_pet.UserPetSrv.FeedPet(r.Context(), req, r.GetCtxUser())
    if err != nil {
        response.Output(r, &pb.RespFeedPet{Success: false, Message: err.Error()})
        return
    }
    
    response.Output(r, resp)
}
```

---

## 4️⃣ 第四步：实现 CMD 消费者（cmd/internal/user_pet_decay/）

```go
package user_pet_decay

import (
    "context"
    "encoding/json"
    "slp/app/consts"
    "slp/app/service/user_pet"
    "slp/library/nsq"
)

type Consumer struct {
    topic   string
    channel string
}

func NewConsumer() *Consumer {
    return &Consumer{
        topic:   consts.PetDecayTopic,
        channel: consts.PetDecayChannel,
    }
}

// Consume 消费消息
func (c *Consumer) Consume(ctx context.Context, msg *nsq.Message) error {
    var event DecayEvent
    if err := json.Unmarshal(msg.Body, &event); err != nil {
        return err
    }
    
    // 调用 Service 处理衰减逻辑
    err := user_pet.UserPetSrv.ProcessDecay(ctx, event.Uid, event.Hours)
    if err != nil {
        // 失败重试
        return err
    }
    
    return nil
}

type DecayEvent struct {
    Uid   uint32 `json:"uid"`
    Hours uint32 `json:"hours"`
}
```

---

## 5️⃣ 第五步：RPC 服务（rpc/server/internal/user_pet/）

```go
package user_pet

import (
    "context"
    "slp/app/service/user_pet"
    "slp/rpc/server/internal/pb"
)

type Service struct{}

// GetUserPet RPC 方法：获取用户宠物
func (s *Service) GetUserPet(ctx context.Context, req *pb.GetUserPetReq) (*pb.GetUserPetResp, error) {
    info, err := user_pet.UserPetSrv.GetPet(ctx, req.Uid)
    if err != nil {
        return &pb.GetUserPetResp{Success: false, Message: err.Error()}, nil
    }
    
    return &pb.GetUserPetResp{
        Success: true,
        PetInfo: info,
    }, nil
}

// FeedPet RPC 方法：喂养宠物
func (s *Service) FeedPet(ctx context.Context, req *pb.FeedPetReq) (*pb.FeedPetResp, error) {
    // 复用 Service 层逻辑
    // ...
    return &pb.FeedPetResp{Success: true}, nil
}
```

---

## ✅ 关键设计总结

### 1. 常量定义（consts/）

```go
consts/
├── user_pet.go      # 宠物业务专属（RPC/CMD/HTTP 共享）
├── redis.go         # 全局 Redis Key 模板
└── nsq.go           # 全局 NSQ Topic 模板
```

**为什么独立**：
- RPC、CMD、HTTP 都引用同一套常量
- 避免循环依赖
- 修改常量不需要改 Service

---

### 2. Service 层组织

```go
app/service/user_pet/
├── service.go       # 主服务（唯一对外接口）
├── pet.go           # 宠物核心逻辑
├── feed.go          # 喂养逻辑
├── level.go         # 等级逻辑
└── event.go         # 事件发送
```

**全局单例注入模式**：

```go
var UserPetSrv = &userPetService{
    pet:   &petLogic{},
    feed:  &feedLogic{},
    level: &levelLogic{},
    event: &eventLogic{},
}
```

**调用关系**：
- 外部调用：`user_pet.UserPetSrv.GetPet()`
- 内部调用：`UserPetSrv.pet.getFromCache()`
- 跨模块：`user_pet.UserPetSrv.GetPetDataFromCache()`

---

### 3. 无 IO 工具函数

放在 `consts/user_pet.go` 中：

```go
// 纯计算，无 IO
func GetPetLevelByExp(exp int) int {
    // ...
}

func CalcDecayValue(lastFeedTime uint32) int {
    // ...
}
```

如果工具函数较大，可放在 `app/utils/pet.go`，但仍保持无 IO。

---

### 4. 跨模块调用

```go
// ✅ 正确：通过全局单例调用
pet := user_pet.UserPetSrv.GetPet(ctx, uid)

// ✅ 正确：DAO 层直接调用（数据访问）
user := dao.User.Ctx(ctx).Where("uid", uid).One()

// ❌ 错误：调用内部子模块
// pet := user_pet.petLogic.getFromCache()  // petLogic 未导出
```

---

## 📋 新业务开发检查清单

- [ ] 在 `consts/` 定义业务常量（状态、Topic、RedisKey）
- [ ] 在 `consts/` 定义配置数据（如等级配置表）
- [ ] 在 `consts/` 定义无 IO 工具函数
- [ ] 创建 `app/service/<business>/` 目录
- [ ] `service.go` 定义唯一对外暴露的全局单例
- [ ] 子模块逻辑注入到主对象
- [ ] Redis Key 使用全局 `RedisKey` 结构体
- [ ] NSQ Topic 遵循 `xs.<module>.*` 命名
- [ ] Handler 只负责参数解析 + 调用 Service + 返回

---

**版本**: 1.0 | **基于 slp-go 和 slp-room 项目实际**
