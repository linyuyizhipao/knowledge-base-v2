---
id: tools/slpctl
label: slpctl
source: curated/tools/slpctl.md
role: 工具
compiled: 2026-04-30
source_hash: ef085a11c008af64
---

> SLP 框架配套的命令行工具集

## 命令速查

| 命令 | 用途 |
|------|------|
| `code` | API 代码生成（Handler + Service + Proto） |
| `gen` | 数据库表代码生成（DAO + Model + PB） |
| `state` | 游戏状态机代码生成 |
| `codec` | Redis Cache 代码生成 |
| `swagger` | Swagger 文档生成 |
| `proxy` | Proxyman 抓包文件生成 |
| `ci` | Jenkins 构建部署 |

## 典型流程

```bash
slpctl gen -t xs_user_profile                              # 1. 生成 DAO
slpctl code -api /go/slp/userCenter/userProfile -desc "用户主页"  # 2. 生成 API
# 3. 手动实现 Service
slpctl swagger -projects slp-go -out ~/.slp/swagger        # 4. 生成文档
```

## code - API 生成

**路由规则**：`/{project}/{service}/{action}`（首字母小写驼峰）

| 项目 | 路由前缀 |
|------|----------|
| slp-go | `/go/slp/` | slp-room | `/go/room/` | slp-starship | `/go/starship/` | slp-circle | `/go/circle/` |

**参数**：`-api` 快速指定 | `-config` JSON 配置 | `-project` 目标目录 | `-desc` 描述 | `-service-var` Service 变量名 | `-handler-var` Handler 变量名

**生成文件**：`api/handler/{service}_api.go`（追加/更新） | `rpc/server/internal/{service}/{service}_pretend.go`（跳过） | `proto/{prefix}{service}_{method}.proto`（覆盖）

## gen - DAO 生成

**参数**：`-t` 表名（逗号分隔） | `-d` 数据库（默认 `xianshi`） | `-u`/`-p` 用户密码 | `-H`/`-P` 主机端口

```bash
slpctl gen -t xs_user_profile                    # 单个
slpctl gen -t xs_user_profile,xs_follow,xs_fans  # 批量
slpctl gen -t xs_user_profile -delete            # 删除
```

**数据库映射**：`xianshi` → `-g default` | `statics` → `-g banban`

**生成文件**：`proto/entity_<table>.proto` | `app/pb/entity_<table>.pb.go` | `app/dao/internal/<table>_dao.go` | `app/dao/<Table>.go`

## ci - Jenkins 构建

**前置**：`export SLPCTL_JENKINS_TOKEN="<token>"`

| 命令 | 说明 |
|------|------|
| `slpctl ci` | 触发构建 |
| `slpctl ci -w` | 触发并等待完成 |
| `slpctl ci open` | 触发并打开浏览器 |
| `slpctl ci last` | 重启最近一次进程 |

**支持项目**：slp-go | slp-room | slp-starship | slp-common-rpc

**Jenkins 流程**：拉取 master → `make build` → 部署到测试服务器 → supervisorctl restart → 健康检查

## state / codec / swagger / proxy

```bash
slpctl state -f game_state.json -o ./output
slpctl codec -t user_info -h 24 -d user -uq uid
slpctl swagger -projects slp-go -out /tmp/swagger
slpctl proxy -projects slp-go -out /tmp/slp
```
