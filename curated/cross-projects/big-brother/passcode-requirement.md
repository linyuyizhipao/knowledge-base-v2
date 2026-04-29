# 大哥房口令功能需求

> **版本**：v2.0（第二迭代）  
> **状态**：需求已冻结，待开发  
> **最后更新**：2026-04-17  
> **负责人**：@Hugh  

## 需求背景

大哥房口令功能是大哥房项目的一个子功能，允许大哥房房主创建和管理"口令"资源。

**业务价值**：
- 增强大哥房的个性化展示能力
- 提升房主的归属感和荣誉感
- 为后续大哥房商业化玩法奠定基础

## 核心概念

### 口令（Passcode）

- **定义**：由大哥房房主创建的一种特殊资源，用于在房间内展示房主的个性化内容
- **创建者**：仅限大哥房房主（需要权限校验）
- **等级限制**：根据大哥房等级，可创建的口令个数不同
- **审核机制**：所有口令必须经过后台审核才能展示
- **资源组成**：包含名称、描述、图片、视频四要素

### 口令数据结构

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int64 | - | 口令 ID（主键） |
| room_id | int64 | 是 | 大哥房 ID |
| owner_uid | int64 | 是 | 房主用户 ID |
| name | string | 是 | 口令名称（限 100 字符） |
| description | string | 否 | 口令描述（限 500 字符） |
| image | string | 是 | 口令图片（URL 或资源 ID） |
| video | string | 是 | MP4 视频资源（URL 或资源 ID） |
| audit_status | int | - | 审核状态（0-待审核，1-审核通过，2-审核拒绝） |
| audit_reason | string | 否 | 审核拒绝原因 |
| auditor_uid | int64 | 否 | 审核人 ID |
| audited_at | datetime | 否 | 审核时间 |
| create_time | datetime | - | 创建时间 |
| update_time | datetime | - | 更新时间 |

### 大哥房等级与口令数量配置

| 大哥房等级 | 可创建口令个数 | 说明 |
|------------|----------------|------|
| Lv1 - Lv7 | 0 | 暂不开放 |
| Lv8 | 8 个 | 起始等级 |
| Lv9 | 9 个 | - |
| Lv10 | 10 个 | - |
| Lv11 | 11 个 | - |
| Lv12 | 12 个 | - |
| Lv13+ | 12 个 | 上限封顶 |

## 功能需求

### 1. 口令创建

**前置条件**：
- 用户必须是房间 owner
- 房间必须是大哥房类型
- 房主当前口令数量 < 等级允许的最大数量

**功能描述**：
- 大哥房房主可以申请创建口令
- 创建时需要填写：名称、描述、上传图片、上传视频
- 创建后状态为"待审核"（`audit_status = 0`）
- 创建数量受大哥房等级限制

**校验规则**：
```
1. 房间类型校验：room.type == BIG_BROTHER
2. 权限校验：current_user.uid == room.owner_uid
3. 数量校验：count(passcode where owner_uid=uid AND audit_status IN(0,1)) < limit(level)
4. 内容校验：
   - name: 1-100 字符，不允许特殊字符
   - description: 0-500 字符
   - image: 必须为有效图片 URL 或资源 ID
   - video: 必须为有效 MP4 URL 或资源 ID
```

### 2. 口令审核

**审核方式**：后台手动审核

**状态流转**：
```
[待审核 audit_status=0] 
    ├─ 审核通过 → [已通过 audit_status=1]
    └─ 审核拒绝 → [已拒绝 audit_status=2]
```

**审核操作**：
- 更新 `audit_status` 状态
- 填充最终的资源地址（`image`、`video`）（审核通过时使用正式 CDN 地址）
- 审核拒绝时可填写拒绝原因（可选）
- 记录审核人 ID 和审核时间

**审核权限**：
- 仅后台管理员可审核
- 需要记录审核日志（操作人、时间、IP）

### 3. 口令展示

**展示场景**：
- 审核通过的口令在**大哥房内**使用
- 通过**独立接口**查询审核通过的口令列表
- 支持按房间 ID、房主 UID 等维度查询

**查询过滤**：
- C 端用户：仅查询 `audit_status=1`（已通过）
- 房主本人：可查询自己所有口令（全状态展示）
- 后台管理员：可按任意条件查询

**前端展示规则**：
- 房主管理端：展示所有状态的口令（待审核、已通过、已拒绝）
- 前端需加状态标签区分：
  - `待审核`（audit_status=0）：灰色/黄色标签
  - `已通过`（audit_status=1）：绿色标签
  - `已拒绝`（audit_status=2）：红色标签，展示拒绝原因
