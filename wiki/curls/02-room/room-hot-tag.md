---
id: curl/02-room_room-hot-tag
label: 房间相关 - room-hot-tag
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 房间相关]
curl_count: 10
---

# 房间相关 - room-hot-tag
> 编译自 Postman Collection | 10 条命令

## 命令列表

1. 获取用户roomtag
2. 获取用户roomtag set
3. 房间减热度
4. 加房间热度
5. 创建商业房的权限
6. https://192.168.1.3/go/slp/gift/panel?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100000260&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=pb
7. getRoomFrameList
8. getRoomFrameList Copy
9. 单个房间热度
10. 批量房间热度

## 获取用户roomtag

> Postman 路径: `user/获取用户roomtag`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Tag/RoomTagGet' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200260243
}'
```

## 获取用户roomtag set

> Postman 路径: `user/获取用户roomtag set`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Tag/RoomTagSet' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200259777,
  "tags": {
    "22": {
      "val": "信息流回流"
    }
  }
}'
```

## 房间减热度

> Postman 路径: `user/房间减热度`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Hot/ReduceHot' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "rid": 100104339,
  "hot": 4,
  "scene": "backend"
}'
```

## 加房间热度

> Postman 路径: `user/加房间热度`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Hot/Add' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "rid": 100104339,
  "hot": 10,
  "effect_hour": 1,
  "admin": 100000001,
  "start_time": 1765880938,
  "effect_time": 111,
  "uid": 200000251
}'
```

## 创建商业房的权限

> Postman 路径: `后台/创建商业房的权限`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Busi/CreateBusiness' \
  -H 'X-RPCX-MessageID: 10000' \
  -H 'X-RPCX-MesssageType: 0' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'X-RPCX-ServicePath: Room.Busi' \
  -H 'X-RPCX-ServiceMethod: CreateBusiness' \
  -H 'Content-Type: application/json' \
  -d '{
  "uid": 600010541,
  "property": "business",
  "factoryType": "business-music",
  "settleChannel": "music",
  "appId": 70,
  "name": "拉拉队2",
  "is_backend": true,
  "is_create": true,
  "sex": 2
}'
```

## https://192.168.1.3/go/slp/gift/panel?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100000260&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=pb

> Postman 路径: `房间角标/https://192.168.1.3/go/slp/gift/panel?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100000260&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=pb`

```bash
curl -X GET 'https://192.168.1.3/go/room/room/getRoomSetInfo?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100100925&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=json&_sign=bece63122664f1e6142b15467dc8ea04&_dk=de12fe6247d8d81893f4c9578eb3bbf6' \
  -H 'user-agent: Mozilla/5.0 (Linux; Android 10; TEL-AN10 Build/HONORTEL-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.105 Mobile Safari/537.36 / Xs android V5.15.0.0 / Js V1.0.0.0 / Login V1710412994' \
  -H 'user-brand: HONOR' \
  -H 'user-model: TEL-AN10' \
  -H 'user-tag: 1615af1a34174394' \
  -H 'user-idfa: ' \
  -H 'user-mac: 1615af1a34174394' \
  -H 'user-channel: slp' \
  -H 'user-oaid: 8d09ccc6-ad83-4e57-b7aa-4e06b7fcb06b' \
  -H 'user-issimulator: false' \
  -H 'user-machine: TEL-AN10' \
  -H 'user-did: DU1jCqoZWPvBV2Dp-XCJUnmy0Kssfh62jXc7' \
  -H 'user-isroot: false' \
  -H 'host: 192.168.1.3' \
  -H 'user-token: bdacVaKPNbmgr3QaaGlrKuoiqIZ6eMAfcUGwq2utjPNk1__2FschhWpm6YQ2hQhcNGpiIdf49GdbQctrjd__2BK__2BEZkl__2BkFlwEe7Vg5ftd7B__2B51O5ML2UPUuVD4qti0w' \
  -H 'user-imei: 1615af1a34174394' \
  -H 'user-language: zh_CN'
```

