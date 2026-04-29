---
id: patterns/architecture-layered-standard
label: architecture-layered-standard
source: /Users/hugh/project/my-wiki/curated/patterns/architecture-layered-standard.md
role: 规范
compiled: 2026-04-28
source_hash: 1a13ee05d580c0470ce33610e94a3abe
---

> 明确 HTTP、RPC、CMD、Service、Domain(Data 层) 的职责边界与调用规则

## 分层调用规则（严格）

```
HTTP / RPC / CMD（接入层）→ 只能调用 → app/service/（业务逻辑层）→ 只能调用 → app/domain/（数据访问层）→ app/dao/ + rpc/client/
```

### 各层职责

| 层级 | 职责 | 禁止 | 位置 |
|------|------|------|------|
| **HTTP/RPC/CMD** | 协议转换、参数校验、响应输出 | 不可直接调用 DAO/domain | `app/api/`, `rpc/server/internal/`, `cmd/internal/` |
| **Service** | 业务逻辑、事务、事件发送 | 不可直接调 DAO，必须通过 domain | `app/service/<business>/` |
| **Domain** | DAO 操作、RPC 调用、数据组装、事件发送 | 不可包含复杂业务逻辑 | `app/domain/<business>/` |
| **DAO/RPC Client** | 底层数据访问 | 不可包含任何逻辑 | `app/dao/`, `rpc/client/` |

**Domain 层说明**：虽然叫 `domain`，实际职责是**数据访问层 + 事件发送**，不是 DDD 领域层。

## 核心规则

### 规则 1：接入层只调 Service

```go
// ✅ Handler 调 Service
info, err := service_user_pet.GetPet(ctx, uid)

// ❌ 接入层直接调 DAO
exist, err := dao.XsUserFriend.Ctx(ctx).One("uid = ?", uid)
```

### 规则 2：Service 封装业务逻辑

职责：业务规则验证、事务操作、调用 domain 层、发送事件。

```go
func ClaimPet(ctx context.Context, uid uint32, petType uint8) (*model.UserPet, error) {
    // 1. 分布式锁 → 2. 事务内调用 domain 层 → 3. 发送领域事件
}
```

### 规则 3：Domain 封装数据访问

职责：封装 DAO 操作、RPC 调用、数据组装、事件发送。**不包含业务规则验证和事务**。

```go
func GetPetByUid(ctx context.Context, uid uint32) (*model.UserPet, error) {
    return dao.UserPet.Ctx(ctx).Where("uid", uid).One()
}
```

### 规则 4：Domain 不能被 RPC 直接调用

依赖方向：`RPC → Service → Domain → DAO/RPC Client`。避免循环依赖。

## 检查清单

- [ ] 常量定义在 `consts/<business>.go`
- [ ] Domain 层在 `app/domain/<business>/`
- [ ] Service 层在 `app/service/<business>/`
- [ ] HTTP/RPC/CMD 只调用 Service 层
- [ ] Service 调用 Domain，不直接调 DAO
- [ ] Domain 不包含复杂业务逻辑
- [ ] Domain 不能被 RPC 直接调用
