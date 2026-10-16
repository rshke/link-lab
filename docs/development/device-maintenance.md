# 设备维修模拟

当前实现面向单个检测设备 measurement-1。浏览器页面由平台 API 在 `http://127.0.0.1:8010/maintenance` 提供，页面只调用同源平台接口。维修请求经过平台校验、工作流设备预留、网关，再通过真正的 SiLA 2 DeviceMaintenance Feature 到达模拟器。

## 故障对应的维修操作

| 持续故障 | 检查内容 | 按顺序执行的模拟操作 |
| --- | --- | --- |
| channel_blockage 检测通道堵塞 | 检查进样通道 | 冲洗通道 → 更换过滤器 |
| sensor_drift 传感器漂移 | 检查标准参考值 | 清洁传感器 → 标准样校准 |
| loose_cable 内部线缆松动 | 检查内部传感器连接 | 重新插接线缆 → 锁紧接插件 |

状态顺序为 `faulted → diagnosed → repairing → awaiting_self_test → ready`。未检查、操作不匹配、顺序错误、旧版本请求均不能清除故障。维修步骤全部完成后，自检通过才恢复设备可用性。此处自检验证模拟维修状态，不是仪器物理参数测试；真实设备接入后需替换为真实自检证据。

## 启动

先按 [交互演示说明](interaction-demo.md) 安装依赖，在仓库根目录执行：

```powershell
.\.venv\Scripts\python scripts/interaction_demo.py serve
```

另开终端载入以下任一故障，然后打开维护页面：

```powershell
.\.venv\Scripts\python scripts/interaction_demo.py channel_blockage
.\.venv\Scripts\python scripts/interaction_demo.py sensor_drift
.\.venv\Scripts\python scripts/interaction_demo.py loose_cable
```

一次只允许一个持续故障，前一个完成维修和自检后才可载入下一个。注入在模拟器独立管理 API 上完成，浏览器不能直连该入口。原 normal/delay/fail 三种一次性场景保持原语义；fail 不自动转化为持续故障。

## 维护与实验的边界

模拟器拥有故障实例、检查及维修进度、设备端历史和请求去重；规则位于 `simulators/runtime/maintenance.py`，不依赖 Web 或 SiLA SDK。模拟器入口只负责协议映射。不同故障对应的操作由 recipe 定义，无关操作不会被当作通用修复。

工作流负责维修和实验之间的独占预留。持续故障阻止新实验准入，模拟器执行入口还会再次拒绝未修好的设备。已有实验运行中或结果 unknown 时，维修请求被拒绝，不能用维修释放原实验资源。维修通信结果不明时保留预留，允许完全相同的待确认请求重试，禁止用新请求重复模拟物理操作。

平台保存本地演示操作者的准入结果审计，设备保留具体动作历史。页面显示当前故障、专属步骤、可选维修动作和历史，轮询只读取状态，不自动维修。手动操作后的重新查询避免把去重缓存中的旧快照误当作当前状态。

维修不会自动将旧实验改为成功，也不自动重做样品或恢复失败步骤。SiLA 网络断线与内部线缆松动分开：进程掉线导致结果不明时，仍需要原工作流的对账和恢复流程。

## 验证

停止已有演示进程后，分别运行：

```powershell
.\.venv\Scripts\python tests/integration/test_maintenance.py
.\.venv\Scripts\python services/workflow-worker/tests/test_maintenance_reservation.py
.\.venv\Scripts\python tests/integration/test_interaction.py
```

维护集成测试通过四个独立进程和真实 SiLA 2 验证三类操作流程、错误步骤、过早自检、重复及旧版本请求、实验隔离与恢复；工作流单元测试验证丢失响应后的同请求确认，以及 unknown 实验预留不被维修清除。原六组测试继续回归通信和一次性 chaos。

## 当前限制

所有维护状态、去重和审计均在内存，重启会丢失；不提供生产认证、持久工单、备件管理或真实维修执行。当前快速模拟操作没有耗时或额外随机维修失败；错误操作导致的失败与未通过自检已覆盖。前端是独立轻量控制台，没有修改 `device-twin-demo/` 或迁移旧前端。

契约见 [平台维护 API](../../contracts/api/platform/maintenance-v1.md)、[工作流维护 API](../../contracts/api/workflow/maintenance-v1.md)、[网关维护 API](../../contracts/api/device-gateway/maintenance-v1.md) 和 [SiLA 2 Feature](../../contracts/sila2/README.md)。
