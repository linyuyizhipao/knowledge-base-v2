---
id: curl/06-backend_shop-bag
label: 后台管理 - shop-bag
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 后台管理]
curl_count: 10
---

# 后台管理 - shop-bag
> 编译自 Postman Collection | 10 条命令

## 命令列表

1. 积分商店的定制列表
2. 积分续期自定义装扮
3. 添加礼包
4. 新增礼包
5. 修改礼包
6. 礼包加商品
7. 购买明细列表
8. 金币购买
9. 获取家族金币商城的主页信息
10. 获取首页的tabs

## 积分商店的定制列表

> Postman 路径: `user/积分商店的定制列表`

```bash
curl -X POST '{{hostname}}/go/slp/shop/getUserCustomList' \
  -H 'user-token: {{user-token}}'
```

## 积分续期自定义装扮

> Postman 路径: `user/积分续期自定义装扮`

```bash
curl -X POST '{{hostname}}/go/slp/shop/customRenewal' \
  -H 'user-token: {{user-token}}'
```

## 添加礼包

> Postman 路径: `后台/添加礼包`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AddShopBag' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "b_type": 1,
  "name": "特使礼包1",
  "b_desc": "礼包描述测试1",
  "image": "static/shop/v2/bg/commodity_bg_2.png",
  "image_bg": "static/shop/v2/bg/commodity_bg_5.png",
  "price": 12000,
  "user_pay_num": 19,
  "stock_num": 100,
  "b_tag": "哈哈哈"
}'
```

## 新增礼包

> Postman 路径: `后台/新增礼包`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AddShopBag' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "b_type": 1,
  "name": "hugh-test礼包",
  "b_desc": "这是一个装testde",
  "b_tag": "限时特够",
  "image": "static/shop/v2/bg/commodity_bg_2.png",
  "image_bg": "static/shop/v2/bg/commodity_bg_3.png",
  "price": 1111,
  "user_pay_num": 2,
  "stock_num": 100
}'
```

## 修改礼包

> Postman 路径: `后台/修改礼包`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AddShopBag' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "b_type": 1,
  "name": "hugh-test礼包",
  "b_desc": "这是一个装testde",
  "b_tag": "限时特够",
  "image": "static/shop/v2/bg/commodity_bg_2.png",
  "image_bg": "static/shop/v2/bg/commodity_bg_3.png",
  "price": 1111,
  "user_pay_num": 2,
  "stock_num": 100
}'
```

## 礼包加商品

> Postman 路径: `后台/礼包加商品`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AddShopBag' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "b_type": 1,
  "name": "hugh-test礼包",
  "b_desc": "这是一个装testde",
  "b_tag": "限时特够",
  "image": "static/shop/v2/bg/commodity_bg_2.png",
  "image_bg": "static/shop/v2/bg/commodity_bg_3.png",
  "price": 1111,
  "user_pay_num": 2,
  "stock_num": 100
}'
```

## 购买明细列表

> Postman 路径: `家族金币商城/购买明细列表`

```bash
curl -X POST '{{hostname}}/go/slp/shop/getFamilyGoldRecord?package=com.yhl.sleepless.android&req_uid=200253499&tab=heartbeat' \
  -H 'user-token: {{user-token}}'
```

## 金币购买

> Postman 路径: `家族金币商城/金币购买`

```bash
curl -X POST '{{hostname}}/go/slp/shop/familyPay' \
  -H 'user-token: {{user-token}}'
```

## 获取家族金币商城的主页信息

> Postman 路径: `家族金币商城/获取家族金币商城的主页信息`

```bash
curl -X POST '{{hostname}}/go/slp/shop/getFamilyGoldShop' \
  -H 'user-token: {{user-token}}'
```

## 获取首页的tabs

> Postman 路径: `装扮/装扮使用发放/获取首页的tabs`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/GetIndexTabs' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{}'
```
