# slp-starship 事件能力清单

> 家族（星舰）系统的事件能力注册表

**最后更新**: 2026-04-05  
**代码版本**: master@80eb9c86d

---

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

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `shop_pay_event` | 家族商城支付 | `event_shop_pay.go` |

---

### 1.2 议事厅事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `bouleuterion_consume_event` | 议事厅消费 | `event_bouleuterion_consume.go` |
| `bouleuterion_add_score_event` | 议事厅加分 | `event_bouleuterion_add_score.go` |

---

### 1.3 领事局事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `consulate_add_score_event` | 领事局加分 | `event_consulate_add_score.go` |
| `consulate_send_msg_event` | 家族群聊发消息任务 | `event_consulate_send_msg_task.go` |
| `consulate_room_time_event` | 房内停留时长任务 (>30 分钟) | `event_consulate_room_time_task.go` |
| `consulate_play_game_event` | 房内玩游戏任务 | `event_consulate_room_play_task.go` |

---

### 1.4 家族核心事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `starship_after_create_event` | 家族创建后处理 | - |
| `starship_refresh_event` | 家族刷新 | `event_starship_refresh.go` |
| `starship_refresh_rank_event` | 家族排行榜刷新 | - |
| `starship_quit_event` | 用户退出家族 | - |
| `starship_dismiss_event` | 家族解散 | `event_starship_dismiss.go` |
| `starship_dismiss_delay_event` | 家族解散延时 | - |

---

### 1.5 家族拍卖事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `starship_auction_event` | 家族拍卖 | `event_starship_auction.go` |
| `starship_auction_notify_event` | 家族拍卖提醒 | `event_starship_auction_notify.go` |
| `auction_add_score_event` | 拍卖厅加分 | `event_starship_auction_add_score.go` |

**Binlog 事件**:
| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `xs_pay_change_new` | 支付订单变更 | `event_binlog_xs_pay_change_new.go` |
| `xs_starship_arch` | 家族建筑变更 | `event_binlog_xs_starship_arch.go` |
| `xs_starship_auction` | 家族拍卖变更 | `event_binlog_xs_starship_auction.go` |
| `xs_starship_auction_goods_conf` | 拍卖商品配置变更 | `event_binlog_xs_starship_auction_goods_conf.go` |

---

### 1.6 领地战事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `starship_spot_war_event` | 领地战提醒 | - |
| `starship_war_flag_event` | 领地战更新旗帜 | - |
| `starship_war_hammer_event` | 领地战获得战锤 | - |
| `starship_war_animation_event` | 领地战攻击/防守动画 | - |

---

### 1.7 星梦空间事件

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `starship_dream_space_event` | 星梦空间赠送礼物 | `event_starship_dream_space.go` |

---

### 1.8 家族房榜单事件 (Fy)

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `fy_interaction_leave_room_event` | 离开家族房 | `event_fy_interaction_leave_room.go` |
| `fy_interaction_leave_room_score_event` | 离开家族房加分 | `event_fy_interaction_leave_room_score.go` |
| `fy_interaction_on_mic_event` | 家族房上麦 | `event_fy_interaction_on_mic.go` |
| `fy_interaction_screen_event` | 家族房屏幕互动 | `event_fy_interaction_screen.go` |
| `fy_starburst_send_gift_event` | 家族房赠送礼物 | `event_fy_starburst_send_gift.go` |

---

### 1.9 家族成员个人房榜单事件 (Pr)

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `pr_interaction_leave_room_event` | 离开个人房 | `event_pr_interaction_leave_room.go` |
| `pr_interaction_leave_room_score_event` | 离开个人房加分 | `event_pr_interaction_leave_room_score.go` |
| `pr_interaction_on_mic_event` | 个人房上麦 | `event_pr_interaction_on_mic.go` |
| `pr_interaction_screen_event` | 个人房屏幕互动 | `event_pr_interaction_screen.go` |
| `pr_starburst_send_gift_event` | 个人房赠送礼物 | `event_pr_starburst_send_gift.go` |

---

### 1.10 农场事件

#### 农场基础

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `farm_up_event` | 农场升级 | - |
| `farm_vege_up_event` | 农场蔬菜摊升级 | - |
| `farm_process_end` | 农场加工坊加工完成 | - |

#### 农场鱼塘

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `farm_fishpond_bait_matures` | 鱼塘抛饵的饵料成熟 | - |
| `farm_fishpond_steal_fish` | 鱼塘钓到鱼事件 | - |
| `farm_fishpond_steal_fish_card_package` | 鱼塘钓到鱼卡包事件 | - |
| `farm_fishpond_level_up` | 鱼塘等级升级事件 | - |
| `farm_fishpond_steal_fish_book_try_task` | 试图完成图鉴任务 | - |

