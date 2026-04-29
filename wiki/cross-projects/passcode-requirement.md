---
id: passcode-requirement
label: 大哥房口令功能需求
source: curated/cross-projects/big-brother/passcode-requirement.md
business: big-brother
compiled: 2026-04-25
links:
  - passcode-technical-design
  - passcode-summary
---

# 大哥房口令功能需求

> 大哥房房主创建和管理"口令"资源，经后台审核后展示

## 核心概念

| 概念 | 说明 |
|------|------|
| 口令 | 房主创建的个性化资源（名称、描述、图片、视频） |
| 创建者 | 仅限大哥房房主 |
| 审核机制 | 所有口令必须经过后台审核才能展示 |

## 配额规则

| 大哥房等级 | 口令配额 |
|------------|----------|
| Lv1 - Lv7 | 0（不开放） |
| Lv8 | 8 |
| Lv9 - Lv12 | 9-12 |
| Lv13+ | 12（封顶） |

## 审核状态

| 状态值 | 状态名 |
|--------|--------|
| 0 | 待审核 |
| 1 | 审核通过 |
| 2 | 审核拒绝 |

## API 接口

| 接口 | 路由 | 说明 |
|------|------|------|
| create | `/go/slp/big-brother/passcode/create` | 创建口令 |
| list | `/go/slp/big-brother/passcode/list` | 查询口令列表 |
| audit | `/go/slp/big-brother/passcode/audit` | 审核口令 |
| delete | `/go/slp/big-brother/passcode/delete` | 删除口令 |
| quota | `/go/slp/big-brother/passcode/quota` | 查询配额 |
| use | `/go/slp/big-brother/passcode/use` | 使用口令 |

## 权限矩阵

| 操作 | 房主 | 普通用户 | 管理员 |
|------|------|----------|--------|
| 创建口令 | ✅ | ❌ | ❌ |
| 查全状态 | ✅ | ❌ | ✅ |
| 查已通过 | ✅ | ✅ | ✅ |
| 审核口令 | ❌ | ❌ | ✅ |
| 删除待审核 | ✅ | ❌ | ✅ |
| 删除已通过 | ❌ | ❌ | ❌ |

## 错误码

| 错误码 | 说明 |
|--------|------|
| 10001 | 口令数量已达上限 |
| 10002 | 口令不存在 |
| 10003 | 无权限操作 |
| 10004 | 审核失败 |
| 10005 | 口令已审核 |
| 10006 | 无效的审核状态 |
| 10007 | 房间不是大哥房 |
| 10008 | 无法删除已通过审核的口令 |

## 数据表

```sql
CREATE TABLE xs_big_brother_passcode (
    id BIGINT UNSIGNED AUTO_INCREMENT,
    room_id BIGINT UNSIGNED NOT NULL,
    owner_uid BIGINT UNSIGNED NOT NULL,
    name VARCHAR(100) NOT NULL,
    image VARCHAR(512),
    video VARCHAR(512),
    audit_status TINYINT DEFAULT 0,
    audit_reason VARCHAR(255),
    auditor_uid BIGINT UNSIGNED,
    audited_at DATETIME,
    create_time DATETIME,
    update_time DATETIME,
    PRIMARY KEY (id),
    KEY idx_room_id (room_id),
    KEY idx_owner_uid (owner_uid),
    KEY idx_audit_status (audit_status)
);
```