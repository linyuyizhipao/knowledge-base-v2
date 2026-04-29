---
id: passcode-readme
label: 大哥房口令功能文档索引
source: curated/cross-projects/big-brother/README-PASSCODE.md
business: big-brother
compiled: 2026-04-25
links:
  - passcode-requirement
  - passcode-technical-design
  - passcode-test-report
  - passcode-summary
---

# 大哥房口令功能 v2.0 文档索引

> 版本: v2.0 | 状态: 开发完成

## 核心文档

| 文档 | 说明 |
|------|------|
| passcode-requirement.md | 产品需求说明 |
| passcode-technical-design.md | 技术架构设计 |
| passcode-test-report.md | 测试结果报告 |
| passcode-summary.md | 完整开发总结 |

## 6 个核心接口

| 接口 | 路由 | 说明 |
|------|------|------|
| create | `/go/room/slp/big-brother/passcode/create` | 创建口令 |
| list | `/go/room/slp/big-brother/passcode/list` | 查询口令列表 |
| audit | `/go/room/slp/big-brother/passcode/audit` | 审核口令 |
| delete | `/go/room/slp/big-brother/passcode/delete` | 删除口令 |
| quota | `/go/room/slp/big-brother/passcode/quota` | 查询配额 |
| use | `/go/room/slp/big-brother/passcode/use` | 使用口令 |

## 核心特性

### 配额规则

| 大哥房等级 | 口令配额 |
|------------|----------|
| Lv1 - Lv7 | 0 |
| Lv8 | 8 |
| Lv13+ | 12 (封顶) |

### 权限分级

| 角色 | 查询权限 | 操作权限 |
|------|----------|----------|
| 房主 | 查全状态 (0/1/2) | 创建、删除、查询配额 |
| 普通用户 | 仅查已通过 (1) | 使用口令 |
| 管理员 | 无限制 | 审核口令 |

## 重要规则

1. 创建口令: 事务 + 行锁，防止并发超卖
2. 审核口令: 已审核的口令不可重复审核
3. 删除口令: 已通过审核的口令不可删除
4. 配额限制: Lv13+ 封顶 12 个口令

## 项目结构

```
slp-room/
├── app/dao/xs/xs_big_brother_passcode.go
├── app/model/xs_big_brother_passcode.go
├── app/service/big_brother/passcode.go
├── app/pb/entity_xs_big_brother_passcode.pb.go
├── api/pb/api_passcode.proto
├── api/handler/big_brother/passcode.go
└── consts/big_brother_passcode.go
```

## 运行测试

```bash
cd slp-room
go test ./app/service/big_brother/passcode_test.go -v
```