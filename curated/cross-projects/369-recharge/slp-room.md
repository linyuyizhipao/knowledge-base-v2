# 369 元观光团 - slp-room 项目视角

> 房间服务在 369 业务中的职责和实现

## 项目内职责

| 职责 | 说明 | 核心文件 |
|------|------|----------|
| **进房事件捕获** | 捕获用户进入白名单房间 | `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` |
| **离房事件捕获** | 捕获用户离开房间 | `cmd/internal/room_recommend_more/event/recharge_369_group_leave_room.go` |
| **白名单房间判断** | 判断房间是否为 369 活动白名单 | `app/service/plugin/service.go` |
| **A/B/C 分组** | 用户分组（RSA 均匀分配） | `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` |
| **版本判断** | 根据客户端版本写入 cast_version | `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` |
| **弹窗触发判断** | B 组 60 秒弹窗，C 组离房弹窗 | `app/service/recharge/recharge369.go` |
| **Domain 层** | 369 用户数据访问 | `app/domain/xs_room_369_group_user.go` |

---

## 核心代码

### 1. 进房事件处理

```go
// cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go

func init() {
    HandleEventMap[consts.Recharge369GroupEnterRoomEvent] = &recharge369EnterRoomEvent{}
}

type recharge369EnterRoomEvent struct{}

func (s *recharge369EnterRoomEvent) RoomRecommendEvent(ctx, nsqEventMsg) error {
    rid := gconv.Uint32(nsqEventMsg.Data["rid"])
    uid := gconv.Uint32(nsqEventMsg.Data["uid"])
    refer := gconv.String(nsqEventMsg.Data["refer"])
    
    // 处理 369 观光团逻辑
    _ = s.handleXsRoom369GroupUser(ctx, uid, rid, refer)
    
    // 发布用户进房事件到 slp-go
    _, _ = client.UserGrowth.UserRoomEvent(ctx, &pb.ReqUserRoomEvent{
        Uid:   uid,
        Event: "enter_room",
    })
    return nil
}
```

### 2. 白名单房间判断

```go
// 检查房间是否在 369 活动白名单中
whiteMap, err := client.CommonCache.BatchBbcRoomRedpacketsWhitelist(ctx, 200, []uint32{rid})
if err != nil {
    g.Log().Ctx(ctx).Error("msg", "handleActRechargeWhite369", "err", err)
    return nil
}
if !whiteMap[rid] {
    return nil // 不是白名单房间
}
```

### 3. 主播身份判断

```go
// 排除主播用户
gsMap := client.UserProfile.BatchCheckGs(ctx, []uint32{uid})
if gsMap[uid] {
    return nil // 是主播，不参与
}
```

### 4. 进房来源判断

```go
// 仅可通过搜索靓号或点击个人主页进房才算有效用户
var referList = []string{
    "pretty_uid",            // 搜用户靓号，直接踩房
    "SearchScreen:UserPage", // 搜用户 UID+ 进用户主页进房
}

if !tool.Slice.InStringArray(refer, referList) {
    return nil // 来源不符合（如私聊、个人资料页进房不算）
}
```

### 5. A/B/C 分组算法

```go
// 绝对均匀的分组逻辑
func (s *recharge369EnterRoomEvent) getNextGroupType(ctx) int64 {
    rds := library.RedisClient(library.RedisPassive)
    groupVal := rds.Incr(ctx, "slp.recharge369EnterRoomEvent.next.group").Val()
    groupType := groupVal % 3 + 1  // 1=A, 2=B, 3=C
    return groupType
}
```

| 分组 | 弹窗策略 | 说明 |
|------|----------|------|
| A 组 | 不可见弹窗 | 对照组，不参与功能 |
| B 组 | 进房 60 秒后触发 | 房间小窗情况下，需再次展开时弹出 |
| C 组 | 离房前触发 | 房间内杀端/切后台，下次上线时触发 |

### 6. 版本判断逻辑

```go
castVersion := "v1"
groupType := int64(0)
versionNum := php2go.IP2long(userVersion.Version)

// 版本低于 5.55.0.0 不参与
if versionNum < php2go.IP2long("5.55.0.0") {
    groupType = 0
} else {
    groupType = s.getNextGroupType(ctx)
}

// 5.58.0.0+ 使用 V2 版本逻辑
if versionNum >= php2go.IP2long("5.58.0.0") {
    castVersion = "v2"
}

// 插入记录
insertData := g.Map{
    "uid": uid, "rid": rid, "enter_refer": refer,
    "pop_state": 1, "group_type": groupType,
    "create_time": time.Now().Unix(),
    "update_time": time.Now().Unix(),
    "cast_version": castVersion,
}
dao.XsRoom369GroupUser.Data(insertData).Insert()
```

### 7. 弹窗触发判断

```go
// app/service/recharge/recharge369.go

func CheckShowRecharge368Pop(ctx, user *pb.EntityXsRoom369GroupUser) bool {
    // A 组用户不显示
    if user.GroupType == dao.Room369GroupUserGroupA {
        return false
    }
    
    // 7 天内未充值不显示
    isFistRechargeInvalidFlag := int64(user.GetCreateTime())+7*86400 < int64(user.GetFirstRechargeTime())
    noRechargeFlag := user.GetFirstRechargeTime() == 0 && int64(user.GetCreateTime()) < time.Now().AddDate(0, 0, -7).Unix()
    if isFistRechargeInvalidFlag || noRechargeFlag {
        return false
    }
    
    // 超过 1 年不显示
    if int64(user.GetCreateTime()) < time.Now().AddDate(-1, 0, 0).Unix() {
        return false
    }
    
    // 已领完最高档不显示
    if user.GetCastVersion() != "v2" {
        if user.GetRechargeRmb() >= 30 && user.GetDay_7() > 0 {
            return false
        }
    } else {
        if user.GetRechargeRmb() >= 100 && user.GetDay_10() > 0 {
            return false
        }
    }
    
    return true
}
```

