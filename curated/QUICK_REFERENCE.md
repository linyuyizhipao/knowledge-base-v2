# AI 快速参考卡片

> 开始任何 coding 任务前，必须先完成知识检索
> 
> **🚨 新 AI 会话请先阅读**: [AI_START_HERE.md](./AI_START_HERE.md)

## 🚨 开始前的必读文档（按顺序）

默认只读最小集（避免每次任务启动都把 token 花在“全量导航”上）：

| 文档 | 何时必须读 | 用途 |
|------|------------|------|
| [`CODING_STANDARDS.md`](./CODING_STANDARDS.md) | 任何编码/改动前 | 核心禁令与代码组织规则 |
| [`knowledge/USER_GUIDE.md`](./knowledge/USER_GUIDE.md) | 任何编码/改动前 | 场景导航与文档定位方法 |

按需阅读（只在触发条件出现时读）：

| 触发条件 | 文档 | 用途 |
|----------|------|------|
| 新需求/要走完整流程 | [`AI_WORKFLOW.md`](./AI_WORKFLOW.md) | 5 阶段流程与检查清单 |
| 不知道该去哪里找资料 | [`knowledge/README.md`](./knowledge/README.md) | 知识库总索引 |
| 需要工具命令/PR 分析 | [`knowledge/tools/`](./knowledge/tools/) | slpctl、gh 等工具文档 |
| 进入某个项目做需求 | `knowledge/projects/<project>/` | 项目结构/架构/API/事件能力等 |

---

## 🧭 AI 阅读范围（省 Token）

原则：不做 `$HARNESS_HOME` 全量扫描，只按“需求类型”与“项目”按需读取。

只读入口与知识体系文档：
- 入口：本文件 + `knowledge/` 下的索引/规范/模式/项目文档
- 按需：匹配需求类型的 `knowledge/tools/`、`knowledge/patterns/`、`knowledge/projects/<project>/`

忽略个人配置与非知识内容（示例）：
- `.claudian/`、`.idea/`、`.vscode/`、临时脚本、缓存目录
- `skills/`（全局技能入口在 `~/.claude/skills`，除非用户明确要求调整/创建 skill，否则不读取）

---

## 🧹 何时做 Compact（省 Token）

Compact 的目标：把“已达成共识 + 关键上下文 + 下一步”留下，把长日志/原始 diff/反复讨论清掉。

推荐触发时机：
- 一个任务阶段性结束：完成设计评审、完成一次实现/修复、PR 分析产出文档之后
- 对话开始出现“上下文变长导致抓不住重点”：反复解释同一背景、回答开始偏题、引用错误文件/规则
- 即将切换任务：从 PR 解读切到编码、从一个项目切到另一个项目
- 出现大块噪音输入：长 diff、长日志、长配置/依赖变更等已经被总结过

通用开发节奏（兜底策略）：
- 长任务：每完成 1 个可验收产物（一个接口/一个功能点/一次修复）就 compact 一次
- 无明显阶段边界：每 10-15 轮对话做一次轻量 compact

Compact 输出模板（建议保留到对话里）：
- 目标：一句话说明当前要达成什么
- 结论：已经确定的关键决策/约束（最多 5 条）
- 关键上下文：涉及的项目/目录/核心文件（只列路径与要点，不贴长片段）
- 未决问题：仍需补充的信息（最多 3 条）
- 下一步：接下来 1-3 个可执行动作

---

## 📋 需求类型快速定位

