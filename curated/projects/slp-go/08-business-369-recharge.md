# 369 元观光团充值业务（slp-go 单项目视角）

> SLP 平台充值营销活动 - slp-go 项目内的核心业务逻辑

**跨项目全景**: [`../../cross-projects/369-recharge/overview.md`](../../cross-projects/369-recharge/overview.md)  
**slp-room 视角**: [`../../cross-projects/369-recharge/slp-room.md`](../../cross-projects/369-recharge/slp-room.md)

---

## 业务概述

369 元观光团是一个**充值档位累计 + 签到领奖**的营销活动。

| 特性 | V1 版本 | V2 版本 |
|------|---------|---------|
| 充值档位 | 6/10/18/30 元 | 10/30/68/100 元 |
| 签到天数 | 7 天 | 10 天 |
| 最高奖励 | 7 天签到 | 10 天签到（6 位靓号） |

**版本路由**：通过 `cast_version` 字段控制，`GetRechargeGroup369Object()` 根据版本返回不同实现。

---

## 数据表结构

### xs_room_369_group_user

| 字段 | 类型 | slp-go 写入 | 说明 |
|------|------|-----------|------|
| `recharge_rmb` | uint32 | ✅ | 累计充值金额（元） |
| `first_recharge_time` | uint32 | ✅ | 首次充值时间 |
| `day_1` ~ `day_10` | uint32 | ✅ | 每天领奖时的充值档位 |
| `last_send_time` | uint32 | ✅ | 最近一次领取奖励时间 |
| `extra` | string | ✅ | 扩展字段（JSON，记录已发物品） |
| `uid` | uint32 | - | 用户 ID（查询条件） |
| `cast_version` | string | - | 版本：v1/v2（slp-room 写入） |

---

## 核心流程（slp-go 负责）

### 1. 充值回调

```go
// app/service/recharge/recharge369V2.go
func (serv *rechargeGroup369V2) RechargeType369Callback(ctx, req *pb.ReqUserRechargeFn) error {
    enterUserRecord := domain.Room369GroupUser.GetRoom369GroupUser(ctx, req.GetUid())
    
    rmb := req.GetTotalMoney() / 100
    
    // 更新累计充值金额
    dataMap := g.Map{
        "recharge_rmb": gdb.Raw(fmt.Sprintf("recharge_rmb+%d", rmb)),
        "update_time":  time.Now().Unix(),
    }
    
    // 记录首次充值时间
    if enterUserRecord.GetRechargeRmb() == 0 {
        dataMap["first_recharge_time"] = time.Now().Unix()
    }
    
    dao.XsRoom369GroupUser.Data(dataMap).Where("uid=?", req.GetUid()).Update()
    
    // 触发在线发奖
    _ = serv.RechargeType369Online(ctx, req.GetUid(), enterUserRecord)
}
```

### 2. 在线发奖

```go
func (serv *rechargeGroup369V2) RechargeType369Online(ctx, uid uint32, user *pb.EntityXsRoom369GroupUser) error {
    day := serv.GetRecharge369UserGroupDay(user)
    if day <= 0 {
        return nil
    }
    
    // 检查用户在线状态（在线才发奖）
    userProfile, _ := client.UserProfile.Get(ctx, uid, []string{"uid", "online_status"})
    if userProfile == nil || userProfile.GetOnlineStatus() > 0 {
        return nil
    }
    
    return serv.sendRechargeType369GroupReward(ctx, uid, day, user)
}
```

### 3. 天数计算

```go
func (serv *rechargeGroup369V2) GetRecharge369UserGroupDay(user *pb.EntityXsRoom369GroupUser) uint32 {
    // 获取已领取的最大天数
    alreadyMaxDay := max(day_1...day_10 where value > 0)
    
    if alreadyMaxDay == 0 {
        return 1 // 首次领取
    }
    
    if alreadyMaxDay == 10 {
        if recharge369Tiers > user.GetDay_10() {
            return 10 // 升档补发
        }
        return 0
    }
    
    // 升档情况：当天继续领
    if yesterday == today && recharge369Tiers > alreadyMaxDayVal {
        return alreadyMaxDay
    }
    
    // 新的一天
    if yesterday != today {
        return alreadyMaxDay + 1
    }
    
    return 0
}
```

### 4. 发奖核心逻辑

```go
func (serv *rechargeGroup369V2) sendRechargeType369GroupReward(ctx, uid, day uint32, user *pb.EntityXsRoom369GroupUser) error {
    // 1. 参数校验
    if day < 1 || day > 10 { return gerror.New("非法") }
    
    // 2. 检查是否已领
    if dayAwardMap[day] > 0 && recharge369Tiers <= dayAwardMap[day] {
        return nil
    }
    
    // 3. 去重：过滤已发物品
    extraMap := json.Unmarshal(user.GetExtra())
    for award in allAwards {
        extraKey := fmt.Sprintf("%d-%d", award.SourceType, award.GoodsId)
        if gconv.Int(extraMap[extraKey]) <= 0 {
            sendGoodsAwards.append(award)
            extraMap[extraKey] = time.Now().Unix()
        }
    }
    
    // 4. 更新数据库（乐观锁）
    fieldName := fmt.Sprintf("day_%d", day)
    dao.XsRoom369GroupUser.Data(g.Map{
        fieldName: recharge369Tiers,
        "last_send_time": time.Now().Unix(),
        "extra": tools.ToJsonString(extraMap),
    }).Where(fmt.Sprintf("uid=? and %s<%d", fieldName, recharge369Tiers), uid).Update()
    
    // 5. 发放物品
    domain.GoodsSourceType.SendUserGoods(ctx, requestId, userGoodsList)
    
    // 6. 发送弹窗通知
    domain.SendRoomPointImMessageV2(ctx, uid, "recharge_369_user_group", content)
}
```

