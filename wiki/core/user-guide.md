---
id: USER_GUIDE
label: 使用指南
type: guide
source: curated/USER_GUIDE.md
sources: [curated/USER_GUIDE.md]
role: 导航
compiled: 2026-04-29
source_hash: e667e5c902f59a21756877cf3e472c39
tags: [导航, 入口, 学习路径, 开发流程]
links_to:
  - CODING_STANDARDS
  - tools/slpctl-usage-guide
  - patterns/slp-business-development-standard
  - patterns/event-extension-guide
  - patterns/nsq-usage
  - patterns/dev-to-dev-deployment
  - projects/slp-go/01-structure
  - projects/slp-room/01-structure
  - projects/slp-starship/01-structure
---

# 使用指南

> 知识库导航与使用场景速查

## 目录结构

```
knowledge/
├── projects/          # 项目知识（slp-go, slp-room, slp-starship）
├── patterns/          # 开发规范（跨项目最佳实践）
├── tools/             # 工具文档（slpctl, gh-pr）
├── cross-projects/    # 跨项目业务（369, 口令等）
└── anti-patterns/     # 反模式（避坑指南）
```

## 四大场景

| 场景 | 入口文档 |
|------|---------|
| 学习新项目 | `projects/<name>/01-structure.md` |
| 新需求开发 | [[patterns/slp-business-development-standard]] |
| 遇到问题 | `anti-patterns/` → `patterns/` |
| PR 解读 | [[tools/gh-pr-analysis]] |

## 开发任务快速入口

| 任务类型 | 参考文档 |
|----------|---------|
| API 接口 | [[tools/slpctl-usage-guide]] → code 命令 |
| 数据库表 | [[tools/slpctl-usage-guide]] → gen 命令 |
| 事件处理 | [[patterns/event-extension-guide]] |
| CMD 模块 | [[patterns/cmd-module-standard]] |
| 部署流程 | [[patterns/dev-to-dev-deployment]] |

## 项目学习路径

| 项目 | 入口 |
|------|------|
| slp-go | [[projects/slp-go/01-structure]] |
| slp-room | [[projects/slp-room/01-structure]] |
| slp-starship | [[projects/slp-starship/01-structure]] |

## 工具速查

```bash
# API 生成
slpctl code -api /go/slp/user/getInfo -project ./slp-go

# 数据库表生成
slpctl gen -t xs_user_profile

# Jenkins 构建
slpctl ci -w
```

## 相关知识

- [[CODING_STANDARDS]] - 核心禁令
- [[patterns/slp-business-development-standard]] - 业务开发规范
- [[patterns/event-extension-guide]] - 事件开发指南
- [[tools/slpctl-usage-guide]] - slpctl详解

---

### 场景 2：新需求开发

**步骤**：

```
1. 确定需求类型
   │
   ├─ 完整业务流程 → patterns/slp-business-development-standard.md（推荐）
   ├─ API 接口 → tools/slpctl.md → code 命令
   ├─ 数据库表 → tools/slpctl.md → gen 命令
   ├─ 事件处理 → patterns/event-extension-guide.md
   └─ CMD 模块 → patterns/cmd-module-standard.md

2. 参考对应项目的业务文档
   └─ projects/<project>/08-business-*.md

3. 开发完成后更新文档
   └─ 更新对应项目的 09-event-capabilities.md
```

