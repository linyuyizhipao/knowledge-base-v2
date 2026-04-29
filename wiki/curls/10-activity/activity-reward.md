---
id: curl/10-activity_activity-reward
label: 活动与支付 - activity-reward
source: raw/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 活动与支付]
curl_count: 1
---

# 活动与支付 - activity-reward
> 编译自 Postman Collection | 1 条命令

## 命令列表

1. 活动发奖

## 活动发奖

> Postman 路径: `大歌房/活动发奖`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Activity.Info/GetXiuXianRwdConf' \
  -H 'X-RPCX-SerializeType: 1' \
  -H 'Content-type: application/rpcx' \
  -d '{}'
```
