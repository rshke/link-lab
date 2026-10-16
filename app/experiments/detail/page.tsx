"use client";
import { useEffect, useState } from "react";
import { AlertTriangle, ArrowLeft, CheckCircle2, Clock3, FlaskConical, Gauge, Microscope, TestTube2, Thermometer } from "lucide-react";

const records={
 "EXP-2026-014":{name:"板式稀释与吸光度检测",owner:"细胞分析组",sample:"plate-001 / plate-002",started:"14:08",eta:"14:38",progress:58,current:"恒温培养",parameters:["温度 37.0°C","培养 30 min","吸光度 450 nm"],devices:[{name:"液体处理设备",feature:"LiquidHandling",state:"已完成",detail:"完成 8 级梯度稀释",time:"14:21"},{name:"恒温培养设备",feature:"Incubation",state:"当前执行",detail:"槽位 A1 · 剩余 12 min",time:"14:26"},{name:"移动机器人 01",feature:"RobotControl",state:"后续计划",detail:"培养完成后搬运至检测设备",time:"预计 14:34"},{name:"微孔板检测仪",feature:"Measurement",state:"等待设备",detail:"设备异常，恢复后重新排程",time:"待定"}]},
 "EXP-2026-021":{name:"细胞活性筛选",owner:"药物筛选组",sample:"plate-017 / plate-018",started:"13:42",eta:"14:51",progress:46,current:"显微成像",parameters:["温度 37.0°C","GFP 通道","20× 物镜"],devices:[{name:"恒温培养设备",feature:"Incubation",state:"已完成",detail:"槽位 A2 · 培养完成",time:"14:25"},{name:"显微成像设备",feature:"Imaging",state:"当前执行",detail:"扫描视野 4 / 12",time:"14:31"},{name:"微孔板检测仪",feature:"Measurement",state:"后续计划",detail:"等待成像结果质检",time:"预计 14:44"}]},
 "EXP-2026-023":{name:"培养条件探索",owner:"工艺开发组",sample:"plate-022",started:"14:20",eta:"15:06",progress:19,current:"离心处理",parameters:["离心 1200 rpm","培养 35.5°C","明场成像"],devices:[{name:"液体处理设备",feature:"LiquidHandling",state:"已完成",detail:"培养基分装完成",time:"14:27"},{name:"离心设备",feature:"Centrifugation",state:"当前执行",detail:"批次 1 · 剩余 4 min",time:"14:32"},{name:"恒温培养设备",feature:"Incubation",state:"后续计划",detail:"已预留槽位 B1",time:"预计 14:38"},{name:"显微成像设备",feature:"Imaging",state:"后续计划",detail:"等待培养完成",time:"预计 14:58"}]},
 "EXP-2026-009":{name:"微孔板终点检测",owner:"分析检测组",sample:"plate-009",started:"13:18",eta:"等待设备恢复",progress:38,current:"异常暂停",parameters:["吸光度 600 nm","重复测量 3 次"],devices:[{name:"移动机器人 01",feature:"RobotControl",state:"已完成",detail:"样品已送达检测设备",time:"13:29"},{name:"微孔板检测仪",feature:"Measurement",state:"设备异常",detail:"舱门未关闭；等待现场处理和设备自检",time:"13:31"}]}
};
type Experiment=typeof records[keyof typeof records];
function icon(feature:string){return feature==="Incubation"?<Thermometer/>:feature==="Imaging"?<Microscope/>:feature==="LiquidHandling"?<TestTube2/>:<Gauge/>}
export default function ExperimentDetailPage(){
 const[record,setRecord]=useState<Experiment>(records["EXP-2026-014"]);const[id,setId]=useState("EXP-2026-014");
 useEffect(()=>{const value=new URLSearchParams(window.location.search).get("experiment")||"EXP-2026-014";if(value in records){setId(value);setRecord(records[value as keyof typeof records])}},[]);
 return <main className="subpage detail-page"><header className="subpage-header"><div className="brand"><span className="brand-mark"><FlaskConical size={19}/></span><div><strong>LabFlow Twin</strong><small>实验详情</small></div></div><nav className="page-nav"><a href="/">实验室总览</a><a className="active" href="/experiments">实验列表</a></nav><div className="header-health"><span className="live-dot"/>实验室 A 在线</div></header>
 <a className="back-link" href="/experiments"><ArrowLeft size={16}/>返回实验列表</a>
 <section className="detail-hero"><div><span className="state-pill 运行中"><ActivityIcon/> {record.current}</span><small>{id}</small><h1>{record.name}</h1><p>{record.sample} · {record.owner}</p></div><div className="detail-progress"><b>{record.progress}%</b><span>整体进度</span><div><i style={{width:`${record.progress}%`}}/></div></div></section>
 <section className="detail-meta"><div><span>开始时间</span><b>{record.started}</b></div><div><span>预计完成</span><b>{record.eta}</b></div><div><span>当前步骤</span><b>{record.current}</b></div><div><span>实验参数</span><b>{record.parameters.join(" · ")}</b></div></section>
 <section className="related-devices"><div className="section-title"><div><small>RELATED DEVICES</small><h2>本实验关联设备</h2></div><p>仅展示本实验占用或计划使用的设备，以及与本实验相关的状态。</p></div><div className="related-device-grid">{record.devices.map((device,index)=><article className={`related-device ${device.state}`} key={device.name}><div className="device-sequence">{index+1}</div><div className="related-icon">{icon(device.feature)}</div><div><small>{device.feature}</small><h3>{device.name}</h3><p>{device.detail}</p><time><Clock3 size={13}/>{device.time}</time></div><span className="device-exp-state">{device.state==="设备异常"?<AlertTriangle size={14}/>:device.state==="已完成"?<CheckCircle2 size={14}/>:null}{device.state}</span></article>)}</div></section>
 </main>
}
function ActivityIcon(){return <span className="detail-live-dot"/>}
