# 跨项目业务知识库

> 涉及多个项目协作的业务知识统一存放在此

## 目录结构

```
knowledge/cross-projects/
├── README.md                          # 本索引
├── 369-recharge/                      # 369 元观光团业务
│   ├── overview.md                    # 业务全景图
│   ├── slp-room.md                    # slp-room 项目职责
│   └── slp-go.md                      # slp-go 项目职责
├── buye-payment/                      # 不夜支付
├── chatroom/                          # 聊天室房间类型拓展
│   ├── room-type-development.md       # 大哥房实战案例
│   ├── room-type-concept.md           # 房间类型拓展概念
│   ├── room-type-work-plan.md         # 按工作日拆分的计划
│   └── room-chat-flow-analysis.md     # 公屏消息发送流转分析
├── fly-chess/                         # 飞行棋游戏功能
│   └── overview.md                    # 业务全景图（综合PR分析）
├── prayer-activity/                   # 祈福抽奖活动（活动模板 2）
│   ├── 01-overview.md                 # 业务全景图（跨项目流程）
│   ├── 02-sql-config.md               # 活动配置 SQL
│   └── 09-prayer-draw-flow.canvas     # 抽奖流程图
├── decorate-commodity-use/            # 装扮类物品使用转发
│   ├── overview.md                    # 业务全景图
│   ├── slp-php.md                     # PHP 侧实现细节
│   └── slp-go.md                      # slp-go 侧实现细节
└── <new-business>/                    # 新增跨项目业务
    ├── overview.md
    ├── <project-a>.md
    └── <project-b>.md
```

## 跨项目业务列表

| 业务名称 | 涉及项目 | 主责项目 | 说明 |
|----------|----------|----------|------|
| **369 元观光团** | slp-room, slp-go | slp-go | 充值档位 + 签到领奖活动 |
| **信息流分配** | slp-room, slp-go | slp-room | 房间信息流推荐 |
| **星舰房间** | slp-starship, slp-room, slp-go | slp-starship | 星舰房间系统 |
| **不夜支付** | slp-php, slp-ee-config | slp-php | 小程序支付系统 |
| **聊天室房间类型** | slp-room, slp-go, slp-common-rpc | slp-go | 房间类型拓展（大哥房、星舰房） |
| **飞行棋游戏** | slp-room, slp-gateway, slp-go, slp-php | slp-room | 飞行棋游戏功能 |
| **祈福抽奖活动** | slp-starship, slp-go | slp-starship | 活动模板 2，概率抽奖玩法，4轮配置见 `02-sql-config.md` |
| **装扮类物品使用** | slp-php, slp-go | slp-go | PHP 扣库存后转发到 slp-go 处理有效期累加 |

## 新增跨项目业务流程

1. 在 `cross-projects/` 下创建业务目录：`cross-projects/<business-name>/`
2. 创建 `01-overview.md` - 业务全景图（跨项目流程、职责分工、数据表结构）
3. 按项目创建分册：`<project-name>.md` - 该项目内的实现细节
4. 如有配置数据，创建 `02-sql-config.md` - SQL 配置脚本
5. 如有流程图，创建 `<NN>-<flow-name>.canvas` - 流程图（JSON Canvas格式）
6. 更新本索引文件

---

## 知识库目录规范

| 知识类型 | 存放位置 | 说明 |
|----------|----------|------|
| **单项目知识** | `projects/<project>/` | 仅涉及一个项目的知识 |
| **跨项目知识** | `cross-projects/<business>/` | 涉及多个项目协作的知识 |
| **通用模式** | `patterns/` | 跨项目通用的设计模式 |
| **通用反模式** | `anti-patterns/` | 跨项目通用的常见错误 |

---

## 跨项目业务判断标准

当满足以下任一条件时，应使用 `cross-projects/` 目录：

| 条件 | 示例 |
|------|------|
| 涉及多个项目协作 | 祈福抽奖：slp-starship + slp-go |
| 数据表跨项目共享 | 支付系统：slp-php + slp-ee-config |
| RPC 调用跨服务 | 房间类型：slp-room + slp-go + slp-common-rpc |
| 事件总线跨模块 | 飞行棋：slp-room + slp-gateway + slp-php |

**注意**：祈福抽奖活动虽然核心逻辑在 slp-starship，但奖励发放依赖 slp-go 的 RPC 服务，因此属于跨项目知识。

## 文档结构规范

### overview.md (业务全景图)

```markdown
# <业务名称>

## 业务全景图
- 跨项目架构图
- 数据流向图

## 项目职责分工
| 项目 | 职责 | 核心模块 |
|------|------|----------|
| slp-room | ... | ... |
| slp-go | ... | ... |

## 核心流程（跨项目）
1. 流程图
2. 事件总线机制
3. RPC 调用关系

## 数据表结构
- 共享数据表
- 各项目私有表

## 配置管理
- 各项目配置项

## 问题排查
- 跨问题排查步骤
```

### <project-name>.md (项目分册)

```markdown
# <业务名称> - <项目名>视角

## 项目内职责
- 模块列表
- 文件路径

## 核心代码
- 关键函数
- 配置常量

## 依赖的外部服务
- RPC 调用
- 事件订阅

## 本地测试
- 测试方法
```

## 引用关系

```
knowledge/
├── cross-projects/369-recharge/overview.md
│   ├── 引用 → projects/slp-go/08-business-369-recharge.md
│   └── 引用 → projects/slp-room/xx-business-369.md
│
├── cross-projects/chatroom/
│   ├── room-type-development.md → 引用 patterns/event-extension-guide.md
│   ├── room-type-development.md → 引用 patterns/cmd-module-standard.md
│   └── room-type-concept.md → 引用 room-type-development.md
│
├── projects/slp-go/
│   └── 01-structure.md (单项目知识)
│
└── projects/slp-room/
    └── xx-structure.md (单项目知识)
```

---

**版本**: 1.0 | **更新**: 2026-04-05