### 8. Domain 层数据访问

```go
// app/domain/xs_room_369_group_user.go

var Room369GroupUser = room369GroupUser{}

type room369GroupUser struct{}

func (r *room369GroupUser) GetRoom369GroupUser(ctx context.Context, uid uint32) *pb.EntityXsRoom369GroupUser {
    var users []*pb.EntityXsRoom369GroupUser
    _ = client.CommonCache.CodecMGetV2(ctx, dao.XsRoom369GroupUser.Table, &users, uid)
    
    userMap := make(map[uint32]*pb.EntityXsRoom369GroupUser)
    for _, user := range users {
        userMap[user.GetUid()] = user
    }
    return userMap[uid]
}
```

---

## 依赖的外部服务

### RPC 调用

| RPC 方法 | 用途 | 服务 |
|----------|------|------|
| `CommonCache.BatchBbcRoomRedpacketsWhitelist` | 批量判断白名单房间 | slp-room 内部 |
| `UserProfile.BatchCheckGs` | 批量判断主播身份 | slp-go |
| `UserProfile.Get` | 获取用户信息 | slp-go |
| `UserGrowth.UserRoomEvent` | 同步进房/离房事件 | slp-go |

### 事件订阅

| 事件 | 用途 |
|------|------|
| `EnterRoomRoomRecommend` | 进房事件（信息流推荐） |
| `Recharge369GroupEnterRoomEvent` | 369 进房事件 |
| `Recharge369GroupLeaveRoomEvent` | 369 离房事件 |

---

## 常量定义

```go
// consts/room_recommend_more.go
const (
    Recharge369GroupEnterRoomEvent RoomRecommendEvent = "recharge_user_group_enter_room"
    Recharge369GroupLeaveRoomEvent RoomRecommendEvent = "recharge_user_group_leave_room"
)

// consts/plugin.go
const (
    PluginIdRecharge369UserGroup = 16  // 369 充值用户分组
)

// consts/white_list.go
const (
    BbcRoomRedpacketsWhitelist369Type      = 200 // 369 白名单类型
    BbcRoomRedpacketsWhitelist369TypeCfgId = 106 // 369 业务 cfg_id
)
```

---

## 本地测试

### 1. 模拟进房事件

```bash
# 发送 NSQ 事件模拟用户进房
curl -X POST http://localhost:8080/nsq/pub \
  -d '{"topic":"slp.room.recommend.event","data":{"uid":123456,"rid":789,"refer":"pretty_uid","event":"enter_room"}}'
```

### 2. 检查数据库记录

```sql
-- 查看用户 369 记录
SELECT * FROM xs_room_369_group_user WHERE uid = 123456;

-- 查看分组分布
SELECT group_type, COUNT(*) as cnt 
FROM xs_room_369_group_user 
GROUP BY group_type;
```

### 3. 检查 Redis 分组计数器

```bash
redis-cli GET "slp.recharge369EnterRoomEvent.next.group"
```

---

## 日志关键点

### 进房事件日志

```go
g.Log().Ctx(ctx).Info("msg", "handleActRechargeWhite369", 
    "rid", rid, "uid", uid, "refer", refer)
```

### 弹窗判断日志

```go
g.Log().Async(true).Ctx(ctx).Info("msg", "Recharge369GroupType", "uid", user.GetUid())
```

---

## 相关文件列表

```
slp-room/
├── cmd/internal/room_recommend_more/event/
│   ├── recharge_369_group_enter_room.go    # 进房事件处理
│   ├── recharge_369_group_leave_room.go    # 离房事件处理
│   └── event_enter_room.go                 # 进房事件总入口
├── app/service/
│   ├── recharge/recharge369.go             # 弹窗判断逻辑
│   └── plugin/service.go                   # 白名单判断
├── app/domain/
│   └── xs_room_369_group_user.go           # Domain 层访问
├── app/dao/
│   ├── xs_room_369_group_user.go           # DAO 层
│   └── internal/xs_room_369_group_user.go  # DAO 内部
├── app/model/
│   ├── xs_room_369_group_user.go           # Model 层
│   └── internal/xs_room_369_group_user.go  # Model 内部
├── app/pb/
│   └── entity_xs_room_369_group_user.pb.go # Proto 定义
├── consts/
│   ├── room_recommend_more.go              # 事件常量
│   ├── plugin.go                           # 插件 ID
│   └── white_list.go                       # 白名单常量
└── proto/
    └── entity_xs_room_369_group_user.proto # Proto 源文件
```

---

## 与其他项目交互

### → slp-go

| 交互点 | 说明 |
|--------|------|
| `UserGrowth.UserRoomEvent` | 同步进房/离房事件，slp-go 用于记录用户行为 |
| `UserProfile.BatchCheckGs` | 查询用户是否为主播 |
| `CommonCache.CodecMGetV2` | 查询 369 用户记录（共享缓存） |

---

**版本**: 1.0 | **更新**: 2026-04-05
