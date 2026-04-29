---
id: curl/02-room_pet
label: 房间相关 - pet
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 房间相关]
curl_count: 3
---

# 房间相关 - pet
> 编译自 Postman Collection | 3 条命令

## 命令列表

1. 宠物info
2. 复活宠物
3. 领取宠物请求

## 宠物info

> Postman 路径: `大歌房/宠物info`

```bash
curl -X POST '{{hostname}}/go/room/immortalPet/info' \
  -H 'user-token: {{user-token}}'
```

## 复活宠物

> Postman 路径: `大歌房/复活宠物`

```bash
curl -X POST '{{hostname}}/go/room/immortalPet/revive' \
  -H 'user-token: {{user-token}}'
```

## 领取宠物请求

> Postman 路径: `大歌房/领取宠物请求`

```bash
curl -X POST '{{hostname}}/go/room/immortalPet/claim' \
  -H 'user-token: {{user-token}}'
```
