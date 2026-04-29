# 房间类型开发完全指南

> 从 0 到 1 实现新房间类型的完整开发流程 - 以大哥房和星舰房为例

**最后更新**: 2026-04-11  
**参考 PR**: slp-go#2760, slp-room#864, slp-common-rpc#220, slp-gateway#106, slp-php#1533, slp-server#90

---

## 文档说明

### 核心理念

**先跑通基础流程，再逐步扩展功能**

开发新房型时，按以下优先级推进：

```
优先级 1: 能创建房间 → 优先级 2: 能进房出房 → 优先级 3: 核心玩法 → 优先级 4: 扩展功能
```

### 开发步骤总览

| 步骤 | 阶段 | 目标 | 耗时 |
|------|------|------|------|
| **第 1 步** | [数据库 + 配置注册](#第-1 步数据库与配置注册先让房型能创建) | 房型能创建 | 0.5 天 |
| **第 2 步** | [代码生成](#第-2 步代码生成-dao-model-proto) | DAO/Model/Proto就绪 | 0.5 天 |
| **第 3 步** | [RPC Proxy 基础实现](#第-3 步-rpc-proxy-基础实现先让房型能跑起来) | 能进房、出房 | 1 天 |
| **第 4 步** | [Service 层基础实现](#第-4 步-service-层基础实现) | 核心数据可读写 | 1 天 |
| **第 5 步** | [CMD 事件消费者](#第-5 步-cmd-事件消费者) | 事件驱动业务 | 1 天 |
| **第 6 步** | [扩展功能](#第-6 步扩展功能按需实现) | 按需求逐步实现 | 按需 |

---

## 第 1 步：数据库与配置注册（先让房型能创建）

**目标**：执行 SQL 后，房型就能在系统中创建

**耗时**：0.5 天

### 1.1 编写 DDL（业务表）

根据房型需求设计表结构：

```sql
-- 主表：房型核心数据
CREATE TABLE `xs_chatroom_big_brother` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rid` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '房间 RID',
  `uid` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '房主 uid',
  `money` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '财富值',
  `level` int(11) unsigned NOT NULL DEFAULT '0' COMMENT '房间等级',
  `dateline` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_rid` (`rid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房';

-- 关联表（可选）：如守护关系
CREATE TABLE `xs_chatroom_big_defend` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rid` int(10) unsigned NOT NULL DEFAULT '0',
  `defend_uid` int(10) unsigned NOT NULL DEFAULT '0',
  `expire_time` int(10) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_rid_defend_uid` (`rid`,`defend_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房守护';

-- 流水表（可选）：如财富值变更
CREATE TABLE `xs_big_brother_money_log` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `rid` int(11) unsigned NOT NULL DEFAULT '0',
  `uid` int(11) unsigned NOT NULL DEFAULT '0',
  `money` int(11) NOT NULL DEFAULT '0',
  `type` varchar(64) NOT NULL DEFAULT '',
  `dateline` int(11) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_rid` (`rid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房财富流水';
```

### 1.2 执行配置注册 SQL（关键！）

**这一步让房型能在系统中创建**：

```sql
-- 1. 修改 xs_chatroom.property 枚举
ALTER TABLE xs_chatroom 
MODIFY COLUMN property enum(
    'business','vip','fleet','private','game','union',
    'meeting','virtual','club','nest','singer','ai',
    'starship','light-up','big-brother'  -- 新增房型
) NOT NULL DEFAULT 'vip';

-- 2. 注册模块工厂（房型生产工厂）
INSERT INTO xs_chatroom_module_factory (
    id, factory_name, factory_type, module_id, party_type,
    default_paier, default_reception, default_display_message,
    default_theme, default_background, default_counter,
    default_mode, default_nine, default_state, default_tag_id,
    promise_app, promise_property, backend_default
) VALUES (
    262, '大哥房', 'big-brother', 151, 'big-brother',
    0, 0, 1, 'normal', 'normal', 0, 'auto', 1, 0, 1,
    '66', 'big-brother', 0
);

-- 3. 注册模块配置（房型玩法配置）
INSERT INTO xs_chatroom_module_config (
    id, module_name, module_type, room_type, room_types,
    room_game, promise_property, promise_theme, promise_background,
    promise_app_id, position_num, default_auction
) VALUES (
    151, '大哥房', 'big-brother', 'big-brother', 'auto',
    'none', 'big-brother', 'normal', 'normal', '66', 11, 0
);
```

### 1.3 验证

```sql
-- 验证枚举已更新
SHOW COLUMNS FROM xs_chatroom LIKE 'property';

-- 验证模块工厂已注册
SELECT * FROM xs_chatroom_module_factory WHERE factory_type = 'big-brother';

-- 验证模块配置已注册
SELECT * FROM xs_chatroom_module_config WHERE module_type = 'big-brother';
```

✅ **完成标志**：能在测试服创建新房型的房间

---

## 第 2 步：代码生成（DAO/Model/Proto）

**目标**：生成基础代码框架

**耗时**：0.5 天

### 2.1 生成 DAO/Model

```bash
# 切换到 slp-go 项目
cd <slp-go 项目目录>

# 生成所有表的 DAO/Model
slpctl gen -t xs_chatroom_big_brother
slpctl gen -t xs_chatroom_big_defend
slpctl gen -t xs_big_brother_money_log
```

**输出**：
```
app/dao/internal/xs_chatroom_big_brother.go
app/dao/xs_chatroom_big_brother.go
app/model/internal/xs_chatroom_big_brother.go
app/model/xs_chatroom_big_brother.go
```

### 2.2 定义 Proto

```protobuf
// entity_xs_chatroom_big_brother.proto
syntax = "proto3";
package pb;

message XsChatroomBigBrother {
  uint32 id = 1;
  uint32 rid = 2;
  uint32 uid = 3;
  uint32 money = 4;
  uint32 level = 5;
  uint32 dateline = 6;
}
```

```bash
# 生成 Proto Go 代码
make proto
```

✅ **完成标志**：DAO/Model/Proto 代码生成完毕，编译通过

---

## 第 3 步：RPC Proxy 基础实现（先让房型能跑起来）

**目标**：实现房型最基础的进房、出房、配置功能

**耗时**：1 天

### 3.1 Property 常量定义

```go
// slp-room/rpc/server/internal/proxy/module/property/consts.go
package property

type Property string

const (
    Business   Property = "business"
    Vip        Property = "vip"
    BigBrother Property = "big-brother"  // 新增
)
```

### 3.2 Property 模块实现（最小化）

```go
// slp-room/rpc/server/internal/proxy/module/property/big-brother.go
package property

import (
    "context"
    pbroom "slp/app/pb/chatroom"
    "slp/rpc/server/internal/proxy/module/api"
    "slp/rpc/server/internal/proxy/operation"
    "slp/rpc/server/internal/proxy/proxy"
    "github.com/gogf/gf/database/gdb"
)

type Module struct {
    api.Empty
}

func NewBigBrother() *BigBrotherProperty {
    return &BigBrotherProperty{Module: Module{}}
}

type BigBrotherProperty struct {
    Module
}

// 只需要先实现这几个核心接口
func (b *BigBrotherProperty) CheckJoin(
    ctx context.Context, 
    room *proxy.Chatroom, 
    join *operation.Configuration,
) error {
    // 基础进房校验（先留空或只检查黑名单）
    return nil
}

func (b *BigBrotherProperty) Configuration(
    ctx context.Context, 
    room *proxy.Chatroom, 
    op *operation.Configuration, 
    configuration *pbroom.ChatroomConfiguration,
) error {
    // 基础配置返回（先留空）
    return nil
}

func (b *BigBrotherProperty) OnAfterCreate(
    ctx context.Context, 
    room *proxy.Chatroom, 
    op *operation.CreateOperation, 
    resp *operation.CreateOperationResponse,
) error {
    // 创建后初始化（可选）
    return nil
}
```

### 3.3 Room 模块实现（最小化）

```go
// slp-room/rpc/server/internal/proxy/module/room/big_brother.go
package room

import (
    "context"
    "slp/rpc/server/internal/proxy/operation"
    "slp/rpc/server/internal/proxy/proxy"
)

type BigBrother struct {
    Module
}

func NewBigBrother() *BigBrother {
    return &BigBrother{}
}

// 进房校验（可复用 Property 的 CheckJoin）
func (b *BigBrother) CheckJoin(
    ctx context.Context, 
    room *proxy.Chatroom, 
    join *operation.Configuration,
) error {
    return nil
}
```

### 3.4 模块注册

```go
// slp-room/rpc/server/internal/proxy/module/property/module.go
func NewModule(property Property) api.Module {
    switch property {
    case BigBrother:
        return NewBigBrother()
    // ...
    }
    return &Module{}
}
```

### 3.5 编译 + 重启 slp-room

```bash
# 编译 slp-room
cd <slp-room 项目目录>
make build

# 重启 RPC 服务
./rpc.sh
```

✅ **完成标志**：能正常进房、出房，房间配置能正常返回

---

## 第 4 步：Service 层基础实现

**目标**：实现房型核心数据的读写

**耗时**：1 天

### 4.1 Service 目录结构

```
app/service/big_brother/
├── big_brother.go    # 初始化入口
├── room.go           # 房间信息管理
└── money.go          # 财富值管理（可选）
```

### 4.2 初始化入口

```go
// app/service/big_brother/big_brother.go
package big_brother

var (
    RoomManager  *roomManagerService
    MoneyManager *moneyManagerService
)

func init() {
    RoomManager = &roomManagerService{}
    MoneyManager = &moneyManagerService{}
}
```

### 4.3 房间信息管理

```go
// app/service/big_brother/room.go
package big_brother

import (
    "context"
    "slp-go/app/dao"
    "slp-go/app/model"
)

type roomManagerService struct{}

// GetRoomInfo 获取房间信息
func (s *roomManagerService) GetRoomInfo(ctx context.Context, rid uint32) (*model.XsChatroomBigBrother, error) {
    return dao.XsChatroomBigBrother.GetByRid(ctx, rid)
}

// CreateRoom 创建房间（如果 OnAfterCreate 中需要）
func (s *roomManagerService) CreateRoom(ctx context.Context, rid, uid uint32) error {
    _, err := dao.XsChatroomBigBrother.Insert(&model.XsChatroomBigBrother{
        Rid:      rid,
        Uid:      uid,
        Money:    1000,  // 初始财富值
        Dateline: uint32(time.Now().Unix()),
    })
    return err
}
```

### 4.4 在 RPC Proxy 中调用 Service

```go
// slp-room/rpc/server/internal/proxy/module/property/big-brother.go
func (b *BigBrotherProperty) OnAfterCreate(...) error {
    // 调用 slp-go 的 Service 层初始化房间数据
    _, _ = client.BigBrother.CreateRoom(ctx, &pb.CreateBigBrotherRoomReq{
        Rid: room.Rid,
        Uid: op.Uid,
    })
    return nil
}
```

✅ **完成标志**：房间数据能正常读写

---

## 第 5 步：CMD 事件消费者

**目标**：监听 NSQ 事件，触发业务逻辑

**耗时**：1 天

### 5.1 定义 Topic 常量

```go
// app/consts/big_brother.go
const BigBrotherTopic = "slp.big.brother"
```

### 5.2 创建 CMD 消费者

```go
// cmd/internal/big_brother/service.go
package big_brother

import (
    "context"
    "encoding/json"
    "slp-go/cmd"
    "slp-go/app/service/big_brother"
    "github.com/nsqio/go-nsq"
)

type Service struct{}

func (s *Service) Run() error {
    return library.NewNsqWorker(
        consts.BigBrotherTopic,
        library.NsqGroupDefault,
        s.NsqMessageHandler,
    ).ConnectWithConcurrency(10)
}

func (s *Service) NsqMessageHandler(msg *nsq.Message) error {
    var nsqMsg cmd.NsqEventMsg
    json.Unmarshal(msg.Body, &nsqMsg)
    
    switch nsqMsg.Cmd {
    case "add_money":
        return s.handleAddMoney(msg.Ctx, &nsqMsg)
    }
    return nil
}

func (s *Service) handleAddMoney(ctx context.Context, data *cmd.NsqEventMsg) error {
    var req struct {
        Uid   uint32 `json:"uid"`
        Rid   uint32 `json:"rid"`
        Money uint32 `json:"money"`
    }
    json.Unmarshal(data.Data, &req)
    
    return big_brother.MoneyManager.AddMoney(ctx, req.Uid, req.Rid, req.Money)
}
```

### 5.3 注册 CMD 启动

```go
// cmd/main.go
func main() {
    // 启动大哥房消费者
    bigBrotherService := big_brother.NewService()
    go bigBrotherService.Run()
}
```

### 5.4 配置 NSQ Topic

```json
// config/slp-nsq-dev.json
{
  "topics": ["slp.big.brother"]
}
```

✅ **完成标志**：发送 NSQ 事件后，业务逻辑正常触发

---

## 第 6 步：扩展功能（按需实现）

**目标**：根据需求逐步实现房型的特色功能

### 6.1 可能的扩展功能

| 功能 | 涉及模块 | 优先级 |
|------|---------|--------|
| 进房校验（密码、好友） | RPC Proxy `CheckJoin` | 高 |
| 麦位管理（守护位） | RPC Proxy `OnBeforeJoinMic` | 高 |
| 房间配置（背景、勋章） | RPC Proxy `Configuration` | 高 |
| 财富值系统 | Service + CMD | 中 |
| 定时任务（衰减、结算） | Service Cron | 中 |
| 灯牌/应援 | API + Service + CMD | 低 |
| 榜单排行 | API + Service | 低 |

### 6.2 扩展示例：麦位守护校验

```go
// slp-room/rpc/server/internal/proxy/module/room/big_brother.go
func (b *BigBrother) OnBeforeJoinMic(
    ctx context.Context, 
    room *proxy.Chatroom, 
    op *operation.JoinMicOption, 
    res *operation.MicOperationResponse,
) error {
    // 守护麦位（1-4 号位）只有守护用户能上
    if op.Position >= 1 && op.Position <= 4 {
        defend, _ := dao.XsChatroomBigDefend.FindOne("defend_uid=? and rid=?", op.Uid, room.Rid)
        if defend == nil || defend.ExpireTime < uint32(time.Now().Unix()) {
            return errors.New("只有守护用户才能上守护麦位")
        }
    }
    return nil
}
```

### 6.3 扩展示例：财富值增加

```go
// app/service/big_brother/money.go
func (s *moneyManagerService) AddMoney(ctx context.Context, uid, rid, money uint32, logType string) error {
    tx, _ := dao.BeginTx(ctx)
    defer tx.Rollback()
    
    // 1. 更新房间财富值
    dao.XsChatroomBigBrother.AddMoney(tx, rid, money)
    
    // 2. 记录流水
    dao.XsBigBrotherMoneyLog.Insert(tx, &model.XsBigBrotherMoneyLog{
        Uid: uid, Rid: rid, Money: money, Type: logType,
    })
    
    return tx.Commit()
}
```

---

## 大哥房 vs 星舰房：模式对比

### 选择建议

| 需求特征 | 推荐模式 | 理由 |
|---------|---------|------|
| **房间类型扩展**（如爆灯房、情侣房） | 大哥房模式 | 轻量级，与现有房间系统集成度高 |
| **独立大型玩法**（如家族、领地战） | 星舰房模式 | 独立项目，可自由扩展 |
| **简单房间属性 + 少量关联表** | 大哥房模式 | 数据库设计简单 |
| **多子玩法模块** | 星舰房模式 | 有多个独立玩法（农场、商城等） |

### 架构对比

| 维度 | 大哥房 | 星舰房 |
|------|--------|--------|
| **所属项目** | slp-go + slp-room | slp-starship（独立） |
| **数据库前缀** | `xs_chatroom_big_*` | `xs_starship*` |
| **RPC Proxy** | `module/property/big-brother.go` | `commonsrv/starship/` |
| **Topic** | `slp.big.brother` | `starship.event.topic` |

---

## 完整 Checklist

### 第 1 步：数据库与配置注册
- [ ] 主表 DDL 编写
- [ ] 关联表 DDL 编写（可选）
- [ ] 流水表 DDL 编写（可选）
- [ ] **property 枚举修改**
- [ ] **模块工厂 INSERT**
- [ ] **模块配置 INSERT**
- [ ] 验证：能创建房间

### 第 2 步：代码生成
- [ ] DAO 层生成（internal + 导出）
- [ ] Model 层生成（internal + 导出）
- [ ] Proto 定义编写
- [ ] PB Go 代码生成
- [ ] 编译通过

### 第 3 步：RPC Proxy 基础实现
- [ ] Property 常量定义
- [ ] Property 模块实现（最小化）
- [ ] Room 模块实现（最小化）
- [ ] 工厂函数注册
- [ ] 编译 + 重启 slp-room
- [ ] 验证：能进房、出房

### 第 4 步：Service 层基础实现
- [ ] Service 初始化入口
- [ ] 房间信息管理
- [ ] RPC Proxy 调用 Service
- [ ] 验证：数据能读写

### 第 5 步：CMD 事件消费者
- [ ] Topic 常量定义
- [ ] CMD 消费者实现
- [ ] NSQ 配置
- [ ] CMD 启动注册
- [ ] 验证：事件能触发

### 第 6 步：扩展功能
- [ ] 按需实现高优先级功能
- [ ] 按需实现中优先级功能
- [ ] 按需实现低优先级功能

---

## 常见坑点

### 1. 枚举未更新

**问题**：创建房间时报错 `property` 值不合法

**解决**：
```sql
ALTER TABLE xs_chatroom 
MODIFY COLUMN property enum(..., 'big-brother');
```

### 2. 模块工厂未注册

**问题**：房间无法创建

**解决**：
```sql
SELECT * FROM xs_chatroom_module_factory WHERE factory_type = 'big-brother';
SELECT * FROM xs_chatroom_module_config WHERE module_type = 'big-brother';
```

### 3. RPC Proxy 未注册

**问题**：进房报错或配置返回空

**解决**：检查 `module/property/module.go` 中的 switch-case 是否添加新房型

### 4. NSQ Topic 未配置

**问题**：事件发送失败

**解决**：在 `config/slp-nsq-dev.json` 添加 Topic

---

## 相关文档

| 文档 | 用途 |
|------|------|
| [[../../patterns/event-extension-guide.md]] | 事件拓展决策树 |
| [[../../patterns/cmd-module-standard.md]] | CMD 模块标准结构 |
| [[room-type-work-plan.md]] | 按工作日拆分的工作计划 |
| [[room-type-concept.md]] | 房间类型概念介绍 |

---

## 附录 A：模块工厂配置详解

### A.1 模块工厂表结构

```sql
-- 模块工厂：定义房间类型的生产工厂
INSERT INTO xs_chatroom_module_factory VALUES (
    262,                              -- id
    '大哥房',                          -- factory_name
    'big-brother',                    -- factory_type (唯一标识)
    151,                              -- module_id (关联模块配置)
    'big-brother',                    -- party_type
    0,                                -- default_paier
    0,                                -- default_reception
    1,                                -- default_display_message
    'normal',                         -- default_theme
    'normal',                         -- default_background
    0,                                -- default_counter
    'auto',                           -- default_mode
    1,                                -- default_nine
    0,                                -- default_state
    1,                                -- default_tag_id
    '66',                             -- promise_app (依赖的 APP ID)
    'big-brother',                    -- promise_property
    0                                 -- backend_default
);
```

### A.2 模块配置表结构

```sql
-- 模块配置：定义房间类型的玩法配置
INSERT INTO xs_chatroom_module_config VALUES (
    151,                              -- id
    '大哥房',                          -- module_name
    'big-brother',                    -- module_type
    'big-brother',                    -- room_type
    'auto',                           -- room_types (支持的房间类型)
    'none',                           -- room_game (支持的游戏房)
    'big-brother',                    -- promise_property
    'normal',                         -- promise_theme
    'normal',                         -- promise_background
    '66',                             -- promise_app_id
    11,                               -- position_num (麦位数量)
    0                                 -- default_auction
);
```

### A.3 更新支持的游戏房

```sql
-- 让游戏房支持新房型
UPDATE xs_chatroom_module_factory 
SET promise_property = CONCAT(promise_property, ',big-brother') 
WHERE factory_type IN (
    "laya-billiards","fly-chess","under","wolf6","laya-tetris",
    "cocos-gobang","cocos-cubebattle_business","cocos-memmatch_business",
    "laya-snake_business","guess-queue","laya-carrom","pick-hole",
    "laya-liar_business","business-actguess","laya-kittens"
);
```

---

## 附录 B：跨服务协调清单

### B.1 涉及服务列表

| 服务 | 变更内容 | 优先级 |
|------|---------|--------|
| **slp-go** | Service/API/DAO/Model/CMD | 高 |
| **slp-room** | RPC Proxy、房间事件处理 | 高 |
| **slp-common-rpc** | RPC 服务支持 | 高 |
| **slp-gateway** | 网关路由配置 | 中 |
| **slp-php** | PHP 端业务逻辑 | 中 |
| **slp-server** | 服务端配置 | 低 |

### B.2 slp-room 变更示例

```go
// rpc/server/internal/proxy/module/property/big-brother.go
package property

type BigBrotherProperty struct {
    Module
}

func (b *BigBrotherProperty) CheckJoin(
    ctx context.Context, 
    room *proxy.Chatroom, 
    join *operation.Configuration,
) error {
    // 基础进房校验
    return nil
}

func (b *BigBrotherProperty) Configuration(
    ctx context.Context, 
    room *proxy.Chatroom, 
    op *operation.Configuration, 
    configuration *pbroom.ChatroomConfiguration,
) error {
    // 基础配置返回
    return nil
}
```

### B.3 slp-php 变更示例

```php
// app/models/XsChatroomBigDefend.php (新增模型)
class XsChatroomBigDefend extends Model {
    protected $table = 'xs_chatroom_big_defend';
}

// app/service/PartyTypeSrv.php (修改支持 big-brother)
case 'big-brother':
    // 大哥房逻辑
    break;
```

### B.4 Helm 部署配置

```yaml
# deploy/helm/cmd/cmds/common-gift-send-consume.yaml
# 添加 big-brother channel 支持

# deploy/helm/rpc/rpcs/room-manager.yaml
# RPC 服务配置更新

# deploy/helm/http/values.yaml
# HTTP 服务配置
```

---

## 附录 C：完整 Checklist（详细版）

### 数据库阶段
- [ ] 主表 DDL 编写
- [ ] 关联表 DDL 编写
- [ ] 流水表 DDL 编写
- [ ] 索引优化
- [ ] 配置表 DDL（模块工厂、模块配置）
- [ ] property 枚举修改
- [ ] 模块工厂 INSERT
- [ ] 模块配置 INSERT
- [ ] 游戏支持 UPDATE

### 代码生成阶段
- [ ] DAO 层生成（internal + 导出）
- [ ] Model 层生成（internal + 导出）
- [ ] Proto 定义编写
- [ ] PB Go 代码生成
- [ ] 编译通过

### 业务实现阶段
- [ ] Service 层主文件
- [ ] Service 层各模块文件
- [ ] Service 层单元测试
- [ ] API 层实现
- [ ] API 路由注册

### RPC Proxy 阶段
- [ ] Property 常量定义
- [ ] Property 模块实现
- [ ] Room 模块实现
- [ ] 工厂函数注册
- [ ] 编译 + 重启 slp-room

### 事件消费阶段
- [ ] Topic 常量定义
- [ ] CMD 消费者启动
- [ ] 事件 Handler 实现
- [ ] NSQ 消息解析
- [ ] CMD 启动注册

### 跨服务阶段
- [ ] slp-room 变更
- [ ] slp-common-rpc 变更
- [ ] slp-php 变更
- [ ] slp-server 变更

### 部署阶段
- [ ] Helm 配置更新
- [ ] 环境变量检查
- [ ] 重启脚本准备

---

**版本**: 2.1 | **最后更新**: 2026-04-11
