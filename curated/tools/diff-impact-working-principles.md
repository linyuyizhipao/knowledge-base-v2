# diff-impact.py 工作原理

> 代码变更影响分析脚本，追踪引用传播，找出需要重启的服务

---

## 一、要解决的问题

在 SLP 多服务架构中，修改一个文件后不知道哪些服务需要重启。

**核心挑战**：
1. 一个文件可能包含多个函数，但只修改了其中一个
2. 私有函数被同包公开函数调用，公开函数被外部服务使用
3. 方法可能通过实例调用（如 `rankScene.GetRank()`）而不是包前缀调用
4. RPC 客户端调用（如 `client.UserRank.GetRank()`）不应被追踪

---

## 二、工作原理

### 2.1 整体架构

```
git diff master → 获取变更文件 → 精确提取变更元素 → BFS 追踪引用 → 服务分类
                        ↓（管道）
            定位 Deploy YAML → 生成打 tag 命令
```

### 2.2 两个独立脚本

**脚本 1：diff-impact.py** — 代码变更影响分析

```
阶段 1: 获取变更文件
    ↓
阶段 2: 精确提取变更元素
    ↓
阶段 3: BFS 追踪引用传播
    ↓
阶段 4: 服务分类（HTTP/RPC/CMD）
    ↓
输出: affected_services + restart_commands（JSON）
```

**脚本 2：deploy-tag.py** — Deploy YAML 定位 + 打 tag 命令

```
输入: diff-impact.py 的 JSON 输出（或 --services 手动指定）
    ↓
5 级匹配策略查找 deploy YAML
    ↓
输出: deploy_yamls + deploy_commands（JSON）
```

两个脚本通过管道串联：

```bash
python scripts/diff-impact.py | python scripts/deploy-tag.py
```

---

## 三、核心机制详解

### 3.1 精确提取变更元素（关键改进）

**问题**：文件可能包含 10 个公开函数，但 git diff 只改了 1 行。

**旧方案（错误）**：扫描整个文件，提取所有公开函数 → 误报

**新方案（正确）**：从 git diff 内容中提取**实际变更的函数**

#### 实现原理

```
git diff -U0 file.go → 无上下文 diff
    ↓
解析 @@ -a,b +c,d @@ → 获取变更行号
    ↓
根据行号定位到所属函数 → 只提取这个函数
```

#### 代码流程

```python
def _get_changed_functions_from_diff(file_path):
    # 1. 获取无上下文 diff（-U0）
    git diff master --no-color -U0 file_path
    
    # 2. 解析 diff 行号
    @@ -10,2 +10,3 @@  → 变更开始于第 10 行
    
    # 3. 找到变更行所属的函数
    遍历文件，记录每个函数的起始行
    根据行号匹配 → 返回函数名
```

#### 变量/常量提取

从 diff 的 `+` 行匹配：
```go
+ const GiftNormalGid = 211766  // test marker  → 提取 GiftNormalGid
+ var PrayCouponRefund = ...                      → 提取 PrayCouponRefund
```

---

### 3.2 私有函数传播

**问题**：私有函数不能被外部直接调用，但可能被同包的公开函数调用。

#### 传播链

```
私有函数变更（如 commonHandle）
    ↓ 被 HandleConsumePackage 调用
公开函数（HandleConsumePackage）
    ↓ 被 common_gift_send CMD 使用
服务入口
    ↓
标记该服务需要重启
```

#### 实现步骤

```python
def _find_public_callers_in_same_package(private_func):
    # 1. 获取同包所有文件
    pkg_dir = parent_dir_of_changed_file
    pkg_files = glob("*.go")
    
    # 2. 查找调用该私有函数的公开函数
    for f in pkg_files:
        content = read(f)
        if func_name not in content: continue
        
        for public_func in get_public_functions(content):
            if public_func_body_calls(func_name):
                add_to_callers(public_func)
    
    return callers  # 这些公开函数会被后续 BFS 追踪
```

#### 多跳私有函数传播链（v9 新增）

