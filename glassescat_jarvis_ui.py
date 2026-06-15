#!/usr/bin/env python3
"""
GlassesCat JARVIS — Windows Desktop App | Iron Man Green Theme
"""

import os, re, json, time, threading, urllib.request, subprocess, tempfile
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
OLLAMA_MODEL = "glassesglitchstudio/gulmzcetiner:Ultra_Agent"
WAKE_WORD = "glassescat"
SAMPLE_RATE = 16000
PORT = 5052
voice_engine = None
brain_engine = None

# ============ HTML UI ============
HTML = r"""<!DOCTYPE html>
<html lang="tr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,user-scalable=no">
<title>JARVIS — GlassesCat</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:100%;height:100%;overflow:hidden;background:#0a0a0a;color:#00ff41;font-family:'Share Tech Mono',monospace;user-select:none}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;
background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,255,65,0.015) 2px,rgba(0,255,65,0.015) 4px);
pointer-events:none;z-index:999}
body::after{content:'';position:fixed;top:0;left:0;width:100%;height:100%;
background:radial-gradient(ellipse at center,transparent 60%,rgba(0,0,0,0.7) 100%);
pointer-events:none;z-index:998}
#bgCanvas{position:fixed;top:0;left:0;width:100%;height:100%;z-index:0}
.grid{position:fixed;top:0;left:0;width:100%;height:100%;z-index:1;pointer-events:none;
background-image:linear-gradient(rgba(0,255,65,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(0,255,65,0.03) 1px,transparent 1px);background-size:60px 60px}
.main{position:fixed;top:0;left:0;width:100%;height:100%;z-index:2;display:flex;flex-direction:column;padding:14px}
.hud{display:flex;align-items:center;justify-content:space-between;padding:8px 18px;
background:rgba(0,10,0,0.85);border:1px solid rgba(0,255,65,0.1);border-radius:6px;margin-bottom:10px}
.hud-logo{font-family:Orbitron,sans-serif;font-size:16px;font-weight:900;color:#00ff41;text-shadow:0 0 15px rgba(0,255,65,0.3);letter-spacing:2px}
.hud-info{display:flex;align-items:center;gap:14px;font-size:10px;color:#005500}
.dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:4px}
.dot-g{background:#00ff41;box-shadow:0 0 6px #00ff41}
.dot-y{background:#005500}
.ct{display:flex;gap:10px;flex:1;min-height:0}
.left{width:180px;display:flex;flex-direction:column;gap:6px}
.center{flex:1;display:flex;align-items:center;justify-content:center;background:rgba(0,10,0,0.6);border:1px solid rgba(0,255,65,0.07);border-radius:6px;position:relative}
.chat{width:340px;display:flex;flex-direction:column;background:rgba(0,10,0,0.6);border:1px solid rgba(0,255,65,0.07);border-radius:6px;overflow:hidden}
.chat-h{padding:8px 14px;font-size:9px;color:#005500;border-bottom:1px solid rgba(0,255,65,0.05);display:flex;align-items:center;gap:4px}
.chat-h span{color:#00ff41}
.chat-msgs{flex:1;overflow-y:auto;padding:10px;scrollbar-width:thin}
.chat-msgs::-webkit-scrollbar{width:2px}
.chat-msgs::-webkit-scrollbar-thumb{background:rgba(0,255,65,0.15);border-radius:2px}
.m{margin-bottom:8px;animation:mi .25s ease}
@keyframes mi{from{opacity:0;transform:translateY(4px)}to{opacity:1;transform:translateY(0)}}
.mb{display:inline-block;max-width:88%;padding:6px 12px;border-radius:4px;font-size:12px;line-height:1.5}
.mu{text-align:right}.mu .mb{background:rgba(0,255,65,0.05);border:1px solid rgba(0,255,65,0.1);color:#00ff41}
.mb{text-align:left}.mb .mb,.ms .mb{background:rgba(0,20,0,0.35);border:1px solid rgba(0,255,65,0.05);color:#33ff77}
.ms{text-align:center}.ms .mb{background:transparent;font-size:9px;color:#003300;border:none}
.ml{font-size:8px;color:#004400;margin-bottom:2px;display:block}
.mu .ml{color:#005500}.mb .ml{color:#00cc33}
.inp{padding:8px 10px;border-top:1px solid rgba(0,255,65,0.05);display:flex;gap:5px;align-items:flex-end}
.inp-t{flex:1;background:rgba(0,15,0,0.5);border:1px solid rgba(0,255,65,0.08);border-radius:4px;
padding:6px 10px;font-family:'Share Tech Mono',monospace;font-size:12px;color:#00ff41;outline:none;
resize:none;min-height:32px;max-height:80px}
.inp-t:focus{border-color:rgba(0,255,65,0.2)}
.inp-t::placeholder{color:#003300}
.ib{width:32px;height:32px;border-radius:4px;border:1px solid rgba(0,255,65,0.1);cursor:pointer;
display:flex;align-items:center;justify-content:center;font-size:14px;background:rgba(0,15,0,0.5);color:#00ff41;flex-shrink:0}
.ib:hover{border-color:rgba(0,255,65,0.25);background:rgba(0,255,65,0.04)}
.ib-m.l{animation:pm 1s infinite;border-color:#00ff41;background:rgba(0,255,65,0.08)}
@keyframes pm{0%,100%{box-shadow:0 0 0 0 rgba(0,255,65,0.15)}50%{box-shadow:0 0 0 8px rgba(0,255,65,0)}}
.right{width:220px;display:flex;flex-direction:column;gap:6px}
.pb{background:rgba(0,10,0,0.6);border:1px solid rgba(0,255,65,0.07);border-radius:6px;padding:8px}
.pt{font-size:7px;color:#003300;letter-spacing:2px;margin-bottom:4px;display:flex;align-items:center;gap:3px}
.pt .b{flex:1;height:1px;background:rgba(0,255,65,0.04)}
/* ============ GLASS ORBIT ============ */
.orb-wrap{display:flex;align-items:center;justify-content:center;position:relative}
/* saydam ana orb */
.orb{width:200px;height:200px;border-radius:50%;position:relative;transition:all .6s ease;background:radial-gradient(circle at 35% 35%,rgba(255,255,255,.02),transparent 70%);border:1px solid rgba(255,255,255,.03)}
/* holographic glare */
.orb::before{content:'';position:absolute;top:-40%;left:-20%;width:80%;height:150%;background:linear-gradient(90deg,transparent 30%,rgba(255,255,255,.03) 50%,transparent 70%);transform:rotate(25deg);z-index:5;pointer-events:none;transition:opacity .6s;opacity:0}
.orb.idle::before,.orb.speak::before,.orb.think::before,.orb.error::before,.orb.superthink::before{opacity:1}

/* küçük saydam core */
.orb .core{width:40px;height:40px;border-radius:50%;position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);animation:orbPulse 3s ease-in-out infinite;transition:all .6s ease;z-index:4;opacity:.6}

/* ORBITING SMALL ORBS — dairesel yörüngede dönen küçük orblar */
.orbit-dot{position:absolute;border-radius:50%;z-index:5;transition:background .6s ease,box-shadow .6s ease}
/* her dot farklı yarıçap ve hızda dairesel yörüngede */
.dot1{top:50%;left:50%;width:16px;height:16px;margin:-8px 0 0 -8px;animation:orbit1 4s linear infinite}
.dot2{top:50%;left:50%;width:12px;height:12px;margin:-6px 0 0 -6px;animation:orbit2 5.5s linear infinite}
.dot3{top:50%;left:50%;width:10px;height:10px;margin:-5px 0 0 -5px;animation:orbit3 7s linear infinite}
.dot4{top:50%;left:50%;width:8px;height:8px;margin:-4px 0 0 -4px;animation:orbit4 3.2s linear infinite reverse}
.dot5{top:50%;left:50%;width:6px;height:6px;margin:-3px 0 0 -3px;animation:orbit5 6.5s linear infinite reverse}
/* glow izi */
.orbit-dot::after{content:'';position:absolute;top:0;left:0;width:100%;height:100%;border-radius:50%;animation:trail 1.5s ease-out infinite;opacity:0}
.dot1::after{animation-duration:1s}
.dot2::after{animation-duration:1.3s}
.dot3::after{animation-duration:1.6s}
/* dairesel yörünge animasyonları */
@keyframes orbit1{0%{transform:rotate(0deg) translateX(80px) rotate(0deg)}100%{transform:rotate(360deg) translateX(80px) rotate(-360deg)}}
@keyframes orbit2{0%{transform:rotate(60deg) translateX(65px) rotate(-60deg)}100%{transform:rotate(420deg) translateX(65px) rotate(-420deg)}}
@keyframes orbit3{0%{transform:rotate(120deg) translateX(50px) rotate(-120deg)}100%{transform:rotate(480deg) translateX(50px) rotate(-480deg)}}
@keyframes orbit4{0%{transform:rotate(200deg) translateX(90px) rotate(-200deg)}100%{transform:rotate(-160deg) translateX(90px) rotate(160deg)}}
@keyframes orbit5{0%{transform:rotate(300deg) translateX(35px) rotate(-300deg)}100%{transform:rotate(-60deg) translateX(35px) rotate(60deg)}}
@keyframes trail{0%{transform:scale(1);opacity:.5}100%{transform:scale(3);opacity:0}}

/* axis çizgileri — sadece çok silik referans */
.axis-x,.axis-y{position:absolute;top:50%;left:50%;z-index:2;transition:opacity .6s}
.axis-x{width:30%;height:0;border-top:1px solid;transform:translate(-50%,-50%);opacity:0}
.axis-y{width:0;height:30%;border-left:1px solid;transform:translate(-50%,-50%);opacity:0}
.orb:not(.idle) .axis-x,.orb:not(.idle) .axis-y{opacity:.08}

/* FLOATING DATA PARTICLES */
.part{position:absolute;border-radius:50%;z-index:2;pointer-events:none;opacity:0;transition:background .6s}
.orb:not(.idle) .part{opacity:1}
.p1{width:2px;height:2px;top:15%;left:20%;animation:partA 4s ease-in-out infinite}
.p2{width:3px;height:3px;top:72%;left:12%;animation:partB 5s ease-in-out infinite}
.p3{width:2px;height:2px;top:82%;left:75%;animation:partA 6s ease-in-out infinite}
.p4{width:3px;height:3px;top:22%;left:82%;animation:partB 3.5s ease-in-out infinite}
.p5{width:2px;height:2px;top:55%;left:88%;animation:partA 4.5s ease-in-out infinite}
.p6{width:3px;height:3px;top:8%;left:55%;animation:partB 5.5s ease-in-out infinite}
@keyframes partA{0%,100%{transform:translate(0,0);opacity:0}25%{transform:translate(12px,-8px);opacity:.5}50%{transform:translate(-4px,12px);opacity:.2}75%{transform:translate(-12px,-4px);opacity:.6}}
@keyframes partB{0%,100%{transform:translate(0,0);opacity:0}25%{transform:translate(-10px,10px);opacity:.4}50%{transform:translate(8px,-6px);opacity:.15}75%{transform:translate(6px,8px);opacity:.5}}

/* ============ ORB STATES ============ */
/* IDLE — Green */
.orb.idle .core{background:radial-gradient(circle at 35% 35%,#00ff41,#003300);box-shadow:0 0 40px rgba(0,255,65,.2),0 0 80px rgba(0,255,65,.08),inset 0 0 20px rgba(0,255,65,.1)}
.orb.idle .orbit-dot{background:#00ff41;box-shadow:0 0 10px rgba(0,255,65,.5)}
.orb.idle .orbit-dot::after{background:#00ff41}
.orb.idle .axis-x,.orb.idle .axis-y{border-color:rgba(0,255,65,.06)}
.orb.idle .part{background:rgba(0,255,65,.3)}

/* SPEAK — Yellow */
.orb.speak .core{background:radial-gradient(circle at 35% 35%,#ffdd00,#664400);box-shadow:0 0 50px rgba(255,221,0,.25),0 0 100px rgba(255,221,0,.08),inset 0 0 20px rgba(255,221,0,.1);animation:orbPulse .4s ease-in-out infinite}
.orb.speak .orbit-dot{background:#ffdd00;box-shadow:0 0 12px rgba(255,221,0,.5)}
.orb.speak .orbit-dot::after{background:#ffdd00}
.orb.speak .axis-x,.orb.speak .axis-y{border-color:rgba(255,221,0,.08)}
.orb.speak .part{background:rgba(255,221,0,.3)}

/* THINK — Blue */
.orb.think .core{background:radial-gradient(circle at 35% 35%,#3388ff,#002266);box-shadow:0 0 50px rgba(0,120,255,.25),0 0 100px rgba(0,120,255,.08),inset 0 0 20px rgba(0,120,255,.1);animation:orbPulse .8s ease-in-out infinite}
.orb.think .orbit-dot{background:#3388ff;box-shadow:0 0 12px rgba(0,120,255,.5)}
.orb.think .orbit-dot::after{background:#3388ff}
.orb.think .axis-x,.orb.think .axis-y{border-color:rgba(0,120,255,.08)}
.orb.think .part{background:rgba(0,120,255,.3)}

/* ERROR — Red */
.orb.error .core{background:radial-gradient(circle at 35% 35%,#ff2222,#440000);box-shadow:0 0 50px rgba(255,30,30,.25),0 0 100px rgba(255,30,30,.08),inset 0 0 20px rgba(255,30,30,.1);animation:orbShake .3s ease-in-out infinite}
.orb.error .orbit-dot{background:#ff2222;box-shadow:0 0 10px rgba(255,30,30,.5)}
.orb.error .orbit-dot::after{background:#ff2222}
.orb.error .axis-x,.orb.error .axis-y{border-color:rgba(255,30,30,.08)}
.orb.error .part{background:rgba(255,30,30,.3)}

/* SUPERTHINK — Purple */
.orb.superthink .core{background:radial-gradient(circle at 35% 35%,#c44bff,#3a0066);box-shadow:0 0 60px rgba(180,0,255,.3),0 0 120px rgba(180,0,255,.1),inset 0 0 25px rgba(180,0,255,.12);animation:orbPulse .3s ease-in-out infinite}
.orb.superthink .orbit-dot{background:#c44bff;box-shadow:0 0 15px rgba(180,0,255,.6)}
.orb.superthink .orbit-dot::after{background:#c44bff}
.orb.superthink .axis-x,.orb.superthink .axis-y{border-color:rgba(180,0,255,.1)}
.orb.superthink .part{background:rgba(180,0,255,.3)}

/* keyframes */
@keyframes orbPulse{0%,100%{transform:translate(-50%,-50%) scale(1)}50%{transform:translate(-50%,-50%) scale(1.1)}}
@keyframes orbScan{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
@keyframes octaSpin{0%{transform:rotate(0)}100%{transform:rotate(360deg)}}
@keyframes orbShake{0%,100%{transform:translate(-50%,-50%) translateX(0)}25%{transform:translate(-50%,-50%) translateX(-5px)}75%{transform:translate(-50%,-50%) translateX(5px)}}

.os{text-align:center;margin-top:10px;font-size:11px;color:#003300;transition:color .4s;letter-spacing:3px}
.os.g{color:#00ff41}.os.y{color:#ffdd00}.os.b{color:#3388ff}.os.r{color:#ff2222}.os.p{color:#c44bff}
.tr{display:flex;align-items:center;justify-content:space-between;padding:2px 0}
.tl{font-size:10px;color:#005500}
.ts{width:30px;height:16px;border-radius:8px;background:rgba(0,255,65,0.03);cursor:pointer;position:relative;border:1px solid rgba(0,255,65,0.05)}
.ts.a{background:rgba(0,255,65,0.08);border-color:rgba(0,255,65,0.12)}
.ts::after{content:'';position:absolute;top:2px;left:2px;width:10px;height:10px;border-radius:50%;background:#003300}
.ts.a::after{left:16px;background:#00ff41;box-shadow:0 0 4px rgba(0,255,65,0.3)}
.cg{display:grid;grid-template-columns:1fr 1fr;gap:2px}
.cb{padding:4px 2px;border-radius:3px;border:1px solid rgba(0,255,65,0.04);background:rgba(0,255,65,0.01);color:#005500;font-size:8px;cursor:pointer}
.cb:hover{background:rgba(0,255,65,0.05);border-color:rgba(0,255,65,0.12);color:#00ff41}
.cb i{font-size:11px;display:block;margin-bottom:1px}
.sl{width:100%;background:rgba(0,15,0,0.5);border:1px solid rgba(0,255,65,0.07);border-radius:3px;padding:3px 5px;font-size:8px;color:#005500;outline:none}
.sl option{background:#0a0a0a;color:#00ff41}
.clb{width:100%;padding:4px;border-radius:3px;border:1px solid rgba(0,255,65,0.05);background:rgba(0,255,65,0.01);color:#003300;font-size:8px;cursor:pointer;margin-top:2px}
.clb:hover{background:rgba(0,255,65,0.05);color:#00cc33}
.td{display:flex;gap:2px;padding:4px 0}.td span{width:4px;height:4px;border-radius:50%;background:#00ff41;animation:tb 1.4s infinite}
.td span:nth-child(2){animation-delay:.2s}.td span:nth-child(3){animation-delay:.4s}
@keyframes tb{0%,80%,100%{transform:scale(.6);opacity:.2}40%{transform:scale(1);opacity:1}}
</style>
</head>
<body>
<canvas id="bgCanvas"></canvas><div class="grid"></div>
<div class="main">
<div class="hud"><div class="hud-logo">◈ GLASSCAT / JARVIS</div>
<div class="hud-info"><span><span class="dot dot-g"></span>ON</span><span id="hModel">Ultra_Agent</span><span id="hTime">--:--:--</span></div></div>
<div class="ct">
<div class="left">
<div class="pb"><div class="pt"><span>●</span>VOICE<span class="b"></span></div>
<div class="tr"><span class="tl">Listen</span><div class="ts" id="vT" onclick="tgV()"></div></div>
<div class="tr"><span class="tl">Speak</span><div class="ts a" id="sT" onclick="tgS()"></div></div></div>
<div class="pb" style="flex:1"><div class="pt"><span>●</span>CMDS<span class="b"></span></div>
<div class="cg"><button class="cb" onclick="qc('chrome')"><i>🌐</i>Chrome</button>
<button class="cb" onclick="qc('youtube')"><i>▶</i>YouTube</button>
<button class="cb" onclick="qc('notepad')"><i>📝</i>Not Defteri</button>
<button class="cb" onclick="qc('spotify')"><i>🎵</i>Spotify</button>
<button class="cb" onclick="qc('cmd')"><i>⎚</i>CMD</button>
<button class="cb" onclick="qc('ss')"><i>📷</i>SS Al</button>
<button class="cb" onclick="qc('saat')"><i>⏰</i>Saat</button>
<button class="cb" onclick="qc('github')"><i>💻</i>GitHub</button>
<button class="cb" onclick="qc('superthink')" style="border-color:rgba(180,0,255,0.2);color:#b300ff"><i>🧠</i>Superthink</button>
</div></div>
<div class="pb"><select class="sl" id="mSel" onchange="chM(this.value)">
<option value="glassesglitchstudio/gulmzcetiner:Ultra_Agent">🪐 Ultra Agent</option>
<option value="glassesglitchstudio/gulmzcetiner:V6_OMNI_OVERLORD">☠️ V6 OMNI OVERLORD</option>
<option value="glassesglitchstudio/gulmzcetiner:V5_NEXUS_CORE">⚡ V5 NEXUS CORE</option>
<option value="glassesglitchstudio/gulmzcetiner:V7_HYBRID_TITAN">🤖 V7 HYBRID TITAN</option>
<option value="glassesglitchstudio/glitch_opus:X_GLITCH_OPUS_V2">🌀 GLITCH OPUS V2</option>
<option value="glassesglitchstudio/gulmzcetiner:V5_XCODE">💻 V5 XCODE</option>
<option value="qwen2.5-coder:7b">🔧 qwen2.5-coder:7b</option>
</select>
<button class="clb" onclick="clr()">⌫ CLEAR</button></div></div>
<div class="center">
<div class="orb-wrap"><div class="orb idle" id="orb">
  <div class="axis-x"></div><div class="axis-y"></div>
  <div class="core"></div>
  <div class="orbit-dot dot1"></div><div class="orbit-dot dot2"></div>
  <div class="orbit-dot dot3"></div><div class="orbit-dot dot4"></div>
  <div class="orbit-dot dot5"></div>
  <div class="part p1"></div><div class="part p2"></div><div class="part p3"></div>
  <div class="part p4"></div><div class="part p5"></div><div class="part p6"></div>
</div></div>
<div class="os g" id="oS">◈ STANDBY</div>
<button class="ib ib-m" id="micB" onclick="tglMic()" style="position:absolute;bottom:14px;left:50%;transform:translateX(-50%);width:auto;padding:6px 16px;gap:6px;font-size:11px">🎤 VOICE</button>
</div>
<div class="chat"><div class="chat-h"><span>◆</span>TERMINAL<span>◆</span><div style="flex:1"></div><span id="mCnt">0</span></div>
<div class="chat-msgs" id="chatMsgs"></div>
<div class="inp"><textarea class="inp-t" id="inpT" rows="1" placeholder=">_" onkeydown="if(event.key=='Enter'&&!event.shiftKey){event.preventDefault();snd()}"></textarea>
<button class="ib" onclick="snd()">⏎</button></div></div>
</div>
<script>
const cv=document.getElementById('bgCanvas'),cx=cv.getContext('2d');let W,H,pts=[],sts=[],mx=0,my=0;
function rs(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight}
window.addEventListener('resize',rs);rs();
window.addEventListener('mousemove',e=>{mx=e.clientX;my=e.clientY});
for(let i=0;i<60;i++)sts.push({x:Math.random()*2000-500,y:Math.random()*2000-500,z:Math.random()*1000,s:Math.random()*1+.2});
for(let i=0;i<40;i++)pts.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3,s:Math.random()*2+.5,a:Math.random()*.4+.1});
function dS(){sts.forEach(s=>{const sx=(s.x/s.z)*200+W/2,sy=(s.y/s.z)*200+H/2,sz=Math.max(.1,200/s.z);
if(s.z>=0){cx.fillStyle='rgba(0,255,65,'+Math.min(.5,sz*.3)+')';
cx.beginPath();cx.arc(sx,sy,s.s*sz,0,7);cx.fill()}s.z-=.5;if(s.z<1){s.z=1000;s.x=Math.random()*2000-500;s.y=Math.random()*2000-500}})}
function dP(){pts.forEach(p=>{p.x+=p.vx;p.y+=p.vy;if(p.x<0||p.x>W)p.vx*=-1;if(p.y<0||p.y>H)p.vy*=-1;
const d=Math.hypot(p.x-mx,p.y-my);cx.fillStyle=d<100?'rgba(0,255,65,'+(p.a*(1-d/100)*2)+')':'rgba(0,255,65,'+(p.a*.5)+')';
cx.beginPath();cx.arc(p.x,p.y,p.s,0,7);cx.fill()})}
function an(){cx.fillStyle='rgba(10,10,10,.25)';cx.fillRect(0,0,W,H);dS();dP();requestAnimationFrame(an)}
an();

const cm=document.getElementById('chatMsgs'),ip=document.getElementById('inpT');
const oS=document.getElementById('oS'),orb=document.getElementById('orb'),mS=document.getElementById('mSel');
const hT=document.getElementById('hTime'),mC=document.getElementById('mCnt');
let lis=false,vM=false,sT=true,mn=0;

function setOrb(s){orb.className='orb '+s;oS.className='os';if(s=='idle')oS.classList.add('g');else if(s=='speak')oS.classList.add('y');else if(s=='think')oS.classList.add('b');else if(s=='error')oS.classList.add('r');else if(s=='superthink')oS.classList.add('p')}

function clk(){const d=new Date();hT.textContent=d.toTimeString().slice(0,8)}
setInterval(clk,1000);clk();

function ad(r,t){const d=document.createElement('div');d.className=r=='user'?'m mu':r=='bot'?'m mb':'m ms';
const l=r=='user'?'U':r=='bot'?'JARVIS':'SYS';
d.innerHTML='<span class="ml">◆ '+l+'</span><div class="mb">'+t+'</div>';
cm.appendChild(d);cm.scrollTop=cm.scrollHeight;if(r!='sys'){mn++;mC.textContent=mn}}
let te=null;
function st(){if(!te){te=document.createElement('div');te.className='m mb';
te.innerHTML='<span class="ml">◆ JARVIS</span><div class="mb"><div class="td"><span></span><span></span><span></span></div></div>';
cm.appendChild(te)}cm.scrollTop=cm.scrollHeight}
function ht(){if(te){te.remove();te=null}}
async function ap(e,d){try{const r=await fetch(e,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});return await r.json()}catch(e){return{response:'ERR'}}}
async function snd(){const t=ip.value.trim();if(!t)return;ip.value='';ad('user',t);st();setOrb('think');oS.textContent='◈ THINKING...';
const r=await ap('/api/chat',{t,model:mS.value});
ht();if(r.r){const reply=r.r;ad('bot',reply);
if(r.type=='superthink'){setOrb('superthink');oS.textContent='◈ SUPER THINKING';}
else{setOrb('idle');oS.textContent='◈ STANDBY';}
return reply}
else{setOrb('error');oS.textContent='◈ ERROR';ad('sys','Connection error');setTimeout(()=>{setOrb('idle');oS.textContent='◈ STANDBY'},3000);return''}}
function qc(c){const m={chrome:'chrome ac',youtube:'youtube ac',notepad:'not defteri ac',spotify:'spotify ac',cmd:'cmd ac',ss:'ekran goruntusu al',saat:'saat kac',github:'github ac',superthink:'superthinking modu aktif'};ip.value=m[c]||c;snd()}
async function clr(){cm.innerHTML='';mn=0;mC.textContent='0';await ap('/api/clear',{});ad('sys','Cleared.')}
function chM(m){document.getElementById('hModel').textContent=m}
function tgV(){vM=!vM;document.getElementById('vT').classList.toggle('a')}
function tgS(){sT=!sT;document.getElementById('sT').classList.toggle('a')}
async function tglMic(){if(lis)return;lis=true;
document.getElementById('micB').classList.add('l');setOrb('speak');
oS.textContent='◈ LISTENING...';ad('sys','🎤');
const r=await ap('/api/listen',{to:5});
if(r.t){ip.value=r.t;const reply=await snd();if(sT&&reply)await ap('/api/speak',{text:reply})}
else ad('sys','No voice (5s)');
lis=false;document.getElementById('micB').classList.remove('l');setOrb('idle');oS.textContent='◈ STANDBY'}
setOrb('idle');ad('sys','JARVIS ready.');ad('bot','Commander Berkay, systems online.');
</script>
</body></html>"""

