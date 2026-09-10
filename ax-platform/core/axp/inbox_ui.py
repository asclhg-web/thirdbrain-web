"""승인함 웹 UI (demo) — API 위의 단일 페이지. prod에서는 Odoo 애드온이 대체.

/inbox 에서 대기 카드 검토 → '왜?' 근거 전개 → 승인/반려(사유 필수).
역할은 우상단 선택(demo 전용) — prod에서는 SSO가 부여한다.
"""

PAGE = """<!doctype html><meta charset="utf-8"><title>판단 카드 승인함</title>
<style>
body{font-family:'Noto Sans CJK KR',sans-serif;margin:24px;background:#F8F2EA;color:#2E241C;max-width:900px}
h1{color:#6E3A1C} .role{float:right;font-size:13px}
.card{background:#fff;border:1px solid #DCCDBB;border-left:6px solid #9C5227;border-radius:10px;
padding:14px 18px;margin-bottom:14px}
.kind{display:inline-block;background:#EFE5D8;border-radius:12px;padding:1px 10px;font-size:12px;color:#6E3A1C}
.range{color:#0E8F86;font-size:13px}
.narr{white-space:pre-line;font-size:13.5px;color:#4a3d31;margin:8px 0;border-top:1px dashed #DCCDBB;padding-top:8px}
button{border:0;border-radius:7px;padding:7px 16px;margin-right:8px;cursor:pointer;font-size:13px}
.ok{background:#0E8F86;color:#fff} .no{background:#A8493B;color:#fff} .why{background:#E8A33D;color:#2B1D12}
.ev{display:none;background:#F8F2EA;border-radius:8px;padding:10px;margin-top:8px;font-size:12.5px;white-space:pre-line}
select,input{padding:5px;border:1px solid #DCCDBB;border-radius:6px;font-size:13px}
.msg{padding:8px 12px;border-radius:8px;margin:10px 0;display:none}
.msg.good{background:#DFF2EF;display:block}.msg.bad{background:#FDECEA;display:block}
small{color:#76675A}
</style>
<h1>판단 카드 승인함
<span class="role">역할(demo):
<select id="role"><option value="card_approver">카드 승인자</option>
<option value="steward">현장 스튜어드(열람만)</option></select>
승인자 이름 <input id="actor" value="김승인" size="8"></span></h1>
<div id="msg" class="msg"></div>
<div id="list">불러오는 중…</div>
<small>승인은 환류(파라미터 기록·감사 로그)까지 한 번에 일어난다 — HITL 기본값.
반려는 사유가 재학습 재료가 된다.</small>
<script>
const REASONS=["수치 의문","근거 부족","시점 부적절","현장 사정","대안 선호","기타"];
async function load(){
  const rs=await fetch('/cards').then(r=>r.json());
  const pend=rs.filter(c=>['proposed','review'].includes(c.status));
  const el=document.getElementById('list');
  if(!pend.length){el.innerHTML='<p>대기 중인 카드가 없습니다 ✅</p>';return}
  el.innerHTML=pend.map(c=>{
    const rng=JSON.parse(c.range_json||'{}');
    const rtxt=rng.p10?`구간 P10 ${rng.p10} · P50 ${rng.p50} · P90 ${rng.p90}`:
      (rng.saving_pct?`절감 ${rng.saving_pct}%`:'');
    return `<div class="card" id="c${c.card_id}">
      <span class="kind">${c.kind}</span> <b>#${c.card_id}</b> ${c.proposal}
      <div class="range">${rtxt} · 에이전트 ${c.agent} · 승인자 ${c.approver}</div>
      <div class="narr">${(c.narrative||'').replace(/</g,'&lt;')}</div>
      <button class="why" onclick="why(${c.card_id})">왜? (근거)</button>
      <button class="ok" onclick="decide(${c.card_id},true)">승인 → 환류</button>
      <button class="no" onclick="reject(${c.card_id})">반려</button>
      <select id="r${c.card_id}">${REASONS.map(x=>`<option>${x}</option>`).join('')}</select>
      <div class="ev" id="e${c.card_id}"></div></div>`}).join('');
}
async function why(id){
  const e=document.getElementById('e'+id);
  const r=await fetch(`/cards/${id}/why`).then(r=>r.json());
  e.textContent=r.text||JSON.stringify(r,null,1).slice(0,1200);
  e.style.display='block';
}
function note(t,good){const m=document.getElementById('msg');
  m.className='msg '+(good?'good':'bad');m.textContent=t;}
async function decide(id,ok,reason=''){
  const role=document.getElementById('role').value,
        actor=document.getElementById('actor').value;
  const p=new URLSearchParams({approve:ok,actor,reason_code:reason,reason_text:''});
  const r=await fetch(`/cards/${id}/decide?`+p,{method:'POST',headers:{'X-Role':role}});
  const j=await r.json();
  if(r.ok){note(ok?`#${id} 승인 — 환류 완료: ${JSON.stringify(j.feedback?.written?.[0]||'')}`:`#${id} 반려(${reason})`,true);load();}
  else note(`거부됨: ${j.detail}`,false);
}
function reject(id){decide(id,false,document.getElementById('r'+id).value)}
load();
</script>"""
