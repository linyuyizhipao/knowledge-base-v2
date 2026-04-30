# 房间类型拓展工作计划

> 按工作日拆分的可执行计划（以大哥房为例）

**最后更新**: 2026-04-11  
**参考 PR**: slp-go#2760, slp-room#864, slp-common-rpc#220, slp-gateway#106, slp-php#1533, slp-server#90

---

## 文档说明

本文档是 [`room-type-extension.md`](./room-type-extension.md) 的配套工作计划，将技术流程拆解为可按日执行的任务清单。

**适用场景**：
- 首次接触房间类型拓展开发
- 需要明确每日工作目标和验收标准
- 项目排期和进度跟踪

---

## 第 1 天：数据库设计 + DAO/Model 生成

### 上午：数据库设计

- [ ] 编写主表 DDL（xs_chatroom_big_brother）
- [ ] 编写关联表 DDL（xs_chatroom_big_defend）
- [ ] 编写流水表 DDL（xs_big_brother_money_log）
- [ ] 编写灯牌表 DDL（xs_big_brother_light_board）
- [ ] 评审 DDL（字段、索引、注释）

**验收标准**：
- [ ] 数据库表创建成功
- [ ] 索引设计合理
- [ ] 字段注释完整

---

### 下午：代码生成

- [ ] 执行 `slpctl gen -t xs_chatroom_big_brother`
- [ ] 执行 `slpctl gen -t xs_chatroom_big_defend`
- [ ] 执行 `slpctl gen -t xs_big_brother_light_board`
- [ ] 执行 `slpctl gen -t xs_big_brother_money_log`
- [ ] 执行 `slpctl gen -t xs_chatroom_settings`
- [ ] 验证生成的 DAO 层文件（internal + 导出）
- [ ] 验证生成的 Model 层文件（internal + 导出）
- [ ] 提交代码到特性分支

**验收标准**：
- [ ] 生成的代码无编译错误
- [ ] DAO 方法可正常调用

---

## 第 2 天：Proto 定义 + Service 层框架

### 上午：Proto 定义

- [ ] 编写 entity_xs_chatroom_big_brother.proto
- [ ] 编写 entity_xs_chatroom_big_defend.proto
- [ ] 编写 entity_xs_big_brother_light_board.proto
- [ ] 编写 entity_xs_big_brother_money_log.proto
- [ ] 编写 api_big_brother.proto
- [ ] 执行 `make proto` 生成 pb.go 文件

**验收标准**：
- [ ] Proto 编译通过
- [ ] 生成的 pb.go 文件无错误

---

### 下午：Service 层框架

- [ ] 创建 app/service/big_brother/ 目录
- [ ] 编写 big_brother.go（初始化入口）
- [ ] 编写 config.go（配置管理）
- [ ] 编写 money.go（财富值管理框架）

**验收标准**：
- [ ] Service 层包结构完整
- [ ] 初始化函数可正常调用

---

## 第 3-4 天：Service 层业务实现

### 第 3 天：核心业务

- [ ] 实现 GetRoomInfo() 房间信息获取
- [ ] 实现 AddMoney() 财富值增加
- [ ] 实现 MoneyLog 流水记录
- [ ] 实现 defend.go 守护管理
- [ ] 单元测试（config、money）

**验收标准**：
- [ ] 核心业务逻辑可独立测试
- [ ] 单元测试通过率 100%

---

### 第 4 天：扩展业务

- [ ] 实现 light_board.go 灯牌管理
- [ ] 实现 cron.go 定时任务（衰减、结算）
- [ ] 完善所有单元测试
- [ ] 代码审查

**验收标准**：
- [ ] 单元测试覆盖率 > 60%
- [ ] 所有业务逻辑可独立测试
- [ ] 错误处理完整

---

## 第 5 天：API 层实现

### 上午：API 编写

- [ ] 编写 app/api/big_brother.go
- [ ] 实现 GetRoomInfo API
- [ ] 实现 Defend API
- [ ] 实现 LightBoard 相关 API

