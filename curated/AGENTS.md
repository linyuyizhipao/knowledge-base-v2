# AI 统一入口

> **所有 AI 工具必读** - Claude / Qoder / Trae / Codex / Cursor / Windsurf
>
> **版本**: 2.0 | **更新**: 2026-04-25

---

## 📍 知识库位置

```
${HARNESS_HOME} = /Users/hugh/project/harness/slp-harness
维护方式: 集中式，所有项目共享，无副本
```

---

## 🤖 AI 入口

**主数据源**: [knowledge/knowledge-graph.json](./knowledge/knowledge-graph.json)

AI 启动时读取该 JSON，包含：
- `nodes`: 所有文档节点 + 路径 + 关联
- `ai_usage_guide`: 按任务类型的必读列表
- `query_shortcuts`: 关键词快速定位

---

## 📁 知识库结构

```
${HARNESS_HOME}/
├── AGENTS.md              ← 本文档（入口）
├── CODING_STANDARDS.md    ← 核心禁令
├── knowledge/
│   ├── INDEX.md           ← 文档索引
│   ├── knowledge-graph.json ← AI 数据源
│   ├── USER_GUIDE.md      ← 使用指南
│   ├── projects/          ← 项目知识
│   ├── cross-projects/    ← 跨项目业务
│   ├── patterns/          ← 通用模式
│   └── tools/             ← 工具文档
```

---

## ⛔ 核心禁令（速查）

| 禁令 | 错误做法 | 正确做法 |
|------|---------|---------|
| 禁止手动写API | 手写 handler/service | `slpctl code` 生成骨架 |
| 禁止循环IO | `for { dao.Find(id) }` | 批量查询 + map |
| 禁止阻塞主goroutine | 同步处理耗时操作 | 异步/NSQ事件 |
| 禁止绕过事件总线 | 直接调用其他模块 | 发布事件解耦 |
| 禁止函数过大 | Handler > 30行 | 按功能拆分 |

**完整规范**: [CODING_STANDARDS.md](./CODING_STANDARDS.md)

---

## 🗂️ 文档存放规则

```
知识涉及几个项目？
    │
    ├── 单个项目 → knowledge/projects/<project>/
    ├── 多个项目 → knowledge/cross-projects/<business>/
    └── 通用方法 → knowledge/patterns/
```

---

## 📝 文档模板

**项目知识**:
```markdown
# <标题>
> 简短说明
**版本**: 1.0 | **更新**: YYYY-MM-DD
## 概述 | ## 核心内容 | ## 相关文档
```

**模式文档**:
```markdown
# <模式名称>
> 解决什么问题
## 问题场景 | ## 解决方案 | ## 代码示例
```

---

## 📋 任务清单

**编码任务**:
- [ ] 先读 `knowledge-graph.json` 的 `ai_usage_guide.dev_task`
- [ ] 新增 API 必须用 `slpctl code` 生成骨架
- [ ] 无循环IO、无阻塞、无绕过事件总线

**写文档任务**:
- [ ] 先读 `knowledge-graph.json` 的 `ai_usage_guide.doc_task`
- [ ] 搜索 INDEX.md 确认无重复
- [ ] 写完更新 INDEX.md

---

**详细内容请查阅 knowledge-graph.json 或对应具体文档**