**问题**：私有函数 A → 私有函数 B → 私有函数 C → 公开函数 D，链长 > 1 时旧逻辑只找直接调用者。

```python
def _extract_func_body(content, func_start_pos):
    """大括号计数提取函数体，支持任意嵌套深度"""
    brace_pos = content.find('{', func_start_pos)
    depth = 0
    for i in range(brace_pos, len(content)):
        if content[i] == '{': depth += 1
        elif content[i] == '}':
            depth -= 1
            if depth == 0:
                return content[brace_pos+1:i]
    return None

def _find_public_callers_via_private_chain(private_func):
    """BFS 在同包内追踪私有→私有→...→公开"""
    visited_private = {func_name}
    queue = deque([func_name])
    public_callers = []
    
    while queue:
        current_name = queue.popleft()
        for f, content in pkg_files:
            for caller_name in get_functions(content):
                func_body = _extract_func_body(content, pos)
                if caller_calls(current_name, func_body):
                    if caller_name[0].isupper():
                        public_callers.append(caller_name)  # 公开 → 记录
                    elif caller_name not in visited_private:
                        visited_private.add(caller_name)
                        queue.append(caller_name)  # 私有 → 继续传播
    return public_callers
```

**实际传播链示例**：
```
broadcastFeedSuccess(私有) → recordFeedSideEffects(私有) → applyFeed(私有) → OnGiftSend(公开)
    ↓ 被 cmd/internal/big_brother/event/send_gift.go 调用
big_brother CMD 需要重启
```

---

### 3.3 BFS 引用追踪

#### 追踪流程

```
变更元素（如 rank.GetRank）
    ↓
grep "rank\.GetRank\b" → 找到引用文件
    ↓
判断文件类型：
    - app/api/ → HTTP 服务，标记并停止
    - rpc/server/internal/user_rank/ → RPC 服务，标记并停止
    - cmd/internal/cron/ → CMD 服务，标记并停止
    - 其他文件 → 继续追踪该文件的公开函数
```

#### 循环检测

```python
path = ["rank.GetRank", "service.User.GetRank", "api.UserHandler"]
if func_key in path:
    cycle = " → ".join(path + [func_key])
    circular_references.append(cycle)
    continue  # 不继续追踪
```

---

### 3.4 实例调用检测

**问题**：`rankScene.GetRank()` 不会匹配 `rank\.GetRank` 模式。

#### 实现原理

```python
def _find_instance_callers(pkg, method_name, changed_file):
    # 1. 搜索所有 .MethodName 调用（包括 .MethodName( 和 .MethodName 函数引用）
    #    使用 \b 而不是 \(，因为方法可能作为回调传递（无括号）
    grep ".GetRank\b" → 所有实例调用 + 函数引用
    
    # 2. 验证：该文件是否导入了变更包
    check import path → 必须有 import "slp/app/domain/rank"
    
    # 3. 排除 RPC client 调用
    if "client.UserRank.GetRank" in content:
        skip  # RPC 调用，不追踪
```

#### RPC client 排除

```go
// 应该追踪：

// 场景 1：直接调用（有括号）
rankScene := rank.RankedMap[req.Scene]
rankScene.GetRank(ctx, ...)  // ← 实例调用，需要追踪

// 场景 2：函数引用传递（无括号，如 cron 回调）
scron.AddSingleton("0 */5 * * * *", farm.FishpondLogic.ScanFishpondBaitMature, "...")  // ← 无括号，也需要追踪

// 不应该追踪：
client.UserRank.GetRank(ctx, req)  // ← RPC 调用，不追踪
```

---

### 3.5 服务分类

#### 路径映射规则

| 路径模式 | 服务类型 | 服务名来源 | 示例 |
|----------|----------|------------|------|
| `app/api/` | HTTP | 无 | `./bin/http` |
| `app/handler/` | HTTP | 无 | `./bin/http` |
| `rpc/server/internal/<name>/` | RPC | 目录名 | `./bin/rpc --name=<name>` |
| `rpc/server/internal/<name>.go` | RPC | 文件名 | `./bin/rpc --name=<name>` |
| `cmd/internal/<name>/` | CMD | 目录名 | `./bin/cmd --name=<name>` |
| `cmd/internal/<name>.go` | CMD | 文件名 | `./bin/cmd --name=<name>` |
| `library/` | library | 无 | 影响全部 |
| `app/consts/` | library | 无 | 影响全部 |
| `app/dao/` | library | 无 | 影响全部 |

