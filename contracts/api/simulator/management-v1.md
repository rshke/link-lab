# Simulator management API v1

模拟器专用本地开发入口 `http://127.0.0.1:8013`，与 SiLA 2 执行协议分离，平台不调用此接口。

- `GET /health` → `{ "service": "measurement-simulator", "status": "ready" }`。
- `POST /v1/chaos`：请求 `{ "mode": "normal|delay|fail" }`，只接受 mode 字段。响应 `{ "nextCommandMode": "…" }`。

配置只影响下一个新命令，领取后自动恢复 normal；重复的已完成命令不消耗配置。normal 按时执行；delay 在 50% 额外等待 500ms；fail 在 50% 返回 failed。非法配置返回 HTTP 400 / `{ "error": "说明" }`，不会修改配置。

## 持续故障注入 v2

`POST /v2/faults` 接受 `{ "code": "channel_blockage|sensor_drift|loose_cable" }`，仅供 CLI 或测试工具调用，返回设备维护快照。设备执行中或已有未关闭故障时拒绝；不覆盖现有维修进度。故障持续阻止新实验，直到完成匹配维修步骤与自检。loose_cable 模拟内部连接，不模拟 SiLA 服务断线。现有 v1 fail 仍为一次性实验失败，不自动创建持续维修故障。
