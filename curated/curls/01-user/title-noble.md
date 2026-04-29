# 贵族与头衔

> User title, noble subscription

## 命令列表

1. 送贵族订阅时间
2. 活动组SaveUserGrowth

## 送贵族订阅时间

> Postman 路径: `贵族/送贵族订阅时间`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Title/SendUserTitleSubTime' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "title_param": [
    {
      "uid": 200246873,
      "month": 12
    }
  ]
}'
```

## 活动组SaveUserGrowth

> Postman 路径: `贵族/活动组SaveUserGrowth`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Title/SaveUserGrowth' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "user_growth": {
    "uid": 200000003,
    "growth_val": 100,
    "effective_value": 100,
    "reason": "sdsdsdsd"
  }
}'
```
