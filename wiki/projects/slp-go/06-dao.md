---
id: slp-go-dao
label: slp-go DAO 层模式
source: curated/projects/slp-go/06-dao.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-service
  - slp-go-development
---

# slp-go DAO 层模式

## DAO 生成

```bash
slpctl gen -t xs_user_profile              # 单个表
slpctl gen -t xs_user_profile,xs_follow    # 批量
slpctl gen -t xs_user_profile -delete      # 删除
```

## 使用示例

```go
dao.UserProfile.Ctx(ctx).One(uid)                          // 单条
dao.UserProfile.Ctx(ctx).WhereIn("uid", uids).All()        // 批量
dao.Ctx(ctx).DB().Begin() ... dao.UserProfile.Ctx(ctx).DB(tx).Update(...) ... tx.Commit()  // 事务
```

## 避免 N+1

```go
// ❌ for _, uid := range uids { dao.UserProfile.One(uid) }
// ✅ dao.UserProfile.WhereIn("uid", uids).All()
```
