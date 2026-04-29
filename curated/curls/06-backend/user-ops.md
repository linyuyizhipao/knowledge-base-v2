# 用户后台操作

> Backend user ops, dispatch, growth

## 命令列表

1. 后台加创作分
2. 批量添加兑换商品
3. 忽略退点亮积分
4. 后台查用户各维度数据
5. 审核启动音
6. 派单插入用户标签
7. 派单查用户信息
8. 派单查用户信息删除
9. 成长值修改
10. 成长值修改 Copy
11. reset 用户基本信息

## 后台加创作分

> Postman 路径: `广场创作/后台加创作分`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/RefreshTable' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "tables": [
    "bbc_square_shop_pretend",
    "bbc_room_index_position"
  ]
}'
```

## 批量添加兑换商品

> Postman 路径: `广场创作/批量添加兑换商品`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/SaveSquareShopAdmin' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "data": [
    {
      "pretend_id": 1,
      "create_score": 100,
      "on_state": 1,
      "sort": 1
    }
  ]
}'
```

## 忽略退点亮积分

> Postman 路径: `user/忽略退点亮积分`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/RefundLightScore' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "id": 354
}'
```

## 后台查用户各维度数据

> Postman 路径: `后台/审核/后台查用户各维度数据`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/MgetUsers' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "u_type": 3,
  "val": [
    "100001"
  ]
}'
```

## 审核启动音

> Postman 路径: `后台/审核启动音`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/BatchSaveXsUserSendOrder' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "data": [
    {
      "id": 9,
      "label_ids": ""
    }
  ]
}'
```

## 派单插入用户标签

> Postman 路径: `后台/派单插入用户标签`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/BatchSaveXsUserSendOrder' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "data": [
    {
      "id": 85,
      "uid": 200000009,
      "boss_uid": 200000003,
      "rid": 100000255
    }
  ]
}'
```

## 派单查用户信息

> Postman 路径: `后台/派单查用户信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/MGetOrderUser' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": [
    200000173,
    200000099
  ]
}'
```

## 派单查用户信息删除

> Postman 路径: `后台/派单查用户信息删除`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/DelXsDispatchUser' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "ids": [
    1
  ]
}'
```

## 成长值修改

> Postman 路径: `后台/成长值修改`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/BatchSaveUserGrowth' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "user_growth": [
    {
      "uid": 200246873,
      "growth_val": 10000,
      "effective_value": 0
    }
  ]
}'
```

## 成长值修改 Copy

> Postman 路径: `后台/成长值修改 Copy`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/SaveXsstChatroomAdminOpTimeLog' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "param": [
    {
      "rid": 100504447,
      "create_time": 1744604681
    }
  ]
}'
```

## reset 用户基本信息

> Postman 路径: `后台/reset 用户基本信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/ResetUserBaseInfo' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "choice": "xs_user_photos",
  "id": [
    64
  ]
}'
```
