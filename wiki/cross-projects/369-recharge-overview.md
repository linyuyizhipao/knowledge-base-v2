---
id: 369-recharge-overview
label: 369 元观光团充值业务
source: curated/cross-projects/369-recharge/overview.md
business: 369-recharge
compiled: 2026-04-25
links:
  - 369-recharge-slp-room
  - 369-recharge-slp-go
---

# 369 元观光团充值业务

> 涉及 slp-room、slp-go 两个项目的充值营销活动

## 业务流程

| 步骤 | 项目 | 职责 | 核心模块 |
|------|------|------|----------|
| 进房捕获 | slp-room | 白名单判断 + A/B/C 分组 + 版本判断 | `cmd/internal/room_recommend_more/event/` |
| 弹窗触发 | slp-room | B 组 60 秒弹窗，C 组离房弹窗 | `app/service/recharge/recharge369.go` |
| 充值回调 | slp-go | 更新 recharge_rmb + 记录充值时间 | `cmd/internal/pay/handle/` |
| 奖励发放 | slp-go | 档位计算 + 发奖 + 弹窗通知 | `app/service/recharge/` |

## 技术架构

| 层级 | slp-room | slp-go |
|------|----------|--------|
| Service | `recharge369.go` | `recharge369.go` / `recharge369V1.go` / `recharge369V2.go` |
| Domain | `xs_room_369_group_user.go` | - |
| DAO | `xs_room_369_group_user.go` | - |
| CMD | `recharge_369_group_enter_room.go` | `pay/handle/` |

## 核心配置

| 配置项 | 说明 |
|--------|------|
| 白名单 type | 200 (BbcRoomRedpacketsWhitelist369Type) |
| cfg_id | 106 (369 路打卡团白名单业务) |
| PluginId | 16 (369 充值用户分组插件) |

## 分组逻辑

| 分组 | 弹窗策略 | 比例 |
|------|----------|------|
| A 组 | 不可见弹窗（对照组） | 1/3 |
| B 组 | 进房 60 秒后触发弹窗 | 1/3 |
| C 组 | 离房前触发弹窗 | 1/3 |

## 版本映射

| 客户端版本 | cast_version | 档位配置 |
|------------|--------------|----------|
| < 5.55.0.0 | - | 不参与活动 |
| 5.55.0.0 ~ 5.57.x | v1 | 6/10/18/30 元，7 天 |
| >= 5.58.0.0 | v2 | 10/30/68/100 元，10 天 |

## 共享数据表

**xs_room_369_group_user** - 两个项目共用同一张表

| 主要写入方 | 字段 |
|------------|------|
| slp-room | rid, enter_refer, group_type, pop_state, cast_version |
| slp-go | recharge_rmb, day_1~day_10, first_recharge_time, last_send_time |