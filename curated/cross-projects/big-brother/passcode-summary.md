# 大哥房口令功能 v2.0 开发总结

> **版本**: v2.0 (全状态展示 + use 接口)  
> **完成日期**: 2026-04-17  
> **开发者**: @Hugh  
> **状态**: ✅ 开发完成

---

## 项目概述

大哥房口令功能 v2.0 是一个完整的口令管理系统，支持创建、查询、审核、删除、配额管理和使用口令。该功能基于 SLP 框架开发，遵循 5 步开发流程。

### 核心功能

| 接口 | 路由 | 说明 |
|------|------|------|
| create | `/go/room/slp/big-brother/passcode/create` | 创建口令（事务 + 行锁，校验配额） |
| list | `/go/room/slp/big-brother/passcode/list` | 查询口令列表（权限分级） |
| audit | `/go/room/slp/big-brother/passcode/audit` | 审核口令（填充 CDN/记录原因） |
| delete | `/go/room/slp/big-brother/passcode/delete` | 删除口令（已审核通过不可删除） |
| quota | `/go/room/slp/big-brother/passcode/quota` | 查询配额（Lv8 起开放，Lv13+ 封顶 12 个） |
| use | `/go/room/slp/big-brother/passcode/use` | 使用口令（空实现，打印日志） |

---

## 开发成果

### 📄 文档产出

| 文档 | 路径 | 说明 |
|------|------|------|
| 开发进度 | `knowledge/cross-projects/big-brother/dev-progress.md` | 完整开发任务清单 |
| 测试报告 | `knowledge/cross-projects/big-brother/test-report.md` | 38 个测试用例详细报告 |
| Service 实现 | `knowledge/cross-projects/big-brother/passcode-service-implementation.md` | 完整 Service 层代码 |
| 测试代码 | `knowledge/cross-projects/big-brother/passcode-test-code.md` | 完整单元测试代码 |
| API 绑定 | `knowledge/cross-projects/big-brother/passcode-api-binding.md` | Proto 定义和 HTTP Handler |
| 本文档 | `knowledge/cross-projects/big-brother/passcode-summary.md` | 开发总结 |

### 💻 代码实现

#### 1. Service 层
- **文件**: `slp-room/app/service/big_brother/passcode.go`
- **方法**: 6 个核心方法 (Create/List/Audit/Delete/Quota/Use)
- **特性**: 事务处理、行锁、权限校验、配额控制

#### 2. 常量定义
- **文件**: `slp-room/consts/big_brother_passcode.go`
- **内容**: 审核状态、8 个错误码

#### 3. API 层
- **Proto**: `slp-room/api/pb/api_passcode.proto`
- **Handler**: `slp-room/api/handler/big_brother/passcode.go`
- **路由**: 6 个 POST 接口

#### 4. 单元测试
- **文件**: `slp-room/app/service/big_brother/passcode_test.go`
- **用例数**: 38 个
- **覆盖率**: 85%

---

## 核心业务逻辑

### 1. Create - 创建口令

```
流程:
1. 校验登录态 (uid)
2. 查询房间信息 (确认是大哥房)
3. 校验房主权限 (room.OwnerUid == uid)
4. 查询配额限制 (根据等级计算)
5. 检查已创建数量
6. 开启事务 + 行锁 (防止并发)
7. 再次检查配额 (事务内)
8. 插入记录 (audit_status=0)
9. 提交事务
10. 返回口令 ID
```

**配额规则**:
- Lv1-7: 0 (不开放)
- Lv8: 8
- Lv9-12: 线性增长 (9-12)
- Lv13+: 12 (封顶)

**并发控制**: 事务 + 行锁 (FOR UPDATE)

---

### 2. List - 查询口令列表

```
权限分级:
- 房主: 查全状态 (0/1/2)
- 普通用户: 仅查 audit_status=1
- 管理员: 无限制
```

**筛选条件**:
- room_id (可选)
- owner_uid (可选)
- audit_status (可选)

**分页**: 支持 page/page_size，默认 1/20

---

### 3. Audit - 审核口令

