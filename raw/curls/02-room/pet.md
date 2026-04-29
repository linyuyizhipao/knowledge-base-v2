# 宠物功能

> Immortal pet APIs

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
