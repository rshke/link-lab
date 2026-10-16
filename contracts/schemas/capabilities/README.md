# 动作语义声明 v1

`action-semantics-v1.schema.json` 定义自有的、由 SiLA 2 ActionSemantics.Definitions 属性承载的 JSON 格式。它不是 SiLA 2 核心标准自带的调度语义。schema 归平台契约维护，设备实现及网关共同遵循，不能由单台设备任意扩展词汇后要求平台执行。

## 文档字段

| 字段 | 含义 |
| --- | --- |
| protocolVersion | 格式版本，当前仅接受 1.0，未知版本拒绝注册 |
| definitionVersion | 该设备声明的正整数版本；声明变化需递增 |
| deviceId | 必须与网关注册的设备标识相同 |
| stateBindings | 统一状态事实到实际 SiLA 属性的映射 |
| actions | 动作 ID、参数、执行绑定、前置条件、资源、成功效果和完成判据 |

action.id 标识统一动作语义，不等同于厂商方法名。binding 使用完整 SiLA Feature 标识和命令名，commandIdParameter 由执行层提供。parameters 将平台参数映射到 SiLA 参数并声明单位及范围。当前 v1 只支持必填的整数毫秒参数，不支持任意 JSON Schema 或动态代码。

preconditions 是合取条件，全部满足才有资格执行。当前唯一事实为 `device.maintenance_state`，scope=device 指向本声明的 deviceId，operator=equals、value=ready。stateBindings 指定从不可变的 Feature 接口读取实时 JSON 属性中的 state；声明本身不携带当前设备是否可用。

resources 中的 id 是同一部署内唯一的物理资源标识，不按动作另起别名；当前只接受 exclusive，锁从设备动作派发前持续到明确的终态或工作流处置确认。资源被占用时，即使维护状态为 ready，也不能直接开始另一个动作。与维修共享同一设备占用语义，不能因设备属性仍为 ready 而跳过工作流预留。

effects 描述成功完成后成立的事实。当前只有 `command.succeeded`，scope=command 绑定本次 commandId；失败、超时或 unknown 不产生该事实。声明效果不等于事实已经发生，执行层必须观察完成证据后才能确认。

completion 当前要求可观察命令的最终 String 响应，按 JSON 解码，只有 state=succeeded 才算成功。“命令已接收”、进度到 100% 或 SiLA 调用正常结束都不能单独替代此判据，因为业务结果仍可能为 failed。

## 约束与演进

字段采用封闭 schema；未知字段、未知事实、操作符、单位和完成判据直接拒绝。动作 ID 必须唯一；每个动作内资源 ID 和 SiLA 参数绑定不能重复；参数范围不能倒置；声明引用的 Feature、命令、属性、参数类型及响应类型须与设备实际发布的 Feature 定义一致。

网关仅使用仓库内的 schema，拒绝超过 64 KiB 的属性载荷和重复 JSON 字段，不下载设备提供的 schema，不导入设备提供的代码。结构及绑定校验不能证明设备真实行为正确，接入设备仍需契约测试。

当前词汇刻意限制在已实现的单设备定时模拟动作。不接受 sample.mixed 等尚无权威事实来源和样品绑定的状态。后续支持样品与跨动作依赖时，先定义 sampleId/stepId 绑定、事实来源、失败效果和共享资源模型，再增加版本；不能只加入自由文本让规划器猜。重大格式变化新增主版本，生成协议代码不得手改。
