# agent-service

对话、实验草案、知识检索与运行解释。拥有会话、模型调用记录及检索证据。内部模块为 dialogue、drafting、knowledge、explanation。只调用平台公开 API 和孪生只读接口，不连接设备、执行数据库或消息总线。

目录层次遵循根目录 docs/architecture/service-boundaries.md。具体业务模块在对应层内按需建立；组件尚未实现，运行时、依赖清单和启动入口待实现时补充。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。
