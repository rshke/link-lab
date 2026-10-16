# 设备能力读取 API v1

`GET /v1/devices/measurement-1/capabilities` 返回设备启动注册时读取的、已校验的动作语义快照：

```json
{
  "deviceId": "measurement-1",
  "definitionVersion": 1,
  "contentHash": "sha256:摘要",
  "retrievedAt": "UTC时间",
  "definition": {"protocolVersion": "1.0", "deviceId": "measurement-1", "其他字段": "见 schema"}
}
```

上例仅展示响应结构，definition 的实际完整格式见 `contracts/schemas/capabilities/action-semantics-v1.schema.json`。快照通过 SiLA 2 ActionSemantics.Definitions 读取，不读取模拟器的本地配置文件。网关还通过 SiLAService 检查实际 Feature 定义，验证所有命令、参数、属性和结果绑定。

contentHash 为 definition 按键排序、无额外空白、ensure_ascii=true 编码为 UTF-8 JSON 后的 SHA-256，前缀 sha256:；不包含 retrievedAt。相同键值的不同字段排列生成相同摘要。当前声明仅含整数、布尔值及字符串，不承诺任意 JSON 数字表示之间的等价规范化。

无效声明会使该演示网关启动失败，不以默认能力掩盖错误。有效快照在当前网关进程内冻结，不在设备故障时改写，不自动热加载或重连刷新。当前只注册固定设备 measurement-1，未实现多设备发现。
