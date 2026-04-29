# slp-starship 项目结构

> 家族（星舰）系统：家族管理、领地战、农场、商城等玩法

**最后更新**: 2026-04-05  
**代码版本**: master@80eb9c86d

---

## 核心架构

两层服务形态：

```
┌─────────────┐   ┌─────────────┐
│ HTTP Server │   │ CMD Workers │
│  (main.go)  │   │  (cmd/)     │
└──────┬──────┘   └──────┬──────┘
       │                 │
       └─────────────────┼─────────────────┐
                         │                 │
                         ▼                 ▼
                    ┌─────────┐     ┌──────────┐
                    │  API    │────▶│ Service  │
                    │ Layer   │     │  Layer   │
                    └─────────┘     └────┬─────┘
                                         │
                                         ▼
                                    ┌──────────┐
                                    │   DAO    │
                                    └────┬─────┘
                                         │
                                ┌────────┴────────┐
                                │                 │
                                ▼                 ▼
                           ┌────────┐     ┌──────────┐
                           │ MySQL  │     │  Redis   │
                           └────────┘     └──────────┘
```

**与 slp-go/slroom 的区别**:
- 没有独立的 RPC 服务层
- 使用 `commonsrv/` 共享服务模块
- 事件处理统一使用 HandleEventMap 模式

---

## 目录结构

```
slp-starship/
├── main.go                       # HTTP 服务入口
├── app/                          # HTTP 应用主代码
│   ├── app.go                    # 应用启动
│   ├── route.go                  # 路由定义 (/go/starship/*)
│   ├── api/                      # HTTP 请求处理器 (28 模块)
│   │   ├── starship.go           # 家族核心 API
│   │   ├── starship_war.go       # 领地战
│   │   ├── starship_auction.go   # 家族拍卖
│   │   ├── starship_shop.go      # 家族商城
│   │   ├── starship_consulate.go # 领事局
│   │   ├── starship_bouleuterion.go # 议事厅
│   │   ├── farm.go               # 农场
│   │   ├── farm_fishpond.go      # 鱼塘
│   │   ├── dream_space.go        # 星梦空间
│   │   └── ...
│   ├── service/                  # 服务层 (14 模块)
│   ├── dao/                      # 数据访问层 (104 文件)
│   ├── model/                    # 数据模型 (108 文件)
│   ├── pb/                       # Protobuf 定义 (149 文件)
│   ├── query/                    # 查询组合层 (14 文件)
│   └── utils/                    # 工具函数 (10 模块)
│
├── cmd/                          # 命令行后台任务
│   ├── main.go                   # CMD 入口
│   └── internal/                 # 任务实现 (7 模块)
│       ├── starship_event/       # 星舰事件消费者 (HandleEventMap)
│       ├── starship_cron/        # 定时任务
│       ├── clear_data/           # 数据清理
│       └── ...
│
├── commonsrv/                    # 共享服务模块 (独有)
│   ├── starship/                 # 家族核心逻辑
│   ├── starship_hall/            # 家族大厅
│   ├── im.go                     # IM 消息
│   ├── rate_limit.go             # 限流
│   └── report.go                 # 上报
│
├── consts/                       # 常量定义 (31 文件)
│   ├── starship_event.go         # 星舰事件定义
│   ├── starship.go               # 家族常量
│   ├── farm.go                   # 农场常量
│   └── ...
├── library/                      # 基础设施库 (28 包)
├── proto/                        # Protobuf 源文件 (145 目录)
├── config/                       # 配置文件 (10 目录)
└── deploy/                       # 部署配置 (11 环境)
```

---

## 入口点

| 入口 | 文件 | 启动命令 |
|------|------|----------|
| HTTP | `main.go` | `./bin/http` |
| CMD | `cmd/main.go` | `./bin/cmd --name=<module>` |

### HTTP 入口分析

```go
// main.go
func main() {
    acm.Init()  // 配置中心初始化
    g.Log().Async(true)
    
    ca := cli.NewApp()
    ca.Name = "family http server"  // 家族服务器
    ca.Version = "0.0.1"
    
    // 日志配置
    g.Log().SetAsync(true)
    g.Log().SetFlags(glog.F_FILE_SHORT)
    g.Log().SetHeaderPrint(true)
    g.Log().SetStack(false)
    g.Log().SetWriter(loghook.NewLogWriter("FamilyHttp"))
    
    app.Run()  // 启动应用
}
```

### 路由分析

