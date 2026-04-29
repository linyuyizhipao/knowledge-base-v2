# 白马挚爱装扮套 - 配置变更设计

**版本**: 1.0 | **日期**: 2026-04-13

---

## 需求

赠送「白马挚爱」礼物（ID: 212483，520000 钻），送礼方和收礼方均获得白马挚爱装扮套 × 5 天。

---

## 变更文件

**唯一文件**: `app/consts/gift_suit.go`（slp-go 项目）

---

## 变更点 1: WhiteGiftIdMap 添加白名单

### Dev 环境（第 288 行 var 块）

```go
WhiteGiftIdMap = map[uint32]bool{
    210853:              true,
    775:                 true,
    210926:              true,
    211027:              true,
    316:                 true,
    Env(211854, 211360): true,
    212483:              true, // 白马挚爱
}
```

### Prod 环境（第 431 行 init() 中）

```go
WhiteGiftIdMap = map[uint32]bool{
    // ... 现有配置 ...
    211854: true,
    212483: true, // 白马挚爱

    211465: true,
    211466: true,
    211467: true,
    211468: true,
}
```

---

## 变更点 2: roomFrameSuitGiftIdMap 添加独立奖品配置

在 `roomFrameSuitGiftIdMap` 中新增 212483 的条目：

```go
roomFrameSuitGiftIdMap = map[uint32][]GoodsFrame{
    Env(211854, 211360): {
        // ... 现有配置 ...
    },
    212483: { // 白马挚爱
        {
            SourceType: 1,
            SourceId:   2822, // 头像框
            Seconds:    24 * 3600 * 5,
        },
        {
            SourceType: 1,
            SourceId:   2824, // 气泡框
            Seconds:    24 * 3600 * 5,
        },
        {
            SourceType: 1,
            SourceId:   2826, // 入场横幅
            Seconds:    24 * 3600 * 5,
        },
    },
}
```

注意：此 map 在 dev 和 init() 中都需要添加。init() 中的版本会覆盖 dev 版本（prod 环境），所以两个地方都要加。

---

## 变更点 3: alisaGiftIdSuitGroupName 添加套装名称

```go
alisaGiftIdSuitGroupName = map[uint32]string{
    Env(211854, 211360): "人鱼传说",
    212483:              "白马挚爱",
}
```

---

## 变更点 4: RoomFrameRecordsMap / RoomCornerRecordsMap 是否需要新增？

不需要。现有代码中 SourceId=2822/2824/2826 只在 `roomFrameSuitGiftIdMap` 中引用，不需要在 RoomFrameRecordsMap（边框展示配置）或 RoomCornerRecordsMap（角标展示配置）中添加，因为这三个物品都是 SourceType=1（装扮），通过 RPC `SendGoods` 直接发放。

---

## 不需要的变更

| 项目 | 原因 |
|------|------|
| RoomFrameSuitList | 不需要新增价格档位，走礼物 ID 优先匹配 |
| 服务层代码 | suitgift.go 和 panel.go 无需修改，自动支持新配置 |

---

## 验证

1. `go build ./app/consts/` 编译通过
2. 确认 `GetRoomFrameSuitList(212483, 520000)` 返回 3 个 GoodsFrame
3. 确认 `GetAlisaGiftPriceSuitGroupName(212483, 520000)` 返回 "白马挚爱"
4. 确认 `WhiteGiftIdMap[212483]` 为 true
