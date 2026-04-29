# slp-room 架构分层

> 四层架构：API → Busi → Service → DAO

**最后更新**: 2026-04-05

---

## 架构总览

```
┌─────────────────────────────────────────────────────────┐
│                      HTTP Request                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  API Layer (app/api/)                                   │
│  - 请求参数解析                                          │
│  - 参数校验                                               │
│  - 响应格式封装                                          │
│  - 不涉及业务逻辑                                        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Busi Layer (app/busi/)                                 │
│  - 复杂业务逻辑                                          │
│  - 跨模块业务编排                                        │
│  - 业务规则校验                                          │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Service Layer (app/service/)                           │
│  - 核心业务逻辑                                          │
│  - 事务管理                                              │
│  - 跨 DAO 协调                                            │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  DAO Layer (app/dao/)                                   │
│  - 数据库 CRUD                                           │
│  - 单表查询                                              │
│  - 缓存读写                                              │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Model Layer (app/model/)                               │
│  - 数据模型定义                                          │
│  - JSON/DB 映射                                          │
└─────────────────────────────────────────────────────────┘
```

---

## 各层职责

### API 层

**位置**: `app/api/`

**职责**：
- 解析 HTTP 请求参数
- 参数合法性校验
- 调用 Busi/Service 层
- 封装响应格式

**禁止**：
- ❌ 直接调用 DAO
- ❌ 编写复杂业务逻辑
- ❌ 直接返回数据库模型

**示例**：

```go
// app/api/room.go
func (api *Room) Info(ctx context.Context, rid uint32) (*RoomInfoResponse, error) {
    // 1. 参数校验（由框架完成）
    
    // 2. 调用业务层
    roomInfo, err := busi.RoomInfo.Get(ctx, rid)
    if err != nil {
        return nil, err
    }
    
    // 3. 封装响应
    return &RoomInfoResponse{
        Rid:   roomInfo.Rid,
        Name:  roomInfo.Name,
        Hot:   roomInfo.Hot,
        Owner: roomInfo.Owner,
    }, nil
}
```

---

### Busi 层（业务层）

**位置**: `app/busi/`

**职责**：
- 复杂业务逻辑实现
- 跨 Service 协调
- 业务规则校验
- 数据组装

**特点**：
- 无状态，可并发调用
- 可调用多个 Service
- 可调用 DAO
- 可调用 CacheModel

**示例**：

```go
// app/busi/room_user.go
package busi

// RoomUser 房间用户业务
var RoomUser = &roomUser{}

type roomUser struct{}

// GetRoomUserList 获取房间用户列表
func (b *roomUser) GetRoomUserList(ctx context.Context, rid uint32) ([]*UserInfo, error) {
    // 1. 从缓存获取房间用户 ID 列表
    uidList, err := cachemodel.XsRoomUser.GetRoomUids(ctx, rid)
    if err != nil {
        return nil, err
    }
    
    // 2. 批量获取用户信息
    users, err := dao.XsUser.BatchGet(ctx, uidList)
    if err != nil {
        return nil, err
    }
    
    // 3. 数据组装
    var userList []*UserInfo
    for _, u := range users {
        userList = append(userList, &UserInfo{
            Uid:      u.Uid,
            Nickname: u.Nickname,
            Avatar:   u.Avatar,
        })
    }
    
    return userList, nil
}
```

---

### Service 层

**位置**: `app/service/`

**职责**：
- 核心业务逻辑
- 事务管理
- 跨 DAO 协调
- 业务状态变更

**特点**：
- 有状态（可能包含事务）
- 可调用 DAO
- 可调用其他 Service
- 不可调用 Busi

**示例**：

```go
// app/service/room/enter.go
package room

// EnterRoom 用户进入房间
func (s *Service) EnterRoom(ctx context.Context, uid, rid uint32) error {
    tx, err := dao.DB().Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback()
    
    // 1. 检查房间状态
    room, err := dao.XsChatroom.Ctx(ctx).FindOne(rid)
    if err != nil {
        return err
    }
    if room.Status != STATUS_NORMAL {
        return errors.New("房间已关闭")
    }
    
    // 2. 添加房间用户
    _, err = dao.XsChatroomUser.Ctx(ctx).Insert(gdb.Map{
        "rid": rid,
        "uid": uid,
        "ts":  time.Now().Unix(),
    })
    if err != nil {
        return err
    }
    
    // 3. 更新房间在线人数
    _, err = dao.XsChatroom.Ctx(ctx).Data(gdb.Map{
        "online_num": gdb.Raw("online_num+1"),
    }).Where("rid", rid).Update()
    
    // 4. 提交事务
    return tx.Commit()
}
```

---

### DAO 层

**位置**: `app/dao/`

**职责**：
- 数据库 CRUD
- 单表查询
- 缓存读写（CacheModel）