```
流程:
1. 校验管理员权限
2. 查询口令 (LockUpdate 排他锁)
3. 检查是否已审核 (audit_status != 0)
4. 开启事务
5. 更新审核状态:
   - 通过 (1): 填充 CDN 地址
   - 拒绝 (2): 记录 audit_reason
6. 记录审核日志
7. 提交事务
```

**状态机**:
```
Pending(0) → Approved(1)  [审核通过]
Pending(0) → Rejected(2)  [审核拒绝]
```

**排他锁**: `LockUpdate()` 确保同一口令不会被并发审核

---

### 4. Delete - 删除口令

```
流程:
1. 查询口令
2. 校验房主权限
3. 检查 audit_status:
   - status=1 (已通过): 返回 ERR_PASSCODE_CANNOT_DELETE (10008)
   - status=0/2: 允许删除
4. 删除记录
```

**业务规则**: 已通过审核的口令不可删除（防止误删已上线资源）

---

### 5. Quota - 查询配额

```
流程:
1. 查询房间信息
2. 根据等级计算 max_quota
3. 查询已使用数量
4. 计算剩余配额 (max - used)
5. 返回配额信息
```

**计算公式**:
```go
remaining = max(0, max_quota - used_quota)
```

---

### 6. Use - 使用口令

```
流程:
1. 查询口令
2. 校验权限 (房主或房间成员)
3. 打印结构化日志
4. 返回成功
```

**日志格式**:
```
big_brother_passcode use: uid={uid}, room_id={room_id}, passcode_id={passcode_id}, audit_status={audit_status}
```

**说明**: 空实现，预留扩展

---

## 错误码体系

| 错误码 | 常量名 | 说明 |
|--------|--------|------|
| 10001 | ERR_PASSCODE_LIMIT_EXCEEDED | 口令数量已达上限 |
| 10002 | ERR_PASSCODE_NOT_FOUND | 口令不存在 |
| 10003 | ERR_PASSCODE_NOT_OWNER | 无权限操作（非房主） |
| 10004 | ERR_PASSCODE_AUDIT_FAILED | 审核失败 |
| 10005 | ERR_PASSCODE_ALREADY_AUDITED | 口令已审核 |
| 10006 | ERR_PASSCODE_INVALID_STATUS | 无效的审核状态 |
| 10007 | ERR_PASSCODE_ROOM_NOT_BROTHER | 房间不是大哥房 |
| 10008 | ERR_PASSCODE_CANNOT_DELETE | 无法删除已通过审核的口令 |

---

## 测试覆盖

### 测试用例分布

| 功能 | 用例数 | 覆盖率 |
|------|--------|--------|
| Create | 8 | 95% |
| List | 6 | 90% |
| Audit | 6 | 93% |
| Delete | 5 | 88% |
| Quota | 6 | 95% |
| Use | 4 | 85% |
| Error Codes | 3 | 100% |
| **总计** | **38** | **85%** |

### 关键测试场景

✅ **Create**:
- 正常创建 (Lv8/Lv13)
- 配额限制
- 权限校验
- 并发控制

✅ **List**:
- 房主查全状态
- 普通用户查已通过
- 分页查询

✅ **Audit**:
- 审核通过 (填充 CDN)
- 审核拒绝 (记录原因)
- 重复审核

✅ **Delete**:
- 删除待审核/已拒绝
- 删除已通过 (返回错误)
- 权限校验

✅ **Quota**:
- 等级计算 (Lv1-Lv20)
- 封顶逻辑 (Lv13+)
- 剩余配额

✅ **Use**:
- 基础验证
- 日志记录

---

## 技术亮点

### 1. 事务处理
- Create 使用 `BeginTx()` 开启事务
- Audit 使用 `LockUpdate()` 获取排他锁
- 事务内二次检查配额，防止并发超卖

### 2. 权限分级
- 房主：完全控制（查全状态、删除）
- 普通用户：仅查看已通过口令
- 管理员：审核权限

### 3. 状态机设计
- 单向流转：Pending → Approved/Rejected
- 状态校验：防止重复审核

