# slpctl 完整参考手册

> SLP 框架配套的命令行工具集详细文档

## 快速开始

```bash
# 安装 slpctl
go install github.com/olaola-chat/slpctl@master

# 查看所有命令
slpctl
```

## 命令列表

| 命令 | 用途 | 详细文档 |
|------|------|---------|
| `code` | API 代码生成（Handler + Service + Proto） | [下文](#1-code---api-代码生成) |
| `gen` | 数据库表代码生成（DAO + Model + PB） | [下文](#2-gen---数据库表代码生成) |
| `state` | 游戏状态机代码生成 | [下文](#3-state---状态机代码生成) |
| `codec` | Redis Cache 代码生成 | [下文](#4-codec---cache-代码生成) |
| `swagger` | Swagger 文档生成 | [下文](#5-swagger---swagger-文档生成) |
| `proxy` | Proxyman 抓包文件生成 | [下文](#6-proxy---抓包文件生成) |
| `ci` | Jenkins 构建部署 | [下文](#7-ci---jenkins-构建命令) |

> **注意**: Proto 编译通过 `make proto` 完成，不是 slpctl 命令

## 典型开发流程

```bash
# 1. 创建数据库表
slpctl gen -t xs_user_profile

# 2. 定义 API
slpctl code -api /go/slp/userCenter/userProfile -desc "用户主页"

# 3. 手动实现 Service 业务逻辑

# 4. 生成文档
slpctl swagger -projects slp-go -out ~/.slp/swagger
```

## Makefile 集成

```makefile
make proto      # 更新已修改的 proto（项目 Makefile）
make proto-all  # 更新所有 proto
make swagger    # 生成并上传 Swagger
```

---

## 目录

1. [code - API 代码生成](#1-code---api-代码生成)
2. [gen - 数据库表代码生成](#2-gen---数据库表代码生成)
3. [state - 状态机代码生成](#3-state---状态机代码生成)
4. [codec - Cache 代码生成](#4-codec---cache-代码生成)
5. [swagger - Swagger 文档生成](#5-swagger---swagger-文档生成)
6. [proxy - 抓包文件生成](#6-proxy---抓包文件生成)
7. [ci - Jenkins 构建命令](#7-ci---jenkins-构建命令)

---

## 1. code - API 代码生成

根据精简的 JSON 配置文件自动生成 API 代码（Handler + Service + Proto）。

### 路由规则

路由采用 4 层结构，使用**首字母小写的驼峰命名**：

```
/{project}/{service}/{action}
   ↑         ↑        ↑
 前缀     业务模块   具体 API
```

**示例**：
- `/go/slp/userCenter/userProfile` - 用户中心 - 用户主页
- `/go/slp/toolRank/rankList` - 工具排行 - 排行榜列表
- `/go/room/game/joinGame` - 房间游戏 - 加入游戏

### 路由前缀

| 项目 | 路由前缀 |
|------|----------|
| slp-go | `/go/slp/` |
| slp-room | `/go/room/` |
| slp-starship | `/go/starship/` |
| slp-circle | `/go/circle/` |

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-api` | 快速生成：直接指定 router_path | - |
| `-config` | JSON 配置文件路径 | - |
| `-project` | 目标项目目录 | `./` |
| `-router` | 路由路径 | - |
| `-method` | HTTP 方法：get/post | `post` |
| `-desc` | 接口描述 | - |
| `-gen` | 根据 router 生成配置文件模板 | `false` |
| `-proto-dir` | proto 文件子目录 | `api` |
| `-proto-prefix` | proto 文件名前缀 | `api_` |
| `-service-var` | Service 变量名 | `Srv` |
| `-service-struct` | Service struct 名 | 驼峰 service 名 |
| `-handler-var` | Handler 变量名 | service 名 + Api |

### 使用模式

#### 模式 1：快速生成

```bash
slpctl code -api /go/slp/klp/home -project ./slp-go
```

自动生成：
- Request Proto: `ReqKlpHome`
- Response Proto: `ResKlpHome`
- Handler: `KlpHome` (在 `api/handler/klp_api.go`)
- Service: `KlpSrv` (在 `rpc/server/internal/klp/klp_pretend.go`)

#### 模式 2：配置文件

```json
[
  {
    "router_path": "/go/slp/klp/home",
    "method": "post",
    "description": "签到主页",
    "request_proto": "ReqKlpHome",
    "response_proto": "ResKlpHome"
  },
  {
    "router_path": "/go/slp/userCenter/userProfile",
    "method": "get",
    "description": "用户主页",
    "request_proto": "ReqUserCenterUserProfile",
    "response_proto": "ResUserCenterUserProfile"
  }
]
```

```bash
slpctl code -config klp.home.json -project ./slp-go
```

#### 模式 3：自定义参数

```bash
# 自定义 Service 变量名
slpctl code -api /go/slp/userCenter/userInfo -service-var UserSrv -service-struct UserCenter

# 自定义 Handler 变量名
slpctl code -api /go/slp/toolRank/rankList -handler-var ToolRankHandler

# 根据 router 生成配置文件模板
slpctl code -router /go/slp/klp/home -gen
```

### 生成的代码

| 文件 | 路径 | 更新策略 |
|------|------|----------|
| API Handler | `api/handler/{service}_api.go` | 追加/更新 |
| Service | `rpc/server/internal/{service}/{service}_pretend.go` | 跳过 |
| Proto | `proto/{protoDir}/{prefix}{service}_{method}.proto` | 覆盖 |

**命名规则**：
- `service` 和 `action` 会组合成驼峰命名
- 示例：`/go/slp/userCenter/userProfile` → `ReqUserCenterUserProfile`, `UserCenterUserProfile`

---

## 2. gen - 数据库表代码生成

根据数据库表名自动生成 DAO + Model + PB。

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-t` | 数据库表名，多个用逗号分隔 | - |
| `-d` | 数据库名 | `xianshi` |
| `-u` | 数据库用户名 | `root` |
| `-p` | 数据库密码 | `root` |
| `-H` | 数据库主机 | `114.55.3.96` |
| `-P` | 数据库端口 | `8547` |
| `-o` | 输出目录 | `./` |
| `-delete` | 删除模式 | `false` |
| `-dry-run` | 预览模式 | `false` |

### 数据库映射

| 数据库 | -g 值 |
|--------|------|
| xianshi | default |
| statics | banban |

### 使用示例

```bash
# 单个表
slpctl gen -t xs_user_profile

# 批量生成
slpctl gen -t xs_user_profile,xs_follow,xs_fans

# 指定数据库
slpctl gen -t xs_tool_rank -d statics

# 自定义连接
slpctl gen -t xs_item -d custom_db -u myuser -p mypass -H 127.0.0.1 -P 3306

# 删除（预览）
slpctl gen -t xs_user_profile -delete -dry-run

# 删除（执行）
slpctl gen -t xs_user_profile -delete
```

### 生成的代码

- `proto/entity_<table>.proto`
- `app/pb/entity_<table>.pb.go`（注入 tag）
- `app/dao/internal/<table>_dao.go`
- `app/dao/<Table>.go`
- `app/pb/entity_<table>.go`

### 删除模式

删除以上所有文件。

### 执行流程

1. 生成临时配置 `config/config_test_tmp.toml`
2. `gf gen pbentity` → `.proto`
3. `protoc` → `pb.go`
4. `protoc-go-inject-tag` → 注入 tag
5. `gf gen dao` → DAO 代码
6. 清理临时配置

---

## 3. state - 状态机代码生成

基于 JSON 配置生成游戏状态机代码。

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-j` | 状态机配置 JSON 目录 | `./rpc/server/internal/room_game/state/json` |
| `-f` | 配置文件名 | - |
| `-o` | 输出目录 | `./rpc/server/internal/room_game` |

### 配置示例

```json
{
  "states": ["idle", "playing", "ended"],
  "initial": "idle",
  "transitions": [
    { "from": "idle", "to": "playing", "event": "start" }
  ]
}
```

### 使用示例

```bash
slpctl state -f game_state.json -o ./output
```

---

## 4. codec - Cache 代码生成

根据数据库表名生成 Redis Cache 层代码。

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-t` | 数据库表名 | - |
| `-s` | 缓存过期时间（秒） | - |
| `-h` | 缓存过期时间（小时） | `3` |
| `-d` | Redis DB 模块 | `passive` |
| `-uq` | 主键别名 | `id` |
| `-m` | 项目 go.mod 包名 | `slp` |

### 使用示例

```bash
slpctl codec -t user_info -h 24 -d user -uq uid
```

---

## 5. swagger - Swagger 文档生成

生成 Swagger 文档，打包为 zip 并上传。

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-wk` | 项目工作目录 | 当前目录 |
| `-projects` | 项目列表（逗号分隔） | `slp-go,slp-room,slp-starship` |
| `-out` | Swagger 输出目录 | - |
| `-host` | 上传 Host | `https://114.55.3.96` |

### 使用示例

```bash
slpctl swagger -projects slp-go -out /tmp/swagger
slpctl swagger -wk=$(pwd)/.. -projects slp-go,slp-room -out ~/.slp/swagger
```

---

## 6. proxy - 抓包文件生成

生成 Proxyman 抓包配置文件。

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `-wk` | 项目工作目录 | 当前目录 |
| `-projects` | 项目列表 | `slp-go,slp-room,slp-starship` |
| `-out` | 输出目录 | `/tmp/slp` |

### 使用示例

```bash
slpctl proxy -projects slp-go -out /tmp/slp
```

### 客户端下载

```bash
curl -L -f --insecure --fail "https://114.55.3.96/go/audit/test/downProxyManSh" \
  -o /tmp/proxyman_setup.sh && \
chmod +x /tmp/proxyman_setup.sh && \
/tmp/proxyman_setup.sh
```

---

## Makefile 集成

```makefile
.PHONY: swagger
swagger:
	slpctl swagger -wk=$(shell cd .. && pwd) -out=$(HOME)/.slp/swagger

.PHONY: proxy
proxy:
	slpctl proxy -wk=$(shell cd .. && pwd) -out=$(HOME)/.slp/proxy
```

> **注意**: proto 编译使用项目自带 Makefile：`make proto` / `make proto-all`

---

## 项目结构

```
slpctl/
├── main.go                 # 入口
├── help_*.go              # 各命令帮助
├── codegen/               # API 生成
├── gengen/                # 数据库表生成
├── stategen/              # 状态机生成
├── codecgen/              # Cache 生成
├── swaggergen/            # Swagger 生成
└── proxygen/              # Proxy 生成
```

---

## 添加新功能

1. 在 `main.go` 的 `initFunctions()` 注册
2. 创建 `help_<name>.go` 实现 `Function` 接口
3. 实现 `InitArgs()`, `Execute()`, `Help()` 方法

```go
type Function interface {
    InitArgs(flagset *flag.FlagSet)
    Execute() error
    Help()
}
```

---

## 构建

```bash
# 本地
go build -o slpctl .

# 跨平台
GOOS=darwin GOARCH=arm64 go build -o slpctl-darwin-arm64 .
GOOS=linux GOARCH=amd64 go build -o slpctl-linux-amd64 .
```

---

## 7. ci - Jenkins 构建命令

触发 Jenkins 构建，支持等待结果、打开浏览器、查看失败日志、重启最近一次进程等模式。

### 前置配置（必须）

`ci` 需要 Jenkins API Token：

```bash
# 方式 1：环境变量（推荐，避免每次输入）
export SLPCTL_JENKINS_TOKEN="<your_jenkins_token>"

# 方式 2：命令行参数（临时）
slpctl ci -token "<your_jenkins_token>" -wait
```

### 参数说明

| 参数 | 说明 |
|------|------|
| `-w` / `-wait` | 触发构建并等待完成，显示构建结果 |
| `open` | 触发构建并打开 Jenkins 页面 |
| `last` | 重启最近一次部署的进程 |
| `-project` | 指定项目名称，默认为当前目录名 |

### 使用示例

```bash
# 触发构建
slpctl ci

# 触发构建并等待完成
slpctl ci -w
slpctl ci -wait

# 触发构建并打开浏览器
slpctl ci open

# 重启最近一次部署的进程
slpctl ci last

# 指定项目名称
slpctl ci -project slp-go -w
```

### 支持的项目

| 项目目录 | JOB_NAME | 构建产物 |
|---------|----------|---------|
| slp-go | slp-go | http, rpc, cmd |
| slp-room | slp-room | http, rpc, cmd |
| slp-starship | slp-starship | http, rpc, cmd |
| slp-common-rpc | slp-common-rpc | rpc, cmd |

### Jenkins 构建流程

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Jenkins 接收构建请求                                     │
│    - 触发条件：API 调用 + Crumb 认证                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 拉取最新代码 (dev 分支)                                   │
│    git pull origin dev                                     │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 编译构建                                                 │
│    make build                                              │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 部署到测试服务器                                         │
│    - 复制二进制文件到目标服务器                               │
│    - 更新 Supervisor 配置                                   │
│    - 重启进程                                               │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. 健康检查                                                 │
│    - 检查进程状态 (supervisorctl status)                    │
│    - 确认进程 RUNNING                                       │
└─────────────────────────────────────────────────────────────┘
```

### 完整开发发布流程

```bash
# 步骤 1: 创建功能分支
git checkout master
git checkout -b hu/user_achievement

# 步骤 2: 本地开发并提交
# ... 编辑代码 ...
git add -A
git commit -anm 'feat: add user achievement'

# 步骤 3: 合入 dev 分支
git checkout dev
git merge hu/user_achievement
git push origin dev

# 步骤 4: 触发构建
slpctl ci -w
```

---

**版本**: 2.0 | **最后更新**: 2026-04-11
