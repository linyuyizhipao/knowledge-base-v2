---
id: patterns/slp-business-development-standard
label: slp-business-development-standard
source: curated/patterns/slp-business-development-standard.md
role: 规范
compiled: 2026-04-28
source_hash: 8a29df3b8d009ac263747b7916054f57
---

> 基于 SLPCTL 工具的标准开发流程

## 开发流程总览

| 步骤 | 阶段 | 工具 | 产出 |
|------|------|------|------|
| 1 | 数据库设计 | MySQL DDL | 表结构 |
| 2 | DAO 生成 | `slpctl gen` | DAO/Model/PB |
| 3 | API 生成 | `slpctl code` | Handler/Service/Proto |
| 4 | 业务实现 | 手动编码 | 业务逻辑 |
| 5 | 测试部署 | `slpctl ci` | Jenkins 构建 |

## 核心命令

```bash
# 步骤 2：生成 DAO
slpctl gen -t xs_<table>

# 步骤 3：生成 API
slpctl code -api /go/room/<biz>/<action> -desc "<desc>"
slpctl code -config apis.json

# 步骤 5：部署
slpctl ci -w
slpctl swagger -projects <project> -out ~/.slp/swagger
```

## 路由命名

```
/go/room/<business>/<action>
  ↑      ↑          ↑
 项目   业务模块    具体 API
```

| 项目 | 路由前缀 |
|------|----------|
| slp-go | `/go/slp/` |
| slp-room | `/go/room/` |
| slp-starship | `/go/starship/` |

## Service 层标准结构

```go
var <Business>Srv = &<business>Service{ /* 子模块注入 */ }

type <business>Service struct { /* 子模块 */ }

func (s *<business>Service) <Method>(ctx context.Context, uid uint32) (*pb.Response, error) {
    // 1. 参数校验 → 2. 数据查询 → 3. 业务逻辑 → 4. 返回结果
}
```

## 检查清单

| 阶段 | 检查项 |
|------|--------|
| 数据库 | DDL 完成、表验证、索引合理 |
| DAO | `slpctl gen` 成功、编译通过 |
| API | Handler/Service 生成、Proto 编译通过 |
| 业务 | Service 逻辑完成、RedisKey 规范、NSQ Topic 规范 |
| 部署 | 测试通过、构建成功、API 文档生成 |

## 常见坑点

| 问题 | 解决 |
|------|------|
| Proto 编译失败 | 清理旧文件，重新 `slpctl proto` |
| API 404 | 检查 `router/<business>.go` 路由注册 |
| 事务不一致 | 所有 DAO 调用必须传入 tx |
| Redis Key 冲突 | 业务专属 Key 加统一前缀 |
| NSQ 消息无法消费 | 检查 Topic/消费者启动/NSQAdmin 面板 |
