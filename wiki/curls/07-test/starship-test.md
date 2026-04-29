---
id: curl/07-test_starship-test
label: 测试端点 - starship-test
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 测试端点]
curl_count: 4
---

# 测试端点 - starship-test
> 编译自 Postman Collection | 4 条命令

## 命令列表

1. 迁移装扮卡到仓库
2. 萌新设置高潜池 Copy
3. 农场鱼塘告警
4. 带装扮 Copy

## 迁移装扮卡到仓库

> Postman 路径: `user/迁移装扮卡到仓库`

```bash
curl -X POST '{{hostname}}/go/starship/test/mv' \
  -H 'user-token: {{user-token}}'
```

## 萌新设置高潜池 Copy

> Postman 路径: `user/萌新设置高潜池 Copy`

```bash
curl -X POST '{{hostname}}/go/starship/test/everyDraw' \
  -H 'user-token: {{user-token}}'
```

## 农场鱼塘告警

> Postman 路径: `starship/农场鱼塘告警`

```bash
curl -X POST '{{hostname}}/go/starship/test/alarm' \
  -H 'user-token: {{user-token}}'
```

## 带装扮 Copy

> Postman 路径: `装扮/带装扮 Copy`

```bash
curl -X POST 'https://114.55.3.96/go/starship/test/sendNsq?format=json' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{
  "topic_name": "slp.room.recommend.more",
  "cmd": "user_statics_ascribe",
  "data": {
    "anchor_uid": 200251609,
    "uid": 200000015,
    "ts": 1755245627
  }
}'
```
