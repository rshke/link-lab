# 网关设备维护内部 API v1

`GET /v1/maintenance` 映射 SiLA 2 `DeviceMaintenance.State`。`POST /v1/maintenance/actions` 将 requestId、incidentId、action、expectedRevision 映射到 `DeviceMaintenance.Perform`，返回其 JSON Result。设备固定为 measurement-1。请求仅供平台准入后的工作流调用，本地演示没有生产服务身份认证。

维护状态不由网关自行推断；协议异常向上返回 502，调用方将其视为结果未确认。设备明确拒绝操作使用 HTTP 200 / accepted=false；不将业务拒绝错误地转换为通信结果不明。
