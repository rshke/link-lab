# 平台设备维护 API v1

本地单设备演示，入口 `http://127.0.0.1:8010`。`GET /maintenance` 提供同源操作页面；浏览器不连接网关、SiLA 2 或模拟器管理端口。

- `GET /v1/maintenance`：返回工作流拥有的设备预留标记 `workflowReserved`，及设备提供的维护快照，格式见 `contracts/sila2/README.md`。
- `POST /v1/maintenance/actions`：JSON 请求仅包含 `requestId`、`incidentId`、`action`、`expectedRevision`。前三项为 1–100 字符字符串，revision 为非负整数。平台校验后交付工作流；工作流预留设备，再经网关和 SiLA 2 执行。响应 `{ "accepted": true, "message": "…", "device": {...} }`。操作不适用或版本过期时 accepted 为 false，不改变维修进度。
- `GET /v1/maintenance/audit`：返回 `{ "records": [...] }`，按 requestId 记录平台收到的执行结果、时间、动作、版本及本地演示操作者。重复投递不增加审计条目；设备本身的操作历史包含拒绝原因。

格式或准入错误返回 HTTP 400；下游故障返回 502。未确认结果需使用原请求 ID 和原始字段重试，不能直接生成新请求重复维修。设备动作发生与平台审计写入尚无持久事务保证。快照响应可能是去重缓存中的历史结果，执行后应再次 GET 获取当前状态。

当前无真实用户认证，actor 固定标记为 local-demo-operator，不代表生产授权；记录仅在内存。平台并不直接修改设备故障，也不会自动恢复已失败实验或重做样品。
