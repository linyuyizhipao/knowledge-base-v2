# 农场发放 (SendFarmCommodity)

> 通过 SendFarmCommodity 发放农场物品（装扮/金币/能量等）。
> `SendPretendFarm` 已弃用（报"类型不合法"），统一使用此接口。

## 参数说明

| 参数 | 说明 |
|------|------|
| uid | 目标用户 UID |
| request_id | 请求唯一 ID，测试环境用 `9000000000` 号段，每次自增 |
| items | 物品列表，支持批量发放 |
| items[].pid | 物品 ID（装扮用 pretend_id，金币用 commodity_id） |
| items[].p_type | 物品类型：1=金币, 2=能量, 3=兑换券, 4=装扮, 5=限定种子, 9=农场道具(鱼饵等) |
| items[].num | 数量 |
| items[].seconds | 有效期（秒），0=永久 |
| items[].scene | 场景标识：`"act"` |
| items[].extra | 扩展字段，通常留空 `""` |

## 发装扮示例

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000001,
    "items": [
        {
            "pid": 16,
            "p_type": 4,
            "num": 1,
            "seconds": 864000,
            "scene": "act",
            "extra": ""
        }
    ]
}'
```

## 批量发多个装扮

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000002,
    "items": [
        {
            "pid": 28,
            "p_type": 4,
            "num": 1,
            "seconds": 864000,
            "scene": "act",
            "extra": ""
        },
        {
            "pid": 33,
            "p_type": 4,
            "num": 1,
            "seconds": 864000,
            "scene": "act",
            "extra": ""
        }
    ]
}'
```

## 发金币 (p_type=1)

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000003,
    "items": [
        {"pid": 1, "p_type": 1, "num": 1000000, "seconds": 0, "scene": "act", "extra": ""}
    ]
}'
```

## 发能量 (p_type=2)

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000004,
    "items": [
        {"pid": 1, "p_type": 2, "num": 500, "seconds": 0, "scene": "act", "extra": ""}
    ]
}'
```

## 发限定种子 (p_type=5)

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000005,
    "items": [
        {"pid": 256, "p_type": 5, "num": 30, "seconds": 0, "scene": "act", "extra": ""},
        {"pid": 257, "p_type": 5, "num": 30, "seconds": 0, "scene": "act", "extra": ""}
    ]
}'
```

## 发农场道具 (p_type=9)

```bash
curl -X POST 'http://114.55.3.96/rpc/Farm.Busi/SendFarmCommodity' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
    "uid": 200257811,
    "request_id": 9000000006,
    "items": [
        {"pid": 3, "p_type": 9, "num": 50, "seconds": 0, "scene": "act", "extra": ""}
    ]
}'
```
