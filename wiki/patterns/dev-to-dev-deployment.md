---
id: patterns/dev-to-dev-deployment
label: dev-to-dev-deployment
source: /Users/hugh/project/my-wiki/curated/patterns/dev-to-dev-deployment.md
role: 规范
compiled: 2026-04-28
source_hash: 08b586360df5a075092149f3246f5cc1
---

> 从本地开发到测试服务器部署的完整流程

**版本**: 1.3 | **最后更新**: 2026-04-27

---

## 与 AI 开发流程的关系

本文档聚焦于 **合入与部署** 环节（`AI_WORKFLOW.md` 的阶段 5）。
完整的 AI 开发流程为：

```
阶段0：创建功能分支 → 阶段1~4：需求→知识→设计→实现 → 阶段5：合入部署 → 阶段6：知识沉淀
                                                         ↑ 本文档覆盖此环节 ↑
```

**开始开发前必读**: [`AI_WORKFLOW.md`](../AI_WORKFLOW.md)

---

## 一、分支管理规范

### 分支命名约定

| 分支类型 | 命名格式 | 说明 |
|----------|---------|------|
| 主分支 | `master` | 生产环境代码，受保护 |
| 开发分支 | `dev` | 测试环境代码，日常合入 |
| 功能分支 | `hu/<需求名称>` | 个人功能开发 |
| 修复分支 | `fix/<问题描述>` | Bug 修复 |
| 紧急修复 | `hotfix/<问题描述>` | 生产环境紧急修复 |

### 分支保护规则

- `master`: 保护分支，只能通过 PR 合入，需要审核
- `dev`: 开发分支，功能开发完成后合入
- 功能分支：个人开发，完成后可删除

### ⚠️ 重要禁令

1. **禁止在 dev 分支直接开发新功能** - dev 只用于合入，不作为开发分支
2. **禁止 dev → 功能分支的合并** - 只能功能分支 → dev
3. **禁止使用 Docker** - 部署采用 Jenkins 构建
4. **禁止跳过知识检索直接写代码** - 必须先阅读 `QUICK_REFERENCE.md` 及对应类型文档

---

## 二、完整开发发布流程

### 阶段 1：创建功能分支

```bash
# 1. 切换到 master 分支
cd <你的项目目录>/slp-go
git checkout master

# 2. 拉取最新代码
git pull origin master

# 3. 创建新功能分支（以需求名称命名）
git checkout -b hu/user_achievement

# 4. 推送新分支到远程
git push -u origin hu/user_achievement
```

**分支命名示例**：
- `hu/user_achievement` - 用户成就系统
- `hu/vip_upgrade` - VIP 升级逻辑
- `hu/gift_coupon` - 打赏送优惠券

---

### 阶段 2：本地开发

```bash
# 1. 在功能分支上开发
git checkout hu/user_achievement

# 2. 编写代码...

# 3. 提交代码
git add -A
git commit -anm 'feat: add user achievement system

- add achievement table and DAO
- add ChatGiftScene handler for achievement
- add NSQ notification for achievement unlock'
```

**Commit 规范**：
- `feat:` 新功能
- `fix:` Bug 修复
- `refactor:` 重构
- `docs:` 文档更新
- `chore:` 配置/工具更新

---

### 阶段 3：合入 dev 分支

#### 3.1 准备合入

```bash
# 1. 确认功能分支开发完成
git checkout hu/user_achievement
git status  # 确保没有未提交的修改

# 2. 推送功能分支到远程
git push origin hu/user_achievement
```

#### 3.2 解决冲突（如有）

**冲突解决原则**：

| 冲突类型 | 解决策略 |
|----------|---------|
| 本次修改的业务代码 | 以功能分支为准 |
| dev 分支的公共配置 | 以 dev 分支为准 |
| deploy/helm 配置文件 | 以功能分支为准（进程重启配置） |
| 不确定归属的冲突 | 提示用户协助解决 |

```bash
# 1. 切换到 dev 分支
git checkout dev

# 2. 尝试合并功能分支
git merge hu/user_achievement

# 3. 如果有冲突，查看冲突文件
git status

# 4. 编辑冲突文件，解决冲突标记
# <<<<<<< HEAD (dev 分支)
# =======
# >>>>>>> hu/user_achievement (功能分支)

# 5. 解决冲突后标记为已解决
git add <file>

# 6. 完成合并
git commit -m "merge: hu/user_achievement into dev"

# 7. 推送到远程
git push origin dev
```