```go
// app/route.go
func initRoute() {
    server := g.Server()
    
    // 所有路由统一前缀：/go/starship/
    server.Group("/go/starship", func(group *ghttp.RouterGroup) {
        group.ALL("/test", api.Test)
        
        // 中间件链：Trace → CORS → Fire(防火墙) → Ctx → Auth → Error
        group.Middleware(
            service.Middleware.Trace,
            service.Middleware.CORS,
            service.Middleware.Fire,      // 防火墙/限流
            service.Middleware.Ctx,       // 用户上下文
            service.Middleware.Auth,      // 登录校验
            service.Middleware.Error,
        )
        
        // API 路由 (15 个)
        group.ALL("/front", api.StarShip)              // 家族前端
        group.ALL("/management", api.Management)       // 管理
        group.ALL("/bouleuterion", api.BouleuterionApi)// 议事厅
        group.ALL("/consulate", api.ConsulateApi)      // 领事局
        group.ALL("/shop", api.ShopApi)                // 商城
        group.ALL("/warcraft", api.Warcraft)           // 领地战
        group.ALL("/auction", api.StarshipAuction)     // 拍卖
        group.ALL("/dreamSpace", api.DreamSpaceApi)    // 星梦空间
        group.ALL("/fyRank", api.FyRankApi)            // 风云榜
        group.ALL("/farm", api.FarmApi)                // 农场
        group.ALL("/gold_coin", api.GoldCoin)          // 家族金币
        group.ALL("/privateRoomRank", api.PrivateRoomRankApiSrv)
        group.ALL("/bubble", api.BubbleApi)
        group.ALL("/subsectionPack", api.SubsectionPackApi)
        group.ALL("/farmDailyPack", api.FarmDailyPackApi)
    })
}
```

---

## 模块统计

| 层级 | 目录 | 数量 |
|------|------|------|
| API | `app/api/` | 28 |
| Service | `app/service/` | 14 |
| DAO | `app/dao/` | 104 |
| Model | `app/model/` | 108 |
| CMD | `cmd/internal/` | 7 |
| 常量 | `consts/` | 31 文件 |
| Proto | `proto/` | 145 目录 |
| 共享服务 | `commonsrv/` | 5 模块 |

---

## 核心业务模块

### API 模块

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
| GoldCoin | `/gold_coin` | 家族金币 |
| PrivateRoomRank | `/privateRoomRank` | 个人房榜单 |
| Bubble | `/bubble` | 气泡 |
| SubsectionPack | `/subsectionPack` | 分段礼包 |
| FarmDailyPack | `/farmDailyPack` | 农场每日礼包 |

### CMD 模块（事件消费者）

| 模块 | 位置 | Topic | 说明 |
|------|------|-------|------|
| starship_event | `cmd/internal/starship_event/` | `starship.event.topic` | 星舰事件中心 (45 事件) |
| starship_cron | `cmd/internal/starship_cron/` | - | 定时任务 |
| clear_data | `cmd/internal/clear_data/` | - | 数据清理 |

---

## 事件能力

### 事件 Topic

```go
// consts/starship_event.go
const StarshipEventTopic = "starship.event.topic"
```

### 事件分类（45 事件）

| 分类 | 事件数量 | 示例 |
|------|---------|------|
| **商城事件** | 1 | `shop_pay_event` |
| **议事厅事件** | 2 | `bouleuterion_consume_event` |
| **领事局事件** | 4 | `consulate_add_score_event` |
| **家族事件** | 9 | `starship_quit_event`, `starship_dismiss_event` |
| **拍卖事件** | 7 | `starship_auction_event`, `xs_starship_auction` |
| **领地战事件** | 4 | `starship_spot_war_event`, `starship_war_flag_event` |
| **星梦空间** | 1 | `starship_dream_space_event` |
| **家族房榜单** | 5 | `fy_interaction_leave_room_event` |
| **个人房榜单** | 5 | `pr_interaction_leave_room_event` |
| **农场事件** | 9 | `farm_up_event`, `farm_fishpond_bait_matures` |
| **农场红包** | 1 | `farm_red_package_award_event` |

### 事件处理模式

**HandleEventMap 模式**:

```go
// cmd/internal/starship_event/event/base.go
type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) error
}

var HandleEventMap = map[consts.StarshipEvent]HandleEvent{}
```

**事件处理器示例**:

