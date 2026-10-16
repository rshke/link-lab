# 最小系统通信链路

目标是运行系统之间的接口。实现单个检测设备的最小实验动作，并提供 [维修模拟页面](device-maintenance.md)；其他设备和业务模块保持骨架。

```text
实验规格
  ↓ HTTP POST /v1/experiments
platform-api（确定性验证 / 本地准入） :8010
  ↓ HTTP POST /v1/runs
workflow-worker（运行状态 / 单设备预留 / 顺序执行） :8011
  ↓ HTTP POST /v1/commands
device-gateway（协议映射 / 状态订阅） :8012
  ↓ SiLA 2 Observable Command: ExperimentDevice.Execute
measurement simulator（模拟动作 / chaos） :50052
  ↑ SiLA 2 Observable Property: ExperimentDevice.Status
device-gateway（打印状态上报，缓存最近 1000 个快照）

模拟器最终结果 → SiLA 命令响应 → 网关 HTTP 响应 → 工作流运行结果
运行查询 → 平台 GET /v1/runs/{runId} → 工作流

开发测试 → 模拟器管理 HTTP :8013 /v1/chaos
```

SiLA 2 是设备侧边界，平台先验证规格，工作流负责运行及资源，网关才接触设备协议。四个进程没有跨服务源码导入或共享业务存储。当前尚未实现 Agent、孪生投影、消息总线、数据库和真实适配器。

## 安装与启动

建议 Python 3.13；本次验证环境为 Windows / Python 3.13.5。在仓库根目录运行：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-interaction.txt
.\.venv\Scripts\python scripts/interaction_demo.py serve
```

若系统 Python 创建 venv 时无法引导 pip，可使用 uv：

```powershell
uv venv --python 3.13 .venv
uv pip install --python .venv/Scripts/python.exe -r requirements-interaction.txt
```

启动器先检查五个端口未占用，然后依次启动模拟器、网关、工作流和平台，并等待健康检查。Ctrl+C 关闭子进程。生成的 SiLA 协议代码已提交，无需首次启动时手动生成；SDK 自身会在临时目录编译 protobuf，因此需要临时目录可写。

另开终端运行以下任一场景：

```powershell
.\.venv\Scripts\python scripts/interaction_demo.py normal
.\.venv\Scripts\python scripts/interaction_demo.py delay
.\.venv\Scripts\python scripts/interaction_demo.py fail
```

normal 返回 succeeded；delay 在 50% 增加 500ms 延迟，仍成功；fail 在 50% 返回 failed 并使工作流停止。启动终端会持续打印收到的 SiLA 状态，包含 commandId、state、progress 和 sequence。运行终端显示最终运行结果。

也可以直接提交规格并查询：

```powershell
$spec = @{ steps = @(@{ deviceId = 'measurement-1'; durationMs = 1000 }) } | ConvertTo-Json -Depth 5
$run = Invoke-RestMethod http://127.0.0.1:8010/v1/experiments -Method Post -ContentType application/json -Body $spec
Invoke-RestMethod "http://127.0.0.1:8010/v1/runs/$($run.runId)"
Invoke-RestMethod http://127.0.0.1:8012/v1/observations
```

## 职责、数据与契约

| 进程 | 数据所有权 | 外部依赖 | 契约 |
| --- | --- | --- | --- |
| platform-api | 本次规格的校验与准入，无持久化记录 | 工作流 HTTP | `contracts/api/platform/interaction-v1.md` |
| workflow-worker | 内存运行记录、单设备预留 | 网关 HTTP | `contracts/api/workflow/interaction-v1.md` |
| device-gateway | 内存设备观察缓存 | sila2 SDK、模拟器 SiLA 2 | `contracts/api/device-gateway/interaction-v1.md` |
| measurement simulator | 动作状态、已完成命令去重、下次 chaos 配置 | sila2 SDK | `contracts/sila2/`、`contracts/api/simulator/management-v1.md` |

`packages/interaction_http.py` 仅复用 JSON HTTP 传输，不包含业务规则。模拟引擎 `simulators/runtime/engine.py` 不依赖 SDK，SiLA 映射在模拟器入口中完成。平台及工作流的应用层通过注入的函数端口访问下游，HTTP 依赖仅出现在入口组装。

## 验证

停止已有演示进程，再运行：

```powershell
.\.venv\Scripts\python tests/integration/test_interaction.py
```

测试自动启动并清理四个独立进程，通过真实 HTTP 和 SiLA 2 验证六组行为：正常执行及去重、故障回传及下次恢复正常、延迟状态及进度订阅、非法规格拒绝、资源预留及多步骤顺序执行、设备进程断开后结果 unknown 且保留资源。不是设备物理行为或生产业务验收。

## 当前限制

单设备、内存状态、固定本机端点，无认证、TLS、人工审批和持久化；合法规格即本地准入。幂等缓存仅对已完成命令、当前设备进程有效。执行失败不自动重试；通信结果不明时保留资源，需要开发者核实后重启。状态属性是快照流，没有可靠事件信封、回放、断线补发或自动重连。本演示不承诺真实硬件接入。

SiLA 实现方式参考 [SDK Feature 实现说明](https://sila2.gitlab.io/sila_python/content/server/feature_implementation.html) 和 [协议代码生成说明](https://sila2.gitlab.io/sila_python/content/code_generator/generate_feature_files.html)。
