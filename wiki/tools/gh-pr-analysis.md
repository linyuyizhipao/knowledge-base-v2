---
id: tools/gh-pr-analysis
label: gh-pr-analysis
source: /Users/hugh/project/my-wiki/curated/tools/gh-pr-analysis.md
role: 工具
compiled: 2026-04-28
source_hash: 4e78ed4952c1244b18a60d999d6a2ca5
---

> 用于 PR 分析、代码审查、反向推导开发流程的完整命令参考

---

## 快速开始

### 认证检查

```bash
# 检查认证状态
gh auth status

# 认证登录
gh auth login
```

---

## PR 分析核心命令

### 1. 查看 PR 基本信息

```bash
# 查看当前分支对应的 PR
gh pr view

# 查看指定 PR
gh pr view <PR 号>
gh pr view 123

# 查看 PR URL
gh pr view --json url -q .url

# 查看 PR 完整 JSON 信息
gh pr view --json additions,author,body,changedFiles,commits,createdAt,files,labels,title
```

### 2. 查看 PR 变更内容

```bash
# 查看完整 diff
gh pr diff

# 查看指定 PR 的 diff
gh pr diff <PR 号>
gh pr diff 123

# 只看文件名（不显示具体变更）
gh pr diff --name-only

# 排除特定文件类型的 diff
gh pr diff --exclude '*.yml' --exclude 'generated/*'

# 输出为 patch 格式
gh pr diff --patch
```

### 2.1 Diff 降噪（减少 Token 消耗）

推荐从“范围”到“细节”逐步展开：

```bash
# 1) 先看范围
gh pr diff <PR 号> --name-only
gh pr diff <PR 号> --stat

# 2) 再看可读的 patch（先排除噪音文件）
gh pr diff <PR 号> --patch \
  --exclude 'vendor/**' --exclude 'node_modules/**' \
  --exclude '**/*.pb.go' --exclude '**/*.gen.*' --exclude 'generated/**' \
  --exclude '**/*.lock' --exclude 'go.sum' \
  --exclude '**/*.{png,jpg,jpeg,gif,svg,ico,webp,pdf,zip,tar,gz}'
```

如果仍然很大：在 `--patch` 输出上做二次清洗（按文件块过滤），只保留“需要读的文件块”再交给 AI 分析。

### 3. 查看 PR 评论和 Review

```bash
# 查看 PR 评论
gh pr view --comments

# 查看 PR 审查意见
gh pr view --json reviews

# 查看 PR 状态检查（CI）
gh pr checks
```

---

## 反向推导开发流程

### Step 1: 获取 PR 基本信息

```bash
# 获取 PR 标题、作者、创建时间、标签
gh pr view <PR 号> --json title,author,createdAt,labels,milestone

# 输出格式化
gh pr view <PR 号> --json title,author,createdAt,labels \
  --template '{{.title}} by {{.author.login}} created at {{.createdAt}}'
```

### Step 2: 分析变更文件

```bash
# 列出所有变更的文件
gh pr diff --name-only

# 获取变更统计（新增/删除行数）
gh pr view --json additions,deletions,changedFiles
```

### Step 3: 深入分析具体文件

```bash
# 查看特定文件的 diff（使用 grep 过滤）
gh pr diff | grep -A 20 "^diff --git.*path/to/file"

# 只看 Go 文件的变更
gh pr diff --exclude '*.md' --exclude '*.json'

# 排除配置文件，只看业务代码
gh pr diff --exclude '*.yml' --exclude '*.yaml' --exclude '*.toml'
```

### Step 4: 获取完整 JSON 数据

```bash
# 获取所有可用字段
gh pr view --json \
  additions,assignees,author,autoMergeRequest,baseRefName,baseRefOid,body,\
  changedFiles,closed,closedAt,comments,commits,createdAt,deletions,files,\
  headRefName,headRefOid,headRepository,labels,number,state,title,updatedAt,url
```

### Step 5: 使用 jq 过滤数据

```bash
# 只获取变更的文件名列表
gh pr view --json files --jq '.files[].path'

# 获取每个文件的变更统计
gh pr view --json files --jq '.files[] | {path: .path, additions: .additions, deletions: .deletions}'

# 获取作者和创建时间
gh pr view --jq '{author: .author.login, created: .createdAt, title: .title}'
```

---

## 实用命令组合

### 命令 1: 生成 PR 变更摘要

```bash
# PR 摘要：标题 + 作者 + 变更文件数 + 新增删除行数
gh pr view <PR 号> --json title,author,changedFiles,additions,deletions \
  --template 'PR: {{.title}}
Author: {{.author.login}}
Files changed: {{.changedFiles}}
Additions: {{.additions}} | Deletions: {{.deletions}}'
```

### 命令 2: 列出所有变更的 Go 文件

```bash
gh pr diff --name-only | grep '\.go$'
```

### 命令 3: 分析 PR 涉及的模块

```bash
# 提取一级目录，了解涉及的模块
gh pr diff --name-only | cut -d'/' -f1 | sort | uniq -c | sort -rn
```

### 命令 4: 获取 PR 提交历史

