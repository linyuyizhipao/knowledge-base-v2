# 房间类型拓展概念介绍

> 快速参考 - 完整开发流程见 [[room-type-development.md]]

**最后更新**: 2026-04-11

---

## 核心理念

**房间类型拓展 = 数据模型 + 业务服务 + 事件消费 + 配置注册**

当新增房间类型时，需要按以下顺序完成：

```
1. 数据库设计 → 2. DAO/Model 生成 → 3. Service 层实现 → 4. API 层暴露
                              ↓
5. Proto 定义 → 6. RPC 服务 → 7. CMD 事件消费者 → 8. 配置注册
```

---

## 开发流程总览

| 阶段 | 目标 | 输出 |
|------|------|------|
| 1. 数据库设计 | 定义房间类型的数据模型 | 主表、关联表、流水表 DDL |
| 2. DAO/Model 生成 | 生成数据访问层代码 | `slpctl gen -t <table>` |
| 3. Proto 定义 | 定义 API 和实体接口 | `.proto` 文件 |
| 4. Service 层实现 | 实现核心业务逻辑 | `app/service/<module>/` |
| 5. API 层实现 | 暴露 HTTP 接口 | `app/api/<module>.go` |
| 6. CMD 事件消费者 | 监听 NSQ 事件 | `cmd/internal/<module>/` |
| 7. 配置注册 | 注册到系统 | 模块工厂、模块配置 SQL |
| 8. 跨服务协调 | 所有服务支持 | slp-room、slp-php 等 |

---

## 快速 CheckList

### 数据库阶段
- [ ] 主表 DDL 编写
- [ ] 关联表 DDL 编写
- [ ] 流水表 DDL 编写
- [ ] property 枚举修改
- [ ] 模块工厂 INSERT
- [ ] 模块配置 INSERT

### 代码阶段
- [ ] DAO/Model 生成
- [ ] Proto 定义
- [ ] Service 层实现
- [ ] API 层实现
- [ ] CMD 消费者实现

### 部署阶段
- [ ] Helm 配置更新
- [ ] 环境变量检查
- [ ] 重启服务

---

## 与星舰房的对比

| 维度 | 大哥房 | 星舰房（slp-starship） |
|------|--------|----------------------|
| **服务形态** | HTTP + CMD | HTTP + CMD |
| **独立 Service** | `app/service/big_brother/` | `commonsrv/starship/` |
| **事件模式** | HandleEventMap + switch-case | HandleEventMap 统一路由 |
| **房间类型** | `property='big-brother'` | `property='starship'` |
| **专属 Topic** | `slp.big.brother` | `starship.event.topic` |

---

## 完整开发指南

**详细开发流程、代码示例、坑点解析**: [[room-type-development.md]]

**工作日安排参考**: [[room-type-work-plan.md]]

---

**版本**: 2.0 | **最后更新**: 2026-04-11