- C 端用户可见场景：仅展示 `audit_status=1` 的口令

### 4. 等级配置

- 大哥房等级与可创建口令个数在**代码中硬编码配置**
- 配置逻辑：8 级及以上才有固定个数，8 级以下暂不开放或为 0
- 配置表见【核心概念】章节

### 5. 口令管理（补充）

**房主可执行的操作**：
- 创建口令（受数量限制）
- 查看自己的口令列表（全状态）
- 删除待审核/已拒绝的口令

**不可执行的操作**：
- ~~修改已通过口令的内容~~（需走重新审核流程）
- ~~删除已通过口令~~（仅可删除待审核/已拒绝状态）

**删除规则**：
- 仅可删除 `audit_status IN (0, 2)` 的口令
- 删除后释放数量配额

## API 接口设计

### 1. 创建口令申请

**接口**：`POST /go/slp/big-brother/passcode/create`

**权限**：登录用户，且为房间 owner

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| room_id | int64 | 是 | 大哥房 ID |
| name | string | 是 | 口令名称（1-100 字符） |
| description | string | 否 | 口令描述（0-500 字符） |
| image | string | 是 | 图片资源（临时/占位） |
| video | string | 是 | 视频资源（临时/占位） |

**返回**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 123,
    "audit_status": 0,
    "create_time": 1713254400
  }
}
```

**错误码**：
- `10001` - 口令数量已达上限
- `10007` - 房间不是大哥房
- `10003` - 无权限操作（非房主）

---

### 2. 口令列表查询

**接口**：`GET /go/slp/big-brother/passcode/list`

**权限**：登录用户

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| room_id | int64 | 是 | 大哥房 ID |
| owner_uid | int64 | 否 | 房主 UID（不传则查 room_id 对应的房主） |
| audit_status | int | 否 | 审核状态（不传则默认查询已通过的） |

**行为逻辑**：
- 普通用户：仅能查询 `audit_status=1` 的记录
- 房主本人：可查询自己所有记录（全状态）
- 后台管理员：无限制

**返回**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "list": [
      {
        "id": 123,
        "room_id": 456,
        "owner_uid": 789,
        "name": "口令名称",
        "description": "描述",
        "image": "https://...",
        "video": "https://...",
        "audit_status": 1,
        "create_time": 1713254400
      }
    ],
    "total": 1
  }
}
```

---

### 3. 审核口令（后台接口）

**接口**：`POST /go/slp/big-brother/passcode/audit`

**权限**：后台管理员

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int64 | 是 | 口令 ID |
| audit_status | int | 是 | 审核状态（1-通过，2-拒绝） |
| image | string | 否 | 正式图片资源地址（审核通过时必填） |
| video | string | 否 | 正式视频资源地址（审核通过时必填） |
| audit_reason | string | 否 | 拒绝原因 |

**返回**：
```json
{
  "code": 0,
  "msg": "success"
}
```

**错误码**：
- `10002` - 口令不存在
- `10005` - 口令已审核
- `10006` - 无效的审核状态

---

### 4. 删除口令（补充）

**接口**：`POST /go/slp/big-brother/passcode/delete`

**权限**：登录用户，且为口令 owner

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int64 | 是 | 口令 ID |

**返回**：
```json
{
  "code": 0,
  "msg": "success"
}
```

**错误码**：
- `10002` - 口令不存在
- `10003` - 无权限操作
- `10008` - 无法删除已通过审核的口令

---

### 5. 获取房主等级和口令配额（补充）

**接口**：`GET /go/slp/big-brother/passcode/quota`

**权限**：登录用户

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| room_id | int64 | 是 | 大哥房 ID |

