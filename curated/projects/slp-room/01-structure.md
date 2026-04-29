# slp-room 项目结构

> 房间服务：多人房、PK、抢麦等实时互动功能

**最后更新**: 2026-04-05

---

## 核心架构

三层服务形态：

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│ HTTP Server │   │ RPC Server  │   │ CMD Workers │
│  (main.go)  │   │ (rpc/server)│   │  (cmd/)     │
└──────┬──────┘   └──────┬──────┘   └──────┬──────┘
       │                 │                 │
       └─────────────────┼─────────────────┘
                         │
       ┌─────────────────┼─────────────────┐
       │                 │                 │
       ▼                 ▼                 ▼
  ┌─────────┐     ┌──────────┐     ┌──────────┐
  │  API    │────▶│  Busi    │────▶│   DAO    │
  │ Layer   │     │  Layer   │     │  Layer   │
  └─────────┘     └──────────┘     └────┬─────┘
                                        │
                                ┌───────┴───────┐
                                │               │
                                ▼               ▼
                           ┌────────┐     ┌──────────┐
                           │ MySQL  │     │  Redis   │
                           └────────┘     └──────────┘
```

---

## 目录结构

```
slp-room/
├── main.go                       # HTTP 服务入口
├── app/                          # HTTP 应用主代码
│   ├── app.go                    # 应用启动和路由
│   ├── route.go                  # 路由定义
│   ├── api/                      # HTTP 请求处理器 (18+ 模块)
│   │   ├── action.go             # 行动 API
│   │   ├── mic.go                # 麦位 API
│   │   ├── room_*.go             # 房间相关 API
│   │   └── ...
│   ├── busi/                     # 业务逻辑层 (60+ 模块)
│   │   ├── room_*.go             # 房间业务
│   │   ├── user_*.go             # 用户业务
│   │   └── ...
│   ├── service/                  # 服务层 (97 模块)
│   ├── dao/                      # 数据访问层 (500+ 文件)
│   ├── model/                    # 数据模型 (500+ 文件)
│   ├── pb/                       # Protobuf 定义 (750+ 文件)
│   ├── query/                    # 查询组合层 (103 文件)
│   ├── cachemodel/               # 缓存模型 (14 文件)
│   └── utils/                    # 工具函数 (32 模块)
│
├── cmd/                          # 命令行后台任务
│   ├── main.go                   # CMD 入口
│   └── internal/                 # 任务实现 (100+ 模块)
│       ├── auction/              # 拍卖
│       ├── big_brother/          # 大哥房间
│       ├── bump/                 # 互动
│       ├── cplink/               # CP 连线
│       ├── enter/                # 进入房间
│       ├── grabmic/              # 抢麦
│       ├── room_pk/              # 房间 PK
│       ├── room_recommend_more/  # 房间推荐
│       └── ...
│
├── rpc/                          # RPC 服务
│   └── server/                   # RPC 服务实现
│
├── consts/                       # 常量定义 (36 文件)
├── library/                      # 基础设施库 (33 包)
├── module/                       # 模块封装 (15 模块)
├── plugin/                       # 插件系统 (17 插件)
├── proto/                        # Protobuf 源文件 (782 目录)
├── config/                       # 配置文件 (12 目录)
└── deploy/                       # 部署配置 (10 环境)
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
    
    ca := cli.NewApp()
    g.Log().Async(true)
    
    ca.Name = "slp http server"
    ca.Version = "0.0.1"
    ca.Flags = []cli.Flag{
        cli.StringFlag{
            Name:  "gf.gcfg.file",
            Usage: "config name",
            Value: "config.toml",
        },
    }
    
    // 设置日志
    g.Log().SetAsync(true)
    g.Log().SetFlags(glog.F_FILE_SHORT)
    g.Log().SetStack(false)
    g.Log().SetWriter(loghook.NewLogWriter(def.ServerHttp))
    
    app.Run()  // 启动应用
}
```

### CMD 入口分析

```go
// cmd/main.go (示例)
func main() {
    // 初始化模块
    // 根据 --name 参数加载对应模块
    // 启动 NSQ 消费者
}
```

---

## 模块统计

| 层级 | 目录 | 数量 |
|------|------|------|
| API | `app/api/` | 18+ |
| 业务 | `app/busi/` | 60+ |
| 服务 | `app/service/` | 97 |
| DAO | `app/dao/` | 500+ |
| Model | `app/model/` | 500+ |
| CMD | `cmd/internal/` | 100+ |
| 常量 | `consts/` | 36 文件 |
| Proto | `proto/` | 782 目录 |

---

## 核心业务模块

### 房间相关

| 模块 | 位置 | 说明 |
|------|------|------|
| 房间状态 | `app/busi/room_state.go` | 房间状态管理 |
| 房间麦位 | `app/busi/room_mic_*.go` | 麦位管理 (10+ 文件) |
| 房间用户 | `app/busi/room_user.go` | 房间用户管理 |
| 房间礼物 | `app/busi/room_gift.go` | 房间礼物系统 |
| 房间热度 | `app/busi/room_hot.go` | 房间热度计算 |
| 房间 PK | `app/busi/room_pk.go` | 房间 PK 功能 |

### CMD 模块（事件消费者）

| 模块 | 位置 | Topic | 说明 |
|------|------|-------|------|
| room_recommend_more | `cmd/internal/room_recommend_more/` | `slp.room.recommend.more` | 房间推荐 |
| grabmic | `cmd/internal/grabmic/` | `grabmic.TopicGrabMic` | 抢麦事件 |
| cplink | `cmd/internal/cplink/` | `cplink.TopicCplinkV2` | CP 连线 |
| room_pk | `cmd/internal/room_pk/` | `room.pk.topic` | 房间 PK |
| big_brother | `cmd/internal/big_brother/` | `slp.big.brother` | 大哥房间 |
| enter | `cmd/internal/enter/` | `xs.room.enter` | 房间进入 |
| auction | `cmd/internal/auction/` | `slp.auction` | 拍卖事件 |
| bump | `cmd/internal/bump/` | `consts.TopicBumpTopic` | 互动事件 |

---

## 模块引用关系

```
app/api      → app/busi, app/service, app/query, app/dao, app/model
app/busi     → app/dao, app/model, library
app/service  → app/dao, app/model, library
app/dao      → app/model (内部调用)
library      → 第三方服务 (Redis, Kafka, MySQL 等)

