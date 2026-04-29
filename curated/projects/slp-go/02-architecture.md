# slp-go 架构分层

## 分层调用规则

| 层级 | 可调用 | 禁止调用 |
|------|--------|----------|
| **API** | Query, Service, DAO, Model, PB, Const | - |
| **Query** | 仅内部 (验证用) | Service, DAO |
| **Service** | DAO, Model, PB, Query, Const, Library | API |
| **DAO** | 仅内部 + Model | API, Service, Library |
| **Model/PB/Const** | 仅内部 | 所有上层 |
| **Library** | 第三方服务 | Service |

## 中间件链

请求处理顺序：

```
1. CORS        - 跨域处理
2. Fire        - 速率限制/防火墙
3. Ctx         - 上下文注入 (User, Span, I18n)
4. Auth        - 身份认证
5. Error       - 错误处理
```

## 代码模板

### API Handler

```go
package api

import (
    "slp/app/pb"
    "slp/app/query"
    "slp/app/service/pay"
    "slp/library/response"
    "github.com/gogf/gf/net/ghttp"
)

var PayApi = new(payApi)  // 全局单例

type payApi struct{}

// ProductTimeLimit 限时充值商品列表
// @Tags 限时充值商品列表
// @Summary  限时充值商品列表
// @Router /go/slp/pay/productTimeLimit [post]
func (t *payApi) ProductTimeLimit(r *ghttp.Request) {
    var req *query.ReqProductTimeLimit
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.ResProductTimeLimit{
            Success: false,
            Msg:     err.Error(),
        })
        return
    }
    
    data := pay.PayTimeLimitService.Products(r.Context())
    response.Output(r, data)
}
```

### Service 层

```go
package pay

import (
    "context"
    "slp/app/pb"
    "slp/app/query"
    "slp/library"
)

var SrvPay = &servicePay{}  // 全局单例

type servicePay struct{}

func (serv *servicePay) Check(ctx context.Context, req *query.ReqPayCheck) *pb.ResPayCheck {
    rds := library.RedisClient(library.RedisPassive)
    pid, err := rds.Get(ctx, req.ClientKey).Int()
    if err != nil {
        return &pb.ResPayCheck{Success: false, Msg: err.Error()}
    }
    return rsp
}
```

### Query 层

```go
package query

type ReqPayCheck struct {
    ClientKey string `v:"client_key@required"`  // GoFrame 验证标签
}
```
