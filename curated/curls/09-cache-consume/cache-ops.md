# 缓存操作

> Common.Cache ops

## 命令列表

1. 更新cache的rpc缓存
2. 查看缓存-table
3. 查询兑换商品信息
4. 兑换商品删除
5. rpc获取主页房间数据
6. codec
7. 送贵族订阅时间 Copy

## 更新cache的rpc缓存

> Postman 路径: `广场创作/更新cache的rpc缓存`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/RefreshTable' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "tables": [
    "bbc_square_shop_pretend",
    "bbc_room_index_position"
  ]
}'
```

## 查看缓存-table

> Postman 路径: `广场创作/查看缓存-table`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/MGetData' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "table": "bbc_square_shop_pretend",
  "ids": [
    313
  ]
}'
```

## 查询兑换商品信息

> Postman 路径: `广场创作/查询兑换商品信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/RefreshTable' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "tables": [
    "bbc_square_shop_pretend",
    "bbc_room_index_position"
  ]
}'
```

## 兑换商品删除

> Postman 路径: `广场创作/兑换商品删除`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/SaveSquareShopAdmin' \
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

## rpc获取主页房间数据

> Postman 路径: `装扮/装扮使用发放/rpc获取主页房间数据`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/GetIndexSixRooms' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "first_id": 1,
  "sub_type": "game-guess"
}'
```

## codec

> Postman 路径: `装扮/codec`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Common.Cache/CodecMGetV2' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "table_name": "bbc_belong_user",
  "ids": [
    10000
  ]
}'
```

## 送贵族订阅时间 Copy

> Postman 路径: `贵族/送贵族订阅时间 Copy`

```bash
curl -X POST '{{rpc-hostname}}/rpc/common.cache/CodecMGet' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "table_name": "bbc_badge",
  "ids": [
    1
  ]
}'
```
