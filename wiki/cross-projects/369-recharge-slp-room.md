---
id: 369-recharge-slp-room
label: 369 元观光团 - slp-room 视角
source: curated/cross-projects/369-recharge/slp-room.md
business: 369-recharge
compiled: 2026-04-25
links:
  - 369-recharge-overview
---

# 369 元观光团 - slp-room 视角

> 房间服务在 369 业务中的职责和实现

## 核心职责

| 职责 | 核心文件 |
|------|----------|
| 进房事件捕获 | `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` |
| 离房事件捕获 | `cmd/internal/room_recommend_more/event/recharge_369_group_leave_room.go` |
| 白名单房间判断 | `app/service/plugin/service.go` |
| A/B/C 分组 | RSA 均匀分配 `groupVal % 3 + 1` |
| 弹窗触发判断 | `app/service/recharge/recharge369.go` |

## 进房判断流程

```
用户进房 → 白名单房间判断 → 主播身份排除 → 进房来源判断 → 版本判断 → A/B/C 分组 → 插入记录 → 发布 NSQ
```

**有效进房来源**:
- `pretty_uid` - 搜用户靓号踩房
- `SearchScreen:UserPage` - 搜用户 UID+ 进用户主页进房

## 关键代码位置

| 文件 | 说明 |
|------|------|
| `cmd/internal/room_recommend_more/event/recharge_369_group_enter_room.go` | 进房事件处理 |
| `cmd/internal/room_recommend_more/event/recharge_369_group_leave_room.go` | 离房事件处理 |
| `app/service/recharge/recharge369.go` | 弹窗判断逻辑 |
| `app/domain/xs_room_369_group_user.go` | Domain 层访问 |
| `consts/room_recommend_more.go` | 事件常量定义 |

## RPC 调用

| RPC 方法 | 用途 |
|----------|------|
| `CommonCache.BatchBbcRoomRedpacketsWhitelist` | 白名单房间判断 |
| `UserProfile.BatchCheckGs` | 主播身份判断 |
| `UserGrowth.UserRoomEvent` | 同步进房/离房事件到 slp-go |