# 搜索系统完整业务逻辑

## 概述

SLP 搜索 API (`/go/slp/search/joint`) 支持多种搜索类型：用户、房间、家族、联盟、群组、礼包、彩蛋、靓号等。采用责任链模式，按顺序执行多个 Searcher。

## API 入口

**路由**: `/go/slp/search/joint`

**Handler**: `app/api/search.go:Joint()`

**核心调用链**:
```
Joint() → MultiSearch() → BatchValidate() → Searcher序列
```

## 搜索流程图

```
用户输入关键词 keyword
    ↓
BatchValidate() 关键词校验 & Alias 解析
    ↓
┌─────────────────────────────────────────────────┐
│ 判断关键词类型                                    │
│ - 纯数字: KeywordDigitsLen4/5/6/9/236           │
│ - 非纯数字: KeywordNotPureDigits                 │
│ - 小拾光2-6位: isXiaoShiGuangRoomSearch          │
└─────────────────────────────────────────────────┘
    ↓
Alias 解析: GetAliasListByKeyword()
    ↓
┌─────────────────────────────────────────────────┐
│ Alias 类型判断                                   │
│ - AliasPrettyUid: 用户靓号 → UID                │
│ - AliasPrettyRid: 房间靓号 → RID                │
│ - AliasName: 中文靓号 → UID                     │
│ - AliasNameRoom: 房间别名 → RID                 │
│ - AliasEgg: 彩蛋                                │
└─────────────────────────────────────────────────┘
    ↓
MultiSearch() 遍历 Searcher 序列
    ↓
[egg → kol → vip888 → user → room → fleet → union → group → giftbag → starship]
    ↓
每个 Searcher: PreJudge() → Search() → AfterJudge()
    ↓
APP 隔离过滤: NeedAppIsolate()
    ↓
返回 JointSearchItem 列表
```

## Searcher 序列

| 序号 | Searcher | 搜索类型 | PreJudge 条件 | AfterJudge |
|------|----------|---------|--------------|------------|
| 1 | egg | 彩蛋 | `q.Egg != nil` | JTBreak |
| 2 | kol | KOL活动 | `len(q.RawKeyword) > 0` | JTBreak |
| 3 | vip888 | VIP888 | keyword == "vip888" | JTBreak |
| 4 | user | 用户 | `IsPretty && PrettyType != Uid` 跳过 | `PrettyType == Uid` 继续 |
| 5 | room | 房间 | `IsPretty && PrettyType != RoomId` 跳过 | `PrettyType == RoomId` JTBreak |
| 6 | fleet | 家族 | `IsPretty` 跳过 | 继续 |
| 7 | union | 联盟 | `IsPretty` 跳过 | 继续 |
| 8 | group | 群组 | `IsPretty` 跳过 | 继续 |
| 9 | giftbag | 礼包 | - | 继续 |
| 10 | starship | 星舰 | - | 继续 |

## 关键词类型 (KeywordType)

| 类型 | 说明 | 示例 | 用途 |
|------|------|------|------|
| `KeywordNotPureDigits` | 非纯数字 | "小明" | 名称搜索 |
| `KeywordDigitsLen9` | 9位数字 | "100204364" | UID/群组ID |
| `KeywordDigitsLen4` | 4位数字 | "1234" | 靓号 |
| `KeywordDigitsLen5` | 5位数字 | "12345" | 靓号 |
| `KeywordDigitsLen6` | 6位数字 | "900075" | 家族/联盟ID |
| `KeywordDigitsLen236` | 2-6位数字 | "123" | 小拾光房间号 |

## Alias 系统（别名/靓号/彩蛋）

Alias 是搜索系统的"预处理器"，将各种别名映射到实际 ID。

### Alias 类型

| PB 常量 | 说明 | 映射方向 |
|---------|------|---------|
| `AliasName` | 中文靓号 | 关键词 → UID |
| `AliasPrettyUid` | 用户靓号 | 数字 → UID |
| `AliasPrettyRid` | 房间靓号 | 数字 → RID |
| `AliasNameRoom` | 房间别名 | 名称 → RID |
| `AliasEgg` | 彩蛋 | 关键词 → Egg配置 |

### Alias 服务接口

**路径**: `rpc/server/internal/cache/alias/alias.go`

