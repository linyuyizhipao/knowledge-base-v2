# 农场多应用数据隔离（farm appid isolation）

> 在 slp-starship 中支持 appid=66（旧版 SLP）与 appid=70（小时光）的农场数据完全隔离

**创建**: 2026-04-25

---

## 背景

slp-starship 的农场功能原本只为 appid=66 设计，所有数据库查询使用 `model.AppSLP`（即 66）作为硬编码过滤条件。新增 appid=70（小时光）后，需要在同一代码库内实现两个应用的农场数据完全隔离。

---

## 架构方案

### 数据库改造

所有 xs_farm_* 表（46张）新增 `app_id int unsigned DEFAULT 66`，加 `(farm_id, app_id)` 或 `(id, app_id)` 复合索引。

### 双服务 + 路由分发

```
API Layer (app/api/)
    │
    ├─ consts.GetFarmRoute(appid, uid)
    │   ├─ "local"    → app/service/farm/       (原服务，appid=66)
    │   └─ "isolated" → app/service/farm_isolated/ (新服务，动态 appid)
    │
    └─ 根据路由结果分发到对应 Service
```

- **farm/** — 原始农场服务，代码不变
- **farm_isolated/** — 镜像目录，将硬编码 `model.AppSLP` 替换为动态 `l.appid`
- 路由逻辑在 `consts/farm_route.go`，支持全局模式 + appid 路由 + 用户级覆盖

### Model/DAO 改动

- Model 加 `Appid uint32` 字段
- DAO 方法增加 `appid uint32` 参数，所有查询加 `Where("app_id=?", appid)`
- 使用常量，禁止硬编码

### 隔离版代码结构

```
/rpc/server/internal/farm/
├── isolated/              ← 隔离版新代码（高内聚）
│   ├── base.go
│   ├── service/
│   ├── logic/
│   └── config.go
└── farm_crop.go          ← 原有代码（不动）
```

**调用关系**:
```
API → appid=66 → localFarm → 原有 service → DAO(appid=66)
    → appid=70 → isolatedFarm → isolated/service → DAO(appid=70)
```

### RPC resolveAppId 兜底

很多 RPC handler 会被外部接入，修改 proto 增加 `app_id` 侵入性大。

**方案**: server 内部 `resolveAppId` 函数，当 app_id=0 时从数据库自动解析：

```
resolveAppId(ctx, uid, appId)
  ├─ appId > 0 → 直接返回
  ├─ 已有农场 → 返回农场 app_id
  ├─ 砍价队员 → 返回队员 app_id
  ├─ 砍价队长 → 返回队长 app_id
  └─ 默认 66
```

涉及 handler: `SendFarmCommodity`、`GivePretend`、`SendLimitCropPermission`、`BuyMonthCard`、`BuyUnionMonthCard`

### 上线策略

1. **测试阶段**: 用户级覆盖，测试账号走 isolated
2. **灰度阶段**: 扩大用户覆盖范围
3. **全量切换**: 全局模式改为 isolated
4. **回退**: 全局模式改回 local

---

## 关键踩坑记录

### 1. INSERT 操作漏写 app_id（最严重）

**问题**: farm_isolated 中有 40+ 处 INSERT 使用 `g.Map{...}` 或 `&pb.EntityXsFarmInfo{...}` 写入数据，均未设置 `app_id`。由于 MySQL DEFAULT 为 66，新用户在 appid=70 创建的农场数据实际被标记为 appid=66。

**修复**: 所有 INSERT 的 `g.Map` 中补 `"app_id": uint32(l.appid)`；struct 插入中补 `AppId: uint32(l.appid)`。

**教训**: **迁移后必须对所有 INSERT/Insert/Create 调用做全局扫描，不能只关注 SELECT/Where 的过滤条件。**

### 2. SaveFarm RPC 创建农场时 app_id=66

**问题**: 创建农场涉及三个层面的问题：

| 层级 | 问题 | 修复 |
|------|------|------|
| Proto 定义 | `ReqSaveFarm` 缺少 `app_id` 字段 | proto 加 `uint32 app_id = 3` |
| RPC Handler | `SaveFarm` 内部 `appid := req.GetAppId(); if appid == 0 { appid = 66 }`，但所有 INSERT 已经正确写了 `appid` 变量 | 修复后依赖调用方传参 |
| 调用方 | farm_isolated 的 `client.StarshipFarm.SaveFarm()` 没传 `AppId` | 改为 `AppId: uint32(l.appid)` |

**教训**: RPC 协议的入参、Handler 的默认值、调用方的传参，三者必须一致检查。

### 3. RPC Handler 内部写入也需要 app_id

**问题**: 即使 RPC 服务本身只处理 appid=66 用户（路由在 API 层），内部的 INSERT（如 `XsFarmVip`、`XsFarmLimitCropPermission`）也需要显式写 app_id，不能依赖数据库 DEFAULT。

**修复**: 所有 RPC handler 的 INSERT/UPDATE 补 `"app_id": uint32(model.AppSLP)`，使用常量而非硬编码数字 66。

**教训**: 显式写入永远比依赖 DEFAULT 更安全——万一 DEFAULT 变了或表被迁移，代码行为不变。

### 4. 硬编码数字 66 vs 常量

**问题**: 初步修复时直接写了 `66` 字面量。

**修复**: 统一使用 `model.AppSLP` 常量（`app/model/const.go` 中定义）。

**教训**: 永远用常量，不用字面量。代码审查时一眼就能看出含义。

### 5. RPC 被外部调用时无法依赖调用方传 app_id

**问题**: 很多 RPC handler（如 `SendFarmCommodity`、`BuyMonthCard`、`GivePretend`、`SendLimitCropPermission`）会被其他项目组接入，这些外部调用方不传 `app_id`，RPC handler 内部的 INSERT 全部使用 `model.AppSLP`（66）兜底，导致 appid=70 用户的数据被错误标记为 66。

**为什么不改 proto**: 修改 proto 增加 `app_id` 字段需要外部调用方同步改造，侵入性大、协调成本高。

**修复方案**: 在 RPC server 内部创建 `resolveAppId` 兜底函数，不依赖调用方传参。

**教训**: 对于会被外部接入的 RPC 服务，不要依赖调用方传参，应在 server 内部做数据兜底。零侵入性。

---

## 实施计划

### Task 概览

| Task | 内容 |
|------|------|
| **Task 1** | 创建开发分支 `feature/farm-appid-isolation` |
| **Task 2** | 生成 SQL 迁移脚本（46张表 ALTER TABLE） |
| **Task 2.5** | 后续新 app_id 数据迁移计划（配置数据拷贝） |
| **Task 3** | Model 加 Appid 字段（46个文件） |
| **Task 4** | DAO internal 加 Appid 列名（46个文件） |
| **Task 5** | DAO 扩展方法加 appid 参数 |
| **Task 6** | 创建农场路由配置（consts/farm_route.go） |
| **Task 7** | 创建 RPC isolated 目录结构 |
| **Task 8** | API 路由转发实现 |
| **Task 9** | 旧代码 DAO 调用适配 |
| **Task 10** | 单元测试 |
| **Task 11** | 最终提交与合并准备 |

### Task 2: SQL 迁移脚本

46张 `xs_farm_*` 表新增 `app_id int unsigned DEFAULT 66` 列，加 `(farm_id, app_id)` 或 `(id, app_id)` 复合索引。SQL 按实际需求用脚本生成，不在此列出。

### Task 2.5: 后续新 app_id 数据迁移计划

当需要支持新 app_id（如 71、72...）时，需将已有配置数据从 app_id=66 拷贝到新 app_id。

**迁移原则**:

| 原则 | 说明 |
|------|------|
| **全量拷贝** | 老 app_id=66 的所有农场配置数据完整复制 |
| **不改逻辑** | 新 app_id 复用现有代码，仅改数据层面过滤值 |
| **独立主键** | INSERT 时生成新自增主键 |
| **双向隔离** | 迁移后两个 app_id 数据各自独立 |

**核心迁移脚本模板**:

```sql
SET @new_app_id = 71;
SET @old_app_id = 66;

-- 配置类（如商品表）：全量复制
INSERT INTO xs_farm_commodity (commodity_name, commodity_type, price, icon, app_id, ...)
SELECT commodity_name, commodity_type, price, icon, @new_app_id AS app_id, ...
FROM xs_farm_commodity WHERE app_id = @old_app_id;

-- 用户数据类（如农场信息）：按 uid 拷贝
INSERT INTO xs_farm_info (belong_uid, farm_name, ..., app_id, ...)
SELECT belong_uid, farm_name, ..., @new_app_id AS app_id, ...
FROM xs_farm_info WHERE app_id = @old_app_id;
```

**9张核心表迁移策略**:

| 表 | 类型 | 策略 |
|----|------|------|
| `xs_farm_commodity` | 全局配置 | 全量复制 |
| `xs_farm_info` | 农场基础 | 按 belong_uid |
| `xs_farm_vip` | VIP 记录 | 按 uid |
| `xs_farm_limit_crop_permission` | 种子权限 | 按 uid |
| `xs_farm_month_card` | 月卡 | 按 uid |
| `xs_farm_union_month_card` | 联合月卡 | 按 uid |
| `xs_farm_pretend` | 假装数据 | 按 farm_id |
| `xs_farm_cut_team` | 砍价队伍 | 按 team_uid |
| `xs_farm_cut_team_member` | 砍价队员 | 按 uid |

**迁移步骤**:

```
1. 备份老 app_id=66 数据
2. 确认新 app_id 无残留数据
3. 逐表执行拷贝（基础 → 用户 → 附属）
4. 验证：新老数据量一致
5. 代码侧：新 app_id 加入路由判断
6. 灰度验证
```

**注意事项**:
- **配置类数据**（如商品表）全量复制
- **关联关系数据**（如砍价队伍）确保关系链完整迁移
- **时间敏感数据**（如月卡到期时间）保持原始时间
- **幂等性**：先 DELETE 再 INSERT，或使用 INSERT IGNORE

### Task 6: 路由配置

```go
// consts/farm_route.go
type FarmRouteType string

const (
    FarmRouteLocal    FarmRouteType = "local"
    FarmRouteIsolated FarmRouteType = "isolated"
)

type FarmRouteConfig struct {
    GlobalMode     FarmRouteType
    RouteByAppID   map[model.AppID]FarmRouteType
    UserOverride   map[uint32]FarmRouteType
}

func GetFarmRoute(appid model.AppID, uid uint32) FarmRouteType
func SetFarmUserOverride(uid uint32, route FarmRouteType)
func SetFarmGlobalMode(route FarmRouteType)
```

---

## 验收 checklist

- [ ] SELECT 过滤条件中的 appid 替换为动态参数
- [ ] **全局扫描所有 INSERT/Insert/Create 调用**，确保写入 app_id
- [ ] **RPC Handler 内部**的 INSERT 是否显式写 app_id（不能依赖 DEFAULT）
- [ ] **RPC Handler 被外部调用时**，是否通过 `resolveAppId` 兜底获取正确的 app_id
- [ ] **全局扫描所有 `model.AppSLP` 硬编码**，确认是否需要动态解析
- [ ] 使用常量（`model.AppSLP`）而非字面量（66）
- [ ] 编译通过：`go build ./app/... && go build ./rpc/...`

---

## 回退方案

1. 修改 `consts/farm_route.go`，设置 `GlobalMode: FarmRouteLocal`
2. 所有请求走原有代码
3. 数据库 appid 字段不影响旧数据（默认 66）

---

## 相关文件索引

| 文件 | 角色 |
|------|------|
| `consts/farm_route.go` | 路由判断逻辑 |
| `app/model/const.go` | `model.AppSLP` 常量定义 (=66) |
| `app/service/farm/` | 原始农场服务 |
| `app/service/farm_isolated/` | 隔离版农场服务 |
| `rpc/server/internal/farm/` | RPC Handler（旧服务） |
| `rpc/server/internal/farm/appid.go` | resolveAppId 兜底函数 |
| `rpc/server/internal/farm/isolated/` | RPC Handler（隔离版） |
| `proto/rpc/rpc_farm.proto` | 农场 RPC 协议 |
| `docs/sql/farm_appid_migration.sql` | 数据库迁移脚本 |

---

## SQL 变更记录

> 本次迭代涉及的数据库变更统一维护在此，后续新增 SQL 直接追加

### app_id 隔离审计

**审计日期**: 2026-04-27

**第一阶段结论**（uid 天然隔离）: `uid` / `belong_uid` 本身即 app 维度标识（app 66 的 uid=100 与 app 70 的 uid=100 不是同一个人），因此 `WHERE uid=?` / `WHERE belong_uid=?` / `WHERE farm_id=?` 已天然实现数据隔离。

**第二阶段调整**（统一加 app_id）: 为保持代码风格统一、防止未来迁移或数据修复场景下的混淆，**`farm_isolated` 中所有表有 `app_id` 字段的查询，一律显式加 `app_id` 过滤条件**。

**隔离保证层级**:
- **INSERT 写入**: 所有 INSERT 必须显式写入 `app_id`
- **查询过滤**: 统一加 `app_id` WHERE 条件（即使 uid/farm_id 已天然隔离）
- **路由分发**: API 层通过 `GetFarmRoute` 确保请求走正确的 service 实例

**DAO 扩展方法改动**:
- `xs_farm_user_seafood.go`: `GetUserFishRecords`, `DeleteZeroUserFishRecords`, `GetUserAllSeafoodRecords`, `GetUserFishSeafoodWeightGrade` 均新增 `appid model.AppID` 参数
- `xs_farm_machine.go`: `GetByMachineIdAndUid`, `ReduceDuration` 均新增 `appid model.AppID` 参数
- 旧 `farm/` 服务调用方传 `model.AppSLP`，`farm_isolated/` 传 `l.appid`

**鱼塘相关表**（暂缺 app_id 字段，仍按 uid 查询）:
- `xs_fishpond_user` — 鱼塘用户主表
- `xs_fishpond_steal_record` — 偷鱼记录
- `xs_fishpond_steal_fish_summary` — 偷鱼统计
- `xs_fishpond_user_book_task` — 鱼塘图鉴任务
- `xs_fishpond_fish_proficiency` — 鱼熟练度

---

## 审计报告（2026-04-27）

### 审计范围

对 `farm_isolated`、旧 `farm/`、`rpc/server/internal/farm/` 三个模块进行全面 app_id 隔离审查，包括：
1. 配置加载函数是否按 app_id 过滤
2. 所有 DAO 查询是否包含 app_id 条件
3. RPC 发奖场景是否存在硬编码奖励 ID
4. 跨 app 资源使用是否被有效阻止

### 配置加载函数修复

**问题**: `GetCropList`、`GetFruitAll` 等配置加载函数原本不带 app_id 参数，查询时不加 `WHERE app_id=?`，导致 app 66 和 app 70 共享同一份配置数据。

**涉及表**: `xs_farm_crop_info`（种子配置）、`xs_farm_fruit`（果实配置）

**修复**: 所有配置加载函数新增 `appid model.AppID` 参数：

| 函数 | 文件 | 修复方式 |
|------|------|----------|
| `GetCropList` | `config_crop.go` | `Where("app_id=?", uint32(appid))` |
| `GetCropConfig` | `config_crop.go` | 同上 |
| `MGetCropConfig` | `config_crop.go` | 同上 |
| `GetCropsByLevel` | `config_crop.go` | 同上 |
| `MGetCropStructByExp` | `config_crop.go` | 同上 |
| `MGetCropLevelByExp` | `config_crop.go` | 同上 |
| `GetCropLevelByExp` | `config_crop.go` | 同上 |
| `GetFruitAll` | `config_fruit.go` | `Where("app_id=?", uint32(appid))` |
| `GetFruitConfig` | `config_fruit.go` | 同上 |
| `MGetFruit` | `config_fruit.go` | 同上 |

**调用方适配**:
- `farm_isolated/` 中所有调用者传 `l.appid`
- 旧 `farm/` 中所有调用者传 `model.AppSLP`

### RPC 发奖场景审计

**审计目标**: 检查是否存在硬编码奖励 ID 的场景（如排行榜发奖、业务触发发奖直接写死 ID）。

**结论**: **未发现硬编码奖励 ID**。所有奖励发放均通过数据库配置驱动：
- 活动奖励 → `XsFarmActivityReward` 表配置
- 商品奖励 → `XsFarmCommodity` 表配置
- 道具奖励 → `XsFarmProp` 表配置
- 伪装数据 → `XsFarmPretend` 表配置

**但发现新问题**: RPC handler 查询这些配置表时未过滤 app_id，导致 app 66 和 app 70 可能读取到对方的配置。

#### RPC farm_commodity.go 修复

**文件**: `rpc/server/internal/farm/farm_commodity.go`

| 位置 | 问题 | 修复 |
|------|------|------|
| `SendFarmCommodity` L76 | farm 查询未带 app_id | 新增 `resolveAppId` 获取 appid，`Where("belong_uid=? and app_id=?", uid, appid)` |
| `pretendRepository` | `XsFarmPretend` 查询缺 app_id | 函数签名加 `appid uint32`，查询加 `Where("id in (?) and app_id=?", ids, appid)` |
| `farmPropHandle` | `XsFarmProp` 查询缺 app_id | 函数签名加 `appid uint32`，查询加 `Where("id in (?) and app_id=?", ids, appid)` |
| `afterSendCommodity` | `XsFarmPretend` + `XsFarmCropInfo` 查询缺 app_id | `AfterSendCommodityParams` 新增 `Appid` 字段，两处查询均加 app_id |

### farm_isolated 代码修复清单

以下文件在本次审计中补充了 app_id 过滤：

| 文件 | 修复内容 |
|------|----------|
| `farm.go` | CropList 限购种子查询 (L509), Plant 限购查询 (L617), Plant action_log (L675), Pick action_log (L825), Pick barn 写入 (L839/856), Watering action_log (L975), GiftPackButtons (L1129/1184), XsFarmFruit 查询 (L754), Plant 限购权限更新 (L691) |
| `farm_fishpond.go` | CastBaitHome 鱼饵道具查询 (L64), CastBait action_log (L237/249), Fish 调用 (L294), FishpondSellFish farmInfo 查询 (L575) |
| `farm_jack.go` | XsFarmPlot 查询 (2处), XsFarmStealKey 查询 (3处), XsFarmCropInfo, XsFarmPretend, XsFarmFruit, XsFarmBarn, XsFarmInfo, XsFarmMarketPrice 均加 app_id |
| `farm_bruce.go` | XsFarmBarn 查询加 app_id |
| `farm_upgrade.go` | GetCropsByLevel 调用传 appid |
| `market.go` | GetCropList 调用传 appid |

### 跨 app 资源使用防护

**种植场景**: `farm_isolated/farm.go:Plant` 中通过以下方式防止跨 app 种植：
1. 查询地块时带 `app_id` 条件（`farm_id + app_id + idx`）
2. 查询种子配置时带 `app_id` 条件（通过 `GetCropConfig(ctx, cropId, l.appid)`）
3. 写入 action_log 时带 `app_id`
4. 写入 barn 时带 `app_id`

**偷取场景**: `farm_isolated/farm_jack.go` 中：
1. 查询 steal_key 时带 `app_id`
2. 查询 pretend 数据时带 `app_id`
3. 查询 crop/fruit 配置时带 `app_id`

**关键原则**: `l.appid` 来自 `farm_isolated` 的 Logic 初始化，由 API 层路由分发时传入，外部无法伪造。

### 数据库表 app_id 覆盖清单

**已有 app_id 字段且查询已加过滤的表（24 张）**:
`xs_farm_info`, `xs_farm_plot`, `xs_farm_crop`, `xs_farm_barn`, `xs_farm_user_checkin`, `xs_farm_user_duration_prop`, `xs_farm_action_log`, `xs_farm_action_log_new`, `xs_farm_market_price`, `xs_farm_market_transaction`, `xs_farm_fish_pond_bait`, `xs_farm_steal_key`, `xs_farm_pretend`, `xs_farm_gift_pack_record`, `xs_farm_limit_crop_permission`, `xs_farm_cut_*`（5张）, `xs_farm_user_seafood`, `xs_farm_user_decoration`, `xs_farm_user_daily_pay_week`, `xs_farm_user_bless_record`, `xs_farm_vistor`, `xs_farm_pretend_privilege`, `xs_farm_crop_info`, `xs_farm_fruit`, `xs_farm_commodity`, `xs_farm_prop`

**缺少 app_id 字段的表（5 张）— 待 SQL 迁移**:
- `xs_fishpond_user` — 鱼塘用户主表
- `xs_fishpond_steal_record` — 偷鱼记录
- `xs_fishpond_steal_fish_summary` — 偷鱼统计
- `xs_fishpond_user_book_task` — 鱼塘图鉴任务
- `xs_fishpond_fish_proficiency` — 鱼熟练度

### 待处理事项

1. **SQL 迁移**: 给 5 张鱼塘表添加 `app_id` 列（参考 Phase 1 建议）
2. **DAO 重生成**: 迁移后重新生成带 app_id 的 DAO 代码
3. **farm_isolated 补充**: 鱼塘相关查询统一加 app_id（待 Phase 1 完成后）
