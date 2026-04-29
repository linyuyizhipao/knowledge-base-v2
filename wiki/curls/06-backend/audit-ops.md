---
id: curl/06-backend_audit-ops
label: 后台管理 - audit-ops
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 后台管理]
curl_count: 4
---

# 后台管理 - audit-ops
> 编译自 Postman Collection | 4 条命令

## 命令列表

1. 测试node
2. 启动音设置分组
3. 审核评论回调
4. 审核动态回调

## 测试node

> Postman 路径: `后台/ai人物/测试node`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.audit.api/Test' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "test_type": "all",
  "body": "200251598"
}'
```

## 启动音设置分组

> Postman 路径: `后台/启动音设置分组`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AuditTone' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "id": 1,
  "state": 1,
  "refuse_reason": "随便",
  "op_uid": 100000001
}'
```

## 审核评论回调

> Postman 路径: `后台/审核评论回调`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AuditCallBack' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "choice": "csms_circle_comment",
  "pk_value": "1776243404584000",
  "status": 1,
  "review": 1,
  "uid": 600024783,
  "value": [
    {
      "field": "content",
      "type": "text",
      "value": [
        "互关吗"
      ]
    }
  ],
  "stage": "csmsaudit",
  "extra": {
    "topic_id": "1776243258948000"
  }
}'
```

## 审核动态回调

> Postman 路径: `后台/审核动态回调`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/AuditCallBack' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "choice": "circle_verify_image",
  "pk_value": "1776946311522000",
  "status": 1,
  "review": 1,
  "uid": 600013910,
  "value": [
    {
      "field": "content",
      "type": "text",
      "value": [
        "互关吗"
      ]
    }
  ],
  "stage": "csmsaudit",
  "extra": {
    "topic_id": "1776946311522000"
  }
}'
```