---

### 3.6 定位 Deploy YAML 文件

**脚本**：`scripts/deploy-tag.py`（独立于 diff-impact.py）

#### Deploy 目录结构

```
项目根目录/
├── deploy/helm/
│   ├── cmd/
│   │   └── cmds/              ← CMD 服务 YAML 配置
│   │       ├── cron.yaml      ← name: "StarshipCron"
│   │       └── event.yaml     ← name: "StarshipEvent"
│   ├── rpc/
│   │   └── rpcs/              ← RPC 服务 YAML 配置
│   │       ├── starship.yaml
│   │       └── starship-farm.yaml
│   └── http/
│       └── values.yaml        ← HTTP 服务配置
```

#### 匹配策略（5 个优先级）

```
服务名: starship_cron (snake_case)
    ↓
策略 1: 文件名精确匹配 → starship_cron.yaml
策略 2: 文件名 kebab-case 匹配 → starship-cron.yaml
策略 3: deployment.name 字段 PascalCase 匹配 → StarshipCron
策略 4: deployment.name 字段 lowercase 匹配 → starshipcron
策略 5: 子串匹配（去前缀）→ starship_cron → cron → cron.yaml ✅
```

#### 名称转换

| 服务名 | 转换方式 | 结果 | 匹配示例 |
|--------|----------|------|----------|
| `starship_cron` | PascalCase | `StarshipCron` | `cron.yaml` (name: "StarshipCron") |
| `starship_cron` | kebab-case | `starship-cron` | `starship-cron.yaml` |
| `starship_cron` | 去前缀 | `cron` | `cron.yaml` |
| `room_list` | kebab-case | `room-list` | `room-list.yaml` |
| `room_list` | lowercase | `roomlist` | `room-list.yaml` (name: "room.list") |

#### 实现原理

```python
# deploy-tag.py
class DeployTagFinder:
    def find_deploy_yaml(service_type, service_name):
        # 确定搜索目录
        if service_type == "cmd": deploy_dir = "deploy/helm/cmd/cmds"
        elif service_type == "rpc": deploy_dir = "deploy/helm/rpc/rpcs"
        
        # 依次尝试 5 种匹配策略
        for strategy in [exact, kebab, pascal, lowercase, substring]:
            match = strategy(yaml_files, service_name)
            if match: return match
```

#### 生成命令

| 服务类型 | 命令格式 | 示例 |
|----------|----------|------|
| HTTP | `./yq.sh http` | 更新 `deploy/helm/http/values.yaml` 的 tag |
| RPC | `./yq.sh rpc <yaml名>` | `./yq.sh rpc starship-farm` |
| CMD | `./yq.sh cmd <yaml名>` | `./yq.sh cmd cron` |

---

## 四、grep 模式设计

### 4.1 精确匹配

```python
# 错误：匹配 rank.GetRankAwardUk（子串匹配）
pattern = "rank\.GetRank"

# 正确：只匹配 rank.GetRank( 或 rank.GetRank（后跟单词边界）
pattern = "rank\.GetRank\(|rank\.GetRank\b"
```

### 4.2 缓存优化

```python
_grep_cache = {}  # pattern -> set(files)

def _grep_pattern(pattern):
    if pattern in _grep_cache:
        return _grep_cache[pattern]  # 命中缓存
    
    result = subprocess.run(["grep", "-r", "-l", pattern, ...])
    _grep_cache[pattern] = result
    return result
```

---

## 五、数据流图

