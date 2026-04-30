# 开发规范

> 所有代码必须遵循的规范
> 
> **🚨 核心红线：开始任何编码任务前，必须先执行"步骤 0：创建功能分支"**
> -严禁在 dev 分支开发
> -严禁直接在 master 开发
> -严禁从 dev 创建功能分支
> -必须从最新 master 创建功能分支

## ⚡ slpctl 生成的代码能力（编码前先了解）

**不要只记住"禁止什么"，先了解 slpctl 为你生成了什么**：

### slpctl code（API 骨架生成）

```bash
slpctl code -api /go/slp/<service>/<action> -desc "描述" -project ./<项目>
```

**生成后自动拥有**：

| 生成的内容 | AI 需要做的 |
|-----------|------------|
| `api/handler/` — Handler 文件（参数解析 + 调用 Service + 返回） | 不需要改，只注册路由 |
| `api/service/` — Service 接口定义 + 实现骨架 | **填充业务逻辑**，这是你唯一需要写代码的地方 |
| `api/dao/` — DAO 接口定义 | 不需要改，接口已定义好 |
| `api/router/` — 路由注册 | 不需要改，工具已自动注册 |

**流程**: 先生成骨架 → 在 Service 中填充业务逻辑 → 完成。**不要跳过生成步骤直接手写任何 API 相关代码**。

### slpctl gen（数据库表代码生成）

```bash
slpctl gen -t <表名> -d <数据库>
```

**生成后自动拥有**：

| 生成的内容 | 说明 |
|-----------|------|
| `app/dao/internal/*.go` — DAO 实现（CRUD、批量查询、分页） | 包含 `Find`、`FindBatch`、`Where`、`All` 等方法 |
| `app/pb/entity_*.pb.go` — 实体定义（Protobuf） | 与数据库表结构一一对应 |
| `proto/entity_*.proto` — Protobuf 定义 | 用于 RPC 通信和序列化 |

**流程**: DB 字段变更时 → 先 `slpctl gen -t <表名>` 重新生成 → 使用新生成的 DAO 方法写业务逻辑。**不要手动编辑 DAO/Model 文件，下次 gen 会被覆盖**。

### slpctl 生成的代码为什么优先使用

1. **一致性**：全项目所有 API 都是同一套骨架，维护成本低
2. **完整性**：自动生成 DAO CRUD、路由注册、Protobuf 实体，手动写容易漏
3. **可维护**：DB 表变更时 `slpctl gen` 一键同步，不需要逐个改文件
4. **规范化**：分层、命名、接口定义都符合项目规范，不需要 AI 自己判断

---

## ⚠️ 核心禁令

### 1. 禁止手动编写 API 代码（强制）

**所有新增 API 必须使用 `slpctl code` 生成骨架代码，然后填充业务逻辑。**

```bash
# ❌ 错误：手动创建 api/handler, service, dao 文件
# ✅ 正确：使用工具生成骨架
slpctl code -api /go/slp/user/profile -desc "用户 profile"
```

**生成后做什么**：
1. 工具会自动生成 Handler、Service 接口、DAO 接口、路由注册
2. 你只需要填充 Service 中的业务逻辑
3. 禁止跳过工具直接手写任何 API 相关代码

**详情**: [`knowledge/tools/slpctl.md`](./knowledge/tools/slpctl.md)

### 2. 禁止在循环中进行 I/O 操作

**I/O 判定口径**：数据库（DAO）、缓存（Redis 等）、RPC/HTTP 调用、消息队列（Kafka/NSQ）、文件读写、以及任何可能阻塞的网络/磁盘访问，均视为 I/O。

```go
// ❌ 错误 - N+1 查询
for _, uid := range userIDs {
    user := dao.User.Find(uid)
}

// ✅ 正确 - 批量查询
users := dao.User.FindBatch(userIDs)
```

### 3. 禁止阻塞主 goroutine

```go
// ❌ 错误 - 同步处理耗时操作
result := ai.Generate(...)  // 2-5 秒

// ✅ 正确 - 异步处理
taskID := createTask(req)
taskBytes, _ := json.Marshal(g.Map{"task_id": taskID})
_ = library.NsqClient().SendBytes("xs.task.generate", taskBytes, 2*time.Second)
return TaskID: taskID
```

