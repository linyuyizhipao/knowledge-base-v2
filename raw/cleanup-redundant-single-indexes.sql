-- ============================================================================
-- 清理 xs_farm_* 表冗余单列索引
-- 日期: 2026-04-25
-- 原则: 若已有联合索引 (col, app_id)，则删除独立的单列索引 (col)
-- 保留: UNIQUE 索引、PRIMARY KEY、多列联合索引、与 app_id 无关的复合索引
-- ============================================================================

-- 分析规则:
--   idx_farm_app (farm_id, app_id) 存在 → 删除 idx_fid / idx_farm_id (farm_id)
--   idx_uid_app (uid/belong_uid, app_id) 存在 → 删除 idx_uid (uid/belong_uid)
--   idx_team_app (team_id, app_id) 存在 → 删除 idx_team_id (team_id)
--   idx_from_uid_app (from_uid, app_id) 存在 → 删除 idx_from_uid (from_uid)

-- ============================================================================
-- 共 10 条 DROP 语句
-- ============================================================================

-- 1. xs_farm_action_log: idx_farm_app(farm_id,app_id) 覆盖 idx_fid(farm_id)
DROP INDEX idx_fid ON xs_farm_action_log;

-- 2. xs_farm_action_log_new: idx_farm_app(farm_id,app_id) 覆盖 idx_fid(farm_id)
DROP INDEX idx_fid ON xs_farm_action_log_new;

-- 3. xs_farm_cut_apply: idx_uid_app(uid,app_id) 覆盖 idx_uid(uid)
DROP INDEX idx_uid ON xs_farm_cut_apply;

-- 4. xs_farm_cut_invite: idx_team_app(team_id,app_id) 覆盖 idx_team_id(team_id)
DROP INDEX idx_team_id ON xs_farm_cut_invite;

-- 5. xs_farm_gift_box: idx_farm_app(farm_id,app_id) 覆盖 idx_farm_id(farm_id)
--    注意: 该表无 idx_belong_uid_app，故 idx_uid(belong_uid) 保留
DROP INDEX idx_farm_id ON xs_farm_gift_box;

-- 6. xs_farm_machine: idx_farm_app(farm_id,app_id) 覆盖 idx_farm_id(farm_id)
DROP INDEX idx_farm_id ON xs_farm_machine;

-- 7. xs_farm_market_transaction: idx_from_uid_app(from_uid,app_id) 覆盖 idx_from_uid(from_uid)
--    注意: 该表无 idx_to_uid_app，故 idx_to_uid(to_uid) 保留
DROP INDEX idx_from_uid ON xs_farm_market_transaction;

-- 8. xs_farm_merchant_exchange_log: idx_uid_app(uid,app_id) 覆盖 idx_uid(uid)
DROP INDEX idx_uid ON xs_farm_merchant_exchange_log;

-- 9. xs_farm_user_decoration: idx_uid_app(uid,app_id) 覆盖 idx_uid(uid)
DROP INDEX idx_uid ON xs_farm_user_decoration;

-- 10. xs_farm_vistor: idx_farm_app(farm_id,app_id) 覆盖 idx_farm_id(farm_id)
DROP INDEX idx_farm_id ON xs_farm_vistor;

-- ============================================================================
-- 以下索引保留（不冗余或 UNIQUE）
-- ============================================================================
-- idx_create_time (*)             — 时间范围查询，与 app_id 无关
-- idx_state (*)                   — 状态过滤，与 app_id 无关
-- idx_steal_key (*)               — 按 key 精确查找
-- idx_uid_date (uid,checkin_date) — 不同查询维度
-- idx_belong_uid_cs2t (belong_uid,crop_state2_time) — 不同查询维度
-- idx_team_day (team_id,day_date) — 不同查询维度
-- idx_task_id_id (task_id,id)     — 不同查询维度
-- idx_crop_id (crop_id)           — 不同查询维度
-- idx_send_uid (send_uid)         — 不同查询维度
-- idx_to_uid (to_uid)             — 不同查询维度
-- idx_farm_plot (farm_id,plot_id) — 不同查询维度
-- idx_valid_until (*)             — 时间过滤
-- idx_result_status (*)           — 状态过滤
-- uk_uid (uid) UNIQUE             — UNIQUE 索引必须保留
-- idx_uid (belong_uid) on gift_box — 无 idx_belong_uid_app 覆盖，保留