#### 3.3 合并命令（无冲突时）

```bash
# 1. 切换到 dev 分支
git checkout dev

# 2. 合并功能分支
git merge hu/user_achievement

# 3. 推送到远程
git push origin dev

# 4. 删除已合并的功能分支（可选）
git branch -d hu/user_achievement
git push origin --delete hu/user_achievement
```

---

### 阶段 4：部署到测试服务器

#### 4.1 推送 dev 分支到远程

```bash
# 1. 确保在 dev 分支
git checkout dev

# 2. 拉取最新代码
git pull origin dev

# 3. 确保本地 dev 已包含功能分支的提交
git log --oneline -5  # 确认合并记录

# 4. 推送到远程（如果之前已推送过，跳过）
git push origin dev
```

#### 4.2 触发 Jenkins 构建

```bash
# 方式 1：使用 slpctl ci 命令（推荐）
slpctl ci -w

# 方式 2：使用 sb 别名
sb -w

# 方式 3：手动触发 Jenkins
# 访问 https://114.55.3.96/jenkins/
# 找到对应项目，点击"Build Now"
```

#### 4.3 构建流程说明

`slpctl ci -w` 命令执行内容：

```bash
# slpctl ci 内部逻辑（Go 实现）
# 1. 获取当前项目名
JOB_NAME=$(basename "$(pwd)")  # slp-go, slp-room, etc.

# 2. 触发 Jenkins 构建
# curl -X POST -u "slpdev:API_TOKEN" -H "Jenkins-Crumb:$CRUMB" \
#   "https://114.55.3.96/jenkins/job/$JOB_NAME/build"

# 3. 等待构建完成（-w 参数）
# - 轮询 Jenkins API
# - 显示构建状态
# - 显示最终结果

# 4. Jenkins 服务端执行：
# - git pull origin dev (拉取最新代码)
# - make build (编译构建)
# - 部署到测试服务器
# - supervisorctl restart (重启进程)
```

#### 4.4 验证部署

```bash
# 1. 查看 slpctl ci 命令输出
# ✅ 构建 #123 完成!
# 🎉 构建结果：SUCCESS

# 2. 访问 Jenkins 查看详情
open https://114.55.3.96/jenkins/job/slp-go/

# 3. SSH 到测试服务器（如需要）
ssh user@test-server
supervisorctl status
```

---

## 三、冲突解决指南

### deploy/helm 文件冲突处理

**原则**：以功能分支为主（因为主要是进程重启配置）

```bash
# 查看冲突
git diff deploy/helm_dev/rpc/values.yaml

# 如果冲突是部署配置（重启、副本数等），接受功能分支版本
git checkout --ours deploy/helm_dev/rpc/values.yaml
git add deploy/helm_dev/rpc/values.yaml
```

### 代码冲突处理

**场景 1：同一文件不同行修改**

```bash
# Git 通常会自动合并
git merge hu/user_achievement
```

**场景 2：同一行代码冲突**

```bash
# 1. 查看冲突内容
git diff --name-only

# 2. 打开冲突文件，手动解决
vim rpc/server/internal/consume/stage2/handler_stage2.go

# 3. 标记为已解决
git add rpc/server/internal/consume/stage2/handler_stage2.go

# 4. 完成合并
git commit -m "merge: resolve conflicts"
```

**场景 3：不确定归属的冲突**

```bash
# 暂停合并，提示用户
echo "⚠️  发现不确定的冲突，请协助确认："
echo "文件：$CONFLICT_FILE"
echo "冲突内容："
git diff $CONFLICT_FILE
```

---

## 四、配置文件说明

### deploy/ 目录结构

```
deploy/
├── deploy_rpc.sh          # RPC 服务部署脚本
├── deploy_cmd.sh          # CMD 服务部署脚本
├── deploy_alpha.sh        # Alpha 环境部署脚本
├── rpc/                   # RPC 服务配置
│   ├── slp-rpc-consume-stage1.conf
│   ├── slp-rpc-consume-payoff.conf
│   └── slp-rpc-consume-lottery.conf
├── cmd/                   # CMD 服务配置
│   ├── slp.cmd.consume.cron.conf
│   ├── slp.cmd.consume.stage0.conf
│   └── slp.cmd.consume.stage2.conf
├── helm/                  # 生产环境 Helm Chart
│   ├── rpc/
│   └── cmd/
└── helm_dev/              # 开发环境 Helm Chart
    ├── rpc/
    │   ├── values.yaml    # 开发环境 RPC 配置
    │   └── rpcs/          # RPC 服务定义
    └── cmd/
```

