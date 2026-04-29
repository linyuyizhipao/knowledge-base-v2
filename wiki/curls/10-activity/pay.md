---
id: curl/10-activity_pay
label: 活动与支付 - pay
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 活动与支付]
curl_count: 4
---

# 活动与支付 - pay
> 编译自 Postman Collection | 4 条命令

## 命令列表

1. 充值
2. 充值订单
3. 充值订单-parse-token
4. 充值订单-token

## 充值

> Postman 路径: `user/充值`

```bash
curl -X POST '{{hostname}}/go/slp/test/recharge' \
  -H 'user-token: {{user-token}}'
```

## 充值订单

> Postman 路径: `user/充值订单`

```bash
curl -X POST '{{hostname}}/pay/create' \
  -H 'user-token: {{user-token}}'
```

## 充值订单-parse-token

> Postman 路径: `user/充值订单-parse-token`

```bash
curl -X POST '{{hostname}}/pay/verifyHarmonyPurchaseToken' \
  -H 'user-token: {{user-token}}'
```

## 充值订单-token

> Postman 路径: `user/充值订单-token`

```bash
curl -X POST '{{hostname}}/pay/verifyHarmonyIap' \
  -H 'user-token: {{user-token}}'
```
