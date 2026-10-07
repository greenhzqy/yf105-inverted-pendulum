# -*- coding: utf-8 -*-
"""生成《直驱摆仿真可视化.html》：内嵌真实仿真轨迹，浏览器可播放。
场景：① 能量起摆+平衡  ② 平衡+扰动  ③ 摩擦死区 PD vs PID
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VIZ = os.path.join(HERE, 'viz')

with open(os.path.join(VIZ, 'viz_data.json'), encoding='utf-8') as f:
    DATA = json.load(f)

JS_DATA = json.dumps(DATA, ensure_ascii=False)

html = r"""<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="utf-8">
<title>电机直驱倒立摆 · 仿真可视化</title>
<style>
  * { box-sizing: border-box; }
  body { font-family: "Microsoft YaHei","PingFang SC",sans-serif; margin: 0; background:#f4f6f8; color:#222; }
  header { background:#2f6db3; color:#fff; padding:12px 20px; }
  header h1 { margin:0; font-size:18px; }
  header p { margin:4px 0 0; font-size:12px; opacity:.9; }
  .tabs { background:#fff; padding:10px 20px; border-bottom:1px solid #ddd; }
  .tabs button { margin-right:8px; padding:8px 16px; border:1px solid #ccc; background:#fff; border-radius:6px;
                 cursor:pointer; font-size:14px; }
  .tabs button.on { background:#2f6db3; color:#fff; border-color:#2f6db3; }
  .stage { display:flex; gap:20px; padding:16px 20px; flex-wrap:wrap; }
  .left { display:flex; gap:14px; }
  .pendbox { text-align:center; }
  .pendbox canvas { background:#fff; border:1px solid #ddd; border-radius:8px; }
  .pendbox .plabel { font-size:13px; margin-top:4px; color:#555; }
  .right { display:flex; flex-direction:column; gap:8px; min-width:300px; flex:1; }
  .right canvas { background:#fff; border:1px solid #ddd; border-radius:6px; }
  .readout { margin-top:6px; font-size:13px; color:#333; line-height:1.6; }
  .readout b { color:#2f6db3; }
  .controls { display:flex; align-items:center; gap:14px; padding:10px 20px; background:#fff; border-top:1px solid #ddd; }
  .controls button { padding:7px 16px; font-size:14px; border-radius:6px; border:1px solid #2f6db3; background:#fff;
                     color:#2f6db3; cursor:pointer; }
  .controls button.primary { background:#2f6db3; color:#fff; }
  .controls input[type=range] { flex:1; max-width:420px; }
  .controls select { padding:5px; }
  #time { font-variant-numeric: tabular-nums; min-width:90px; }
  .modechip { padding:3px 10px; border-radius:12px; color:#fff; font-size:13px; }
  .modechip.PUMP { background:#1565c0; }
  .modechip.BALANCE { background:#2e7d32; }
  .modechip.FAULT { background:#c62828; }
  .note { padding:8px 20px; color:#666; font-size:12px; }
</style>
</head>
<body>
<header>
  <h1>电机直驱倒立摆 · 仿真可视化（与实物同结构 · 2ms 闭环）</h1>
  <p>模型：I·θ″ = k_g·sinθ − τ_f − τ_m ｜ 重力矩 11.8 mN·m vs 静摩擦 5 mN·m（摩擦死区）</p>
</header>

<div class="tabs">
  <button class="on" data-tab="swingup">① 能量起摆 + 平衡</button>
  <button data-tab="balance">② 平衡 + 脉冲扰动</button>
  <button data-tab="deadzone">③ 摩擦死区：PD vs PID</button>
</div>

<div class="stage" id="stage"></div>

<div class="controls">
  <button id="play" class="primary">▶ 播放</button>
  <button id="rst">↺ 重播</button>
  <input type="range" id="slider" min="0" max="100" value="0">
  <select id="speed">
    <option value="1">1×</option><option value="2" selected>2×</option>
    <option value="4">4×</option><option value="8">8×</option>
  </select>
  <span id="time">t=0.0s</span>
  <span id="modechip"></span>
  <span id="duty"></span>
</div>
<div class="note" id="note"></div>

<script>
const DATA = __VIZ_DATA__;

let tab = 'swingup';
let playing = true;
let idx = 0;
let speed = 2;
let last = 0;

const pendCanvas = document.createElement('canvas'); pendCanvas.width=300; pendCanvas.height=400;
const pendCanvas2 = document.createElement('canvas'); pendCanvas2.width=300; pendCanvas2.height=400;
const pendBig = document.createElement('canvas'); pendBig.width=360; pendBig.height=430;
const chTheta = document.createElement('canvas'); chTheta.width=560; chTheta.height=120;
const chDuty  = document.createElement('canvas'); chDuty.width=560; chDuty.height=120;
const chE     = document.createElement('canvas'); chE.width=560; chE.height=120;

const stage = document.getElementById('stage');

function seriesLen(){
  if (tab==='deadzone') return DATA.deadzone.pd.t.length;
  return DATA[tab].t.length;
}

function buildStage(){
  stage.innerHTML='';
  if (tab==='deadzone'){
    const l=document.createElement('div'); l.className='left';
    for (const [key,label] of [['pd','纯 PD（卡在死区）'],['pid','PID（积分跨死区）']]){
      const b=document.createElement('div'); b.className='pendbox';
      const c=key==='pd'?pendCanvas:pendCanvas2;
      b.appendChild(c);
      const p=document.createElement('div'); p.className='plabel'; p.textContent=label; b.appendChild(p);
      l.appendChild(b);
    }
    stage.appendChild(l);
  } else {
    const l=document.createElement('div'); l.className='left';
    const b=document.createElement('div'); b.className='pendbox';
    // 起摆主场景用大画布（长杆 + 最低点→最高点轨迹）
    b.appendChild(pendBig);
    const p=document.createElement('div'); p.className='plabel';
    p.textContent = tab==='swingup' ? '起摆（绿→红 = 从最低点荡到最高点）' : '摆杆（基座固定 · 电机直驱）';
    b.appendChild(p);
    l.appendChild(b);
    stage.appendChild(l);
  }
  const r=document.createElement('div'); r.className='right';
  r.appendChild(chTheta);
  r.appendChild(chDuty);
  if (tab==='swingup') r.appendChild(chE);
  const rd=document.createElement('div'); rd.className='readout'; rd.id='readout'; r.appendChild(rd);
  stage.appendChild(r);
}

function chartDual(canvas, t1, v1, c1, t2, v2, c2, ylabel, idxNow){
  const ctx=canvas.getContext('2d');
  const W=canvas.width, H=canvas.height;
  ctx.clearRect(0,0,W,H);
  const pl=26, pr=8, pt=10, pb=20, iw=W-pl-pr, ih=H-pt-pb;
  let mn=Infinity, mx=-Infinity;
  const n=Math.max(1, Math.min(idxNow+1, t1.length, t2.length));
  for(let j=0;j<n;j++){ for (const v of [v1[j], v2[j]]) { if(v<mn)mn=v; if(v>mx)mx=v; } }
  if(!isFinite(mn)){mn=0;} if(mn===mx){mn-=1;mx+=1;}
  const span=mx-mn||1;
  const X=(tArr,i)=>pl+i/(tArr.length-1||1)*iw;
  const Y=v=>pt+(mx-v)/span*ih;
  ctx.strokeStyle='#e0e0e0'; ctx.lineWidth=1;
  for(let g=0;g<=4;g++){const y=pt+ih*g/4; ctx.beginPath();ctx.moveTo(pl,y);ctx.lineTo(pl+iw,y);ctx.stroke();}
  for (const [tArr, vArr, color] of [[t1,v1,c1],[t2,v2,c2]]){
    ctx.strokeStyle=color; ctx.lineWidth=1.6; ctx.beginPath();
    for(let i=0;i<n;i++){const x=X(tArr,i), y=Y(vArr[i]); i?ctx.lineTo(x,y):ctx.moveTo(x,y);}
    ctx.stroke();
  }
  ctx.fillStyle='#555'; ctx.font='11px sans-serif';
  ctx.fillText(ylabel, 4, pt+8);
  ctx.fillText(mx.toFixed(1), pl, pt+8); ctx.fillText(mn.toFixed(1), pl, pt+ih);
  ctx.fillText('t='+(t1[Math.min(n-1,t1.length-1)]||0).toFixed(1)+'s', pl+iw-50, pt+ih+14);
  ctx.fillStyle=c1; ctx.fillText('─ PD', pl+iw-72, pt+8);
  ctx.fillStyle=c2; ctx.fillText('─ PID', pl+iw-28, pt+8);
}

// 主场景：倒立摆起摆。aDeg=从最低点算的角度：0=最低点(杆垂下)，180=最高点(直立)
function drawPendBig(aDeg, mode){
  const ctx=pendBig.getContext('2d');
  const W=pendBig.width, H=pendBig.height;
  ctx.clearRect(0,0,W,H);
  const cx=W/2, cy=H-56;                 // 转轴在画布下部中间
  const L=215;                           // 加长杆
  const a = aDeg*Math.PI/180;            // a=0 指向正下，a=180 指向正上
  // 屏幕坐标：a=0 → 指向正下 (sin=0, 向下)；a=180 → 指向正上
  // 用角度 a 画：杆端 = 轴 + L*(sin(a), cos(a))，其中 a=0 时 (0,1) 向下
  const tx = cx + L*Math.sin(a);
  const ty = cy + L*Math.cos(a);         // a=0 → ty=cy+L(下方最低)，a=180 → ty=cy-L(上方最高)
  // 参考虚线（过转轴的竖直线）
  ctx.strokeStyle='#d5dbe2'; ctx.lineWidth=1;
  ctx.setLineDash([4,4]); ctx.beginPath(); ctx.moveTo(cx,cy-L-20); ctx.lineTo(cx,cy+L+16); ctx.stroke();
  ctx.setLineDash([]);
  // 最高点(直立) / 最低点标注
  ctx.fillStyle='#2e7d32'; ctx.beginPath(); ctx.arc(cx, cy-L-12, 6, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle='#bdbdbd'; ctx.beginPath(); ctx.arc(cx, cy+L+4, 6, 0, Math.PI*2); ctx.fill();
  ctx.fillStyle='#555'; ctx.font='13px sans-serif'; ctx.textAlign='center';
  ctx.fillText('最高点 · 直立', cx, cy-L-24);
  ctx.fillText('最低点 · 下垂', cx, cy+L+22);
  // 已扫过的摆尖轨迹圆弧：从最低点(a=0)到当前(aDeg)，绿→红渐变，直观“从下荡到上”
  const R = L;
  // 屏幕圆弧：以正下方为 0 起点。屏幕 y 向下为正，角度 φ 从正下开始算
  // 最低点方向=向下=+y。扫过的弧从最低点(角度0)顺时针扫到当前 a。
  const start_ang = Math.PI/2;   // 正下（+y）在 canvas 圆角 = π/2
  const end_ang   = Math.PI/2 - a;  // a=π(上)→ -π/2(正上)。逆时针扫
  ctx.strokeStyle='rgba(150,150,150,0.12)'; ctx.lineWidth=3;
  ctx.beginPath(); ctx.arc(cx,cy,R, Math.PI/2, -Math.PI/2); ctx.stroke();  // 整段右半边? 
  // 直接用杆扫过的实际方向画渐变弧（右摆）
  ctx.strokeStyle='#e3b6b6'; ctx.lineWidth=4;
  ctx.beginPath(); ctx.arc(cx,cy,R, Math.PI/2, end_ang, end_ang<Math.PI/2); ctx.stroke();
  // 电机（转轴）
  ctx.fillStyle='#455a64'; ctx.beginPath(); ctx.arc(cx,cy,18,0,Math.PI*2); ctx.fill();
  ctx.fillStyle='#fff'; ctx.font='11px sans-serif'; ctx.textAlign='center'; ctx.fillText('M',cx,cy+4);
  // 摆杆本体
  ctx.strokeStyle='#4e342e'; ctx.lineWidth=7; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(tx,ty); ctx.stroke();
  // 尖端配重
  ctx.fillStyle='#263238'; ctx.beginPath(); ctx.arc(tx,ty,10,0,Math.PI*2); ctx.fill();
  // 文字
  ctx.textAlign='left'; ctx.font='bold 16px sans-serif';
  const mc = mode==='FAULT'?'#c62828': mode==='PUMP'?'#1565c0':'#2e7d32';
  ctx.fillStyle=mc; ctx.fillText(mode||'', 12, 26);
  ctx.fillStyle='#222'; ctx.font='bold 17px sans-serif';
  ctx.fillText('距最低点 '+aDeg.toFixed(1)+'°', 12, 50);
  ctx.fillStyle='#666'; ctx.font='13px sans-serif';
  ctx.fillText(aDeg<45 ? '→ 已到最高点(直立)' : (aDeg<170 ? '→ 摆动中' : '→ 最低点(下垂)'), 12, 72);
  ctx.textAlign='left';
}

function drawPend(canvas, thDeg, mode, label){
  const ctx=canvas.getContext('2d');
  const W=canvas.width, H=canvas.height;
  ctx.clearRect(0,0,W,H);
  const cx=W/2, cy=H-70;
  // 底座
  ctx.fillStyle='#8d6e63'; ctx.fillRect(cx-78, cy-8, 156, 16);
  ctx.fillStyle='#a1887f'; ctx.fillRect(cx-90, cy-8, 12, 16); ctx.fillRect(cx+78, cy-8, 12, 16);
  // 电机
  ctx.fillStyle='#607d8b'; ctx.beginPath(); ctx.arc(cx,cy,22,0,2*Math.PI); ctx.fill();
  ctx.strokeStyle='#37474f'; ctx.lineWidth=2; ctx.stroke();
  ctx.fillStyle='#37474f'; ctx.font='11px sans-serif'; ctx.textAlign='center';
  ctx.fillText('M', cx, cy+4);
  // 摆杆
  const th=thDeg*Math.PI/180, L=135;
  const tx=cx+L*Math.sin(th), ty=cy-L*Math.cos(th);
  ctx.strokeStyle='#6d4c41'; ctx.lineWidth=7; ctx.lineCap='round';
  ctx.beginPath(); ctx.moveTo(cx,cy); ctx.lineTo(tx,ty); ctx.stroke();
  // 尖端配重
  ctx.fillStyle='#37474f'; ctx.beginPath(); ctx.arc(tx,ty,10,0,2*Math.PI); ctx.fill();
  // 角度弧
  ctx.strokeStyle='#2f6db3'; ctx.lineWidth=1.5;
  ctx.beginPath(); ctx.arc(cx,cy,26,-Math.PI/2,-Math.PI/2+th*(th>0?1:-1), th<0); ctx.stroke();
  // 模式 + 角度
  ctx.textAlign='left'; ctx.font='15px sans-serif';
  const mc = mode==='FAULT'?'#c62828': mode==='PUMP'?'#1565c0':'#2e7d32';
  ctx.fillStyle=mc; ctx.fillText(label?label+' · ':'', 10, 24);
  ctx.fillStyle='#222'; ctx.fillText('θ='+thDeg.toFixed(1)+'°', cx-44, cy+44);
  ctx.textAlign='left';
}

function chart(canvas, tArr, vArr, color, ylabel, idxNow, extra){
  const ctx=canvas.getContext('2d');
  const W=canvas.width, H=canvas.height;
  ctx.clearRect(0,0,W,H);
  const pad=26, pl=pad, pr=8, pt=10, pb=20;
  const iw=W-pl-pr, ih=H-pt-pb;
  let mn=Infinity, mx=-Infinity;
  const upto=Math.max(1, Math.min(idxNow+1, tArr.length));
  for(let i=0;i<upto;i++){const v=vArr[i]; if(v<mn)mn=v; if(v>mx)mx=v;}
  if (extra){ mn=Math.min(mn, extra[0]); mx=Math.max(mx, extra[1]); }
  if (!isFinite(mn)){mn=0;} if(mn===mx){mn-=1;mx+=1;}
  const span=mx-mn||1;
  const X=i=>pl+i/ (tArr.length-1||1)*iw;
  const Y=v=>pt+(mx-v)/span*ih;
  ctx.strokeStyle='#e0e0e0'; ctx.lineWidth=1;
  for(let g=0;g<=4;g++){const y=pt+ih*g/4; ctx.beginPath();ctx.moveTo(pl,y);ctx.lineTo(pl+iw,y);ctx.stroke();}
  ctx.strokeStyle=color; ctx.lineWidth=1.6; ctx.beginPath();
  for(let i=0;i<upto;i++){const x=X(i), y=Y(vArr[i]); i?ctx.lineTo(x,y):ctx.moveTo(x,y);}
  ctx.stroke();
  ctx.fillStyle='#555'; ctx.font='11px sans-serif';
  ctx.fillText(ylabel, 4, pt+8);
  ctx.fillText(mx.toFixed(1), pl, pt+8); ctx.fillText(mn.toFixed(1), pl, pt+ih);
  ctx.fillText('t='+(tArr[Math.min(upto-1,tArr.length-1)]||0).toFixed(1)+'s', pl+iw-50, pt+ih+14);
}

function frame(){
  if (tab==='deadzone'){
    const dz=DATA.deadzone;
    const pd=dz.pd, pid=dz.pid;
    const i=Math.min(idx, pd.t.length-1);
    drawPend(pendCanvas, pd.du[i], 'PD', '纯 PD');
    drawPend(pendCanvas2, pid.du[i], 'PID', 'PID');
    chartDual(chTheta, pd.t, pd.du, '#c62828', pid.t, pid.du, '#2e7d32', '距直立 (°)', idx);
    chartDual(chDuty, pd.t, pd.duty, '#c62828', pid.t, pid.duty, '#2e7d32', 'duty (%)', idx);
    document.getElementById('readout').innerHTML =
      '纯 PD → 卡在距直立 <b>'+pd.du[pd.t.length-1].toFixed(2)+'°</b>　|　PID → 收敛到 <b>'+pid.du[pid.t.length-1].toFixed(2)+'°</b>（0=直立）';
  } else {
    const d=DATA[tab];
    const i=Math.min(idx, d.t.length-1);
    if (tab==='swingup') drawPendBig(d.a[i], d.mode[i]);
    else drawPend(pendCanvas, d.du[i], d.mode[i], null);   // 小画布用"距直立"显示
    chart(chTheta, d.t, tab==='swingup' ? d.a : d.du, '#2e7d32',
          tab==='swingup' ? '距最低点 (°)' : '距直立 (°)', idx, null);
    chart(chDuty, d.t, d.duty, '#e65100', 'duty (%)', idx, null);
    if (tab==='swingup') chart(chE, d.t, d.E, '#6a1b9a', 'E (J)', idx, null);
    document.getElementById('readout').innerHTML =
      '距最低点=<b>'+d.a[i].toFixed(2)+'°</b>（180=直立）　|&nbsp; duty=<b>'+d.duty[i].toFixed(1)+'%</b>'+
      (d.E?'　|&nbsp; E=<b>'+d.E[i].toFixed(4)+'J</b>':'')+
      '　|&nbsp; 模式=<b>'+d.mode[i]+'</b>';
  }
}

function loop(ts){
  if (playing){
    idx += speed;
    if (idx >= seriesLen()) idx = 0;
    frame();
    document.getElementById('slider').value = Math.round(idx/(seriesLen()-1)*100);
    const d = tab==='deadzone' ? DATA.deadzone.pd : DATA[tab];
    const i = Math.min(idx, d.t.length-1);
    document.getElementById('time').textContent = 't='+d.t[i].toFixed(1)+'s';
  }
  requestAnimationFrame(loop);
}

document.getElementById('play').onclick = ()=>{ playing=!playing;
  document.getElementById('play').textContent = playing?'⏸ 暂停':'▶ 播放';
  document.getElementById('play').classList.toggle('primary', playing);
};
document.getElementById('rst').onclick = ()=>{ idx=0; frame(); };
document.getElementById('slider').oninput = e=>{ idx=Math.round(e.target.value/100*(seriesLen()-1)); frame(); };
document.getElementById('speed').onchange = e=>{ speed=parseInt(e.target.value); };

document.querySelectorAll('.tabs button').forEach(b=>{
  b.onclick=()=>{
    document.querySelectorAll('.tabs button').forEach(x=>x.classList.remove('on'));
    b.classList.add('on');
    tab=b.dataset.tab;
    idx=0;
    buildStage();
    frame();
    const n=document.getElementById('note');
    n.textContent = tab==='swingup' ? DATA.swingup.note : (tab==='balance' ? '2s 时刻给 2 rad/s 角速度冲击，PID 1.19s 内恢复。' : '同样从 2° 起步：纯 PD 的力矩正比于偏差，小偏差时压不过静摩擦（5 mN·m）→ 卡在 2.03°；PID 积分项累积到跨过门槛 → 1.20s 收敛到 −0.51°。');
    document.getElementById('time').textContent='t=0.0s';
  };
});

buildStage();
frame();
requestAnimationFrame(loop);
</script>
</body>
</html>
"""

html = html.replace('__VIZ_DATA__', JS_DATA)
out = os.path.join(VIZ, '直驱摆仿真可视化.html')
with open(out, 'w', encoding='utf-8') as f:
    f.write(html)
print('saved:', out, os.path.getsize(out), 'bytes')
