# slp-go DAO 层模式

## DAO 生成

```bash
# 单个表
slpctl gen -t xs_user_profile

# 批量生成
slpctl gen -t xs_user_profile,xs_follow,xs_fans

# 删除模式
slpctl gen -t xs_user_profile -delete
```

**详情**: [`knowledge/tools/slpctl.md`](../../tools/slpctl.md)

## 使用示例

```go
// 单条查询
user, err := dao.UserProfile.Ctx(ctx).One(uid)

// 批量查询
users, err := dao.UserProfile.Ctx(ctx).
    WhereIn("uid", []interface{}{1, 2, 3}).
    Order("created_at", "desc").
    All()

// 事务操作
tx, _ := dao.Ctx(ctx).DB().Begin()
dao.UserProfile.Ctx(ctx).DB(tx).Update(...)
tx.Commit()
```

## 避免 N+1

```go
// ❌ 错误
for _, uid := range uids {
    user, _ := dao.UserProfile.One(uid)
}

// ✅ 正确
users, _ := dao.UserProfile.WhereIn("uid", uids).All()
```
