# twin-service

设备、机器人、工位、样品和运行的查询投影、实时推送及回放。内部模块为 projections、queries、realtime、replay。拥有可重建投影及事件消费游标，不拥有运行状态机、资源锁或控制权。

目录层次遵循根目录 docs/architecture/service-boundaries.md。具体业务模块在对应层内按需建立；组件尚未实现，运行时、依赖清单和启动入口待实现时补充。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。
