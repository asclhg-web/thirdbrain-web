// 공통 덱 프레임워크 — 방글라데시 국영 제약사 Odoo ERP·GMP·AX 제안서
// 테마: 딥네이비 + 제약 그린(신뢰·GMP) + 골드 포인트. 16:9 13.333x7.5in
const pptxgen = require("pptxgenjs");
const F = "맑은 고딕";
const C = {
  NAVY:"14304F", NAVY2:"1F3A5F", GREEN:"0E7C6B", TEAL:"0E8F86", GOLD:"C07F1E", RED:"B03A2E",
  PURPLE:"714B67", INK:"222B36", SUB:"6B7480", LINE:"C9D3DE", BG:"FFFFFF", TINT:"F3F7F9", HEAD:"E6EEF3",
  LIGHTGREEN:"E4F3EF", LIGHTGOLD:"FBF2E3",
};
const W=13.333, H=7.5, MX=0.65;

function newDeck(){
  const p = new pptxgen();
  p.defineLayout({ name:"W", width:W, height:H }); p.layout="W";
  p.author="에이에스씨(ASC) · AX Platform"; p.company="ASC";
  return p;
}
function titleBar(s, kicker, title, tag){
  s.addShape("rect",{x:0,y:0,w:W,h:1.12,fill:{color:C.NAVY}});
  s.addShape("rect",{x:0,y:1.12,w:W,h:0.06,fill:{color:C.GREEN}});
  if(kicker) s.addText(kicker,{x:MX,y:0.14,w:9,h:0.3,fontFace:F,fontSize:11.5,color:"9FC7BD",bold:true,charSpacing:1.2});
  const tfs = title.length>46?17.5 : title.length>38?19.5 : title.length>32?22 : 24;   // 긴 제목 자동 축소(1줄 유지)
  s.addText(title,{x:MX,y:0.4,w:12.0,h:0.62,fontFace:F,fontSize:tfs,color:"FFFFFF",bold:true,valign:"middle",fit:"shrink"});
  s.addText(tag||"국영 제약사 · Odoo ERP · GMP · AX 제안",{x:W-4.9,y:0.14,w:4.25,h:0.3,fontFace:F,fontSize:9.5,color:"9FC7BD",align:"right"});
}
function foot(s,n,note){
  s.addShape("rect",{x:MX,y:H-0.5,w:W-2*MX,h:0.012,fill:{color:C.LINE}});
  s.addText(note||"에이에스씨(ASC) · AX 플랫폼 사업팀 · odooaierp.com",{x:MX,y:H-0.44,w:8,h:0.3,fontFace:F,fontSize:8.5,color:C.SUB});
  s.addText(String(n),{x:W-1.1,y:H-0.44,w:0.55,h:0.3,fontFace:F,fontSize:9.5,color:C.SUB,align:"right"});
}
function section(p, num, title, sub){
  const s=p.addSlide(); s.background={color:C.NAVY};
  s.addShape("rect",{x:0,y:H-0.9,w:W,h:0.05,fill:{color:C.GREEN}});
  s.addText(num,{x:0.9,y:2.0,w:3,h:1.0,fontFace:F,fontSize:60,bold:true,color:"9FC7BD"});
  s.addText(title,{x:0.9,y:3.05,w:11.5,h:1.0,fontFace:F,fontSize:36,bold:true,color:"FFFFFF"});
  if(sub) s.addText(sub,{x:0.92,y:4.1,w:11.5,h:0.7,fontFace:F,fontSize:15,color:"C9D9E3"});
  return s;
}
function bullets(s, items, x, y, w, o={}){
  const arr=items.map(it=>{
    const txt=typeof it==="string"?it:it.t;
    return {text:txt,options:{fontFace:F,fontSize:o.fs||13,color:o.color||C.INK,bold:typeof it==="object"&&it.b,
      bullet:{code:"2022",indent:14},paraSpaceAfter:o.sa!=null?o.sa:6,breakLine:true}};
  });
  s.addText(arr,{x,y,w,h:o.h||3.5,valign:"top",lineSpacingMultiple:o.ls||1.05});
}
function para(s, txt, x, y, w, h, o={}){
  s.addText(txt,{x,y,w,h,fontFace:F,fontSize:o.fs||13,color:o.color||C.INK,bold:o.b,italic:o.i,valign:o.valign||"top",align:o.align||"left",lineSpacingMultiple:o.ls||1.08});
}
function card(s,x,y,w,h,label,body,accent,o={}){
  s.addShape("roundRect",{x,y,w,h,rectRadius:0.07,fill:{color:o.fill||C.TINT},line:{color:C.LINE,width:0.75}});
  s.addShape("rect",{x,y,w:0.08,h,fill:{color:accent||C.GREEN}});
  s.addText(label,{x:x+0.18,y:y+0.1,w:w-0.3,h:0.38,fontFace:F,fontSize:o.lfs||13,bold:true,color:o.lcolor||C.NAVY,valign:"middle"});
  if(Array.isArray(body)) bullets(s,body,x+0.12,y+0.5,w-0.25,{fs:o.fs||10.5,sa:3,h:h-0.58});
  else s.addText(body,{x:x+0.18,y:y+0.5,w:w-0.32,h:h-0.6,fontFace:F,fontSize:o.fs||10.5,color:C.INK,valign:"top",lineSpacingMultiple:1.04});
}
function table(s, header, rows, x, y, w, colW, o={}){
  const hdr=header.map(h=>({text:h,options:{fill:o.headFill||C.NAVY,color:"FFFFFF",bold:true,fontFace:F,fontSize:o.hfs||11,align:"center",valign:"middle"}}));
  const body=rows.map((r,i)=>r.map((c,j)=>{
    const txt=typeof c==="string"?c:c.t;
    const op={fill:i%2?C.TINT:"FFFFFF",color:(typeof c==="object"&&c.color)||C.INK,fontFace:F,fontSize:o.fs||10,valign:"middle",
      align:(o.center&&o.center.includes(j))?"center":"left",bold:(typeof c==="object"&&c.b)||(o.boldCol===j)};
    return {text:txt,options:op};
  }));
  s.addTable([hdr,...body],{x,y,w,colW,rowH:o.rowH||0.34,border:{type:"solid",color:C.LINE,pt:0.5},autoPage:false});
}
function flow(s, steps, x, y, w, o={}){
  const n=steps.length, gap=0.12, bw=(w-gap*(n-1))/n, h=o.h||0.95;
  steps.forEach((t,i)=>{
    const bx=x+i*(bw+gap);
    s.addShape("roundRect",{x:bx,y,w:bw,h,rectRadius:0.08,fill:{color:(o.colors&&o.colors[i])||(i%2?C.NAVY2:C.GREEN)}});
    s.addText(t,{x:bx,y,w:bw,h,fontFace:F,fontSize:o.fs||11,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    if(i<n-1) s.addText("▶",{x:bx+bw-0.03,y,w:gap+0.06,h,fontFace:F,fontSize:9,color:C.SUB,align:"center",valign:"middle"});
  });
}
function kpiTiles(s, tiles, x, y, w, o={}){
  const n=tiles.length, gap=0.15, tw=(w-gap*(n-1))/n, h=o.h||1.55;
  tiles.forEach((t,i)=>{
    const tx=x+i*(tw+gap);
    s.addShape("roundRect",{x:tx,y,w:tw,h,rectRadius:0.08,fill:{color:C.TINT},line:{color:t.c||C.GREEN,width:1.2}});
    s.addText(t.v,{x:tx,y:y+0.12,w:tw,h:0.55,fontFace:F,fontSize:o.vfs||22,bold:true,color:t.c||C.GREEN,align:"center",valign:"middle"});
    s.addText(t.l,{x:tx+0.1,y:y+0.7,w:tw-0.2,h:h-0.78,fontFace:F,fontSize:o.lfs||10.5,color:C.INK,align:"center",valign:"top",lineSpacingMultiple:1.03});
  });
}
function note(s, txt, y, o={}){
  s.addText(txt,{x:MX,y:y,w:W-2*MX,h:o.h||0.4,fontFace:F,fontSize:o.fs||9.5,color:C.SUB,italic:true,valign:"top"});
}
module.exports={pptxgen,newDeck,F,C,W,H,MX,titleBar,foot,section,bullets,para,card,table,flow,kpiTiles,note};
