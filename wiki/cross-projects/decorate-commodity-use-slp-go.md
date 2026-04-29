---
id: decorate-commodity-use-slp-go
label: 装扮类物品使用转发 - slp-go 视角
source: curated/cross-projects/decorate-commodity-use/slp-go.md
business: decorate-commodity-use
compiled: 2026-04-25
links:
  - decorate-commodity-use-overview
---

# 装扮类物品使用转发 - slp-go 视角

> slp-go 侧负责调用装扮服务添加有效期 + 自动佩戴

## 核心职责

| 职责 | 说明 |
|------|------|
| 接收 RPC 请求 | UseDecorateCommodity 接口 |
| 查询装扮信息 | 根据 pretend_id 获取 cate_id/group_id |
| 添加有效期 | 调用 sendGroupPretend 续期 |
| 自动佩戴 | 如果用户正在使用，自动更新佩戴状态 |

## 核心代码位置

| 文件 | 说明 |
|------|------|
| `proto/rpc/rpc_pretend.proto` | Proto 定义 |
| `rpc/server/internal/pretend/rpc.go` | RPC 入口 |
| `rpc/server/internal/pretend/service/pretend.go` | Service 常量 |
| `rpc/server/internal/pretend/service/pretend_discard.go` | Service 实现 |

## Service 实现

```
获取 Redis 锁 → GetCateIdAndGroupId → 构造 groupParam → sendGroupPretend → 返回结果
```

**锁 Key**: `pretend.useDecorateCommodity.locker.uid.{uid}` (2s 超时)

## Source 类型注册

```go
const AddFragmentSourceDecorateCommodity = "decorate_commodity"

var addFragmentSourceMap = map[string]bool{
    AddFragmentSourceDecorateCommodity: true,
}
```

## 测试场景

| 场景 | 预期结果 |
|------|----------|
| pretend_id 有效 | 有效期累加成功 |
| pretend_id 不存在 | 返回错误 |
| 新用户首次使用 | 创建新的装扮记录 |
| 老用户续期 | 在原有有效期基础上累加 |