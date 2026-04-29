---
id: prayer-activity-sql-config
label: 祈福抽奖活动配置 SQL
source: curated/cross-projects/prayer-activity/02-sql-config.md
business: prayer-activity
compiled: 2026-04-25
links:
  - prayer-activity-overview
---

# 祈福抽奖活动配置 SQL

> 活动 2 配置数据（测试环境）

## 活动配置概览

| 特点 | 配置 |
|------|------|
| 轮次 | 4 轮（6/8/12/16 次） |
| 价格 | 200/600/1000/1400 钻/次 |
| 大奖池 | 4 个大奖（每人每轮只能获得 1 个） |
| 小奖池 | 20 个小奖（可重复获得） |
| 大奖池概率 | 20% |

## 价格配置

| 轮次 | 抽奖次数 | 单价 | 总价 |
|------|----------|------|------|
| 第1轮 | 6 次 | 200 钻 | 1200 钻 |
| 第2轮 | 8 次 | 600 钻 | 4800 钻 |
| 第3轮 | 12 次 | 1000 钻 | 12000 钻 |
| 第4轮 | 16 次 | 1400 钻 | 22400 钻 |

## 配置规则检查

| 规则 | 结果 |
|------|------|
| Round 数量 = 大奖个数 | 4 = 4 ✅ |
| 总抽奖次数 | 42 ✅ |
| 奖池概率总和 | 100% ✅ |

## 数据库表

```sql
-- xs_prayer_user_record (抽奖记录)
-- xs_prayer_user_wish_value (心愿值)
-- xs_prayer_user_progress (进度)
-- xs_farm_activity_config (活动配置)
-- xs_farm_activity_price (价格配置)
-- xs_farm_activity_reward (奖励配置)
```

## 奖品配置示例

| ID | 名称 | 类型 |
|----|------|------|
| 17 | 绝版装扮-星辰之愿 | 大奖 |
| 18 | 绝版装扮-月光之羽 | 大奖 |
| 21 | 钻石*1000 | 小奖 |
| 23 | 装扮碎片*10 | 小奖 |