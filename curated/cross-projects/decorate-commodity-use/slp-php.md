# 装扮类物品使用转发 - slp-php 视角

> PHP 侧负责扣库存 + 消费记录，然后转发到 slp-go

**版本**: 1.0 | **更新**: 2026-04-14

---

## 项目内职责

| 职责 | 说明 |
|------|------|
| 判断是否转发 | 检查物品类型 + pretend_id |
| 扣减背包库存 | 使用锁 + 事务保证一致性 |
| 计算有效期秒数 | period + period_hour |
| 转发 RPC | 调用 slp-go 的 UseDecorateCommodity |

---

## 核心代码

### 文件路径

```
app/service/mate/UserCommodity.php    # 物品使用入口
app/service/rpc/RpcPretend.php        # RPC 客户端
```

### 关键函数

#### UserCommodity::use()

```php
// 装扮类物品转发到 slp-go 处理（先扣库存再调用 RPC）
if (\CommodityModel::isDecoType($this->_comm->type)) {
    $extra = json_decode($this->_comm->extra, true);
    if (!empty($extra['pretend_id']) && $extra['pretend_id'] > 0) {
        // 1. 扣减背包库存
        $ret = $this->_deductCommodityStock($this->_use_num);
        if ($ret !== true) return $ret;

        // 2. 计算有效期秒数
        $seconds = ($this->_comm->period * 24 * 3600 + $this->_comm->period_hour * 3600) * $this->_use_num;

        // 3. 调用装扮 RPC
        return RpcPretend::UseDecorateCommodity([
            'uid' => $this->_uid,
            'pretend_id' => (int)$extra['pretend_id'],
            'seconds' => $seconds,
        ]);
    }
}
```

#### UserCommodity::_deductCommodityStock()

```php
private function _deductCommodityStock($use_num)
{
    $keyLock = 'Pay.' . $this->_uid;
    $conn = Di::getDefault()->getShared('db');
    $conn->begin();
    try {
        // 1. 获取锁
        $res = Helper::fetchColumn("select get_lock('{$keyLock}', 10) ");
        if (!is_numeric($res) || $res != 1) throw new \Exception(__T("ERROR_LOCK_FAILED"));

        // 2. 检查数量
        $userCommodity = \XsUserCommodity::findFirst([...]);
        if (!$userCommodity || $userCommodity->num < $use_num) {
            throw new \Exception("not enough commodity");
        }

        // 3. 扣减背包库存
        $this->_ucomm->num -= $use_num;
        $this->_ucomm->num > 0 ? $this->_ucomm->save() : $this->_ucomm->delete();

        // 4. 消费记录
        \XsPayChange::log($this->_uid, 0, 'consume', $logMessage, [...]);

        $conn->commit();
    } catch (\Exception $exp) {
        $conn->rollback();
        return $exp->getMessage();
    }
    Helper::fetchColumn("select release_lock('{$keyLock}') ");
    return true;
}
```

#### RpcPretend::UseDecorateCommodity()

```php
public static function UseDecorateCommodity(array $params)
{
    try {
        $r = self::request(self::RpcServerName, "UseDecorateCommodity", [
            'uid' => intval($params['uid']),
            'pretend_id' => intval($params['pretend_id']),
            'seconds' => intval($params['seconds']),
        ]);
        return isset($r['success']) ? $r['success'] : false;
    } catch (\Exception $e) {
        \Imee\Service\Helper::debugger()->error(
            "UseDecorateCommodity: " . $e->getMessage()
        );
        return $e->getMessage();
    }
}
```

---

## 配置常量

### 装扮类型列表

```php
// CommodityModel::$decorates
$decorates = [
    'header',           // 头像框
    'mounts',           // 座驾
    'effect',           // 入场特效
    'decorate',         // 主页装扮
    'bubble',           // 聊天气泡
    'ring',             // 麦上光圈
    'union_header',     // 公会头像框
    'bubble_tail',      // 聊天气泡尾灯
    'card_decorate',    // 资料卡装扮
    'circle_background' // 动态背景
];
```

### RPC Server 名称

```php
public const RpcServerName = "rpc.pretend";
```

---

## 依赖的外部服务

| 服务 | 方法 | 说明 |
|------|------|------|
| slp-go rpc.pretend | UseDecorateCommodity | 添加有效期 + 自动佩戴 |

---

## 本地测试

### 测试场景

1. **正常转发**：装扮物品 pretend_id > 0 → 扣库存 + 转发成功
2. **不转发**：装扮物品 pretend_id = 0 → 走原有 PHP 逻辑
3. **库存不足**：扣库存失败 → 返回错误信息
4. **RPC 失败**：slp-go 返回错误 → 错误信息透传

### 测试数据准备

```sql
-- 确认物品 extra 中有 pretend_id
SELECT cid, name, type, extra FROM xs_commodity 
WHERE type IN ('header', 'bubble', 'decorate') 
AND extra LIKE '%pretend_id%';
```

---

## 相关文件

| 文件 | 说明 |
|------|------|
| `app/service/mate/UserCommodity.php` | 物品使用入口 |
| `app/service/rpc/RpcPretend.php` | RPC 客户端 |
| `app/models/mate/CommodityModel.php` | 装扮类型定义 |

---

**分支**: `hu562/decorate-use-forward`