| 需求类型 | 工具命令 | 参考文档 |
|----------|---------|---------|
| **新增 API** | `slpctl code -api /go/slp/user/getInfo` | [knowledge/tools/slpctl.md#1-code](./knowledge/tools/slpctl.md#1-code---api-代码生成) |
| **新增数据库表** | `slpctl gen -t xs_user_profile` | [knowledge/tools/slpctl.md#2-gen](./knowledge/tools/slpctl.md#2-gen---数据库表代码生成) |
| **新增事件处理** | - | [knowledge/patterns/event-extension-guide.md](./knowledge/patterns/event-extension-guide.md) |
| **新增 CMD 模块** | - | [knowledge/patterns/cmd-module-standard.md](./knowledge/patterns/cmd-module-standard.md) |
| **部署到测试服** | `slpctl ci -w` | [knowledge/patterns/dev-to-dev-deployment.md](./knowledge/patterns/dev-to-dev-deployment.md) |

---

## ⚠️ 核心禁令（违反将导致任务失败）

| 禁令 | 错误示例 | 正确做法 |
|------|---------|---------|
| **禁止手动编写 API 代码** | 手写 handler/service/dao | 使用 `slpctl code` 或 `make generate` |
| **禁止循环 IO** | `for { dao.Find(id) }` | 批量查询 + map 组装 |
| **禁止阻塞主 goroutine** | 同步处理耗时操作 (>100ms) | 异步任务队列 / NSQ 事件 |
| **禁止绕过事件总线** | 直接调用其他模块内部方法 | 通过事件总线解耦 |
| **禁止函数/文件过大** | Handler > 30 行，Service > 100 行 | 按功能拆分，保持精简 |
| **禁止常量分散** | 常量分散在各个文件中 | 统一在 `consts/` 或模块 `const.go` |

---

## 🔧 常用命令速查

```bash
# API 代码生成
slpctl code -api /go/slp/user/profile -desc "用户 profile" -project ./slp-go

# 数据库代码生成
slpctl gen -t xs_user_profile

# Jenkins 构建部署
export SLPCTL_JENKINS_TOKEN="<your_jenkins_token>"
slpctl ci -w

# 代码检查
./check.sh ./app/service/

# 问题捕获
./capture.sh "循环 IO" -t anti -f ./file.go -d "N+1 查询问题"
```

---

## 🔍 PR / Diff 降噪（省 Token）

推荐顺序（从低成本到高成本）：
1. 先看范围：`gh pr diff --name-only` + `gh pr diff --stat`
2. 再看关键信息：优先只看 Go/核心业务目录，先排除 lock/生成物/资源文件
3. 最后才看完整 patch：只对“关键文件”展开全文 diff

排除建议（按仓库情况增删）：
- 依赖/锁文件：`go.sum`、`package-lock.json`、`yarn.lock`、`pnpm-lock.yaml`
- 生成物：`**/*.pb.go`、`**/*.gen.*`、`generated/**`
- 三方/构建：`vendor/**`、`node_modules/**`、`dist/**`、`build/**`
- 资源/二进制：`**/*.{png,jpg,jpeg,gif,svg,ico,webp,pdf,zip,tar,gz}`

---

## 🗂️ 项目知识库导航

| 项目                 | 入口文档                                                                                                       |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| **slp-go**         | [knowledge/projects/slp-go/01-structure.md](./knowledge/projects/slp-go/01-structure.md)                   |
| **slp-room**       | [knowledge/projects/slp-room/01-structure.md](./knowledge/projects/slp-room/01-structure.md)               |
| **slp-starship**   | [knowledge/projects/slp-starship/01-structure.md](./knowledge/projects/slp-starship/01-structure.md)       |
| **slp-common-rpc** | [knowledge/projects/slp-common-rpc/CORE_LEARNING.md](./knowledge/projects/slp-common-rpc/CORE_LEARNING.md) |

---

## 🧠 开发流程（7 阶段）

```
阶段0：创建功能分支（禁止在 master 直接开发）
         ↓
阶段1：需求分析 → 确定项目/类型
         ↓
阶段2：知识检索 → 阅读 QUICK_REFERENCE.md + 类型文档
         ↓
阶段3：方案设计 → 参考现有模式/案例
         ↓
阶段4：实施开发 → 按复杂度触发 sub-agent + 使用 slpctl
         ↓
阶段5：合入与部署 → 代码审查 + PR 合入 master + Jenkins 构建
         ↓
阶段6：知识沉淀 → 更新对应文档
```

**⚠️ 重要**: 未完成阶段 2（知识检索）前，禁止编写代码。

---

---

## 🤖 Sub-agent 快速选择

AI 自主触发，用户无需手动指定。复杂度分级如下：

| 复杂度 | 编排 | 示例 |
|--------|------|------|
| **简单**（单文件，<50行） | 直接写 | 加字段、修 bug |
| **中等**（多文件，单一项目） | Explore → 编写 → code-reviewer | 新增 API + Service |
| **复杂**（跨项目/架构改动） | Plan → Explore → 实现 → code-reviewer | 跨项目改造 |

**用户覆盖**: 可以说"直接用 sub-agent"强制走复杂流程，或"不用 sub-agent"强制直接写。

**详情**: [`patterns/sub-agent-orchestration.md`](./patterns/sub-agent-orchestration.md)

---

## 📝 PR Review 流程速查

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

**详情**: [`tools/gh-pr-analysis.md`](./tools/gh-pr-analysis.md)

---

## 📝 文档更新清单

| 变更类型 | 更新文档 |
|----------|---------|
| 新增 API | `knowledge/projects/<project>/04-api.md` |
| 新增 Service | `knowledge/projects/<project>/05-service.md` |
| 新增事件 | `knowledge/projects/<project>/09-event-capabilities.md` |
| 发现新模式 | `knowledge/patterns/` |
| 发现反模式 | `knowledge/anti-patterns/` |

---

**版本**: 1.0 | **最后更新**: 2026-04-06