---

### 下午：路由注册 + 测试

- [ ] 在 app/app/route.go 注册路由
- [ ] 编写 API 测试用例
- [ ] 本地启动 HTTP 服务测试

**验收标准**：
- [ ] API 可正常访问
- [ ] 参数校验生效
- [ ] 响应格式正确

---

## 第 6-7 天：CMD 事件消费者

### 第 6 天：消费者框架

- [ ] 创建 cmd/internal/big_brother/ 目录
- [ ] 编写 consumer.go（NSQ 消费者启动）
- [ ] 编写 service.go（事件处理主逻辑）
- [ ] 定义 Topic 常量
- [ ] 实现 NSQ 消息解析

**验收标准**：
- [ ] CMD 服务可正常启动
- [ ] NSQ 连接成功

---

### 第 7 天：事件 Handler

- [ ] 实现 handleAddMoney() 财富值事件
- [ ] 实现 handleDefendCreate() 守护事件
- [ ] 实现 handleLightBoardSubmit() 灯牌事件
- [ ] 添加错误处理和日志
- [ ] 本地启动 CMD 测试

**验收标准**：
- [ ] NSQ 消息可正常消费
- [ ] 事件处理逻辑正确

---

## 第 8 天：配置注册

### 上午：数据库配置

- [ ] 执行 ALTER TABLE 更新 property 枚举
- [ ] INSERT 模块工厂记录
- [ ] INSERT 模块配置记录
- [ ] UPDATE 游戏支持列表

**验收标准**：
- [ ] 房间类型可正常创建
- [ ] 模块工厂配置生效

---

### 下午：NSQ 配置

- [ ] 在 config/slp-nsq-dev.json 添加 Topic
- [ ] 在 config/slp-nsq-prod.json 添加 Topic
- [ ] 更新 Helm 部署配置

**验收标准**：
- [ ] NSQ Topic 配置完整

---

## 第 9-10 天：跨服务协调

### 第 9 天：slp-room 变更

- [ ] 新增 DAO 层代码（如需要）
- [ ] 新增事件消费者（如需要）
- [ ] 更新房间进入逻辑
- [ ] 代码审查

---

### 第 10 天：其他服务

- [ ] slp-common-rpc: RPC 服务支持
- [ ] slp-php: PHP 端业务逻辑
- [ ] slp-server: 服务端配置
- [ ] slp-gateway: 网关路由

**验收标准**：
- [ ] 所有服务编译通过
- [ ] 跨服务调用正常
- [ ] 配置同步完成

---

## 第 11 天：部署配置

### 上午：Helm 配置

- [ ] 更新 CMD 部署配置
- [ ] 更新 RPC 部署配置
- [ ] 更新 HTTP 部署配置
- [ ] 更新环境变量

---

### 下午：测试环境部署

- [ ] 提交 PR 到 master 分支
- [ ] 触发 Jenkins 构建
- [ ] 部署到测试环境
- [ ] 验证服务启动

**验收标准**：
- [ ] 所有服务正常启动
- [ ] 日志无报错
- [ ] 监控指标正常

---

## 第 12 天：测试验证 + 文档沉淀

### 上午：功能测试

- [ ] 创建房间测试
- [ ] 守护功能测试
- [ ] 财富值功能测试
- [ ] 灯牌功能测试
- [ ] 定时任务测试

---

### 下午：文档沉淀

- [ ] 更新项目文档
- [ ] 编写测试报告
- [ ] 代码审查收尾
- [ ] 准备上线

**验收标准**：
- [ ] 所有功能测试通过
- [ ] 文档完整
- [ ] 代码审查通过

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [[room-type-extension.md]] | 房间类型拓展技术流程（概念版） |
| [[event-extension-guide.md]] | 事件拓展决策树 |
| [[cmd-module-standard.md]] | CMD 模块标准结构 |

---

**版本**: 1.0 | **最后更新**: 2026-04-11
