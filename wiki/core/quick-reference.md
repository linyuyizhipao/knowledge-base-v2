---
id: quick-reference
label: AI 快速参考卡片
source: curated/QUICK_REFERENCE.md
role: reference
compiled: 2026-04-27
tags:
  - reference
  - quick-start
  - core
  - sub-agent
links:
  - agents
  - user-guide
  - ai-workflow
  - coding-standards
  - sub-agent-orchestration
  - gh-pr-analysis
---

# AI 快速参考卡片

> 开始任何 coding 任务前，必须先完成知识检索

## 开始前的必读文档（按顺序）

| 文档 | 何时必须读 | 用途 |
|------|------------|------|
| `CODING_STANDARDS.md` | 任何编码/改动前 | slpctl能力 + 核心禁令 + 代码组织规则 |
| `knowledge/USER_GUIDE.md` | 任何编码/改动前 | 场景导航与文档定位方法 |

## 按需阅读

| 触发条件 | 文档 | 用途 |
|----------|------|------|
| 新需求/要走完整流程 | `AI_WORKFLOW.md` | 7 阶段流程 + slpctl能力前置 + 检查清单 |
| 不知道该去哪里找资料 | `knowledge/README.md` | 知识库总索引 |
| 需要工具命令/PR 分析 | `knowledge/tools/` | slpctl、gh 等工具文档 |
| 进入某个项目做需求 | `knowledge/projects/<project>/` | 项目结构/架构/API/事件能力等 |
| 需要 sub-agent 编排 | `patterns/sub-agent-orchestration.md` | 何时触发哪种 agent |

## 开发流程（7 阶段）

```
阶段0：创建功能分支（禁止在 dev/master 直接开发）
         ↓
阶段1：需求分析 → 确定项目/类型
         ↓
阶段2：知识检索 → 阅读 QUICK_REFERENCE.md + 类型文档
         ↓
阶段3：方案设计 → 先查 slpctl 能生成什么 → 基于生成结果设计
         ↓
阶段4：实施开发 → 按复杂度触发 sub-agent + slpctl 生成代码
         ↓
阶段5：合入与部署 → 代码审查 + 合入 dev + Jenkins 构建
         ↓
阶段6：知识沉淀 → 更新对应文档
```

**⚠️ 重要**: 阶段 2（知识检索）和阶段 3（slpctl 能力前置）未完成前，禁止编写代码。

## Sub-agent 快速选择

AI 自主触发，用户无需手动指定：

| 复杂度 | 编排 | 示例 |
|--------|------|------|
| **简单**（单文件，<50行） | 直接写 | 加字段、修 bug |
| **中等**（多文件，单一项目） | Explore → 编写 → code-reviewer | 新增 API + Service |
| **复杂**（跨项目/架构改动） | Plan → Explore → 实现 → code-reviewer | 跨项目改造 |

**用户覆盖**: 可以说"直接用 sub-agent"强制走复杂流程，或"不用 sub-agent"强制直接写。

## slpctl 快速定位

| 场景 | 命令 | 结果 |
|------|------|------|
| 新 API | `slpctl code -api /go/slp/<service>/<action>` | 生成 Handler + Service 接口 + DAO 接口 + 路由 |
| DB 表变更 | `slpctl gen -t <表名>` | 重新生成 DAO CRUD + Protobuf 实体 |
| 部署 | `slpctl ci -w` | 触发 Jenkins 构建 + 等待完成 |

**核心**: 先调用工具生成骨架/实体，再填充业务逻辑。**不要先想怎么写代码，先问 slpctl 能帮我生成什么**。

## 需求类型快速定位

| 需求类型 | 工具命令 | 参考文档 |
|----------|---------|---------|
| **新增 API** | `slpctl code -api /go/slp/user/getInfo` | `knowledge/tools/slpctl.md#1-code` |
| **新增数据库表** | `slpctl gen -t xs_user_profile` | `knowledge/tools/slpctl.md#2-gen` |
| **新增事件处理** | - | `knowledge/patterns/event-extension-guide.md` |
| **新增 CMD 模块** | - | `knowledge/patterns/cmd-module-standard.md` |
| **部署到测试服** | `slpctl ci -w` | `knowledge/patterns/dev-to-dev-deployment.md` |

## 核心禁令（违反将导致任务失败）

| 禁令 | 错误示例 | 正确做法 |
|------|---------|---------|
| **禁止手动编写 API 代码** | 手写 handler/service/dao | 使用 `slpctl code` |
| **禁止手动编辑 DAO/Model** | 改 dao/internal/*.go | 使用 `slpctl gen` 重新生成 |
| **禁止循环 IO** | `for { dao.Find(id) }` | 批量查询 + map 组装 |
| **禁止阻塞主 goroutine** | 同步处理耗时操作 (>100ms) | 异步任务队列 / NSQ 事件 |
| **禁止绕过事件总线** | 直接调用其他模块内部方法 | 通过事件总线解耦 |
| **禁止函数/文件过大** | Handler > 30 行，Service > 100 行 | 按功能拆分，保持精简 |

## 常用命令速查

```bash
slpctl code -api /go/slp/user/profile -desc "用户 profile" -project ./slp-go
slpctl gen -t xs_user_profile
export SLPCTL_JENKINS_TOKEN="<your_jenkins_token>"
slpctl ci -w
./check.sh ./app/service/
./capture.sh "循环 IO" -t anti -f ./file.go -d "N+1 查询问题"
```

## PR Review 流程速查

```
PR 解读/分析:
  1. gh pr view <number> → 获取 PR 元信息
  2. gh pr diff <number> --stat → 变更范围
  3. 按目录重要性分层阅读（核心业务优先，生成物排除）
  4. 反向沉淀开发文档

PR 创建:
  1. 代码审查通过（code-reviewer agent）
  2. git push origin <功能分支>
  3. gh pr create → 创建 PR
```

## PR / Diff 降噪（省 Token）

**推荐顺序**：
1. 先看范围：`gh pr diff --name-only` + `gh pr diff --stat`
2. 再看关键信息：优先只看 Go/核心业务目录
3. 最后才看完整 patch：只对"关键文件"展开全文 diff

**排除建议**：
- 依赖/锁文件：`go.sum`、`package-lock.json`、`yarn.lock`
- 生成物：`**/*.pb.go`、`**/*.gen.*`、`generated/**`
- 三方/构建：`vendor/**`、`node_modules/**`、`dist/**`
- 资源/二进制：`**/*.{png,jpg,jpeg,gif,svg,ico,webp,pdf,zip}`

## 项目知识库导航

| 项目 | 入口文档 |
|------|---------|
| **slp-go** | `knowledge/projects/slp-go/01-structure.md` |
| **slp-room** | `knowledge/projects/slp-room/01-structure.md` |
| **slp-starship** | `knowledge/projects/slp-starship/01-structure.md` |
| **slp-common-rpc** | `knowledge/projects/slp-common-rpc/CORE_LEARNING.md` |

## 文档更新清单

| 变更类型 | 更新文档 |
|----------|---------|
| 新增 API | `knowledge/projects/<project>/04-api.md` |
| 新增 Service | `knowledge/projects/<project>/05-service.md` |
| 新增事件 | `knowledge/projects/<project>/09-event-capabilities.md` |
| 发现新模式 | `knowledge/patterns/` |
| 发现反模式 | `knowledge/anti-patterns/` |
