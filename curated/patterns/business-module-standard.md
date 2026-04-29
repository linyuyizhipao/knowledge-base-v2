# 业务开发规范

> 业务代码的组织结构与职责划分

**版本**: 1.0 | **最后更新**: 2026-04-09

---

## 🎯 核心原则

**一个业务模块 = 一个目录 = 一个对外服务对象**

业务代码组织的核心目标：
1. **职责清晰** - 每个文件/目录只做一件事
2. **易于导航** - 看到文件名就知道去哪里找代码
3. **低耦合** - 模块间通过明确接口交互
4. **可测试** - 每个模块可以独立测试

---

## 📁 标准结构

### 推荐模式

```
<project>/
├── consts/                      # 常量定义（按业务模块划分）
│   ├── redis.go                 # 全局 Redis Key 定义
│   ├── nsq.go                   # 全局 NSQ Topic 定义
│   ├── error.go                 # 全局错误定义
│   ├── <business>.go            # 业务专属常量（推荐）
│   └── ...
│
└── app/service/                 # Service 层（按业务模块划分）
    ├── <business>/              # 业务模块目录
    │   ├── service.go           # 主服务文件（唯一对外接口）
    │   ├── const.go             # 模块专属常量（RedisKey, Topic, 配置等）
    │   ├── model.go             # 模块专属数据结构
    │   ├── <module>.go          # 子模块逻辑（可选）
    │   └── <module>_test.go     # 测试文件
    └── ...
```

---

## 📦 各层级职责

### 1. consts/ - 常量定义层

**职责**：定义全局共享的常量、Key、Topic

**文件组织**：

| 文件 | 用途 | 示例 |
|------|------|------|
| `redis.go` | 全局 Redis Key 模板 | `RedisKey` 结构体定义 |
| `nsq.go` | 全局 NSQ Topic/Channel | `TopicUserLogin`, `ChannelDefault` |
| `error.go` | 全局错误定义 | `ErrUserNotFound` |
| `<business>.go` | 业务专属常量 | `PetMaxLevel`, `GiftConfig` |

**业务专属常量示例** (`consts/immortal_pet.go`):

```go
package consts

// 状态常量
const (
    PetStatusUnclaimed   = 0  // 未领取
    PetStatusFeeding     = 1  // 喂养中
    PetStatusHatching    = 2  // 孵化中
    PetStatusRewardReady = 3  // 奖励待领取
)

// 配置数据结构
type PetLevelConfig struct {
    Level          int
    Name           string
    PetImage       string
    HatchThreshold int
    RewardPool     []PetRewardPoolEntry
}

// Redis Key（业务专属）
var (
    ImmortalPetRewardPoolKey = &RedisKey{
        key: "immortal:pet:reward:pool:%d:%d:%d",
        ttl: 7 * 24 * time.Hour,
    }
)

// 完整配置映射
var PetLevelConfigMap = map[int]PetLevelConfig{
    1: { Level: 1, Name: "灵月狐", HatchThreshold: 100 },
    2: { Level: 2, Name: "幻羽鹿", HatchThreshold: 200 },
    // ...
}

// 工具函数（无 IO）
func GetPetLevelByRoomLevel(roomLevel int32) int {
    if petLevel, ok := RoomLevelToPetLevelMap[roomLevel]; ok {
        return petLevel
    }
    return PetMaxLevel
}
```

---

### 2. app/service/<business>/ - Service 层

**职责**：实现完整的业务逻辑

**标准结构**：

```
app/service/anchor/
├── service.go           # 主服务文件（对外暴露唯一入口）
├── const.go             # 模块专属常量
├── model.go             # 模块专属数据结构
├── credit.go            # 信用分逻辑（子模块）
├── match.go             # 匹配逻辑（子模块）
└── anchor_test.go       # 测试文件
```

#### service.go - 主服务文件

**规范**：
- 定义唯一的对外暴露对象（全局单例）
- 所有外部调用通过此对象进行
- 子模块的方法应注入到主对象

