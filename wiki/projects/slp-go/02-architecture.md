---
id: slp-go-architecture
label: slp-go 架构分层
source: curated/projects/slp-go/02-architecture.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-structure
  - slp-go-api
  - slp-go-service
  - slp-go-dao
---

# slp-go 架构分层

## 分层调用规则

| 层级 | 可调用 | 禁止调用 |
|------|--------|----------|
| API | Query, Service, DAO, Model, PB, Const | - |
| Query | 仅内部 | Service, DAO |
| Service | DAO, Model, PB, Query, Const, Library | API |
| DAO | 仅内部 + Model | API, Service, Library |
| Model/PB/Const | 仅内部 | 所有上层 |
| Library | 第三方服务 | Service |

## 中间件链

| 序号 | 中间件 | 用途 |
|------|--------|------|
| 1 | CORS | 跨域处理 |
| 2 | Fire | 速率限制/防火墙 |
| 3 | Ctx | 上下文注入 (User, Span, I18n) |
| 4 | Auth | 身份认证 |
| 5 | Error | 错误处理 |

## 代码模板

### API Handler

```go
var PayApi = new(payApi)

func (t *payApi) ProductTimeLimit(r *ghttp.Request) {
    var req *query.ReqProductTimeLimit
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.ResProductTimeLimit{Success: false, Msg: err.Error()})
        return
    }
    data := pay.PayTimeLimitService.Products(r.Context())
    response.Output(r, data)
}
```

### Service 层

```go
var SrvPay = &servicePay{}

func (serv *servicePay) Check(ctx context.Context, req *query.ReqPayCheck) *pb.ResPayCheck {
    rds := library.RedisClient(library.RedisPassive)
    pid, err := rds.Get(ctx, req.ClientKey).Int()
    return &pb.ResPayCheck{Success: true, Data: pid}
}
```

## 相关知识

- [[projects/slp-go/01-structure]]
- [[patterns/architecture-layered-standard]]
