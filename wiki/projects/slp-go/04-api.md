---
id: slp-go-api
label: slp-go API 层模式
source: curated/projects/slp-go/04-api.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-architecture
  - slp-go-service
---

# slp-go API 层模式

## 路由规则

| 格式 | 说明 |
|------|------|
| `/go/slp/{service}/{action}` | 4 层结构，首字母小写驼峰 |

**示例**:
| 路由 | 说明 |
|------|------|
| `/go/slp/userCenter/userProfile` | 用户中心 - 用户主页 |
| `/go/slp/toolRank/rankList` | 工具排行 - 排行榜列表 |

## 代码生成

| 命令 | 用途 |
|------|------|
| `slpctl code -api /go/slp/userCenter/userProfile -desc "用户主页"` | 快速生成 |
| `slpctl code -config user.profile.json` | 配置文件模式 |

## Handler 模板

```go
var <Module>Api = new(<module>Api)

func (m *<module>Api) <Action>(r *ghttp.Request) {
    var req *query.Req<Action>
    if err := r.Parse(&req); err != nil {
        response.Output(r, &pb.Res<Action>{Success: false, Msg: err.Error()})
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

```go
group.Group("/", func(group *ghttp.RouterGroup) {
    group.Middleware(service.Middleware.Auth)
    group.ALL("/slp/userCenter", api.UserCenter)
})
```