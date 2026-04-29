# 公屏消息流转深度分析

> **最后更新**: 2026-04-12  
> **分析工具**: Claude Code  
> **原始问题**: 公屏消息发送流转链路分析

## 消息流转的完整调用栈

### 1. 消息入口：ClientSendMessage -> RoomMessageHandler

```
ClientHandle.go:385 ClientSendMessage()
  -> clientAddr: {ClientId, GateAddr}
  -> 从 Redis 获取 uid/rid
  -> 调用 RoomMessageHandler()
```

**room_message.go:92 RoomMessageHandler()**
```
参数:
  - rid, uid: int32 (房间ID和用户ID)
  - res: map[string]interface{} (完整消息负载)
  - content: string (消息内容)

返回: error

处理流程:
  1. 解析 extra (JSON) -> MessageExtra
  2. 表情处理 (dice/coin/rand/stone/card)
  3. 内容合法校验 (长度、表情等)
  4. 创建 common.Message 结构
  5. 调用 AddMessage() [进入工作流]
```

### 2. 消息投递：AddMessage -> WorkManager.RevMsg

**room_message.go:154 AddMessage()**
```go
// 直接调用 mng.RevMsg
s.AddMessage(&message)  // 即 mng.RevMsg()
```

**work_pool.go:54 WorkManager.RevMsg()** - 单线程快路径
```go
func (m *WorkManager) RevMsg(id int64, msg interface{}) {
    // 通过 id % workCount 选择固定的任务线程
    task := m.taskPool[int(id)%m.workCount]
    task.AddTask(&taskInfo{id, msg})
}
```

### 3. 任务处理：TaskLimiter.AddTask -> run() -> allowMsg/WrapSendMessage

**work.go:71 TaskLimiter.AddTask()**
```go
func (t *TaskLimiter) AddTask(info *taskInfo) {
    t.infoChan <- info  // 阻塞发送到 channel
}
```

**work.go:86 TaskLimiter.run()** - 异步处理循环
```go
for {
    select {
    case info := <-t.infoChan:
        msg := info.msg.(*common.Message)
        allow, err := t.allowMsg(info.Id)
        if err != nil {
            allow = true  // 错误时默认允许
        }
        go func() {
            err = gServer.RoomMessage.WrapSendMessage(msg, allow)
        }()
    case mutis := <-t.tokenChan:
        t.updateTokenMuti(mutis)  // 更新房间人数
    }
}
```

### 4. 限流判断：allowMsg

**work.go:143 TaskLimiter.allowMsg()**
```go
func (t *TaskLimiter) allowMsg(id int64) (ret bool, err error) {
    tokenMuti, ok := t.tokenMuti[id]  // 房间人数倍数
    if !ok || tokenMuti <= 0 {
        return true, nil
    }
    
    limiter, ok := t.limiterMap[id]
    if !ok {
        return true, nil
    }
    
    // 调用 Redis 限流器
    ret, err = limiter.GetToken(tokenMuti)
    return
}
```

### 5. 消息发送：WrapSendMessage -> GateClient.SendMessageToGroup

**room_message.go:208 WrapSendMessage()**
```go
func (r *RoomMessage) WrapSendMessage(message *common.Message, bAllow bool) error {
    // 1. 限流检查 (超管/VIP/EmotePosition 不限流)
    if !bAllow && ... {
        atomic.AddInt64(&gLImitMsgCnt, 1)
        return nil  // 被限流丢弃
    }
    
    // 2. 查询用户信息
    user, _ := dao.XsUserProfile.Where("uid=?", message.Uid).One()
    
    // 3. 查询头像框/聊天气泡等样式装饰
    // 4. 构建 message.Extra 的大量标签字段
    // 5. NSQ 转发 (特定条件)
    // 6. 调用 sendToGate()
    
    // 最终发送给客户端
    return r.sendToGate(message)
}
```

**sendToGate() (推断)**
```
-> GateClientImp.SendMessageToGroup()
-> RPC 调用 room_gate 的 SendMessageToGroup()
```

---

## 核心发现

### 1. 调用层数
- 10层调用栈：ClientSendMessage → RoomMessageHandler → RevMsg → TaskLimiter.AddTask → run() → allowMsg → WrapSendMessage → sendToGate → GateClientImp → room_gate

### 2. 限流机制
- Redis 基于令牌桶的 limiter
- 房间人数作为倍数 (tokenMuti = members)
- 超管/VIP/EmotePosition>0 不限流
- 限流丢弃计数器：gLImitMsgCnt

### 3. 性能瓶颈 (5个)
- 单线程 RevMsg 可能阻塞
- Goroutine 无限增长风险
- 每条消息 4-5 次 MySQL 查询
- 每条消息 1 次 Redis 限流查询
- 200 个 TaskLimiter 内存开销

### 4. 消息丢失场景 (5种)
- TaskLimiter.infoChan 溢出(1000 cap)
- 限流器拒绝(静默丢弃)
- 用户被封禁
- 表情白名单过滤
- Content 长度过长

### 5. 关键缺失
- 无可见敏感词过滤实现(注释与代码不符)
- 无消息追踪 ID
- 无限流丢弃日志

