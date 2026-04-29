# 装扮类物品使用转发 - slp-go 视角

> slp-go 侧负责调用装扮服务添加有效期 + 自动佩戴

**版本**: 1.0 | **更新**: 2026-04-14

---

## 项目内职责

| 职责 | 说明 |
|------|------|
| 接收 RPC 请求 | UseDecorateCommodity 接口 |
| 查询装扮信息 | 根据 pretend_id 获取 cate_id/group_id |
| 添加有效期 | 调用 sendGroupPretend 续期 |
| 自动佩戴 | 如果用户正在使用，自动更新佩戴状态 |

---

## 核心代码

### 文件路径

```
proto/rpc/rpc_pretend.proto                              # Proto 定义
rpc/server/internal/pretend/rpc.go                       # RPC 入口
rpc/server/internal/pretend/service/pretend.go           # Service 常量
rpc/server/internal/pretend/service/pretend_discard.go   # Service 实现
```

### Proto 定义

```protobuf
// 使用装扮类物品（PHP 转发）
message UseDecorateCommodityReq{
    uint32 uid = 1;
    uint32 pretend_id = 2;
    int64 seconds = 3; // 有效期秒数
}

message UseDecorateCommodityResp{
    bool success = 1;
    string msg = 2;
}

service pretend{
    // 使用装扮类物品（PHP 转发，PHP 已扣库存）
    rpc UseDecorateCommodity(UseDecorateCommodityReq)returns(UseDecorateCommodityResp);
}
```

### RPC 实现

```go
// UseDecorateCommodity 使用装扮类物品（PHP 转发，PHP 已扣库存）
func (p *PretendRpc) UseDecorateCommodity(ctx context.Context, req *pb.UseDecorateCommodityReq, resp *pb.UseDecorateCommodityResp) error {
    err := service.PretendService.UseDecorateCommodity(ctx, req.Uid, req.PretendId, req.Seconds)
    if err != nil {
        resp.Success = false
        resp.Msg = err.Error()
        g.Log().Ctx(ctx).Error("msg", "UseDecorateCommodity", "err", err, "req", req)
        return nil
    }
    resp.Success = true
    g.Log().Ctx(ctx).Info("msg", "UseDecorateCommodity", "req", req)
    return nil
}
```

### Service 实现

```go
// UseDecorateCommodity 使用装扮类物品（PHP 已扣库存，此处只添加有效期）
func (p *Pretend) UseDecorateCommodity(ctx context.Context, uid uint32, pretendId uint32, seconds int64) (err error) {
    locker := utils.NewRedisLocker(fmt.Sprintf("pretend.useDecorateCommodity.locker.uid.%d", uid), p.rpcCache)
    err = locker.Lock(ctx, time.Second*2, func() error {
        return p.useDecorateCommodity(ctx, uid, pretendId, seconds)
    })
    return err
}

func (p *Pretend) useDecorateCommodity(ctx context.Context, uid uint32, pretendId uint32, seconds int64) (err error) {
    // 1. 根据 pretend_id 获取 cate_id 和 group_id
    result := p.GetCateIdAndGroupId(pretendId)
    if result.CateId == 0 || result.GroupId == 0 {
        return gerror.Newf("pretend_id=%d not found", pretendId)
    }

    // 2. 构造请求参数
    groupParam := &pb.PretendSendGroupPretendReq{
        Uid:           uid,
        PretendCateId: result.CateId,
        GroupId:       result.GroupId,
        Seconds:       seconds,
        GotType:       AddFragmentSourceDecorateCommodity,
        StarNum:       result.StarNum,
    }

    // 3. 调用 sendGroupPretend 添加有效期
    return p.sendGroupPretend(ctx, AddFragmentSourceDecorateCommodity, groupParam)
}
```

---

## 配置常量

### Source 类型

```go
const (
    // ... 其他 source 类型
    AddFragmentSourceDecorateCommodity = "decorate_commodity" // hugh 装扮类物品使用
)
```

### Source 注册

```go
var (
    addFragmentSourceMap = map[string]bool{
        // ... 其他 source
        AddFragmentSourceDecorateCommodity: true,
    }
)
```

---

## 依赖的内部服务

| 服务 | 方法 | 说明 |
|------|------|------|
| PretendService | GetCateIdAndGroupId | 根据 pretend_id 获取 cate_id/group_id |
| PretendService | sendGroupPretend | 添加有效期 + 自动佩戴 |

---

## 数据表

| 表 | 说明 |
|-----|------|
| `xs_user_pretend_list` | 用户装扮拥有记录（有效期存储） |
| `bbc_pretend_info` | 装扮信息表（内存缓存） |
| `bbc_pretend_group_info` | 装扮系列信息（内存缓存） |

---

## 本地测试

### 编译验证

```bash
make rpc
```

### 测试场景

1. **正常添加**：pretend_id 有效 → 有效期累加成功
2. **pretend_id 不存在**：返回错误
3. **新用户首次使用**：创建新的装扮记录
4. **老用户续期**：在原有有效期基础上累加

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `proto/rpc/rpc_pretend.proto` | Proto 定义 |
| `rpc/server/internal/pretend/rpc.go` | RPC 入口 |
| `rpc/server/internal/pretend/service/pretend.go` | Service 常量定义 |
| `rpc/server/internal/pretend/service/pretend_discard.go` | Service 实现 |

---

**分支**: `hu562/decorate-use-forward`