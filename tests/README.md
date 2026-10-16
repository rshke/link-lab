# 跨组件验证

- `contract/api/`：公开服务接口的兼容性与输入输出。
- `contract/devices/`：同一套 SiLA 2 行为验收用于模拟器及真实适配器。
- `integration/`：准入与工作流交付、网关与设备通信、事件与投影一致性。
- `e2e/`：设计稿中的板式稀释与检测闭环，包含耗材不足后的暂停及恢复。
- `fixtures/scenarios/`：多设备场景、固定种子、故障与期望事实。

单元测试放在各组件自己的 `tests/`。当前 `integration/test_interaction.py` 已有六组可执行的真实进程通信测试，运行 `.\.venv\Scripts\python tests/integration/test_interaction.py`，覆盖最小 HTTP / SiLA 2 链路及 chaos。其余测试目录仍为占位，设备全量契约验收、事件投影和业务端到端场景尚未实现。详细说明见 `docs/development/interaction-demo.md`。

`integration/test_maintenance.py` 验证三种持续故障的专属维修链路及自检准入；`services/workflow-worker/tests/test_maintenance_reservation.py` 验证维护结果不明时的预留和幂等确认。启动方式见 `docs/development/device-maintenance.md`。
