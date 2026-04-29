# 祈福抽奖活动配置 SQL

> 活动2 配置数据（测试环境）  
> **最后更新**: 2026-04-14  
> **版本**: 1.0

---

## 活动配置说明

**活动特点**：
- 4轮，每轮抽奖次数分别为：6/8/12/16
- 价格：200/600/1000/1400 钻/次
- 大奖池：4个大奖（每人每轮只能获得1个）
- 小奖池：20个小奖（可重复获得）
- 大奖池概率：20%，小奖池概率：80%

---

## 1. 更新活动配置

```sql
INSERT INTO `xs_farm_activity_config` (`id`, `activity_name`, `start_time`, `end_time`, `round_draws`, `round_times`, `status`, `reward_pool_config`, `rule_text`, `created_at`, `updated_at`, `tab_icon`, `show_home_button`, `home_button_icon`, `activity_type`)
VALUES
	(2, '活动2', 1776142752, 1776574750, 4, 6, 1, '{\n    \"multi_draw_config\": {\"enabled\": false, \"draw_count\": 10, \"discount_rate\": 90},\n    \"rounds\": [\n        {\"round_num\": 1, \"draw_count\": 6, \"prices\": [{\"draw_index\": 1, \"price\": 200, \"discount\": 0},{\"draw_index\": 2, \"price\": 200, \"discount\": 0},{\"draw_index\": 3, \"price\": 200, \"discount\": 0},{\"draw_index\": 4, \"price\": 200, \"discount\": 0},{\"draw_index\": 5, \"price\": 200, \"discount\": 0},{\"draw_index\": 6, \"price\": 200, \"discount\": 0}]},\n        {\"round_num\": 2, \"draw_count\": 8, \"prices\": [{\"draw_index\": 1, \"price\": 600, \"discount\": 0},{\"draw_index\": 2, \"price\": 600, \"discount\": 0},{\"draw_index\": 3, \"price\": 600, \"discount\": 0},{\"draw_index\": 4, \"price\": 600, \"discount\": 0},{\"draw_index\": 5, \"price\": 600, \"discount\": 0},{\"draw_index\": 6, \"price\": 600, \"discount\": 0},{\"draw_index\": 7, \"price\": 600, \"discount\": 0},{\"draw_index\": 8, \"price\": 600, \"discount\": 0}]},\n        {\"round_num\": 3, \"draw_count\": 12, \"prices\": [{\"draw_index\": 1, \"price\": 1000, \"discount\": 0},{\"draw_index\": 2, \"price\": 1000, \"discount\": 0},{\"draw_index\": 3, \"price\": 1000, \"discount\": 0},{\"draw_index\": 4, \"price\": 1000, \"discount\": 0},{\"draw_index\": 5, \"price\": 1000, \"discount\": 0},{\"draw_index\": 6, \"price\": 1000, \"discount\": 0},{\"draw_index\": 7, \"price\": 1000, \"discount\": 0},{\"draw_index\": 8, \"price\": 1000, \"discount\": 0},{\"draw_index\": 9, \"price\": 1000, \"discount\": 0},{\"draw_index\": 10, \"price\": 1000, \"discount\": 0},{\"draw_index\": 11, \"price\": 1000, \"discount\": 0},{\"draw_index\": 12, \"price\": 1000, \"discount\": 0}]},\n        {\"round_num\": 4, \"draw_count\": 16, \"prices\": [{\"draw_index\": 1, \"price\": 1400, \"discount\": 0},{\"draw_index\": 2, \"price\": 1400, \"discount\": 0},{\"draw_index\": 3, \"price\": 1400, \"discount\": 0},{\"draw_index\": 4, \"price\": 1400, \"discount\": 0},{\"draw_index\": 5, \"price\": 1400, \"discount\": 0},{\"draw_index\": 6, \"price\": 1400, \"discount\": 0},{\"draw_index\": 7, \"price\": 1400, \"discount\": 0},{\"draw_index\": 8, \"price\": 1400, \"discount\": 0},{\"draw_index\": 9, \"price\": 1400, \"discount\": 0},{\"draw_index\": 10, \"price\": 1400, \"discount\": 0},{\"draw_index\": 11, \"price\": 1400, \"discount\": 0},{\"draw_index\": 12, \"price\": 1400, \"discount\": 0},{\"draw_index\": 13, \"price\": 1400, \"discount\": 0},{\"draw_index\": 14, \"price\": 1400, \"discount\": 0},{\"draw_index\": 15, \"price\": 1400, \"discount\": 0},{\"draw_index\": 16, \"price\": 1400, \"discount\": 0}]}\n    ],\n    \"pool_config\": {\n        \"grand_pool_rate\": 20,\n        \"normal_pool_rate\": 80,\n        \"grand_pool\": {\"items\": [{\"id\": 17, \"probability\": 25},{\"id\": 18, \"probability\": 25},{\"id\": 19, \"probability\": 25},{\"id\": 20, \"probability\": 25}]},\n        \"normal_pool\": {\"items\": [{\"id\": 21, \"probability\": 2},{\"id\": 22, \"probability\": 2},{\"id\": 23, \"probability\": 2},{\"id\": 24, \"probability\": 2},{\"id\": 25, \"probability\": 2},{\"id\": 26, \"probability\": 2},{\"id\": 27, \"probability\": 2},{\"id\": 28, \"probability\": 2},{\"id\": 29, \"probability\": 2},{\"id\": 30, \"probability\": 2},{\"id\": 31, \"probability\": 2},{\"id\": 32, \"probability\": 2},{\"id\": 33, \"probability\": 2},{\"id\": 34, \"probability\": 2},{\"id\": 35, \"probability\": 3},{\"id\": 36, \"probability\": 3},{\"id\": 37, \"probability\": 3},{\"id\": 38, \"probability\": 3},{\"id\": 39, \"probability\": 3},{\"id\": 40, \"probability\": 3},{\"id\": 41, \"probability\": 3},{\"id\": 42, \"probability\": 3},{\"id\": 43, \"probability\": 3},{\"id\": 44, \"probability\": 3},{\"id\": 45, \"probability\": 3},{\"id\": 46, \"probability\": 3},{\"id\": 47, \"probability\": 3},{\"id\": 48, \"probability\": 3},{\"id\": 49, \"probability\": 3},{\"id\": 50, \"probability\": 3},{\"id\": 51, \"probability\": 3},{\"id\": 52, \"probability\": 3},{\"id\": 53, \"probability\": 3},{\"id\": 54, \"probability\": 3},{\"id\": 55, \"probability\": 3},{\"id\": 56, \"probability\": 3},{\"id\": 57, \"probability\": 3},{\"id\": 58, \"probability\": 3}]}\n    }\n}', '没有规则', 1774419941, 1774419941, '/starship/65ac45940e2d86c1abe8875f0568738b.png', 0, '', 1);

```

