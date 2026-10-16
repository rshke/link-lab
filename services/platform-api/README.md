# platform-api

实验规格、确定性验证、审批与执行准入。拥有规格版本、验证报告、规则集、审批及能力快照。内部模块为 experiments、validation、approvals、capabilities、execution-admission。运行及控制请求在授权后交给工作流，不直接下发设备命令。

已有 Python 最小通信实现：领域层验证演示规格，应用层通过注入的提交端口完成本地准入并交付工作流，HTTP 入口位于 `src/interfaces/main.py`。没有生产审批或持久化。契约见 `contracts/api/platform/interaction-v1.md`，依赖与启动见根目录 `requirements-interaction.txt` 和 `docs/development/interaction-demo.md`。验证方式为根目录 `tests/integration/test_interaction.py`。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。

维护模块 `application/maintenance.py` 校验维护请求并记录内存审计，入口同源托管 `apps/console/maintenance.html`。所有设备操作仍交付工作流，接口见 `contracts/api/platform/maintenance-v1.md`。
