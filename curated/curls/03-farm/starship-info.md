# 星舰信息

> Starship.Busi RPC

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
