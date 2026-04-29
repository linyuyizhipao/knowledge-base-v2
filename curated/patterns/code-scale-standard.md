# 代码规模标准

> 函数和文件的合理规模控制

**版本**: 1.0 | **最后更新**: 2026-04-09

---

## 🎯 核心原则

**一个函数只做一件事，一个文件只负责一个领域**

代码规模控制的核心不是"行数越少越好"，而是：
1. **可读性** - 其他人能快速理解这段代码在做什么
2. **可维护性** - 修改一个功能时，影响范围是可控的
3. **可测试性** - 每个函数可以独立测试

---

## 📏 推荐规模

### 函数级别

| 函数类型 | 推荐行数 | 上限 | 说明 |
|----------|---------|------|------|
| **Handler** | 10-25 行 | 30 行 | 只做参数解析 + 调用 service + 返回响应 |
| **Service** | 20-50 行 | 100 行 | 包含完整业务逻辑 |
| **DAO** | 5-25 行 | - | 代码生成，保持极简 |
| **工具函数** | 5-20 行 | 30 行 | 单一功能封装 |

### 文件级别

| 文件类型 | 推荐行数 | 上限 | 说明 |
|----------|---------|------|------|
| **API Handler** | 50-200 行 | 300 行 | 按业务功能聚合 handler |
| **Service（根目录）** | 100-300 行 | 500 行 | 基础服务（firewall、middleware） |
| **Service（子目录）** | 100-400 行 | 500 行 | 业务服务子模块 |
| **DAO** | 25 行左右 | 50 行 | 代码生成 |

---

## ✅ 好的代码示例

### 示例 1：极简 Handler（推荐模式）

**文件**：`app/api/transfer.go`

```go
func (*transferApi) Show(r *ghttp.Request) {
    output := transfer.TransferService.Show(r.Context())
    response.Output(r, output)
}
```

- **仅 4 行代码**
- 只做三件事：调 service → 输出响应

---

### 示例 2：标准 Handler 模式

**文件**：`app/api/wave.go`

```go
func (w *waveApi) Config(request *ghttp.Request) {
    var req *query.ReqWaveConfig
    if err := request.Parse(&req); err != nil {
        response.Output(request, &pb.ApiWaveConfigResponse{
            Success: false,
            Message: err.Error(),
        })
        return
    }
    response.Output(request, wave.Config(request.Context(), req))
}
```

- **约 15 行**
- 标准流程：参数解析 → 错误处理 → 调用 service → 返回

---

### 示例 3：合理的 Service 函数

**文件**：`app/service/context_service.go`

```go
// Init: 5 行
func Init() {
    _context = context.Background()
}

// Get: 12 行
func Get() context.Context {
    if _context == nil {
        return context.Background()
    }
    return _context
}

// SetUser: 5 行
func (c *Context) SetUser(user *model.User) {
    c.user = user
}
```

- 小函数职责单一，命名即说明功能

---

## ❌ 反模式

### 反模式 1：超长函数

```go
// ❌ 错误 - 函数超过 100 行
func (s *service) ProcessComplexLogic(ctx context.Context, req *Request) (*Response, error) {
    // 1000 行代码...
    // 包含了参数验证、业务逻辑、错误处理、数据组装...
}
```

**问题**：
- 难以理解整体流程
- 修改一处可能影响多处
- 难以编写单元测试

**正确做法**：按功能步骤拆分

```go
// ✅ 正确 - 拆分为多个小函数
func (s *service) ProcessComplexLogic(ctx context.Context, req *Request) (*Response, error) {
    if err := s.validateRequest(req); err != nil {
        return nil, err
    }
    
    data, err := s.fetchData(ctx, req)
    if err != nil {
        return nil, err
    }
    
    result, err := s.processData(ctx, data)
    if err != nil {
        return nil, err
    }
    
    return s.assembleResponse(result), nil
}

func (s *service) validateRequest(req *Request) error {
    // 20 行：只做参数验证
}

func (s *service) fetchData(ctx context.Context, req *Request) (*Data, error) {
    // 30 行：只做数据获取
}

func (s *service) processData(ctx context.Context, data *Data) (*Result, error) {
    // 40 行：只做数据处理
}

func (s *service) assembleResponse(result *Result) *Response {
    // 15 行：只做响应组装
}
```

---

### 反模式 2：过度拆分

```go
// ❌ 错误 - 为了"小而小"过度拆分
func process1(data) { processData(data) }
func processData(d) { validate(d); transform(d) }
func validate(d) { check1(d); check2(d) }
func check1(d) { ... }
func check2(d) { ... }
```

**问题**：
- 函数链过长，阅读时需要跳来跳去
- 每个函数都太简单，失去了独立存在的意义
- 增加了文件数量和导航成本

**正确做法**：保持合理的函数粒度

```go
// ✅ 正确 - 适度聚合
func process(data) {
    // 10 行：参数验证
    if !isValid(data) { return error }
    
    // 15 行：数据转换
    transformed := transform(data)
    
    // 20 行：核心处理
    result := doWork(transformed)
    
    return result
}
```

---

### 反模式 3：超大文件

```go
// ❌ 错误 - 一个文件包含所有功能
// app/service/user.go - 2000 行
// 包含了用户信息、用户关系、用户动态、用户成就...
```

**问题**：
- 难以导航和定位
- 职责不清晰
- 合并冲突概率高

**正确做法**：按业务领域拆分

```
app/service/user/
├── info.go        # 用户信息（300 行）
├── relation.go    # 用户关系（200 行）
├── feed.go        # 用户动态（150 行）
└── achievement.go # 用户成就（180 行）
```

---

## 🧭 判断标准

### 函数是否需要拆分？

当你发现一个函数中出现以下情况时，考虑拆分：

| 信号 | 说明 | 建议 |
|------|------|------|
| 注释里有"第一步"、"第二步" | 函数内部有明显的步骤划分 | 按步骤拆分 |
| 局部变量超过 10 个 | 函数在"记住"太多东西 | 考虑拆分或用结构体封装 |
| if/for 嵌套超过 3 层 | 逻辑过于复杂 | 抽取为独立函数 |
| 无法用一句话描述函数功能 | 职责不单一 | 按功能拆分 |

---

### 文件是否需要拆分？

| 信号 | 说明 | 建议 |
|------|------|------|
| 文件名是 `utils.go` 或 `common.go` | 可能是"杂物箱" | 按功能重新组织 |
| 一个文件超过 500 行 | 阅读成本高 | 按功能模块拆分 |
| 文件里有明显的"区块"注释 | 自然的功能边界 | 拆分为独立文件 |

---

## 📋 检查清单

开始编码前，问自己：

- [ ] 这个函数能否用一句话描述它的功能？
- [ ] 如果别人要看懂这个函数，需要跳进多少个被调用的函数？
- [ ] 这个文件里的所有函数，是否都属于同一个业务领域？
- [ ] 如果我要修改这个函数，影响范围有多大？

写完代码后，检查：

- [ ] Handler 函数不超过 30 行
- [ ] Service 函数不超过 100 行
- [ ] API 文件不超过 300 行
- [ ] Service 文件不超过 500 行

---

## 🔗 相关文档

- [[event-extension-guide.md]] - 事件开发规范（含观察者模式）
- [[cmd-module-standard.md]] - CMD 模块标准

---

**参考项目数据**：基于 slp-go（190 个 API 模块、183 个 Service 模块）和 slp-room 的实际代码分析
