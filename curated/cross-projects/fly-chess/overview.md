# 飞行棋游戏功能

## 业务全景图

飞行棋游戏功能使用户能够在平台上进行飞行棋游戏互动，涉及多个服务模块的协作。

```
[slp-php] - 前端控制器和房间配置接口
    ↓
[slp-gateway] - 网关路由和请求转发
    ↓
[slp-room] - 飞行棋核心游戏逻辑
    ↓
[slp-go] - 部署和服务配置
```

## PR分析与知识沉淀

基于以下PR的分析：

- **slp-room#584** - 飞行棋游戏核心服务实现
- **slp-gateway#82** - 飞行棋网关转发配置
- **slp-go#2186** - 飞行棋相关部署配置
- **slp-php#1198** - 房间配置新接口实现

## 项目职责分工

| 项目 | 职责 | 核心模块 |
|------|------|----------|
| slp-room | 飞行棋核心游戏逻辑 | app/service/fly_chess/ |
| slp-gateway | 飞行棋网关转发配置 | rpc/server/internal/roommanager/fly_chess.go |
| slp-go | 飞行棋相关部署配置 | deploy/helm/cmd/cmds/ |
| slp-php | 房间配置新接口实现 | app/controllers/RoomController.php |

## 核心流程（跨项目）

### 1. 游戏创建流程
1. slp-php接收前端请求
2. 通过gateway转发到slp-room
3. slp-room创建飞行棋游戏实例
4. 通过NSQ事件通知相关服务

### 2. 游戏进行流程
1. 玩家操作通过gateway转发
2. slp-room处理游戏逻辑
3. 更新游戏状态并通知相关服务

## 数据表结构

### 共享数据表
- `xs_chatroom_fly_chess` - 飞行棋房间核心数据
- `xs_fly_chess_player_status` - 飞行棋玩家状态

### 各项目私有表
- slp-go: 部署相关配置表
- slp-php: 房间配置相关表

## 配置管理

### 各项目配置项
- slp-room: 飞行棋游戏逻辑配置
- slp-gateway: 飞行棋网关路由配置
- slp-go: 部署和运维配置
- slp-php: 房间配置新接口配置

## 问题排查

### 跨项目问题排查步骤
1. 检查slp-php接口是否正常
2. 验证gateway路由配置
3. 确认slp-room游戏逻辑
4. 检查slp-go部署状态

## slp-room项目职责

### 核心模块
- `app/service/fly_chess/` - 飞行棋核心游戏逻辑
- `app/pb/chatroom/chatroom_fly_chess.pb.go` - 飞行棋协议定义
- `app/pb/rpc_room_game.pb.go` - 房间游戏协议定义

### 文件路径
- 服务实现: `app/service/fly_chess/`
- 协议定义: `app/pb/chatroom/chatroom_fly_chess.pb.go`
- 数据模型: `app/model/` 和 `app/dao/` (通过slpctl gen生成)

### 飞行棋服务实现
- `app/service/fly_chess/service.go` - 主要服务接口
- `app/service/fly_chess/game_logic.go` - 游戏逻辑实现
- `app/service/fly_chess/types.go` - 类型定义

### Property模块
- `rpc/server/internal/proxy/module/property/fly_chess.go` - 飞行棋属性模块

### 依赖的外部服务
- 依赖slp-go的基础服务
- 通过事件总线与其它服务通信

### 事件订阅
- 订阅房间创建、用户进出等事件
- 发布游戏状态变更事件

### 本地测试
1. 启动slp-room服务
2. 创建飞行棋房间
3. 测试游戏基本功能
4. 验证游戏状态同步

## slp-gateway项目职责

### 核心模块
- `proto/rpc_room_game.proto` - 飞行棋游戏协议定义
- `rpc/client/room_game.go` - 飞行棋游戏客户端
- `rpc/server/internal/roommanager/fly_chess.go` - 飞行棋网关处理逻辑

