---
id: prayer-activity-slp-starship
label: 祈福抽奖活动 - slp-starship 视角
source: curated/cross-projects/prayer-activity/slp-starship.md
business: prayer-activity
compiled: 2026-04-25
links:
  - prayer-activity-overview
---

# 祈福抽奖活动 - slp-starship 视角

> slp-starship 在祈福抽奖活动中的职责和实现细节

## 核心代码位置

| 文件 | 说明 |
|------|------|
| `app/service/farm/prayer.go` | 祈福抽奖核心逻辑 |
| `app/service/farm/prayer_test.go` | 单元测试 |
| `app/api/farm.go` | API 接口定义 |
| `proto/entity_xs_prayer_user_*.proto` | Proto 定义 |

## 核心函数

| 函数 | 说明 |
|------|------|
| PrayerHome | 活动主页，返回用户进度、心愿值、价格配置 |
| PrayerDraw | 祈福抽奖，执行两轮概率抽奖 |
| PrayerRecord | 查询用户抽奖历史记录 |

## 两轮抽奖实现

### 第一轮（奖池选择）

```go
func selectPool(config *PoolConfig, drawIndex, maxDraws int) bool {
    if drawIndex >= maxDraws {
        return true // 最后一次强制大奖池
    }
    return rand.Intn(100) < config.GrandPoolRate
}
```

### 第二轮（奖品抽取）

```go
func drawFromPoolWithDedup(pool *PrizePool, obtained map[int64]bool, roundNum int) *PrizeItem {
    // 筛选未获得奖品
    // 大奖池需要匹配 group == roundNum
    // 兜底：如果所有奖品都已获得，从已获得的里面随机一个
}
```

## 心愿值管理

```go
func handleWishValue(...) int32 {
    if isGrand {
        // 中大奖则清空心愿值
        return 0
    }
    // 否则 +drawCount
    return currentWish + drawCount
}
```

## 外部 RPC 调用

| 服务 | 方法 | 说明 |
|------|------|------|
| slp-go:MoneyConsume | SlpCommonConsume | 钻石扣除 |
| slp-go:StarshipFarm | SendFarmCommodity | 发放奖励 |