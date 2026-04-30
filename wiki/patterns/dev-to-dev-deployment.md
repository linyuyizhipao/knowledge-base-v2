---
id: patterns/dev-to-dev-deployment
label: 开发与发布流程（PR → master）
source: curated/patterns/dev-to-dev-deployment.md
role: 规范
compiled: 2026-04-30
source_hash: 2c73dbbe16936d09
tags:
  - deployment
  - workflow
  - git
  - PR
  - master
  - Jenkins
links:
  - ai-workflow
  - slpctl
  - slpctl-usage-guide
---

# 开发与发布流程

> 从本地开发到测试服务器部署的完整流程

## 分支管理

| 分支类型 | 命名格式 | 说明 |
|----------|---------|------|
| 主分支 | `master` | 生产环境，保护分支，PR 目标 |
| 功能分支 | `hu/<需求名称>` | 个人功能开发 |
| 修复分支 | `fix/<问题描述>` | Bug 修复 |
| 紧急修复 | `hotfix/<问题描述>` | 生产环境紧急修复 |

### 禁令

1. **禁止在 master 分支直接开发** - 必须从 master 创建功能分支
2. **禁止跳过 PR 直接合并** - 所有合入 master 的变更必须通过 PR
3. **禁止使用 Docker** - Jenkins 构建
4. **禁止跳过知识检索直接写代码**

## 开发发布流程

### 1. 创建功能分支

```bash
git checkout master && git pull origin master
git checkout -b hu/<需求名称>
git push -u origin hu/<需求名称>
```

### 2. 本地开发

```bash
git checkout hu/<需求名称>
# ... 编辑代码 ...
git add -A && git commit -anm 'feat: <描述>'
```

### 3. 创建 PR 并合入 master

```bash
# 准备
git push origin hu/<需求名称>

# 创建 PR
gh pr create --base master --head hu/<需求名称> --title "<标题>" --body "<描述>"

# 审查通过后合入
gh pr merge --merge
```

### 4. 解决冲突（如需要）

```bash
git checkout hu/<需求名称>
git fetch origin && git rebase origin/master
# 解决冲突后
git add <file> && git rebase --continue
git push --force-with-lease origin hu/<需求名称>
```

### 5. 部署

```bash
slpctl ci -w  # 触发 Jenkins 构建并等待完成
```

Jenkins 构建流程：`git pull origin master` → `make build` → 部署到测试服务器 → `supervisorctl restart`

## 常见场景

### 快速修复小 Bug

```bash
git checkout master && git pull
git checkout -b fix/<描述>
# 修复并提交
gh pr create --base master --head fix/<描述> --title "fix: <描述>" --body "<描述>"
gh pr merge --merge
slpctl ci -w
```

### 紧急上线

```bash
git checkout master && git pull
git checkout -b hotfix/<问题>
# 修复并提交
gh pr create --base master --head hotfix/<问题> --title "hotfix: <描述>" --body "<描述>"
gh pr merge --merge
```

## 检查清单

### PR 提交前

- [ ] 代码本地测试通过
- [ ] Commit 信息清晰
- [ ] 无编译错误和 Warning
- [ ] PR 目标分支为 master

### 部署后

- [ ] slpctl ci 输出 SUCCESS
- [ ] Jenkins 日志无错误
- [ ] Supervisor 进程 RUNNING
- [ ] 核心功能验证通过
