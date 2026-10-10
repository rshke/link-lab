import { ChevronDown, Layers, SlidersHorizontal } from "lucide-react";
import { deviceCapabilities } from "./device-capabilities";
export function DeviceCapabilities({deviceId,state}:{deviceId:string;state:string}){
 const capability=deviceCapabilities[deviceId];
 return <section className="capability-panel" aria-label="设备能力">
  <div className="capability-heading"><Layers size={16}/><h3>设备能力</h3><span>{capability.actions.length} 个动作</span></div>
  <h4>{capability.name}</h4><p>{capability.description}</p>
  <div className={`capability-availability ${state==="异常"?"blocked":""}`}>{state==="异常"?"设备异常 · 动作暂不可执行":state==="运行中"?"设备运行中 · 新任务需检查资源与条件":"设备空闲 · 任务仍需通过执行条件校验"}</div>
  <small className="capability-help">支持的动作 · 点击查看参数与执行条件</small>
  {capability.actions.map((action,index)=><details className="capability-action" key={action.name} open={index===0?true:undefined}>
   <summary><span className="action-number">{String(index+1).padStart(2,"0")}</span><b>{action.name}</b><ChevronDown size={15}/></summary>
   <div className="action-content"><p>{action.description}</p><span className="action-source">{action.source}</span>
    <h5><SlidersHorizontal size={12}/> 参数示例</h5><dl>{action.parameters.map(parameter=><div key={parameter.name}><dt>{parameter.name}</dt><dd>{parameter.example}</dd></div>)}</dl>
    <h5>执行条件</h5><p>{action.prerequisite}</p><h5>执行结果</h5><p>{action.output}</p>
   </div>
  </details>)}
  <p className="capability-footnote">演示能力目录，参数为任务示例；实际支持范围以设备型号与驱动配置为准。</p>
 </section>
}
