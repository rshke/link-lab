# 智能实验室平台

本仓库采用 monorepo 管理前端、平台服务、设备适配器和设备模拟器。组件共享版本化接口契约，各自拥有业务实现、配置和数据。目前已有一条最小系统通信链路：平台验证准入 → 工作流 → 设备网关 → SiLA 2 检测设备模拟器，支持状态订阅与简单 chaos 注入。其他模块仍为骨架。

## 最小系统交互演示

通过四个独立进程验证 HTTP 与 SiLA 2 通信，启动、接口与限制见 [运行说明](docs/development/interaction-demo.md)。

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-interaction.txt
.\.venv\Scripts\python scripts/interaction_demo.py serve
```

另开终端执行 `.\.venv\Scripts\python scripts/interaction_demo.py normal`，也可将 normal 改为 delay 或 fail，观察状态上报和最终结果。

## 目录

```text
apps/
  console/                  正式操作台预留位置
services/
  platform-api/             实验规格、确定性验证、审批与执行准入
  agent-service/            对话、实验草案、知识检索与运行解释
  workflow-worker/          排程、资源锁、运行状态机与异常处置
  device-gateway/           设备发现、命令路由、幂等与设备事件转换
  twin-service/             事件投影、状态查询、实时推送与回放
adapters/
  sila2/                    部署在设备侧的真实设备适配器
simulators/
  robot/                    机器人模拟器
  liquid-handler/           液体处理器模拟器
  measurement/              检测设备模拟器
  runtime/                  模拟器专用时钟、场景与故障注入组件
contracts/
  api/                      各服务的公开 API 定义
  schemas/                  实验规格、计划、能力等数据契约
  events/                   事件信封与各领域事件定义
  sila2/                    真机与模拟器共用的 Feature 定义
packages/                   按实际需求提取的技术库
tests/
  contract/                 服务接口和设备协议契约测试
  integration/              跨组件集成测试
  e2e/                      全链路场景
  fixtures/                 测试数据与固定场景
deploy/                     本地集成拓扑、环境配置与可观测性
scripts/                    仓库开发和检查工具
docs/                       服务边界、架构决策与开发说明
device-twin-demo/           现有孪生界面原型，保留原有运行方式
```

每个服务内部按 `domain → application → ports` 定义业务及接口，`infrastructure` 实现外部依赖，`interfaces` 承接 HTTP、事件或 Worker 入口。箭头表示业务处理顺序；源码依赖方向以[边界规则](docs/architecture/service-boundaries.md)为准。

## 开发约定

- 服务间通过公开 API 或事件交互，禁止直接引用其他服务源码、访问其他服务数据表。
- 契约统一存放于 `contracts/`，不共享 ORM 实体、业务状态机或验证规则实现。
- Agent 生成草案、查询投影和提交平台请求；设备控制必须经过确定性验证及执行准入。
- 平台服务连接设备网关，网关连接真实设备适配器或模拟器。浏览器和 Agent 不连接设备协议端点。
- 单元测试归属各组件自己的 `tests/`；根目录测试只验证跨组件行为。
- 各组件独立管理依赖与构建。待语言和运行时确定后添加对应清单与锁文件；当前不添加空壳启动命令或不可运行的部署配置。

服务目录表示职责与演进边界，并不要求首期全部独立部署。参见[monorepo 决策](docs/adr/0001-monorepo.md)。

专门的 Chaos 子系统设计见 [Chaos 设计文档](docs/architecture/chaos-system-design.md)，包含动作故障点、概率判定、多动作关联、管理接口及实施阶段；该子系统尚未实现。

AI 根据实验反馈持续改进方案的闭环见 [隐藏规律实验环境设计](docs/architecture/experiment-world-design.md)。世界服务拥有私有产物规律，AI 仅通过获准实验和公开测量学习；该系统尚未实现。

## 设计依据

架构基线见根目录的《全链路智能实验室系统架构设计.docx》和 `智能实验室模块详细设计/` 中的七份详细设计。原始设计文件、生成脚本与质检产物保持原位。服务划分与原设计的映射见[服务边界](docs/architecture/service-boundaries.md)。