**快速入口**：
- [**SLP 业务开发规范（全流程）**](./patterns/slp-business-development-standard.md) ⭐
- [API 开发流程](./tools/slpctl.md#1-code---api-代码生成)
- [数据库开发](./tools/slpctl.md#2-gen---数据库表代码生成)
- [事件开发](./patterns/event-extension-guide.md)
- [部署流程](./patterns/dev-to-dev-deployment.md)

---

### 场景 3：遇到问题

**步骤**：
1. 检查 `anti-patterns/` - 是否已有记录
2. 检查 `patterns/` - 是否有最佳实践
3. 检查项目特有的反模式文档
4. 解决后补充记录

**常见问题索引**：
- [N+1 查询问题](./patterns/README.md#批量查询模式)
- [NSQ 使用规范](./patterns/nsq-usage.md)
- [事务使用规范](./patterns/README.md#事务模式)

---

### 场景 5：PR 解读与反向推导开发文档（省 Token）

目标：用最少的信息成本提取“需求是什么/改了什么/为什么这么改/该沉淀到哪里”。

**步骤**：
1. 读 PR 元信息：标题、描述、标签、commit message（优先看意图，不先看 diff）
2. 读变更范围：文件列表 + 变更统计（先确认涉及模块与关键路径）
3. 分层展开 diff：只展开关键文件的 patch；排除 lock/生成物/资源/三方依赖等噪音
4. 反推文档沉淀点：新模式进 `patterns/`，新反模式进 `anti-patterns/`，项目特有改动进 `projects/<project>/`

**参考**：
- 命令参考：[gh-pr-analysis.md](./tools/gh-pr-analysis.md)
- 入口卡片：[QUICK_REFERENCE.md](../QUICK_REFERENCE.md)

---

### 场景 4：添加新项目

**步骤**：
1. 在 `projects/` 下创建目录
2. 复制模板文件（参考 slp-go）
3. 更新 `knowledge/README.md` 索引
4. 按 [学习框架](./patterns/project-learning-framework.md) 填充内容

---

## 三、工具速查

### slpctl 工具

```bash
# API 代码生成
slpctl code -api /go/slp/user/getInfo -project ./slp-go

# 数据库表代码生成
slpctl gen -t xs_user_profile

# Jenkins 构建部署
slpctl ci -w

# 查看完整文档
cat ./tools/slpctl.md
```

### 常用命令

```bash
# 项目统计
find . -name "*.go" | wc -l

# 查找事件处理
grep -r "HandleEventMap" app/service/

# 查找 NSQ 消费者
grep -r "NewNsqWorker" cmd/
```

---

## 四、文档更新原则

### 何时更新

| 触发条件 | 更新位置 |
|----------|---------|
| 新增 API | `projects/<project>/04-api.md` |
| 新增服务 | `projects/<project>/05-service.md` |
| 新增事件 | `projects/<project>/09-event-capabilities.md` |
| 发现反模式 | `anti-patterns/` 或项目反模式文档 |
| 发现新模式 | `patterns/` |

### 更新格式

所有文档使用统一格式：
- 标题：`# 标题`
- 说明：`> 简短说明`
- 版本：`**版本**: 1.0 | **最后更新**: 2026-04-06`
- 内容：使用 Markdown 表格、代码块

---

## 五、核心文档索引

### 入门必读

| 文档 | 说明 |
|------|------|
| [knowledge/README.md](./README.md) | 知识库总索引 |
| [tools/slpctl.md](./tools/slpctl.md) | 命令行工具完整参考 |
| [patterns/project-learning-framework.md](./patterns/project-learning-framework.md) | 项目学习方法论 |

### 开发参考

| 文档 | 说明 |
|------|------|
| [patterns/event-extension-guide.md](./patterns/event-extension-guide.md) | 事件开发总纲 |
| [patterns/nsq-usage.md](./patterns/nsq-usage.md) | NSQ 使用规范 |
| [patterns/cmd-module-standard.md](./patterns/cmd-module-standard.md) | CMD 模块标准 |
| [patterns/dev-to-dev-deployment.md](./patterns/dev-to-dev-deployment.md) | 开发部署流程 |

### 业务参考

| 文档 | 说明 |
|------|------|
| [cross-projects/369-recharge/](./cross-projects/369-recharge/overview.md) | 369 元观光团业务 |

---

## 六、扩展能力检查

### 已支持

- ✅ 多项目独立知识库
- ✅ 跨项目模式沉淀
- ✅ 工具使用文档
- ✅ 业务流程文档
- ✅ 反模式记录
- ✅ 部署流程文档

### 待扩展

- [ ] 新项目模板
- [ ] 自动化文档生成
- [ ] CI/CD 集成检查

---

## 七、维护清单

### 定期清理

- [ ] 删除过时的临时文档
- [ ] 更新版本号和日期
- [ ] 检查死链接

### 持续沉淀

- [ ] 遇到新问题 → 记录
- [ ] 解决新问题 → 沉淀模式
- [ ] 学习新知识 → 整理文档

---

**最后更新**: 2026-04-06
