---
id: slp-starship-event-capabilities
label: slp-starship 事件能力清单
source: curated/projects/slp-starship/01-event-capabilities.md
project: slp-starship
role: event-capabilities
compiled: 2026-04-25
tags:
  - event
  - topic
  - starship
links:
  - slp-starship-structure
---

# slp-starship 事件能力清单

> 家族（星舰）系统的事件能力注册表

## 事件能力总览

| 业务领域 | Topic | 消费者位置 | 处理方式 | 事件数量 |
|---------|-------|-----------|---------|---------|
| 星舰事件中心 | `starship.event.topic` | `cmd/internal/starship_event/` | HandleEventMap | 45 |

---

## 1. 星舰事件中心

**Topic**: `starship.event.topic`  
**消费者**: `cmd/internal/starship_event/service.go`  
**处理方式**: HandleEventMap 路由 (50 并发)

### 事件常量定义

```go
// consts/starship_event.go
const StarshipEventTopic = "starship.event.topic"

type StarshipEvent string

func (s StarshipEvent) ToString() string {
    return string(s)
}
```

---

## 事件分类详情

### 1.1 商城事件

| 事件 Cmd | 说明 |
|---------|------|
| `shop_pay_event` | 家族商城支付 |

### 1.2 议事厅事件

| 事件 Cmd | 说明 |
|---------|------|
| `bouleuterion_consume_event` | 议事厅消费 |
| `bouleuterion_add_score_event` | 议事厅加分 |

### 1.3 领事局事件

| 事件 Cmd | 说明 |
|---------|------|
| `consulate_add_score_event` | 领事局加分 |
| `consulate_send_msg_event` | 家族群聊发消息任务 |
| `consulate_room_time_event` | 房内停留时长任务 (>30 分钟) |
| `consulate_play_game_event` | 房内玩游戏任务 |

### 1.4 家族核心事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_after_create_event` | 家族创建后处理 |
| `starship_refresh_event` | 家族刷新 |
| `starship_refresh_rank_event` | 家族排行榜刷新 |
| `starship_quit_event` | 用户退出家族 |
| `starship_dismiss_event` | 家族解散 |
| `starship_dismiss_delay_event` | 家族解散延时 |

### 1.5 家族拍卖事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_auction_event` | 家族拍卖 |
| `starship_auction_notify_event` | 家族拍卖提醒 |
| `auction_add_score_event` | 拍卖厅加分 |

### 1.6 Binlog 事件

| 事件 Cmd | 说明 |
|---------|------|
| `xs_pay_change_new` | 支付订单变更 |
| `xs_starship_arch` | 家族建筑变更 |
| `xs_starship_auction` | 家族拍卖变更 |
| `xs_starship_auction_goods_conf` | 拍卖商品配置变更 |

---

## 新增事件方式

在 `cmd/internal/starship_event/event/` 创建新文件，在 `init()` 中注册到 `HandleEventMap`：

```go
package starship_event

func init() {
    HandleEventMap[consts.NewEventCmd] = &newEventHandler{}
}

type newEventHandler struct{}

func (h *newEventHandler) StarshipEvent(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```