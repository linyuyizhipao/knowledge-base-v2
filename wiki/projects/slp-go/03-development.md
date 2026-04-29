---
id: slp-go-development
label: slp-go 开发工作流
source: curated/projects/slp-go/03-development.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-api
  - slp-go-service
  - slp-go-dao
---

# slp-go 开发工作流

## 代码生成

| 命令 | 用途 |
|------|------|
| `slpctl gen -t xs_user_profile` | 单表 DAO/Model/PB 生成 |
| `slpctl gen -t xs_user_profile,xs_follow` | 批量生成 |
| `slpctl gen -t xs_user_profile -delete` | 删除模式 |

## 构建命令

| 命令 | 用途 |
|------|------|
| `make` | 构建所有服务 |
| `make http` | 仅 HTTP 服务 |
| `make rpc` | 仅 RPC 服务 |
| `make cmd` | 仅 CMD 工具 |

## 本地运行

| 命令 | 用途 |
|------|------|
| `./bin/http` | HTTP 服务 |
| `./bin/rpc --name=user` | RPC 服务 |
| `./bin/cmd --name=cache --action=Main` | CMD 任务 |

## 代码检查

| 命令 | 用途 |
|------|------|
| `golangci-lint run ./...` | 静态检查 |
| `gofmt -l -s -w app/` | 代码格式化 |

## 测试

| 命令 | 用途 |
|------|------|
| `go test -v -count=1 ./...` | 所有测试 |
| `go test -v ./app/service/... -run TestXxx` | 特定测试 |

## API 开发流程

| 步骤 | 目录 | 说明 |
|------|------|------|
| 1 | `app/api/` | 创建 handler，添加 Swagger 注解 |
| 2 | `app/query/` + `app/pb/` | 定义结构体 |
| 3 | `app/service/` | 实现业务逻辑 |
| 4 | `make swagger` | 生成文档 |

## 相关知识

- [[projects/slp-go/01-structure]]
- [[patterns/slp-business-development-standard]]
