---
id: tools/gh-pr-analysis
label: gh-pr-analysis
source: curated/tools/gh-pr-analysis.md
role: 工具
compiled: 2026-04-28
source_hash: 4e78ed4952c1244b18a60d999d6a2ca5
---

> PR 分析、代码审查、反向推导开发流程的完整命令参考

## 核心命令

### 查看 PR 信息

```bash
gh pr view                    # 当前分支 PR
gh pr view <PR号>             # 指定 PR
gh pr view --json url -q .url
```

### 查看变更

```bash
gh pr diff                    # 完整 diff
gh pr diff --name-only        # 文件名
gh pr diff --exclude '*.pb.go' --exclude 'vendor/**'  # 排除噪音
```

### Diff 降噪（从范围到细节）

```bash
gh pr diff <PR> --name-only              # 1) 先看范围
gh pr diff <PR> --stat
gh pr diff <PR> --patch --exclude 'vendor/**' --exclude '**/*.pb.go'  # 2) 再看 patch
```

### 评论和 Review

```bash
gh pr view --comments     # 评论
gh pr view --json reviews # 审查意见
gh pr checks              # CI 状态
```

## 反向推导流程

```bash
# Step 1: 基本信息
gh pr view <PR> --json title,author,createdAt,labels

# Step 2: 变更分析
gh pr diff --name-only
gh pr view --json additions,deletions,changedFiles

# Step 3: 深入文件
gh pr diff | grep -A 20 "^diff --git.*path/to/file"

# Step 4: jq 过滤
gh pr view --json files --jq '.files[].path'
```

## 实用组合

```bash
# PR 摘要
gh pr view <PR> --json title,author,changedFiles,additions,deletions

# 涉及模块（提取一级目录）
gh pr diff --name-only | cut -d'/' -f1 | sort | uniq -c | sort -rn

# 批量分析已合并 PR
gh pr list --state merged --limit 10 --json number,title,additions,deletions \
  --jq '.[] | "#\(.number): \(.title) (+\(.additions)/-\(.deletions))"'
```

## 常用字段

| 字段 | 说明 |
|------|------|
| `title` / `body` | PR 标题/描述 |
| `author.login` | 作者 |
| `additions` / `deletions` | 新增/删除行数 |
| `changedFiles` | 变更文件数 |
| `files[].path` | 变更文件路径 |
