---
id: tools/slpctl-usage-guide
label: slpctl-usage-guide
source: curated/tools/slpctl-usage-guide.md
role: 工具
compiled: 2026-04-30
source_hash: 489a980b806156210
---

> slpctl 开发工作流指南

## 标准开发流程（8 步）

```
建表 → gen DAO → code API → proto → 实现业务 → 注册路由 → swagger → ci 部署
```

### 步骤 2：生成 DAO

```bash
slpctl gen -t xs_big_brother_passcode
```

**参数**：`-t` 表名 | `-d` 数据库 | `-u`/`-p` 用户名密码 | `-H`/`-P` 主机端口 | `-project` 目标目录 | `-delete` 删除 | `-dry-run` 预览

**⚠️ 禁止手动编辑 DAO/Model** — 必须通过 `slpctl gen` 生成。

### 步骤 3：生成 API

```bash
# 快速
slpctl code -api /go/room/bigBrother/passcodeCreate -desc "创建口令"

# 批量（JSON 配置）
slpctl code -config passcode_apis.json
```

### 步骤 4：编译 Proto

```bash
make proto          # 修改过的
make proto-all      # 全部
```

### 步骤 8：部署（PR 到 master）

```bash
gh pr create --base master --head <feature> --title "feat: <描述>" --body "<描述>"
gh pr merge --merge
slpctl ci -w
```

## 路由命名

```
/go/room/bigBrother/passcodeCreate
  ↑      ↑          ↑
 项目   业务模块    具体 API
```

| 项目 | 路由前缀 |
|------|----------|
| slp-go | `/go/slp/` |
| slp-room | `/go/room/` |
| slp-starship | `/go/starship/` |