## getRoomFrameList

> Postman 路径: `房间角标/getRoomFrameList`

```bash
curl -X GET 'https://116.62.125.230/go/room/roomGiftSuit/getRoomFrameList?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100000260&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=json&_sign=bece63122664f1e6142b15467dc8ea04&_dk=de12fe6247d8d81893f4c9578eb3bbf6' \
  -H 'user-agent: Mozilla/5.0 (Linux; Android 10; TEL-AN10 Build/HONORTEL-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.105 Mobile Safari/537.36 / Xs android V5.15.0.0 / Js V1.0.0.0 / Login V1710412994' \
  -H 'user-brand: HONOR' \
  -H 'user-model: TEL-AN10' \
  -H 'user-tag: 1615af1a34174394' \
  -H 'user-idfa: ' \
  -H 'user-mac: 1615af1a34174394' \
  -H 'user-channel: slp' \
  -H 'user-oaid: 8d09ccc6-ad83-4e57-b7aa-4e06b7fcb06b' \
  -H 'user-issimulator: false' \
  -H 'user-machine: TEL-AN10' \
  -H 'user-did: DU1jCqoZWPvBV2Dp-XCJUnmy0Kssfh62jXc7' \
  -H 'user-isroot: false' \
  -H 'host: 192.168.1.3' \
  -H 'user-token: bdacVaKPNbmgr3QaaGlrKuoiqIZ6eMAfcUGwq2utjPNk1__2FschhWpm6YQ2hQhcNGpiIdf49GdbQctrjd__2BK__2BEZkl__2BkFlwEe7Vg5ftd7B__2B51O5ML2UPUuVD4qti0w' \
  -H 'user-imei: 1615af1a34174394' \
  -H 'user-language: zh_CN'
```

## getRoomFrameList Copy

> Postman 路径: `房间角标/getRoomFrameList Copy`

```bash
curl -X GET 'https://116.62.125.230/go/room/roomGiftSuit/getRoomFrameList?version=20&type=room&support_coin_use=0&act_version=2&unity_rocket_version=1&rid=100000260&tower=0&package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=2635&_model=TEL-AN10&_timestamp=1711760152&format=json&_sign=bece63122664f1e6142b15467dc8ea04&_dk=de12fe6247d8d81893f4c9578eb3bbf6' \
  -H 'user-agent: Mozilla/5.0 (Linux; Android 10; TEL-AN10 Build/HONORTEL-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/92.0.4515.105 Mobile Safari/537.36 / Xs android V5.15.0.0 / Js V1.0.0.0 / Login V1710412994' \
  -H 'user-brand: HONOR' \
  -H 'user-model: TEL-AN10' \
  -H 'user-tag: 1615af1a34174394' \
  -H 'user-idfa: ' \
  -H 'user-mac: 1615af1a34174394' \
  -H 'user-channel: slp' \
  -H 'user-oaid: 8d09ccc6-ad83-4e57-b7aa-4e06b7fcb06b' \
  -H 'user-issimulator: false' \
  -H 'user-machine: TEL-AN10' \
  -H 'user-did: DU1jCqoZWPvBV2Dp-XCJUnmy0Kssfh62jXc7' \
  -H 'user-isroot: false' \
  -H 'host: 192.168.1.3' \
  -H 'user-token: bdacVaKPNbmgr3QaaGlrKuoiqIZ6eMAfcUGwq2utjPNk1__2FschhWpm6YQ2hQhcNGpiIdf49GdbQctrjd__2BK__2BEZkl__2BkFlwEe7Vg5ftd7B__2B51O5ML2UPUuVD4qti0w' \
  -H 'user-imei: 1615af1a34174394' \
  -H 'user-language: zh_CN'
```

## 单个房间热度

> Postman 路径: `room/单个房间热度`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Hot/Get' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "rid": 100104339
}'
```

## 批量房间热度

> Postman 路径: `room/批量房间热度`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Room.Hot/GetBatch' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "rids": [
    100104339
  ]
}'
```
