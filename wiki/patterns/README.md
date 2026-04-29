---
id: patterns/README
label: README
source: /Users/hugh/project/my-wiki/curated/patterns/README.md
role: 规范
compiled: 2026-04-28
source_hash: d8fb9a625883f9c865dcdb0334cfa298
---

> 跨项目通用的开发模式和最佳实践

## 已收录模式

| 模式 | 说明 |
|------|------|
| [[slp-business-development-standard]] | 从数据库到 API 全链路开发指南 |
| [[event-extension-guide]] | 事件拓展决策树 + HandleEventMap/观察者模式 |
| [[nsq-usage]] | NSQ 发送/消费统一标准 |
| [[cmd-module-standard]] | 所有 Go 项目新增 cmd 的统一结构 |
| [[code-scale-standard]] | 函数和文件的合理规模控制 |
| [[architecture-layered-standard]] | RPC/CMD/Domain/DAO 的职责边界 |
| [[business-module-standard]] | 常量/Service/工具函数的职责划分 |
| [[business-code-example]] | 从 0 到 1 实现完整业务模块 |
| [[project-learning-framework]] | 可复用的新项目学习方法论 |
| [[sub-agent-orchestration]] | AI 子 agent 编排策略 |

## 通用模式速查

### 批量查询

```go
// ❌ for _, id := range ids { item := dao.Item.One(id) }
// ✅ items := dao.Item.BatchGet(ids)
```

### 缓存（Cache-Aside）

```go
func Get(ctx context.Context, id uint32) (*Item, error) {
    data := redis.Get(ctx, key)
    if data != nil { return unmarshal(data) }
    item := dao.Item.One(id)
    go redis.Set(ctx, key, marshal(item), 3600)
    return item, nil
}
```

### 事务

```go
err := gdb.Transaction(ctx, func(tx *gdb.TX) error {
    dao.User.Update(ctx, uid, data, tx)
    dao.Log.Insert(ctx, log, tx)
    return nil
})
```

**原则**：事务内操作必须绑定 tx；粒度尽可能小；禁止事务中 RPC 调用。

## 路径警示

AI 容易混淆以下路径：

| 路径 | 说明 |
|------|------|
| `/Users/hugh/project/harness/slp-harness` | 正确 - 实际工作项目 |
| `/Users/hugh/harness/slp-harness` | 错误 - 不存在 |

写文件前必须 `ls -la` 确认目录存在。
