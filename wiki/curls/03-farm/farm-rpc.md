---
id: curl/03-farm_farm-rpc
label: 农场/星舰 - farm-rpc
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 农场/星舰]
curl_count: 15
---

# 农场/星舰 - farm-rpc
> 编译自 Postman Collection | 15 条命令

## 命令列表

1. 用户贵族
2. 鱼列表
3. 池塘信息
4. 查看鱼的售价
5. 鱼塘深度
6. 鱼塘等级
7. 鱼塘鱼饵
8. 农场装扮信息rpc
9. 农场装扮buf信息返回
10. 农场能量值rpc
11. 农场装扮发放rpc
12. SendFarmCommodity
13. 初始化农场
14. 农场限定种子权限发放
15. 农场装扮赠送rpc

## 用户贵族

> Postman 路径: `user/用户贵族`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GetFishpondInfo' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "fishpond_uid": 200000025
}'
```

## 鱼列表

> Postman 路径: `starship/鱼塘/鱼列表`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/ConfigFarmFish' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "ids": [],
  "show_type": "map"
}'
```

## 池塘信息

> Postman 路径: `starship/鱼塘/池塘信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GetFishpondInfo' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "fishpond_uid": 200254645
}'
```

## 查看鱼的售价

> Postman 路径: `starship/鱼塘/查看鱼的售价`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GetFishSellPrice' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200254645,
  "sell_param": [
    {
      "fish_id": 131,
      "seafood_weight_grade": 1
    }
  ]
}'
```

## 鱼塘深度

> Postman 路径: `starship/鱼塘/鱼塘深度`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/ConfigFarmFishPondDeep' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{}'
```

## 鱼塘等级

> Postman 路径: `starship/鱼塘/鱼塘等级`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/ConfigFarmFishPondLevel' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{}'
```

## 鱼塘鱼饵

> Postman 路径: `starship/鱼塘/鱼塘鱼饵`

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/ConfigFarmFishPondBaitV2' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{"app_id": 66}'
```

**注意**: RPC 方法名是 `ConfigFarmFishPondBaitV2`（带 V2 后缀），不是 `ConfigFarmFishPondBait`。

## 农场装扮信息rpc

> Postman 路径: `starship/农场装扮信息rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/MGetPretendFarm' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "ids": [
    1,
    2
  ]
}'
```

## 农场装扮buf信息返回

> Postman 路径: `starship/农场装扮buf信息返回`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GetUseFarmPretendBuf' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200251598
}'
```

## 农场能量值rpc

> Postman 路径: `starship/农场能量值rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GetFarmUserEnergy' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200258283
}'
```

## 农场装扮发放rpc

> Postman 路径: `starship/农场装扮发放rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/SendPretendFarm' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200253529,
  "pretend_id": 43,
  "seconds": 106400,
  "num": 1,
  "scene": "act"
}'
```

## SendFarmCommodity

> Postman 路径: `starship/SendFarmCommodity`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200254024,
  "request_id": 121212,
  "items": [
    {
      "pid": 28,
      "p_type": 4,
      "num": 1,
      "seconds": 864000,
      "scene": "act",
      "extra": "extra"
    },
    {
      "pid": 33,
      "p_type": 4,
      "num": 1,
      "seconds": 864000,
      "scene": "act",
      "extra": "extra"
    }
  ]
}'
```

## 初始化农场

> Postman 路径: `starship/初始化农场`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/SaveFarm' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200259151
}'
```

## 农场限定种子权限发放

> Postman 路径: `starship/农场限定种子权限发放`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/SendLimitCropPermission' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "request_id": 13232343434,
  "limit_crop": [
    {
      "crop_id": 136,
      "uid": 200251598,
      "num": 1
    }
  ]
}'
```

## 农场装扮赠送rpc

> Postman 路径: `starship/农场装扮赠送rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Farm.Busi/GivePretend' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "uid": 200251609,
  "to_uid": 200251598,
  "pretend_id": 2,
  "seconds": 86400,
  "num": 1,
  "scene": "act"
}'
```
