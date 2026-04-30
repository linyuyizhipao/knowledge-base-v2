---
id: ai-workflow
label: AI 新需求开发流程（7阶段）
source: curated/AI_WORKFLOW.md
role: workflow
compiled: 2026-04-30
source_hash: 86e283f671fed413492ba9736502adf471cc3e27ea193e4f6c00d2d1a664cf5e
tags:
  - workflow
  - development
  - core
  - sub-agent
  - slpctl能力前置
  - PR
  - master
  - git-branch-enforcement
links:
  - coding-standards
  - slpctl-usage-guide
  - sub-agent-orchestration
  - dev-to-dev-deployment
---

# AI 新需求开发流程

> 当 AI 开始新需求开发时，必须遵循此流程以确保与现有知识体系对齐

## 流程概览（7 阶段）

```
阶段 0：创建功能分支（强制检查）→ 从 master 拉取 / 禁止直接在 master 开发
    ↓
阶段 1：需求分析 → 确定需求类型（API/事件/CMD/DB）
    ↓
阶段 2：知识检索 → 阅读 QUICK_REFERENCE.md，根据类型查阅对应文档
    ↓
阶段 3：方案设计 → 先查 slpctl 能生成什么 → 基于生成结果设计
    ↓
阶段 4：实施开发 → 按复杂度触发 sub-agent，使用 slpctl 生成代码
    ↓
阶段 5：PR 合入与部署 → 代码审查 → gh pr create → PR 合入 master → Jenkins 构建
    ↓
阶段 6：知识沉淀 → 更新相关文档，记录新模式/反模式
```

## 步骤详解

### 步骤 0：创建功能分支（强制检查）

**任务**: 确认或创建功能分支，禁止在 master 上直接开发  
**强制要求**: **必须从最新的 master 创建分支，禁止从 dev 或其他分支创建**

**判断逻辑**：

```
用户是否指定了功能分支？
  ├─ 是 → 检查分支来源（见下），然后切换并获取最新代码
  └─ 否 → 搜索相关分支（git branch -a | grep hu/）
          ├─ 找到已有分支 → 询问用户是否使用（必须确认基于 master）
          └─ 无相关分支 → 强制从 master 创建新分支
```

**分支来源强制检查**（任何情况创建分支前必须执行）：
```bash
# 1. 确保远程 master 是最新的
git fetch origin master

# 2. 检查远程 master 的最新提交
echo "Remote master HEAD: $(git log -1 origin/master --oneline)"

# 3. 如果未基于最新 master，终止流程并报错
git merge-base --is-ancestor origin/master HEAD || \
  (echo "❌ 错误：当前分支不是基于最新 master！" && \
   echo "请先：git fetch origin master && git rebase origin/master" && \
   exit 1)
```

**创建新分支流程**：

```bash
git checkout master && git pull origin master
git checkout -b hu/<需求名称>
git push -u origin hu/<需求名称>
```

**⚠️ 禁令**：
- ❌ 禁止在 master 分支直接开发 — 必须从 master 创建功能分支
- ❌ 禁止在功能分支以外的分支开发 — 所有改动在功能分支完成
- ❌ 禁止从 dev 创建功能分支 — 必须从 master 开始
- PR 目标分支为 master — 从 master 拉分支，开发完 PR 回 master

### 步骤 1：需求分析

| 项目 | slp-go / slp-room / slp-starship / slp-common-rpc |
|------|------|
| 类型 | 新增 API / 数据库表 / 事件处理 / CMD 模块 / 修改现有功能 |

### 步骤 2：知识检索

**必读文档**：以 `QUICK_REFERENCE.md` 为唯一入口，按其中"必读文档（按顺序）"完成阅读。

检查清单：
- [ ] 已阅读 `QUICK_REFERENCE.md` 并按清单完成必读文档
- [ ] 已阅读 `knowledge/USER_GUIDE.md`
- [ ] 已确定项目目录
- [ ] 已查阅工具文档
- [ ] 已检查是否有类似功能的参考案例

### 步骤 3：方案设计（slpctl 能力前置）

**设计前先确认 slpctl 能生成什么**：

| 需求涉及 | 先执行 | 基于生成结果设计方案 |
|----------|--------|-------------------|
| 新 API | `slpctl code -api /go/slp/<service>/<action>` | 生成骨架后只需填充 Service 逻辑 |
| 新表/字段变更 | `slpctl gen -t <表名>` | 使用生成的 DAO 方法（Find/FindBatch/Where/All） |
| 新事件 | 查 `event-extension-guide.md` | 按现有 Topic/Cmd 模型设计 |

**⚠️ 重要**: 设计方案必须基于 slpctl 能生成的能力来推演，而不是先手写再让工具覆盖。

### 步骤 4：实施开发（Sub-agent 编排）

| 复杂度 | 触发条件 | 编排方式 | 示例 |
|--------|---------|---------|------|
| **简单**（单文件，<50行） | 逻辑明确 | 直接写 | 加个字段、修个 bug |
| **中等**（多文件，单一项目） | 多文件 | Explore → 编写 → code-reviewer | 新增 API + Service |
| **复杂**（跨项目/架构改动） | 涉及多项目 | Plan → Explore → 实现 → code-reviewer | 跨项目改造 |

**工具使用**：

```bash
slpctl code -api /go/slp/<service>/<action> -project ./<project>
slpctl gen -t <table_name> -d <database>
slpctl ci -w
```

### 步骤 5：PR 合入与部署

**代码审查**：实现完成后，启动 `code-reviewer` agent 进行审查。

**创建 PR 并合入 master**：

```bash
git status
git push origin hu/<需求名称>
gh pr create --base master --head hu/<需求名称> --title "<标题>" --body "<描述>"
gh pr merge --merge
```

**部署**：

```bash
slpctl ci -w
```

### 步骤 6：知识沉淀

| 变更类型 | 更新文档 |
|----------|---------|
| 新增 API | `knowledge/projects/<project>/04-api.md` |
| 新增 Service | `knowledge/projects/<project>/05-service.md` |
| 新增事件 | `knowledge/projects/<project>/09-event-capabilities.md` |
| 发现新模式 | `knowledge/patterns/` |
| 发现反模式 | `knowledge/anti-patterns/` |

## 重要提醒

**开发前必须**：
1. 执行步骤 0（创建功能分支）- **强制检查分支来源**
2. 执行步骤 2（知识检索）
3. 执行步骤 3（slpctl 能力前置查询）

**AI 行为约束**：
- 开始任何 coding 任务前，必须先执行步骤 0、2、3，否则禁止编写代码。
- 所有编码任务在步骤 3 中必须先查询 slpctl 能生成什么，基于生成结果设计方案。
- Sub-agent 由 AI 自主触发。
