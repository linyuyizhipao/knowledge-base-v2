---
id: room-type-development
label: 房间类型开发完全指南
source: curated/cross-projects/chatroom/room-type-development.md
business: chatroom
compiled: 2026-04-25
links:
  - room-type-concept
  - room-type-work-plan
---

# 房间类型开发完全指南

> 从 0 到 1 实现新房间类型的完整开发流程

## 开发优先级

```
优先级 1: 能创建房间 → 优先级 2: 能进房出房 → 优先级 3: 核心玩法 → 优先级 4: 扩展功能
```

## 第 1 步：数据库与配置注册

### 配置注册 SQL（关键）

```sql
-- 1. 修改 xs_chatroom.property 枚举
ALTER TABLE xs_chatroom 
MODIFY COLUMN property enum(..., 'big-brother');

-- 2. 注册模块工厂
INSERT INTO xs_chatroom_module_factory (
    id, factory_name, factory_type, module_id, party_type, ...
) VALUES (262, '大哥房', 'big-brother', 151, 'big-brother', ...);

-- 3. 注册模块配置
INSERT INTO xs_chatroom_module_config (
    id, module_name, module_type, room_type, ...
) VALUES (151, '大哥房', 'big-brother', 'big-brother', ...);
```

## 第 2 步：代码生成

```bash
slpctl gen -t xs_chatroom_big_brother
make proto
```

## 第 3 步：RPC Proxy 基础实现

### Property 模块实现（最小化）

```go
// rpc/server/internal/proxy/module/property/big-brother.go
type BigBrotherProperty struct {
    Module
}

func (b *BigBrotherProperty) CheckJoin(...) error { return nil }
func (b *BigBrotherProperty) Configuration(...) error { return nil }
func (b *BigBrotherProperty) OnAfterCreate(...) error { return nil }
```

## 第 4 步：Service 层

```
app/service/big_brother/
├── big_brother.go    # 初始化入口
├── room.go           # 房间信息管理
└── money.go          # 财富值管理
```

## 第 5 步：CMD 消费者

```go
// cmd/internal/big_brother/service.go
func (s *Service) NsqMessageHandler(msg *nsq.Message) error {
    switch nsqMsg.Cmd {
    case "add_money":
        return s.handleAddMoney(...)
    }
}
```

## 第 6 步：扩展功能

| 功能 | 模块 | 优先级 |
|------|------|--------|
| 进房校验 | RPC Proxy CheckJoin | 高 |
| 麦位管理 | RPC Proxy OnBeforeJoinMic | 高 |
| 房间配置 | RPC Proxy Configuration | 高 |
| 财富值系统 | Service + CMD | 中 |
| 定时任务 | Service Cron | 中 |

## 常见坑点

| 问题 | 解决 |
|------|------|
| 枚举未更新 | ALTER TABLE xs_chatroom MODIFY COLUMN property |
| 模块工厂未注册 | INSERT xs_chatroom_module_factory |
| RPC Proxy 未注册 | 添加 switch-case 到 module.go |
| NSQ Topic 未配置 | config/slp-nsq-dev.json |