---

## 奖励配置（V2）

### 档位配置

```go
// app/consts/recharge_369_group_v2.go
var recharge369GroupSliceV2 = []uint32{10, 30, 68, 100}
```

| 档位 | 签到天数 | 描述 |
|------|----------|------|
| 10 元 | 3 天 | 普通档 |
| 30 元 | 5 天 | 高级档 |
| 68 元 | 7 天 | 豪华档 |
| 100 元 | 10 天 | 典藏档（6 位靓号） |

### 奖励类型

| SourceType | 说明 | 示例 |
|------------|------|------|
| `Badge` | 勋章 | 9057 |
| `Cid` | 装扮 | 100861 |
| `UserPretty` | 7 位靓号 | 随机 |
| `UserPrettySix` | 6 位靓号 | V2 典藏档第 10 天 |
| `RoomEmoji` | 表情包 | 10005 |
| `PretendFragment` | 装扮碎片 | V2 第 9 天 |

### 100 元档第 10 天奖励示例

```go
"100-10": {
    {SourceType: UserPrettySix, Num: 1, Seconds: 7*86400, Param: {"group_name": "recharge_369_six"}},
    {SourceType: Cid, GoodsId: 100568, Seconds: 7*86400},
}
```

---

## API 接口

### 领取 369 奖励

```
POST /go/slp/recharge/recharge369
```

```go
// app/api/recharge.go
func (m *rechargeApi) Recharge369(r *ghttp.Request) {
    req := &query.GetRecharge369AwardReq{}
    uid := service.Context.Get(ctx).User.UID
    
    _, err := recharge.Serv.RechargeType369(ctx, uid, req.PopDay)
    
    response.Output(r, &pb.Recharge369Rsp{Success: true})
}
```

---

## 关键业务规则

### 1. 升档补发
```go
if yesterday == today && recharge369Tiers > alreadyMaxDayVal {
    return alreadyMaxDay // 当天继续领，不增加天数
}
```

### 2. 防重复领取
```go
extraKey := fmt.Sprintf("%d-%d", award.SourceType, award.GoodsId)
if gconv.Int(extraMap[extraKey]) > 0 {
    return // 已发过，过滤
}
```

### 3. 同一天限制
```go
if dayAwardMap[day] == 0 && yesterday == today {
    return // 拒绝领取
}
```

### 4. 数据库乐观锁
```go
WHERE uid=? AND day_{day} < recharge369Tiers
// 只允许小档位往大档位更新
```

---

## 扩展字段 (extra)

JSON 格式，记录已发放的物品：

```json
{
  "1-100861": 1712304000,  // SourceType=1(Cid), GoodsId=100861
  "5-9057": 1712304000,    // SourceType=5(Badge), GoodsId=9057
  "10-10005": 1712390400   // SourceType=10(RoomEmoji), GoodsId=10005
}
```

---

## 常见问题

### Q1: 用户充值后没有立即发奖？

**原因**：用户在线时才触发自动发奖。

**解决**：用户下次上线时补发。

### Q2: V1/V2 版本如何路由？

```go
func GetRechargeGroup369Object(ctx, uid, user) (any, string) {
    if user.GetCastVersion() == "v2" {
        return NewRechargeGroup369V2(), "v2"
    }
    return NewRechargeGroup369V1(), "v1"
}
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `app/service/recharge/recharge369.go` | 版本路由 |
| `app/service/recharge/recharge369V1.go` | V1 实现 |
| `app/service/recharge/recharge369V2.go` | V2 实现 |
| `app/consts/recharge_369_group_v1.go` | V1 配置 |
| `app/consts/recharge_369_group_v2.go` | V2 配置 |
| `app/api/recharge.go` | API 接口 |

---

## 事件处理

369 充值业务涉及的事件处理：

| 事件类型 | 来源 | 处理方式 | 位置 |
|---------|------|---------|------|
| 充值回调 | 支付系统 | RPC `UserGrowth.UserRechargeFn` → `RechargeEvent` 观察者模式 | `rpc/server/internal/user_growth/user_recharge_fn.go` |
| 进房事件 | slp-room | RPC `UserGrowth.UserRoomEvent` → 触发在线发奖 | 同上 |

👉 **事件处理通用规范**: [`../../../patterns/cmd-module-standard.md`](../../../patterns/cmd-module-standard.md)  
👉 **NSQ 使用规范**: [`../../../patterns/nsq-usage.md`](../../../patterns/nsq-usage.md)

---

**版本**: 2.0 | **更新**: 2026-04-05