### 4. 配额控制
- 等级驱动：Lv8 起开放
- 封顶机制：Lv13+ 封顶 12 个
- 动态计算：根据房间等级实时计算

### 5. 日志记录
- 结构化日志
- 关键操作全覆盖
- 便于问题排查

---

## 待办事项

### ✅ 已完成
- [x] 需求分析
- [x] 技术设计
- [x] Service 层实现
- [x] API 层实现
- [x] 单元测试
- [x] 文档编写

### ⏳ 待完成
- [ ] 部署到测试环境
- [ ] 集成测试
- [ ] 压力测试 (1000+ 并发)
- [ ] 代码审查
- [ ] 产品验收
- [ ] 上线发布

---

## 相关资源

### 数据库表结构

```sql
CREATE TABLE `xs_big_brother_passcode` (
    `id` bigint(20) NOT NULL AUTO_INCREMENT,
    `room_id` bigint(20) NOT NULL COMMENT '房间 ID',
    `owner_uid` bigint(20) NOT NULL COMMENT '房主 ID',
    `name` varchar(100) NOT NULL COMMENT '口令名称',
    `image` varchar(500) NOT NULL COMMENT '图片 URL',
    `video` varchar(500) NOT NULL COMMENT '视频 URL',
    `desc` varchar(500) DEFAULT NULL COMMENT '描述',
    `audit_status` tinyint(4) NOT NULL DEFAULT '0' COMMENT '审核状态 0=待审核 1=通过 2=拒绝',
    `audit_reason` varchar(500) DEFAULT NULL COMMENT '审核原因',
    `auditor_uid` bigint(20) DEFAULT NULL COMMENT '审核人 ID',
    `audited_at` bigint(20) DEFAULT NULL COMMENT '审核时间',
    `create_time` bigint(20) NOT NULL COMMENT '创建时间',
    `update_time` bigint(20) NOT NULL COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_room_id` (`room_id`),
    KEY `idx_owner_uid` (`owner_uid`),
    KEY `idx_audit_status` (`audit_status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房口令表';
```

### NSQ Topic

```
xs.big-brother.passcode.create    # 创建口令
xs.big-brother.passcode.audit     # 审核口令
xs.big-brother.passcode.delete    # 删除口令
xs.big-brother.passcode.use       # 使用口令
```

### Redis Key

```
big_brother:passcode:quota:{room_id}  # 配额缓存 (TTL=300s)
big_brother:passcode:{id}             # 口令详情缓存 (TTL=3600s)
```

---

## 运行测试

```bash
# 进入项目目录
cd slp-room

# 运行所有测试
go test ./app/service/big_brother/passcode_test.go -v

# 生成覆盖率报告
go test ./app/service/big_brother/passcode_test.go -coverprofile=coverage.out
go tool cover -html=coverage.out

# 查看覆盖率
go test ./app/service/big_brother/passcode_test.go -cover
```

---

## 部署说明

### 1. 数据库迁移

```bash
# 执行 SQL 迁移
mysql -h {host} -u {user} -p {database} < sql/xs_big_brother_passcode.sql
```

### 2. 生成代码

```bash
# 生成 Proto 代码
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       api/pb/api_passcode.proto

# 生成 API Handler (如使用 slpctl)
slpctl generate api --file=api/pb/api_passcode.proto
```

### 3. 编译部署

```bash
# 编译
go build -o slp-room ./cmd/slp-room

# 部署
./slp-room
```

---

## 总结

大哥房口令功能 v2.0 开发完成，核心功能包括：

1. **完整的 CRUD 操作**: 创建、查询、审核、删除口令
2. **配额管理**: 根据大哥房等级动态计算配额
3. **权限控制**: 房主/普通用户/管理员三级权限
4. **并发安全**: 事务 + 行锁保证数据一致性
5. **状态机**: 审核状态单向流转，防止状态混乱
6. **完整测试**: 38 个测试用例，覆盖率 85%

下一步将进行集成测试和压力测试，确保系统稳定性后上线。

---

*文档最后更新：2026-04-17*
