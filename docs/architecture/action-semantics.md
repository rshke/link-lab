# 基于 SiLA 2 的内部动作语义协议

设备通过自定义 ActionSemantics Feature 发布结构化声明，网关读取、校验并形成快照，平台提供查询入口。执行 Feature 继续负责实际动作。这样设备接入方提供声明，编排层按统一词汇处理动作和约束，不从厂商名称或文字说明猜测依赖。

## 当前实现

```text
设备本地动作声明 JSON
    ↓ 模拟器发布为只读属性
SiLA 2 ActionSemantics.Definitions
    ↓ 网关通过协议读取
JSON Schema 校验 + SiLA Feature 绑定校验
    ↓ 冻结版本和内容摘要
网关能力快照 API → 平台查询 API
```

源声明位于 [检测设备配置](../../simulators/measurement/config/action-semantics-v1.json)，格式见 [内部 schema](../../contracts/schemas/capabilities/README.md)。设备启动时载入配置，运行期间保持固定。网关不读取该文件，也不导入设备源码；它通过真正的 SiLA 2 属性获取声明。

当前只声明 `simulation.execute`，映射已经实现的 ExperimentDevice.Execute。它要求维护状态为 ready、独占本设备资源、接收 durationMs 参数，并以最终 JSON 结果 state=succeeded 确认成功。不宣称已经实现样品变化、加料、混匀或科学检测结果。维修动作仍由原有 DeviceMaintenance Feature 及维护流程负责，此版不把它们注册成通用实验动作。

网关用本地 JSON Schema 校验结构，再用设备通过 SiLAService 发布的真实 Feature 定义核对命令、属性、参数和响应。跨字段不变量保留在网关领域层；JSON Schema、XML 和 SDK 交互属于基础设施。缺失 Feature、未知版本或绑定不匹配会导致该演示网关拒绝启动，不把不理解的声明交给排程器。

## 如何推导等待与并行

目标规划器需要合并两类输入：设备声明的动作前置条件、成功效果和资源占用，以及实验方案的步骤、样品和工艺依赖。

1. 按统一动作 ID 查找候选设备，验证参数、单位和范围，并固化使用的快照版本与摘要。
2. 将实验显式 dependsOn、数据依赖和可绑定的状态依赖转换为执行图中的边，检查环路、缺失输入和不可达前置条件。
3. 只有所有依赖步骤完成、实时前置条件满足，且全部资源被成功预留后才可派发。
4. 无依赖且无资源冲突的步骤只是并行候选，还要满足平台的并发策略和接入设备契约。不能把“没有声明冲突”当作安全证明。
5. 成功事实由设备完成证据产生；失败和 unknown 走工作流处置，不能靠声明提前满足后续步骤。

这些规划能力尚未实现。当前工作流继续单设备顺序执行，查询新增声明不会自动改变已有实验的行为，也不会关闭原有维护和资源准入。

## 事实与资源的语义

scope=device 的事实指向声明所属的设备；scope=command 指向当前命令，不会自动传播成任何样品的化学状态。`ready` 只表示维护门槛满足，是否空闲由工作流独占预留决定。实时维护状态变化不改变设备“支持哪些动作”的静态声明。

未来加入 `sample.mixed` 时，必须声明 sampleId 如何从步骤参数绑定，哪个成功动作能够产生该事实，哪个事实来源有权确认它，以及后续动作是否使其失效。设备单方面写一个字符串不能形成可信的跨设备工艺状态。工艺规定的“先加 A 再加 B”仍来自实验方案，不由单台设备推断。

共享物理资源必须使用部署内统一 ID，例如两个动作共享同一个移液头时都声明同一资源。网关接入策略和设备契约测试检查声明是否符合实际设备，并防止通过另起资源别名绕过平台限制。

## 查询与验证

按 [运行说明](../development/interaction-demo.md) 安装新增依赖并启动演示后，查询：

```powershell
Invoke-RestMethod http://127.0.0.1:8010/v1/devices/measurement-1/capabilities
```

响应包含 definitionVersion、contentHash、retrievedAt 和完整 definition。声明在当前设备及网关进程内冻结；修改配置后需重启二者并重新注册。缓存不是持续在线证明，读取能力不能替代设备实时状态检查。

测试命令：

```powershell
.\.venv\Scripts\python services/device-gateway/tests/test_capabilities.py
.\.venv\Scripts\python tests/integration/test_capability_discovery.py
```

单元测试覆盖未知版本和词汇、重复字段和动作、错误范围与绑定、重复资源及摘要稳定性。集成测试通过四个进程验证声明从 SiLA 2 进入网关再到平台，并确认故障发生时能力不被重写。原有维护及实验通信测试继续回归。

## 下一步

先定义版本化的实验步骤模型，包含 stepId、actionId、parameters、dependsOn 及资源绑定，再让平台在准入时固定快照，工作流按固定快照生成并执行计划。样品事实、多设备注册和动态并行排程分别演进，不与本次声明读取混为同一交付。
