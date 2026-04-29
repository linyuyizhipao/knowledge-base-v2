# 大额装扮套 - 需求与设计文档

> 用户在商业房送大额礼物 → 触发装扮套发放（装扮、房间边框、角标）

**版本**: 1.0 | **最后更新**: 2026-04-13

---

## 一、业务概述

用户在商业房（property=business）送特定大额礼物时，系统自动向送礼者和接收者发放装扮套奖励，包括：
- **装扮**（SourceType=1）：用户头像/角色装扮皮肤，有时效
- **房间边框**（SourceType=2）：房间边框皮肤，有时效
- **房间角标**（SourceType=3）：房间角标装饰，有时效

---

## 二、核心配置文件

**文件**: `app/consts/gift_suit.go`（slp-go 项目）

### 2.1 WhiteGiftIdMap - 装扮套礼物白名单

只有在此白名单中的礼物 ID 才会触发装扮套发放。定义了两套配置：

**Dev 环境**（包级别 var）:

| Gift ID | 说明 |
|---------|------|
| 210853 | - |
| 775 | - |
| 210926 | - |
| 211027 | - |
| 316 | 告白大厦 |
| 211360 (Env) | 支持新的一个礼物赠送装扮套 |

**Prod 环境**（init() 中覆盖）:

| Gift ID | 说明 |
|---------|------|
| 853 | 步步生花 |
| 210775 | 梦中情人 |
| 316 | 告白大厦 |
| 210888 | 如鲸向海 |
| 210989 | 星河灿烂 |
| 210990 | 挚爱永恒 |
| 211176 | 夜店之王 |
| 210777 | 亚特兰蒂斯 |
| 211177 | 冰封王座 |
| 211854 | 支持新的一个礼物赠送装扮套 |
| 211465-211468 | 甜蜜相册 15~16 等级礼物 |

### 2.2 RoomFrameSuitList - 按价格档位配置奖品

按礼物**价格**映射可获得的奖品列表：

| 价格档位 | 装扮（天数） | 边框/角标 |
|----------|-------------|-----------|
| 1314 | 3个装扮 × 1天 | 无 |
| 5200 | 3个装扮 × 5天 | 无 |
| 3344 | 3个装扮 × 3天 | 无 |
| 9999 | 3个装扮 × 7天 | 边框×1天 + 角标×1天 |
| 13140 | 3个装扮 × 7天 | 边框×1天 + 角标×1天 |

Dev 和 Prod 使用不同的 SourceId（dev: 600系列, prod: 900系列）。

### 2.3 roomFrameSuitGiftIdMap - 按礼物 ID 配置奖品（优先级更高）

某些特定礼物 ID 有独立的奖品配置，优先于价格档位匹配：

```go
Env(211854, 211360): {
    // 4个装扮 × 7天
    {SourceType: 1, SourceId: Env(2070, 101), Seconds: 7天},
    {SourceType: 1, SourceId: Env(2071, 2099), Seconds: 7天},
    {SourceType: 1, SourceId: Env(2072, 2076), Seconds: 7天},
    {SourceType: 1, SourceId: Env(2069, 2079), Seconds: 7天},
    // 边框 × 1天 + 角标 × 1天
    {SourceType: 2, SourceId: 3, Seconds: 1天},
    {SourceType: 3, SourceId: 3, Seconds: 1天},
}
```

### 2.4 套装名称配置

| 变量 | 按价格 | 按礼物ID |
|------|--------|----------|
| `AlisaGiftPriceSuitGroupName` | 1314→King皇冠, 5200→鸾凤和鸣, 3344→赛博朋克, 9999/13140→凤冠霞披 | - |
| `alisaGiftIdSuitGroupName` | - | 211854→人鱼传说 |

---

## 三、核心数据结构

### GoodsFrame

```go
type GoodsFrame struct {
    SourceType uint32  // 1=装扮, 2=房间边框, 3=角标
    SourceId   uint32  // 具体资源 ID
    Seconds    int64   // 有效时长（秒）
}
```

### 奖品查找优先级

```
GetRoomFrameSuitList(giftId, price):
  1. 先查 roomFrameSuitGiftIdMap[giftId]  → 按礼物 ID 精确匹配
  2. 再查 RoomFrameSuitList[price]        → 按价格档位匹配
  3. 都没有 → 返回空
```

---

## 四、发放流程

### 触发入口

**文件**: `app/service/giftsuit/suitgift.go` - `giftSuitSrv.Send()`

```
用户送礼
  ↓
suitgift.Send(ctx, toUids, data, isReissue...)
  ↓
① GetRoomFrameSuitList(giftId, price) 获取奖品列表
  ↓
② WhiteGiftIdMap[giftId] 校验白名单（补发可跳过）
  ↓
③ roomInfo.GetProperty() == "business" 校验商业房
  ↓
④ Redis 锁: giftSuitSrv.Send.suit.locker.rid.{rid}
  ↓
⑤ 事务写入:
   - xs_room_frame_skin_wear_cfg (边框/角标)
   - xs_user_suit_gift_packet_log (防重日志)
  ↓
⑥ sendPretend() → RPC 调用 MoneyConsume.SendGoods 发放装扮
```

### 面板展示入口

**文件**: `app/service/gift/panel.go` - `GetContentZone()`

仅在商业房 + room 类型礼物 + 白名单礼物时，展示装扮套宣传面板。

---

## 五、关键表

| 表 | 用途 |
|----|------|
| `xs_room_frame_skin_wear_cfg` | 房间边框/角标穿戴配置（记录有效期、穿戴状态） |
| `xs_user_suit_gift_packet_log` | 装扮套发放日志（requestId 去重，防重复发放） |

---

## 六、添加新礼物的步骤

1. 在 `WhiteGiftIdMap` 中添加新礼物 ID（dev 和 prod 都要加）
2. 确定价格档位或在 `roomFrameSuitGiftIdMap` 中添加独立配置
3. 如果有独立名称，在 `alisaGiftIdSuitGroupName` 中添加
4. 如需新的边框/角标资源，在 `RoomFrameRecordsMap` / `RoomCornerRecordsMap` 中添加

---

## 七、相关文件

| 文件 | 路径 |
|------|------|
| 配置常量 | `app/consts/gift_suit.go` |
| 发放服务 | `app/service/giftsuit/suitgift.go` |
| 面板展示 | `app/service/gift/panel.go` |
| Redis Key | `RdsRoomFrameSkin = "slp.room.frame.skin.rid.%d"` |
