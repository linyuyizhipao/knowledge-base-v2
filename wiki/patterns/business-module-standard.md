---
id: patterns/business-module-standard
label: business-module-standard
source: /Users/hugh/project/my-wiki/curated/patterns/business-module-standard.md
role: 规范
compiled: 2026-04-28
source_hash: 12e7c3e3c9dea0839990f4cd322e6d4f
---

> 业务代码的组织结构与职责划分

## 核心原则

**一个业务模块 = 一个目录 = 一个对外服务对象**

## 标准结构

```
<project>/
├── consts/                      # 常量定义（按业务模块划分）
└── app/service/<business>/      # Service 层
    ├── service.go               # 主服务文件（唯一对外接口）
    ├── const.go                 # 模块专属常量
    ├── model.go                 # 模块专属数据结构
    └── <module>.go              # 子模块逻辑
```

## 各层职责

| 层级 | 职责 | 位置 |
|------|------|------|
| **consts/** | 全局共享常量（Redis Key、NSQ Topic、错误定义） | `consts/redis.go`, `consts/nsq.go` |
| **consts/<biz>.go** | 业务专属常量（状态、配置、RedisKey、工具函数） | `consts/immortal_pet.go` |
| **app/service/<biz>/** | 业务逻辑实现 | `service.go` + 子模块 |
| **app/utils/** | 纯计算工具函数，无 IO | `app/utils/bit.go` |

## Service 层组织

```go
var GiftSrv = &giftService{
    panel: &giftPanel{}, box: &giftBox{}, suit: &giftSuit{}, event: &giftEvent{},
}
```

**调用关系**：外部 `GiftSrv.PanelList()` → 内部 `g.panel.GetList()`

## 常量定义优先级

| 常量类型 | 定义位置 | 示例 |
|----------|----------|------|
| 业务专属 | `app/service/<business>/const.go` | `anchor/const.go` |
| 全局共享 | `consts/redis.go`, `consts/nsq.go` | `RedisKey`, `TopicUserLogin` |
| 配置型数据 | `consts/<business>.go` | `PetLevelConfigMap` |

## 反模式

| 反模式 | 错误 | 正确 |
|--------|------|------|
| 常量分散 | 常量分散在各个文件中 | 统一在 `const.go` |
| Service 无聚合 | 每个子模块独立暴露 | 主对象统一聚合 |
| 工具函数带 IO | `utils/` 中包含 Redis/DB 操作 | IO 放 Service，utils 做纯计算 |

## 检查清单

- [ ] 常量在 `consts/` 或 `const.go` 中定义
- [ ] Redis Key 使用 `RedisKey` 结构体，带 TTL
- [ ] NSQ Topic 统一命名（如 `xs.<module>.*`）
- [ ] Service 层有唯一对外暴露对象（全局单例）
- [ ] 子模块方法注入到主对象，不直接暴露
- [ ] 无 IO 的工具函数放在 `app/utils/`
