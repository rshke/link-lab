# SiLA 2 设备通信 v1.0

源契约为 `ExperimentDevice-v1_0.sila.xml`。网关经 SiLA 2 / gRPC 调用模拟器，不以 JSON HTTP 冒充设备协议。模拟器对外仅暴露一个演示设备 `measurement-1`。

- `Execute(CommandId: String, DurationMs: Integer)` 是可观察命令。时长 100–5000ms，响应 Result 为 JSON：`{ "commandId": "…", "state": "succeeded|failed", "chaos": "normal|delay|fail", "error": "失败时提供" }`。相同 ID 和参数返回缓存结果；已完成的 ID 配不同参数会抛出协议执行错误；并发新命令在设备忙时拒绝。
- `Status: String` 是可观察属性，内容为 JSON 快照：`{ "deviceId": "measurement-1", "commandId": "…或 null", "state": "idle|running|delayed|succeeded|failed", "progress": 0, "sequence": 0 }`。progress 范围 0–100，sequence 在设备进程内递增；SiLA 命令自身进度遵循 SDK 的 0–1 范围。重启后 sequence 和去重缓存重置。

JSON 内容是本演示 Feature 的版本化负载约定，不是其他 SiLA 设备自动支持的通用能力。真实适配器应实现同一 XML，并运行同一设备契约测试；当前尚未实现真实适配器。

`generated/` 完全由 sila2 0.14.0 生成，禁止手改。从仓库根目录重新生成：

```powershell
.\.venv\Scripts\sila2-codegen.exe generate-feature-files --overwrite --output-directory contracts/sila2/generated contracts/sila2/ExperimentDevice-v1_0.sila.xml
```

本地演示关闭 TLS 和服务发现，监听 `127.0.0.1:50052`。订阅不提供持久化游标、断线补发或自动重连保证。

## ActionSemantics Feature v1.0

源契约为 `ActionSemantics-v1_0.sila.xml`。只读属性 Definitions 返回符合 `contracts/schemas/capabilities/action-semantics-v1.schema.json` 的 JSON 声明，包含动作参数、SiLA 执行绑定、前置条件、资源、成功效果和完成判据。此 Feature 是本项目扩展，非 SiLA 2 标准化调度协议。

当前只声明已实现的 simulation.execute。属性不执行命令，不改变设备状态，也不代表当前能立即执行。声明变更需更新 definitionVersion 并重新注册；详细语义见 `contracts/schemas/capabilities/README.md`。

```powershell
.\.venv\Scripts\sila2-codegen.exe generate-feature-files --overwrite --output-directory contracts/sila2/generated contracts/sila2/ActionSemantics-v1_0.sila.xml
```

## DeviceMaintenance Feature v1.0

新增源契约 `DeviceMaintenance-v1_0.sila.xml`，不改变现有 ExperimentDevice Feature。

- `State`：不可观察属性，JSON 快照包含 deviceId、incidentId、faultCode、state、revision、recipe、completed 和 history。state 为 ready、faulted、diagnosed、repairing 或 awaiting_self_test。recipe 为适用的检查说明和有序维修步骤；ready 时可保留上一故障及历史以供追溯。
- `Perform(RequestId, IncidentId, Action, ExpectedRevision)`：不可观察命令，执行快速的模拟操作并返回 JSON Result，含 accepted、message、device。Action 包含 inspect、self_test 及当前 recipe 定义的操作。先检查，再按序完成所有专属维修步骤，最后自检；错误操作、自检过早、版本过期不会清除故障。此处自检验证模拟状态机，不代表真实设备物理检测。

不同故障的维修步骤为：channel_blockage 先 flush_channel 再 replace_filter；sensor_drift 先 clean_sensor 再 calibrate_sensor；loose_cable 先 reseat_cable 再 secure_connector。相同 RequestId 和原始字段返回同一缓存结果；ID 重用但字段不同会拒绝。设备端保存故障及维修进度，工作流保存独占预留，平台保存演示审计记录；均不持久化。

重新生成新 Feature：

```powershell
.\.venv\Scripts\sila2-codegen.exe generate-feature-files --overwrite --output-directory contracts/sila2/generated contracts/sila2/DeviceMaintenance-v1_0.sila.xml
```
