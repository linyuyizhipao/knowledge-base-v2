---
id: slp-room-architecture
label: slp-room 架构分层
source: curated/projects/slp-room/02-architecture.md
project: slp-room
compiled: 2026-04-25
links:
  - slp-room-structure
  - slp-room-event-capabilities
---

# slp-room 架构分层

## 分层架构

| 层级 | 位置 | 职责 |
|------|------|------|
| API | `app/api/` | 请求参数解析、参数校验、响应格式封装 |
| Busi | `app/busi/` | 复杂业务逻辑、跨模块业务编排、业务规则校验 |
| Service | `app/service/` | 核心业务逻辑、事务管理、跨 DAO 协调 |
| DAO | `app/dao/` | 数据库 CRUD、单表查询、缓存读写 |
| Model | `app/model/` | 数据模型定义、JSON/DB 映射 |
| CacheModel | `app/cachemodel/` | Redis 缓存封装、缓存更新策略 |

## 层间调用规则

| 层级 | 可调用 | 禁止调用 |
|------|--------|----------|
| API | Busi, Service, DAO, Model | - |
| Busi | Service, DAO, Model, Library | API, 其他 Busi |
| Service | DAO, Model, Library | API, Busi |
| DAO | Model | API, Service, Library |
| Model | 仅内部 | 所有上层 |

## 模块统计

| 层级 | 目录 | 数量 |
|------|------|------|
| API | `app/api/` | 18+ |
| Busi | `app/busi/` | 60+ |
| Service | `app/service/` | 97 |
| DAO | `app/dao/` | 500+ |
| CMD | `cmd/internal/` | 100+ |

## API 模块

| 模块 | 路由前缀 | 说明 |
|------|---------|------|
| Room | `/go/room/` | 房间核心 API |
| Mic | `/go/room/mic/` | 麦位操作 |
| Action | `/go/room/action/` | 进房/离开/踢人 |
| Gift | `/go/room/gift/` | 礼物打赏 |
| PK | `/go/room/pk/` | 房间 PK |
| GrabMic | `/go/room/grabmic/` | 抢唱玩法 |
| Auction | `/go/room/auction/` | 拍卖玩法 |
| CPLink | `/go/room/cplink/` | CP 连线 |

## Busi 模块

| 模块 | 说明 |
|------|------|
| RoomState | 房间状态管理 |
| RoomUser | 房间用户管理 |
| RoomGift | 房间礼物 |
| RoomHistory | 房间历史 |
| RoomOnline | 房间在线人数 |
| RoomTransfer | 房间转让 |

## 与 slp-go 对比

| 维度 | slp-go | slp-room |
|------|--------|----------|
| 架构 | API → Service → DAO | API → Busi → Service → DAO |
| Busi 层 | 无独立 Busi 层 | 有独立 Busi 层 |
| Query 层 | 160 文件 | 103 文件 |
| CacheModel | 分散在 Service | 独立 cachemodel 目录 |

## 相关知识

- [[projects/slp-room/01-structure]]
- [[patterns/architecture-layered-standard]]
