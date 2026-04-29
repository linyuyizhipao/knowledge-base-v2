---
id: curl/06-backend_circle-pk-task
label: 后台管理 - circle-pk-task
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 后台管理]
curl_count: 7
---

# 后台管理 - circle-pk-task
> 编译自 Postman Collection | 7 条命令

## 命令列表

1. 获取pk黑名单
2. 激励任务修改
3. 批量获取房间状态
4. pk黑名单
5. 添加置顶动态
6. 删除置顶动态
7. 动态评论

## 获取pk黑名单

> Postman 路径: `后台/ai人物/获取pk黑名单`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Backend.PKRule/GetPkBlack' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "rid": [
    100104419
  ],
  "from_uid": 200252459
}'
```

## 激励任务修改

> Postman 路径: `后台/激励任务修改`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Backend.Service/SaveSquareTask' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "task_id": 1,
  "task_name": "任务名"
}'
```

## 批量获取房间状态

> Postman 路径: `后台/批量获取房间状态`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Backend.Service/SaveSquareTask' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "task_id": 1,
  "task_name": "任务名"
}'
```

## pk黑名单

> Postman 路径: `后台/pk黑名单`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Backend.PKRule/GetPkBlack' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "from_uid": 200251598,
  "rid": [
    100104316,
    100104360
  ]
}'
```

## 添加置顶动态

> Postman 路径: `后台/添加置顶动态`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/SaveTopCircle' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "begin_time": 1751299200,
  "end_time": 1751385602,
  "tpid": 1688365815130000,
  "id": 3
}'
```

## 删除置顶动态

> Postman 路径: `后台/删除置顶动态`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Backend.Service/DelTopCircle' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "id": [
    2,
    4
  ]
}'
```

## 动态评论

> Postman 路径: `starship/动态评论`

```bash
curl -X POST '{{rpc-hostname}}/rpc/rpc.circle.move/MgetComment' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200000003,
  "cmt_filter": [
    {
      "tpid": 1688366179308000,
      "cmtid": 0
    }
  ]
}'
```
