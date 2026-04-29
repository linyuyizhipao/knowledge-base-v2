# 装扮类物品使用转发

> 装扮类物品（头像框、气泡、座驾等）使用时，PHP 扣库存后转发到 slp-go 处理有效期累加

**版本**: 1.0 | **更新**: 2026-04-14

---

## 业务背景

### 问题

原有装扮类物品使用逻辑完全在 PHP 侧处理，包括：
- 扣减背包库存
- 有效期累加
- 缓存清理
- 消费记录

当装扮系统升级到 slp-go 的"新装扮"体系后，PHP 侧无法直接操作新装扮的数据结构。

### 解决方案

采用**转发模式**：
- PHP 侧：扣库存 + 消费记录（复用现有逻辑）
- slp-go 侧：调用装扮 RPC 添加有效期 + 自动佩戴

---

## 判断条件

```php
// UserCommodity::use() 入口处
if (\CommodityModel::isDecoType($this->_comm->type)) {
    $extra = json_decode($this->_comm->extra, true);
    if (!empty($extra['pretend_id']) && $extra['pretend_id'] > 0) {
        // 转发到 slp-go
    }
}
```

| 条件 | 说明 |
|------|------|
| `isDecoType($type)` | 装扮类型：header/mounts/bubble/effect/decorate/ring 等 |
| `extra.pretend_id > 0` | 物品关联到新装扮系统的装扮 ID |

---

## 项目职责分工

| 项目 | 职责 | 核心模块 |
|------|------|----------|
| **slp-php** | 扣减背包库存 + 消费记录 + 转发 RPC | `UserCommodity::use()` |
| **slp-go** | 装扮有效期累加 + 自动佩戴 | `rpc.pretend.UseDecorateCommodity` |

---

## 跨项目数据流

```
┌─────────────────────────────────────────────────────────────┐
│                    用户使用装扮类物品                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PHP: UserCommodity::use()                                  │
│  判断：isDecoType(type) && extra.pretend_id > 0?           │
└─────────────────────────────────────────────────────────────┘
                            ↓
            ┌───────────────┴───────────────┐
            │ 是                            │ 否
            ↓                               ↓
    ┌───────────────────┐           ┌───────────────────┐
    │ PHP 扣库存         │           │ PHP 本地事务      │
    │ + 消费记录         │           │ （原有逻辑）      │
    └───────────────────┘           └───────────────────┘
            ↓
    ┌───────────────────┐
    │ 计算 seconds       │
    │ period * 24h       │
    │ + period_hour * h  │
    └───────────────────┘
            ↓
    ┌───────────────────┐
    │ RPC: UseDecorate   │
    │ Commodity()        │
    └───────────────────┘
            ↓
    ┌───────────────────┐
    │ slp-go RPC        │
    │ GetCateIdAndGroup │
    │ Id(pretend_id)    │
    └───────────────────┘
            ↓
    ┌───────────────────┐
    │ sendGroupPretend  │
    │ → 有效期累加       │
    │ → 自动佩戴         │
    └───────────────────┘
            ↓
    ┌───────────────────┐
    │ 返回结果           │
    │ success: true/false│
    └───────────────────┘
```

---

## RPC 接口定义

### 请求

```json
{
  "uid": 用户ID,
  "pretend_id": 装扮ID,
  "seconds": 有效期秒数
}
```

### 响应

```json
{
  "success": true,
  "msg": ""
}
```

---

## 有效期计算

```php
// PHP 侧计算
$seconds = ($this->_comm->period * 24 * 3600 + $this->_comm->period_hour * 3600) * $this->_use_num;
```

| 字段 | 说明 | 单位 |
|------|------|------|
| `period` | 有效期天数 | 天 |
| `period_hour` | 有效期小时数 | 小时 |
| `use_num` | 使用数量 | 个 |

---

## 数据表

| 表 | 项目 | 说明 |
|-----|------|------|
| `xs_user_commodity` | slp-php | 用户背包库存 |
| `xs_pay_change` | slp-php | 消费记录 |
| `xs_user_pretend_list` | slp-go | 用户装扮拥有记录 |
| `bbc_pretend_info` | slp-go | 装扮信息表（内存） |

---

## 配置项

### PHP 侧

- 物品 `extra.pretend_id` 配置：物品表的 `extra` JSON 字段中配置 pretend_id

### slp-go 侧

- Source 类型：`decorate_commodity` 需在 `addFragmentSourceMap` 中注册

---

## 问题排查

### 1. 物品使用不转发

**检查项**：
- 物品类型是否在 `CommodityModel::$decorates` 列表中
- 物品 `extra.pretend_id` 是否 > 0

### 2. RPC 调用失败

**检查项**：
- slp-go rpc.pretend 服务是否正常
- pretend_id 是否在 `bbc_pretend_info` 表中存在
- 查看 slp-go 日志：`UseDecorateCommodity` 相关错误

### 3. 有效期未累加

**检查项**：
- seconds 参数是否正确传递
- 用户是否已有该装扮（新用户需先获取）
- 查看 `xs_user_pretend_list` 表数据

---

## 相关文档

- [slp-php.md](./slp-php.md) - PHP 侧实现细节
- [slp-go.md](./slp-go.md) - slp-go 侧实现细节

---

**PR 链接**：
- slp-php: https://github.com/olaola-chat/slp-php/pull/new/hu562/decorate-use-forward
- slp-go: https://github.com/olaola-chat/slp-go/pull/new/hu562/decorate-use-forward