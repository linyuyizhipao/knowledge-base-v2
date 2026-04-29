---
id: curl/07-test_room-test
label: 测试端点 - room-test
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 测试端点]
curl_count: 7
---

# 测试端点 - room-test
> 编译自 Postman Collection | 7 条命令

## 命令列表

1. 房间热度push
2. push
3. 给用户发放房间靓号
4. 大咖
5. 炫彩昵称
6. 设置主播分配等级
7. 设置用户等级

## 房间热度push

> Postman 路径: `user/房间热度push`

```bash
curl -X POST '{{hostname}}/go/room/test/refreshHot' \
  -H 'user-token: {{user-token}}'
```

## push

> Postman 路径: `user/push`

```bash
curl -X POST '{{hostname}}/go/room/test/refreshHot' \
  -H 'user-token: {{user-token}}'
```

## 给用户发放房间靓号

> Postman 路径: `user/给用户发放房间靓号`

```bash
curl -X POST '{{hostname}}/go/room/test/sendRomPretty' \
  -H 'user-token: {{user-token}}'
```

## 大咖

> Postman 路径: `user/大咖`

```bash
curl -X POST '{{hostname}}/go/room/test/addFlow' \
  -H 'user-token: {{user-token}}'
```

## 炫彩昵称

> Postman 路径: `user/炫彩昵称`

```bash
curl -X POST '{{hostname}}/go/room/test/addColorName' \
  -H 'user-token: {{user-token}}'
```

## 设置主播分配等级

> Postman 路径: `user/设置主播分配等级`

```bash
curl -X POST 'https://114.55.3.96/go/room/test/setUserLv'
```

## 设置用户等级

> Postman 路径: `家族金币商城/设置用户等级`

```bash
curl -X POST '{{hostname}}/go/room/test/setUserLv' \
  -H 'user-token: {{user-token}}'
```
