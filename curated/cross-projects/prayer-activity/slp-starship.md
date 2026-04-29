# 祈福抽奖活动 - slp-starship视角

> slp-starship 在祈福抽奖活动中的职责和实现细节

---

## 项目内职责

| 模块 | 职责 |
|------|------|
| `app/service/farm/prayer.go` | 核心抽奖逻辑实现 |
| `app/api/farm.go` | API 接口定义 |
| `app/dao/xs_prayer_user_*.go` | 数据访问层 |
| `proto/entity_xs_prayer_user_*.proto` | Proto 定义 |

---

## 核心代码

### Service 层

| 文件 | 说明 |
|------|------|
| `app/service/farm/prayer.go` | 祈福抽奖核心逻辑 |
| `app/service/farm/prayer_test.go` | 单元测试 |

**核心函数**：

| 函数 | 说明 |
|------|------|
| `PrayerHome` | 活动主页，返回用户进度、心愿值、价格配置 |
| `PrayerDraw` | 祈福抽奖，执行两轮概率抽奖 |
| `PrayerRecord` | 查询用户抽奖历史记录 |

### DAO 层

| Table | DAO 文件 | Model 文件 |
|-------|----------|------------|
| xs_prayer_user_progress | `app/dao/xs_prayer_user_progress.go` | `app/model/xs_prayer_user_progress.go` |
| xs_prayer_user_record | `app/dao/xs_prayer_user_record.go` | `app/model/xs_prayer_user_record.go` |
| xs_prayer_user_wish_value | `app/dao/xs_prayer_user_wish_value.go` | `app/model/xs_prayer_user_wish_value.go` |

### Proto 层

| Proto 文件 | 说明 |
|------------|------|
| `api/api_farm.proto` | API 接口定义 |
| `entity_xs_prayer_user_progress.proto` | 进度表定义 |
| `entity_xs_prayer_user_record.proto` | 日志表定义 |
| `entity_xs_prayer_user_wish_value.proto` | 心愿值表定义 |

---

## 配置常量

```go
// consts/farm.go
const (
    FarmActivityTypeTemplate1 = 0 // 装饰祈福（模板 1）
    FarmActivityTypeTemplate2 = 1 // 祈福抽奖（模板 2）
)
```

---

## 核心逻辑

### 两轮概率抽奖

**第一轮**（奖池选择）：
```go
// selectPool 选择奖池（第一次概率选择）
// 返回 true 表示大奖池，false 表示小奖池
func selectPool(config *PoolConfig, drawIndex, maxDraws int) bool {
    // 最后一次抽奖强制进入大奖池
    if drawIndex >= maxDraws {
        return true
    }
    // 按概率选择奖池
    return rand.Intn(100) < config.GrandPoolRate
}
```

**第二轮**（奖品抽取）：
```go
// drawFromPoolWithDedup 从奖池中抽取奖品（去重）
func drawFromPoolWithDedup(pool *PrizePool, obtained map[int64]bool, roundNum int) *PrizeItem {
    // 筛选出未获得的奖品
    // 大奖池需要匹配 group == roundNum
    // 兜底：如果所有奖品都已获得，从已获得的里面随机一个
}
```

### 心愿值管理

```go
// handleWishValue 处理心愿值更新
func (s *PrayerLogic) handleWishValue(ctx context.Context, uid uint32, activityID uint32, round int32, drawCount int32, isGrand bool) int32 {
    // 中大奖则清空心愿值
    if isGrand {
        // 删除心愿值记录
        return 0
    }
    // 否则 +drawCount
    return currentWish + drawCount
}
```

---

## 依赖的外部服务

| 服务 | 调用方法 | 说明 |
|------|----------|------|
| `slp-go:MoneyConsume` | `SlpCommonConsume` | 钻石扣除 |
| `slp-go:StarshipFarm` | `SendFarmCommodity` | 发放奖励 |

---

## 本地测试

### 1. 准备测试数据

```sql
-- 参见 02-sql-config.md
UPDATE xs_farm_activity_config SET activity_type = 1, reward_pool_config = '...' WHERE id = 2;
INSERT INTO xs_farm_activity_price ...;
INSERT INTO xs_farm_activity_reward ...;
```

### 2. 测试步骤

1. 启动 slp-starship 服务
2. 调用 `PrayerHome` 接口获取活动主页
3. 调用 `PrayerDraw` 接口执行抽奖
4. 检查返回结果和数据库记录

### 3. 预期结果

- 抽奖成功后，用户背包应收到对应奖励
- `xs_prayer_user_progress` 表应更新进度
- `xs_prayer_user_record` 表应记录抽奖日志
- `xs_prayer_user_wish_value` 表应更新心愿值

---

## 参考文档

- [`01-overview.md`](../01-overview.md) - 祈福抽奖活动业务全景图
- [`02-sql-config.md`](../02-sql-config.md) - 活动配置 SQL
