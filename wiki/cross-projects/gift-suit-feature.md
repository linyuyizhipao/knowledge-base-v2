---
id: gift-suit-feature
label: 大额装扮套
source: curated/cross-projects/gift-suit/gift-suit-feature.md
business: gift-suit
compiled: 2026-04-25
links:
  - white-horse-love-design
---

# 大额装扮套

> 用户在商业房送大额礼物 → 触发装扮套发放（装扮、房间边框、角标）

## 触发流程

```
用户送礼 → GetRoomFrameSuitList 获取奖品 → WhiteGiftIdMap 校验 → 商业房判断 → Redis 锁 → 事务写入 → RPC 发放装扮
```

## 配置结构

| 配置 | 文件 | 说明 |
|------|------|------|
| WhiteGiftIdMap | `app/consts/gift_suit.go` | 装扮套礼物白名单 |
| RoomFrameSuitList | `app/consts/gift_suit.go` | 按价格档位配置奖品 |
| roomFrameSuitGiftIdMap | `app/consts/gift_suit.go` | 按礼物 ID 配置奖品（优先级更高） |

## 奖品查找优先级

```
GetRoomFrameSuitList(giftId, price):
  1. 先查 roomFrameSuitGiftIdMap[giftId]
  2. 再查 RoomFrameSuitList[price]
  3. 都没有 → 返回空
```

## GoodsFrame 结构

```go
type GoodsFrame struct {
    SourceType uint32  // 1=装扮, 2=房间边框, 3=角标
    SourceId   uint32  // 具体资源 ID
    Seconds    int64   // 有效时长（秒）
}
```

## 核心文件

| 文件 | 路径 |
|------|------|
| 配置常量 | `app/consts/gift_suit.go` |
| 发放服务 | `app/service/giftsuit/suitgift.go` |
| 面板展示 | `app/service/gift/panel.go` |

## 数据表

| 表 | 用途 |
|----|------|
| xs_room_frame_skin_wear_cfg | 房间边框/角标穿戴配置 |
| xs_user_suit_gift_packet_log | 装扮套发放日志（防重复发放） |

## 添加新礼物步骤

1. 在 WhiteGiftIdMap 中添加新礼物 ID
2. 确定价格档位或在 roomFrameSuitGiftIdMap 中添加独立配置
3. 如有独立名称，在 alisaGiftIdSuitGroupName 中添加