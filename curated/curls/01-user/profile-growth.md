# 用户档案与成长

> User profile, growth channel, balance, room tag

## 命令列表

1. 用户渠道
2. 获取厅的私聊率
3. 获取厅l里面新用户的私聊率
4. 用户余额
5. MgetBadges
6. 萌新查看用户是不是主播的rpc
7. 查看转化率
8. 加用户榜单分数
9. rpc_friend
10. 获取用户信息

## 用户渠道

> Postman 路径: `user/用户渠道`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Growth/CheckUserParentChannel' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200253716,
  "user_channel": [
    96,
    100
  ]
}'
```

## 获取厅的私聊率

> Postman 路径: `user/获取厅的私聊率`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Growth/BatchRoomPrivateRate' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uids": [
    200259090
  ],
  "rid": 100104339
}'
```

## 获取厅l里面新用户的私聊率

> Postman 路径: `user/获取厅l里面新用户的私聊率`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Growth/BatchNewUserPrivateRate' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uids": [
    200260243,
    200259090
  ],
  "rid": 100104339
}'
```

## 用户余额

> Postman 路径: `user/用户余额`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Profile/GetUserBalance' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "user_id": 200000022
}'
```

## MgetBadges

> Postman 路径: `user/MgetBadges`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Profile/MgetBadges' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "badge_ids": [
    7547
  ],
  "fields": []
}'
```

## 萌新查看用户是不是主播的rpc

> Postman 路径: `user/萌新查看用户是不是主播的rpc`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Profile/MgetUserAggr' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uids": [
    200251598
  ]
}'
```

## 查看转化率

> Postman 路径: `后台/信息流/查看转化率`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Growth/BatchAnchorRoomPrivateRate' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "anchor_uid": 200251664,
  "uids": [
    200000098,
    200252480,
    200000019,
    200000002,
    200000032
  ]
}'
```

## 加用户榜单分数

> Postman 路径: `后台/加用户榜单分数`

```bash
curl -X POST '{{rpc-hostname}}/rpc/User.Rank/BatchIncrRank' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "incr_rank": [
    {
      "member_id": 200000024,
      "scene": 8,
      "group_id": 300000043,
      "score": 2,
      "sort": [
        2,
        2
      ]
    }
  ]
}'
```

## rpc_friend

> Postman 路径: `装扮/rpc_friend`

```bash
curl -X GET '{{rpc-hostname}}/rpc/User.Profile/MgetUserAggr' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": [
    200251598,
    200000177,
    200000329
  ]
}'
```

## 获取用户信息

> Postman 路径: `ai/获取用户信息`

```bash
curl -X GET '{{rpc-hostname}}/rpc/User.Profile/Mget' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uids": [
    200253517
  ],
  "fields": [
    "name",
    "uid"
  ]
}'
```
