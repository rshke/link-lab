# 设备模拟器

模拟器是独立设备进程，通过共享的 SiLA 2 Feature 接入设备网关。目前 measurement 已有最小执行、进度和故障注入实现，robot 与 liquid-handler 仍为占位目录。

measurement 现支持三种持续故障及各自维修流程，规则位于 `runtime/maintenance.py`；通过 DeviceMaintenance SiLA 2 Feature 检查、操作和自检，独立管理接口只用于开发注入。详见 `docs/development/device-maintenance.md`。

| 目录 | 职责 |
| --- | --- |
| robot | 位姿、路径、搬运、载荷与工位交互 |
| liquid-handler | 移液、混匀、清洗、耗材与分阶段进度 |
| measurement | 检测进度、结果生成与结果异常 |
| runtime | 模拟器内部复用的虚拟时钟、场景装载、固定 seed 与故障注入 |

每种设备分别拥有 `src/`、`tests/` 和 `scenarios/`。runtime 是模拟器专用代码，平台和真实适配器不得依赖它。当前 `runtime/engine.py` 管理模拟动作、内存去重及下个命令的 chaos 配置，measurement 的 `src/interfaces/main.py` 映射为 SiLA 2 Feature 并提供独立管理 HTTP。外部依赖为 Python sila2 SDK；入口、依赖和集成验证见 `docs/development/interaction-demo.md`。设备命令行为以 `contracts/sila2/` 为准，不能用模拟管理 API 代替正式设备协议。

共用契约测试位于 `tests/contract/devices/`，需要覆盖命令准入、进度、最终结果、幂等、断线重连与取消。设备专属场景保存在各自目录，多设备全链路场景保存在根目录 `tests/fixtures/scenarios/`。
