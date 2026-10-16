# Workflow internal API v1

入口默认 `http://127.0.0.1:8011`，仅供本地平台调用，JSON HTTP。

- `GET /health` → `{ "service": "workflow-worker", "status": "ready" }`。
- `POST /v1/runs`：接收 `{ "admissionVersion": 1, "steps": [...] }`，steps 为平台校验后的有序步骤，格式见 platform 契约。返回 `{ "runId": "UUID", "state": "accepted" }`。单次只预留一个运行；占用时拒绝新运行。
- `GET /v1/runs/{runId}` → `{ "runId": "UUID", "state": "running|succeeded|failed|unknown", "results": [...] }`，异常时增加 `error`。results 为网关命令结果，按执行顺序排列。命令 ID 为 `{runId}:{从零开始的步骤序号}`。

工作流依次执行步骤；首个设备失败后停止后续步骤。已确认成功或失败时释放资源。通信失败或结果不明时置 unknown 并保留设备预留，Demo 需人工核实后重启；不自动重发命令。

错误使用 HTTP 400 / `{ "error": "说明" }`；下游错误使用 502。运行和资源状态仅在本进程内存，不具备持久化恢复。