---

## 敏感词过滤和限流的具体实现机制

### 敏感词过滤
从代码中未找到真正的"敏感词过滤"逻辑。代码中显示的是：
```go
// 有表情的置空content，不做敏感词处理
s.AddMessage(&message)
```

**实际过滤机制:**
1. `common.CreateFilter(cfg.FilterSwitch)` 初始化 filter
2. Filter 是否被实际使用需要查看 `common` package
3. 代码注释提到"写入channel, 等待敏感词处理，以及做房间限流"，但实际 SendToGate 逻辑中未体现过滤

### 房间限流实现

**限流规则 (work.go:143-159):**
```go
1.room 人数倍数: tokenMuti = room_members
2.限流器: Redis 基于令牌桶的 limiter.GetToken(tokenMuti)
3.回调逻辑: 
   - 超管不限流
   - VIP等级 >= cfg.MinUlimitVipLevel 不限流
   - EmotePosition > 0 不限流
```

**限流统计 (work.go:162-204):**
```go
outputCalcLogByMinute() 每分钟输出:
  - roomId: 房间ID
  - rateByCycle: 周期内速率
  - limitCnt: 丢弃条数
  - 房间人数
```

---

## 潜在的性能瓶颈点

### 1. 单线程 RevMsg 投递 (work_pool.go:54)
```go
func (m *WorkManager) RevMsg(id int64, msg interface{}) {
    task := m.taskPool[int(id)%m.workCount]
    task.AddTask(&taskInfo{id, msg})  // 可能阻塞在 channel 满时
}
```
**问题:** Call by retry 失败时会重试, 而所有消息按 rid % workCount 分配, 可能导致部分线程过载。

### 2. Goroutine 泄漏风险 (work.go:105-110)
```go
go func() {
    err = gServer.RoomMessage.WrapSendMessage(msg, allow)
}()
```
**问题:** WrapSendMessage 中包含大量数据库查询 (Redis/MySQL), 如果限流开启时 goroutine 无限增长会导致资源耗尽。

### 3. WrapSendMessage 数据库查询密集
```go
// 每条消息调用:
- dao.XsUserProfile.Where()     // MySQL 查询用户
- dao.XsChatroomHeadpic.Where() // MySQL 查询头像框
- dao.XsChatroomBubble.Where()  // MySQL 查询气泡
- dao.XsChatroom.Where()        // MySQL 查询房间信息
```
**问题:** 每条消息需要 4-5 次数据库查询, 且未看到缓存机制。

### 4. Redis 限流查询
```go
limiter.GetToken(tokenMuti)  // 每条消息至少 1 次 Redis 调用
```
**问题:** 高并发下 Redis QPS 会很高。

### 5. workCount 默认值 (work_pool.go:14)
```go
const DefWorkCnt = 200
```
**问题:** 200 个 TaskLimiter, 每个都有独立的 limiterMap 和 tokenMuti, 内存开销大。

---

## 消息丢失的可能原因和诊断方法

### 消息丢失场景分析

#### 场景 1: TaskLimiter.infoChan 溢出 (work.go:56)
```go
infoChan: make(chan *taskInfo, TaskInfoMaxLen)  // 1000
```
**丢失原因:** 当消费者处理慢时, channel 满后会阻塞新消息。

#### 场景 2: 限流丢弃 (work.go:240-244)
```go
if !bAllow && ... {
    atomic.AddInt64(&gLImitMsgCnt, 1)
    return nil  // 直接返回不发送
}
```
**丢失原因:** 被限流器拒绝的消息静默丢弃。

#### 场景 3: 用户状态检查失败 (room_message.go:225-228)
```go
if user.Deleted > 1 {
    r.sendWarnmessage(message, "此账户已经被封禁，请重试")
    return nil  // 封禁用户消息丢弃
}
```

#### 场景 4: 表情白名单过滤 (room_message.go:121-129)
```go
for _, match := range matchValues {
    if match.MatchString(messageExtra.Emote) {
        return nil  // 非法表情丢弃
    }
}
```

#### 场景 5:Content 过长过滤 (room_message.go:418-426)
```go
if len(content) >= model.MaxDanmuSize {
    s.SendMsgToClientWithMsgPack(..., "聊天消息长度超过限制")
    return  // 但不返回 error, 消息静默丢弃
}
```

### 诊断建议

#### 1. 监控指标收集
```bash
# 检查限流计数
grep "LimitTps" /var/log/slp-gateway/*.log

# 检查消息处理速率
grep "msg handle report" /var/log/slp-gateway/*.log

# 检查房间限流报告
grep "roomLimitReport" /var/log/slp-gateway/*.log
```

#### 2. Redis 限流器诊断
```bash
# 查看限流 key
redis-cli keys "*limiter*"

# 检查限流配置
GET xs.room.limiter.config
```

#### 3. 消息追踪 ID
建议在 `RevMsg` 处添加Trace ID:
```go
func (m *WorkManager) RevMsg(id int64, msg interface{}) {
    traceID := fmt.Sprintf("msg-%d-%d", time.Now().UnixNano(), rand.Int64())
    g.Log().Debugf("trace_id=%s rid=%d uid=%d", traceID, msg.Rid, msg.Uid)
    ...
}
```