```go
// cmd/internal/starship_event/event/shop_pay_event.go
package event

func init() {
    HandleEventMap[consts.EventShopPay] = &shopPayEventHandler{}
}

type shopPayEventHandler struct{}

func (h *shopPayEventHandler) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

---

## 模块引用关系

```
app/api      → app/service, commonsrv/*
app/service  → app/dao, app/model, commonsrv/*
commonsrv/*  → app/dao, app/model, library
app/dao      → app/model (内部调用)
library      → 第三方服务 (Redis, NSQ, MySQL 等)

严格禁止：
- 任何层不可调用 app/api
- library 不可调用 app/service
```

---

## 技术栈

### 核心框架

| 组件 | 技术 | 版本 |
|------|------|------|
| Web 框架 | GoFrame | v1.16.4 |
| Redis | go-redis/v8 | v8.11.5 |
| MySQL | go-sql-driver | v1.5.0 |
| NSQ | go-nsq | v1.0.8 |
| RPC | rpcx | v0.0.0 |
| Swagger | gof/swagger | v1.3.0 |
| Kafka | sarama | v1.28.0 |

### 基础设施

| 库 | 说明 |
|------|------|
| `library/nsq.go` | NSQ 客户端封装 |
| `library/redis/` | Redis 客户端封装 |
| `library/acm/` | 配置中心 |
| `library/tracer/` | 链路追踪 |

---

## 配置管理

### 配置文件

```
config/
├── config.toml           # 主配置
├── config.dev.toml       # 开发环境
└── config.prod.toml      # 生产环境
```

### ACM 配置中心

```go
// library/acm/acm.go
func Init() {
    // 从 ACM 拉取配置
}
```

---

## 开发相关

### 构建命令

```bash
# HTTP 服务
./dev.sh

# 全量构建
make build

# 生成 Proto
./dev_proto.sh

# 生成代码
./gen.sh
```

### 本地开发

```bash
# 开发模式启动
./dev.sh

# 查看日志
tail -f logs/starship.log
```

---

## 与 slp-go/slroom 对比

| 维度 | slp-go | slp-room | slp-starship |
|------|--------|----------|-------------|
| **服务类型** | HTTP+RPC+CMD | HTTP+CMD | HTTP+CMD |
| **共享模块** | 无 | 无 | commonsrv/ |
| **API 模块** | 160+ | 18+ | 28 |
| **CMD 模块** | 219 | 100+ | 7 |
| **DAO 文件** | 968 | 500+ | 104 |
| **事件模式** | HandleEventMap | 混合 | HandleEventMap |
| **路由前缀** | `/go/` | `/go/room/` | `/go/starship/` |
| **核心功能** | 用户/关系/礼物 | 房间/麦位/PK | 家族/领地战/农场 |

---

## 家族系统特色

### 1. 共享服务模式

`commonsrv/` 目录是 slp-starship 独有的设计：

```
commonsrv/
├── starship/           # 家族核心共享逻辑
├── starship_hall/      # 家族大厅共享逻辑
├── im.go               # IM 消息发送共享
├── rate_limit.go       # 限流共享
└── report.go           # 数据上报共享
```

### 2. 家族玩法矩阵

- **家族管理** - 创建、加入、退出、解散
- **领地战** - 家族间争夺领地
- **家族拍卖** - 道具拍卖交易
- **家族商城** - 道具购买
- **领事局** - 家族任务系统
- **议事厅** - 家族议事/积分
- **农场** - 种植、加工、鱼塘
- **星梦空间** - 家族成员互动
- **风云榜** - 家族排行榜
- **家族金币** - 家族货币系统

---

## 关键文件

| 文件 | 用途 |
|------|------|
| `main.go` | HTTP 服务入口 |
| `app/app.go` | 应用启动逻辑 |
| `app/route.go` | 路由定义 |
| `cmd/internal/starship_event/service.go` | 事件消费者启动 |
| `consts/starship_event.go` | 事件常量定义 |
| `go.mod` | 依赖管理 |
| `commonsrv/starship/` | 家族核心共享逻辑 |

---

**参考文档**:
- [`01-event-capabilities.md`](./01-event-capabilities.md) - 事件能力清单
- [`../../../patterns/event-extension-guide.md`](../../../patterns/event-extension-guide.md) - 事件能力拓展指南

---

## 业务开发文档

| 文档 | 说明 |
|------|------|
| [../../../cross-projects/prayer-activity/09-business-prayer-draw-activity.md](../../../cross-projects/prayer-activity/09-business-prayer-draw-activity.md) | 祈福抽奖活动（活动模板 2）技术方案 |
