---
id: room-type-concept
label: 房间类型拓展概念介绍
source: curated/cross-projects/chatroom/room-type-concept.md
business: chatroom
compiled: 2026-04-25
links:
  - room-type-development
  - room-type-work-plan
---

# 房间类型拓展概念介绍

> 快速参考 - 完整开发流程见 room-type-development.md

## 核心理念

**房间类型拓展 = 数据模型 + 业务服务 + 事件消费 + 配置注册**

## 开发流程总览

| 阶段 | 目标 | 输出 |
|------|------|------|
| 1. 数据库设计 | 定义数据模型 | 主表、关联表、流水表 DDL |
| 2. DAO/Model 生成 | 数据访问层代码 | `slpctl gen -t <table>` |
| 3. Proto 定义 | API 和实体接口 | `.proto` 文件 |
| 4. Service 层 | 核心业务逻辑 | `app/service/<module>/` |
| 5. API 层 | HTTP 接口 | `app/api/<module>.go` |
| 6. CMD 消费者 | NSQ 事件监听 | `cmd/internal/<module>/` |
| 7. 配置注册 | 注册到系统 | 模块工厂、模块配置 SQL |
| 8. 跨服务协调 | 所有服务支持 | slp-room、slp-php 等 |

## 快速 CheckList

### 数据库阶段
- [ ] 主表 DDL 编写
- [ ] property 枚举修改
- [ ] 模块工厂 INSERT
- [ ] 模块配置 INSERT

### 代码阶段
- [ ] DAO/Model 生成
- [ ] Proto 定义
- [ ] Service 层实现
- [ ] API 层实现

### 部署阶段
- [ ] Helm 配置更新
- [ ] 重启服务

## 大哥房 vs 星舰房

| 维度 | 大哥房 | 星舰房 |
|------|--------|--------|
| 服务形态 | HTTP + CMD | HTTP + CMD |
| 独立 Service | `app/service/big_brother/` | `commonsrv/starship/` |
| 房间类型 | `property='big-brother'` | `property='starship'` |
| 专属 Topic | `slp.big.brother` | `starship.event.topic` |

**选择建议**:
- 房间类型扩展 → 大哥房模式
- 独立大型玩法 → 星舰房模式