严格禁止：
- 任何层不可调用 app/api
- library 不可调用 app/busi/app/service
```

---

## 基础设施

### library/ 核心库

| 包 | 说明 |
|------|------|
| `library/nsq/` | NSQ 客户端封装 |
| `library/redis/` | Redis 客户端封装 |
| `library/rpc/` | RPC 客户端封装 |
| `library/tool/` | 工具函数 |

### module/ 模块封装

| 模块 | 说明 |
|------|------|
| `module/pool/` | 连接池管理 |
| `module/heartbeat/` | 心跳管理 |
| `module/proxy/` | 代理服务 |

### plugin/ 插件系统

| 插件 | 说明 |
|------|------|
| `plugin/config/` | 插件配置 |
| `plugin/lucky/` | 幸运抽奖 |
| `plugin/vote/` | 投票插件 |

---

## 配置管理

### 配置文件位置

```
config/
├── config.toml           # 主配置
├── config.dev.toml       # 开发环境
├── config.prod.toml      # 生产环境
└── <module>/             # 模块配置
```

### ACM 配置中心

```go
// library/acm/acm.go
func Init() {
    // 初始化配置中心
    // 从 ACM 拉取配置
}
```

---

## 开发相关

### 构建命令

```bash
# HTTP 服务
./http.sh

# RPC 服务
./rpc.sh

# CMD 模块
./cmd.sh

# 全量构建
make build
```

### 本地开发

```bash
# 开发模式启动
./dev.sh

# 查看日志
tail -f logs/slp-room.log
```

---

## 代码生成

### DAO 生成

```bash
# 生成 DAO 代码
gen xs_chatroom default
```

### Proto 生成

```bash
# 生成 Protobuf 代码
make proto
```

---

## 测试

```bash
# 运行测试
go test ./app/service/... -v

# 覆盖率
go test -cover ./...
```

---

## 关键文件

| 文件 | 用途 |
|------|------|
| `main.go` | HTTP 服务入口 |
| `app/app.go` | 应用启动逻辑 |
| `app/route.go` | 路由定义 |
| `cmd/main.go` | CMD 入口 |
| `go.mod` | 依赖管理 |
| `Makefile` | 构建命令 |
| `claude.md` | 项目 AI 上下文 |

---

## 与 slp-go 的对比

| 维度 | slp-go | slp-room |
|------|--------|----------|
| **服务类型** | HTTP + RPC + CMD | HTTP + CMD |
| **API 模块** | 160+ | 18+ |
| **CMD 模块** | 219 | 100+ |
| **DAO 文件** | 968 | 500+ |
| **核心功能** | 用户、关系、礼物 | 房间、麦位、PK |
| **事件模式** | HandleEventMap | HandleEventMap + switch-case |

---

**参考文档**:
- [`02-architecture.md`](./02-architecture.md) - 架构分层
- [`03-development.md`](./03-development.md) - 开发流程
- [`08-event-capabilities.md`](./08-event-capabilities.md) - 事件能力清单
