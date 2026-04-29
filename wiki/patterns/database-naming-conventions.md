---
id: patterns/database-naming-conventions
label: database-naming-conventions
source: curated/patterns/database-naming-conventions.md
role: 规范
compiled: 2026-04-28
source_hash: b3b9236cc5379d9b4b243b2fb73a2a17
---

> SLP 项目数据库命名规范

## 核心规范

### 时间字段

```sql
-- ✅ 正确：create_time / update_time
`create_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
`update_time` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP

-- ❌ 错误：created_at / updated_at
```

### 表命名

- 必须带项目前缀（如 `xs_`）
- 小写字母 + 下划线

```sql
✅ xs_big_brother_passcode    ❌ BigBrotherPasscode / passcode
```

### 字段命名

- snake_case，禁止驼峰
- 主键：`id` BIGINT UNSIGNED AUTO_INCREMENT
- 外键：`room_id`, `owner_uid`
- 索引：`idx_字段名`, `uniq_字段名`, 复合：`idx_字段1_字段2`

## DAO 代码生成

```bash
cd slp-room
gf gen dao -l "mysql:user:pass@tcp(127.0.0.1:3306)/slp_room" -t xs_big_brother_passcode
```

Go Frame 自动将 `snake_case` 转 `PascalCase` 结构体字段，JSON 标签保持 `snake_case`。