**返回**：
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "room_id": 456,
    "owner_uid": 789,
    "level": 10,
    "max_quota": 10,
    "used_quota": 5,
    "remaining_quota": 5
  }
}
```

---

### 6. 使用口令（新增）

**接口**：`POST /go/slp/big-brother/passcode/use`

**权限**：登录用户

**请求参数**：
| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | int64 | 是 | 口令 ID |
| room_id | int64 | 是 | 大哥房 ID |

**行为逻辑**：
- 验证口令存在且属于该房间
- 验证 `audit_status=1`（仅审核通过的口令可用）
- 验证当前用户为房主（`owner_uid == current_user.uid`）
- **空实现**：仅打印日志，不发放奖励，不做实际业务逻辑

**日志格式**：
```json
{
  "module": "big_brother_passcode",
  "action": "use",
  "uid": 123,
  "room_id": 456,
  "passcode_id": 789,
  "audit_status": 1,
  "timestamp": 1713254400
}
```

**返回**：
```json
{
  "code": 0,
  "msg": "success"
}
```

**错误码**：
- `10002` - 口令不存在
- `10003` - 无权限操作（非房主）
- `10006` - 无效的审核状态（口令未通过审核）
- `10007` - 房间不是大哥房

## 技术设计

### 数据库设计

#### 表结构

```sql
CREATE TABLE `xs_big_brother_passcode` (
    `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '口令 ID（主键）',
    `room_id` BIGINT(20) UNSIGNED NOT NULL COMMENT '大哥房 ID',
    `owner_uid` BIGINT(20) UNSIGNED NOT NULL COMMENT '房主用户 ID',
    `name` VARCHAR(100) NOT NULL COMMENT '口令名称',
    `description` VARCHAR(500) DEFAULT NULL COMMENT '口令描述',
    `image` VARCHAR(255) DEFAULT NULL COMMENT '图片资源 URL/ID',
    `video` VARCHAR(255) DEFAULT NULL COMMENT '视频资源 URL/ID',
    `audit_status` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '审核状态：0-待审核，1-通过，2-拒绝',
    `audit_reason` VARCHAR(255) DEFAULT NULL COMMENT '审核拒绝原因',
    `auditor_uid` BIGINT(20) UNSIGNED DEFAULT NULL COMMENT '审核人 ID',
    `audited_at` DATETIME DEFAULT NULL COMMENT '审核时间',
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    PRIMARY KEY (`id`),
    KEY `idx_room_id` (`room_id`) COMMENT '房间 ID 索引',
    KEY `idx_owner_uid` (`owner_uid`) COMMENT '房主 ID 索引',
    KEY `idx_audit_status` (`audit_status`) COMMENT '审核状态索引',
    KEY `idx_create_time` (`create_time`) COMMENT '创建时间索引'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房口令表';
```

#### 索引设计说明

| 索引名 | 字段 | 类型 | 说明 |
|--------|------|------|------|
| `PRIMARY` | `id` | 主键 | 自增主键 |
| `idx_room_id` | `room_id` | 普通索引 | 按房间查询口令列表 |
| `idx_owner_uid` | `owner_uid` | 普通索引 | 按房主查询口令 |
| `idx_audit_status` | `audit_status` | 普通索引 | 审核后台查询待审核/已通过 |
| `idx_create_time` | `create_time` | 普通索引 | 按时间排序 |

#### SQL 语句示例

**1. 创建口令**
```sql
INSERT INTO `xs_big_brother_passcode` 
    (`room_id`, `owner_uid`, `name`, `description`, `image`, `video`, `audit_status`) 
VALUES 
    (?, ?, ?, ?, ?, ?, 0);
```

**2. 查询房间口令列表（仅审核通过）**
```sql
SELECT id, room_id, owner_uid, name, description, image, video, create_time 
FROM `xs_big_brother_passcode` 
WHERE room_id = ? AND audit_status = 1 
ORDER BY create_time DESC;
```

**3. 查询房主的口令（包含待审核）**
```sql
SELECT * FROM `xs_big_brother_passcode` 
WHERE owner_uid = ? 
ORDER BY audit_status ASC, create_time DESC;
```

**4. 审核通过**
```sql
UPDATE `xs_big_brother_passcode` 
SET audit_status = 1, 
    image = ?, 
    video = ?, 
    auditor_uid = ?, 
    audited_at = NOW() 
WHERE id = ? AND audit_status = 0;
```

**5. 审核拒绝**
```sql
UPDATE `xs_big_brother_passcode` 
SET audit_status = 2, 
    audit_reason = ?, 
    auditor_uid = ?, 
    audited_at = NOW() 
WHERE id = ? AND audit_status = 0;
```

**6. 检查房主当前口令数量**
```sql
SELECT COUNT(*) AS total 
FROM `xs_big_brother_passcode` 
WHERE owner_uid = ? AND audit_status IN (0, 1);
```

### 错误码定义

```go
// app/def/error_code.go
const (
    // 大哥房口令错误码 (10000-10099)
    ERR_PASSCODE_LIMIT_EXCEEDED   = 10001  // 口令数量已达上限
    ERR_PASSCODE_NOT_FOUND        = 10002  // 口令不存在
    ERR_PASSCODE_NOT_OWNER        = 10003  // 无权限操作（非房主）
    ERR_PASSCODE_AUDIT_FAILED     = 10004  // 审核失败
    ERR_PASSCODE_ALREADY_AUDITED  = 10005  // 口令已审核
    ERR_PASSCODE_INVALID_STATUS   = 10006  // 无效的审核状态
    ERR_PASSCODE_ROOM_NOT_BROTHER = 10007  // 房间不是大哥房
)
```

### 事务处理

**创建口令事务**
```go
err := dao.XsBigBrotherPasscode.DB.Transaction(func(tx *gdb.TX) error {
    // 1. 检查房间是否为大哥哥房
    brother, err := dao.XsChatroomBigBrother.Ctx(ctx).TX(tx).FindOne("rid=?", req.RoomId)
    if err != nil || brother == nil {
        return errors.New("房间不是大哥房")
    }
    
    // 2. 检查口令数量限制
    count, err := dao.XsBigBrotherPasscode.Ctx(ctx).TX(tx).
        Where("owner_uid=? AND audit_status IN(0,1)", uid).Count()
    if err != nil {
        return err
    }
    if count >= getMaxPasscodeLimit(brother.Level) {
        return errors.New("口令数量已达上限")
    }
    
    // 3. 插入口令记录
    _, err = dao.XsBigBrotherPasscode.Ctx(ctx).TX(tx).Data(g.Map{
        "room_id": req.RoomId,
        "owner_uid": uid,
        "name": req.Name,
        "description": req.Description,
        "image": req.Image,
        "video": req.Video,
        "audit_status": 0,
    }).Insert()
    
    return err
})
```

**审核口令事务**
```go
err := dao.XsBigBrotherPasscode.DB.Transaction(func(tx *gdb.TX) error {
    // 1. 查询口令记录（排他锁）
    record, err := dao.XsBigBrotherPasscode.Ctx(ctx).TX(tx).
        Where("id=?", req.Id).LockUpdate().FindOne()
    if err != nil || record == nil {
        return errors.New("口令不存在")
    }
    
    // 2. 检查是否已审核
    if record.AuditStatus != 0 {
        return errors.New("口令已审核")
    }
    
    // 3. 更新审核状态
    data := g.Map{
        "audit_status": req.AuditStatus,
        "auditor_uid": auditorUid,
        "audited_at": time.Now(),
    }
    if req.AuditStatus == 1 {
        data["image"] = req.Image
        data["video"] = req.Video
    } else if req.AuditStatus == 2 {
        data["audit_reason"] = req.AuditReason
    }
    
    _, err = dao.XsBigBrotherPasscode.Ctx(ctx).TX(tx).
        Where("id=?", req.Id).Data(data).Update()
    
    return err
})
```

### 大哥房等级与口令数量配置

**硬编码配置**（`app/service/big_brother/config.go`）
```go
// 大哥房等级与口令数量映射
var passcodeLimitMap = map[uint8]uint8{
    0: 0,  // Lv1-Lv7 不开放
    1: 0,
    2: 0,
    3: 0,
    4: 0,
    5: 0,
    6: 0,
    7: 0,
    8: 8,  // Lv8: 8 个
    9: 9,  // Lv9: 9 个
    10: 10, // Lv10: 10 个
    11: 11, // Lv11: 11 个
    12: 12, // Lv12: 12 个
    13: 12, // Lv13+: 12 个（上限）
}

// 获取最大口令数量
func getMaxPasscodeLimit(level uint8) uint8 {
    if limit, ok := passcodeLimitMap[level]; ok {
        return limit
    }
    return 12 // 默认上限
}
```

### API 接口设计（待补充）

- [ ] 创建口令接口
- [ ] 查询口令列表接口
- [ ] 审核接口
- [ ] 返回审核通过口令的接口

## 非功能性需求

### 1. 性能要求

| 指标 | 要求 | 说明 |
|------|------|------|
| 创建口令接口 P99 | < 200ms | 不含文件上传时间 |
| 查询列表接口 P99 | < 100ms | 单页 20 条记录 |
| 审核接口 P99 | < 150ms | - |
| 并发支持 | 1000 QPS | 峰值流量 |

### 2. 安全要求

- **权限校验**：所有接口必须校验登录态和操作权限
- **SQL 注入防护**：使用参数化查询，禁止拼接 SQL
- **XSS 防护**：对输入内容进行转义处理
- **敏感信息**：审核日志记录操作人 ID，不记录明文用户名

### 3. 数据一致性

- **事务保障**：创建、审核操作必须使用数据库事务
- **并发控制**：审核时使用行锁（`FOR UPDATE`）防止并发修改
- **幂等性**：审核接口需支持幂等（重复请求不产生副作用）

### 4. 监控告警

**需要监控的指标**：
- 各接口 QPS、P99 延迟、错误率
- 待审核口令数量（积压告警）
- 审核通过率/拒绝率

**告警阈值**：
- 待审核数量 > 1000：触发告警
- 接口错误率 > 1%：触发告警
- 接口 P99 > 500ms：触发告警

### 5. 日志记录

**业务日志**：
```json
{
  "module": "big_brother_passcode",
  "action": "create|audit|delete",
  "uid": 123,
  "room_id": 456,
  "passcode_id": 789,
  "audit_status": 1,
  "timestamp": 1713254400
}
```

**审核日志**（单独建表或写入操作日志）：
- 操作人 UID
- 操作时间
- 操作 IP
- 审核结果

---

## 需求边界和约束

### 边界定义

**包含在范围内**：
- ✅ 口令的创建、查询、审核、删除
- ✅ 大哥房等级与口令配额管理
- ✅ 后台审核功能
- ✅ 基础权限校验

**不包含在范围内**：
- ❌ 口令在前端的具体展示样式和交互动效
- ❌ 口令内容的二次编辑（需走重新审核流程，后续迭代）
- ❌ 批量审核功能（后续迭代）
- ❌ 口令使用情况统计（后续迭代）

### 技术约束

1. **数据库**：使用 MySQL，表名必须带 `xs_` 前缀
2. **框架**：遵循 slp-go 项目现有的 DAO/Service/Controller 分层架构
3. **配置**：大哥房等级与口令数量配置硬编码在代码中
4. **资源存储**：图片/视频使用公司统一 CDN 服务

### 依赖关系

| 依赖项 | 说明 | 状态 |
|--------|------|------|
| 大哥房基础服务 | 提供房间类型查询、房主信息查询 | 已存在 |
| 用户认证服务 | 提供登录态校验、用户信息查询 | 已存在 |
| 后台管理系统 | 提供审核界面 | 待开发 |
| CDN 服务 | 提供图片/视频存储和分发 | 已存在 |
| 风控服务 | 提供内容风控审核（可选） | 待对接 |

---

## 风险评估

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 审核积压 | 中 | 中 | 设置告警阈值，必要时增加审核人力 |
| 内容违规 | 高 | 低 | 强制人工审核，可接入机审预审 |
| 性能瓶颈 | 低 | 低 | 做好索引优化，必要时加缓存 |
| 配额超发 | 中 | 低 | 事务 + 行锁保障并发安全 |

---

## 验收标准

### 功能验收

- [ ] 房主可以成功创建口令（配额充足时）
- [ ] 房主创建口令被正确限制（配额不足时）
- [ ] 非房主无法创建口令
- [ ] 非大哥房无法创建口令
- [ ] 后台可以审核通过/拒绝口令
- [ ] 用户仅能看到审核通过的口令
- [ ] 房主可以查看自己所有状态的口令
- [ ] 房主可以删除待审核/已拒绝的口令
- [ ] 无法删除已通过审核的口令
- [ ] 房主可以使用口令（空实现，仅验证 + 日志）
- [ ] 未通过审核的口令无法使用
- [ ] 前端正确展示不同状态的标签

### 性能验收

- [ ] 创建接口 P99 < 200ms
- [ ] 查询接口 P99 < 100ms
- [ ] 审核接口 P99 < 150ms
- [ ] 支持 1000 QPS 并发

### 安全验收

- [ ] 所有接口校验登录态
- [ ] 权限校验正确（房主、管理员）
- [ ] 无 SQL 注入风险
- [ ] 输入参数校验完善

---

## 关联项目

- 主项目：大哥房（big-brother）
- 相关项目：slp-room, slp-go
- 相关技能：`multi-pr-feature-analysis-for-development`、`comprehensive-dev-documentation`

## 开发计划

1. **数据库设计** - 创建 `xs_big_brother_passcode` 表
2. **Model/DAO 层** - 基础 CRUD 代码
3. **Service 层** - 业务逻辑（创建、审核、查询、删除）
4. **API 层** - 接口实现
5. **配置管理** - 大哥房等级与口令数量配置
6. **后台审核界面** - 与前端配合开发
7. **测试与部署**

---

*最后更新：2026-04-17*