### 4. 禁止绕过事件总线

```go
// ❌ 错误 - 直接模块调用
orderService.CreateOrder(...)

// ✅ 正确 - 发布事件
eventBus.Publish("order.created", &OrderCreatedEvent{...})
```

### 5. 禁止函数/文件过大

**函数规模上限**：
- Handler 函数：≤ 30 行（只做参数解析 + 调用 service + 返回）
- Service 函数：≤ 100 行（完整业务逻辑）

**文件规模上限**：
- API Handler 文件：≤ 300 行（按业务功能聚合）
- Service 文件：≤ 500 行（复杂功能用子目录）

```go
// ❌ 错误 - Service 函数超过 100 行
func (s *service) Process(ctx context.Context, req *Request) (*Response, error) {
    // 150 行代码...
}

// ✅ 正确 - 按功能拆分
func (s *service) Process(ctx context.Context, req *Request) (*Response, error) {
    data := s.fetchData(ctx, req)    // 30 行
    result := s.processData(data)    // 40 行
    return s.assemble(result)        // 15 行
}
```

**详情**: [`knowledge/patterns/code-scale-standard.md`](./knowledge/patterns/code-scale-standard.md)

### 6. 禁止不缓存的连表查询

```go
// ❌ 错误 - 连表查询无缓存
// ✅ 正确 - 使用缓存层
```

### 7. 消息队列选型（以现状为准）

当前仍以 NSQ 为主，新需求默认沿用项目既有队列与消费模型；如需引入 Kafka，必须在需求/PR 中说明原因与收益，并补齐对应的监控、告警与回滚方案。

### 8. 分支强制约束（红线禁令）

**所有新需求开发必须遵守**：
1. **禁止在 dev 分支开发** - dev 只用于合入，不作为开发分支
2. **禁止在 master 分支直接开发** - 必须从 master 创建功能分支
3. **禁止从 dev 创建功能分支** - 功能分支必须从 master 创建
4. **禁止跳过步骤 0** - 开始任何 coding 前必须先执行"步骤 0：创建功能分支"

**强制检查命令**（AI 启动新需求时必须执行）：
```bash
# 检查当前是否在 master
git rev-parse --abbrev-ref HEAD | grep -q master || (echo "❌ 错误：必须在 master 分支创建功能分支" && exit 1)

# 检查 master 是否最新
git fetch origin master >/dev/null 2>&1
git merge-base --is-ancestor origin/master HEAD || (echo "❌ 错误：master 不是最新的，请先 git pull origin master" && exit 1)

# 检查当前是否有未提交的修改
git diff --quiet || (echo "❌ 错误：当前有未提交的修改，请先 stash 或 commit" && exit 1)
```

---

## 9. 代码组织结构规范（AI 必读）

### 核心原则

**一个行为 = 一个文件 + 一个大写入口（对外）+ 小写实现（对内）**

```
一个行为一个文件
├─ 大写方法 Process()  - 对外唯一入口
└─ 小写方法           - 内部实现（loadData, checkX, matchX...）
```

### ⛔ 禁令

| 禁令 | 说明 |
|------|------|
| **禁止循环内 IO** | `for` 循环里不能有 `dao.Where()` |
| **禁止重复 IO** | 同一流程查同一张表（除非必要） |
| **禁止逻辑散落** | 一个行为的代码不要拆到多个文件 |

### ✅ 必做

| 必做               | 说明                            |
| ---------------- | ----------------------------- |
| **简单行为**（<200 行） | 直接一个大写方法搞定                    |
| **复杂行为**（>200 行） | 一个大写入口 + 多个小写实现               |
| **IO 尽量集中**      | 能提前查的放 `loadData()`，依赖型放对应逻辑后 |
| **同类型批量查**       | 多个同类数据用 `WhereIn`             |

### 📝 模板

#### 场景 A：简单行为（<200 行）

