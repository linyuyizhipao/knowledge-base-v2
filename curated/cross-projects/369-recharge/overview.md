# 369 元观光团充值业务 - 跨项目全景

> 涉及 slp-room、slp-go 两个项目的充值营销活动

## 业务全景图

```
┌─────────────────────────────────────────────────────────────────┐
│                        369 元观光团业务全貌                       │
└─────────────────────────────────────────────────────────────────┘

┌───────────────────┐         ┌───────────────────┐
│    slp-room       │         │     slp-go        │
│   (房间服务)       │         │   (用户/充值服务)  │
│                   │         │                   │
│  ● 进房事件捕获    │────────▶│  ● 充值记录管理   │
│  ● 离房事件捕获    │         │  ● 奖励发放       │
│  ● 白名单房间判断  │         │  ● 档位计算       │
│  ● A/B/C 分组      │         │  ● 签到领奖       │
│  ● 弹窗触发       │◀────────│  ● 弹窗状态同步   │
└───────────────────┘         └───────────────────┘
         │                              │
         ▼                              ▼
  ┌─────────────┐              ┌─────────────┐
  │ xs_room_369 │              │ xs_room_369 │
  │ _group_user │              │ _group_user │
  │ (房间侧缓存) │              │ (用户侧主表)  │
  └─────────────┘              └─────────────┘
```

---

## 项目职责分工

| 项目 | 职责 | 核心模块 | 文档 |
|------|------|----------|------|
| **slp-room** | 进房/离房事件捕获、白名单判断、A/B/C 分组、弹窗触发 | `cmd/internal/room_recommend_more/event/` | [`slp-room.md`](./slp-room.md) |
| **slp-go** | 充值记录管理、档位计算、奖励发放、签到领奖、API 接口 | `app/service/recharge/` | [`slp-go.md`](./slp-go.md) |

---

## 核心数据表

### xs_room_369_group_user

两个项目**共享同一张表**

| 字段 | 类型 | 说明 | 主要写入方 |
|------|------|------|-----------|
| `uid` | uint32 | 用户 ID | 共用 |
| `rid` | uint32 | 进入的房间 ID | slp-room |
| `enter_refer` | string | 进房来源 | slp-room |
| `group_type` | uint32 | 分组：1=A,2=B,3=C | slp-room |
| `pop_state` | uint32 | 弹窗状态 | slp-room |
| `recharge_rmb` | uint32 | 累计充值金额 | slp-go |
| `day_1`~`day_10` | uint32 | 每天领奖档位 | slp-go |
| `cast_version` | string | 版本：v1/v2 | slp-room |
| `first_recharge_time` | uint32 | 首次充值时间 | slp-go |
| `last_send_time` | uint32 | 最近一次领取奖励时间 | slp-go |
| `extra` | string | 扩展字段（JSON） | slp-go |

---

## 跨项目核心流程

### 1. 用户进房流程

```
用户进房
   │
   ▼
┌─────────────────────────────┐
│ slp-room: 捕获进房事件       │
│ event_enter_room.go         │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 1. 白名单房间判断            │
│ BatchBbcRoomRedpacketsWhitelist │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 2. 主播身份判断              │
│ BatchCheckGs                │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 3. 进房来源判断              │
│ refer: pretty_uid/SearchScreen │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 4. 是否已存在记录            │
│ XsRoom369GroupUser.Where(uid) │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 5. 插入用户记录              │
│ - group_type: A/B/C (RSA 均匀) │
│ - cast_version: v1/v2 (版本号) │
│ - pop_state: 1              │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ 6. 发布 NSQ 事件              │
│ UserGrowth.UserRoomEvent    │
└─────────────────────────────┘
```

### 2. 充值回调流程

