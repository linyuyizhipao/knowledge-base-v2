# 农场 HTTP

> Farm HTTP endpoints

## 命令列表

1. 池塘升级
2. 池塘深度升级
3. 池塘深度升级
4. 祈福抽奖活动主页，返回活动信息、用户进度、心愿值、价格配置
5. 祈福抽奖
6. 农场能量值转存rpc
7. 农场种子列表
8. 农场沙漏使用
9. 每日礼包主页
10. 农场升级页面
11. 农场装扮赠送api
12. 菜摊升级页面
13. 农场装扮分类列表
14. 农场装扮穿戴
15. 农场装扮列表
16. 农场装扮用户权限列表

## 池塘升级

> Postman 路径: `starship/鱼塘/池塘升级`

```bash
curl -X POST '{{hostname}}/go/starship/farm/fishpondUpLevel' \
  -H 'user-token: {{user-token}}'
```

## 池塘深度升级

> Postman 路径: `starship/鱼塘/池塘深度升级`

```bash
curl -X POST '{{hostname}}/go/starship/farm/fishpondUpLevel' \
  -H 'user-token: {{user-token}}'
```

## 池塘深度升级

> Postman 路径: `starship/鱼塘/池塘深度升级`

```bash
curl -X POST '{{hostname}}/go/starship/farm/castBaitHome' \
  -H 'user-token: {{user-token}}'
```

## 祈福抽奖活动主页，返回活动信息、用户进度、心愿值、价格配置

> Postman 路径: `starship/农场活动模版2/祈福抽奖活动主页，返回活动信息、用户进度、心愿值、价格配置`

```bash
curl -X POST '{{hostname}}/go/starship/farm/prayerHome' \
  -H 'user-token: {{user-token}}'
```

## 祈福抽奖

> Postman 路径: `starship/农场活动模版2/祈福抽奖`

```bash
curl -X POST '{{hostname}}/go/starship/farm/prayerDraw' \
  -H 'user-token: {{user-token}}'
```

## 农场能量值转存rpc

> Postman 路径: `starship/农场能量值转存rpc`

```bash
curl -X POST '{{hostname}}/go/starship/farm/farmEnergyMv' \
  -H 'user-token: {{user-token}}'
```

## 农场种子列表

> Postman 路径: `starship/农场种子列表`

```bash
curl -X POST '{{hostname}}/go/starship/farm/cropList' \
  -H 'user-token: {{user-token}}'
```

## 农场沙漏使用

> Postman 路径: `starship/农场沙漏使用`

```bash
curl -X POST '{{hostname}}/go/starship/farm/sandClockUse' \
  -H 'user-token: {{user-token}}'
```

## 每日礼包主页

> Postman 路径: `starship/每日礼包主页`

```bash
curl -X POST '{{hostname}}/go/starship/farmDailyPack/home' \
  -H 'user-token: {{user-token}}'
```

## 农场升级页面

> Postman 路径: `starship/农场升级页面`

```bash
curl -X POST '{{hostname}}/go/starship/farm/levelUpPanel' \
  -H 'user-token: {{user-token}}'
```

## 农场装扮赠送api

> Postman 路径: `starship/农场装扮赠送api`

```bash
curl -X POST '{{hostname}}/go/starship/farm/givePretend' \
  -H 'user-token: {{user-token}}'
```

## 菜摊升级页面

> Postman 路径: `starship/菜摊升级页面`

```bash
curl -X POST '{{hostname}}/go/starship/farm/vegeUpPanel' \
  -H 'user-token: {{user-token}}'
```

## 农场装扮分类列表

> Postman 路径: `starship/农场装扮分类列表`

```bash
curl -X POST '{{hostname}}/go/starship/farm/getCateList' \
  -H 'user-token: {{user-token}}'
```

## 农场装扮穿戴

> Postman 路径: `starship/农场装扮穿戴`

```bash
curl -X POST '{{hostname}}/go/starship/farm/wearPretend' \
  -H 'user-token: {{user-token}}'
```

## 农场装扮列表

> Postman 路径: `starship/农场装扮列表`

```bash
curl -X POST '{{hostname}}/go/starship/farm/getPretendList' \
  -H 'user-token: {{user-token}}'
```

## 农场装扮用户权限列表

> Postman 路径: `starship/农场装扮用户权限列表`

```bash
curl -X POST '{{hostname}}/go/starship/farm/getUserAllPrivilege' \
  -H 'user-token: {{user-token}}'
```
