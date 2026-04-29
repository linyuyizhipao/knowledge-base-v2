---
id: curl/04-pretend_fragment
label: 装扮系统 - fragment
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 装扮系统]
curl_count: 7
---

# 装扮系统 - fragment
> 编译自 Postman Collection | 7 条命令

## 命令列表

1. user_auth
2. 设置用户歌手标签
3. 加碎片
4. 批量加碎片
5. 批量减碎片
6. 批量查白名单的rpc
7. 减碎片

## user_auth

> Postman 路径: `user/user_auth`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/AddFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000022,
  "fragment_num": 10000,
  "source": "activity"
}'
```

## 设置用户歌手标签

> Postman 路径: `user/设置用户歌手标签`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/AddFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000022,
  "fragment_num": 10000,
  "source": "activity"
}'
```

## 加碎片

> Postman 路径: `装扮/加碎片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/AddFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000022,
  "fragment_num": 10000,
  "source": "activity"
}'
```

## 批量加碎片

> Postman 路径: `装扮/批量加碎片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/AddFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200254645,
  "fragment_num": 11111110,
  "source": "activity"
}'
```

## 批量减碎片

> Postman 路径: `装扮/批量减碎片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/BatchSubFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "list": [
    {
      "uid": 200000003,
      "fragment_num": 18350,
      "source": "activity"
    },
    {
      "uid": 200000024,
      "fragment_num": 100,
      "source": "activity"
    }
  ]
}'
```

## 批量查白名单的rpc

> Postman 路径: `装扮/批量查白名单的rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/SubFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000003,
  "fragment_num": 10,
  "source": "activity"
}'
```

## 减碎片

> Postman 路径: `装扮/减碎片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.pretend/SubFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200000003,
  "fragment_num": 10,
  "source": "activity"
}'
```
