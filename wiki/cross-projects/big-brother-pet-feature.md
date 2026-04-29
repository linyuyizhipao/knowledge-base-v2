---
id: big-brother-pet-feature
label: 大哥房修仙宠物
source: curated/cross-projects/big-brother/pet-feature.md
business: big-brother
compiled: 2026-04-25
links: []
---

# 大哥房修仙宠物

> 大哥房专属修仙宠物玩法：打赏喂养 → 营养增长 → 孵化奖励

## 核心表设计

| 表 | 说明 |
|----|------|
| xs_big_brother_pet | 宠物主记录（1:1 房间） |
| xs_big_brother_pet_log | 宠物操作日志 |
| xs_big_brother_pet_round_user | 轮次用户参与记录 |

## 状态机

| 状态 | 值 | 说明 |
|------|-----|------|
| 喂养 | 1 | 正常状态 |
| 饥饿 | 4 | last_feed_time + 48h 后进入 |
| 濒危 | 5 | nutrition <= -30 |
| 死亡 | 6 | nutrition <= -50 |
| 孵化 | 2 | nutrition >= hatch_threshold |
| 可领奖 | 3 | hatch_start_at + 5min |

## 核心时间常量

| 常量 | 值 | 说明 |
|------|-----|------|
| HatchCountdownSeconds | 300 | 孵化倒计时 5 分钟 |
| RewardTimeoutSeconds | 1800 | 奖励超时 30 分钟 |
| HungerThreshold | 172800 | 48 小时未喂养进入饥饿 |
| DecayInterval | 7200 | 饥饿后每 2 小时衰减 1 营养 |
| ReviveCostDiamonds | 1000 | 复活消耗星钻 |

## API 接口

| 接口 | 路由 | 校验 |
|------|------|------|
| Claim | `/go/slp/pet/Claim` | 房主 + 大哥房 + 宠物不存在 |
| Info | `/go/slp/pet/Info` | 无校验 |
| Reward | `/go/slp/pet/Reward` | status=3 + 每日 3 次 + 每轮 1 次 |
| Revive | `/go/slp/pet/Revive` | status=6 + 房主 + 1000 钻 |
| SelectLevel | `/go/slp/pet/SelectLevel` | status=1 + 每天 1 次 |

## 技术要点

- **分布式锁**: `immortal_pet:{rid}` (Redis SETNX, 5s 超时)
- **奖池存储**: Redis LIST `immortal:pet:reward:pool:{rid}:{round_no}:{level}`
- **状态推进**: Scanner + NSQ 延时消息驱动

## 已修复 Bug

**last_feed_time 初始化为 0 导致饥饿失效**
- 修复：首次喂养时在 applyFeed 中设置 last_feed_time 为当前时间
- 分支: `fix/pet-last-feed-time`