# 口令功能

> Passcode APIs

## 命令列表

1. 获取用户勋章列表
2. 口令创建
3. 口令列表
4. 口令开启
5. 口令使用
6. 口令使用config
7. 口令详情

## 获取用户勋章列表

> Postman 路径: `大歌房/获取用户勋章列表`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/getUserBadges' \
  -H 'user-token: {{user-token}}'
```

## 口令创建

> Postman 路径: `大歌房/口令创建`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeCreate' \
  -H 'user-token: {{user-token}}'
```

## 口令列表

> Postman 路径: `大歌房/口令列表`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeList' \
  -H 'user-token: {{user-token}}'
```

## 口令开启

> Postman 路径: `大歌房/口令开启`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeToggle' \
  -H 'user-token: {{user-token}}'
```

## 口令使用

> Postman 路径: `大歌房/口令使用`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeUse' \
  -H 'user-token: {{user-token}}'
```

## 口令使用config

> Postman 路径: `大歌房/口令使用config`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeConfig' \
  -H 'user-token: {{user-token}}'
```

## 口令详情

> Postman 路径: `大歌房/口令详情`

```bash
curl -X POST '{{hostname}}/go/room/bigBrother/passcodeDetail' \
  -H 'user-token: {{user-token}}'
```
