# slp-go API 层模式

## 路由规则

路由采用 4 层结构，使用**首字母小写的驼峰命名**：

```
/go/slp/{service}/{action}
         ↑        ↑
       业务模块  具体 API
```

**示例**：
- `/go/slp/userCenter/userProfile` - 用户中心 - 用户主页
- `/go/slp/toolRank/rankList` - 工具排行 - 排行榜列表

## 代码生成

使用 `slpctl code` 命令自动生成 API 代码（Handler + Service + Proto）：

```bash
# 快速生成模式
slpctl code -api /go/slp/userCenter/userProfile -desc "用户主页" -project ./slp-go

# 配置文件模式
slpctl code -config user.profile.json -project ./slp-go
```

**详情**: [`knowledge/tools/slpctl.md`](../../tools/slpctl.md)

## Handler 模板

```go
package api

import (
    "slp/app/pb"
    "slp/app/query"
    "slp/app/service/<module>"
    "slp/library/response"
    "github.com/gogf/gf/net/ghttp"
)

var <Module>Api = new(<module>Api)

type <module>Api struct{}

// 路由：/go/slp/<module>/<action>
func (m *<module>Api) <Action>(r *ghttp.Request) {
    var req *query.Req<Action>
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.Res<Action>{
            Success: false,
            Msg:     err.Error(),
        })
        return
    }
    
    data := <module>.<Module>Srv.<Action>(r.Context(), req)
    response.Output(r, data)
}
```

## Swagger 注解

```go
// @Tags 用户模块
// @Summary 用户主页
// @Router /go/slp/userCenter/userProfile [post]
```

## 路由注册

`app/app/route.go`:

```go
// 认证路由
group.Group("/", func(group *ghttp.RouterGroup) {
    group.Middleware(service.Middleware.Auth)
    group.ALL("/slp/userCenter", api.UserCenter)
})
```
