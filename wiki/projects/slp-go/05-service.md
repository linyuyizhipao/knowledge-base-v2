---
id: slp-go-service
label: slp-go Service 层模式
source: curated/projects/slp-go/05-service.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-architecture
  - slp-go-dao
---

# slp-go Service 层模式

## Service 模板

```go
package <module>

var <Module>Srv = &service{}

type service struct{}

func (s *service) Action(ctx context.Context, req *query.Req<Action>) *pb.Res<Action> {
    // 1. 参数验证  2. 缓存查询  3. 数据库查询  4. 返回
}
```

## 事务处理

```go
func (s *service) Transfer(ctx context.Context, from, to int) error {
    tx, _ := dao.Ctx(ctx).DB().Begin()
    defer tx.Rollback()
    dao.User.Ctx(ctx).DB(tx).Update(...)
    return tx.Commit()
}
```

## 中间件

CORS（跨域） | Fire（速率限制） | Ctx（上下文注入） | Auth（身份认证） | Error（错误处理） | Trace（链路追踪）
