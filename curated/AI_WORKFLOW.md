# AI 新需求开发流程

> 当 AI 开始新需求开发时，必须遵循此流程以确保与现有知识体系对齐

**版本**: 1.0 | **最后更新**: 2026-04-06

---

## 🎯 流程概览

```
┌─────────────────────────────────────────────────────────────┐
│ 阶段 0：创建功能分支                                          │
│    → 检查已有分支 / 从 master 拉取 / 禁止直接在 master 开发    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 1：需求分析阶段                                          │
│    → 确定需求类型（API/事件/CMD/DB）                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 2：知识检索阶段                                          │
│    → 阅读 QUICK_REFERENCE.md                                 │
│    → 根据类型查阅对应文档                                    │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 3：方案设计阶段                                          │
│    → 参考现有模式和案例                                      │
│    → 输出设计方案                                            │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 4：实施开发阶段                                          │
│    → 按复杂度触发 sub-agent 编排                              │
│    → 使用 slpctl 工具生成代码                                │
│    → 遵循项目规范编写                                        │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 5：合入与部署                                            │
│    → 代码审查（code-reviewer agent）                          │
│    → PR 合入 master → 触发 Jenkins 构建                       │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ 阶段 6：知识沉淀阶段                                          │
│    → 更新相关文档                                            │
│    → 记录新模式/反模式                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 步骤详解

### 步骤 0：创建功能分支

**任务**: 确认或创建功能分支，禁止在 master 上直接开发

**判断逻辑**:

```
用户是否指定了功能分支？
  ├─ 是 → 切换到该分支（git checkout <分支名> && git pull）
  └─ 否 → 搜索相关分支（git branch -a | grep hu/）
          ├─ 找到已有分支 → 询问用户是否使用
          └─ 无相关分支 → 从 master 创建新分支
```

**创建新分支流程**:

```bash
# 1. 切换到 master 分支
git checkout master

# 2. 拉取最新代码
git pull origin master

# 3. 创建新功能分支（以需求名称命名）
git checkout -b hu/<需求名称>

# 4. 推送新分支到远程
git push -u origin hu/<需求名称>
```

**⚠️ 禁令**:
- ❌ 禁止在 master 分支直接开发 — 必须从 master 创建功能分支
- ❌ 禁止在功能分支以外的分支开发 — 所有改动在功能分支完成
- PR 目标分支为 master — 从 master 拉分支，开发完 PR 回 master

**输出**: 已切换至正确的功能分支

---

### 步骤 1：需求分析

**任务**: 确定需求类型和所属项目

**问题清单**：
1. 这个需求属于哪个项目？（slp-go / slp-room / slp-starship / slp-common-rpc）
2. 需求类型是什么？
   - [ ] 新增 API 接口
   - [ ] 新增数据库表
   - [ ] 新增事件处理
   - [ ] 新增 CMD 模块
   - [ ] 修改现有功能

**输出**: 需求类型判断

---

### 步骤 2：知识检索

**必读文档**：以 `QUICK_REFERENCE.md` 为唯一入口，按其中“必读文档（按顺序）”完成阅读。

```bash
# 1. 入口 - 统一必读清单
cat QUICK_REFERENCE.md

# 2. 总入口 - 了解整体结构与使用方式
cat knowledge/USER_GUIDE.md

# 3. 根据需求类型查阅
# API 开发 → tools/slpctl.md#1-code
# 数据库表 → tools/slpctl.md#2-gen
# 事件处理 → knowledge/patterns/event-extension-guide.md
# CMD 模块 → knowledge/patterns/cmd-module-standard.md

# 4. 项目特定知识
cat knowledge/projects/<project>/01-structure.md
cat knowledge/projects/<project>/02-architecture.md
cat knowledge/projects/<project>/09-event-capabilities.md
```

**检查清单**：
- [ ] 已阅读 `QUICK_REFERENCE.md` 并按清单完成必读文档
- [ ] 已阅读 `knowledge/USER_GUIDE.md`
- [ ] 已确定项目目录
- [ ] 已查阅工具文档
- [ ] 已检查是否有类似功能的参考案例

---

### 步骤 3：方案设计

**slpctl 能力前置查询**（设计前先确认）：

| 需求涉及 | 先执行 | 基于生成结果设计方案 |
|----------|--------|-------------------|
| 新 API | `slpctl code -api /go/slp/<service>/<action>` | 生成骨架后只需填充 Service 逻辑，不用设计 Handler/Router |
| 新表/字段变更 | `slpctl gen -t <表名>` | 使用生成的 DAO 方法（Find/FindBatch/Where/All），不用设计 DAO 接口 |
| 新事件 | 查 `event-extension-guide.md` | 按现有 Topic/Cmd 模型设计 |

**⚠️ 重要**: 设计方案必须基于 slpctl 能生成的能力来推演，而不是先手写再让工具覆盖。先查能生成什么，再设计方案，最后实现。

**参考模式**：

| 需求类型 | 参考文档 | 检查点 |
|----------|---------|--------|
| API | `04-api.md` | 路由命名、Handler 命名、Service 命名 |
| Service | `05-service.md` | 分层、接口定义 |
| DAO | `06-dao.md` | 表名、字段映射 |
| 事件 | `event-extension-guide.md` | Topic、Cmd、消费者位置 |
| CMD | `cmd-module-standard.md` | 目录结构、入口文件 |

**反模式检查**：
```bash
# 检查是否有相关反模式
grep -r "N+1" knowledge/anti-patterns/
grep -r "循环.*IO" knowledge/anti-patterns/
```

**输出**: 设计方案（包含文件位置、命名、关键代码结构、slpctl 生成命令）

---

### 步骤 4：实施开发

**Sub-agent 复杂度分级**：

| 复杂度 | 触发条件 | 编排方式 | 示例 |
|--------|---------|---------|------|
| **简单**（单文件，<50行） | 单文件改动，逻辑明确 | 直接写，不用 sub-agent | 加个字段、修个 bug |
| **中等**（多文件，单一项目） | 多文件，但限于单一项目 | 用 Explore agent 做调研，然后直接写 | 新增一个 API + Service |
| **复杂**（跨项目 / 架构改动） | 涉及多项目或架构级重构 | Plan → Explore → general-purpose → code-reviewer | 369 跨项目改造 |

**编排流程**:

```
简单任务:  直接编写代码
                  ↓