```go
package anchor

import (
    "context"
    "slp/app/pb"
    "slp/app/query"
    "slp/app/model"
)

// ========== 对外暴露的唯一对象 ==========
var AnchorSrv = &anchorSrv{
    credit:  &anchorCredit{},
    match:   &anchorMatch{},
    mission: &anchorMission{},
}

type anchorSrv struct {
    credit  *anchorCredit
    match   *anchorMatch
    mission *anchorMission
}

// ========== 主入口方法 ==========

func (s *anchorSrv) Index(ctx context.Context, req *query.ReqAnchorTab, user *model.ContextUser) *pb.AnchorCenter {
    if req.Type == 1 {
        return s.homeTab(ctx, user)
    }
    return s.missionTab(ctx, user)
}

// ========== 内部方法（按子模块划分） ==========

func (s *anchorSrv) homeTab(ctx context.Context, user *model.ContextUser) *pb.AnchorCenter {
    // 调用子模块
    credit := s.credit.GetScore(user.UID)
    missions := s.mission.GetList(ctx, user.UID)
    return &pb.AnchorCenter{Credit: credit, Missions: missions}
}
```

#### const.go - 模块专属常量

```go
package anchor

const (
    AnchorTopic        = "xs.anchor"
    AnchorTopicChannel = "default"
    AnchorAllMicGiftCmd  = "all.mic"
    AnchorFirstGiftCmd   = "first.gift"
)

const (
    AnchorUserUnPickedList       = "Xs.Anchor.User.UnPicked.List"
    AnchorUserRePickedListPrefix = "Xs.Anchor.User.RePicked.List.%d"
)

// 模块专属 Redis Key
var (
    AnchorCreditKey = &RedisKey{
        key: "anchor:credit:%d",
        ttl: 24 * time.Hour,
    }
)
```

#### model.go - 模块专属数据结构

```go
package anchor

type AnchorCredit struct {
    UID      uint32
    Score    int64
    Level    uint8
    UpdatedAt uint32
}

type AnchorMission struct {
    ID          uint32
    Title       string
    Description string
    Reward      int64
    Status      uint8
}
```

#### 子模块文件（credit.go, match.go）

```go
package anchor

type anchorCredit struct{}

func (c *anchorCredit) GetScore(uid uint32) int64 {
    // 纯业务逻辑，无 IO 或通过 DAO 层访问
    return 100
}

func (c *anchorCredit) AddScore(uid uint32, delta int64) error {
    // ...
    return nil
}
```

---

### 3. app/utils/ - 工具函数层

**职责**：纯计算、无 IO 的工具函数

**原则**：
- 不涉及数据库、Redis、NSQ 等 IO 操作
- 可以被多个业务模块复用
- 按功能类型划分文件

```
app/utils/
├── bit.go              # 位运算
├── array.go            # 数组操作
├── room.go             # 房间相关工具
├── gift_format.go      # 礼物格式化
└── ...
```

**示例** (`utils/bit.go`):

```go
package utils

var RoomPk = &roomPk{}
type roomPk struct{}

// 纯计算函数，无 IO
func (r *roomPk) BitEncode(uid uint32, cateId uint8, groupId uint16) uint64 {
    return (uid << 32) | (uint64(cateId) << 24) | uint64(groupId)
}

func (r *roomPk) GrayUid(uid uint32, rate uint8) bool {
    return uid % 100 < uint32(rate)
}
```

---

## ✅ 推荐做法

### 做法 1：常量定义优先级

| 常量类型 | 定义位置 | 示例 |
|----------|----------|------|
| **业务专属** | `app/service/<business>/const.go` | `anchor/const.go` |
| **全局共享** | `consts/redis.go`, `consts/nsq.go` | `RedisKey`, `TopicUserLogin` |
| **配置型数据** | `consts/<business>.go` | `PetLevelConfigMap` |

---

### 做法 2：Service 层对象组织

```go
// ✅ 推荐：全局单例 + 子模块注入
var GiftSrv = &giftService{
    panel:  &giftPanel{},
    box:    &giftBox{},
    suit:   &giftSuit{},
    event:  &giftEvent{},
}

type giftService struct {
    panel *giftPanel
    box   *giftBox
    suit  *giftSuit
    event *giftEvent
}

func (g *giftService) PanelList(ctx context.Context, uid uint32) []*pb.GiftPanel {
    return g.panel.GetList(ctx, uid)  // 调用子模块
}
```

---

### 做法 3：模块间调用

```go
// ✅ 推荐：通过全局单例调用
credit := anchor.AnchorSrv.GetCredit(ctx, uid)

// ✅ 推荐：通过 DAO 层调用（数据访问）
user := dao.User.Find(uid)

// ❌ 避免：直接调用其他模块的内部方法
// credit := anchor.credit.GetScore(uid)  // credit 是内部子模块
```

---

### 做法 4：Redis Key 定义

