---
id: curl_README
label: Curl 命令库总览
source: curated/curls/README.md
role: curl
compiled: 2026-04-28
tags: [curl, 索引]
---

# Curl 命令库总览


> Postman 导出的 curl 命令，按功能分类。测试环境: 114.55.3.96
> 共 **27** 个文件，**188** 条命令

## 目录

### 01-user/ - 用户相关

- [用户档案与成长](01-user/profile-growth.md) (10 条)
- [用户关系与徽章](01-user/relation-badges.md) (2 条)
- [贵族与头衔](01-user/title-noble.md) (2 条)

### 02-room/ - 房间相关

- [口令功能](02-room/passcode.md) (7 条)
- [宠物功能](02-room/pet.md) (3 条)
- [房间红包](02-room/redpacket.md) (4 条)
- [房间热度与标签](02-room/room-hot-tag.md) (10 条)

### 03-farm/ - 农场/星舰

- [农场 HTTP](03-farm/farm-http.md) (16 条)
- [农场 RPC](03-farm/farm-rpc.md) (15 条)
- [星舰信息](03-farm/starship-info.md) (1 条)

### 04-pretend/ - 装扮系统

- [碎片管理](04-pretend/fragment.md) (7 条)
- [装扮发放与删除](04-pretend/send-drop.md) (14 条)

### 05-ai/ - AI 人物

- [AI 人物卡片](05-ai/ai-card.md) (18 条)

### 06-backend/ - 后台管理

- [审核操作](06-backend/audit-ops.md) (4 条)
- [动态/PK/任务](06-backend/circle-pk-task.md) (7 条)
- [礼包与商城](06-backend/shop-bag.md) (10 条)
- [用户后台操作](06-backend/user-ops.md) (11 条)

### 07-test/ - 测试端点

- [房间测试端点](07-test/room-test.md) (7 条)
- [SLP 测试端点](07-test/slp-test.md) (13 条)
- [星舰测试端点](07-test/starship-test.md) (4 条)

### 08-data-query/ - 数据查询

- [ES 与数据修复](08-data-query/es-fix.md) (8 条)
- [SQL 查询](08-data-query/sql-select.md) (4 条)

### 09-cache-consume/ - 缓存与消费

- [缓存操作](09-cache-consume/cache-ops.md) (7 条)
- [消费发放](09-cache-consume/consume.md) (2 条)

### 10-activity/ - 活动与支付

- [活动与发奖](10-activity/activity-reward.md) (1 条)
- [外部审核](10-activity/audit-external.md) (1 条)
- [充值支付](10-activity/pay.md) (4 条)

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{rpc-hostname}}` | RPC 服务地址 | `http://114.55.3.96:8080` |
| `{{hostname}}` | HTTP 服务地址 | `https://114.55.3.96` |
| `{{token}}` | 用户认证 Token | 登录后获取 |

## RPC vs HTTP 头部

**RPC (`/rpc/...`)**:
- `X-RPCX-SerializeType: 1`
- `Content-type: application/rpcx`

**HTTP (`/go/...`)**:
- `Content-Type: application/json`
- `user-token: <token>` (需认证)