# ============ BACKEND ============
conversations = {}
MAX_HISTORY = 20

def get_brain(model):
    global brain_engine
    class Brain:
        def __init__(self, m):
            self.model = m
        def ask(self, prompt, session="default"):
            if session not in conversations:
                conversations[session] = [
                    {"role": "system", "content": "Adın JARVIS. Berkay'ın yapay zeka asistanısın. Türkçe konuş, kısa ve net cevap ver. Önceki konuşmayı unutma, bağlamı koru. Zorlanırsan 'superthinking modu aktif' yaz, derin düşünce moduna geçerim. Uygulama açmak için 'X i aç' formatını kullan, Windows Search ile bulurum."}
                ]
            conversations[session].append({"role": "user", "content": prompt})
            history = conversations[session][-(MAX_HISTORY+1):]
            try:
                payload = json.dumps({
                    "model": self.model,
                    "messages": history,
                    "stream": False,
                    "options": {"temperature": 0.3, "num_predict": 2048, "num_ctx": 8192}
                }).encode()
                req = urllib.request.Request(
                    "http://localhost:11434/api/chat",
                    data=payload, headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=60) as r:
                    data = json.loads(r.read())
                    reply = data.get("message", {}).get("content", "").strip() or "..."
                    conversations[session].append({"role": "assistant", "content": reply})
                    return reply
            except Exception as e:
                return f"Ollama offline ({e})"
    if brain_engine is None or brain_engine.model != model:
        brain_engine = Brain(model)
    return brain_engine

