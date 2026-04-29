---
id: tools/curl-sink
label: curl-sink
source: curated/tools/curl-sink.md
role: 工具
compiled: 2026-04-28
source_hash: 6c87f9971879a0434304bd70fc7365bd
---

# Curl 沉淀工作流

## 三种输入方式

| 方式 | 处理流程 |
|------|---------|
| 复制 curl 命令 | 解析 → 匹配 category → 追加到 `raw/curls/<category>/<file>.md` |
| Postman 导出文件 | 放到 `raw/curls/` → 运行 `gen_curls.py` → 编译 wiki |
| 指定路由路径 | 从代码中解析 `r.Get("xxx")` 参数 → 生成 curl 模板 |

## 分类规则

| URL 前缀 | Category | 文件 |
|----------|----------|------|
| `/rpc/Farm.Busi/` | 03-farm | farm-rpc |
| `/rpc/User.Profile/` | 01-user | profile-growth |
| `/rpc/Room.Busi/` | 02-room | room-hot-tag |
| `/go/slp/test/` | 07-test | slp-test |
| `/rpc/rpc.pretend/` | 04-pretend | send-drop |

## 环境变量

| 变量 | 说明 |
|------|------|
| `{{rpc-hostname}}` | RPC 服务地址 |
| `{{hostname}}` | HTTP 服务地址 |
| `{{token}}` | 用户认证 Token |

## 约束

- 所有 curl 存入 `raw/curls/`，不直接写 `wiki/curls/`
- 通过编译流程统一生成到 `wiki/`
