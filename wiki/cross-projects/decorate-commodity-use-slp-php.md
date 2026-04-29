---
id: decorate-commodity-use-slp-php
label: 装扮类物品使用转发 - slp-php 视角
source: curated/cross-projects/decorate-commodity-use/slp-php.md
business: decorate-commodity-use
compiled: 2026-04-25
links:
  - decorate-commodity-use-overview
---

# 装扮类物品使用转发 - slp-php 视角

> PHP 侧负责扣库存 + 消费记录，然后转发到 slp-go

## 核心职责

| 职责 | 说明 |
|------|------|
| 判断是否转发 | 检查物品类型 + pretend_id |
| 扣减背包库存 | 使用锁 + 事务保证一致性 |
| 计算有效期秒数 | period + period_hour |
| 转发 RPC | 调用 slp-go 的 UseDecorateCommodity |

## 核心代码位置

| 文件 | 说明 |
|------|------|
| `app/service/mate/UserCommodity.php` | 物品使用入口 |
| `app/service/rpc/RpcPretend.php` | RPC 客户端 |
| `app/models/mate/CommodityModel.php` | 装扮类型定义 |

## 扣库存流程

```
获取锁 → 检查数量 → 扣减背包 → 消费记录 → 释放锁
```

**锁 Key**: `Pay.{uid}`

## RPC Server

```php
public const RpcServerName = "rpc.pretend";
```

## 测试场景

| 场景 | 预期结果 |
|------|----------|
| pretend_id > 0 | 扣库存 + 转发成功 |
| pretend_id = 0 | 走原有 PHP 逻辑 |
| 库存不足 | 返回错误信息 |
| RPC 失败 | 错误信息透传 |