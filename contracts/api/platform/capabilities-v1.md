# 平台设备动作声明查询 API v1

`GET /v1/devices/measurement-1/capabilities` 读取网关已验证的设备声明快照，原样返回 deviceId、definitionVersion、contentHash、retrievedAt 和 definition。格式见网关 `capabilities-v1.md`，仅为查询，不授予执行权限。

浏览器和 Agent 通过平台读取，不连接 SiLA 2 设备。平台访问网关公开 API，不读取网关表或模拟器文件。下游不可达返回 502，未知路由或设备返回 400。

目前实验 v1 准入和工作流仍为既有单设备实现，尚未依据此快照生成计划或自动解析任意动作；也尚未在每个准入记录中固化能力版本。查询能力与具备通用编排能力是两件事，后续实施见 `docs/architecture/action-semantics.md`。