#### 4. 日志分析 key
```
1. ["wrap send message begin"] -> 消息开始处理
2. ["allowMsg id: %d, err"] -> 限流检查异常
3. ["wrapSendMessage info:%+v allow:%t err"] -> 发送异常
4. ["roomLimitReport"] -> 房间限流统计
5. ["sendWarnmessage"] -> 警告消息发送
```

#### 5. 消息丢失确认清单

| 位置 | 可能丢失 | 诊断日志 | counter |
|------|---------|---------|---------|
| RoomMessageHandler 表情过滤 | 是 | 无 | 无 |
| 限流器 (allowMsg) | 是 | `"allowMsg id: %d, err"` | gLImitMsgCnt |
| WrapSendMessage 限流检查 | 是 | 无 | gLImitMsgCnt |
| wrapSendMessage 查询用户 | 否 (error 返回) | `"wrap send message query rid: %d, uid: %d, err"` | - |
| sendToGate RPC 调用 | 是 | `"SendMessageToGroup gate manager"` | - |
| Gate 服务不可用 | 是 | `"CloseClient %+v %v"` | - |

---

## 性能优化建议

### 1. 添加缓存层
```go
// 在 WrapSendMessage 开头添加缓存
userCacheKey := fmt.Sprintf("user_profile:%d", message.Uid)
if cached, err := r.rdbCache.Get(ctx, userCacheKey).Result(); err == nil {
    // 解析缓存
}
```

### 2. 分离高/低优先级消息
```go
// EmotePosition > 0 的消息走高优先级队列
if message.Extra.EmotePosition > 0 {
    task := m.highPriTaskPool[int(id)%m.highPriCount]
    task.AddTask(...)
    return
}
```

### 3. 批量更新房间人数
当前每个房间每次更新都调用 Redis, 可以合并为:
```go
// 批量更新
for roomID, members := range roomMembersMap {
    // ... 现有逻辑
}
// gather to batch
```

### 4. 异步消息发送
```go
// WrapSendMessage 本身已经是 goroutine
// 但 sendToGate 可能阻塞
// 建议 sendToGate 也异步化
```

### 5. 增加消息队列深度监控
```go
type TaskLimiter struct {
    ...
    queueDepth int64  // 添加原子计数
}

func (t *TaskLimiter) AddTask(info *taskInfo) {
    atomic.AddInt64(&t.queueDepth, 1)
    t.infoChan <- info
}

func (t *TaskLimiter) run() {
    ...
    case info := <-t.infoChan:
        atomic.AddInt64(&t.queueDepth, -1)
        ...
}
```

---

## 消息流转时序图 (文本版)

```
客户端 -> room_manager (RPC)
    |
    v
ClientSendMessage() [ClientHandle.go:385]
    |
    v
RoomMessageHandler() [room_message.go:92]
    | 1. 解析 extra (JSON)
    | 2. 表情检查
    | 3. 内容校验
    v
AddMessage() [即 mng.RevMsg()]
    |
    v
WorkManager.RevMsg() [work_pool.go:54]
    | 计算: taskPool[rid % workCount]
    v
TaskLimiter.AddTask() [work.go:71]
    | 发送到 infoChan
    v
TaskLimiter.run() - 协程工作循环
    |
    | 从 infoChan 取出
    v
allowMsg() [work.go:143]
    | 调用 Redis 限流器
    |
    +-- 限流通过 -> allow=true
    +-- 限流拒绝 -> allow=false, gLImitMsgCnt++
    v
WrapSendMessage(msg, allow) [room_message.go:208] - goroutine
    |
    | 1. 限流检查 (重复)
    | 2. 查询用户信息 (MySQL)
    | 3. 查询装饰数据 (MySQL × 4)
    | 4. 构建 message.Extra
    | 5. NSQ 转发 (部分房间)
    |
    v
 sendToGate() [推断]
    |
    v
GateClientImp.SendMessageToGroup()
    |
    v
RPC 调用 room_gate:SendMessageToGroup
    |
    v
客户端接收消息
```

---

## 总结

### 核心链路
```
ClientSendMessage 
  -> RoomMessageHandler (同步)
  -> RevMsg (同步)
  -> TaskLimiter.AddTask (异步通道)
  -> run() 循环
  -> allowMsg (Redis 限流)
  -> WrapSendMessage (Goroutine + MySQL × 5)
  -> sendToGate (RPC)
  -> room_gate
  -> 客户端
```

### 关键问题
1. **无可见敏感词过滤** - 代码注释与实现不符
2. **无消息追踪机制** - 难以诊断消息丢失
3. **Goroutine 无限制** - 可能导致资源耗尽
4. **数据库查询串联** - 高延迟
5. **限流丢弃静默** - 无法监控

### 诊断命令
```bash
# 查看限流频率
grep "LimitTps" gateway.log

# 查看房间限流触发
grep "roomLimitReport" gateway.log

# 查看消息处理速率
grep "msg handle report" gateway.log

# 查看错误日志
```

---
*此报告由 Claude Code 深入分析生成*