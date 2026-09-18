'use strict';

const state = {manifest:null,nodes:[],theory:null,receipt:null,history:null};
const $ = (q,root=document)=>root.querySelector(q);
const $$ = (q,root=document)=>[...root.querySelectorAll(q)];
const esc = s => String(s ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

async function json(path){const r=await fetch(path,{cache:'no-store'});if(!r.ok)throw new Error(`${path}: ${r.status}`);return r.json();}

function tabSetup(){
  $$('.tab').forEach(btn=>btn.addEventListener('click',()=>{
    $$('.tab').forEach(x=>x.classList.toggle('active',x===btn));
    $$('.view').forEach(v=>v.classList.toggle('active',v.dataset.view===btn.dataset.view));
  }));
}

function nodeDef(id){return state.nodes.find(n=>n.id===id);}
function roleClass(inst){const d=nodeDef(inst.node);if(d?.role==='source')return 'role-source';if(inst.id.includes('frozen'))return 'role-attacker';return 'role-mechanism';}

function renderWorkbench(){
  const t=state.theory;
  $('#theory-title').textContent=t.title;$('#theory-id').textContent=t.id;$('#theory-question').textContent=t.question;$('#theory-hypothesis').textContent=t.hypothesis;
  const graph=$('#graph'); graph.innerHTML='';
  const positions={write_input:[35,70],probe_input:[35,280],memory:[360,70],frozen_memory:[360,280]};
  const svg=document.createElementNS('http://www.w3.org/2000/svg','svg'); graph.append(svg);
  for(const edge of t.edges){
    const [s]=edge.from.split('.'),[d]=edge.to.split('.'); const a=positions[s],b=positions[d]; if(!a||!b)continue;
    const path=document.createElementNS('http://www.w3.org/2000/svg','path');
    const x1=a[0]+210,y1=a[1]+45,x2=b[0],y2=b[1]+45,dx=Math.max(55,(x2-x1)*.5);
    path.setAttribute('d',`M${x1},${y1} C${x1+dx},${y1} ${x2-dx},${y2} ${x2},${y2}`);path.setAttribute('class','wire');svg.append(path);
  }
  for(const inst of t.nodes){
    const def=nodeDef(inst.node),pos=positions[inst.id]||[50,50]; const card=document.createElement('div');
    card.className=`graph-node ${roleClass(inst)}`;card.style.left=`${pos[0]}px`;card.style.top=`${pos[1]}px`;
    card.innerHTML=`<div class="node-head"><b>${esc(inst.id)}</b><span>${esc(def.role)}</span></div><div class="node-body"><code>${esc(inst.node)}</code><div class="node-ports"><span class="ports">in · ${Object.keys(def.inputs).join(', ')||'—'}</span><span class="ports">out · ${Object.keys(def.outputs).join(', ')||'—'}</span></div></div>`;
    card.addEventListener('click',()=>inspect(def,inst)); graph.append(card);
  }
  $('#experiments').innerHTML=t.experiments.map(e=>`<article class="experiment-card"><div class="eyebrow">${esc(e.id)}</div><h3>${esc(e.purpose)}</h3><div>${e.protocol.map(p=>`<span class="phase">${esc(p.id)}</span>`).join('')}</div><p>${e.measurements.map(m=>m.name).join(' · ')}</p></article>`).join('');
  $('#gates').innerHTML=t.gates.map(g=>`<article class="gate-card"><div class="eyebrow">GATE</div><strong>${esc(g.id)}</strong><p>${esc(g.lhs)} ${esc(g.op)} ${esc(g.rhs)}</p><small>${esc(g.meaning)}</small></article>`).join('');
}

function inspect(def,inst){
  $('#inspector-empty').hidden=true; const host=$('#inspector-content');host.hidden=false;
  const ports=(obj)=>Object.entries(obj).map(([k,v])=>`<tr><td>${esc(k)}</td><td>${esc(typeof v==='string'?v:v.type)}</td></tr>`).join('');
  host.innerHTML=`<div class="eyebrow">${esc(def.role)} · ${esc(def.version)}</div><h2>${esc(inst.id)}</h2><p>${esc(def.summary)}</p><div class="inspect-block"><small>EXECUTOR</small><p><code>${esc(def.executor)}</code></p></div><div class="inspect-block"><small>INPUT PORTS</small><table class="ports-table">${ports(def.inputs)}</table></div><div class="inspect-block"><small>OUTPUT PORTS</small><table class="ports-table">${ports(def.outputs)}</table></div><div class="inspect-block"><small>NARROW CLAIMS</small>${def.claims.map(c=>`<p>${esc(c)}</p>`).join('')}</div><div class="inspect-block"><small>PROVENANCE</small><p>${esc(def.provenance?.source||'—')}</p></div>`;
}

function renderNodes(filter=''){
  const q=filter.trim().toLowerCase(); const nodes=state.nodes.filter(n=>!q||[n.id,n.role,n.summary,...(n.tags||[])].join(' ').toLowerCase().includes(q));
  $('#node-library').innerHTML=nodes.map(n=>`<article class="library-card"><span class="role">${esc(n.role)}</span><h3>${esc(n.id)}</h3><p>${esc(n.summary)}</p><div class="tags">${(n.tags||[]).join(' · ')}</div></article>`).join('');
}

function renderReceipt(){
  const r=state.receipt;$('#receipt-status').textContent=r.status.toUpperCase();
  $('#measurements').innerHTML=Object.entries(r.measurements).map(([k,v])=>`<div class="measurement"><span>${esc(k)}</span><b>${typeof v==='number'?v.toFixed(6):esc(JSON.stringify(v))}</b></div>`).join('');
  $('#receipt-gates').innerHTML=r.gates.map(g=>`<div class="receipt-gate"><b>${esc(g.id)} · ${g.passed?'PASS':'FAIL'}</b><div>${esc(g.lhs)} ${esc(g.op)} ${esc(g.rhs)}</div><small>${esc(g.meaning)}</small></div>`).join('');
  const groups=[['SUPPORTED',r.claims.supported],['LIMITED',r.claims.limited],['KILLED',r.claims.killed],['LIMITATIONS',r.limitations]];
  $('#claim-ledger').innerHTML=groups.map(([name,items])=>`<div class="claim-group"><h3>${name}</h3>${items?.length?`<ul>${items.map(x=>`<li>${esc(x)}</li>`).join('')}</ul>`:'<p class="fineprint">none</p>'}</div>`).join('');
}

function depthMap(){const by=new Map(state.history.attempts.map(a=>[a.id,a]));const cache={};function d(a){if(a.parent==null)return 0;if(cache[a.id]!=null)return cache[a.id];return cache[a.id]=1+d(by.get(a.parent));}return Object.fromEntries(state.history.attempts.map(a=>[a.id,d(a)]));}
function renderHistory(){const depths=depthMap();$('#history-tree').innerHTML=state.history.attempts.slice().sort((a,b)=>a.created_order-b.created_order).map(a=>`<div class="history-node depth-${Math.min(4,depths[a.id])}"><b>${esc(a.id)}</b><span class="score">${Number(a.score).toFixed(2)}</span><p>${esc(a.variant)} · ${esc(a.outcome)} · cost ${esc(a.cost)}</p><p>${esc(a.observation)}</p></div>`).join('');}
function replay(policy,budget){const attempts=state.history.attempts,children={};for(const a of attempts)(children[a.parent??'ROOT']??=[]).push(a);Object.values(children).forEach(v=>v.sort((a,b)=>a.created_order-b.created_order));let frontier=[...(children.ROOT||[])],visited=[];while(frontier.length&&visited.length<budget){let cur;if(policy==='depth_first')cur=frontier.pop();else if(policy==='breadth_first')cur=frontier.shift();else{frontier.sort((a,b)=>(b.priority_hint??b.score)-(a.priority_hint??a.score)||b.score-a.score);cur=frontier.shift();}visited.push(cur);const kids=[...(children[cur.id]||[])];if(policy==='depth_first')frontier.push(...kids.reverse());else frontier.push(...kids);}const best=visited.slice().sort((a,b)=>b.score-a.score)[0];return{visited:visited.map(x=>x.id),cost:visited.reduce((s,x)=>s+x.cost,0),best:best?.id,score:best?.score};}
function renderReplayResult(){const p=$('#policy').value,b=Number($('#budget').value),r=replay(p,b);$('#replay-result').textContent=`policy: ${p}\nbudget: ${b}\nvisited: ${r.visited.join(' → ')}\nbest: ${r.best}\nbest score: ${r.score}\nrepresented cost: ${r.cost}`;}

async function init(){
  tabSetup();
  try{
    state.manifest=await json('theorylab.json');state.nodes=await json(state.manifest.entrypoints.node_catalog);state.theory=await json(state.manifest.entrypoints.theories[0]);state.receipt=await json(state.manifest.entrypoints.receipts[0]);state.history=await json(state.manifest.entrypoints.discovery_history);
    $('#stat-nodes').textContent=state.nodes.length;$('#stat-theories').textContent=state.manifest.entrypoints.theories.length;$('#stat-gates').textContent=state.theory.gates.length;$('#stat-attempts').textContent=state.history.attempts.length;$('#runtime-status').textContent='contracts loaded';
    renderWorkbench();renderNodes();renderReceipt();renderHistory();$('#manifest-preview').textContent=JSON.stringify(state.manifest,null,2);renderReplayResult();
    $('#node-search').addEventListener('input',e=>renderNodes(e.target.value));$('#budget').addEventListener('input',e=>{$('#budget-out').textContent=e.target.value;renderReplayResult();});$('#policy').addEventListener('change',renderReplayResult);$('#run-replay').addEventListener('click',renderReplayResult);
  }catch(err){$('#runtime-status').textContent='load failed';console.error(err);}
}
init();
