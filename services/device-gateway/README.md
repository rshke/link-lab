# device-gateway

设备发现、能力注册、命令路由、平台侧幂等及设备事件转换。内部模块为 registry、commands、observations。拥有平台命令记录与协议关联关系，连接 SiLA 2 真实适配器或模拟器。厂商 SDK 留在设备侧适配器。

目录层次遵循根目录 docs/architecture/service-boundaries.md。具体业务模块在对应层内按需建立；组件尚未实现，运行时、依赖清单和启动入口待实现时补充。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。
