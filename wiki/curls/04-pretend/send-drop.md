---
id: curl/04-pretend_send-drop
label: 装扮系统 - send-drop
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 装扮系统]
curl_count: 14
---

# 装扮系统 - send-drop
> 编译自 Postman Collection | 14 条命令

## 命令列表

1. 装扮系列随机
2. 取消装扮穿戴
3. rpc-批量发送用户装扮TX
4. rpc-申请requestid
5. 客户端本地img图片更新
6. cid发放装扮
7. 批量送装扮
8. 批量送装扮_v2
9. 批量多人多装扮赠送_tx
10. 送装扮_v2
11. 删装扮
12. 批量删装扮
13. 带装扮
14. 根据装扮id获取信息

## 装扮系列随机

> Postman 路径: `装扮/装扮使用发放/装扮系列随机`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/RandomChange' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "category": 3,
  "uid": 200000173
}'
```

## 取消装扮穿戴

> Postman 路径: `装扮/装扮使用发放/取消装扮穿戴`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/Cancel' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "pretend_cate_id": 3,
  "uid": 200000173,
  "group_id": 5
}'
```

## rpc-批量发送用户装扮TX

> Postman 路径: `装扮/装扮使用发放/rpc-批量发送用户装扮TX`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/MultiSendPretendsTx' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "first_id": 1,
  "sub_type": "game-guess"
}'
```

## rpc-申请requestid

> Postman 路径: `装扮/装扮使用发放/rpc-申请requestid`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/MultiSendPretendsTx' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "first_id": 1,
  "sub_type": "game-guess"
}'
```

## 客户端本地img图片更新

> URL 为空，请从 Postman 手动复制。

## cid发放装扮

> Postman 路径: `装扮/cid发放装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/UseDecorateCommodity' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200251598,
  "pretend_id": 329,
  "cid": 27846,
  "scene": "背包",
  "seconds": 86400
}'
```

## 批量送装扮

> Postman 路径: `装扮/批量送装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/BatchBackendSendGroupPretend' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "list": [
    {
      "uid": 200253529,
      "pretend_cate_id": 3,
      "group_id": 32,
      "star_num": 3,
      "seconds": 200000,
      "got_type": "fg",
      "is_perpetual": false
    }
  ]
}'
```

## 批量送装扮_v2

> Postman 路径: `装扮/批量送装扮_v2`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/MultiSendPretends' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "send_list": [
    {
      "uid": 200250785,
      "seconds": 200000,
      "got_type": "activity",
      "is_perpetual": false,
      "num": 1,
      "pretend_id": 2198,
      "is_notice": true
    }
  ]
}'
```

## 批量多人多装扮赠送_tx

> Postman 路径: `装扮/批量多人多装扮赠送_tx`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/MultiSendPretendsTx' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "send_list": [
    {
      "uid": 200254645,
      "num": 1,
      "pretend_id": 139,
      "period_end": 1757139310,
      "is_notice": true
    }
  ]
}'
```

## 送装扮_v2

> Postman 路径: `装扮/送装扮_v2`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/SendPretend' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200254645,
  "pretend_cate_id": 1,
  "group_id": 32,
  "star_num": 1,
  "seconds": 200000,
  "got_type": "fh"
}'
```

## 删装扮

> Postman 路径: `装扮/删装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/DropUserGroupPretend' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000003,
  "pretend_cate_id": 1,
  "group_id": 49,
  "source": "activity"
}'
```

## 批量删装扮

> Postman 路径: `装扮/批量删装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/BatchDropUserGroupPretend' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "list": [
    {
      "uid": 200000003,
      "pretend_cate_id": 1,
      "group_id": 32,
      "source": "fg",
      "star_num": 1,
      "id": 1
    }
  ]
}'
```

## 带装扮

> Postman 路径: `装扮/带装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/Use' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000024,
  "pretend_cate_id": 3,
  "group_id": 5,
  "star_num": 1,
  "sex": 1
}'
```

## 根据装扮id获取信息

> Postman 路径: `装扮/根据装扮id获取信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/MGetPretends' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000003,
  "pretend_cate_id": 1,
  "group_id": 2,
  "source": "fg"
}'
```