中等任务:  Explore（调研）→ 编写代码 → code-reviewer（审查）
                  ↓
复杂任务:  Plan（设计方案）→ Explore（调研）→ general-purpose（实现）→ code-reviewer（审查）
```

**工具使用**：

```bash
# API 开发
slpctl code -api /go/slp/<service>/<action> -project ./<project>

# 数据库表
slpctl gen -t <table_name> -d <database>

# 构建部署
slpctl ci -w
```

**代码检查**：
```bash
# 运行代码检查
./check.sh ./app/service/<new-service>/
```

**检查清单**：
- [ ] 已按复杂度分级选择合适的 sub-agent 编排
- [ ] 使用工具生成代码（非手写）
- [ ] 命名符合规范
- [ ] 无 N+1 查询
- [ ] 无阻塞主 goroutine
- [ ] 通过代码检查

---

### 步骤 5：PR 合入与部署

**代码审查**：
- 实现完成后，启动 `code-reviewer` agent 进行审查
- 审查维度：代码正确性、项目规范、性能影响、安全考量
- 修复 reviewer 提出的问题

**创建 PR 并合入 master**：

```bash
# 1. 确认功能分支开发完成
git status  # 确保没有未提交的修改

# 2. 推送功能分支到远程
git push origin hu/<需求名称>

# 3. 创建 PR，目标分支为 master
gh pr create --base master --head hu/<需求名称> --title "<标题>" --body "<描述>"

# 4. PR 审查通过后，合入 master
gh pr merge <PR 号> --merge
```

**部署到测试服务器**：

```bash
# 触发 Jenkins 构建并等待完成
slpctl ci -w
```

**检查清单**：
- [ ] 代码审查通过
- [ ] 所有提交已推送到远程
- [ ] 合入 master 无冲突
- [ ] Jenkins 构建 SUCCESS
- [ ] 测试服务验证通过

---

### 步骤 6：知识沉淀

**更新文档**：

| 变更类型 | 更新文档 |
|----------|---------|
| 新增 API | `knowledge/projects/<project>/04-api.md` |
| 新增 Service | `knowledge/projects/<project>/05-service.md` |
| 新增事件 | `knowledge/projects/<project>/09-event-capabilities.md` |
| 发现新模式 | `knowledge/patterns/` |
| 发现反模式 | `knowledge/anti-patterns/` |

**输出**: 更新后的文档

---

## 🔗 快速参考

### 核心文档路径

```
knowledge/
├── USER_GUIDE.md              # 总入口
├── tools/
│   └── slpctl.md              # 工具参考（含 ci 命令）
├── patterns/
│   ├── event-extension-guide.md
│   ├── nsq-usage.md
│   └── cmd-module-standard.md
└── projects/
    ├── slp-go/
    ├── slp-room/
    ├── slp-starship/
    └── slp-common-rpc/
```

### 常用命令

```bash
# 查看文档
cat knowledge/USER_GUIDE.md
cat knowledge/tools/slpctl.md

# 生成代码
slpctl code -api /go/slp/user/getInfo
slpctl gen -t xs_user_profile
slpctl ci -w

# 检查代码
./check.sh ./app/service/
```

---

## ⚠️ 重要提醒

**开发前必须**：
1. 阅读 `knowledge/USER_GUIDE.md`
2. 确定需求类型和所属项目
3. 查阅对应模式和案例

**禁止行为**：
- ❌ 手写 API 代码（必须用 slpctl code）
- ❌ 循环中 IO 操作（使用批量查询）
- ❌ 阻塞主 goroutine（使用异步）
- ❌ 绕过事件总线（使用事件解耦）

**必须沉淀**：
- ✅ 新 API 更新到 04-api.md
- ✅ 新事件更新到 09-event-capabilities.md
- ✅ 新模式/反模式记录到 patterns/ 或 anti-patterns/

---

**AI 行为约束**:
- 开始任何 coding 任务前，必须先执行步骤 0（创建功能分支）和步骤 2（知识检索），否则禁止编写代码。
- Sub-agent 由 AI 自主触发，用户无需手动指定。复杂度分级为默认策略，用户可随时覆盖。
- 所有编码任务在步骤 3（方案设计）中必须先查询 slpctl 能生成什么，基于生成结果设计方案。不要先想好怎么写再去找工具覆盖。
