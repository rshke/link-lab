# device-gateway

设备发现、能力注册、命令路由、平台侧幂等及设备事件转换。内部模块为 registry、commands、observations。拥有平台命令记录与协议关联关系，连接 SiLA 2 真实适配器或模拟器。厂商 SDK 留在设备侧适配器。

已有 Python 最小协议转发实现：`src/interfaces/main.py` 暴露内部 HTTP，`infrastructure/sila_device.py` 使用 sila2 SDK 下发可观察命令并订阅 Status 属性。拥有最近 1000 条设备快照缓存，不拥有运行状态。端点为配置的本机 SiLA 2 端口，设备仅支持 measurement-1，尚未实现自动发现、通用能力注册和可靠事件发布。契约见 `contracts/api/device-gateway/interaction-v1.md` 与 `contracts/sila2/`。依赖与启动见根目录 `requirements-interaction.txt` 和 `docs/development/interaction-demo.md`，验证方式为 `tests/integration/test_interaction.py`。

数据库迁移归本服务 src/infrastructure/persistence/migrations/；组件内部测试归 tests/，跨组件验证归根目录 tests/。

维护状态及动作分别映射到 DeviceMaintenance.State 和 Perform，不修改设备故障或工作流预留；接口见 `contracts/api/device-gateway/maintenance-v1.md`。

启动时读取 ActionSemantics.Definitions，用本地 JSON Schema 及真实 Feature 定义校验并缓存动作声明；公开接口见 `contracts/api/device-gateway/capabilities-v1.md`。目前是固定单设备注册，不是通用发现或调度器。
