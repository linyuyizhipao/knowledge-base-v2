# Curl 沉淀工作流

## 背景

用户有三种方式获取测试环境的 API curl 命令，需要统一沉淀到知识库的 `raw/curls/` 目录。

## 三种输入方式

### 1. 复制 curl 命令

用户提供完整的 curl 命令文本，AI 解析后存入 wiki。

**处理流程**:
- 解析 curl 提取 URL、headers、body
- 根据 URL 路径匹配 category（参照 `raw/curls/` 现有的分类逻辑）
- 追加到对应的 `raw/curls/<category>/<file>.md`
- 如文件不存在则新建
- 运行 `编译wiki` 生成到 `wiki/curls/`

### 2. Postman 导出文件

用户提供 Postman collection JSON 文件，走现有增量编译流程。

**处理流程**:
- 文件放到 `raw/curls/` 目录
- 运行现有的 `gen_curls.py` 分类脚本（位于 `/private/tmp/gen_curls.py`）
- 增量更新已有 markdown 文件
- 运行 `编译wiki`

### 3. 指定路由

用户提供项目路由路径（如 `/go/slp/test/Recharge`），AI 从代码中生成 curl 模板。

**处理流程**:
- 在 slp-go 项目的 `app/api/test_tool.go` 或 `app/api/test.go` 中找到对应方法
- 解析方法体中所有 `r.Get("xxx")` 参数
- 生成带参数占位符的 curl 模板
- 归类到 `raw/curls/` 对应 category
- 运行 `编译wiki`

## 分类规则

参照 `gen_curls.py` 中的 classify 映射，主要分类：

| URL 前缀/关键词 | Category | 文件 |
|-----------------|----------|------|
| `/rpc/Farm.Busi/` | 03-farm | farm-rpc |
| `/rpc/User.Profile/` | 01-user | profile-growth |
| `/rpc/Room.Busi/` | 02-room | room-hot-tag |
| `/go/slp/test/` | 07-test | slp-test |
| `/rpc/rpc.pretend/` | 04-pretend | send-drop |
| `/go/starship/farm` | 03-farm | farm-http |
| `/rpc/Common.Cache/` | 09-cache-consume | cache-ops |

新增未覆盖的 URL 时，AI 自行判断最接近的 category 或新建。

## 输出格式

每个 markdown 文件结构：

```markdown
# 标题

> 简要说明

## 命令列表

1. 命令名称
2. ...

## 命令名称

> 来源说明

```bash
curl -X POST '{{rpc-hostname}}/rpc/...' \
  -H 'Content-Type: application/rpcx' \
  -H 'X-RPCX-SerializeType: 1' \
  -d '{...}'
```
```

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `{{rpc-hostname}}` | RPC 服务地址 | `http://114.55.3.96` |
| `{{hostname}}` | HTTP 服务地址 | `https://114.55.3.96` |
| `{{token}}` | 用户认证 Token | 登录后获取 |

## 约束

- 所有 curl 存入 `raw/curls/`，不直接写 `wiki/curls/`
- 通过编译流程统一生成到 `wiki/`
- knowledge-index.json 的 paths 统一指向 `wiki/`