```
用户运行脚本
    │
    ├─ 1. git rev-parse → 检查 Git 仓库
    │
    ├─ 2. git diff master --name-only → 变更文件列表
    │     ["app/domain/rank/base.go", "rpc/server/internal/backend/refund/pray_coupon.go"]
    │
    ├─ 3. git diff -U0 file → 解析变更元素
    │     → 公开函数: [GetRank, IncrRank]
    │     → 私有函数: [getTableName] → 传播到公开函数
    │     → 常量/变量: [MaxTopNum]
    │
    ├─ 4. BFS 追踪
    │     ├── rank.GetRank → grep "rank\.GetRank\b"
    │     │   └── rpc/server/internal/user_rank/rank_rpc.go → RPC: user_rank
    │     │
    │     ├── rank.IncrRank → grep "rank\.IncrRank\b"
    │     │   └── rpc/server/internal/user_rank/rank_rpc.go → RPC: user_rank
    │     │
    │     └── 实例调用检测 → .GetRank(
    │         └── rpc/server/internal/user_rank/rank_rpc.go → RPC: user_rank
    │
    ├─ 5. 服务分类
    │     http: true, rpc: [user_rank], cmd: []
    │
    ├─ 6. 定位 Deploy YAML
    │     ├── http → deploy/helm/http/values.yaml
    │     ├── user_rank RPC → deploy/helm/rpc/rpcs/user_rank.yaml
    │     └── 未找到 → 跳过
    │
    └─ 7. 生成命令
          本地重启: make build && ./bin/http
          打 tag:   ./yq.sh http
                    ./yq.sh rpc user_rank
```

---

## 六、边界情况处理

| 场景 | 处理方式 |
|------|----------|
| 当前在 master 分支 | 返回错误 |
| 无代码变更 | 返回空结果 |
| 只有 _test.go 变更 | 忽略（过滤） |
| 只有 .pb.go 变更 | 忽略（过滤） |
| 公共库变更 | 标记 library，影响全部 |
| 循环引用 | 检测并记录，不无限循环 |
| RPC client 调用 | 排除，不追踪 |
| 子串匹配 | 使用 \b 和 \( 精确匹配 |
| Deploy YAML 未找到 | 跳过，不报错（服务名无对应 YAML 时正常） |
| YAML name 带点号 | 正则 `[\w.]+` 支持如 `room.list` |

---

## 七、性能优化

| 优化点 | 效果 |
|--------|------|
| 按需 grep（不预构建索引） | 启动快，按需加载 |
| grep 结果缓存 | 避免重复搜索 |
| 文件解析缓存 | 避免重复解析 |
| 遇到服务入口停止 | 减少不必要的追踪 |
| 精确提取变更元素 | 减少误报和额外搜索 |
| max_depth=50 | 防止无限传播 |

---

## 八、版本演进

| 版本 | 改进 |
|------|------|
| v1 | 扫描整个文件提取所有公开函数（误报多） |
| v2 | 从 git diff 精确提取变更函数 |
| v3 | 排除 RPC client 调用 |
| v4 | 精确 grep 匹配（\b 边界） |
| v5 | 支持入口文件（rpc/server/internal/*.go） |
| v6 | 实例调用匹配函数引用传递（cron 回调等无括号场景） |
| v7 | 自动定位 Deploy YAML 文件 + 生成 `./yq.sh` 打 tag 命令 |
| v8 | 拆分为两个独立脚本：diff-impact.py（影响分析）+ deploy-tag.py（deploy 定位） |
| v9 | 修复私有函数多跳传播链（BFS 追踪私有→私有→公开），函数体提取改用大括号计数支持任意嵌套 |

---

## 九、使用限制

1. **只支持 Go 项目**：依赖 Go 的包命名和函数定义语法
2. **对比基准固定**：始终对比 master 分支
3. **不追踪接口调用**：如 `ranker.GetRank()` 无法确定具体实现
4. **不追踪泛型方法**：当前版本未处理泛型

---

## 十、相关文件

- **脚本**：`scripts/diff-impact.py`
- **Skill**：`.claude/skills/diff-impact/skill.md`
- **验证报告**：`curated/tools/diff-impact-validation-report.md`
- **Wiki 文档**：`wiki/tools/diff-impact.md`