### 文件路径
- 协议定义: `proto/rpc_room_game.proto`
- 客户端: `rpc/client/room_game.go`
- 服务端处理: `rpc/server/internal/roommanager/fly_chess.go`
- 配置文件: `deploy/rpc/room.gatemanager.conf`

### 协议定义
- `proto/rpc_room_game.proto` - 定义飞行棋游戏相关RPC接口

### 客户端实现
- `rpc/client/room_game.go` - 实现飞行棋游戏相关的客户端调用

### 网关处理逻辑
- `rpc/server/internal/roommanager/fly_chess.go` - 飞行棋相关的网关处理

### 配置管理
- `deploy/rpc/room.gatemanager.conf` - 网关配置
- `deploy/helm/rpc/rpcs/room-manager.yaml` - Helm部署配置

### 依赖的外部服务
- 转发请求到slp-room的飞行棋服务
- 与slp-room进行协议交互

### 事件订阅
- 无直接事件订阅，主要负责请求转发

### 本地测试
1. 启动slp-gateway服务
2. 验证飞行棋相关接口的路由
3. 测试请求转发功能
4. 确认与slp-room的通信正常

## slp-go项目职责

### 核心模块
- `deploy/` - 飞行棋相关部署配置
- `cmd/internal/fly_chess/` - 飞行棋事件消费者
- 协议定义和生成

### 文件路径
- 部署脚本: `deploy/cmd_list_a.sh`, `deploy/cmd_multi.sh`
- 部署配置: `deploy/helm/cmd/cmds/`
- 事件消费者: `cmd/internal/fly_chess/`

### 部署配置
- `deploy/cmd_list_a.sh` - 部署命令列表
- `deploy/cmd_multi.sh` - 多命令部署脚本
- `deploy/helm/cmd/cmds/delay-msg-consume.yaml` - 延迟消息消费配置
- `deploy/helm/cmd/cmds/match-match.yaml` - 匹配服务配置

### 事件消费者
- `cmd/internal/fly_chess/service.go` - 飞行棋事件处理消费者

### 环境配置
- `.env` - 环境变量配置

### 依赖的外部服务
- 无直接RPC调用

### 事件订阅
- 订阅飞行棋相关事件 (`slp.fly.chess`)

### 本地测试
1. 部署飞行棋相关服务
2. 验证事件消费者运行正常
3. 测试部署脚本
4. 确认环境配置正确

## slp-php项目职责

### 核心模块
- `app/controllers/RoomController.php` - 房间控制器，新增飞行棋相关接口
- `app/models/XsChatroom.php` - 房间模型，支持飞行棋相关功能
- `app/service/rpc/RpcRoomProxy.php` - RPC代理，处理飞行棋相关调用

### 文件路径
- 控制器: `app/controllers/RoomController.php`
- 模型: `app/models/XsChatroom.php`
- 服务代理: `app/service/rpc/RpcRoomProxy.php`
- 配置文件: `deploy/cmd/xs.room.conf` 等

### 控制器实现
- `app/controllers/RoomController.php` - 实现房间配置新接口

### 模型更新
- `app/models/XsChatroom.php` - 扩展房间模型以支持飞行棋功能

### RPC代理
- `app/service/rpc/RpcRoomProxy.php` - 代理飞行棋相关RPC调用

### 部署配置
- `deploy/cmd/xs.room.conf` - 房间服务配置
- `deploy/cmd2/xs.room.user.state.conf` - 用户状态服务配置
- `deploy/helm/cli/tasks/xs-room-user-state.yaml` - Helm部署任务
- `deploy/helm/cli/tasks/xs-room.yaml` - 房间服务Helm配置
- `deploy/helm/web/values.yaml` - Web服务Helm配置

### 依赖的外部服务
- 调用slp-room的飞行棋游戏服务
- 通过gateway转发请求

### 事件订阅
- 无直接事件订阅

### 本地测试
1. 验证房间配置新接口
2. 测试与gateway的通信
3. 验证RPC调用正常
4. 确认配置文件生效