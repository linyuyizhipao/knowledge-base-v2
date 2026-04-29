---
id: curl/03-farm_farm-commodity
label: 农场/星舰 - farm-commodity
source: curated/curls/03-farm/farm-commodity.md
role: curl
compiled: 2026-04-28
tags: [curl, 农场/星舰, farm-commodity]
curl_count: 2
---

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
| items[].p_type | 物品类型：4=装扮, 1=金币, 2=能量, 3=兑换券 |
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
