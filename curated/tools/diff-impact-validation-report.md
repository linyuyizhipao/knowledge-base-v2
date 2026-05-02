---
name: diff-impact-validation-report
description: diff-impact.py 测试验证报告
type: report
---

# diff-impact.py 测试验证报告

**测试日期**: 2026-05-02
**测试项目**: slp-go
**脚本版本**: v2 (按需 grep + 缓存)

---

## 测试结果汇总

| 场景 | 测试目标 | 结果 | 说明 |
|------|----------|------|------|
| C | RPC 服务入口 (user.go) | ✅ 通过 | 正确识别 `rpc: ["user"]` |
| D | CMD 服务入口 (anchor.go) | ✅ 通过 | 正确识别 `cmd: ["anchor"]` |
| E | HTTP Handler (home.go) | ✅ 通过 | 正确识别 `http: true` |
| A | 公共方法 (library/nsq.go) | ⏱️ 超时 | 使用量太大，需性能优化 |
| B | 常量变更 (consts/const.go) | ⏱️ 超时 | 文件包含太多公开元素 |

---

## 详细测试记录

### 场景 C：RPC 服务入口变更

**变更文件**: `rpc/server/internal/user.go`
**变更内容**: 在 `PRCUser` 函数添加日志
**预期输出**: `rpc: ["user"]`

**实际输出**:
```json
{
  "changed_files": ["rpc/server/internal/user.go"],
  "affected_services": {
    "http": false,
    "rpc": ["user"],
    "cmd": []
  },
  "restart_commands": ["make build && ./bin/rpc --name=user"]
}
```

**结论**: ✅ 符合预期

**修复过程**: 
- 初次测试失败，`rpc/server/internal/user.go` 未被识别为 RPC 服务入口
- 原因：脚本只匹配 `rpc/server/internal/<name>/` 子目录，不匹配入口文件
- 修复：更新 `_get_service_from_file` 方法，支持 `rpc/server/internal/*.go` 入口文件

---

### 场景 D：CMD 服务入口变更

**变更文件**: `cmd/internal/anchor.go`
**变更内容**: 在 `CmdAnchor.Main` 方法添加日志
**预期输出**: `cmd: ["anchor"]`

**实际输出**:
```json
{
  "changed_files": ["cmd/internal/anchor.go"],
  "affected_services": {
    "http": false,
    "rpc": [],
    "cmd": ["anchor"]
  },
  "restart_commands": ["make build && ./bin/cmd --name=anchor"]
}
```

**结论**: ✅ 符合预期

---

### 场景 E：HTTP Handler 变更

**变更文件**: `app/api/home.go`
**变更内容**: 在 `Foryou` 方法添加日志
**预期输出**: `http: true`

**实际输出**:
```json
{
  "changed_files": ["app/api/home.go"],
  "affected_services": {
    "http": true,
    "rpc": [],
    "cmd": []
  },
  "restart_commands": ["make build && ./bin/http"]
}
```

**结论**: ✅ 符合预期

---

### 场景 A：公共方法变更（超时）

**变更文件**: `library/nsq.go`
**变更内容**: 在 `NsqClient` 函数添加日志
**预期输出**: 多个 RPC 和 CMD 服务

**问题**: 脚本在 BFS 追踪阶段超时
- `NsqClient` 被 71+ 文件使用
- 每个引用文件又可能传播到更多文件
- grep 调用次数太多

**结论**: ⏱️ 性能问题，需优化

---

### 场景 B：常量变更（超时）

**变更文件**: `app/consts/const.go`
**变更内容**: 修改 `GiftAwakeDiscountGiftNormalGid` 常量注释
**预期输出**: HTTP + CMD 服务

**问题**: `consts/const.go` 文件包含 15+ 公开常量/变量
- 脚本提取所有公开元素并分别追踪
- 导致大量 grep 调用

**结论**: ⏱️ 性能问题，需优化

---

## 发现的问题

### 1. 服务入口识别不全

**问题**: 原脚本只识别 `rpc/server/internal/<name>/` 子目录，遗漏入口文件

**修复**: 已修复，现在支持：
- `rpc/server/internal/*.go` 入口文件
- `cmd/internal/*.go` 入口文件

### 2. 性能问题

**问题**: 公共方法/常量追踪耗时过长

**原因**:
1. BFS 追踪时每个引用文件都触发 grep
2. 公共元素使用量大（RedisClient 272+, NsqClient 71+）
3. 常量文件包含多个元素，分别追踪

**建议优化方向**:
1. 增加传播深度限制（当前 max_depth=50 已有，但可能不够严格）
2. 对公共库（library/consts）变更直接标记"影响全部"，不追踪
3. 增加引用数量阈值，超过阈值的服务列表直接返回"全部"

---

## 验证结论

### 核心功能验证 ✅

| 功能 | 状态 |
|------|------|
| RPC 服务入口识别 | ✅ 通过 |
| CMD 服务入口识别 | ✅ 通过 |
| HTTP 服务入口识别 | ✅ 通过 |
| JSON 输出格式 | ✅ 通过 |
| 重启命令生成 | ✅ 通过 |

### 待优化功能 ⏱️

| 功能 | 问题 |
|------|------|
| 公共方法追踪 | 性能需优化 |
| 常量追踪 | 性能需优化 |
| 私有函数传播 | 未测试（场景 F） |

---

## 后续行动

1. **优化性能**：对 library/consts 变更直接标记"影响全部"
2. **测试场景 F**：私有函数传播测试
3. **测试场景 H**：无影响变更测试
4. **测试场景 G**：多服务同时变更