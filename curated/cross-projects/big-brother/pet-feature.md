# 大哥房修仙宠物 - 需求与设计文档

> 大哥房专属修仙宠物玩法：打赏喂养 → 营养增长 → 孵化奖励

**版本**: 1.1 | **最后更新**: 2026-04-13

---

## 一、业务概述

大哥房（超级大户房间）提供修仙宠物玩法，用户通过打赏喂养宠物，宠物成长孵化后可领取丰富奖励。宠物与大哥房等级绑定，高等级房间解锁高阶宠物和更丰富的奖池。

---

## 二、核心表设计

### `xs_big_brother_pet` - 宠物主记录（1:1 房间）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | bigint | 主键 |
| room_id | bigint | 房间ID（唯一索引） |
| owner_uid | bigint | 房主UID |
| status | tinyint | 1喂养 2孵化 3可领奖 4饥饿 5濒危 6死亡 |
| nutrition | int | 当前营养值（可为负） |
| hatch_level | int | 孵化锁定等级（孵化瞬间写入，平时为0） |
| round_no | int | 喂养轮次（每轮循环+1） |
| last_feed_time | int | 最后一次喂养时间戳 |
| hatch_start_at | int | 孵化开始时间戳 |
| reward_expire_at | int | 奖励领取截止时间戳 |
| create_time | int | 创建时间 |
| update_time | int | 更新时间 |
| selected_hatch_level | int | 房主选择的本轮孵化等级（0=未选择） |
| select_date | int | 选择日期（Unix时间戳0点） |
| hunger_start_at | int | 本轮饥饿开始时间（第一次进入饥饿状态的时间） |

### `xs_big_brother_pet_log` - 宠物操作日志

| 字段 | 类型 | 说明 |
|------|------|------|
| log_type | tinyint | 1打赏喂养 2饥饿衰减 3复活重置 4领取奖励 |
| nutrition_change | int | 营养值变化量（可为负，领奖时为0） |
| extra | varchar | 喂养{nobility,gift_id} 领奖{reward_id,reward_name,reward_num} |

### `xs_big_brother_pet_round_user` - 轮次用户参与记录

| 字段 | 类型 | 说明 |
|------|------|------|
| round_no | int | 轮次 |
| uid | bigint | 用户ID |
| feed_count | int | 本轮喂养次数 |
| nutrition_total | int | 本轮累计贡献营养值 |

---

## 三、状态机设计

```
喂养(1) ──→ 饥饿(4) ──→ 濒危(5) ──→ 死亡(6)
    │           ↓           ↓           ↑
    │         衰减        衰减        复活
    └─────→ 孵化(2) ──→ 可领奖(3) ──→ 下一轮
              5分钟倒计时    30分钟过期
```

### 状态转换规则

| 转换 | 触发条件 | 时间阈值 |
|------|----------|----------|
| 喂养 → 饥饿 | last_feed_time + 48h | 172800 秒 |
| 饥饿 → 濒危 | 营养值 ≤ -30 | 每 2h 衰减 1 |
| 濒危 → 死亡 | 营养值 ≤ -50 | 每 2h 衰减 1 |
| 喂养/饥饿/濒危 → 孵化 | nutrition ≥ hatch_threshold | - |
| 孵化 → 可领奖 | hatch_start_at + 5min | 300 秒 |
| 可领奖 → 下一轮 | 奖池清空 或 30min 过期 | 1800 秒 |
| 死亡 → 喂养 | 房主复活（1000 星钻） | - |

---

## 四、核心配置

### 时间常量

| 常量 | 值 | 说明 |
|------|-----|------|
| HatchCountdownSeconds | 300 | 孵化倒计时 5分钟 |
| RewardTimeoutSeconds | 1800 | 奖励超时 30分钟 |
| HungerThreshold | 172800 | 48小时未喂养进入饥饿 |
| DecayInterval | 7200 | 饥饿后每2小时衰减1营养 |
| CriticalNutrition | -30 | 濒危阈值 |
| DeathNutrition | -50 | 死亡阈值 |
| ReviveCostDiamonds | 1000 | 复活消耗 |

### 爵位营养加成

| 爵位 | 加成 |
|------|------|
| 0(无) | 1 |
| 10-60 | 2-3 |
| 70-80 | 3-4 |
| 90-100 | 5-6 |

### 房间等级 → 宠物等级映射

| 房间LV | 1-2 | 3-4 | 5-6 | 7-8 | 9-10 | 11-12 | 13-14 | 15-16 | 17-18 | 19-20 |
|--------|-----|-----|-----|-----|------|-------|-------|-------|-------|-------|
| 宠物LV | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |

---

## 五、API 接口

| 接口 | 功能 | 校验 |
|------|------|------|
| `/go/slp/pet/Claim` | 领取宠物 | 房主 + 大哥房 + 宠物不存在 |
| `/go/slp/pet/Info` | 获取宠物信息 | - |
| `/go/slp/pet/Reward` | 领取奖励 | status=3 + 每日3次 + 每轮1次 |
| `/go/slp/pet/Revive` | 复活宠物 | status=6 + 房主 + 1000钻 |
| `/go/slp/pet/SelectLevel` | 选择孵化等级 | status=1 + 每天1次 |
| `/go/slp/pet/Rule` | 玩法规则 | - |

---

## 六、技术架构

### 代码文件

```
app/service/immortal_pet/     # 核心服务
├── api.go                    # Service API 入口
├── feed.go                   # 喂养逻辑
├── claim.go                  # 领取逻辑
├── reward.go                 # 奖励逻辑
├── revive.go                 # 复活逻辑
├── state.go                  # 状态机
├── db.go                     # 数据库操作
├── stub.go                   # 辅助函数（广播/奖池）
├── info.go                   # 信息查询
└── rule.go                   # 玩法规则

cmd/internal/big_brother/     # CMD 事件处理
├── scanner.go                # 定时扫描器（每3分钟）
├── event/
│   ├── send_gift.go          # 打赏事件 → 喂养
│   ├── try_status_change.go  # 延时消息 → 状态推进
│   └── pet_status_change.go  # 状态变更 → 广播通知
```

### 技术要点

- **分布式锁**: `immortal_pet:{rid}` (Redis SETNX, 5s 超时)
- **奖池存储**: Redis LIST `immortal:pet:reward:pool:{rid}:{round_no}:{level}`
- **状态推进**: Scanner + NSQ 延时消息驱动，不依赖轮询
- **幂等**: 领奖通过 pet_log 校验，复活检查 status=Dead

---

## 七、已知问题与修复记录

### Bug 1: last_feed_time 初始化为 0 导致饥饿失效

**分支**: `fix/pet-last-feed-time`
**问题**: 领取/复活时 `last_feed_time=0`，导致 `LastFeedTime > 0` 判断永远不触发，饥饿状态永远不会进入
**修复**:
- 领取时 `status=1`(feeding)，`last_feed_time=0`（不设喂养时间，饥饿倒计时尚未开始）
- 首次喂养时在 `applyFeed` 中将 `last_feed_time` 设为当前时间（饥饿倒计时从此刻开始）
- 复活时 `last_feed_time=nowTs`
- `resetToNextRound` 同步设置 `last_feed_time=nowTs`
- 清理了 `claim.go` 和 `feed.go` 中所有 `PetStatusUnclaimed` 相关逻辑

---

## 八、相关文档

- [slp-room 项目结构](../../projects/slp-room/01-structure.md)
- [slp-room 架构](../../projects/slp-room/02-architecture.md)
- [大哥房事件能力](../../projects/slp-room/01-event-capabilities.md)
