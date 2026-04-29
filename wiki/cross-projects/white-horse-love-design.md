---
id: white-horse-love-design
label: 白马挚爱装扮套配置变更
source: curated/cross-projects/gift-suit/2026-04-13-white-horse-love-design.md
business: gift-suit
compiled: 2026-04-25
links:
  - gift-suit-feature
---

# 白马挚爱装扮套 - 配置变更设计

> 赠送「白马挚爱」礼物（ID: 212483，520000 钻），获得白马挚爱装扮套 x 5 天

## 变更文件

唯一文件: `app/consts/gift_suit.go` (slp-go 项目)

## 变更点

### 1. WhiteGiftIdMap 添加白名单

```go
// Dev 环境
212483: true, // 白马挚爱

// Prod 环境 init() 中
212483: true, // 白马挚爱
```

### 2. roomFrameSuitGiftIdMap 添加独立配置

```go
212483: {
    {SourceType: 1, SourceId: 2822, Seconds: 5天}, // 头像框
    {SourceType: 1, SourceId: 2824, Seconds: 5天}, // 气泡框
    {SourceType: 1, SourceId: 2826, Seconds: 5天}, // 入场横幅
}
```

### 3. alisaGiftIdSuitGroupName 添加套装名称

```go
212483: "白马挚爱"
```

## 不需要的变更

| 项目 | 原因 |
|------|------|
| RoomFrameSuitList | 走礼物 ID 优先匹配 |
| 服务层代码 | suitgift.go 和 panel.go 无需修改 |
| RoomFrameRecordsMap | SourceType=1（装扮）通过 RPC 直接发放 |

## 验证项

1. `go build ./app/consts/` 编译通过
2. `GetRoomFrameSuitList(212483, 520000)` 返回 3 个 GoodsFrame
3. `WhiteGiftIdMap[212483]` 为 true