| 方法 | 功能 | 用途 |
|------|------|------|
| `GetAliasInfoByKeyword` | 单个alias信息 | `Validate` 使用 |
| `GetAliasListByKeyword` | 所有alias信息 | `BatchValidate` 使用 |
| `GetUidByPrettyId` | 靓号→UID | 用户搜索 |
| `GetPrettyIdByUid` | UID→靓号 | profile显示 |
| `GetUidByAlias` | 中文别名→UID | 名称搜索 |
| `GetRoomIdByPrettyId` | 靓号→RID | 房间搜索 |
| `GetRidByAlias` | 房间别名→RID | 别名搜索 |

### Alias 数据表

| 表名 | Alias类型 | Reload方法 |
|------|----------|------------|
| `bbc_peipei_pretty` | 用户靓号 | `reloadPrettyUidData` |
| `xsst_room_pretty` | 房间靓号 | `reloadPrettyRidData` |
| `bbc_peipei_pretty_alias` | 中文别名 | `reloadAliasUserData` |
| `bbc_search_egg` | 彩蛋 | `reloadEggData` |
| `xsst_room_pretty_user_attach` | 用户绑定房间 | `reloadPrettyAttachData` |

---

## 用户靓号系统

### 表: `bbc_peipei_pretty`

| 字段 | 说明 |
|------|------|
| `pretty_id` | 靓号数字 |
| `uid` | 用户 UID |
| `type` | 靓号类型 |
| `is_use` | 使用状态（1=使用中） |

### type 字段含义

| type | 说明 | 搜索支持 | profile显示 |
|------|------|---------|-------------|
| 1 | 未分类 | ✅ | ❌ |
| 2 | 个人靓号 | ✅ | ✅ |
| 3 | 运营发放 | ✅ | ✅ |
| 4 | 只能被搜索 | ✅ | ❌ |

**差异原因**: type=1/4 只写入 `prettyId→uid` 映射，不写入 `uid→prettyId`。

### 数据加载逻辑

```go
for _, d := range ds {
    if d.Type == 4 {
        prettyUidOnlySearchData[d.PrettyId] = ...  // 只搜索
    } else if d.Type == 2 || d.Type == 3 {
        uidPrettyMap[d.Uid] = d.PrettyId           // 可显示
    } else {
        newPrettyMap[d.PrettyId] = ...             // type=1: 只搜索
    }
}
```

---

## 房间靓号系统

### 表: `xsst_room_pretty`

| 字段 | 说明 |
|------|------|
| `pretty_id` | 靓号数字 |
| `room_id` | 房间 RID |
| `alias` | 房间别名（中文） |
| `show_type` | 展示类型 |
| `sex` | 性别定向 |
| `weight` | 权重（用于随机分配） |

### show_type 字段含义

| show_type | 说明 | 适用场景 |
|-----------|------|---------|
| 0 | 全量展示 | 所有用户可见 |
| 1 | 新用户展示 | 注册24小时内 |
| 2 | 老用户展示 | 注册超过24小时 |
| 3 | 只能被搜索 | 仅搜索可见，不推荐 |

### 性别定向

| sex | 说明 |
|-----|------|
| 0 | 男女都展示 |
| 1 | 男性展示 |
| 2 | 女性展示 |

### 房间靓号查询流程

```
GetRoomIdByPrettyId(prettyId, searcherId)
    ↓
判断搜索者是否新用户（注册时间 < 24小时）
    ↓
获取搜索者性别
    ↓
选择对应的数据池:
  - 新用户+男: prettyRidOnlyNewMaleData
  - 新用户+女: prettyRidOnlyNewFemaleData
  - 老用户+男: prettyRidOnlyOldMaleData
  - 老用户+女: prettyRidOnlyOldFemaleData
    ↓
按权重随机选择房间（alias_sample）
    ↓
缓存结果 12小时: xs.user.search.pretty.{uid}.{prettyId}
```

### 房间别名查询流程

```
GetRidByAlias(aliasName)
    ↓
从 prettyRidAliasData 获取所有房间+权重
    ↓
按权重排序
    ↓
按权重概率随机选择房间
    ↓
返回 RID
```

### 用户绑定房间

表: `xsst_room_pretty_user_attach`

用于让特定用户优先进入指定房间（绑定关系）。

```go
func randAttachIfExist(uid, rids) uint32 {
    if rid, ok := prettyUidAttach[uid]; ok {
        for _, r := range rids {
            if r == rid { return rid }  // 优先返回绑定房间
        }
    }
    return 0
}
```

---

## 各 Searcher 详细逻辑

### User Searcher

**文件**: `usersearcher.go`

**搜索分支**:
- `KeywordDigitsLen9`: `search9DigitKeyword()` → 按UID查询
- `非纯数字`: `searchNon9DigitKeyword()` → 名称搜索

