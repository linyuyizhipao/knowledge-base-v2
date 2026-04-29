# SLP 业务开发规范

> 基于 SLPCTL 工具的标准开发流程 - 从数据库到 API 全链路指南

**版本**: 1.0 | **最后更新**: 2026-04-16 | **适用项目**: slp-go, slp-room, slp-starship

---

## 🎯 核心理念

**一个业务模块 = 一个目录 = 一个对外服务对象**

使用 SLPCTL 工具实现标准化开发：
- **数据库优先** - 先定义表结构，再生成代码
- **Proto 驱动** - 基于 `.proto` 文件生成请求/响应结构
- **自动化工具** - 减少重复劳动，聚焦业务逻辑

---

## 📋 开发流程总览

```
第 1 步：数据库设计 → 第 2 步：DAO 生成 → 第 3 步：Proto/API 生成 → 
第 4 步：业务实现 → 第 5 步：测试部署
```

| 步骤 | 阶段 | 工具 | 产出 | 耗时 |
|------|------|------|------|------|
| **1** | [数据库设计](#第 1 步-数据库设计) | MySQL DDL | 表结构 | 0.5 天 |
| **2** | [DAO 生成](#第 2 步-dao-生成) | `slpctl gen` | DAO/Model/PB | 0.5 天 |
| **3** | [API 生成](#第 3 步-api-生成) | `slpctl code` | Handler/Service/Proto | 0.5 天 |
| **4** | [业务实现](#第 4 步-业务实现) | 手动编码 | 业务逻辑 | 1-3 天 |
| **5** | [测试部署](#第 5 步-测试部署) | `slpctl ci` | Jenkins 构建 | 0.5 天 |

---

## 第 1 步：数据库设计

### 1.1 编写 DDL

**主表结构模板**：

```sql
CREATE TABLE `xs_<business>_<table_name>` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `rid` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '房间 RID',
  `uid` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '用户 UID',
  
  -- 业务字段（根据需求定义）
  `status` tinyint(3) unsigned NOT NULL DEFAULT '0' COMMENT '状态',
  `data` json DEFAULT NULL COMMENT '扩展数据',
  
  -- 审计字段
  `created_at` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '创建时间',
  `updated_at` int(10) unsigned NOT NULL DEFAULT '0' COMMENT '更新时间',
  
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_rid` (`rid`),
  KEY `idx_uid` (`uid`),
  KEY `idx_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='业务表说明';
```

### 1.2 执行建表

```bash
# 连接数据库
mysql -h <host> -u <user> -p <database>

# 执行 DDL
source /path/to/schema.sql
```

### 1.3 验证表结构

```sql
DESC xs_<business>_<table_name>;
SHOW CREATE TABLE xs_<business>_<table_name>;
```

---

## 第 2 步：DAO 生成

### 2.1 生成 DAO 层代码

```bash
cd <project-root>  # slp-go 或 slp-room

# 单个表生成
slpctl gen -t xs_<business>_<table_name>

# 批量生成（关联表）
slpctl gen -t xs_<business>_<table_name>,xs_<business>_related
```

### 2.2 生成内容

```
生成文件清单：
├── proto/entity_<table_name>.proto          # Proto 定义
├── app/pb/entity_<table_name>.pb.go         # Go 代码
├── app/dao/internal/<table_name>_dao.go     # DAO 实现
└── app/dao/<TableName>.go                   # DAO 入口
```

### 2.3 验证生成

```bash
# 检查文件是否存在
ls -la app/dao/<TableName>.go
ls -la app/pb/entity_<table_name>.pb.go

# 编译检查
go build ./...
```

---

## 第 3 步：API 生成

### 3.1 定义 API 列表

**方式 1：命令行快速定义**

```bash
slpctl code -api /go/room/<business>/<action> -desc "<动作描述>"
```

**方式 2：配置文件批量定义**

```bash
cat > <business>_apis.json << 'EOF'
[
  {"router_path": "/go/room/<business>/<action1>", "description": "动作 1 描述"},
  {"router_path": "/go/room/<business>/<action2>", "description": "动作 2 描述"},
  {"router_path": "/go/room/<business>/<action3>", "description": "动作 3 描述"}
]
EOF

slpctl code -config <business>_apis.json
```

### 3.2 生成内容

```
生成文件清单：
├── proto/api/api_<business>_<action>.proto  # 请求/响应 Proto
├── api/handler/<business>_api.go            # HTTP Handler
└── rpc/server/internal/<business>/<business>_pretend.go  # Service 骨架
```

### 3.3 路由命名规范

采用 4 层结构，首字母小写的驼峰命名：

```
/go/room/<business>/<action>
  ↑      ↑          ↑
 项目   业务模块    具体 API
```

**项目前缀对照**：

| 项目 | 路由前缀 |
|------|----------|
| slp-go | `/go/slp/` |
| slp-room | `/go/room/` |
| slp-starship | `/go/starship/` |

---

## 第 4 步：业务实现

### 4.1 填充 Service 逻辑

编辑生成的 Service 骨架文件：

```go
// rpc/server/internal/<business>/<business>_pretend.go
package <business>

import (
    "context"
    "slp/app/dao"
    "slp/app/pb"
)

func (s *Service) <Action>(ctx context.Context, req *pb.<Action>Request) (*pb.<Action>Response, error) {
    // 1. 参数校验
    if req.GetRid() == 0 {
        return nil, errors.New("rid is required")
    }
    
    // 2. 数据查询
    info, err := dao.<TableName>.GetByRid(ctx, req.GetRid())
    if err != nil {
        return nil, err
    }
    
    // 3. 业务逻辑
    // ...
    
    // 4. 返回结果
    return &pb.<Action>Response{
        Code: 0,
        Data: &pb.<Action>Data{
            // ...
        },
    }, nil
}
```

### 4.2 常量定义

**业务专属常量** (`app/service/<business>/const.go`):

```go
package <business>

const (
    <Business>Topic = "xs.<business>"
    ChannelDefault  = "default"
)

var (
    <Business>DataKey = &RedisKey{
        key: "<business>:data:%d",
        ttl: 24 * time.Hour,
    }
)
```

### 4.3 Service 层组织

**全局单例模式** (`app/service/<business>/service.go`):

```go
package <business>

var <Business>Srv = &<business>Service{
    // 子模块注入
}

type <business>Service struct {
    // 子模块
}

func (s *<business>Service) <Method>(ctx context.Context, uid uint32) (*pb.Response, error) {
    // 业务逻辑
}
```

### 4.4 工具函数（纯计算）

**app/utils/<business>.go**:

```go
package utils

var <Business> = &<business>Utils{}

type <business>Utils struct{}

// 纯计算函数，无 IO
func (b *<business>Utils) FormatData(input string) string {
    return strings.TrimSpace(input)
}
```

---

## 第 5 步：测试部署

### 5.1 编译 Proto

```bash
# 生成所有修改过的 proto
slpctl proto -p .

# 或生成指定表
slpctl proto -t xs_<business>_<table_name> -p .
```

### 5.2 本地测试

```bash
# 运行单元测试
go test ./app/service/<business>/... -v

# 覆盖率检查
go test -cover ./app/service/<business>/...
```

### 5.3 提交代码

```bash
# 创建功能分支
git checkout master
git pull origin master
git checkout -b hu/<business>_feature

# 提交代码
git add -A
git commit -anm "feat: <business> 功能开发"
git push origin hu/<business>_feature
```

### 5.4 触发构建

```bash
# 提交到 dev 分支
git checkout dev
git merge hu/<business>_feature
git push origin dev

# 触发 Jenkins 构建
slpctl ci -w
```

### 5.5 生成 API 文档

```bash
slpctl swagger -projects <project-name> -out ~/.slp/swagger
```

---

## 📁 标准目录结构

```
<project>/
├── consts/
│   ├── redis.go                 # 全局 Redis Key
│   ├── nsq.go                   # 全局 NSQ Topic
│   └── <business>.go            # 业务专属常量
│
├── app/
│   ├── dao/
│   │   ├── internal/
│   │   │   └── <table_name>_dao.go
│   │   └── <TableName>.go
│   │
│   ├── pb/
│   │   ├── entity_<table_name>.pb.go
│   │   └── api_<business>_<action>.pb.go
│   │
│   ├── service/
│   │   └── <business>/
│   │       ├── service.go       # 主服务
│   │       ├── const.go         # 常量
│   │       ├── model.go         # 数据模型
│   │       └── <module>.go      # 子模块
│   │
│   └── utils/
│       └── <business>.go        # 工具函数
│
├── api/handler/
│   └── <business>_api.go        # HTTP Handler
│
├── rpc/server/internal/
│   └── <business>/
│       └── <business>_pretend.go  # Service
│
└── proto/
    ├── entity_<table_name>.proto
    └── api/
        └── api_<business>_<action>.proto
```

---

## ✅ 检查清单

### 数据库阶段
- [ ] DDL 编写完成
- [ ] 表结构验证通过
- [ ] 索引创建合理

### DAO 生成阶段
- [ ] `slpctl gen` 执行成功
- [ ] DAO 文件生成
- [ ] Proto 文件生成
- [ ] 编译通过

### API 生成阶段
- [ ] API 列表定义
- [ ] `slpctl code` 执行成功
- [ ] Handler 生成
- [ ] Service 骨架生成
- [ ] Proto 编译通过

### 业务实现阶段
- [ ] Service 逻辑填充
- [ ] 常量定义
- [ ] Redis Key 使用 `RedisKey` 结构体
- [ ] NSQ Topic 命名规范
- [ ] 工具函数无 IO

### 测试部署阶段
- [ ] 单元测试通过
- [ ] 代码提交
- [ ] Jenkins 构建成功
- [ ] API 文档生成

---

## 🔧 常用命令速查

```bash
# DAO 生成
slpctl gen -t xs_<table>

# API 生成（单个）
slpctl code -api /go/room/<biz>/<action> -desc "<desc>"

# API 生成（批量）
slpctl code -config apis.json

# Proto 编译
slpctl proto -p .
slpctl proto -t xs_<table> -p .

# Jenkins 构建
slpctl ci -w

# API 文档
slpctl swagger -projects <project> -out ~/.slp/swagger
```

---

## ⚠️ 常见坑点

### 1. 枚举类型未更新

**问题**：插入数据时报错 `Column 'type' cannot be null`

**解决**：
```sql
ALTER TABLE xs_chatroom 
MODIFY COLUMN property enum(..., '<new-type>') NOT NULL DEFAULT 'vip';
```

### 2. Proto 编译失败

**问题**：`protoc` 报错找不到 import 文件

**解决**：
```bash
# 清理旧的生成文件
rm app/pb/*.pb.go
rm proto/api/*.proto

# 重新生成
slpctl proto -p .
```

### 3. 路由未注册

**问题**：API 调用 404

**解决**：检查 `router/<business>.go` 是否注册路由

### 4. DAO 生成后编译报错

**问题**：`undefined: dao.<TableName>`

**原因**：DAO 文件生成后未重新编译或导入路径错误

**解决**：
```bash
# 清理并重新编译
go clean -cache
go build ./...

# 检查导入路径
grep "import.*dao" app/service/<business>/service.go
```

### 5. Proto 字段不匹配

**问题**：运行时 panic 或字段值为空

**原因**：`.proto` 文件修改后未重新生成 `.pb.go`

**解决**：
```bash
# 强制重新生成
slpctl proto -all -p .
```

**预防**：每次修改 proto 后必须执行 `slpctl proto`

### 6. Redis Key 冲突

**问题**：不同业务使用相同 Key 导致数据覆盖

**解决**：
- 业务专属 Key 使用统一前缀：`<business>:<type>:<id>`
- 全局 Key 在 `consts/redis.go` 中集中定义
- 避免硬编码 Key 字符串

### 7. NSQ 消息无法消费

**问题**：消息发送成功但消费者未收到

**排查步骤**：
```bash
# 1. 检查 Topic 是否正确
grep -r "<Business>Topic" app/ cmd/

# 2. 检查消费者是否启动
ps aux | grep <business>

# 3. 检查 NSQ 地址配置
cat config/config.toml | grep nsq

# 4. 查看 NSQAdmin 面板
http://<nsqadmin-host>:4171
```

### 8. 事务使用不当

**问题**：数据不一致或部分操作未回滚

**正确用法**：
```go
// ✅ 正确
err := gdb.Transaction(ctx, func(tx *gdb.TX) error {
    // 所有 DAO 调用传入 tx
    dao.User.Update(ctx, uid, data, tx)
    dao.Log.Insert(ctx, log, tx)
    return nil
})

// ❌ 错误 - 部分操作在事务外
gdb.Transaction(ctx, func(tx *gdb.TX) error {
    dao.User.Update(ctx, uid, data, tx)  // 事务内
    return nil
})
dao.Log.Insert(ctx, log)  // 事务外！
```

### 9. 常量定义位置混乱

**问题**：相同常量在多个文件重复定义

**规范**：
| 常量类型 | 定义位置 |
|----------|----------|
| 业务专属状态码 | `app/service/<biz>/const.go` |
| 全局 NSQ Topic | `consts/nsq.go` |
| 全局 Redis Key 模板 | `consts/redis.go` |
| 业务专属 Redis Key | `app/service/<biz>/const.go` |

### 10. 分支管理混乱

**问题**：代码合入错误分支导致发布问题

**规范流程**：
```bash
# 功能开发
git checkout master && git pull
git checkout -b hu/<feature>

# 合入 dev 测试
git checkout dev && git merge hu/<feature>
git push origin dev

# 验证通过后合入 master 发布
git checkout master && git merge dev
git push origin master
```

---

## 🔗 相关文档

| 文档 | 用途 |
|------|------|
| [[business-module-standard]] | 业务模块组织结构 |
| [[slpctl-usage-guide]] | slpctl 工具参考 |
| [[cmd-module-standard]] | CMD 模块开发规范 |
| [[room-type-development-template]] | 房间类型开发模板 |

---

**基于项目**: slp-go, slp-room, slp-starship  
**维护者**: SLP 开发团队
