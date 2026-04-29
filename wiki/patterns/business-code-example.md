---
id: patterns/business-code-example
label: business-code-example
source: curated/patterns/business-code-example.md
role: 规范
compiled: 2026-04-28
source_hash: 64838328138230636a8c6c15a4a510c3
---

> 从 0 到 1 实现一个完整业务模块

## 完整文件结构

```
<project>/
├── consts/user_pet.go              # 宠物专属常量（RPC/CMD/HTTP 共享）
├── app/service/user_pet/           # Service 层
│   ├── service.go                  # 主服务（唯一对外接口）
│   ├── pet.go / feed.go / level.go / event.go  # 子模块
├── app/dao/                        # 数据访问层（代码生成）
├── app/pb/                         # Protobuf 定义（代码生成）
├── app/api/user_pet_api.go         # HTTP Handler
├── cmd/internal/user_pet_decay/    # CMD 消费者
└── rpc/server/internal/user_pet/   # RPC 服务实现
```

## 1. 常量定义（consts/user_pet.go）

```go
const ( PetStatusUnclaimed = 0; PetStatusActive = 1; PetStatusFrozen = 2 )
const ( PetTopic = "xs.user.pet"; PetDecayTopic = "xs.user.pet.decay" )

var UserPetDataKey = &RedisKey{ key: "user:pet:data:%d", ttl: 24 * time.Hour }

// 纯计算工具函数
func GetPetLevelByExp(exp int) int { ... }
func CalcDecayValue(lastFeedTime uint32) int { ... }
```

## 2. Service 层（全局单例注入）

```go
var UserPetSrv = &userPetService{
    pet: &petLogic{}, feed: &feedLogic{}, level: &levelLogic{}, event: &eventLogic{},
}
```

**调用关系**：外部 `UserPetSrv.GetPet()` → 内部 `UserPetSrv.pet.getFromCache()`

### pet.go 核心模式

```go
func (l *petLogic) Claim(ctx context.Context, uid uint32, petType uint8) (*model.UserPet, error) {
    // 1. 分布式锁  2. 检查已领取  3. 事务内创建记录  4. 写缓存
}

func (l *petLogic) getFromCache(ctx context.Context, uid uint32) (*model.UserPet, error) {
    // 先读 Redis → 未命中则读 DB → 回写缓存
}
```

### feed.go 核心模式

```go
func (l *feedLogic) Feed(ctx, req, user) (*pb.RespFeedPet, error) {
    // 1. 获取宠物  2. 检查状态  3. 增加经验  4. 检查升级
    // 5. 事务更新 DB  6. 更新缓存  7. 记录日志  8. 发送事件
}
```

## 3. API Handler

```go
func (a *userPetApi) FeedPet(r *ghttp.Request) {
    var req *query.ReqFeedPet
    r.Parse(&req)
    resp, err := user_pet.UserPetSrv.FeedPet(r.Context(), req, r.GetCtxUser())
    response.Output(r, resp)
}
```

## 4. CMD 消费者

```go
func (c *Consumer) Consume(ctx context.Context, msg *nsq.Message) error {
    var event DecayEvent
    json.Unmarshal(msg.Body, &event)
    return user_pet.UserPetSrv.ProcessDecay(ctx, event.Uid, event.Hours)
}
```

## 5. RPC 服务

```go
func (s *Service) GetUserPet(ctx context.Context, req *pb.GetUserPetReq) (*pb.GetUserPetResp, error) {
    info, err := user_pet.UserPetSrv.GetPet(ctx, req.Uid)
    return &pb.GetUserPetResp{Success: true, PetInfo: info}, nil
}
```

## 关键设计

| 设计 | 做法 |
|------|------|
| 常量定义 | `consts/` 中，RPC/CMD/HTTP 共享 |
| Service 组织 | 全局单例 + 子模块注入 |
| 跨模块调用 | `user_pet.UserPetSrv.GetPet()` |
| 无 IO 工具函数 | `consts/user_pet.go` 或 `app/utils/pet.go` |

## 新业务开发检查清单

- [ ] 在 `consts/` 定义业务常量（状态、Topic、RedisKey）
- [ ] `service.go` 定义唯一对外暴露的全局单例
- [ ] 子模块逻辑注入到主对象
- [ ] Redis Key 使用全局 `RedisKey` 结构体
- [ ] NSQ Topic 遵循 `xs.<module>.*` 命名
- [ ] Handler 只负责参数解析 + 调用 Service + 返回