**流程**:
```
关键词 → uint32 → UserProfile.Get()
    ↓
用户有效性检查（deleted, UID范围）
    ↓
APP隔离: NeedAppIsolate(searcherAppId, targetAppId)
    ↓
红人标签 → 返回结果
```

### Room Searcher

**文件**: `roomsearcher.go`

**搜索分支**:
- `非纯数字`: 名称搜索 → `SearchRoomByName`
- `纯数字(小拾光AppId=70)`: `searchXiaoShiGuangRoomByShowRid`
- `纯数字(其他APP)`: 直接按RID查询

**小拾光特殊处理**:
```
keyword → xs_chatroom_map(show_rid) → 真实rid
    ↓
xs_chatroom → 房间详情
    ↓
APP隔离检查 → 返回结果(含show_rid)
```

### Fleet Searcher

**文件**: `fleetsearcher.go`

**触发条件**:
- 6位数字 > 90000 → 按GID查询
- 名称搜索 → `SearchFleet`

### Union Searcher

**文件**: `unionsearcher.go`

**触发条件**:
- 6位数字 >= 100000 → 按ID查询
- 名称搜索 → `SearchUnion`

### Group Searcher

**文件**: `groupsearcher.go`

**触发条件**: 仅支持9位数字群组ID

**返回**: 群组信息 + 是否官方群组 + 是否在群内

### Egg Searcher

**文件**: `eggsearcher.go`

**触发**: `q.Egg != nil`（由 Alias 解析设置）

**跳转类型**:
| RedirectType | 说明 |
|--------------|------|
| 0 | 个人主页 |
| 1 | 房间 |
| 2 | 私聊 |
| 3 | 剧本 |
| 4-7 | 桌游类 |

---

## APP 隔离机制

### 隔离配置

**文件**: `app/model/const.go` + `app/utils/isolation.go`

```go
// 隔离app显示的配置，不在配置里的不隔离
var isolateAppGroupMap = map[AppID][]AppID{
    AppSLP:           {AppSLP},           // 不夜星球：只能搜到不夜用户
    AppXiaoShiGuang:  {AppXiaoShiGuang},  // 小拾光：只能搜到小拾光用户
    AppYinLang:       {AppYinLang},       // 音浪：只能搜到音浪用户
    AppChongYa:       {AppChongYa},       // 冲鸭：只能搜到冲鸭用户
    // ...
}
```

### 隔离开关配置

```go
Isolation = &isolationService{
    config: &IsolationConfig{
        Enabled:            true,  // 总开关开启
        SearchEnabled:      true,  // 搜索隔离：全量启用
        PrivateChatEnabled: true,  // 私聊隔离：全量启用
        RoomEnabled:        true,  // 房间隔离：全量启用
    },
}
```

### 隔离检查逻辑

```go
func NeedAppIsolate(curAppId, targetAppId AppID) bool {
    allowAppIds := isolateAppGroupMap[curAppId]
    for _, v := range allowAppIds {
        if v == targetAppId { return false }  // 允许
    }
    return true  // 需隔离
}
```

### 用户靓号搜索隔离流程图

```
用户输入靓号 keyword (如 "888")
    ↓
BatchValidate() 解析 Alias
    ↓
GetAliasListByKeyword() → 检查 AliasPrettyUid
    ↓
找到靓号映射 → 获取 UID (全局映射，不区分APP)
    ↓
UserSearcher.search9DigitKeyword()
    ↓
UserProfile.Get(uid) → 获取用户 profile，包含 app_id
    ↓
┌─────────────────────────────────────────────────────┐
│ APP 隔离检查 (usersearcher.go:457-468)              │
│                                                     │
│ 1. 获取搜索者 appId: searcherAppId = q.AppId        │
│ 2. 检查隔离开关: IsSearchIsolationEnabled(appId)    │
│ 3. 获取目标用户 appId: targetAppId = profile.AppId  │
│ 4. 隔离判断: NeedAppIsolate(searcherAppId, targetAppId) │
│                                                     │
│ isolateAppGroupMap[searcherAppId] 包含 targetAppId? │
│   - 是 → 不隔离，返回搜索结果                        │
│   - 否 → 需隔离，返回 nil (用户搜不到)               │
└─────────────────────────────────────────────────────┘
    ↓
┌──────────────┬──────────────┐
│  不需要隔离   │   需要隔离    │
│  返回用户信息 │   返回空结果  │
└──────────────┴──────────────┘
```

