# SLP 项目数据库命名规范

> 📋 **规范类型**: 数据库设计规范  
> 🎯 **适用范围**: slp-room, slp-go 等 SLP 项目  
> 📁 **知识库**: 业务知识库 (`slp-harness/knowledge`)  
> 📍 **路径**: `patterns/database-naming-conventions.md`  
> 👤 **作者**: @Hugh  
> 📅 **创建时间**: 2026-04-16  

---

## 📌 核心规范

### 时间字段命名

**❌ 错误用法**：
```sql
`created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
`updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

**✅ 正确用法**：
```sql
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
`update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

### 规范说明

| 项目 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| 创建时间 | `create_time` | DATETIME | 记录创建时间，默认 `CURRENT_TIMESTAMP` |
| 更新时间 | `update_time` | DATETIME | 记录更新时间，默认 `ON UPDATE CURRENT_TIMESTAMP` |
| 审核时间 | `audited_at` | DATETIME | 业务时间点，允许 NULL |
| 删除时间 | `delete_time` | DATETIME | 软删除标记，允许 NULL |

---

## 📑 完整命名规范

### 1. 表命名

**规则**：
- 必须带项目前缀（如 `xs_` 表示 xs 项目）
- 使用小写字母和下划线
- 使用复数形式（如果表存储的是多条记录）

**示例**：
```sql
✅ xs_big_brother_passcode      -- 大哥房口令表
✅ xs_chatroom_config           -- 聊天室配置表
✅ xs_chatroom_extend_auction   -- 聊天室拍卖扩展表

❌ BigBrotherPasscode           -- 缺少前缀，驼峰命名
❌ xs_big_brother_passcodes     -- 复数形式（但项目规范是单数）
❌ passcode                     -- 缺少项目前缀
```

### 2. 字段命名

**通用规则**：
- 使用小写字母和下划线（snake_case）
- 禁止使用驼峰命名（camelCase）
- 禁止使用大写字母

**主键**：
```sql
✅ `id` BIGINT(20) UNSIGNED NOT NULL AUTO_INCREMENT
```

**外键**：
```sql
✅ `room_id` BIGINT(20) UNSIGNED NOT NULL    -- 房间 ID
✅ `owner_uid` BIGINT(20) UNSIGNED NOT NULL  -- 用户 ID
✅ `auditor_uid` BIGINT(20) UNSIGNED         -- 审核人 ID
```

**业务字段**：
```sql
✅ `name` VARCHAR(100) NOT NULL           -- 名称
✅ `description` VARCHAR(500)             -- 描述
✅ `image` VARCHAR(255)                   -- 图片 URL/ID
✅ `video` VARCHAR(255)                   -- 视频 URL/ID
✅ `audit_status` TINYINT(4)              -- 审核状态
✅ `audit_reason` VARCHAR(255)            -- 审核原因
```

**时间字段**：
```sql
✅ `create_time` DATETIME                 -- 创建时间
✅ `update_time` DATETIME                 -- 更新时间
✅ `audited_at` DATETIME                  -- 审核时间（业务时间）
✅ `delete_time` DATETIME                 -- 删除时间（软删除）
```

### 3. 索引命名

**规则**：
- 主键：`PRIMARY`
- 普通索引：`idx_字段名`
- 唯一索引：`uniq_字段名`
- 复合索引：`idx_字段 1_字段 2_字段 3`

**示例**：
```sql
✅ PRIMARY KEY (`id`)
✅ KEY `idx_room_id` (`room_id`)
✅ KEY `idx_owner_uid` (`owner_uid`)
✅ KEY `idx_audit_status` (`audit_status`)
✅ KEY `idx_create_time` (`create_time`)
✅ KEY `idx_owner_status_created` (`owner_uid`, `audit_status`, `create_time`)

❌ KEY `idxRoomId` (`room_id`)          -- 驼峰命名
❌ INDEX `room_id_index` (`room_id`)     -- 命名不规范
❌ KEY `idx_created_at` (`created_at`)   -- 使用了错误的字段名
```

### 4. 注释规范

**表注释**：
```sql
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='大哥房口令表';
```

**字段注释**：
```sql
`room_id` BIGINT(20) UNSIGNED NOT NULL COMMENT '大哥房 ID',
`owner_uid` BIGINT(20) UNSIGNED NOT NULL COMMENT '房主用户 ID',
`audit_status` TINYINT(4) NOT NULL DEFAULT 0 COMMENT '审核状态：0-待审核，1-通过，2-拒绝',
```

**索引注释**（MySQL 8.0+）：
```sql
KEY `idx_room_id` (`room_id`) COMMENT '房间 ID 索引',
KEY `idx_owner_uid` (`owner_uid`) COMMENT '房主 ID 索引',
```

---

## 🚨 常见错误

### 错误 1：使用时间字段 `created_at`/`updated_at`

```sql
-- ❌ 错误
CREATE TABLE `xs_example` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- ✅ 正确
CREATE TABLE `xs_example` (
    `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    `create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### 错误 2：缺少项目前缀

```sql
-- ❌ 错误
CREATE TABLE `big_brother_passcode` (...);

-- ✅ 正确
CREATE TABLE `xs_big_brother_passcode` (...);
```

### 错误 3：使用驼峰命名字段

```sql
-- ❌ 错误
CREATE TABLE `xs_example` (
    `roomId` BIGINT,
    `ownerUid` BIGINT,
    `auditStatus` TINYINT
);

-- ✅ 正确
CREATE TABLE `xs_example` (
    `room_id` BIGINT,
    `owner_uid` BIGINT,
    `audit_status` TINYINT
);
```

---

## 🛠️ DAO 代码生成

使用 Go Frame 的 `gf gen dao` 命令时，会自动根据表结构生成对应的 Model 和 DAO 代码。

**命令示例**：
```bash
cd slp-room
gf gen dao -l "mysql:user:pass@tcp(127.0.0.1:3306)/slp_room" -t xs_big_brother_passcode
```

**生成的 Go 结构体字段**：
```go
type XsBigBrotherPasscode struct {
	Id           int64     `json:"id"`           // 口令 ID
	RoomId       int64     `json:"room_id"`      // 大哥房 ID
	OwnerUid     int64     `json:"owner_uid"`    // 房主用户 ID
	AuditStatus  int       `json:"audit_status"` // 审核状态
	CreateTime   time.Time `json:"create_time"`  // 创建时间 ⏰
	UpdateTime   time.Time `json:"update_time"`  // 更新时间 ⏰
}
```

> ⚠️ **注意**：Go Frame 会自动将 `snake_case` 字段转换为 `PascalCase` 的 Go 结构体字段，JSON 标签保持 `snake_case`。

---

## 📚 参考资料

- [Go Frame ORM 规范](https://goframe.org/pages/viewpage.action?pageId=1114307)
- [SLP 房间类型开发模板](room-type-development-template)
- [MySQL 命名最佳实践](https://dev.mysql.com/doc/refman/8.0/en/identifiers.html)

---

## 📝 变更记录

| 日期 | 变更内容 | 作者 |
|------|---------|------|
| 2026-04-16 | 初始版本，明确时间字段使用 `create_time`/`update_time` | @Hugh |

---

*最后更新：2026-04-16*
