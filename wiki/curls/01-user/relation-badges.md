---
id: curl/01-user_relation-badges
label: 用户相关 - relation-badges
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 用户相关]
curl_count: 2
---

# 用户相关 - relation-badges
> 编译自 Postman Collection | 2 条命令

## 命令列表

1. 关系装扮
2. 星舰审核天

## 关系装扮

> Postman 路径: `后台/关系装扮/关系装扮`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Relation/MGetActPretendIds' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "group_ids": [
    10
  ]
}'
```

## 星舰审核天

> Postman 路径: `后台/审核/星舰审核天`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Relation/SaveUserDefendRelation' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "relation_id": 45,
  "defend_uid": 200783701,
  "uid": 200009996,
  "defend_val": 1000,
  "gift_defend_value": 1000,
  "seconds": 172800
}'
```
