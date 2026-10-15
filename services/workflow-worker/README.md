# workflow-worker

排程、资源锁、工作流状态机与运行异常处置。拥有不可变计划、运行和步骤状态、资源预留及处置记录。内部模块为 planning、scheduling、resources、runtime、incidents。消费准入请求，通过网关发命令，发布运行事实。

目录层次遵循根目录 docs/architecture/service-boundaries.md。具体业务模块在对应层内按需建立；组件尚未实现，运行时、依赖清单和启动入口待实现时补充。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。
