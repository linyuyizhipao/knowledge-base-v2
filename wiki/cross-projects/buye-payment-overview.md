---
id: buye-payment-overview
label: 不夜星球支付业务
source: curated/cross-projects/buye-payment/overview.md
business: buye-payment
compiled: 2026-04-25
links: []
---

# 不夜星球支付业务

> 不夜星球小程序支付系统 - 跨项目全景

## 业务流程

| 步骤 | 项目 | 职责 |
|------|------|------|
| 支付创建 | slp-php | pay/create API，判断支付类型，钻石足够则扣钻石 |
| 订单创建 | slp-ee-config | 创建支付订单，写入 xs_pay 表 |
| 支付回调 | slp-ee-config | 更新 xs_pay，发布 NSQ xs.pay |
| 业务执行 | slp-php | PayTask.php 消费 xs.pay，按 type 执行业务 |

## 技术架构

| 层级 | slp-php | slp-ee-config |
|------|----------|---------------|
| Controller | `pay/create` | `pay/PayCommon.php` |
| Task | `cli/tasks/PayTask.php` | - |
| NSQ | 消费 xs.pay | 发布 xs.pay |

## 业务类型路由

| type | 业务逻辑 |
|------|----------|
| packet | 房间打赏 |
| recharge | 充值（增加用户余额/钻石） |
| goods | 商品购买 |
| vip | 贵族购买 |

## 小程序配置

| MINI 名称 | appid | 商户 ID | 状态 |
|-----------|-------|---------|------|
| 一禾联 | wx5348d62e1619c021 | 1647922337 | 使用中 |
| 一禾联不夜星球 | wx54e631663baae480 | 1647922337 | 备用中 |
| 不夜星球 App | wxe99f2a88d571410f | 1647922337 | 备用中 |

## 问题排查

| 问题 | 排查步骤 |
|------|----------|
| 支付成功但未执行业务 | 1. 检查 xs_pay.type 2. 确认 NSQ 发布 3. 检查 PayTask.php 消费 |
| 非充值类型扣费异常 | 1. 检查钻石余额判断 2. 确认 xs_pay 写入 3. 检查订单创建 |