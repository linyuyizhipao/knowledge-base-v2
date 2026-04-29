---
id: fly-chess-overview
label: 飞行棋游戏功能
source: curated/cross-projects/fly-chess/overview.md
business: fly-chess
compiled: 2026-04-25
links: []
---

# 飞行棋游戏功能

> 飞行棋游戏互动，涉及多个服务模块协作

## 业务流程

| 步骤 | 项目 | 职责 | 核心模块 |
|------|------|------|----------|
| 前端请求 | slp-php | 房间配置接口 | `app/controllers/RoomController.php` |
| 网关转发 | slp-gateway | 路由转发 | `rpc/server/internal/roommanager/fly_chess.go` |
| 游戏逻辑 | slp-room | 飞行棋核心游戏逻辑 | `app/service/fly_chess/` |
| 部署配置 | slp-go | 服务部署 | `deploy/helm/cmd/cmds/` |

## 技术架构

| 层级 | slp-room | slp-gateway | slp-php |
|------|----------|-------------|---------|
| Service | `app/service/fly_chess/` | `roommanager/fly_chess.go` | `RoomController.php` |
| Protocol | `chatroom_fly_chess.pb.go` | `rpc_room_game.proto` | `RpcRoomProxy.php` |
| Config | - | `room.gatemanager.conf` | `xs.room.conf` |

## PR 参考

| PR | 项目 |
|----|------|
| slp-room#584 | 飞行棋游戏核心服务实现 |
| slp-gateway#82 | 飞行棋网关转发配置 |
| slp-go#2186 | 飞行棋相关部署配置 |
| slp-php#1198 | 房间配置新接口实现 |

## 数据表

| 表 | 说明 |
|----|------|
| xs_chatroom_fly_chess | 飞行棋房间核心数据 |
| xs_fly_chess_player_status | 飞行棋玩家状态 |

## 跨项目问题排查

1. 检查 slp-php 接口是否正常
2. 验证 gateway 路由配置
3. 确认 slp-room 游戏逻辑
4. 检查 slp-go 部署状态