def get_voice():
    global voice_engine
    if voice_engine is None:
        class Voice:
            def __init__(self):
                self.whisper = None
            def _load(self):
                if self.whisper is None:
                    from faster_whisper import WhisperModel
                    self.whisper = WhisperModel("small", device="cuda", compute_type="float16")
            def listen(self, timeout=5):
                import sounddevice as sd, numpy as np
                import scipy.io.wavfile as wav
                self._load()
                # record in 0.5s chunks, stop after 1.5s silence or timeout
                max_chunks = int(timeout / 0.5)
                buffer = []
                silence = 0
                speech_detected = False
                for _ in range(max_chunks):
                    chunk = sd.rec(int(SAMPLE_RATE * 0.5), samplerate=SAMPLE_RATE, channels=1, dtype="float32")
                    sd.wait()
                    energy = np.sqrt(np.mean(chunk**2))
                    if energy > 0.008:
                        silence = 0
                        speech_detected = True
                    else:
                        silence += 1
                    buffer.append(chunk)
                    if speech_detected and silence >= 3:
                        break
                if not speech_detected: return ""
                audio = np.concatenate(buffer, axis=0)
                with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
                    wav.write(f.name, SAMPLE_RATE, (audio * 32767).astype("int16"))
                    segs, _ = self.whisper.transcribe(f.name, language="tr", beam_size=3)
                    text = " ".join(s.text for s in segs)
                try: os.unlink(f.name)
                except: pass
                return text.strip().lower()
            def speak(self, text):
                import pyttsx3
                try:
                    eng = pyttsx3.init()
                    for v in eng.getProperty("voices"):
                        if "turkish" in v.name.lower():
                            eng.setProperty("voice", v.id); break
                    eng.setProperty("rate", 165)
                    eng.say(text); eng.runAndWait()
                except: pass
        voice_engine = Voice()
    return voice_engine

