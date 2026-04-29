# 外部审核

> External audit

## 命令列表

1. 审核测试回调

## 审核测试回调

> Postman 路径: `后台/审核/审核测试回调`

```bash
curl -X POST 'https://audit-api.miaodongshiguang.com:12001/go/audit/audit/callback' \
  -H 'Authorization: 111111' \
  -d '{
  "choice": "circle_verify",
  "stage": "csmsaudit",
  "pk_value": "1702550701802956",
  "uid": 200000022,
  "review": 0,
  "origin": [],
  "value": [
    {
      "field": "content",
      "type": "text",
      "value": [
        "โสดนะคร้า ทักได้คร้า🥺"
      ],
      "data_id": "76d964cda16d787896bf652083da3a4f"
    },
    {
      "field": "attach",
      "type": "image",
      "value": [
        "https://xs-aws-proxy.letsveeka.com/vkimg/up/202312/14/5067319_657adcacc08a2.jpeg"
      ],
      "data_id": "4b2a6c558c1b81662703e59fe0b24b2a"
    }
  ],
  "uniqid": "657add37357ed53",
  "extra": {
    "unnecessary": 1
  },
  "status": 1,
  "reason": "reason mark",
  "admin": 1670
}'
```
