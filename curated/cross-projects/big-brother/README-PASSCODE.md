# 大哥房口令功能 v2.0 文档索引

> **版本**: v2.0  
> **状态**: ✅ 开发完成  
> **最后更新**: 2026-04-17

---

## 📚 文档导航

### 核心文档

| 文档 | 说明 | 链接 |
|------|------|------|
| 📋 需求文档 | 产品需求说明 | [passcode-requirement.md](./passcode-requirement.md) |
| 🏗️ 技术设计 | 技术架构设计 | [passcode-technical-design.md](./passcode-technical-design.md) |
| 📝 开发进度 | 开发任务清单 | [dev-progress.md](./dev-progress.md) |
| 📊 测试报告 | 测试结果报告 | [test-report.md](./test-report.md) |
| 📖 开发总结 | 完整开发总结 | [passcode-summary.md](./passcode-summary.md) |

### 实现文档

| 文档 | 说明 | 链接 |
|------|------|------|
| 💻 Service 实现 | 完整 Service 层代码 | [passcode-service-implementation.md](./passcode-service-implementation.md) |
| 🧪 测试代码 | 完整单元测试代码 | [passcode-test-code.md](./passcode-test-code.md) |
| 🔌 API 绑定 | Proto 和 HTTP Handler | [passcode-api-binding.md](./passcode-api-binding.md) |

---

## 🚀 快速开始

### 1. 查看需求

阅读 [需求文档](./passcode-requirement.md) 了解功能需求。

### 2. 查看技术设计

阅读 [技术设计文档](./passcode-technical-design.md) 了解架构设计。

### 3. 查看代码实现

- [Service 层实现](./passcode-service-implementation.md) - 核心业务逻辑
- [API 层实现](./passcode-api-binding.md) - 接口定义和路由
- [测试代码](./passcode-test-code.md) - 单元测试示例

### 4. 运行测试

```bash
cd slp-room
go test ./app/service/big_brother/passcode_test.go -v
```

### 5. 查看测试结果

阅读 [测试报告](./test-report.md) 了解测试覆盖率和结果。

---

## 📋 功能概览

### 6 个核心接口

| 接口 | 路由 | 说明 |
|------|------|------|
| **create** | `/go/room/slp/big-brother/passcode/create` | 创建口令（事务 + 行锁，校验配额） |
| **list** | `/go/room/slp/big-brother/passcode/list` | 查询口令列表（权限分级） |
| **audit** | `/go/room/slp/big-brother/passcode/audit` | 审核口令（填充 CDN/记录原因） |
| **delete** | `/go/room/slp/big-brother/passcode/delete` | 删除口令（已审核通过不可删除） |
| **quota** | `/go/room/slp/big-brother/passcode/quota` | 查询配额（Lv8 起开放，Lv13+ 封顶 12 个） |
| **use** | `/go/room/slp/big-brother/passcode/use` | 使用口令（空实现，打印日志） |

---

## 🎯 核心特性

### 配额规则

| 大哥房等级 | 口令配额 | 说明 |
|------------|----------|------|
| Lv1 - Lv7 | 0 | 暂不开放 |
| Lv8 | 8 | 起始等级 |
| Lv9 - Lv12 | 9-12 | 线性增长 |
| Lv13+ | 12 | 上限封顶 |

### 审核状态

| 状态值 | 状态名 | 说明 |
|--------|--------|------|
| 0 | AuditStatusPending | 待审核 |
| 1 | AuditStatusApproved | 审核通过 |
| 2 | AuditStatusRejected | 审核拒绝 |

### 权限分级

| 角色 | 查询权限 | 操作权限 |
|------|----------|----------|
| 房主 | 查全状态 (0/1/2) | 创建、删除、查询配额 |
| 普通用户 | 仅查已通过 (1) | 使用口令 |
| 管理员 | 无限制 | 审核口令 |

---

## ⚠️ 重要规则

1. **创建口令**: 事务 + 行锁，防止并发超卖
2. **审核口令**: 已审核的口令不可重复审核
3. **删除口令**: 已通过审核的口令不可删除 (错误码 10008)
4. **配额限制**: Lv13+ 封顶 12 个口令
5. **权限校验**: 所有操作需校验房主权限

---

## 🔢 错误码

| 错误码 | 说明 |
|--------|------|
| 10001 | 口令数量已达上限 |
| 10002 | 口令不存在 |
| 10003 | 无权限操作（非房主） |
| 10004 | 审核失败 |
| 10005 | 口令已审核 |
| 10006 | 无效的审核状态 |
| 10007 | 房间不是大哥房 |
| 10008 | 无法删除已通过审核的口令 |

---

## 📊 测试结果

- **测试用例**: 38 个
- **代码覆盖率**: 85%
- **通过测试**: 38 个
- **失败测试**: 0 个

详细测试结果见 [测试报告](./test-report.md)。

---

## 🛠️ 技术栈

- **语言**: Go 1.21+
- **框架**: Go Frame V1.15.4
- **数据库**: MySQL 5.7
- **缓存**: Redis 6.0
- **消息队列**: NSQ
- **测试框架**: Go Testing + gomock

---

## 📁 项目结构

```
slp-room/
├── app/
│   ├── dao/
│   │   └── xs/
│   │       └── xs_big_brother_passcode.go    # DAO 层
│   ├── model/
│   │   └── xs_big_brother_passcode.go        # Model
│   ├── service/
│   │   └── big_brother/
│   │       ├── passcode.go                   # Service 层
│   │       └── passcode_test.go              # 单元测试
│   └── pb/
│       └── entity_xs_big_brother_passcode.pb.go
├── api/
│   ├── pb/
│   │   └── api_passcode.proto                # Proto 定义
│   └── handler/
│       └── big_brother/
│           └── passcode.go                   # API Handler
└── consts/
    └── big_brother_passcode.go               # 常量定义
```

---

## 🔗 相关链接

- [大哥房宠物功能](./pet-feature.md) - 参考实现
- [SLP 开发规范](../slp-dev-guide.md) - 开发规范
- [错误码规范](../error-code-guide.md) - 错误码定义规范

---

## 📞 联系方式

- **开发者**: @Hugh
- **项目**: slp-harness
- **分支**: feature/passcode-v2

---

*文档最后更新：2026-04-17*