# Windows Search ile uygulama bul + aç
def win_search_app(app_name):
    try:
        # PowerShell ile Start Menu'de ara
        cmd = f'powershell -Command "($app = Get-StartApps | Where-Object {{ $_.Name -like \\\"*{app_name}*\\\" }} | Select-Object -First 1); if ($app) {{ $null = [System.Diagnostics.Process]::Start($app.AppId); Write-Output \\\"OK\\\" }} else {{ Write-Output \\\"NOT_FOUND\\\" }}"'
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10, shell=True)
        out = r.stdout.strip()
        if "OK" in out:
            return True
        # fallback: PATH'te dene
        subprocess.run(["where", app_name], capture_output=True, timeout=5)
        subprocess.Popen(["cmd", "/c", "start", "", app_name], shell=True)
        return True
    except:
        return False

def extract_app_name(t):
    # "aç calculator" formatı (verb + object)
    m = re.search(r"(?:a[çc]\b|başlat|açıver)\s+(\w[\w\-]*)", t)
    if m: return m.group(1).strip("'\"")
    # "calculator'ı aç" / "calculator aç" (object + verb, Türkçe)
    m = re.search(r"(\w[\w\-]*)(?:'?[ıiuüeo])?\s*(?:a[çc]\b|başlat|açıver)", t)
    if m: return m.group(1)
    return None