---

## 2. 插入抽奖价格配置

```sql
-- 第1轮：6次，每次200钻
INSERT INTO xs_farm_activity_price (activity_id, round, draw_count, price, discount) VALUES
(2, 1, 1, 200, 0),
(2, 1, 2, 200, 0),
(2, 1, 3, 200, 0),
(2, 1, 4, 200, 0),
(2, 1, 5, 200, 0),
(2, 1, 6, 200, 0);

-- 第2轮：8次，每次600钻
INSERT INTO xs_farm_activity_price (activity_id, round, draw_count, price, discount) VALUES
(2, 2, 1, 600, 0),
(2, 2, 2, 600, 0),
(2, 2, 3, 600, 0),
(2, 2, 4, 600, 0),
(2, 2, 5, 600, 0),
(2, 2, 6, 600, 0),
(2, 2, 7, 600, 0),
(2, 2, 8, 600, 0);

-- 第3轮：12次，每次1000钻
INSERT INTO xs_farm_activity_price (activity_id, round, draw_count, price, discount) VALUES
(2, 3, 1, 1000, 0),
(2, 3, 2, 1000, 0),
(2, 3, 3, 1000, 0),
(2, 3, 4, 1000, 0),
(2, 3, 5, 1000, 0),
(2, 3, 6, 1000, 0),
(2, 3, 7, 1000, 0),
(2, 3, 8, 1000, 0),
(2, 3, 9, 1000, 0),
(2, 3, 10, 1000, 0),
(2, 3, 11, 1000, 0),
(2, 3, 12, 1000, 0);

-- 第4轮：16次，每次1400钻
INSERT INTO xs_farm_activity_price (activity_id, round, draw_count, price, discount) VALUES
(2, 4, 1, 1400, 0),
(2, 4, 2, 1400, 0),
(2, 4, 3, 1400, 0),
(2, 4, 4, 1400, 0),
(2, 4, 5, 1400, 0),
(2, 4, 6, 1400, 0),
(2, 4, 7, 1400, 0),
(2, 4, 8, 1400, 0),
(2, 4, 9, 1400, 0),
(2, 4, 10, 1400, 0),
(2, 4, 11, 1400, 0),
(2, 4, 12, 1400, 0),
(2, 4, 13, 1400, 0),
(2, 4, 14, 1400, 0),
(2, 4, 15, 1400, 0),
(2, 4, 16, 1400, 0);
```

