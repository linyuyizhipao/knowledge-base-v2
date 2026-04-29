---
id: curl/09-cache-consume_consume
label: 缓存与消费 - consume
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 缓存与消费]
curl_count: 2
---

# 缓存与消费 - consume
> 编译自 Postman Collection | 2 条命令

## 命令列表

1. 发放卡片
2. 发放碎片

## 发放卡片

> Postman 路径: `后台/ai人物/发放卡片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Consume.Money/SlpCommonConsume' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "request_id": 30000,
  "uid": 200000025,
  "consume_type": 19,
  "want_data": [
    {
      "pid": 1,
      "op": "add",
      "num": 1,
      "to_uid": 200000025,
      "log_reason": "发放",
      "p_type": "ai_character_cards"
    }
  ]
}'
```

## 发放碎片

> Postman 路径: `后台/ai人物/发放碎片`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Consume.Money/SlpCommonConsume' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "request_id": 30001,
  "uid": 200000025,
  "consume_type": 19,
  "want_data": [
    {
      "pid": 5,
      "op": "add",
      "num": 1000,
      "to_uid": 200000025,
      "extra": "{\"reason\":\"sasad\",\"seconds\":100}",
      "log_reason": "发放",
      "p_type": "user_statics_score"
    }
  ]
}'
```
