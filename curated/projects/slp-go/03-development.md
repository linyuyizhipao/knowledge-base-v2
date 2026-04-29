# slp-go 开发工作流

## 代码生成

### 数据库表 → DAO/Model/PB

```bash
# 单个表
slpctl gen -t xs_user_profile

# 批量生成
slpctl gen -t xs_user_profile,xs_follow,xs_fans

# 删除模式
slpctl gen -t xs_user_profile -delete
```

**自动执行步骤：**
1. 生成临时配置文件
2. `gf gen pbentity` → 生成 `.proto` 文件
3. `protoc` → 生成 `pb.go`
4. `protoc-go-inject-tag` → 注入 tag
5. `gf gen dao` → 生成 DAO 代码
6. 清理临时配置

### 构建命令

```bash
make          # 构建所有服务
make http     # 仅 HTTP 服务
make rpc      # 仅 RPC 服务
make cmd      # 仅 CMD 工具
```

## 本地运行

```bash
./bin/http                        # HTTP 服务
./bin/rpc --name=user             # RPC 服务
./bin/cmd --name=cache --action=Main  # CMD 任务
```

## 代码检查

```bash
golangci-lint run ./...    # 静态检查
gofmt -l -s -w app/        # 代码格式化
```

## 测试

```bash
go test -v -count=1 ./...              # 所有测试
go test -v ./app/service/... -run TestXxx  # 特定测试
```

## API 开发流程

1. 在 `app/api/` 创建 handler，添加 Swagger 注解
2. 在 `app/query/` 和 `app/pb/` 定义结构体
3. 在 `app/service/` 实现业务逻辑
4. `make swagger` 生成文档
