# 共享技术库

有实际复用需求后再创建具体技术包，例如追踪、日志或生成的 API 客户端。每个包拥有自己的依赖清单、公开入口和测试。

当前 `interaction_http.py` 为本地通信演示复用的 JSON HTTP 传输，公开入口为 `serve(port, dispatch)` 和 `request(url, payload=None)`，只依赖 Python 标准库，平台、工作流、网关与模拟器入口使用它。通过 `tests/integration/test_interaction.py` 验证真实进程通信；不提供业务规则或持久化。

业务状态机、验证规则、资源锁和持久化实体归属各自服务，不进入公共包。不得通过公共包转发其他服务的内部实现。
