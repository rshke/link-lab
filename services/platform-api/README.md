# platform-api

实验规格、确定性验证、审批与执行准入。拥有规格版本、验证报告、规则集、审批及能力快照。内部模块为 experiments、validation、approvals、capabilities、execution-admission。运行及控制请求在授权后交给工作流，不直接下发设备命令。

目录层次遵循根目录 docs/architecture/service-boundaries.md。具体业务模块在对应层内按需建立；组件尚未实现，运行时、依赖清单和启动入口待实现时补充。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。
