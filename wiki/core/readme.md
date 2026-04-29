---
id: readme
label: Harness - 个人知识库
source: curated/README.md
role: overview
compiled: 2026-04-25
tags:
  - overview
  - core
links:
  - agents
  - user-guide
  - quick-reference
  - index
---

# Harness - 个人知识库

> AI 驱动的开发规范与知识库管理系统

## 快速开始

### 1. 运行全局配置脚本

```bash
cd /Users/hugh/project/harness/slp-harness
./setup-global-ai.sh
```

这将自动配置以下 AI 工具：
- Claude Code (`~/.claude/CLAUDE.md`)
- Qoder (`~/.qoder/QODER.md`)
- Cursor (`~/.cursorrules`)
- Windsurf (`~/.windsurf/rules`)
- Trae (`~/.trae/rules`)
- Codex (`~/.codex/AGENTS.md`)

### 2. 重启终端

```bash
source ~/.zshrc
```

### 3. 验证配置

```bash
echo $HARNESS_HOME
# 输出: /Users/hugh/project/harness/slp-harness
```

## 目录结构

```
$HARNESS_HOME/
├── AGENTS.md              # AI 统一入口（所有 AI 必读）
├── CODING_STANDARDS.md    # 核心禁令
├── AI_WORKFLOW.md         # 5 阶段开发流程
├── QUICK_REFERENCE.md     # 快速参考卡片
├── setup-global-ai.sh     # 全局配置脚本
└── knowledge/
    ├── INDEX.md           # 已有文档索引（写前必查）
    ├── USER_GUIDE.md      # 使用说明书
    ├── DOCUMENT_LOCATION_RULES.md  # 文档存放规则
    ├── projects/          # 项目知识
    ├── cross-projects/    # 跨项目业务
    ├── patterns/          # 通用模式
    ├── tools/             # 工具文档
    └── anti-patterns/     # 反模式
```

## 核心禁令

| 禁令 | 错误做法 | 正确做法 |
|------|---------|---------|
| 禁止手动编写API代码 | 手写 handler/service/dao | `slpctl code` |
| 禁止循环IO | `for { dao.Find(id) }` | 批量查询 + map |
| 禁止阻塞主goroutine | 同步处理耗时操作 | 异步/NSQ事件 |
| 禁止绕过事件总线 | 直接调用其他模块 | 发布事件解耦 |

## 文档导航

| 文档 | 用途 |
|------|------|
| `AGENTS.md` | AI 统一入口 |
| `CODING_STANDARDS.md` | 核心禁令 |
| `knowledge/INDEX.md` | 已有文档索引 |
| `knowledge/USER_GUIDE.md` | 使用说明书 |

## 推送到 GitHub

```bash
cd $HARNESS_HOME
git add -A
git commit -m "更新知识库"
git push origin main
```

**状态**: 完成 - 集中式管理，所有 AI 工具统一入口