### 靓号跨APP场景示例

| 场景 | 靓号绑定用户APP | 搜索者APP | 是否能搜到 |
|------|---------------|----------|-----------|
| 靓号888绑定不夜用户 | AppSLP(66) | AppSLP(66) | ✅ 能搜到 |
| 靓号888绑定不夜用户 | AppSLP(66) | AppXiaoShiGuang(70) | ❌ 隔离，搜不到 |
| 靓号888绑定小拾光用户 | AppXiaoShiGuang(70) | AppSLP(66) | ❌ 隔离，搜不到 |
| 靓号888绑定小拾光用户 | AppXiaoShiGuang(70) | AppXiaoShiGuang(70) | ✅ 能搜到 |

**关键点**：靓号映射（`prettyId→uid`）是全局的，不区分APP。但搜索结果会根据搜索者和目标用户的APP进行隔离过滤。

### 名称搜索隔离流程

```
用户输入名称 keyword (如 "小明")
    ↓
UserSearcher.searchNon9DigitKeyword()
    ↓
UserProfile.SearchByName(keyword, appId) → 按名称搜索
    ↓
遍历搜索结果，对每个用户：
    ↓
┌─────────────────────────────────────────────────────┐
│ APP 隔离检查 (usersearcher.go:547-558)              │
│                                                     │
│ if NeedAppIsolate(searcherAppId, targetAppId) {     │
│     continue  // 跳过该用户，不加入结果列表          │
│ }                                                   │
└─────────────────────────────────────────────────────┘
    ↓
返回过滤后的用户列表
```

### 隔离开关

| 功能 | 开关字段 | 说明 |
|------|---------|------|
| 用户搜索 | `SearchEnabled` | 控制搜索结果是否隔离 |
| 房间搜索 | `SearchEnabled` | 控制房间搜索是否隔离 |
| 私聊 | `PrivateChatEnabled` | 控制私聊是否隔离 |
| 进房 | `RoomEnabled` | 控制进房是否隔离 |
| 礼物面板 | `GiftPanelEnabled` | 控制礼物面板是否隔离 |

---

## 小拾光搜索特殊处理

### BatchValidate 中的处理

```go
isXiaoShiGuangRoomSearch := q.IsAllDigits && q.AppId == 70 && lenK >= 2 && lenK <= 6

if !isXiaoShiGuangRoomSearch {
    // 正常 alias 检查（所有类型）
} else {
    // 只检查 AliasPrettyUid，跳过 AliasPrettyRid
}
```

**原因**: 小拾光使用 `show_rid`（2-6位），走正常靓号流程会把 `show_rid` 替换成真实 `rid`。

---

## 搜索结果结构

```go
type JointSearchItem struct {
    Type pb.JointSearchItemType  // 类型
    Id   uint32                  // ID
    Name string                  // 名称
    Icon string                  // 头像
    
    User     *JointSearchUserItem     // 用户
    Room     *JointSearchRoomItem     // 房间（含pretty_id/show_rid）
    Fleet    *JointSearchFleetItem    // 家族
    Union    *JointSearchUnionItem    // 联盟
    Group    *JointSearchGroupItem    // 群组
    Egg      *JointSearchEggItem      // 彩蛋
    KolBanner *JointSearchKolBannerItem // KOL banner
    KolRoom   *JointSearchKolRoomItem   // KOL 房间
}
```

---

## 排查记录

### 2026-04-30: 小拾光搜不到用户靓号

**根因**: `BatchValidate` 中小拾光2-6位纯数字搜索跳过了所有alias检查。

**修复**: else分支中单独检查 `AliasPrettyUid`。

### 2026-04-30: profile/home prettyUid alpha无值

**根因**: alpha靓号type=1，dev靓号type=3。type=1不写入 `uidPrettyMap`。

**解决**: 修改靓号发放数据，type改为2或3。

---

## 相关文件速查

| 模块 | 文件 |
|------|------|
| API入口 | `app/api/search.go` |
| 搜索流程 | `app/service/search/search.go` |
| 关键词校验 | `app/service/search/query.go` |
| User Searcher | `app/service/search/usersearcher.go` |
| Room Searcher | `app/service/search/roomsearcher.go` |
| Alias服务 | `rpc/server/internal/cache/alias/alias.go` |
| 用户靓号加载 | `rpc/server/internal/cache/alias/prettyuid.go` |
| 房间靓号加载 | `rpc/server/internal/cache/alias/prettyrid.go` |
| 隔离服务 | `app/utils/isolation.go` |