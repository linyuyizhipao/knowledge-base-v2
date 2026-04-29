---
id: slp-go-369-recharge
label: slp-go 369元观光团充值业务
source: curated/projects/slp-go/08-business-369-recharge.md
project: slp-go
role: business
compiled: 2026-04-25
tags:
  - 369-recharge
  - recharge
links:
  - slp-go-structure
  - slp-go-event-capabilities
---

# 369 元观光团充值业务（slp-go 单项目视角）

> SLP 平台充值营销活动 - slp-go 项目内的核心业务逻辑

## 业务概述

369 元观光团是一个**充值档位累计 + 签到领奖**的营销活动。

| 特性 | V1 版本 | V2 版本 |
|------|---------|---------|
| 充值档位 | 6/10/18/30 元 | 10/30/68/100 元 |
| 签到天数 | 7 天 | 10 天 |
| 最高奖励 | 7 天签到 | 10 天签到（6 位靓号） |

**版本路由**：通过 `cast_version` 字段控制，`GetRechargeGroup369Object()` 根据版本返回不同实现。

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
            // 可以领取下一档
        }
    }
    
    return alreadyMaxDay + 1
}
```