```go
// ✅ 推荐：业务模块内定义专属 Key
package anchor

var (
    AnchorCreditKey = &RedisKey{
        key: "anchor:credit:%d",
        ttl: 24 * time.Hour,
    }
)

// 使用
creditData, _ := redis.Get(ctx, AnchorCreditKey.Key(uid))
```

---

### 做法 5：NSQ Topic 定义

```go
// ✅ 推荐：模块内定义专属 Topic
package anchor

const (
    AnchorTopic        = "xs.anchor"
    AnchorTopicChannel = "default"
)

// 使用
nsq.Publish(AnchorTopic, &NsqData{Cmd: "anchor.update", Data: data})
```

---

## ❌ 反模式

### 反模式 1：常量分散

```go
// ❌ 错误：常量分散在各个文件中
// app/service/anchor/anchor.go
const AnchorTopic = "xs.anchor"  // 应该移到 const.go

// app/service/anchor/match.go
const MatchTopic = "xs.match"    // 应该移到 const.go
```

**正确做法**：
```go
// ✅ 统一在 const.go 中定义
package anchor

const (
    AnchorTopic = "xs.anchor"
    MatchTopic  = "xs.match"
)
```

---

### 反模式 2：Service 无聚合

```go
// ❌ 错误：每个子模块独立暴露
var AnchorCreditSrv = &anchorCredit{}
var AnchorMatchSrv  = &anchorMatch{}
var AnchorMissionSrv = &anchorMission{}

// 外部调用混乱
credit := anchor.AnchorCreditSrv.GetScore(uid)
match  := anchor.AnchorMatchSrv.GetMatch(uid)
```

**正确做法**：
```go
// ✅ 统一通过主对象暴露
var AnchorSrv = &anchorSrv{
    credit: &anchorCredit{},
    match:  &anchorMatch{},
}

credit := AnchorSrv.GetCredit(uid)  // 内部调用 s.credit.GetScore(uid)
```

---

### 反模式 3：工具函数带 IO

```go
// ❌ 错误：utils 中包含 IO 操作
func GetUser(uid uint32) *User {
    return redis.Get("user:" + uid)  // IO 操作！
}
```

**正确做法**：
```go
// ✅ IO 操作放在 Service 层
func (s *userService) GetUser(uid uint32) *User {
    return dao.User.Find(uid)
}

// utils 只做纯计算
func (u *userUtils) FormatName(name string) string {
    return strings.TrimSpace(name)
}
```

---

## 📋 检查清单

创建新业务模块时，确认：

- [ ] 在 `consts/` 或 `app/service/<business>/const.go` 中定义常量
- [ ] Redis Key 使用 `RedisKey` 结构体，带 TTL
- [ ] NSQ Topic 有统一的命名（如 `xs.<module>.*`）
- [ ] Service 层有唯一的对外暴露对象（全局单例）
- [ ] 子模块方法注入到主对象，不直接暴露
- [ ] 无 IO 的工具函数放在 `app/utils/`
- [ ] 测试文件跟随服务文件（`<name>_test.go`）

---

## 📁 完整示例：新业务模块创建

假设要创建「用户成就」模块：

```
1. 创建目录
   mkdir -p app/service/achievement

2. 创建文件结构
   app/service/achievement/
   ├── service.go           # 主服务
   ├── const.go             # 常量
   ├── model.go             # 数据模型
   ├── medal.go             # 勋章子模块
   ├── title.go             # 称号子模块
   └── achievement_test.go  # 测试

3. consts.go
   package achievement

   const (
       AchievementTopic = "xs.achievement"
       ChannelDefault   = "default"
   )

   var (
       AchievementUserKey = &RedisKey{
           key: "achievement:user:%d",
           ttl: 24 * time.Hour,
       }
   )

4. service.go
   package achievement

   var AchievementSrv = &achievementService{
       medal: &medalService{},
       title: &titleService{},
   }

   type achievementService struct {
       medal *medalService
       title *titleService
   }

   func (s *achievementService) GetUserAchievements(ctx context.Context, uid uint32) *pb.UserAchievement {
       medals := s.medal.GetList(ctx, uid)
       titles := s.title.GetList(ctx, uid)
       return &pb.UserAchievement{Medals: medals, Titles: titles}
   }
```

---

## 🔗 相关文档

- [`code-scale-standard.md`](./code-scale-standard.md) - 代码规模标准
- [`event-extension-guide.md`](./event-extension-guide.md) - 事件开发规范
- [`cmd-module-standard.md`](./cmd-module-standard.md) - CMD 模块标准

---

**版本**: 1.0 | **基于 slp-go 和 slp-room 项目实际代码分析**
