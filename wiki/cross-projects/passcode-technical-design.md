---
id: passcode-technical-design
label: 大哥房口令功能技术设计
source: curated/cross-projects/big-brother/passcode-technical-design.md
business: big-brother
compiled: 2026-04-25
links:
  - passcode-requirement
  - passcode-summary
---

# 大哥房口令功能技术设计

> 大哥房口令功能技术开发文档

## 技术栈

| 组件 | 技术选型 |
|------|----------|
| 语言 | Go 1.21+ |
| 框架 | Go Frame V1.15.4 |
| 数据库 | MySQL 5.7 |
| ORM | Go Frame DAO |
| 缓存 | Redis |

## 代码结构

```
slp-room/
├── app/
│   ├── dao/xs_big_brother_passcode.go
│   ├── service/big_brother/passcode.go
│   ├── controller/big_brother/passcode.go
│   └── def/error_code.go
└── consts/big_brother_passcode.go
```

## 业务流程伪代码

### 创建口令

```
校验登录态 → 校验房间大哥房 → 校验房主权限 → 查询配额 → 开启事务 → 插入记录 → 返回 ID
```

### 审核口令

```
校验管理员 → 查询口令(LockUpdate) → 检查已审核 → 开启事务 → 更新状态 → 记录日志
```

### 查询列表

```
校验登录态 → 构建查询 → 权限过滤 → 执行分页 → 返回结果
```

### 使用口令

```
校验登录态 → 校验口令存在 → 校验 audit_status=1 → 校验房主 → 打印日志 → 返回成功
```

## 代码生成命令

```bash
slpctl gen -t xs_big_brother_passcode
slpctl code -api /go/room/bigbrother/create
```

## 配额配置

```go
var passcodeLimitMap = map[uint8]uint8{
    8: 8,   // Lv8: 8 个
    9: 9,   // Lv9: 9 个
    10: 10, // Lv10: 10 个
    11: 11, // Lv11: 11 个
    12: 12, // Lv12: 12 个
    13: 12, // Lv13+: 12 个封顶
}
```

## 事务处理示例

```go
err := dao.XsBigBrotherPasscode.DB.Transaction(func(tx *gdb.TX) error {
    // 1. 检查房间是否为大哥哥房
    // 2. 检查口令数量限制
    // 3. 插入口令记录
})
```

## 开发任务清单

| 阶段 | 任务 |
|------|------|
| 数据库层 | DDL 创建 → DAO 生成 |
| API 层 | Service + Handler + Proto |
| 验证部署 | Proto 生成 → 路由注册 → 测试验证 |