def execute_command(text):
    t = text.lower().strip()
    app = extract_app_name(t)
    if app:
        known = {"chrome":"chrome","youtube":"","not":"notepad","notepad":"notepad","spotify":"spotify",
                 "cmd":"cmd","terminal":"cmd","github":"","google":"","word":"winword","excel":"excel",
                 "powerpoint":"powerpnt","paint":"mspaint","calc":"calc","hesap":"calc","calculator":"calc",
                 "ayarlar":"ms-settings:","discord":"discord","telegram":"telegram","vs":"code",
                 "vscode":"code","code":"code","dosya":"explorer","explorer":"explorer",
                 "edge":"msedge","brave":"brave","firefox":"firefox","zoom":"zoom",
                 "aygıt":"devicepairingwizard","not":"notepad","blok":"notepad",
                 "makinesini":"calc","makine":"calc"}
        mapped = known.get(app, app)
        if app == "youtube":
            subprocess.Popen(["cmd","/c","start","https://youtube.com"]); return f"YouTube opened."
        if app == "github":
            subprocess.Popen(["cmd","/c","start","https://github.com"]); return f"GitHub opened."
        if app == "google":
            subprocess.Popen(["cmd","/c","start","https://google.com"]); return f"Google opened."
        if mapped.startswith("ms-"):
            subprocess.Popen(["cmd","/c","start",mapped]); return f"{app} opened."
        try:
            os.startfile(mapped)
            return f"{app} opened."
        except:
            if win_search_app(app):
                return f"{app} opened."
            return f"Could not find {app}."
    if re.search(r"\b(saat|zaman)\b", t) and re.search(r"(ka[çc]|nedir)", t):
        return datetime.now().strftime("Time: %H:%M")
    if re.search(r"\b(tarih|bugün)\b", t) and re.search(r"(ka[çc]|ne|nedir)", t):
        return datetime.now().strftime("Date: %d %B %Y")
    if re.search(r"\b(ekran|screenshot|ss)\b", t) and re.search(r"(al|[çc]ek|görüntü)", t):
        try:
            import pyautogui
            pyautogui.screenshot(str(Path.home()/"Pictures"/f"jarvis_{int(time.time())}.png"))
            return "Screenshot saved."
        except: return "Screenshot failed."
    if re.search(r"\b(superthinking|super.think|derin.düşünce|zorlan)\b", t):
        return "__SUPER_THINK__"
    if re.search(r"\b(kapat|shutdown)\b", t):
        subprocess.Popen(["shutdown","/s","/t","30"])
        return "Shutdown in 30s."
    return None