**特点**：
- 由代码生成工具生成
- 每个表对应一个 DAO
- 不包含业务逻辑
- 只处理单表

**示例**：

```go
// app/dao/xs_chatroom.go (自动生成)
package dao

var XsChatroom = xsChatroom{}

type xsChatroom struct{}

// FindOne 根据主键查询
func (d *xsChatroom) FindOne(ctx context.Context, rid uint32) (*model.XsChatroom, error) {
    var m *model.XsChatroom
    err := d.Where("rid", rid).Scan(&m)
    return m, err
}

// BatchGet 批量查询
func (d *xsChatroom) BatchGet(ctx context.Context, rids []uint32) ([]*model.XsChatroom, error) {
    var ms []*model.XsChatroom
    err := d.WhereIn("rid", rids).Scan(&ms)
    return ms, err
}

// Update 更新
func (d *xsChatroom) Update(ctx context.Context, data gdb.Map, rid uint32) (int64, error) {
    result, err := d.Ctx(ctx).Data(data).Where("rid", rid).Update()
    if err != nil {
        return 0, err
    }
    return result.RowsAffected()
}
```

---

### Model 层

**位置**: `app/model/`

**职责**：
- 数据模型定义
- JSON 序列化/反序列化
- DB 映射

**示例**：

```go
// app/model/xs_chatroom.go
package model

// XsChatroom 房间表
type XsChatroom struct {
    Rid       uint32 `json:"rid" orm:"rid"`         // 房间 ID
    Uid       uint32 `json:"uid" orm:"uid"`         // 房主 UID
    Name      string `json:"name" orm:"name"`       // 房间名称
    Status    int    `json:"status" orm:"status"`   // 状态：1-正常，0-关闭
    OnlineNum int    `json:"online_num" orm:"online_num"` // 在线人数
    Hot       int64  `json:"hot" orm:"hot"`         // 热度
    CreatedAt int64  `json:"created_at" orm:"created_at"`
    UpdatedAt int64  `json:"updated_at" orm:"updated_at"`
}

// TableName 表名
func (m *XsChatroom) TableName() string {
    return "xs_chatroom"
}
```

---

### CacheModel 层

**位置**: `app/cachemodel/`

**职责**：
- Redis 缓存封装
- 缓存更新策略
- 缓存预热

**示例**：

```go
// app/cachemodel/xs_chatroom.go
package cachemodel

var XsChatroom = &chatroomCache{}

type chatroomCache struct {
    rds *redis.Client
}

// Get 从缓存获取房间信息
func (c *chatroomCache) Get(ctx context.Context, rid uint32) (*model.XsChatroom, error) {
    key := fmt.Sprintf("xs_chatroom:%d", rid)
    data, err := c.rds.Get(ctx, key).Bytes()
    if err != nil {
        return nil, err
    }
    
    var m *model.XsChatroom
    if err := json.Unmarshal(data, &m); err != nil {
        return nil, err
    }
    return m, nil
}

// Set 设置缓存
func (c *chatroomCache) Set(ctx context.Context, room *model.XsChatroom, ttl time.Duration) error {
    key := fmt.Sprintf("xs_chatroom:%d", room.Rid)
    data, _ := json.Marshal(room)
    return c.rds.Set(ctx, key, data, ttl).Err()
}

// Del 删除缓存
func (c *chatroomCache) Del(ctx context.Context, rid uint32) error {
    key := fmt.Sprintf("xs_chatroom:%d", rid)
    return c.rds.Del(ctx, key).Err()
}
```

---

## 层间调用规则

### ✅ 允许的调用

```
API → Busi → Service → DAO → Model
  │     │        │
  │     └────────┘
  └───────────────→
```

### ❌ 禁止的调用

```
❌ API → DAO (绕过业务层)
❌ Service → API (反向调用)
❌ DAO → Service (反向调用)
❌ Model → 任何层 (被动数据)
❌ Busi → Busi (跨模块调用需通过 Service)
```

---

## Query 层（查询组合层）

**位置**: `app/query/`

**职责**：
- 组合查询条件
- 分页封装
- 排序封装

**示例**：

```go
// app/query/room_query.go
package query

type RoomQuery struct {
    Keyword    string `json:"keyword"`     // 搜索关键词
    RoomType   int    `json:"room_type"`   // 房间类型
    MinHot     int64  `json:"min_hot"`     // 最小热度
    MaxHot     int64  `json:"max_hot"`     // 最大热度
    Page       int    `json:"page"`        // 页码
    PageSize   int    `json:"page_size"`   // 每页数量
    SortBy     string `json:"sort_by"`     // 排序字段
    SortOrder  string `json:"sort_order"`  // 排序方向
}

// Build 构建查询条件
func (q *RoomQuery) Build() *gdb.Condition {
    cond := gdb.NewCondition()
    
    if q.Keyword != "" {
        cond.And("name LIKE ?", "%"+q.Keyword+"%")
    }
    if q.RoomType > 0 {
        cond.And("room_type", q.RoomType)
    }
    if q.MinHot > 0 {
        cond.And("hot >= ?", q.MinHot)
    }
    if q.MaxHot > 0 {
        cond.And("hot <= ?", q.MaxHot)
    }
    
    cond.Limit(q.PageSize).Offset((q.Page - 1) * q.PageSize)
    cond.OrderBy(q.SortBy + " " + q.SortOrder)
    
    return cond
}
```

