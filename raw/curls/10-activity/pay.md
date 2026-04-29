# 充值支付

> Pay, recharge, harmony IAP

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