# ============ ROUTES ============
@app.route("/")
def index(): return HTML

STRUGGLE_PATTERNS = [
    r"(?:bilmiyorum|anlamadım|emin değilim|karmaşık|zor|anlayamadım)",
    r"(?:I'?m (?:not sure|uncertain|confused)|(?:don'?t|do not) know)",
    r"(?:too complex|difficult|unclear|ambiguous)",
]

@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.json
    text = data.get("t", "")
    model = data.get("model", OLLAMA_MODEL)
    cmd = execute_command(text)
    if cmd == "__SUPER_THINK__":
        return jsonify({"r": "Superthinking mode active. Processing with enhanced depth.", "type": "superthink"})
    if cmd: return jsonify({"r": cmd, "type": "cmd"})
    reply = get_brain(model).ask(text)
    # auto-superthink if AI struggles
    if any(re.search(p, reply, re.IGNORECASE) for p in STRUGGLE_PATTERNS):
        # retry with deeper reasoning
        deep = get_brain(model).ask(
            "[SUPER THINKING MODE] " + text +
            " - Think step by step deeply. Use chain-of-thought. Do not say you don't know.",
            session="superthink"
        )
        return jsonify({"r": deep, "type": "superthink"})
    return jsonify({"r": reply, "type": "ai"})

