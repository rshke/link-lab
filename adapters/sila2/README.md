# SiLA 2 真实设备适配器

适配器部署在设备 PC 或同机边车，对平台设备网关暴露 SiLA 2，向本地 C# 上位机、厂商 SDK、PLC 或 IPC 转发操作。它只负责单台设备，不进行跨设备排程。

- `src/features/`：实现 `contracts/sila2/` 中的标准能力。
- `src/drivers/`：隔离具体厂商 SDK、PLC 和本地 IPC。
- `src/state-mapping/`：设备状态、错误及告警映射。
- `src/commands/`：本地命令协调、持久化去重及最终状态查询。
- `src/event-buffer/`：断网期间的状态变化与结果缓冲。
- `config/`：设备标识、证书引用及驱动配置示例。
- `tests/`：设备专属驱动和映射验证。

设备侧本地去重不能被网关侧幂等代替。平台断线不等于设备停止；重连时查询原命令，不能直接重发物理动作。共用协议验收放在 `tests/contract/devices/`。当前仅有目录骨架。