```
用户充值成功
     │
     ▼
┌─────────────────────────────┐
│ slp-go: 支付回调             │
│ cmd/internal/pay/handle/    │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ RechargeType369Callback     │
│ - 更新 recharge_rmb          │
│ - 记录 first_recharge_time   │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ RechargeType369Online       │
│ (用户在线时自动发奖)          │
└─────────────┬───────────────┘
              │
              ▼
┌─────────────────────────────┐
│ sendRechargeType369GroupReward │
│ - 更新 day_N 字段             │
│ - 发放物品                   │
│ - 发送弹窗通知               │
└─────────────────────────────┘
```

### 3. A/B/C 分组逻辑

```go
// slp-room: 绝对均匀的分组算法
func (s *recharge369EnterRoomEvent) getNextGroupType(ctx) int64 {
    rds := library.RedisClient(library.RedisPassive)
    groupVal := rds.Incr(ctx, "slp.recharge369EnterRoomEvent.next.group").Val()
    groupType := groupVal % 3 + 1  // 1=A, 2=B, 3=C
    return groupType
}
```

| 分组 | 弹窗策略 | 比例 |
|------|----------|------|
| A 组 | 不可见弹窗（对照组） | 1/3 |
| B 组 | 进房 60 秒后触发弹窗 | 1/3 |
| C 组 | 离房前触发弹窗/杀端后上线触发 | 1/3 |

### 4. 版本判断逻辑

```go
// slp-room: 根据客户端版本号决定使用哪个版本
versionNum := php2go.IP2long(userVersion.Version)

if versionNum < php2go.IP2long("5.55.0.0") {
    groupType = 0  // 老版本不参与
}

if versionNum >= php2go.IP2long("5.58.0.0") {
    castVersion = "v2"  // 新版本用 V2 逻辑
} else {
    castVersion = "v1"  // 老版本用 V1 逻辑
}
```

| 客户端版本 | cast_version | 档位配置 | 签到天数 |
|------------|--------------|----------|----------|
| < 5.55.0.0 | - | 不参与活动 | - |
| 5.55.0.0 ~ 5.57.x | v1 | 6/10/18/30 元 | 7 天 |
| >= 5.58.0.0 | v2 | 10/30/68/100 元 | 10 天 |

---

## 事件总线（NSQ）

### slp-room 发布的事件

| 事件名 | Topic | 触发时机 | 订阅方 |
|--------|-------|----------|--------|
| `recharge_user_group_enter_room` | slp.room.recommend.event | 用户进入白名单房间 | slp-go (UserGrowth.UserRoomEvent) |
| `recharge_user_group_leave_room` | slp.room.recommend.event | 用户离开房间 | slp-go (UserGrowth.UserRoomEvent) |

### 事件数据结构

```go
// enter_room 事件数据
{
    "uid": 123456,
    "rid": 789,
    "refer": "pretty_uid",
    "event": "enter_room"
}

// leave_room 事件数据
{
    "uid": 123456,
    "rid": 789,
    "event": "leave_room"
}
```

---

## RPC 调用关系

### slp-room → slp-go

| RPC 方法 | 用途 | 调用方 |
|----------|------|--------|
| `UserGrowth.UserRoomEvent` | 同步进房/离房事件 | slp-room → slp-go |
| `CommonCache.BatchBbcRoomRedpacketsWhitelist` | 批量判断白名单房间 | slp-room 内部 |
| `UserProfile.BatchCheckGs` | 批量判断主播身份 | slp-room 内部 |

### slp-go 内部 RPC

| RPC 方法 | 用途 |
|----------|------|
| `MoneyConsume.GetRequestId` | 获取发奖请求 ID |
| `GoodsSourceType.SendUserGoods` | 发放物品 |
| `UserProfile.Get` | 检查用户在线状态 |
| `RoomInfo.InRoom` | 检查用户是否在房间 |
| `Broadcast.PositionPluginChange` | 广播插件状态变更 |

---

## 配置管理

### slp-room 配置

