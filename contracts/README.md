# 接口契约

这里保存跨组件交换的数据与协议定义，不保存业务实现或数据库实体。目前已定义最小通信演示的 platform、workflow、device-gateway API v1，simulator 管理 API v1，以及 SiLA 2 ExperimentDevice Feature v1.0；其余目录仍为预留。

- `api/platform/`：规格、验证、审批、运行及控制请求。
- `api/agent/`：会话与草案生成。
- `api/device-gateway/`：内部设备能力与命令接口。
- `api/workflow/`：已准入计划交付与运行查询。
- `api/simulator/`：仅开发使用的故障注入管理接口。
- `api/twin/`：查询投影、实时订阅与回放。
- `schemas/`：实验规格、验证结果、计划、能力及命令数据。
- `events/`：事件信封及设备、运行、告警和样品事件。
- `sila2/`：模拟器和真实适配器共用 Feature Definition。

每份契约标明所属组件和版本。兼容性破坏需新增版本并记录迁移方式；生成客户端放在使用方或单独发布的技术包中，不手工修改生成代码。