### 关键配置文件

| 文件 | 用途 | 冲突策略 |
|------|------|---------|
| `deploy/helm_dev/rpc/values.yaml` | 开发环境 RPC 部署配置 | 功能分支优先 |
| `deploy/helm_dev/rpc/rpcs/*.yaml` | RPC 服务启用配置 | 功能分支优先 |
| `deploy/helm_dev/cmd/values.yaml` | 开发环境 CMD 部署配置 | 功能分支优先 |
| `deploy/rpc/*.conf` | Supervisor 进程配置 | 功能分支优先 |
| `deploy/cmd/*.conf` | CMD 进程配置 | 功能分支优先 |

---

## 五、常见场景处理

### 场景 1：快速修复小 Bug

```bash
# 1. 基于 master 创建修复分支
git checkout master
git checkout -b fix/stage2_null_check

# 2. 修复代码并提交
git commit -anm 'fix: nil check in Stage2 handler'

# 3. 合入 dev
git checkout dev
git merge fix/stage2_null_check
git push origin dev

# 4. 部署测试
slpctl ci -w
```

### 场景 2：大功能开发（多人协作）

```bash
# 1. 创建功能主分支
git checkout -b hu/user_achievement

# 2. 推送并设置上游
git push -u origin hu/user_achievement

# 3. 团队成员基于主分支创建子分支
git checkout hu/user_achievement
git checkout -b hu/user_achievement_sub1

# 4. 子分支完成后先合入主分支
git checkout hu/user_achievement
git merge hu/user_achievement_sub1

# 5. 主分支完成后合入 dev
git checkout dev
git merge hu/user_achievement
git push origin dev
```

### 场景 3：紧急上线

```bash
# 1. 基于 master 创建 hotfix 分支
git checkout master
git checkout -b hotfix/critical_bug

# 2. 修复并测试
git commit -anm 'hotfix: critical bug fix'

# 3. 合入 master 和 dev
git checkout master
git merge hotfix/critical_bug
git push origin master

git checkout dev
git merge hotfix/critical_bug
git push origin dev
```

---

## 六、检查清单

### 合入 dev 前检查

- [ ] 代码已在本地测试通过
- [ ] Commit 信息清晰可读
- [ ] 无编译错误和 Warning
- [ ] 已解决所有 Git 冲突
- [ ] deploy/helm 配置已更新（如需要）

### 部署后检查

- [ ] sb 命令输出 SUCCESS
- [ ] Jenkins 构建日志无错误
- [ ] Supervisor 进程状态正常
- [ ] 日志无 Error
- [ ] 核心功能验证通过
- [ ] 监控指标正常

---

## 七、快捷命令

### slpctl ci 命令（构建部署）

```bash
# 触发构建
slpctl ci

# 触发构建并等待完成
slpctl ci -w

# 触发构建并打开浏览器
slpctl ci open

# 重启最近一次的进程
slpctl ci last

# 使用别名（如果配置了）
sb -w
```

### 项目特定命令

```bash
# slp-go 项目
cd <你的项目目录>/slp-go
slpctl ci -w

# slp-room 项目
cd <你的项目目录>/slp-room
slpctl ci -w

# slp-starship 项目
cd <你的项目目录>/slp-starship
slpctl ci -w

# slp-common-rpc 项目
cd <你的项目目录>/slp-common-rpc
slpctl ci -w
```

### 进程管理

```bash
# 查看所有进程状态
supervisorctl status

# 重启指定服务
supervisorctl restart slp-rpc-consume-stage1

# 停止服务
supervisorctl stop slp-rpc-consume-stage1

# 启动服务
supervisorctl start slp-rpc-consume-stage1
```

---

## 八、相关文档

- [slpctl ci 命令](../tools/slpctl.md#8-ci---jenkins-构建命令)
- [分支管理规范](../patterns/git-branch-conventions.md)
- [Commit 规范](../patterns/commit-conventions.md)
- [Jenkins 配置指南](../infra/jenkins.md)
- [Supervisor 配置说明](../infra/supervisor.md)
- [知识库使用说明书](../USER_GUIDE.md)