@app.route("/api/listen", methods=["POST"])
def api_listen():
    try: return jsonify({"t": get_voice().listen(timeout=request.json.get("to", 8))})
    except Exception as e: return jsonify({"t": "", "e": str(e)})

@app.route("/api/speak", methods=["POST"])
def api_speak():
    text = request.json.get("text", "")
    if text: threading.Thread(target=get_voice().speak, args=(text,), daemon=True).start()
    return jsonify({"ok": True})

@app.route("/api/clear", methods=["POST"])
def api_clear():
    conversations.pop("default", None)
    return jsonify({"ok": True})

# ============ OLLAMA BOOT ============
G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; R = "\033[91m"; B = "\033[1m"; N = "\033[0m"

def check_ollama():
    os.system("cls" if os.name == "nt" else "clear")
    banner = f"""{G}
    {'='*50}
    {C}[+] GLASSCAT / JARVIS — OLLAMA BOOT SEQUENCE{G}
    {'='*50}{N}
    """
    print(banner)
    ollama_ok = False
    # check if ollama is running
    for i in range(15):
        try:
            req = urllib.request.Request("http://localhost:11434/api/tags")
            with urllib.request.urlopen(req, timeout=2) as r:
                data = json.loads(r.read())
                models = [m["name"] for m in data.get("models", [])]
                print(f"  {G}[OK] Ollama is running{N}")
                print(f"  {C}  -> {len(models)} model{'s' if len(models)!=1 else ''} available{N}")
                for m in models:
                    print(f"  {G}    * {m}{N}")
                ollama_ok = True
                break
        except:
            if i == 0:
                print(f"  {Y}[!] Ollama not detected. Starting...{N}")
                # try to start ollama
                paths = [
                    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Ollama\ollama.exe"),
                    os.path.expandvars(r"%PROGRAMFILES%\Ollama\ollama.exe"),
                    os.path.expandvars(r"%PROGRAMFILES(X86)%\Ollama\ollama.exe"),
                    "ollama",
                ]
                for p in paths:
                    try:
                        subprocess.Popen([p, "serve"], creationflags=subprocess.CREATE_NO_WINDOW)
                        print(f"  {G}  -> Started: {p}{N}")
                        break
                    except: continue
            print(f"  {Y}  waiting... ({i+1}/15){N}")
            time.sleep(2)
    if not ollama_ok:
        print(f"\n  {R}[ERR] Ollama failed to start. Check if it's installed.{N}")
        print(f"  {Y}  Download: https://ollama.com/download{N}")
    else:
        target = OLLAMA_MODEL
        print(f"\n  {C}[?] Checking target model: {target}{N}")
        if target not in models:
            print(f"  {Y}  [!] Model not found locally, will pull on first request{N}")
        else:
            print(f"  {G}  [OK] Model ready{N}")
    print(f"\n  {G}{'='*46}{N}")
    print(f"  {B}{G}  * JARVIS UI starting on http://127.0.0.1:{PORT}{N}")
    print(f"  {G}{'='*46}{N}\n")

# ============ MAIN ============
def run_flask():
    app.run(host="127.0.0.1", port=PORT, debug=False, use_reloader=False)

if __name__ == "__main__":
    check_ollama()
    threading.Thread(target=run_flask, daemon=True).start()
    time.sleep(1.5)
    import webview
    webview.create_window("JARVIS — GlassesCat", f"http://127.0.0.1:{PORT}",
                         width=1100, height=680, min_size=(900,500), resizable=True)
    webview.start(debug=False, http_server=False)
