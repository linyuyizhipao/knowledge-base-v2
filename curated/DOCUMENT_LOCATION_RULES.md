# 知识库文档存放规则

> **核心原则**：先判断知识类型，再选择存放位置  
> **最后更新**: 2026-04-13

---

## 目录结构概览

```
knowledge/
├── projects/                      # 单项目知识
│   ├── slp-go/                    # slp-go 项目
│   ├── slp-room/                  # slp-room 项目
│   ├── slp-starship/              # slp-starship 项目
│   └── slp-php/                   # slp-php 项目
├── cross-projects/                # 跨项目知识
│   ├── chatroom/                  # 聊天室房间类型
│   ├── fly-chess/                 # 飞行棋游戏
│   └── prayer-activity/           # 祈福抽奖活动
├── patterns/                      # 通用模式
│   ├── event-extension-guide.md   # 事件拓展指南
│   └── business-module-standard.md
├── anti-patterns/                 # 反模式
│   ├── n-plus-one-query.md
│   └── blocking-main-goroutine.md
└── tools/                         # 工具文档
    ├── slpctl.md                  # 完整命令参考
    └── slpctl-usage-guide.md      # 开发工作流
```

---

## 目录选择规则

### 1. projects/ - 单项目知识

**存放条件**（满足任一即可）：
- 仅涉及单个项目的目录结构
- 仅涉及单个项目的模块设计
- 仅涉及单个项目的 API 规范

**示例**：
| 文档 | 路径 | 说明 |
|------|------|------|
| slp-go 项目结构 | `projects/slp-go/01-structure.md` | 仅描述 slp-go |
| slp-room 事件能力 | `projects/slp-room/01-event-capabilities.md` | 仅描述 slp-room |

**禁止场景**：
- ❌ 涉及多个项目的交互流程
- ❌ 跨项目的 RPC 调用关系
- ❌ 需要多个项目协作的业务

---

### 2. cross-projects/ - 跨项目知识

**存放条件**（满足任一即应使用）：
| 条件 | 说明 | 示例 |
|------|------|------|
| 涉及多个项目协作 | 知识需要多个项目共同理解 | 祈福抽奖：slp-starship + slp-go |
| 数据表跨项目共享 | 同一张表被多个项目读写 | 支付系统：slp-php + slp-ee-config |
| RPC 调用跨服务 | 项目 A 调用项目 B 的 RPC | 房间类型：slp-room + slp-go |
| 事件总线跨模块 | 多个项目订阅同一 Topic | 飞行棋：slp-room + slp-gateway |

**示例**：
| 文档 | 路径 | 说明 |
|------|------|------|
| 祈福抽奖活动 | `cross-projects/prayer-activity/01-overview.md` | slp-starship + slp-go |
| 飞行棋游戏 | `cross-projects/fly-chess/overview.md` | 多项目协作 |
| 聊天室房间类型 | `cross-projects/chatroom/room-type-development.md` | 多个项目 |

**目录命名规则**：
- 使用业务名称作为目录名（如 `prayer-activity/`）
- 核心文档使用 `01-overview.md`
- 项目分册使用 `<project-name>.md`

---

### 3. patterns/ - 通用模式

**存放条件**：
- 跨项目通用的设计模式
- 多个业务共享的实现方法
- 可复用的架构方案

**示例**：
| 文档 | 说明 |
|------|------|
| `patterns/event-extension-guide.md` | 事件拓展指南（含完整示例） |
| `patterns/business-module-standard.md` | 业务模块标准 |

---

### 4. anti-patterns/ - 反模式

**存放条件**：
- 跨项目的常见错误
- 多个项目都踩过的坑
- 需要警示的反模式

**示例**：
| 文档 | 说明 |
|------|------|
| `anti-patterns/n-plus-one-query.md` | N+1 查询问题 |
| `anti-patterns/blocking-main-goroutine.md` | 阻塞主协程 |

---

## 快速决策表

