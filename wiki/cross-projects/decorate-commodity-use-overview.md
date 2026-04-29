---
id: decorate-commodity-use-overview
label: 装扮类物品使用转发
source: curated/cross-projects/decorate-commodity-use/overview.md
business: decorate-commodity-use
compiled: 2026-04-25
links:
  - decorate-commodity-use-slp-php
  - decorate-commodity-use-slp-go
---

# 装扮类物品使用转发

> 装扮类物品（头像框、气泡、座驾等）使用时，PHP 扣库存后转发到 slp-go 处理有效期累加

## 判断条件

| 条件 | 说明 |
|------|------|
| `isDecoType($type)` | 装扮类型：header/mounts/bubble/effect/decorate/ring 等 |
| `extra.pretend_id > 0` | 物品关联到新装扮系统的装扮 ID |

## 业务流程

```
PHP UserCommodity::use() → 判断装扮类型 + pretend_id → 扣库存 → 计算 seconds → RPC UseDecorateCommodity → slp-go 添加有效期 + 自动佩戴
```

## 技术架构

| 层级 | slp-php | slp-go |
|------|----------|--------|
| Service | `UserCommodity::use()` | `Pretend::UseDecorateCommodity()` |
| RPC Client | `RpcPretend::UseDecorateCommodity()` | `rpc/server/internal/pretend/` |

## RPC 接口

```json
// Request
{
  "uid": 用户ID,
  "pretend_id": 装扮ID,
  "seconds": 有效期秒数
}

// Response
{
  "success": true,
  "msg": ""
}
```

## 有效期计算

```php
$seconds = ($period * 24 * 3600 + $period_hour * 3600) * $use_num;
```

## 装扮类型列表

| 类型 | 说明 |
|------|------|
| header | 头像框 |
| mounts | 座驾 |
| effect | 入场特效 |
| decorate | 主页装扮 |
| bubble | 聊天气泡 |
| ring | 麦上光圈 |
| union_header | 公会头像框 |
| bubble_tail | 聊天气泡尾灯 |
| card_decorate | 资料卡装扮 |
| circle_background | 动态背景 |

## 数据表

| 表 | 项目 | 说明 |
|----|------|------|
| xs_user_commodity | slp-php | 用户背包库存 |
| xs_pay_change | slp-php | 消费记录 |
| xs_user_pretend_list | slp-go | 用户装扮拥有记录 |
| bbc_pretend_info | slp-go | 装扮信息表（内存） |