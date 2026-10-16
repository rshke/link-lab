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
