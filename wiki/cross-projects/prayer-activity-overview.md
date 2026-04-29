---
id: prayer-activity-overview
label: 祈福抽奖活动（活动模板 2）
source: curated/cross-projects/prayer-activity/01-overview.md
business: prayer-activity
compiled: 2026-04-25
links:
  - prayer-activity-slp-starship
  - prayer-activity-sql-config
---

# 祈福抽奖活动（活动模板 2）

> 基于活动模板 2 的概率抽奖玩法，新增两轮概率抽奖机制和心愿值系统

## 核心流程

| 步骤 | 说明 |
|------|------|
| 用户进入 | 选择轮次 |
| 扣除钻石 | 按价格配置扣费 |
| 两轮概率抽奖 | 第一轮选择奖池，第二轮抽取奖品 |
| 获得奖励 | 更新进度 |
| 心愿值处理 | 中大奖清空，否则 +1 |

## 技术架构

| 层级 | slp-starship | slp-go |
|------|--------------|--------|
| Service | `app/service/farm/prayer.go` | `rpc/client/starship_farm.go` |
| DAO | `xs_prayer_user_*.go` | - |
| RPC | - | SendFarmCommodity / SlpCommonConsume |

## 两轮抽奖算法

**第一轮（奖池选择）**:
- 最后一次抽奖强制进入大奖池
- 否则按概率选择（grand_pool_rate vs normal_pool_rate）

**第二轮（奖品抽取）**:
- 筛选未获得的奖品
- 大奖池需匹配 group == roundNum
- 兜底：所有奖品已获得则随机一个

## 数据表

| 表 | 说明 |
|----|------|
| xs_farm_activity_config | 活动配置（含 reward_pool_config JSON） |
| xs_prayer_user_progress | 用户进度（轮次、已获得奖励、心愿值） |
| xs_prayer_user_record | 抽奖日志 |
| xs_prayer_user_wish_value | 心愿值记录 |

## API 接口

| 接口 | 路由 | 说明 |
|------|------|------|
| PrayerHome | `/go/slp/farm/prayerHome` | 活动主页 |
| PrayerDraw | `/go/slp/farm/prayerDraw` | 祈福抽奖 |
| PrayerRecord | `/go/slp/farm/prayerRecord` | 抽奖记录 |

## 配置验证规则

| 规则 | 说明 |
|------|------|
| Round 数量 = 大奖个数 | 每轮对应一个大奖 |
| 奖池概率总和 = 100% | Grand + Normal = 100 |
| 奖池内奖品概率总和 = 100% | 每个奖池内部概率归一化 |