---
id: slp-room-structure
label: slp-room 项目结构
source: curated/projects/slp-room/01-structure.md
project: slp-room
compiled: 2026-04-25
links:
  - slp-room-architecture
  - slp-room-event-capabilities
---

# slp-room 项目结构

## 目录树

| 目录 | 说明 | 数量 |
|------|------|------|
| `main.go` | HTTP 服务入口 | 1 |
| `app/` | HTTP 应用主代码 | - |
| `app/api/` | HTTP 请求处理器 | 18+ |
| `app/busi/` | 业务逻辑层 | 60+ |
| `app/service/` | 服务层 | 97 |
| `app/dao/` | 数据访问层 | 500+ |
| `app/model/` | 数据模型 | 500+ |
| `app/pb/` | Protobuf 定义 | 750+ |
| `app/query/` | 查询组合层 | 103 |
| `app/cachemodel/` | 缓存模型 | 14 |
| `cmd/internal/` | CMD 任务实现 | 100+ |
| `rpc/server/` | RPC 服务实现 | - |
| `consts/` | 常量定义 | 36 |
| `library/` | 基础设施库 | 33 |
| `module/` | 模块封装 | 15 |
| `plugin/` | 插件系统 | 17 |
| `proto/` | Protobuf 源文件 | 782 |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `main.go` | `./bin/http` |
| CMD | `cmd/main.go` | `./bin/cmd --name=<module>` |

## 模块引用关系

| 上层 | 下层 | 说明 |
|------|------|------|
| `app/api` | `app/busi`, `app/service` | API 调用 Busi/Service |
| `app/busi` | `app/dao`, `library` | Busi 调用 DAO |
| `app/service` | `app/dao`, `library` | Service 调用 DAO |
| `app/dao` | `app/model` | DAO 调用 Model |

**禁止调用**:
- 任何层不可调用 `app/api`
- `library` 不可调用 `app/busi/app/service`

## CMD 模块 (事件消费者)

| 模块 | Topic | 说明 |
|------|-------|------|
| `room_recommend_more/` | `slp.room.recommend.more` | 房间推荐 |
| `grabmic/` | `grabmic.TopicGrabMic` | 抢麦事件 |
| `cplink/` | `cplink.TopicCplinkV2` | CP 连线 |
| `room_pk/` | `room.pk.topic` | 房间 PK |
| `big_brother/` | `slp.big.brother` | 大哥房间 |
| `enter/` | `xs.room.enter` | 房间进入 |
| `auction/` | `slp.auction` | 拍卖事件 |

## 与 slp-go 对比

| 维度 | slp-go | slp-room |
|------|--------|----------|
| 服务类型 | HTTP + RPC + CMD | HTTP + CMD |
| API 模块 | 160+ | 18+ |
| CMD 模块 | 219 | 100+ |
| DAO 文件 | 968 | 500+ |
| 核心功能 | 用户、关系、礼物 | 房间、麦位、PK |
| Busi 层 | 无 | 有独立 Busi 层 |