---

## 3. 插入奖励配置

```sql
-- 插入奖品配置（主键 id 17-30）
-- 注意：reward_pool_config 中引用的是 xs_farm_activity_reward.id 字段
INSERT INTO `xs_farm_activity_reward` (`id`, `reward_name`, `reward_icon`, `reward_type`, `expire_sec`, `description`, `sort_order`, `create_at`, `update_at`, `reward_id`, `num`)
VALUES
    -- 大奖（4个，每人每轮只能获得1个）
    (17, '绝版装扮-星辰之愿', 'icon_grand_prize_1', 1, 31536000, '第1轮大奖：绝版装扮', 0, 0, 0, 1001, 0),
    (18, '绝版装扮-月光之羽', 'icon_grand_prize_2', 1, 31536000, '第2轮大奖：绝版装扮', 0, 0, 0, 1002, 0),
    (19, '绝版装扮-幻梦星尘', 'icon_grand_prize_3', 1, 31536000, '第3轮大奖：绝版装扮', 0, 0, 0, 1003, 0),
    (20, '绝版装扮-永恒之耀', 'icon_grand_prize_4', 1, 31536000, '第4轮大奖：绝版装扮', 0, 0, 0, 1004, 0),
    -- 小奖（10个，可重复获得）
    (21, '钻石*1000', 'icon_diamond', 1, 0, '小奖：1000钻石', 0, 0, 0, 2001, 0),
    (22, '钻石*500', 'icon_diamond', 1, 0, '小奖：500钻石', 0, 0, 0, 2002, 0),
    (23, '装扮碎片*10', 'icon_fragment', 7, 0, '小奖：10片装扮碎片', 0, 0, 0, 2003, 0),
    (24, '装扮碎片*5', 'icon_fragment', 7, 0, '小奖：5片装扮碎片', 0, 0, 0, 2004, 0),
    (25, '限定皮肤体验卡', 'icon_skin', 2, 86400, '小奖：1天限定皮肤体验', 0, 0, 0, 2005, 0),
    (26, '限定皮肤体验卡', 'icon_skin', 2, 0, '小奖：3天限定皮肤体验', 0, 0, 0, 2006, 0),
    (27, '道具礼包A', 'icon_gift', 3, 0, '小奖：随机道具礼包A', 0, 0, 0, 2007, 0),
    (28, '道具礼包B', 'icon_gift', 3, 0, '小奖：随机道具礼包B', 0, 0, 0, 2008, 0),
    (29, '精灵碎片*20', 'icon_spirit', 4, 0, '小奖：20片精灵碎片', 0, 0, 0, 2009, 0),
    (30, '精灵碎片*10', 'icon_spirit', 4, 0, '小奖：10片精灵碎片', 0, 0, 0, 2010, 0)
ON DUPLICATE KEY UPDATE reward_name=VALUES(reward_name);
```

