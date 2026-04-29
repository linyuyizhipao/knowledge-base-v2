---
title: 农场多应用数据隔离
project: slp-starship
tags: [farm, appid, isolation, multi-app]
source: curated/projects/slp-starship/02-farm-appid-isolation.md
created: 2026-04-25
updated: 2026-04-28
---

# 农场多应用数据隔离（slp-starship）

## 概要

在 slp-starship 中为农场功能实现 appid=66（旧版SLP）与 appid=70（小时光）的完全数据隔离。

## 方案

- **路由层**: `consts.GetFarmRoute(appid, uid)` 返回 "local" 或 "isolated"
- **服务层**: `app/service/farm_isolated/` 镜像 `app/service/farm/`，将 `model.AppSLP` 替换为动态 `l.appid`
- **数据库**: 每张表新增 `app_id` 列（DEFAULT 66），所有查询带 `(field, app_id)` 复合索引
- **RPC 兜底**: `rpc/server/internal/farm/appid.go` 的 `resolveAppId` 函数，外部调用方不传 app_id 时自动从数据库解析

## 实施进度（2026-04-28）

### ✅ 已完成

| 阶段 | 状态 | 说明 |
|------|------|------|
| Phase 1: SQL 迁移 | ⏳ 待执行 | DDL 已写完（xs_farm_* + xs_fishpond_*），配置数据迁移 SQL 已完成 |
| Phase 2: DAO 生成 | ⏳ 待执行 | 50 条 `slpctl gen -t <表名> -d starship` 命令已列出 |
| Phase 3: 代码修复 | ✅ 已完成 | 鱼塘表 INSERT/UPDATE 补 app_id，event handler 加强校验 |
| Phase 4: RPC 层 | ✅ 已确认无需改 | `resolveAppId` 已正确处理，`SendMailToFarmMailbox` 仅写 Redis |
| dev 合并发布 | ✅ 已完成 | Jenkins #2296 构建成功 |

### Phase 3 改动清单

**鱼塘表 app_id 补充（6 个文件）:**

| 文件 | 改动 |
|------|------|
| `farm_fishpond.go` | 4 处 UPDATE 加 `app_id` 字段和 WHERE 条件 |
| `farm_upgrade.go` | UPDATE 加 `app_id` |
| `fish/farm_fishpond_fish.go` | INSERT steal_record + UPDATE fishpond_user 加 `app_id` |
| `fish/tasks/task_base.go` | INSERT book_task 加 `appid` 参数 |
| `farm_up_event.go` | UPDATE fishpond_user 加 `app_id` WHERE |
| `farm_fishpond_bait_matures_event.go` | UPDATE 加 `app_id` |

**app_id=0 处理策略（变更）:**

原方案：`appid == 0` 时兜底为 66
新方案：`appid == 0` 视为非法，打 warning 日志后 return，不继续处理

理由：SQL 加字段时已 `DEFAULT 66`，代码层面不应再兜底，必须强校验。

改动文件：`farm_fishpond_bait_matures_event.go`, `farm_fishpond_steal_fish_event.go`, `farm_fishpond_steal_fish_card_package_event.go`, `farm_fishpond_steal_fish_book_try_task_event.go`, `farm_up_event.go`, `rpc/server/internal/farm/farm_info.go`

## 数据迁移策略（简化）

**配置类数据** — 从 app_id=66 复制到 app_id=70（15 张表）
- `xs_farm_activity_config`, `xs_farm_activity_price`, `xs_farm_activity_reward`
- `xs_farm_crop_info`, `xs_farm_fish_info`, `xs_farm_fish_pond_bait`
- `xs_farm_fish_pond_deep_info`, `xs_farm_fish_pond_level`, `xs_farm_fruit`
- `xs_farm_level_info`, `xs_farm_plot_info`, `xs_farm_pretend`
- `xs_farm_pretend_group`, `xs_farm_pretend_privilege`, `xs_farm_pretend_privilege_ref`, `xs_farm_prop`

**用户数据** — 不迁移
- 用户类数据（`xs_farm_info`, `xs_farm_vip`, `xs_farm_user_*` 等）由新 app 用户自行产生
- 新 app 用户首次进入农场时，代码层显式写入其 app_id

## 5 个关键踩坑

1. **INSERT 漏写 app_id** — 40+ 处 INSERT 未写 app_id，数据被 DEFAULT 66 错误归类
2. **SaveFarm RPC 三层不一致** — proto 缺字段、handler 默认 66、调用方不传
3. **RPC Handler 内部写入依赖 DEFAULT** — 应显式写入，不依赖数据库默认值
4. **硬编码字面量 66** — 应使用 `model.AppSLP` 常量
5. **RPC 被外部调用时无法依赖传参** — 应在 server 内部 `resolveAppId` 兜底，零侵入性

## 验收 checklist

- [x] SELECT 过滤条件替换为动态参数
- [x] **全局扫描所有 INSERT/Insert/Create**
- [x] **RPC Handler 内部**的 INSERT 是否显式写 app_id
- [x] **RPC Handler 被外部调用时**，是否通过 `resolveAppId` 兜底
- [x] **全局扫描所有 `model.AppSLP` 硬编码**
- [x] 使用常量非字面量
- [x] **app_id=0 强校验**，打 warning 日志，不兜底为 66

## 完整执行清单

详见计划文件：`~/.claude/plans/dapper-orbiting-mccarthy.md`

包含：
- Phase 1: SQL DDL + 配置数据迁移（直接可执行）
- Phase 2: 50 条 DAO 生成命令
- Phase 3-5: 代码修复、RPC 确认、验证步骤