```
┌─────────────────────────────────────────────────────────┐
│  知识涉及范围？                                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  是单个项目 → projects/<project>/                      │
│                                                         │
│  涉及多个项目 → cross-projects/<business>/            │
│                                                         │
│  通用设计模式/方法 → patterns/                         │
│                                                         │
│  常见错误/坑 → anti-patterns/                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 原则说明

### 为什么要有这个规则？

1. **便于检索**：用户知道去哪里找相关知识
2. **避免重复**：明确的归属减少文档重复
3. **易于维护**：清晰的边界便于后续更新

### AI 协作规范

**路径引用规范**（所有 AI 必须遵循）：
```markdown
✅ 正确：使用环境变量或相对路径
- `${HARNESS_HOME}/knowledge/cross-projects/chatroom/`
- `${HARNESS_HOME}/knowledge/patterns/event-extension-guide.md`
- [房间类型开发](${HARNESS_HOME}/knowledge/cross-projects/chatroom/room-type-development.md)

❌ 错误：硬编码全路径
- `/Users/hugh/project/harness/slp-harness/knowledge/...`
- `~/project/harness/slp-harness/...`
```

**AI 分工原则**：
- ✅ AI 负责：写内容、遵循格式、搜索/读取文档、写完告知路径
- ❌ AI 不负责：创建目录结构、移动/重组文件、添加双向链接/标签

**其他 AI 快速上手**（Trae、Claude Code 等）：
> "请先阅读 ${HARNESS_HOME}/knowledge/DOCUMENT_LOCATION_RULES.md 和 ${HARNESS_HOME}/CLAUDE.md，遵循其中的协作规范"

核心注意事项：
1. 路径必须用 `${HARNESS_HOME}` 变量
2. 写完文档必须告知路径
3. 不确定目录归属时先查本文档
4. 不要擅自改动目录结构

### 如果不确定怎么办？

**判断标准**：想象一个新加入项目的开发者的视角

- 如果他需要 **同时阅读多个项目** 才能理解这个知识 → `cross-projects/`
- 如果他只需要查看 **单个项目文档** 就能理解 → `projects/`

---

## 单需求单文件原则

**禁令：同一需求的知识沉淀、技术设计、实施计划必须聚合在一个文件内，禁止分散到多处。**

| 错误做法 | 正确做法 |
|----------|----------|
| 踩坑在 `projects/`、设计在 `cross-projects/design.md`、计划在 `cross-projects/implementation-plan.md` | 全部内容合并在一个文件，按 `projects/` 或 `cross-projects/` 的归属规则选定**唯一路径** |
| 目录下放 `design.md` + `plan.md` + `knowledge.md` 三件套 | 一个需求一个 `.md`，用章节标题区分（背景 / 方案 / 踩坑 / 计划 / checklist） |

**判定标准**：如果读者只打开一个文件就能理解这个需求的**全部上下文**（背景、方案、踩坑、计划），就是合格的。

**如何执行**：
1. 先按"快速决策表"选定归属目录（`projects/` 或 `cross-projects/`）
2. 在该目录下**只建一个文件**
3. 文件内用 `##` 二级标题分区：背景、架构、踩坑、实施计划、验收清单、文件索引
4. 实施计划中的长 SQL/代码模板可以内联，不必另起文件

---

## 历史案例

| 案例 | 原位置 | 新位置 | 说明 |
|------|--------|--------|------|
| 祈福抽奖活动 | ~~projects/slp-starship/~~ | `cross-projects/prayer-activity/` | 涉及 slp-go 的 RPC 调用 |
| 聊天室房间类型 | patterns/ | `cross-projects/chatroom/` | 明确的跨项目协作 |
| 飞行棋游戏 | patterns/ | `cross-projects/fly-chess/` | 涉及 4 个项目 |
| 农场 appid 隔离 | ~~projects/ + cross-projects/ 散 3 个文件~~ | `projects/slp-starship/02-farm-appid-isolation.md` | 合并为单文件 |

---

**版本**: 1.0 | **创建**: 2026-04-13