---

## 模块统计

### API 模块 (18+)

| 模块 | 路由前缀 | 说明 |
|------|---------|------|
| Room | `/go/room/` | 房间核心 API |
| Mic | `/go/room/mic/` | 麦位操作 |
| Action | `/go/room/action/` | 进房/离开/踢人 |
| Gift | `/go/room/gift/` | 礼物打赏 |
| PK | `/go/room/pk/` | 房间 PK |
| GrabMic | `/go/room/grabmic/` | 抢唱玩法 |
| Auction | `/go/room/auction/` | 拍卖玩法 |
| CPLink | `/go/room/cplink/` | CP 连线 |

### Busi 模块 (60+)

| 模块 | 说明 |
|------|------|
| RoomState | 房间状态管理 |
| RoomUser | 房间用户管理 |
| RoomGift | 房间礼物 |
| RoomHistory | 房间历史 |
| RoomOnline | 房间在线人数 |
| RoomTransfer | 房间转让 |

### Service 模块 (97+)

| 模块 | 说明 |
|------|------|
| RoomService | 房间服务 |
| UserService | 用户服务 |
| GiftService | 礼物服务 |
| PayService | 支付服务 |

---

## 最佳实践

### 1. API 层最佳实践

```go
// ✅ 推荐：简洁的请求处理
func (api *Room) Info(ctx context.Context, req *RoomInfoReq) (*RoomInfoResp, error) {
    // 参数校验由框架完成
    room, err := busi.RoomInfo.Get(ctx, req.Rid)
    if err != nil {
        return nil, err
    }
    return convertRoomResp(room), nil
}

// ❌ 错误：在 API 层写业务逻辑
func (api *Room) Info(ctx context.Context, req *RoomInfoReq) (*RoomInfoResp, error) {
    // 不应该在这里写复杂逻辑
    room := dao.XsChatroom.FindOne(req.Rid)
    // ... 一堆业务逻辑
}
```

### 2. Busi 层最佳实践

```go
// ✅ 推荐：组合多个 Service
func (b *roomGift) SendGift(ctx context.Context, fromUid, toUid, rid, giftId uint32) error {
    // 1. 检查房间状态
    room, err := busi.RoomInfo.Get(ctx, rid)
    if err != nil {
        return err
    }
    
    // 2. 检查礼物库存
    has, err := busi.UserGift.GetCount(ctx, fromUid, giftId)
    if err != nil {
        return err
    }
    if has == 0 {
        return errors.New("礼物不足")
    }
    
    // 3. 调用 Service 执行赠送
    if err := service.Gift.Send(ctx, fromUid, toUid, giftId); err != nil {
        return err
    }
    
    // 4. 更新房间热度
    busi.RoomHot.Incr(ctx, rid, giftId)
    
    return nil
}
```

### 3. Service 层最佳实践

```go
// ✅ 推荐：事务管理
func (s *roomService) Transfer(ctx context.Context, rid, newOwnerUid uint32) error {
    tx, err := dao.DB().Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback()
    
    // 所有操作绑定 tx
    dao.XsChatroom.DB(tx).Update(...)
    dao.XsChatroomUser.DB(tx).Insert(...)
    dao.XsChatroomLog.DB(tx).Insert(...)
    
    return tx.Commit()
}
```

### 4. DAO 层最佳实践

```go
// ✅ 推荐：批量查询避免 N+1
func (d *userDao) BatchGet(ctx context.Context, uids []uint32) ([]*User, error) {
    var users []*User
    err := d.Ctx(ctx).WhereIn("uid", uids).Scan(&users)
    return users, err
}

// ❌ 错误：循环查询
for _, uid := range uids {
    user := d.FindOne(ctx, uid) // N 次查询
}
```

---

## 与 slp-go 架构对比

| 维度 | slp-go | slp-room |
|------|--------|----------|
| **架构** | API → Service → DAO | API → Busi → Service → DAO |
| **Busi 层** | 无独立 Busi 层 | 有独立 Busi 层 |
| **Query 层** | 160 文件 | 103 文件 |
| **CacheModel** | 分散在 Service | 独立 cachemodel 目录 |

---

**参考文档**:
- [`01-structure.md`](./01-structure.md) - 项目结构
- [`05-service.md`](./05-service.md) - Service 层模式
- [`06-dao.md`](./06-dao.md) - DAO 层模式
