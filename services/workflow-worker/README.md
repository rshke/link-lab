# workflow-worker

排程、资源锁、工作流状态机与运行异常处置。拥有不可变计划、运行和步骤状态、资源预留及处置记录。内部模块为 planning、scheduling、resources、runtime、incidents。消费准入请求，通过网关发命令，发布运行事实。

已有 Python 最小通信实现：内存运行记录、单设备资源预留、按序执行步骤，通过注入的执行端口调用网关。HTTP 入口为 `src/interfaces/main.py`，运行和资源数据归 `application/runtime.py`，不读取其他服务数据。契约见 `contracts/api/workflow/interaction-v1.md`。依赖与启动见根目录 `requirements-interaction.txt` 和 `docs/development/interaction-demo.md`。验证方式为根目录 `tests/integration/test_interaction.py`，未实现持久化、复杂排程和恢复策略。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。

维护操作与实验共用独占设备预留，未通过自检的设备不能接收新实验；通信不明时只允许原维护请求确认，不用维修清除 unknown 实验预留。接口见 `contracts/api/workflow/maintenance-v1.md`。
