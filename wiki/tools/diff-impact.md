---
id: tools/diff-impact
type: tool
source_file: scripts/diff-impact.py
sources: [scripts/diff-impact.py]
compiled: 2026-05-02
tags: [python, go, git, code-analysis, dev-tool]
links_to:
  - tools/slpctl-usage-guide
  - core/coding-standards
  - projects/slp-go/01-structure
---

# diff-impact.py - 代码变更影响分析

> Python 工具，分析 Go 项目代码变更对服务的影响范围

## 功能概述

分析当前分支相对于 master 的代码变更，追踪引用传播，找出需要重启的服务。

**输出**：JSON 格式，包含变更文件、变更元素、影响服务、重启命令。

## 使用方法

```bash
# 在 Go 项目目录下运行（slp-go/slp-room/slp-starship）
python scripts/diff-impact.py

# 输出示例
{
  "changed_files": ["app/domain/rank/base.go"],
  "affected_services": {
    "http": true,
    "rpc": ["user_rank"],
    "cmd": ["hour_rank"]
  },
  "restart_commands": [
    "make build && ./bin/http",
    "make build && ./bin/rpc --name=user_rank"
  ]
}
```

## 核心机制

### 1. 私有函数传播

**关键逻辑**：私有函数变更 → 找同包内调用它的公开函数 → 追踪公开函数的调用者

```
私有函数（如 commonHandle）
    ↓ 被 HandleConsumePackage 调用
公开函数（HandleConsumePackage）
    ↓ 被 common_gift_send CMD 使用
服务入口（common_gift_send）
    ↓
标记该服务需要重启
```

### 2. 实例调用检测

检测 `.MethodName()` 模式的实例调用：

```
configRank.GetRank 方法变更
    ↓ rankScene.GetRank() 实例调用
user_rank RPC（rankScene 来自 rank.RankedMap）
```

**实现**：搜索 `.MethodName(` 调用，验证调用者是否导入了方法所在包。

### 3. BFS 引用追踪

```
变更元素 → grep 找引用文件 → 判断服务类型
    ↓ 非服务入口
继续追踪该文件的公开函数 → grep 找引用 → ...
    ↓ 遇到服务入口
停止传播，标记服务
```

## 服务分类规则

| 路径模式 | 服务类型 | 示例 |
|----------|----------|------|
| `app/api/`, `app/handler/` | HTTP | `./bin/http` |
| `rpc/server/internal/<name>/` | RPC | `./bin/rpc --name=<name>` |
| `cmd/internal/<name>/` | CMD | `./bin/cmd --name=<name>` |
| `library/`, `app/consts/`, `app/dao/` | library | 影响全部 |

## 性能优化

| 策略 | 说明 |
|------|------|
| 按需 grep | 不预构建索引，按需搜索 + 缓存 |
| 提前终止 | 遇到服务入口立即停止传播 |
| 深度限制 | max_depth=50 防止无限循环 |
| 结果缓存 | grep 结果和文件解析结果缓存 |

## 输出字段

| 字段 | 说明 |
|------|------|
| `changed_files` | 变更的 .go 文件（排除 _test.go, .pb.go） |
| `changed_elements` | 提取的公开函数/常量/变量 |
| `affected_services` | 影响的服务（http/rpc/cmd/library） |
| `circular_references` | 检测到的循环引用路径 |
| `restart_commands` | 生成的重启命令 |

## 相关文档

- [[tools/slpctl-usage-guide]] - slpctl 工具使用指南
- [[curated/tools/diff-impact-validation-plan]] - 测试验证计划
- [[core/coding-standards]] - 编码规范

## 注意事项

1. **必须在非 master 分支运行**
2. **只追踪公开元素**（Go 首字母大写）
3. **私有函数通过传播机制追踪**（找同包内公开调用者）
4. **实例调用需要验证导入关系**