```go
func GetUserProfile(ctx context.Context, uid uint32) (*pb.UserProfile, error) {
    user, _ := dao.User.Where("uid=?", uid).One()
    return &pb.UserProfile{Uid: user.Uid, Name: user.Name}, nil
}
```

#### 场景 B：复杂行为（>200 行）

```go
type Handler struct {
    ctx context.Context
    uid uint32
    
    user  *pb.User
    pond  *pb.Fishpond
    fish  []*pb.Fish
}

// 对外：一个大写方法（唯一入口）
func (h *Handler) Process() error {
    // 1. IO 集中
    if err := h.loadData(); err != nil {
        return err
    }
    
    // 2. 逻辑解耦
    if err := h.checkEnergy(); err != nil {
        return err
    }
    if err := h.matchFish(); err != nil {
        return err
    }
    if err := h.updateDB(); err != nil {
        return err
    }
    
    return nil
}

// 内部：IO（小写）
func (h *Handler) loadData() error {
    h.user, _ = dao.User.Where("uid=?", h.uid).One()
    h.pond, _ = dao.Fishpond.Where("uid=?", h.uid).One()
    h.fish, _ = dao.Fish.Where("pond_id=?", h.pond.Id).All()
    return nil
}

// 内部：逻辑（小写）
func (h *Handler) checkEnergy() error { /* 纯逻辑 */ }
func (h *Handler) matchFish() error   { /* 纯逻辑 */ }
func (h *Handler) updateDB() error    { /* 写入 */ }
```

### 🔍 自检清单

| 检查项             | 合格   |
| --------------- | ---- |
| 简单行为 < 200 行？   | 是/否  |
| 一个行为一个文件？       | 是    |
| 复杂行为有大写入口？      | 是    |
| `for` 里有 `dao`？ | 无    |
| 同表重复查？          | 尽量避免 |

---

## ✅ 代码实现共识

### 1. 遍历表必须使用 TableLoopHandle

如果需要遍历某个表，且该表存在主键 id，必须使用 `table_manage.TableLoopHandle`：

```go
// ❌ 错误 - 直接遍历
rows := dao.XsUser.FindAll()
for _, row := range rows {
    // 处理逻辑
}

// ✅ 正确 - 使用 TableLoopHandle
table_manage.TableLoopHandle(ctx, &dao.XsUser{}, func(row interface{}) error {
    // 处理逻辑
    return nil
})
```

**原因**: `TableLoopHandle` 内置了分页、错误处理、日志记录等机制，避免大表遍历导致的内存和性能问题。

### 2. 业务代码可读性优先

编写业务代码时，**可读性优先于性能**，除非两者性能差异巨大：

```go
// ✅ 正确 - 清晰的业务逻辑
if user.IsActive() && user.HasPermission() && !user.IsBanned() {
    return true
}

// ❌ 错误 - 过度优化的位运算
if (user.flags & 0x07) == 0x05 {
    return true
}
```

**原则**:
- 业务代码的首要目标是**易于理解和维护**
- 只有当性能差异达到**数量级**时才考虑牺牲可读性
- 算法优化应有明确的性能数据支撑

---

## ✅ 编码检查清单

开始 coding 前，确认：

- [ ] **新增 API 必须使用 `slpctl code` 生成骨架**（禁止手写 Handler/Service/DAO）
- [ ] 新增表/修改表使用 `slpctl gen` 生成 DAO/Model
- [ ] 无循环 IO 风险
- [ ] 耗时操作已异步处理
- [ ] 模块间通信通过事件总线
- [ ] Handler 函数 ≤ 30 行，Service 函数 ≤ 100 行
- [ ] 常量定义在 `consts/` 或模块 `const.go`
- [ ] Service 有唯一对外暴露对象（全局单例）
- [ ] 子模块方法注入到主对象，不直接暴露

**业务开发规范**: [`knowledge/patterns/business-module-standard.md`](./knowledge/patterns/business-module-standard.md)

## 📋 脚本使用

```bash
# 问题捕获
./capture.sh "问题描述" -t anti -f ./file.go -d "详细描述"

# 代码检查
./check.sh ./app/service/
```

---

**版本**: 3.0 | **更新**: 2026-04-05
