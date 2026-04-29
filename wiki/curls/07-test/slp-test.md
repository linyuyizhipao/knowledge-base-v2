---
id: curl/07-test_slp-test
label: 测试端点 - slp-test
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 测试端点]
curl_count: 21
---

# 测试端点 - slp-test
> 编译自 Postman Collection | 21 条命令

## 命令列表

1. 萌新白名单
2. 信息流2转
3. 信息流1转
4. 王权重新跑用户
5. 王权入驻
6. 萌新设置每天被私聊数
7. 发nsq
8. 萌新设置主播
9. 萌新设置高潜池
10. 设置互为好友测试环境
11. 测试-评论的点赞修改
12. 点赞动态评论
13. 查tablestore
14. 修复动态的es
15. 修复好友
16. 送装扮
17. unfollow
18. 修复es
19. 设置神秘人
20. 设置banner白名单
21. 查询派单es

## 萌新白名单

> Postman 路径: `user/萌新白名单`

```bash
curl -X POST '{{hostname}}/go/slp/test/setKaTouch' \
  -H 'user-token: {{user-token}}'
```

## 信息流2转

> Postman 路径: `user/信息流2转`

```bash
curl -X POST '{{hostname}}/go/slp/test/sendFlowPop' \
  -H 'user-token: {{user-token}}'
```

## 信息流1转

> Postman 路径: `user/信息流1转`

```bash
curl -X POST '{{hostname}}/go/slp/test/sendFlowPopV2' \
  -H 'user-token: {{user-token}}'
```

## 王权重新跑用户

> Postman 路径: `user/王权重新跑用户`

```bash
curl -X POST '{{hostname}}/go/slp/test/setEnter' \
  -H 'user-token: {{user-token}}'
```

## 王权入驻

> Postman 路径: `user/王权入驻`

```bash
curl -X POST '{{hostname}}/go/slp/test/setKaTouch' \
  -H 'user-token: {{user-token}}'
```

## 萌新设置每天被私聊数

> Postman 路径: `user/萌新设置每天被私聊数`

```bash
curl -X POST '{{hostname}}/go/slp/test/setKaTouchPrivateNum' \
  -H 'user-token: {{user-token}}'
```

## 发nsq

> Postman 路径: `user/发nsq`

```bash
curl -X POST '{{hostname}}/go/slp/test/sendNsq' \
  -H 'user-token: {{user-token}}'
```

## 萌新设置主播

> Postman 路径: `user/萌新设置主播`

```bash
curl -X POST '{{hostname}}/go/slp/test/setKaTouchBroker' \
  -H 'user-token: {{user-token}}'
```

## 萌新设置高潜池

> Postman 路径: `user/萌新设置高潜池`

```bash
curl -X POST '{{hostname}}/go/slp/test/setNewGui' \
  -H 'user-token: {{user-token}}'
```

## 设置互为好友测试环境

> Postman 路径: `user/设置互为好友测试环境`

```bash
curl -X POST '{{hostname}}/go/slp/test/setFriend' \
  -H 'user-token: {{user-token}}'
```

## 测试-评论的点赞修改

> Postman 路径: `test/测试-评论的点赞修改`

```bash
curl -X POST '{{hostname}}/go/slp/test/uploadCode'
```

## 点赞动态评论

> Postman 路径: `test/点赞动态评论`

```bash
curl -X POST '{{hostname}}/go/slp/circle/commentLike'
```

## 查tablestore

> Postman 路径: `select/查tablestore`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/tableStore'
```

## 修复动态的es

> Postman 路径: `select/修复动态的es`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/tableStore'
```

## 修复好友

> Postman 路径: `select/修复好友`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/rebuild'
```

## 送装扮

> Postman 路径: `select/送装扮`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/rebuild'
```

## unfollow

> Postman 路径: `select/unfollow`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/tableStore'
```

## 修复es

> Postman 路径: `select/修复es`

```bash
curl -X POST 'https://116.62.125.230/go/slp/test/circleEsRebuild'
```

## 设置神秘人

> Postman 路径: `select/设置神秘人`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/setMystery'
```

## 设置banner白名单

> Postman 路径: `select/设置banner白名单`

```bash
curl -X POST 'https://alpha.sleeplessplanet.com/go/slp/test/setBannerWhite'
```

## 查询派单es

> Postman 路径: `select/查询派单es`

```bash
curl -X GET 'https://114.55.3.96/go/slp/test/gameOrderSearch?package=com.yhl.sleepless.android&_ipv=0&_platform=android&_index=655&_model=MAA-AN10&_timestamp=1721014263&format=pb&_sign=9875d03ec17f8ff33356a721c04a9d35&_dk=ca987378cb9dcbc2b947a8d2707cd346&uid=200000003&rid=0&ver=7&scene=0' \
  -H 'user-agent: Mozilla/5.0 (Linux; Android 14; MAA-AN10 Build/HONORMAA-AN10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/120.0.6099.193 Mobile Safari/537.36 / Xs android V5.22.0.0 / Js V1.0.0.0 / Login V1720679451' \
  -H 'user-brand: HONOR' \
  -H 'user-model: MAA-AN10' \
  -H 'user-tag: 54cab64442125b04' \
  -H 'user-idfa: ' \
  -H 'user-mac: 54cab64442125b04' \
  -H 'user-channel: slp' \
  -H 'user-oaid: ' \
  -H 'user-issimulator: false' \
  -H 'user-machine: MAA-AN10' \
  -H 'user-did: DUx-RsuwycK95qkILZd_DWPRg3JCsUZ5kc02' \
  -H 'user-isroot: false' \
  -H 'host: 114.55.3.96' \
  -H 'user-token: c71eKhxKXxKVHkoWNjoBzSJFDi0ROpUep6Z1QQ15ncn46IuHRRj7PTqxUfFeUuIDOXdFYE6DNUVfGQlJRet4a9EfJmSe1ega__2FGxiWWcImyj45TM6rqI__2FJF4yCg' \
  -H 'user-imei: 54cab64442125b04' \
  -H 'user-language: zh_CN' \
  -d '{
  "param": {
    "id": 100,
    "uid": 200000003,
    "boss_uid": 200000024,
    "rid": 100000255,
    "bid": 100000002,
    "game_id": 8,
    "levels": "76",
    "status": 2,
    "system": "不限",
    "start_time": 1720696938,
    "end_time": 1722220685,
    "desc": "暂无他他他他不",
    "page_index": 1000001,
    "count": 1,
    "u_tag": "3",
    "u_tone": "1,2,3,4,5,6,7"
  }
}'
```