---

## 4. 活动配置验证

### 配置规则检查

| 规则 | 检查点 | 本配置结果 |
|------|--------|------------|
| Round 数量 = 大奖个数 | 4轮 = 4个大奖 | ✅ |
| 总抽奖次数 | 6+8+12+16 = 42 | ✅ |
| 奖池概率总和 = 100% | Grand(20%) + Normal(80%) = 100% | ✅ |
| 小奖池奖品概率总和 = 100% | 10个×10% = 100% | ✅ |
| GrandPoolRate 配置 | 20% | ✅ |

### 抽奖价格总览

| 轮次 | 抽奖次数 | 单价 | 总价（全抽） |
|------|----------|------|--------------|
| 第1轮 | 6次 | 200钻 | 1200钻 |
| 第2轮 | 8次 | 600钻 | 4800钻 |
| 第3轮 | 12次 | 1000钻 | 12000钻 |
| 第4轮 | 16次 | 1400钻 | 22400钻 |

---

## 5. 数据库表初始化（如未创建）

```sql
-- xs_prayer_user_record (抽奖记录表)
CREATE TABLE IF NOT EXISTS `xs_prayer_user_record` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `uid` INT UNSIGNED NOT NULL COMMENT '用户 ID',
  `activity_id` INT UNSIGNED NOT NULL COMMENT '活动 ID',
  `round` SMALLINT UNSIGNED NOT NULL COMMENT '第几轮',
  `draw_count` SMALLINT UNSIGNED NOT NULL COMMENT '第几次抽奖',
  `reward_id` BIGINT UNSIGNED NOT NULL COMMENT '获得的奖励 ID',
  `price` INT UNSIGNED NOT NULL COMMENT '消耗的钻石',
  `dateline` INT UNSIGNED NOT NULL COMMENT '抽奖时间戳',
  PRIMARY KEY (`id`),
  KEY `idx_uid_activity` (`uid`, `activity_id`),
  KEY `idx_uid_activity_round` (`uid`, `activity_id`, `round`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='祈福抽奖用户记录表';

-- xs_prayer_user_wish_value (心愿值表)
CREATE TABLE IF NOT EXISTS `xs_prayer_user_wish_value` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `uid` INT UNSIGNED NOT NULL COMMENT '用户 ID',
  `activity_id` INT UNSIGNED NOT NULL COMMENT '活动 ID',
  `round` SMALLINT UNSIGNED NOT NULL COMMENT '第几轮',
  `wish_value` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '心愿值',
  `updated_at` INT UNSIGNED NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uid_activity_round` (`uid`, `activity_id`, `round`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='祈福抽奖用户心愿值表';

-- xs_prayer_user_progress (进度表)
CREATE TABLE IF NOT EXISTS `xs_prayer_user_progress` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '主键 ID',
  `uid` INT UNSIGNED NOT NULL COMMENT '用户 ID',
  `activity_id` INT UNSIGNED NOT NULL COMMENT '活动 ID',
  `round` SMALLINT UNSIGNED NOT NULL COMMENT '当前第几轮',
  `draw_count` SMALLINT UNSIGNED NOT NULL DEFAULT 0 COMMENT '本轮已抽次数',
  `obtained_rewards` JSON DEFAULT NULL COMMENT '已获得奖励 ID 列表 (JSON 数组)',
  `wish_value` INT UNSIGNED NOT NULL DEFAULT 0 COMMENT '当前心愿值',
  `updated_at` INT UNSIGNED NOT NULL COMMENT '更新时间戳',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_uid_activity` (`uid`, `activity_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='祈福抽奖用户进度表';
```

---

## 版本信息

- v1.0 (2026-04-14)：更新奖品 ID 使用表主键（17-30）
- v0.1 (2026-04-13)：初版，基于 PR #294
