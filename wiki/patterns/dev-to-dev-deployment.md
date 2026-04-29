---
id: patterns/dev-to-dev-deployment
label: dev-to-dev-deployment
source: /Users/hugh/project/my-wiki/curated/patterns/dev-to-dev-deployment.md
role: 规范
compiled: 2026-04-28
source_hash: 08b586360df5a075092149f3246f5cc1
---

> 从本地开发到测试服务器部署的完整流程

## 分支管理

| 分支类型 | 命名 | 说明 |
|----------|------|------|
| 主分支 | `master` | 生产环境，保护分支 |
| 开发分支 | `dev` | 测试环境代码 |
| 功能分支 | `hu/<需求名称>` | 个人功能开发 |

### 禁令

1. **禁止在 dev 分支直接开发** - dev 只用于合入
2. **禁止 dev → 功能分支的合并**
3. **禁止使用 Docker** - Jenkins 构建
4. **禁止跳过知识检索直接写代码**

## 开发流程

```bash
# 1. 创建功能分支
git checkout master && git pull origin master
git checkout -b hu/user_achievement && git push -u origin hu/user_achievement

# 2. 开发并提交
git add -A && git commit -anm 'feat: add user achievement system'

# 3. 合入 dev
git checkout dev && git merge hu/user_achievement && git push origin dev

# 4. 触发构建
slpctl ci -w    # 推荐
sb -w           # 别名
```

## 冲突解决策略

| 冲突类型 | 策略 |
|----------|------|
| 本次修改的业务代码 | 以功能分支为准 |
| dev 分支的公共配置 | 以 dev 分支为准 |
| deploy/helm 配置文件 | 以功能分支优先 |
| 不确定归属 | 提示用户协助 |

## 快捷命令

| 命令 | 说明 |
|------|------|
| `slpctl ci` | 触发构建 |
| `slpctl ci -w` | 触发并等待完成 |
| `slpctl ci open` | 触发并打开浏览器 |
| `slpctl ci last` | 重启最近一次进程 |

## 合入前检查

- [ ] 代码已本地测试通过
- [ ] Commit 信息清晰
- [ ] 无编译错误
- [ ] 已解决 Git 冲突
- [ ] deploy/helm 配置已更新（如需要）

## 部署后检查

- [ ] 构建输出 SUCCESS
- [ ] Supervisor 进程状态正常
- [ ] 日志无 Error
- [ ] 核心功能验证通过
