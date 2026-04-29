---
id: slp-go-business-369-recharge
label: 369 元观光团充值业务
source: curated/projects/slp-go/08-business-369-recharge.md
project: slp-go
compiled: 2026-04-25
links:
  - slp-go-event-capabilities
---

# 369 元观光团充值业务

## 业务概述

| 特性 | V1 版本 | V2 版本 |
|------|---------|---------|
| 充值档位 | 6/10/18/30 元 | 10/30/68/100 元 |
| 签到天数 | 7 天 | 10 天 |
| 最高奖励 | 7 天签到 | 10 天签到（6 位靓号） |

## 数据表结构

| 字段 | 类型 | slp-go 写入 | 说明 |
|------|------|-------------|------|
| `recharge_rmb` | uint32 | Y | 累计充值金额 |
| `first_recharge_time` | uint32 | Y | 首次充值时间 |
| `day_1` ~ `day_10` | uint32 | Y | 每天领奖档位 |
| `last_send_time` | uint32 | Y | 最近领奖时间 |
| `extra` | string | Y | 已发物品 JSON |
| `cast_version` | string | - | 版本 v1/v2 |

## 核心流程

| 流程 | 说明 |
|------|------|
| 充值回调 | 更新累计充值，触发在线发奖 |
| 在线发奖 | 用户在线时自动发奖 |
| 天数计算 | 根据已领天数和档位计算 |
| 发奖逻辑 | 去重检查，乐观锁更新，发放物品 |

## 奖励配置 (V2)

| 档位 | 签到天数 | 描述 |
|------|----------|------|
| 10 元 | 3 天 | 普通档 |
| 30 元 | 5 天 | 高级档 |
| 68 元 | 7 天 | 豪华档 |
| 100 元 | 10 天 | 典藏档（6 位靓号） |

## API 接口

| 路由 | 说明 |
|------|------|
| `POST /go/slp/recharge/recharge369` | 领取 369 奖励 |

## 关键业务规则

| 规则 | 说明 |
|------|------|
| 升档补发 | 当天升档继续领，不增加天数 |
| 防重复领取 | extra 字段记录已发物品 |
| 同一天限制 | 已领且未升档则拒绝 |
| 乐观锁 | 只允许小档位往大档位更新 |

## 相关文件

| 文件 | 说明 |
|------|------|
| `app/service/recharge/recharge369.go` | 版本路由 |
| `app/service/recharge/recharge369V2.go` | V2 实现 |
| `app/consts/recharge_369_group_v2.go` | V2 配置 |