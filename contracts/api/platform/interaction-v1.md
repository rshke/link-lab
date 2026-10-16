# Platform interaction API v1

所有请求和响应为 JSON，本地入口默认 `http://127.0.0.1:8010`。此版本仅用于单设备通信演示。

- `GET /health` → `{ "service": "platform-api", "status": "ready" }`。
- `POST /v1/experiments`：请求 `{ "steps": [{ "deviceId": "measurement-1", "durationMs": 400 }] }`。只接受这些字段；步骤数量 1–10，时长为 100–5000 的整数，设备仅支持 `measurement-1`。验证通过后交付工作流，返回 `{ "runId": "UUID", "state": "accepted" }`；accepted 表示已接收，不表示设备完成。
- `GET /v1/runs/{runId}`：代理工作流拥有的运行状态，格式见 workflow 契约。

格式、验证、资源冲突、未知 ID 返回 HTTP 400 / `{ "error": "说明" }`；下游或协议错误返回 502 / 同一错误结构。Demo 没有认证或人工审批；合法规格即本地准入，不代表生产授权策略。
