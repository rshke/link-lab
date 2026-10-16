# Device gateway internal API v1

入口默认 `http://127.0.0.1:8012`，仅供本地工作流及开发测试调用，JSON HTTP。

- `GET /health` → `{ "service": "device-gateway", "status": "ready" }`，表示已连接并初始化协议客户端；不是持续连接探针。
- `POST /v1/commands`：请求 `{ "commandId": "run UUID:0", "deviceId": "measurement-1", "durationMs": 400 }`。只接受这三个字段。映射至 SiLA 2 `ExperimentDevice.Execute(CommandId, DurationMs)`，等待其结束，返回 `{ "commandId": "…", "state": "succeeded|failed", "chaos": "normal|delay|fail" }`。设备失败时包含 `error`。业务失败是显式命令结果，SiLA 2 调用本身可以正常完成。
- `GET /v1/observations` → `{ "observations": [...] }`，为 SiLA 2 `Status` 订阅收到的最近 1000 个快照，格式见 `contracts/sila2/README.md`。此缓存用于开发观察，不是可靠事件总线或权威运行状态。

格式错误返回 400 / `{ "error": "说明" }`；协议错误或等待超过 12 秒返回 502 / 同一错误结构。超时不能证明设备动作停止，网关不自动重试。幂等由模拟器按 CommandId 保证，仅在设备进程生命周期内有效。
