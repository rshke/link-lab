# 实验室操作台

`maintenance.html` 已提供最小设备维修模拟页面，由平台 API 同源托管在 `/maintenance`，只调用平台维护接口，无额外前端依赖。支持检查、按故障选择维修操作、自检和历史记录，见 `docs/development/device-maintenance.md`。其他正式前端目录仍为预留：`src/features/` 按会话、实验、运行和数字孪生等业务功能组织，`src/components/` 放应用内通用组件，`src/api/` 封装公开服务接口，`tests/` 保存前端测试。

前端读取平台 API 和孪生投影，通过平台 API 提交受权限约束的操作。前端不连接 SiLA 2、厂商 SDK、数据库或消息总线。

现有 `../../device-twin-demo/` 保持原位作为界面原型；本目录暂未迁移或复制其实现。