```bash
# 查看 PR  commits
gh pr view <PR 号> --json commits --jq '.commits[].commit.messageHeadline'
```

### 命令 5: 导出 PR 分析数据为 JSON

```bash
# 完整导出用于后续分析
gh pr view <PR 号> \
  --json title,author,createdAt,commits,files,additions,deletions,labels,body \
  > pr-<PR 号>-analysis.json
```

---

## 常用 JSON 字段说明

| 字段 | 说明 |
|------|------|
| `title` | PR 标题 |
| `author` | 作者信息（`.login` 获取用户名） |
| `body` | PR 描述 |
| `createdAt` | 创建时间 |
| `updatedAt` | 更新时间 |
| `state` | 状态（OPEN/CLOSED/MERGED） |
| `additions` | 新增行数 |
| `deletions` | 删除行数 |
| `changedFiles` | 变更文件数 |
| `files` | 文件详情数组（path, additions, deletions） |
| `commits` | 提交历史 |
| `labels` | 标签 |
| `headRefName` | 源分支名 |
| `baseRefName` | 目标分支名 |
| `url` | PR 链接 |

---

## API 高级用法

### 使用 gh api 直接调用 GitHub API

```bash
# 获取 PR 列表
gh api /repos/{owner}/{repo}/pulls

# 获取特定 PR
gh api /repos/{owner}/{repo}/pulls/{number}

# 获取 PR 文件列表
gh api /repos/{owner}/{repo}/pulls/{number}/files

# 获取 PR commits
gh api /repos/{owner}/{repo}/pulls/{number}/commits
```

### 使用当前仓库占位符

```bash
# {owner} {repo} 会自动替换为当前仓库
gh api /repos/{owner}/{repo}/pulls

# 查看替换后的实际值
echo "Owner: $GH_REPO_OWNER, Repo: $GH_REPO_NAME"
```

---

## 反向推导开发流程模板

### 完整分析脚本

```bash
#!/bin/bash
# 使用方法：./analyze-pr.sh <PR 号>

PR_NUMBER=$1

echo "=== PR 基本信息 ==="
gh pr view $PR_NUMBER --json title,author,createdAt,labels \
  --template '标题：{{.title}}
作者：{{.author.login}}
创建时间：{{.createdAt}}
标签：{{range .labels}}{{.name}} {{end}}'

echo ""
echo "=== 变更统计 ==="
gh pr view $PR_NUMBER --json additions,deletions,changedFiles \
  --template '文件数：{{.changedFiles}}
新增：{{.additions}} 行
删除：{{.deletions}} 行'

echo ""
echo "=== 变更文件列表 ==="
gh pr diff --name-only

echo ""
echo "=== 提交历史 ==="
gh pr view $PR_NUMBER --json commits \
  --jq '.commits[].commit.messageHeadline'
```

### 分析输出示例

```
=== PR 基本信息 ===
标题：feat: 添加用户 profile API
作者：hugh
创建时间：2026-04-10T08:00:00Z
标签：feature enhancement

=== 变更统计 ===
文件数：5
新增：120 行
删除：15 行

=== 变更文件列表 ===
app/api/user/profile.go
app/service/user/profile.go
app/dao/user/profile.go
app/domain/user/profile.go
proto/user/profile.proto

=== 提交历史 ===
feat: 添加 profile API
feat: 完善 profile 查询逻辑
fix: 修复 profile 缓存问题
```

---

## 其他有用命令

```bash
# 列出所有 PR
gh pr list

# 列出我创建的 PR
gh pr list --author @me

# 列出需要我审查的 PR
gh pr list --review-requested @me

# 切换当前分支到指定 PR
gh pr checkout <PR 号>

# 创建新 PR
gh pr create --title "标题" --body "描述"

# 关闭 PR
gh pr close <PR 号>

# 合并 PR
gh pr merge <PR 号> --merge
```

---

## jq 查询速查

```bash
# 获取所有变更文件路径
gh pr view --json files --jq '.files[].path'

# 只获取 Go 文件
gh pr view --json files --jq '.files[] | select(.path | endswith(".go")) | .path'

# 按变更大小排序
gh pr view --json files --jq '.files | sort_by(.additions + .deletions) | reverse'

# 获取作者和提交数
gh pr view --json author,commits --jq '{author: .author.login, commits: (.commits | length)}'
```

---

## 最佳实践

### 分析大型 PR

1. **先看概览**：`gh pr view --json changedFiles,additions,deletions`
2. **按模块筛选**：`gh pr diff --name-only | cut -d'/' -f1 | sort | uniq`
3. **重点文件深入**：`gh pr diff | grep -A 50 "path/to/key/file"`

### 分析小型 PR

1. **直接看 diff**：`gh pr diff`
2. **快速审查**：`gh pr view --web`

### 批量分析多个 PR

```bash
# 获取最近 10 个已合并 PR 的统计
gh pr list --state merged --limit 10 --json number,title,additions,deletions \
  --jq '.[] | "#\(.number): \(.title) (+\(.additions)/-\(.deletions))"'
```

---

**版本**: 1.0 | **创建**: 2026-04-11


## 相关知识

- [[USER_GUIDE]]
