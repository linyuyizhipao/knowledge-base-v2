---
id: slp-starship-event-capabilities
label: slp-starship 事件能力清单
source: curated/projects/slp-starship/01-event-capabilities.md
project: slp-starship
compiled: 2026-04-25
links:
  - slp-starship-structure
---

# slp-starship 事件能力清单

## 事件能力总览

| 业务领域 | Topic | 处理方式 | 事件数量 |
|---------|-------|---------|---------|
| 星舰事件中心 | `starship.event.topic` | HandleEventMap | 45 |

## 商城事件

| 事件 Cmd | 说明 |
|---------|------|
| `shop_pay_event` | 家族商城支付 |

## 议事厅事件

| 事件 Cmd | 说明 |
|---------|------|
| `bouleuterion_consume_event` | 议事厅消费 |
| `bouleuterion_add_score_event` | 议事厅加分 |

## 领事局事件

| 事件 Cmd | 说明 |
|---------|------|
| `consulate_add_score_event` | 领事局加分 |
| `consulate_send_msg_event` | 家族群聊发消息任务 |
| `consulate_room_time_event` | 房内停留时长任务 |
| `consulate_play_game_event` | 房内玩游戏任务 |

## 家族核心事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_after_create_event` | 家族创建后处理 |
| `starship_refresh_event` | 家族刷新 |
| `starship_refresh_rank_event` | 家族排行榜刷新 |
| `starship_quit_event` | 用户退出家族 |
| `starship_dismiss_event` | 家族解散 |
| `starship_dismiss_delay_event` | 家族解散延时 |

## 家族拍卖事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_auction_event` | 家族拍卖 |
| `starship_auction_notify_event` | 家族拍卖提醒 |
| `auction_add_score_event` | 拍卖厅加分 |
| `xs_pay_change_new` | 支付订单变更 |
| `xs_starship_arch` | 家族建筑变更 |
| `xs_starship_auction` | 家族拍卖变更 |

## 领地战事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_spot_war_event` | 领地战提醒 |
| `starship_war_flag_event` | 领地战更新旗帜 |
| `starship_war_hammer_event` | 领地战获得战锤 |
| `starship_war_animation_event` | 领地战动画 |

## 星梦空间事件

| 事件 Cmd | 说明 |
|---------|------|
| `starship_dream_space_event` | 星梦空间赠送礼物 |

## 家族房榜单事件 (Fy)

| 事件 Cmd | 说明 |
|---------|------|
| `fy_interaction_leave_room_event` | 离开家族房 |
| `fy_interaction_on_mic_event` | 家族房上麦 |
| `fy_interaction_screen_event` | 家族房屏幕互动 |
| `fy_starburst_send_gift_event` | 家族房赠送礼物 |

## 个人房榜单事件 (Pr)

| 事件 Cmd | 说明 |
|---------|------|
| `pr_interaction_leave_room_event` | 离开个人房 |
| `pr_interaction_on_mic_event` | 个人房上麦 |
| `pr_interaction_screen_event` | 个人房屏幕互动 |
| `pr_starburst_send_gift_event` | 个人房赠送礼物 |

## 农场事件

| 事件 Cmd | 说明 |
|---------|------|
| `farm_up_event` | 农场升级 |
| `farm_vege_up_event` | 农场蔬菜摊升级 |
| `farm_process_end` | 农场加工坊加工完成 |
| `farm_fishpond_bait_matures` | 鱼塘饵料成熟 |
| `farm_fishpond_steal_fish` | 鱼塘钓到鱼 |
| `farm_fishpond_level_up` | 鱼塘等级升级 |
| `farm_pretend_send_event` | 用户获取装扮 |
| `farm_red_package_award_event` | 发放农场红包 |

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
| 农场事件 | 9 |
| **总计** | **45** |

## 事件处理模式

slp-starship 统一使用 HandleEventMap 模式：
- 业务解耦 - 家族系统业务模块多
- 符合开闭原则 - 新增事件无需修改原有代码
- 与 slp-go/slp-room 保持一致 |