| 配置项 | 说明 | 获取方式 |
|--------|------|----------|
| `bbc_room_redpackets_whitelist` | 房间白名单 (type=200) | `client.CommonCache.BatchBbcRoomRedpacketsWhitelist` |
| `cfg_id=106` | 369 路打卡团白名单业务 | 常量定义 |

### slp-go 配置

| 配置项 | 说明 | 文件 |
|--------|------|------|
| `recharge369GroupSliceV1` | V1 档位配置 | `app/consts/recharge_369_group_v1.go` |
| `recharge369GroupSliceV2` | V2 档位配置 | `app/consts/recharge_369_group_v2.go` |
| `GetRecharge369GroupGoods` | 奖励配置 | `app/consts/recharge_369_group_v2.go` |

---

## 插件系统（slp-room）

### PluginId = 16

369 充值用户分组插件，用于房间前端展示：

```go
// slp-room/consts/plugin.go
const (
    PluginIdRecharge369UserGroup = 16  // 369 充值用户分组
)
```

**插件状态变更**：
```go
// 用户领完最高档后，删除插件
messageData := &pb.RoomRoomPositionPluginItemStageInfoMessage{
    Data: &pb.ResRoomPositionPluginItem{
        PluginId:       16,
        PluginShowType: "delete",
    },
}
broadcast := client.NewBroadcastClient(client.BroadcastRooms(inRid))
_, _ = broadcast.PositionPluginChange(ctx, messageData)
```

---

## 跨项目问题排查

### 问题 1: 用户进房后没有创建记录

**排查步骤**：
1. slp-room 日志：检查 `handleXsRoom369GroupUser` 是否执行
2. 检查房间是否在白名单：`BatchBbcRoomRedpacketsWhitelist(rid)`
3. 检查用户是否主播：`BatchCheckGs(uid)`
4. 检查进房来源：`refer` 是否在允许列表
5. 检查客户端版本：`version >= 5.55.0.0`

### 问题 2: 充值后没有发奖

**排查步骤**：
1. slp-go 日志：检查 `RechargeType369Callback` 是否执行
2. 检查数据库记录是否存在：`SELECT * FROM xs_room_369_group_user WHERE uid=?`
3. 检查充值金额是否更新：`recharge_rmb` 字段
4. 检查用户在线状态：在线才触发自动发奖
5. 检查 `GetRecharge369UserGroupDay` 返回值

### 问题 3: V1/V2 版本混乱

**排查步骤**：
1. 检查 `cast_version` 字段值
2. 检查客户端版本号
3. 检查 `GetRechargeGroup369Object` 路由逻辑
4. 确认奖励配置是否匹配版本

---

## 相关文件索引

### slp-room

| 文件 | 说明 |
|------|------|
| `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` | 进房事件处理 |
| `cmd/internal/room_recommend_more/event/recharge_369_group_leave_room.go` | 离房事件处理 |
| `app/service/recharge/recharge369.go` | 弹窗判断逻辑 |
| `app/domain/xs_room_369_group_user.go` | Domain 层访问 |
| `consts/room_recommend_more.go` | 事件常量定义 |
| `consts/plugin.go` | 插件 ID 定义 |

### slp-go

| 文件 | 说明 |
|------|------|
| `app/service/recharge/recharge369.go` | 版本路由 |
| `app/service/recharge/recharge369V1.go` | V1 版本实现 |
| `app/service/recharge/recharge369V2.go` | V2 版本实现 |
| `app/consts/recharge_369_group_v1.go` | V1 奖励配置 |
| `app/consts/recharge_369_group_v2.go` | V2 奖励配置 |
| `app/api/recharge.go` | API 接口 |

---

## 文档导航

- **[slp-room 视角](./slp-room.md)** - slp-room 项目内的实现细节
- **[slp-go 单项目业务](../../projects/slp-go/08-business-369-recharge.md)** - slp-go 项目内的核心业务逻辑

---

**版本**: 1.0 | **更新**: 2026-04-05
