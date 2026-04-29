---
id: curl/05-ai_ai-card
label: AI 人物 - ai-card
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, AI 人物]
curl_count: 18
---

# AI 人物 - ai-card
> 编译自 Postman Collection | 18 条命令

## 命令列表

1. 查看人物卡片列表
2. 碎片合成
3. 人物背包
4. 碎片合成记录
5. 人物心动等级配置
6. 物品详情
7. 新增卡片
8. act主题info
9. act发放碎片
10. 给后台支持发放物品
11. MgetShareCardLog
12. 删除卡片
13. 批量送卡
14. 单个发卡
15. 分享卡片
16. 编辑卡片图片
17. 唤醒
18. 选择卡图

## 查看人物卡片列表

> Postman 路径: `后台/ai人物/查看人物卡片列表`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/characterCardHome?package=com.yhl.sleepless.android&req_uid=200253499&tab=heartbeat' \
  -H 'user-token: {{user-token}}'
```

## 碎片合成

> Postman 路径: `后台/ai人物/碎片合成`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/fragmentMerge?package=com.yhl.sleepless.android' \
  -H 'user-token: {{user-token}}'
```

## 人物背包

> Postman 路径: `后台/ai人物/人物背包`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/packsack?package=com.yhl.sleepless.android' \
  -H 'user-token: {{user-token}}'
```

## 碎片合成记录

> Postman 路径: `后台/ai人物/碎片合成记录`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/fragmentMergeLog?package=com.yhl.sleepless.android' \
  -H 'user-token: {{user-token}}'
```

## 人物心动等级配置

> Postman 路径: `后台/ai人物/人物心动等级配置`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/heartbeatLvCfg?package=com.yhl.sleepless.android' \
  -H 'user-token: {{user-token}}'
```

## 物品详情

> Postman 路径: `后台/ai人物/物品详情`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/propDetail?package=com.yhl.sleepless.android' \
  -H 'user-token: {{user-token}}'
```

## 新增卡片

> Postman 路径: `ai/新增卡片`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Backend.Service/AddAiCard' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "theme_name": "小k",
  "card_level": 3,
  "source": "act1",
  "id": 0,
  "card_keyword": "西湖边上散步",
  "scene": "xinzi",
  "default_card_img_1": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_img_2": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_img_3": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_woman_img_1": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_woman_img_2": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_woman_img_3": "/static/birthday_housekeeper/birthday_ai_woman_default.png",
  "default_card_video_1": "/video/default.mp4",
  "default_card_video_2": "/video/default.mp4",
  "default_card_video_3": "/video/default.mp4",
  "default_card_woman_video_1": "/video/default.mp4",
  "default_card_woman_video_2": "/video/default.mp4",
  "default_card_woman_video_3": "/video/default.mp4"
}'
```

## act主题info

> Postman 路径: `ai/act主题info`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Character.Ai/MGetThemeInfo' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "theme_ids": [
    1
  ]
}'
```

## act发放碎片

> Postman 路径: `ai/act发放碎片`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Character.Ai/SendAiPropFragment' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "uid": 200251598,
  "prop_fragment": [
    {
      "goods_id": 1,
      "num": 2
    }
  ],
  "request_id": 122323
}'
```

## 给后台支持发放物品

> Postman 路径: `ai/给后台支持发放物品`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Backend.Service/BackendSendGoods' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
    "source":"backend_union",//必传.区分接入业务场景的，本次传：backend_union
    "send_unique_key":"dsds25",
    "send_param":[
        {
            "uid":200253529,//发放对象的uid 89312
            "goods_type":1,//0:物品cid；1：装扮id
            "goods_id":118,//物品cid或者装扮id
            "seconds":86400,//goods_type=1则必传。发放装扮的时长，单位为秒。 如果goods_type=0则不需要传，发放的为cid后台配置的时长
            "num":1//必传。发放个数
        }
    ]
}'
```

## MgetShareCardLog

> Postman 路径: `ai/MgetShareCardLog`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Character.Ai/MgetShareCardLog' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "card_id": 272,
  "params": [
    {
      "uid": 200253529,
      "to_uid": 200251598
    },
    {
      "uid": 200253529,
      "to_uid": 200252459
    },
    {
      "uid": 200253529,
      "to_uid": 200252351
    }
  ]
}'
```

## 删除卡片

> Postman 路径: `ai/删除卡片`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Backend.Service/DelAiCard' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "id": 86
}'
```

## 批量送卡

> Postman 路径: `ai/批量送卡`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Character.Ai/SendCards' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "request_id": 2121677,
  "send_param": [
    {
      "to_uid": 200253529,
      "character_uid": 200253529,
      "theme_id": 168,
      "num": 1,
      "source": "k1"
    }
  ]
}'
```

## 单个发卡

> Postman 路径: `ai/单个发卡`

```bash
curl -X GET '{{rpc-hostname}}/rpc/Character.Ai/SendCard' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "to_uid": 200254943,
  "character_uid": 200254943,
  "theme_id": 3,
  "num": 1
}'
```

## 分享卡片

> Postman 路径: `ai/分享卡片`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/shareCard' \
  -H 'user-token: {{user-token}}'
```

## 编辑卡片图片

> Postman 路径: `ai/编辑卡片图片`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/editCardBackend' \
  -H 'user-token: {{user-token}}'
```

## 唤醒

> Postman 路径: `ai/唤醒`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/rouseVideo' \
  -H 'user-token: {{user-token}}'
```

## 选择卡图

> Postman 路径: `ai/选择卡图`

```bash
curl -X POST '{{hostname}}/go/slp/aiCard/choiceBackendImg' \
  -H 'user-token: {{user-token}}'
```