#### 农场装扮

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `farm_pretend_send_event` | 用户获取装扮 | - |

#### 农场红包

| 事件 Cmd | 说明 | 处理器位置 |
|---------|------|-----------|
| `farm_red_package_award_event` | 发放农场红包 | - |

---

## HandleEventMap 结构

```go
// cmd/internal/starship_event/event/base.go
package event

type HandleEvent interface {
    Handle(ctx context.Context, data *cmd.NsqEventMsg) (err error)
}

var HandleEventMap = map[consts.StarshipEvent]HandleEvent{}
```

---

## 新增事件模板

### 步骤 1: 定义事件常量

```go
// consts/starship_event.go
const (
    EventMyNewFeature StarshipEvent = "my_new_feature_event"
)
```

### 步骤 2: 创建事件处理器

```go
// cmd/internal/starship_event/event/my_new_feature_event.go
package event

func init() {
    HandleEventMap[consts.EventMyNewFeature] = &myNewFeatureHandler{}
}

type myNewFeatureHandler struct{}

func (h *myNewFeatureHandler) Handle(ctx context.Context, data *cmd.NsqEventMsg) error {
    // 业务逻辑
    return nil
}
```

---

## 事件发送

### NSQ 发送格式

```go
// JSON 格式（推荐）
type NsqEventData struct {
    Cmd  string `json:"cmd"`
    Data any    `json:"data"`
}

nsqData, _ := json.Marshal(&NsqEventData{
    Cmd:  "shop_pay_event",
    Data: map[string]interface{}{
        "uid": uid,
        "starship_id": starshipId,
        "amount": amount,
    },
})
_ = library.NsqClient().SendBytes(consts.StarshipEventTopic, []byte(nsqData), 2*time.Second)
```

### PHP 序列化格式（兼容老代码）

```go
data := php_serialize.PhpArray{
    "uid": uid,
    "starship_id": starshipId,
}
dataBytes, _ := php_serialize.Serialize(data)
_ = library.NsqClient().SendBytes(consts.StarshipEventTopic, dataBytes)
```

---

## 事件调试

### 查看 NSQ Topic 状态

```bash
# 查看 Topic 信息
curl http://nsqadmin:4171/api/topic?topic=starship.event.topic

# 查看消费者连接
curl http://nsqadmin:4171/api/channel?topic=starship.event.topic&channel=default
```

### 本地测试发送事件

```bash
curl -X POST http://localhost:4151/pub?topic=starship.event.topic \
  -d '{"cmd":"shop_pay_event","data":{"uid":123,"starship_id":456,"amount":100}}'
```

### 日志排查

```go
// 所有事件处理都有统一日志
g.Log().Ctx(ctx).Info("msg", "NsqMessageHandler", "nsqMsg.Cmd", nsqMsg.Cmd)
```

---

## 事件处理器模式

slp-starship **统一使用 HandleEventMap 模式**，原因：

1. **业务解耦** - 家族系统业务模块多，需要动态扩展
2. **符合开闭原则** - 新增事件无需修改原有代码
3. **与 slp-go/slroom 保持一致** - 遵循统一的事件拓展规范

---

## 跨项目事件协调

### slp-starship → slp-go

| 事件 | Topic | 说明 |
|------|-------|------|
| 支付订单变更 | `xs_pay_change_new` | slp-go 支付回调 |

### slp-go → slp-starship

| 事件 | Topic | 说明 |
|------|-------|------|
| 家族拍卖 | `starship_auction_event` | 触发家族拍卖处理 |

---

## 事件统计

| 分类 | 事件数量 |
|------|---------|
| 商城事件 | 1 |
| 议事厅事件 | 2 |
| 领事局事件 | 4 |
| 家族核心事件 | 6 |
| 家族拍卖事件 | 7 |
| 领地战事件 | 4 |
| 星梦空间事件 | 1 |
| 家族房榜单事件 | 5 |
| 个人房榜单事件 | 5 |
| 农场事件 | 6 |
| **总计** | **41** |

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [`01-structure.md`](./01-structure.md) | 项目结构 |
| [`../../../patterns/event-extension-guide.md`](../../../patterns/event-extension-guide.md) | 事件能力拓展指南 |
| [`../../../patterns/nsq-usage.md`](../../../patterns/nsq-usage.md) | NSQ 使用规范 |

---

**维护说明**:
- 新增事件能力时，在对应章节追加记录
- 废弃事件时，在事件后标注 `@deprecated` 和废弃日期
- 每季度审查一次事件列表，清理无用事件
