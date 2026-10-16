import { Activity, AlertTriangle, ArrowRight, CheckCircle2, Clock3, FlaskConical } from "lucide-react";

const experiments=[
 {id:"EXP-2026-014",name:"板式稀释与吸光度检测",status:"运行中",progress:58,owner:"细胞分析组",started:"14:08",eta:"14:38",current:"恒温培养",sample:"plate-001 / plate-002",devices:4,alert:false},
 {id:"EXP-2026-021",name:"细胞活性筛选",status:"运行中",progress:46,owner:"药物筛选组",started:"13:42",eta:"14:51",current:"显微成像",sample:"plate-017 / plate-018",devices:3,alert:false},
 {id:"EXP-2026-023",name:"培养条件探索",status:"运行中",progress:19,owner:"工艺开发组",started:"14:20",eta:"15:06",current:"离心处理",sample:"plate-022",devices:4,alert:false},
 {id:"EXP-2026-009",name:"微孔板终点检测",status:"异常暂停",progress:38,owner:"分析检测组",started:"13:18",eta:"等待设备恢复",current:"检测设备异常",sample:"plate-009",devices:2,alert:true},
 {id:"EXP-2026-008",name:"缓冲液梯度验证",status:"已完成",progress:100,owner:"方法开发组",started:"11:32",eta:"12:26 完成",current:"结果已归档",sample:"plate-006",devices:3,alert:false}
];

export default function ExperimentsPage(){
 return <main className="subpage">
  <header className="subpage-header"><div className="brand"><span className="brand-mark"><FlaskConical size={19}/></span><div><strong>LabFlow Twin</strong><small>实验管理</small></div></div><nav className="page-nav"><a href="/">实验室总览</a><a className="active" href="/experiments">实验列表</a></nav><div className="header-health"><span className="live-dot"/>实验室 A 在线</div></header>
  <section className="page-intro"><div><small>EXPERIMENTS</small><h1>实验列表</h1><p>查看当前运行、异常暂停与近期完成的实验。</p></div><div className="experiment-stats"><div><span>运行中</span><b>3</b></div><div><span>异常暂停</span><b className="danger-text">1</b></div><div><span>今日完成</span><b>7</b></div></div></section>
  <section className="experiment-table"><div className="table-head"><span>实验</span><span>当前状态</span><span>负责人</span><span>设备</span><span>时间</span><span/></div>{experiments.map(exp=><a className={`experiment-row ${exp.alert?"has-alert":""}`} href={`/experiments/detail?experiment=${exp.id}`} key={exp.id}><div className="experiment-main"><b>{exp.id}</b><span>{exp.name}</span><small>{exp.sample}</small></div><div className="experiment-state"><span className={`state-pill ${exp.status}`}>{exp.alert?<AlertTriangle size={13}/>:exp.progress===100?<CheckCircle2 size={13}/>:<Activity size={13}/>} {exp.status}</span><small>{exp.current}</small><div className="list-progress"><i style={{width:`${exp.progress}%`}}/></div></div><div><b>{exp.owner}</b><small>任务负责人</small></div><div><b>{exp.devices} 台</b><small>关联设备</small></div><div><b><Clock3 size={13}/>{exp.eta}</b><small>开始 {exp.started}</small></div><ArrowRight size={18}/></a>)}</section>
 </main>
}
