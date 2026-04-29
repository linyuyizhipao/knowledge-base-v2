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

| 模式 | 路径 | 说明 |
|------|------|------|
| **SLP 业务开发规范** | [`slp-business-development-standard.md`](./slp-business-development-standard.md) ⭐ | 从数据库到 API 全链路开发指南 |
| **事件能力拓展指南** | [`event-extension-guide.md`](./event-extension-guide.md) | 事件拓展决策树 + HandleEventMap/观察者模式完整示例 |
| **NSQ 使用规范** | [`nsq-usage.md`](./nsq-usage.md) | NSQ 发送/消费统一标准 |
| **CMD 模块标准** | [`cmd-module-standard.md`](./cmd-module-standard.md) | 所有 Go 项目新增 cmd 的统一结构 |
| **代码规模标准** | [`code-scale-standard.md`](./code-scale-standard.md) | 函数和文件的合理规模控制 |
| **分层架构共识** | [`architecture-layered-standard.md`](./architecture-layered-standard.md) | RPC/CMD/Domain/DAO 的职责边界 |
| **业务开发规范** | [`business-module-standard.md`](./business-module-standard.md) | 常量/Service/工具函数的职责划分 |
| **业务代码示例** | [`business-code-example.md`](./business-code-example.md) | 从 0 到 1 实现完整业务模块 |
| **项目学习框架** | [`project-learning-framework.md`](./project-learning-framework.md) | 可复用的新项目学习方法论 |
| **房间类型开发** | [`../cross-projects/chatroom/room-type-development.md`](../cross-projects/chatroom/room-type-development.md) | 房间类型拓展完整指南（含代码模板） |
| 批量查询模式 | 下文 | 解决 N+1 查询问题 |
| 异步任务模式 | 下文 | 耗时操作异步化 |
| 缓存模式 | 下文 | Cache-Aside 策略 |
| 事务模式 | 下文 | 数据库事务规范 |

**注意**: HandleEventMap 和观察者模式代码模板已整合到 [[event-extension-guide]] 附录 A/B

---

## 批量查询模式

**问题**: N+1 查询导致性能问题

```go
// ❌ 错误 - N+1 查询
for _, id := range ids {
    item := dao.Item.One(id)  // N 次查询
}

// ✅ 正确 - 批量查询
items := dao.Item.BatchGet(ids)  // 1 次查询
```

## 异步任务模式

**问题**: 耗时操作阻塞请求

```
HTTP 请求 → 创建任务记录 → 发布消息 → 立即返回
                           ↓
                    后台消费者 → 执行任务 → 更新状态
```

## 缓存模式 (Cache-Aside)

```go
func Get(ctx context.Context, id uint32) (*Item, error) {
    // 1. 读缓存
    data := redis.Get(ctx, key)
    if data != nil {
        return unmarshal(data)
    }
    
    // 2. 读数据库
    item := dao.Item.One(id)
    
    // 3. 写缓存（异步）
    go redis.Set(ctx, key, marshal(item), 3600)
    
    return item, nil
}
```

## 事务模式

```go
func Transfer(ctx context.Context, from, to int) error {
    tx, _ := db.Begin()
    defer tx.Rollback()
    
    // 所有操作绑定 tx
    dao.Account.DB(tx).Update(...)
    dao.Log.DB(tx).Insert(...)
    
    return tx.Commit()
}
```

**原则**:
- 事务内操作必须绑定 tx
- 事务粒度尽可能小
- 禁止在事务中进行 RPC 调用

---

## 🚨 关键提醒（AI 必读）

### 路径混淆警示

AI 容易混淆以下两个路径：

| 路径 | 说明 |
|------|------|
| `/Users/hugh/project/harness/slp-harness` | ✅ **正确** - 这是实际工作项目目录 |
| `/Users/hugh/harness/slp-harness` | ❌ **错误** - 这个目录不存在（少 `project`） |

**写文件前必须确认路径**：
- 工作项目：`/Users/hugh/project/harness/slp-harness`
- 配置目录：`/Users/hugh/.claude`

错误示例：
```bash
# ❌ 错误 - 写到不存在的目录
/Users/hugh/harness/slp-harness/knowledge/patterns/CODING_STANDARD.md

# ✅ 正确 - 写到实际项目目录
/Users/hugh/project/harness/slp-harness/knowledge/patterns/CODING_STANDARD.md
```

**检查方法**：写文件前先 `ls -la` 确认目录存在。
