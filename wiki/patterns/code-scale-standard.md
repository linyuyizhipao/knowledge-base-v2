---
id: patterns/code-scale-standard
label: code-scale-standard
source: /Users/hugh/project/my-wiki/curated/patterns/code-scale-standard.md
role: 规范
compiled: 2026-04-28
source_hash: e22988e77ae89c0efb9fcd0e469cb691
---

> 函数和文件的合理规模控制

## 推荐规模

### 函数

| 函数类型 | 推荐行数 | 上限 | 说明 |
|----------|---------|------|------|
| Handler | 10-25 | 30 | 参数解析 + 调 service + 返回 |
| Service | 20-50 | 100 | 完整业务逻辑 |
| 工具函数 | 5-20 | 30 | 单一功能 |

### 文件

| 文件类型 | 推荐行数 | 上限 | 说明 |
|----------|---------|------|------|
| API Handler | 50-200 | 300 | 按业务功能聚合 |
| Service | 100-300 | 500 | 基础/业务服务 |

## 好的模式

```go
// Handler 极简：只做三件事
func (*transferApi) Show(r *ghttp.Request) {
    output := transfer.TransferService.Show(r.Context())
    response.Output(r, output)
}
```

## 拆分信号

| 信号 | 建议 |
|------|------|
| 注释里有"第一步"、"第二步" | 按步骤拆分 |
| 局部变量超过 10 个 | 考虑拆分或用结构体封装 |
| if/for 嵌套超过 3 层 | 抽取为独立函数 |
| 无法用一句话描述功能 | 按功能拆分 |
| 文件超过 500 行 | 按功能模块拆分 |

## 检查清单

- [ ] Handler 函数不超过 30 行
- [ ] Service 函数不超过 100 行
- [ ] API 文件不超过 300 行
- [ ] Service 文件不超过 500 行
- [ ] 文件内函数属于同一业务领域
