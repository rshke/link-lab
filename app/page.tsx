"use client";
import { useEffect, useMemo, useRef, useState, type PointerEvent } from "react";
import { Activity, AlertTriangle, Bot, FlaskConical, Gauge, ListTree, Minus, Pause, Play, Plus, Server, TestTube2, Wifi, X } from "lucide-react";
import { Sheet, SheetClose, SheetContent, SheetDescription, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import Link from "next/link";
import { deviceCapabilities } from "./device-capabilities";
import { DeviceCapabilities } from "./device-capabilities-panel";
type Workload={experiment:string;sample:string;slot:string;state:string;progress:number};
type Device={id:string;name:string;type:string;state:"运行中"|"空闲"|"异常";action:string;progress:number;detail:string;mode:"独占"|"容量并发"|"批处理";capacity:number;workloads:Workload[]};
const devices:Device[]=[
{id:"robot-01",name:"移动机器人 01",type:"RobotControl",state:"运行中",action:"搬运 plate-001 至检测设备",progress:64,detail:"位于通道 B，载荷 1 个孔板",mode:"独占",capacity:1,workloads:[{experiment:"EXP-2026-014",sample:"plate-001",slot:"载台",state:"搬运中",progress:64}]},
{id:"liquid-01",name:"液体处理器 01",type:"LiquidHandling",state:"空闲",action:"等待下一任务",progress:0,detail:"枪头 72%，台面已清洁",mode:"独占",capacity:1,workloads:[]},
{id:"reader-01",name:"微孔板检测仪 01",type:"Measurement",state:"异常",action:"等待设备侧自检恢复",progress:38,detail:"舱门未关闭，检测已暂停；平台等待设备人员处理",mode:"独占",capacity:1,workloads:[{experiment:"EXP-2026-009",sample:"plate-009",slot:"读板舱",state:"异常暂停",progress:38}]},
{id:"incubator-01",name:"恒温培养设备 01",type:"Incubation",state:"运行中",action:"3 个实验并发培养",progress:58,detail:"37.0 °C，CO₂ 5.0%，三个槽位独立计时",mode:"容量并发",capacity:8,workloads:[{experiment:"EXP-2026-014",sample:"plate-002",slot:"槽位 A1",state:"培养中",progress:72},{experiment:"EXP-2026-021",sample:"plate-017",slot:"槽位 A2",state:"培养中",progress:46},{experiment:"EXP-2026-023",sample:"plate-022",slot:"槽位 B1",state:"培养中",progress:19}]},
{id:"centrifuge-01",name:"离心设备 01",type:"Centrifugation",state:"空闲",action:"转子已平衡，等待任务",progress:0,detail:"转子容量 8，舱盖锁定正常",mode:"批处理",capacity:8,workloads:[]},
{id:"imager-01",name:"显微成像设备 01",type:"Imaging",state:"运行中",action:"采集 EXP-2026-021 图像",progress:31,detail:"20× 物镜，通道 GFP，正在扫描视野 4 / 12",mode:"独占",capacity:1,workloads:[{experiment:"EXP-2026-021",sample:"plate-018",slot:"成像台",state:"采集中",progress:31}]}];
const initialEvents=[["14:32:18","机器人","已到达设备交接点 B","ok"],["14:32:12","工作流","步骤 3 搬运开始","info"],["14:31:54","检测仪","告警：舱门未关闭，等待设备侧处理与自检","error"],["14:31:48","液体处理","稀释步骤完成","ok"],["14:31:03","Agent","实验计划通过确定性验证","info"]];
const experimentRuns=[
 {id:"EXP-2026-014",name:"板式稀释与吸光度检测",device:"培养设备 · A1",eta:"14:38",active:3,steps:["任务验证","孔板准备","液体稀释","恒温培养","机器人搬运","吸光度检测"]},
 {id:"EXP-2026-021",name:"细胞活性筛选",device:"培养设备 · A2",eta:"14:51",active:3,steps:["任务验证","样品装载","恒温培养","显微成像","荧光检测","结果归档"]},
 {id:"EXP-2026-023",name:"培养条件探索",device:"培养设备 · B1",eta:"15:06",active:2,steps:["任务验证","液体制备","离心处理","恒温培养","图像采集","结果归档"]}
];
type RouteStatus="done"|"current"|"upcoming";
const experimentRoutes={
 "EXP-2026-014":[{deviceId:"liquid-01",status:"done"},{deviceId:"incubator-01",status:"current"},{deviceId:"robot-01",status:"upcoming"},{deviceId:"reader-01",status:"upcoming"}],
 "EXP-2026-021":[{deviceId:"incubator-01",status:"done"},{deviceId:"imager-01",status:"current"},{deviceId:"reader-01",status:"upcoming"}],
 "EXP-2026-023":[{deviceId:"liquid-01",status:"done"},{deviceId:"centrifuge-01",status:"current"},{deviceId:"incubator-01",status:"upcoming"},{deviceId:"imager-01",status:"upcoming"}]
} satisfies Record<string,{deviceId:string;status:RouteStatus}[]>;
type TransferStatus="done"|"current"|"upcoming";
// Sample handoffs have their own state, independent of device execution.
const experimentTransfers:Record<keyof typeof experimentRoutes,TransferStatus[]>={
 "EXP-2026-014":["done","upcoming","upcoming"],
 "EXP-2026-021":["done","upcoming"],
 "EXP-2026-023":["done","upcoming","upcoming"]
};
// Separate handoff lanes terminate at the visible (80%-scaled) device edges.
const transferPaths:Record<keyof typeof experimentRoutes,string[]>={
 "EXP-2026-014":["M100 199.5 V285 H100 V342","M248 390 H290 V290 H350","M470 260 H780 V202.5"],
 "EXP-2026-021":["M248 390 H305 V422 H370","M530 395 H590 V285 H735 V202.5"],
 "EXP-2026-023":["M230 199.5 V225 H405 V168.2","M490 168.2 V295 H210 V342","M248 405 H310 V420 H370"]
};
const transferLabels={done:"已交接",current:"传递中",upcoming:"待传递"};
function Status({state}:{state:Device["state"]}){return <span className={`status status-${state}`}>● {state}</span>}
export default function Home(){
 const mapViewport=useRef<HTMLDivElement>(null);
 useEffect(()=>{
  const viewport=mapViewport.current;if(!viewport)return;
  const observer=new IntersectionObserver(entries=>{
   for(const entry of entries){
    const element=entry.target as SVGElement;
    const clipped=1-entry.intersectionRatio;
    element.style.setProperty("--edge-opacity",String(1-clipped*.65));
    element.style.setProperty("--edge-blur",`${clipped*3}px`);
   }
  },{root:viewport,threshold:Array.from({length:41},(_,index)=>index/40)});
  viewport.querySelectorAll(".station,.robot").forEach(element=>observer.observe(element));
  return()=>observer.disconnect();
 },[]);
 const[pan,setPan]=useState({x:0,y:0});
 const[dragging,setDragging]=useState(false);
 const dragOrigin=useRef<{pointerId:number;x:number;y:number;panX:number;panY:number}|null>(null);
 function startPan(event:PointerEvent<HTMLDivElement>){
  if(event.button!==0||(event.target as Element).closest("button,a,.station,.robot,.route-summary,.map-toast"))return;
  dragOrigin.current={pointerId:event.pointerId,x:event.clientX,y:event.clientY,panX:pan.x,panY:pan.y};
  event.currentTarget.setPointerCapture(event.pointerId);setDragging(true);
 }
 function movePan(event:PointerEvent<HTMLDivElement>){
  const origin=dragOrigin.current;if(!origin||origin.pointerId!==event.pointerId)return;
  setPan({x:origin.panX+event.clientX-origin.x,y:origin.panY+event.clientY-origin.y});
 }
 function endPan(){dragOrigin.current=null;setDragging(false)}
 const[deviceOpen,setDeviceOpen]=useState(false);
 const[deviceView,setDeviceView]=useState<"list"|"detail">("list");
 function inspectDevice(device:Device){setSelected(device);setDeviceView("detail");setDeviceOpen(true)}
 const[selected,setSelected]=useState<Device>(devices[0]);const[running,setRunning]=useState(true);const[robotX,setRobotX]=useState(49);const[events,setEvents]=useState(initialEvents);const[zoom,setZoom]=useState(1);const[selectedExperiment,setSelectedExperiment]=useState<keyof typeof experimentRoutes|null>(null);
 // Keep motion phase across pauses; ease into each end of the corridor.
 const robotPhase=useRef(Math.acos((53.5-49)/18.5));
 useEffect(()=>{
  if(!running)return;
  let frame=0;
  let previous:number|undefined;
  const animate=(timestamp:number)=>{
   if(document.hidden){previous=undefined;frame=requestAnimationFrame(animate);return;}
   const elapsed=previous===undefined?0:Math.min(timestamp-previous,50);
   previous=timestamp;
   robotPhase.current=(robotPhase.current+elapsed*Math.PI/6400)%(Math.PI*2);
   setRobotX(53.5-18.5*Math.cos(robotPhase.current));
   frame=requestAnimationFrame(animate);
  };
  frame=requestAnimationFrame(animate);
  return()=>cancelAnimationFrame(frame);
 },[running]);
 const route=useMemo(()=>(selectedExperiment?experimentRoutes[selectedExperiment]:[]).map(node=>({...node,point:node.deviceId==="liquid-01"?[165,213]:node.deviceId==="reader-01"?[735,217]:node.deviceId==="incubator-01"?[160,330]:node.deviceId==="centrifuge-01"?[450,180]:node.deviceId==="imager-01"?[450,340]:[robotX*8.3,260]})),[selectedExperiment,robotX]);
 const routeStatus=(deviceId:string)=>selectedExperiment?route.find(node=>node.deviceId===deviceId)?.status:undefined;
 function injectFault(){setEvents(old=>[[new Date().toLocaleTimeString("zh-CN",{hour12:false}),"模拟器","注入故障：机器人路径被占用","error"],...old].slice(0,7));setRunning(false)}
 return <main className={`app-shell lab-overview ${selectedExperiment?"experiment-focused":""}`}>
  <header className="topbar"><div className="brand"><span className="brand-mark"><FlaskConical size={19}/></span><div><strong>LabFlow Twin</strong><small>实验室 A</small></div></div><nav className="page-nav"><Link className="active" href="/">实验室总览</Link><Link href="/experiments">实验列表</Link></nav><div className="top-actions"><button className="ghost" onClick={()=>setRunning(!running)}>{running?<Pause size={16}/>:<Play size={16}/>} {running?"暂停演示":"继续演示"}</button><button className="danger" onClick={injectFault}><AlertTriangle size={16}/> 注入异常</button></div></header>
  <section className="metrics environment-metrics" aria-label="实验室环境状态"><div><span>设备在线</span><strong>6 / 6</strong><small><Wifi size={13}/> SiLA 2 连接正常</small></div><div><span>温度 / 湿度</span><strong>22.4°C</strong><small><Activity size={13}/> 45% RH · 稳定</small></div><div><span>气压 / 空气</span><strong>101.2 kPa</strong><small><Activity size={13}/> PM2.5 3 μg/m³</small></div><div className="metric-alert"><span>活动告警</span><strong>1</strong><small><AlertTriangle size={13}/> 检测仪舱门</small></div></section>
  <section className="workspace"><div className="map-panel"><div className="panel-heading map-heading"><div><small className="eyebrow">LIVE DEVICE MAP</small><h1>实验室实时设备地图</h1><p>实验室 A · 6 台设备在线 · 数据延迟 180 ms</p></div><div className="legend"><span><i className="lg online"/>在线</span><span><i className="lg busy"/>运行</span><span><i className="lg alarm"/>异常</span></div></div>
   <div className="lab-map"><div ref={mapViewport} className={`map-stage ${dragging?"is-panning":""} ${zoom<=.8?"compact-devices":""}`} onPointerDown={startPan} onPointerMove={movePan} onPointerUp={endPan} onPointerCancel={endPan} onLostPointerCapture={endPan} style={{backgroundSize:`${28*zoom}px ${28*zoom}px`,backgroundPosition:`calc(50% + ${pan.x}px) calc(50% + ${pan.y}px)`}} onWheel={e=>setZoom(z=>Math.min(1.5,Math.max(.7,+(z+(e.deltaY<0?.1:-.1)).toFixed(1))))}><svg style={{transform:`translate(${pan.x}px, ${pan.y}px) scale(${zoom})`}} viewBox="0 0 900 510" role="img" aria-label="实验室布局图"><defs>{(["done","current","upcoming"] as const).map(status=><marker key={status} id={`handoff-${status}`} viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto" markerUnits="userSpaceOnUse"><path d="M1 1L9 5L1 9" fill="none" stroke={{done:"#47c997",current:"#59d8e6",upcoming:"#e8b76a"}[status]} strokeWidth="2"/></marker>)}</defs><path d="M126 260H725" className="robot-path"/><path d="M450 180V222M450 298V340" className="robot-path faint"/>{route.slice(1).map((node,i)=><path key={`${selectedExperiment}-${i}`} d={selectedExperiment==="EXP-2026-014"&&i===1?`M248 390 H290 V290 H${robotX*8.3} V288`:selectedExperiment==="EXP-2026-014"&&i===2?`M${robotX*8.3+27} 260 H780 V202.5`:transferPaths[selectedExperiment!][i]} markerEnd={`url(#handoff-${experimentTransfers[selectedExperiment!][i]})`} className={`route-line ${experimentTransfers[selectedExperiment!][i]}`}><title>{`${devices.find(d=>d.id===route[i].deviceId)?.name} → ${devices.find(d=>d.id===node.deviceId)?.name} · ${transferLabels[experimentTransfers[selectedExperiment!][i]]}`}</title></path>)}
   {([{device:devices[1],x:55,y:78,width:220,height:135},{device:devices[2],x:625,y:72,width:220,height:145},{device:devices[4],x:350,y:62,width:200,height:118},{device:devices[3],x:50,y:330,width:220,height:120},{device:devices[5],x:350,y:340,width:200,height:110}]).map(({device,x,y,width,height})=>{
 const workload=device.workloads[0];
 const task=device.action;
 const sample=workload?.sample??"—";
 return <g key={device.id} className={`station route-device ${device.state==="异常"?"alarm-station":""} ${routeStatus(device.id)??"dimmed"}`} onClick={()=>inspectDevice(device)}>
  <rect x={x} y={y} width={width} height={height} rx="14"/>
  <text x={zoom<=.8?x+width/2:x+16} y={zoom<=.8?y+height/2-9:y+25} textAnchor={zoom<=.8?"middle":undefined} className="map-device-name">{zoom<=.8?device.name.replace(/ 01$/,""):device.name}</text>
  <text x={zoom<=.8?x+width/2:x+16} y={zoom<=.8?y+height/2+21:y+43} textAnchor={zoom<=.8?"middle":undefined} className="machine-label">{zoom<=.8?device.state:`${device.id} · ${device.state}`}</text>
  <circle cx={x+width-18} cy={y+21} r="4" className={device.state==="异常"?"dot-alarm":device.state==="运行中"?"dot-running":"dot-idle"}/>
  <text x={x+16} y={y+64} className="map-device-field">任务 · {task.length>19?`${task.slice(0,18)}…`:task}</text>
  <text x={x+16} y={y+81} className="map-device-field">样品 · {sample}{device.workloads.length>1?` 等 ${device.workloads.length} 个`:""}</text>
  <text x={x+16} y={y+98} className="map-device-field">占用 · {device.workloads.length} / {device.capacity} · {device.mode}</text>
 </g>
 })}
   <g className="station route-device dimmed"><rect x="625" y="330" width="220" height="120" rx="14"/><text x={zoom<=.8?735:641} y={zoom<=.8?381:355} textAnchor={zoom<=.8?"middle":undefined} className="map-device-name">机器人充电设备</text><text x={zoom<=.8?735:641} y={zoom<=.8?411:373} textAnchor={zoom<=.8?"middle":undefined} className="machine-label">{zoom<=.8?"空闲":"dock-01 · 空闲"}</text><text x="641" y="394" className="map-device-field">任务 · 等待充电对接</text><text x="641" y="411" className="map-device-field">样品 · —</text><text x="641" y="428" className="map-device-field">占用 · 0 / 1 · 独占</text><circle cx="827" cy="351" r="4" className="dot-idle"/></g>
   <g className={`robot route-robot ${routeStatus("robot-01")??"dimmed"}`} transform={`translate(${robotX*8.3},260)`} onClick={()=>inspectDevice(devices[0])}><title>移动机器人 01 · 孔板搬运</title><ellipse className="robot-shadow" cy="5" rx="29" ry="23"/><rect className="robot-wheel" x="-27" y="-16" width="7" height="13" rx="3"/><rect className="robot-wheel" x="-27" y="6" width="7" height="13" rx="3"/><rect className="robot-wheel" x="20" y="-16" width="7" height="13" rx="3"/><rect className="robot-wheel" x="20" y="6" width="7" height="13" rx="3"/><rect className="robot-body" x="-22" y="-25" width="44" height="50" rx="11"/><path className="robot-bumper" d="M-12-19H12"/><rect className="robot-deck" x="-15" y="-11" width="30" height="25" rx="5"/><rect className="robot-payload" x="-10" y="-7" width="20" height="15" rx="2"/>{[-6,0,6].map(x=>[-3,3].map(y=><circle key={`${x}-${y}`} className="robot-well" cx={x} cy={y} r="1.4"/>))}<path className="robot-direction" d="M-4 20L0 17L4 20"/><circle className="robot-status" cx="16" cy="-18" r="2"/><text x="0" y="48" textAnchor="middle">Robot 01</text></g>{route.filter(node=>node.status==="current").map(node=>{
 const bounds:Record<string,[number,number,number,number]>={"liquid-01":[55,78,220,135],"reader-01":[625,72,220,145],"incubator-01":[50,330,220,120],"centrifuge-01":[350,62,200,118],"imager-01":[350,340,200,110],"robot-01":[robotX*8.3-25,232,50,56]};
 const [x,y,width,height]=bounds[node.deviceId];
 return <g key={node.deviceId} className="device-execution-effect" transform={node.deviceId==="robot-01"?undefined:`translate(${x+width/2},${y+height/2}) scale(.8) translate(${-x-width/2},${-y-height/2})`} aria-label="所选实验任务执行中"><rect className="execution-halo" x={x-4} y={y-4} width={width+8} height={height+8} rx="17"/><rect className="execution-tracer" x={x} y={y} width={width} height={height} rx="14" pathLength="100"/><g transform={`translate(${x+width/2-38},${y+height+22})`}><circle className="execution-dot" r="3"/><text x="9" dy="3">本实验执行中</text></g></g>
 })}{route.map((node,index)=><g key={node.deviceId} className={`route-sequence ${node.status}`} transform={`translate(${node.point[0]},${node.deviceId==="robot-01"?node.point[1]-40:({"liquid-01":75.5,"reader-01":70.5,"incubator-01":326,"centrifuge-01":56,"imager-01":333} as Record<string,number>)[node.deviceId]})`}><title>{`${devices.find(d=>d.id===node.deviceId)?.name} · ${node.status==="done"?"任务已完成":node.status==="current"?"任务执行中":"任务待执行"}`}</title><circle r="11"/><text textAnchor="middle" dy="4">{index+1}</text></g>)}</svg>{selectedExperiment&&<div className="route-summary"><b>{selectedExperiment}</b><button className="clear-experiment" onClick={()=>setSelectedExperiment(null)} aria-label="取消实验选择"><X size={12}/> 清除选择</button><div className="route-legend-row"><small>样品连线</small><span><i className="done"/>已交接</span><span><i className="current"/>传递中</span><span><i className="upcoming"/>待传递</span></div><div className="route-legend-row"><small>设备边框</small><span><i className="done"/>已完成</span><span><i className="current"/>执行中</span><span><i className="upcoming"/>待执行</span></div></div>}<div className="map-toast robot-device-summary"><Bot size={16}/><div><b>移动机器人 01</b><small>robot-01 · {running?"运行中":"已暂停"}</small><span>任务 · 孔板搬运</span><span>样品 · plate-001</span><span>占用 · 1 / 1 · 独占</span></div></div></div></div></div>
  </section>
  <div className="zoom-controls"><button onClick={()=>setZoom(z=>Math.max(.7,+(z-.1).toFixed(1)))} aria-label="缩小地图"><Minus size={16}/></button><button className="fit-view" onClick={()=>{setZoom(1);setPan({x:0,y:0})}} title="显示全部设备">适应视图</button><button className="zoom-value" onClick={()=>{setZoom(1);setPan({x:0,y:0})}} title="适应视图：恢复缩放并居中">{Math.round(zoom*100)}%</button><button onClick={()=>setZoom(z=>Math.min(1.5,+(z+.1).toFixed(1)))} aria-label="放大地图"><Plus size={16}/></button></div>
  <div className="floating-actions">
   <Sheet open={deviceOpen} onOpenChange={setDeviceOpen}><SheetTrigger asChild><button onClick={()=>setDeviceView("list")}><Server size={17}/><span>设备</span><b>6</b></button></SheetTrigger><SheetContent className="twin-sheet"><SheetHeader><SheetTitle>{deviceView==="list"?"设备列表":selected.name}</SheetTitle><SheetDescription>{deviceView==="list"?"选择设备查看能力、支持的动作与实验占用":`${selected.type} · 设备状态与能力`}</SheetDescription></SheetHeader>{deviceView==="list"?<div className="device-list">{devices.map(d=><button key={d.id} className={`device-card ${selected.id===d.id?"selected":""}`} onClick={()=>inspectDevice(d)}><div className="device-title"><span className="device-icon">{d.id.startsWith("robot")?<Bot/>:d.id.startsWith("liquid")?<TestTube2/>:<Gauge/>}</span><div><b>{d.name}</b><small>{d.type}</small></div><Status state={d.state}/></div><p>{d.action}</p><div className="device-capability-count">{deviceCapabilities[d.id].name} · {deviceCapabilities[d.id].actions.length} 个动作</div><div className="capacity-line"><span>{d.mode}</span><b>{d.workloads.length} / {d.capacity} 占用</b></div>{d.progress>0&&<div className="progress"><span style={{width:`${d.progress}%`}}/></div>}</button>)}</div>:<div className="detail-card"><button className="device-back" onClick={()=>setDeviceView("list")}>← 全部设备</button><div className="detail-head"><div><small>当前选择</small><h3>{selected.name}</h3></div><Status state={selected.state}/></div><p>{selected.detail}</p><dl><div><dt>并发模式</dt><dd>{selected.mode}</dd></div><div><dt>资源占用</dt><dd>{selected.workloads.length} / {selected.capacity}</dd></div><div><dt>Feature</dt><dd>{selected.type}</dd></div></dl>{selected.state==="异常"&&<div className="recovery-note"><AlertTriangle size={16}/><div><b>等待设备侧恢复</b><span>设备人员现场处理 → 设备执行自检 → SiLA 2 上报正常状态 → 平台重新排程</span></div></div>}{selected.workloads.length>0&&<div className="workloads"><small>设备内运行实验</small>{selected.workloads.map(w=><div className="workload" key={`${w.experiment}-${w.slot}`}><div><b>{w.experiment}</b><span>{w.sample} · {w.slot}</span></div><em>{w.state} {w.progress}%</em></div>)}</div>}<DeviceCapabilities key={selected.id} deviceId={selected.id} state={selected.state}/></div>}</SheetContent></Sheet>
  </div>
  <Sheet><SheetTrigger asChild><button className="timeline-trigger"><ListTree size={17}/><span>实验与事件</span><b>{selectedExperiment?selectedExperiment.replace("EXP-2026-", "EXP-"):"选择实验"}</b></button></SheetTrigger><SheetContent side="bottom" className="operations-sheet"><SheetHeader><SheetTitle>实验运行中心</SheetTitle><SheetDescription>点击实验，在地图中查看所需设备、执行顺序和当前状态</SheetDescription></SheetHeader><section className="bottom-grid"><div className="run-panel"><div className="panel-heading"><div><h2>并行实验执行链</h2><p>3 个实验正在共享设备资源</p></div><span className="eta">选择实验查看路径</span></div><div className="experiment-runs">{experimentRuns.map(run=><SheetClose asChild key={run.id}><button className={`experiment-run ${selectedExperiment===run.id?"selected":""}`} onClick={()=>setSelectedExperiment(run.id as keyof typeof experimentRoutes)}><div className="run-identity"><b>{run.id}</b><span>{run.name}</span><small>{run.device} · ETA {run.eta}</small></div><div className="mini-steps">{run.steps.map((s,i)=><div key={s} className={`mini-step ${i<run.active?"done":i===run.active?"active":""}`} title={s}><i>{i<run.active?"✓":i+1}</i><span>{s}</span>{i<run.steps.length-1&&<b/>}</div>)}</div></button></SheetClose>)}</div></div><div className="event-panel"><div className="panel-heading"><div><h2>实时事件</h2><p>命令、状态与异常回流</p></div></div><div className="events">{events.map((e,i)=><div className={`event ${e[3]}`} key={`${e[0]}-${i}`}><time>{e[0]}</time><b>{e[1]}</b><span>{e[2]}</span></div>)}</div></div></section></SheetContent></Sheet>
 </main>
}
