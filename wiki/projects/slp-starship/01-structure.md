---
id: slp-starship-structure
label: slp-starship 项目结构
source: curated/projects/slp-starship/01-structure.md
project: slp-starship
compiled: 2026-04-25
links:
  - slp-starship-event-capabilities
---

# slp-starship 项目结构

## 目录树

| 目录 | 说明 | 数量 |
|------|------|------|
| `main.go` | HTTP 服务入口 | 1 |
| `app/` | HTTP 应用主代码 | - |
| `app/api/` | HTTP 请求处理器 | 28 |
| `app/service/` | 服务层 | 14 |
| `app/dao/` | 数据访问层 | 104 |
| `app/model/` | 数据模型 | 108 |
| `app/pb/` | Protobuf 定义 | 149 |
| `app/query/` | 查询组合层 | 14 |
| `cmd/internal/` | CMD 任务实现 | 7 |
| `commonsrv/` | 共享服务模块 | 5 |
| `consts/` | 常量定义 | 31 |
| `library/` | 基础设施库 | 28 |
| `proto/` | Protobuf 源文件 | 145 |

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `main.go` | `./bin/http` |
| CMD | `cmd/main.go` | `./bin/cmd --name=<module>` |

## 路由前缀

所有路由统一前缀：`/go/starship/`

## 模块引用关系

| 上层 | 下层 | 说明 |
|------|------|------|
| `app/api` | `app/service`, `commonsrv/*` | API 调用 Service/Commonsrv |
| `app/service` | `app/dao`, `commonsrv/*` | Service 调用 DAO/Commonsrv |
| `commonsrv/*` | `app/dao`, `library` | Commonsrv 调用 DAO |
| `app/dao` | `app/model` | DAO 调用 Model |

## API 模块

| 模块 | 路由 | 说明 |
|------|------|------|
| StarShip | `/front` | 家族核心功能 |
| Management | `/management` | 家族管理 |
| StarshipWar | `/warcraft` | 领地战 |
| StarshipAuction | `/auction` | 家族拍卖 |
| StarshipShop | `/shop` | 家族商城 |
| StarshipConsulate | `/consulate` | 领事局任务 |
| StarshipBouleuterion | `/bouleuterion` | 议事厅 |
| DreamSpace | `/dreamSpace` | 星梦空间 |
| Farm | `/farm` | 农场玩法 |
| FarmFishpond | `/farm/fishpond` | 鱼塘玩法 |
| FyRank | `/fyRank` | 风云排行榜 |

## CMD 模块

| 模块 | Topic | 说明 |
|------|-------|------|
| `starship_event/` | `starship.event.topic` | 星舰事件中心 (45 事件) |
| `starship_cron/` | - | 定时任务 |
| `clear_data/` | - | 数据清理 |

## 共享服务模块 (commonsrv)

| 模块 | 说明 |
|------|------|
| `starship/` | 家族核心共享逻辑 |
| `starship_hall/` | 家族大厅共享逻辑 |
| `im.go` | IM 消息发送共享 |
| `rate_limit.go` | 限流共享 |
| `report.go` | 数据上报共享 |

## 与其他项目对比

| 维度 | slp-go | slp-room | slp-starship |
|------|--------|----------|-------------|
| 服务类型 | HTTP+RPC+CMD | HTTP+CMD | HTTP+CMD |
| 共享模块 | 无 | 无 | commonsrv/ |
| API 模块 | 160+ | 18+ | 28 |
| CMD 模块 | 219 | 100+ | 7 |
| DAO 文件 | 968 | 500+ | 104 |
| 路由前缀 | `/go/` | `/go/room/` | `/go/starship/` |

## 家族玩法矩阵

| 玩法 | 说明 |
|------|------|
| 家族管理 | 创建、加入、退出、解散 |
| 领地战 | 家族间争夺领地 |
| 家族拍卖 | 道具拍卖交易 |
| 家族商城 | 道具购买 |
| 领事局 | 家族任务系统 |
| 议事厅 | 家族议事/积分 |
| 农场 | 种植、加工、鱼塘 |
| 星梦空间 | 家族成员互动 |
| 风云榜 | 家族排行榜 |
| 家族金币 | 家族货币系统 |