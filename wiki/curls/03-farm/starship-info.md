---
id: curl/03-farm_starship-info
label: 农场/星舰 - starship-info
source: curated/curls/
role: curl
compiled: 2026-04-28
tags: [curl, 农场/星舰]
curl_count: 1
---

# 农场/星舰 - starship-info
> 编译自 Postman Collection | 1 条命令

## 命令列表

1. 查看星舰信息

## 查看星舰信息

> Postman 路径: `starship/查看星舰信息`

```bash
curl -X POST '{{rpc-hostname}}/rpc/Starship.Busi/MGetMap' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{
  "sids": [
    300000083
  ]
}'
```
