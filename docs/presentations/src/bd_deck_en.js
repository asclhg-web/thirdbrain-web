// Bangladesh state-owned pharmaceutical company — Odoo 20 ERP · GMP · AX Agents implementation proposal (EN, 39 slides)
const T = require("./bd_theme_en.js");
const {newDeck,F,C,W,H,MX,titleBar,foot,section,bullets,para,card,table,flow,kpiTiles,note} = T;
const p = newDeck();
let n=0; const pg=()=>++n;

// ───────────────────────── 1. Cover
{ const s=p.addSlide(); n++; s.background={color:C.NAVY};
  s.addShape("rect",{x:0,y:4.62,w:W,h:0.05,fill:{color:C.GREEN}});
  s.addText("PROPOSAL · ODOO 20 ERP + GMP + AX AGENTS",{x:0.9,y:1.55,w:11,h:0.35,fontFace:F,fontSize:12,color:"9FC7BD",bold:true,charSpacing:2});
  s.addText("GMP Plant Digital Transformation Proposal",{x:0.9,y:1.95,w:11.8,h:0.95,fontFace:F,fontSize:38,bold:true,color:"FFFFFF"});
  s.addText("Odoo 20 ERP  ·  GMP Data Integrity Layer  ·  AX (AI Transformation) Agents",{x:0.92,y:2.95,w:11.8,h:0.5,fontFace:F,fontSize:17,color:"E6C9A8",bold:true});
  s.addText("Prepared for: State-Owned Pharmaceutical Company, Bangladesh (presumed Essential Drugs Company Ltd.)",{x:0.92,y:3.7,w:11.5,h:0.5,fontFace:F,fontSize:16,color:"C9D9E3"});
  s.addText("From raw-material receipt to batch release — one ledger, tamper-proof records, human-approved AI",{x:0.92,y:4.85,w:11.8,h:0.45,fontFace:F,fontSize:14,color:"AEC2DA"});
  s.addText("October 2026  ·  ASC (AX Platform) · AX Platform Business Team  ·  odooaierp.com  ·  asclhg@gmail.com",{x:0.92,y:6.55,w:11.5,h:0.4,fontFace:F,fontSize:11.5,color:"8FA6BF"});
  s.addText("Preliminary proposal (outline) · Detailed scope, schedule and cost to be finalized after requirements analysis",{x:0.92,y:6.95,w:11.5,h:0.3,fontFace:F,fontSize:9.5,color:"6F8AA6",italic:true});
}

// ───────────────────────── 2. Contents
{ const s=p.addSlide(); titleBar(s,"CONTENTS","Contents"); const k=pg();
  const toc=[["1","Executive Summary · Client Understanding (Bangladesh Pharma Industry · State-Owned Manufacturer)"],["2","Background — Why a GMP Plant Must Digitalize Now"],
  ["3","GMP Regulatory Requirements → ERP Requirements (WHO · EU Annex 11 · 21 CFR Part 11 · ALCOA+)"],["4","Pharmaceutical Manufacturing Process and System Roles (ERP · MES/eBR · LIMS · QMS)"],
  ["5","Odoo 20 — New Features and Pharma/GMP Modules"],["6","GMP Gap Analysis · GMP Layer Design · CSV Validation"],
  ["7","AX Architecture — Agent Portfolio · Odoo 20 Connectivity · Ontology"],["8","International Benchmarks (Odoo in Pharma · Global eBR · Lessons from State-Owned Peers)"],
  ["9","Requirements · Localization/Infrastructure · Roadmap · Risks · KPIs · Governance"]];
  let y=1.45; toc.forEach(([a,b])=>{ s.addShape("roundRect",{x:MX,y,w:0.5,h:0.5,rectRadius:0.06,fill:{color:C.GREEN}});
    s.addText(a,{x:MX,y,w:0.5,h:0.5,fontFace:F,fontSize:17,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(b,{x:MX+0.7,y,w:11,h:0.5,fontFace:F,fontSize:14.5,color:C.INK,valign:"middle"}); y+=0.6; });
  foot(s,k);
}

// ───────────────────────── 3. Executive summary
{ const s=p.addSlide(); titleBar(s,"EXECUTIVE SUMMARY","At a Glance — Odoo 20 Core + GMP Layer + AX Agents"); const k=pg();
  para(s,"We consolidate your GMP plant operations (raw materials → production → QC/QA → release) on a single Odoo 20 ledger, reinforce the data integrity (ALCOA+), audit trail, electronic signatures and validation that regulators demand through a dedicated 'GMP Layer', and add human-approved AX agents on top to structurally reduce stock-outs, deviations and release delays.",MX,1.35,12,0.85,{fs:13});
  card(s,MX,2.3,3.9,2.55,"① Odoo 20 ERP Core",["GA September 2026 · standard support to September 2029","Purchase · Inventory (lot/expiry/FEFO) · Manufacturing · Quality · Maintenance · PLM · Accounting","Automatic lot creation · unified traceability report · recall tracing (new)","Offline mode — resilient to power cuts and unstable networks"],C.NAVY2);
  card(s,MX+4.05,2.3,3.9,2.55,"② GMP Data Integrity Layer",["Field-level tamper-proof audit trail with mandatory reason","Record e-signature and re-authentication (Part 11 / Annex 11 §14)","eBMR/BPR · Deviation/CAPA/Change Control QMS · SOP/Training","CSV package (GAMP 5 · IQ/OQ/PQ) — a first-class WBS deliverable"],C.GREEN);
  card(s,MX+8.1,2.3,3.9,2.55,"③ AX Agents (Human-Approved)",["Connected via Odoo 20 native MCP and JSON-2 API","Demand/production planning · material replenishment · quality deviation · predictive maintenance · batch release · audit response agents","Decision card → approval inbox → human approval → written to Odoo","Numbers are computed by the graph; the LLM only narrates"],C.GOLD);
  kpiTiles(s,[{v:"−30~50%",l:"Batch release cycle time\n(industry 12–18 days → best 3–5)"},{v:"−80%",l:"Batch record documentation errors\n(eBR benchmark)"},{v:"≥99%",l:"Inventory accuracy ·\n100% FEFO compliance"},{v:"100%",l:"Pre-release audit-trail review ·\nzero shared accounts"}],MX,5.05,12,{h:1.45,vfs:20,lfs:10});
  note(s,"Targets are illustrative, based on global eBR/ERP benchmarks; 6- and 12-month targets are fixed after baseline measurement at kick-off.",6.6);
  foot(s,k);
}

// ───────────────────────── 4. Client understanding ① Industry
{ const s=p.addSlide(); titleBar(s,"01. CLIENT UNDERSTANDING","Bangladesh Pharma Industry — Self-Sufficient, Growing, Regulation Maturing"); const k=pg();
  kpiTiles(s,[{v:"US$ 3.3B",l:"Domestic market size\n(MAT Q2 2026, +10.6%)"},{v:"98%",l:"Drug self-sufficiency\n(~85% of APIs imported)"},{v:"US$ 238M",l:"Exports FY2025-26\n(130+ countries)"},{v:"ML2 → ML3",l:"DGDA WHO regulatory maturity\n(ML3 target May 2027)"},{v:"Nov 2026",l:"LDC graduation →\nTRIPS pharma waiver ends"}],MX,1.4,12,{h:1.5,vfs:19,lfs:9.5});
  table(s,["Area","Current Status (as researched)","Implication for the Proposal"],[
    ["Market structure","Top 10 ≈ 75% — Square 17%, Incepta 12.6%, Beximco 9.8%, Renata 5.7%, Eskayef 4.9%","Private leaders run SAP (Incepta, 2021) and Oracle EBS (Beximco) — the state-owned firm needs equivalent controls"],
    ["Regulation","Drugs & Cosmetics Act 2023 · National Drug Policy 2016 (WHO certification, PIC/S accession goals) · DGDA inspections based on WHO GMP","Designing to WHO GMP + PIC/S PI 041 data integrity supports ML3 and international certification"],
    ["GMP enforcement","2014–16: 84 firms assessed → 20–34 production halts; 2009–23: 45 licences revoked (penicillin, cephalosporin, oncology, hormones)","Batch record reliability, cross-contamination and QC capability are recurring findings → prioritize eBMR, QC and quarantine control"],
    ["Infrastructure & policy","3–4 h daily outages in industrial belts (2026) · Data Protection Ordinance 2025 (in-country hosting) · national sovereign cloud (NDC Tier-IV) · e-GP mandatory","Offline resilience, on-premise/sovereign cloud and e-GP integration are mandatory requirements"],
    ["Serialization","No confirmed DGDA mandate · Renata adopted voluntarily · India and Pakistan mandating from 2026","Pre-build the GS1 batch/serial data model — a differentiator ahead of mid-term regulation"],
  ],MX,3.1,12,[1.5,5.7,4.8],{fs:9.5,rowH:0.55,boldCol:0});
  note(s,"Sources: IQVIA (secondary citation), EPB, DGDA, TBS, Daily Star, etc. (see Appendix). Figures should be re-verified against primary sources before final submission.",6.6);
  foot(s,k);
}

// ───────────────────────── 5. Client understanding ② EDCL
{ const s=p.addSlide(); titleBar(s,"01. CLIENT UNDERSTANDING","State-Owned Manufacturer Profile — Essential Drugs Company Ltd. (EDCL)"); const k=pg();
  para(s,"Bangladesh's only state-owned pharmaceutical manufacturer is EDCL, 100% government-owned under the Ministry of Health and Family Welfare (Government Pharmaceutical Laboratory 1962 → EDCL 1983). Even if your company is not EDCL, the same regulatory and infrastructure conditions apply, so the design in this proposal remains valid.",MX,1.35,12,0.7,{fs:12});
  card(s,MX,2.15,5.9,2.2,"Organization & Business",["Tejgaon (Dhaka) main plant · Bogura · Gopalganj (3rd plant, Tk 800 crore) · Khulna latex plant","~140 products — IV fluids, iron supplements, hormones, penicillins, contraceptives, antibiotics","Supplies ~80% of public-hospital drug demand (mandatory purchase, no tender) · target to cover 70%→90% of government demand","New management (Jan 2025) — tender transparency, workforce efficiency, up to 50% price cuts on 33 items"],C.NAVY2,{fs:10});
  card(s,MX+6.1,2.15,5.9,2.2,"GMP & Governance Issues",["Ageing facilities → cGMP non-compliance → history of certifications withdrawn by WHO and other international bodies","CAG audit (2019–21): 32 irregularities, Tk 477 crore loss → High Court and ACC investigations","Prolonged antibiotic production stoppage due to tender disputes","→ Internal control, procurement transparency and audit trail are the ERP's top-priority value"],C.RED,{fs:10});
  card(s,MX,4.5,5.9,2.0,"Investments & Procurement in Progress (★ Proposal Timing)",["★ May 2026: EDCL EOI for ERP design, development & implementation (QCBS, self-funded, national consulting firms; finance·HR·procurement·planning·inventory·sales·QC·manufacturing·PM)","★ ADB US$336.5M vaccine & therapeutics manufacturing and regulatory strengthening project (Nov 2023) — WHO GMP vaccine plant (target 2032) + DGDA ML3","Tejgaon → Manikganj relocation (ECNEC, Tk 1,905 crore) / Munshiganj integrated complex concept"],C.GOLD,{fs:10});
  card(s,MX+6.1,4.5,5.9,2.0,"Three Axes of Our Positioning",["① Partner to complement the in-progress ERP with a GMP layer (audit trail, eBMR, QMS, serialization)","② Digital GMP (MES/eBR, LIMS, QMS) supplier for the ADB vaccine plant — international competitive track","③ Support for DGDA ML3 and WHO GMP re-certification (data integrity package)"],C.GREEN,{fs:10});
  note(s,"EOI award result and your exact scale/products are unconfirmed — see the pre-kick-off checklist (final slide).",6.6);
  foot(s,k);
}

// ───────────────────────── 6. Background
{ const s=p.addSlide(); titleBar(s,"02. BACKGROUND","Background — Five Reasons a GMP Plant Must Digitalize Now"); const k=pg();
  const items=[["GMP Re-certification & ML3","Paper batch records and scattered data cannot demonstrate WHO/PIC/S data integrity (ALCOA+) → tamper-proof electronic records are a precondition for certification",C.RED],
   ["ERP Procurement Under Way","The May 2026 ERP EOI demands finance, procurement, inventory, QC and manufacturing at once. Generic ERP lacks GMP controls (audit trail, e-signature, CSV) → complementary design required",C.GOLD],
   ["ADB Vaccine Plant","The new WHO GMP plant (2032) presupposes eBR, LIMS, QMS and serialization from the design stage — it must extend on the same data model as the existing plants",C.TEAL],
   ["Governance & Transparency","Audit findings (Tk 477 crore) and tender disputes → approval workflows, e-GP integration and immutable logs so that 'structure, not people, enforces the rules'",C.NAVY2],
   ["LDC Graduation & Exports","TRIPS waiver ends Nov 2026 → competitiveness in off-patent essential medicines and exports will be decided by cost, quality and traceability data",C.PURPLE]];
  let y=1.4; items.forEach(([t,b,c],i)=>{ s.addShape("roundRect",{x:MX,y,w:0.55,h:0.9,rectRadius:0.06,fill:{color:c}});
    s.addText(String(i+1),{x:MX,y,w:0.55,h:0.9,fontFace:F,fontSize:20,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(t,{x:MX+0.7,y,w:2.6,h:0.9,fontFace:F,fontSize:13.5,bold:true,color:C.NAVY,valign:"middle"});
    s.addText(b,{x:MX+3.4,y,w:8.6,h:0.9,fontFace:F,fontSize:11,color:C.INK,valign:"middle"}); y+=1.0; });
  s.addShape("roundRect",{x:MX,y:6.45,w:12,h:0.45,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("Conclusion: not an 'ERP project' but GMP data integrity + control + intelligence on one platform — the path that unlocks re-certification and profitability together.",{x:MX+0.2,y:6.45,w:11.6,h:0.45,fontFace:F,fontSize:11.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 7. GMP regulation → ERP requirements
section(p,"03","GMP Regulatory Requirements → ERP Requirements","WHO · EU GMP Annex 11/15 · FDA 21 CFR Part 11 · PIC/S PI 041 · GAMP 5 · ALCOA+"); n++;
{ const s=p.addSlide(); titleBar(s,"03. GMP → ERP","What Regulations Demand of the ERP — Data Integrity and Validation"); const k=pg();
  table(s,["Standard","Core Requirements","ERP Design Requirements (reflected in this proposal)"],[
    ["WHO GMP TRS 986 Annex 2 · TRS 1033 Annex 4 (Data Integrity, 2021)","Batch manufacturing/packaging records (theoretical vs. actual quantity, yield reconciliation, date/time, responsible person) · appropriate control and validation of computerized systems","Auto-generated BMR/BPR · yield reconciliation · step-level signatures · system validation documentation"],
    ["EU GMP Annex 11 (2011 → July 2025 draft revision, 5→19 pages)","§9 audit trail (who, what, old/new value, when, why — automatic) · §12 security (RBAC) · §14 e-signature (permanently linked to record) · §15 batch release (QP only)","Field-level old/new log with mandatory reason · individual accounts + MFA · signature re-authentication · QA-only release rights"],
    ["EU GMP Annex 15 · GAMP 5 (2nd ed.)","Risk-based validation; VMP, URS, IQ/OQ/PQ; configured COTS = Cat. 4, custom = Cat. 5","CSV package as a first-class WBS deliverable · minimize customization to shrink Cat. 5 scope"],
    ["FDA 21 CFR Part 11","§11.10: 11 controls for closed systems (validation, accurate copies, audit trail, access, training, signature accountability) · Subpart C e-signatures (two components, unique)","Audit trail independent of users and non-disableable · e-signature ID + password re-authentication · training records"],
    ["PIC/S PI 041-1 (2021) · ALCOA+","Data governance · Attributable / Legible / Contemporaneous / Original / Accurate + Complete / Consistent / Enduring / Available","ALCOA+ control mapping applied — see next slide"],
    ["EU GMP Ch. 1/4/8","PQS and CAPA · batch document retention (expiry + 1 year or QP certification + 5 years, whichever is longer) · complaints, recalls, CAPA effectiveness","Deviation/CAPA/change control QMS · retention policy and archiving · instant recall impact scoping"],
  ],MX,1.4,12,[3.0,4.8,4.2],{fs:9.5,rowH:0.72,boldCol:0});
  note(s,"Important notice: Odoo is not a product 'certified' for Part 11 / Annex 11 compliance. Compliance is achieved through configuration + GMP Layer + CSV + SOPs/training — all of which are within the scope of this proposal.",6.5,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 8. ALCOA+
{ const s=p.addSlide(); titleBar(s,"03. GMP → ERP","ALCOA+ Data Integrity → ERP Control Mapping"); const k=pg();
  table(s,["Attribute","Meaning","ERP · GMP Layer Controls","Verification (CSV)"],[
    ["Attributable","Who did it and when","Individual accounts (no sharing) · e-signature · user attribution in audit trail","OQ: per-account log check"],
    ["Legible","Permanently readable","Readable reports · archive legibility · readability after upgrades","PQ: retrieve historical batches"],
    ["Contemporaneous","Recorded at time of activity","Server timestamps (single NTP time source) · shop-floor tablet entry · reason required for late entries","OQ: time-sync verification"],
    ["Original","Original or certified copy","Source-system records · minimal transcription (LIMS, balance interfaces)","IQ/OQ: interfaces"],
    ["Accurate","Free of errors","Range, unit and mandatory-value checks · old/new on edits · double verification","OQ: boundary-value tests"],
    ["+ Complete","Everything, incl. retests","Failed tests retained · no deletion · append-only","OQ: blocked delete attempts"],
    ["+ Consistent","Chronologically consistent","State-transition control (quarantine → testing → release) · enforced workflows","OQ: blocked state bypass"],
    ["+ Enduring","Retained for the full period","Backup/restore tests · retention policy (expiry + 1 year) · migration verification","PQ: restore rehearsal"],
    ["+ Available","Accessible on demand","Search, reports, inspector read access · offline queue sync verification","PQ: inspection scenario"],
  ],MX,1.4,12,[1.6,2.4,5.2,2.8],{fs:9.8,rowH:0.5,boldCol:0});
  note(s,"Sources: PIC/S PI 041-1, WHO TRS 1033 Annex 4, TGA ALCOA ↔ Annex 11 mapping. Controls and verification are within this proposal's GMP Layer and CSV scope.",6.5);
  foot(s,k);
}

// ───────────────────────── 9. Pharma process → ERP
section(p,"04","Pharmaceutical Manufacturing Process and System Roles","From raw-material receipt to batch release — which records live where"); n++;
{ const s=p.addSlide(); titleBar(s,"04. PROCESS","11-Step Pharma Manufacturing Process — GMP Points and Odoo Mapping (OSD)"); const k=pg();
  flow(s,["① Receipt · Lot","② Quarantine · QC","③ Material Issue","④ Dispensing","⑤ Granulation · Blending","⑥ Compression · Coating","⑦ Packaging","⑧ Finished QC","⑨ QA Release","⑩ Warehouse · Distribution","⑪ Post-Market"],MX,1.35,12,{h:0.7,fs:8.5});
  table(s,["Step","GMP Requirement Points","Odoo 20 + GMP Layer Mapping"],[
    ["①–③ Materials","Order only from approved suppliers · immediate quarantine · spec-based QC · status changed by QC/QA only","Approved-supplier check on PO · lot/mfg date/expiry/retest date mandatory · automatic quarantine location · incoming QCP · e-signed status transition · supplier quality rate (new)"],
    ["④ Dispensing","Approved formula · FEFO · calibrated balances · double verification","BOM frozen at MO creation · FEFO lot reservation · balance ID, operator/verifier recorded · block equipment with expired calibration (layer)"],
    ["⑤–⑥ Processing","Process parameters · line clearance · IPC · yield","Work-order checklists · measurement-type quality checks (out-of-range alerts) · continuous production (new) · yield reconciliation · deviation logging (QMS)"],
    ["⑦ Packaging","Packaging order · label reconciliation · serialization","Packaging MO/BPR · label issue/return reconciliation · GS1 master data + serialization system interface"],
    ["⑧–⑨ QC/QA","Spec testing · retained samples · BMR review · deviation closure · audit-trail review · QP certification","Finished-product QCP · LIMS integration · release checklist + e-signature · QA-only rights · unified traceability report (new)"],
    ["⑩–⑪ Distribution & Post-Market","FEFO dispatch · distribution records · complaints/recalls · PQR","FEFO enforced · lot → delivery-line recall tracing (new) · complaint → investigation → CAPA · PQR data extraction"],
  ],MX,2.25,12,[1.5,4.3,6.2],{fs:9.5,rowH:0.6,boldCol:0});
  note(s,"Key perspective: the essence of a batch record is a 'material ledger' that records what was input, what happened, what was measured, what moved on and where the remainder went — and reconciles it.",6.5);
  foot(s,k);
}

// ───────────────────────── 10. System role boundaries
{ const s=p.addSlide(); titleBar(s,"04. PROCESS","System Role Boundaries — ERP · MES/eBR · LIMS · QMS · Serialization · AX"); const k=pg();
  const cols=[["Odoo 20 ERP (L4)","Owner of record",["Master data · BOM/formula","MPS/MRP · purchasing · inventory (lot/status/FEFO)","Manufacturing orders · work orders · costing","Quality disposition · maintenance · PLM","Accounting · procurement (e-GP) · KPIs"],C.NAVY2],
   ["MES / eBR (L3)","Execution record",["Step-by-step electronic batch record","Equipment data · line clearance","IPC · reconciliation","Small sites: replaced by Odoo work orders + quality checks + eBMR module","Large/sterile sites: dedicated MES roadmap"],C.GREEN],
   ["LIMS · QMS","Testing & quality systems",["Samples · tests · OOS · stability (LIMS)","Deviation · CAPA · change · documents · training (QMS)","Not in standard Odoo → GMP Layer or external integration","ERP receives pass/fail, CoA and closure status"],C.PURPLE],
   ["Serialization","Traceability",["GTIN + serial + lot + expiry","Aggregation (SSCC) · EPCIS","ERP provides master data and dispatch linkage","Pre-built for a future DGDA mandate"],C.GOLD],
   ["AX Agents (L5)","Intelligence & decision support",["ERP/MES/LIMS events → features","Knowledge graph (ontology)","Decision cards → human approval","Writes only via approved server actions"],C.TEAL]];
  const cw=2.3, gap=0.125; cols.forEach((c,i)=>{ const x=MX+i*(cw+gap);
    s.addShape("roundRect",{x,y:1.4,w:cw,h:0.75,rectRadius:0.07,fill:{color:c[3]}});
    s.addText(c[0],{x,y:1.4,w:cw,h:0.45,fontFace:F,fontSize:12,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(c[1],{x,y:1.8,w:cw,h:0.3,fontFace:F,fontSize:9.5,color:"E6EEF3",align:"center"});
    s.addShape("roundRect",{x,y:2.25,w:cw,h:3.5,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1}});
    bullets(s,c[2],x+0.08,2.35,cw-0.15,{fs:9.8,sa:4,h:3.3}); });
  s.addShape("roundRect",{x:MX,y:5.95,w:12,h:0.85,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"Principles  ",options:{bold:true,color:C.NAVY}},{text:"① One owner of record (the ERP ledger)  ② GMP records are created only where e-signatures and audit trails attach  ③ AI reads first; writes only through human-approved server actions  ④ Interfaces (LIMS, balances, labels, serialization) eliminate transcription to secure Original and Accurate",options:{color:C.INK}}],
    {x:MX+0.2,y:5.95,w:11.6,h:0.85,fontFace:F,fontSize:10.5,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 11. Odoo 20 new features
section(p,"05","Odoo 20 — New Features and Pharma/GMP Application","GA September 2026 · AI Agents · native MCP · enhanced traceability · offline mode"); n++;
{ const s=p.addSlide(); titleBar(s,"05. ODOO 20","Odoo 20 (GA 24 Sept 2026) — New Features Relevant to This Proposal"); const k=pg();
  kpiTiles(s,[{v:"Odoo 20",l:"GA 24 Sept 2026\nStandard support to Sept 2029"},{v:"MCP",l:"Native MCP server\n(OAuth 2.1 · API keys)"},{v:"AI Agents",l:"Automation & scheduled runs\n8 Skills (create/edit records)"},{v:"JSON-2 API",l:"Recommended external API\n(XML/JSON-RPC deprecated)"},{v:"Offline",l:"Offline mode\n(local queue → sync, 2 GB)"}],MX,1.4,12,{h:1.45,vfs:18,lfs:9.5});
  table(s,["Area","Odoo 20 New / Enhanced Features","Pharma · GMP Value"],[
    ["AI & Agents","Agents invoked by automation rules and schedules · automated chat audit log · create records from uploaded PDF instructions · self-improvement · choice of AI provider · IAP credit billing","Automate deviation drafts, audit Q&A and SOP Q&A — with every run fully auditable"],
    ["MCP Server","/mcp endpoint · OAuth 2.1 or MCP-scoped API keys · 5 default read tools · server actions exposed as MCP tools · operates within user permissions","Official channel for external AX agents — controlled via a least-privilege dedicated user"],
    ["Manufacturing","Continuous production (next step starts once partial qty is done) · work-order Kanban/Gantt · automatic backorder planning · MO split · single 'Produce' on Shop Floor · WIP costing","Campaign production and line balancing · shop-floor tablet execution records"],
    ["Inventory & Traceability","Lot always auto-created at MO close · delivery lines shown on lot 'Transfers' (targeted recall) · unified upstream/downstream traceability report · stock ageing","Prevents unassigned lots · instant recall impact scoping · proven genealogy"],
    ["Quality (Enterprise)","Check bypass restricted to quality managers · failed items moved to a 'failure location' · supplier quality rate (%) in Purchase","Stronger role-based control · automated non-conforming quarantine · supplier qualification evidence"],
    ["Maintenance · PLM · Docs","Maintenance Gantt (per equipment) · PLM Compare BoMs · Documents group permissions · Sign auto-signature requests (automation rules)","Calibration/PM planning · formula change control (ECO) · automatic signature requests for SOP approval"],
  ],MX,3.0,12,[1.7,6.0,4.3],{fs:9.3,rowH:0.47,boldCol:0});
  note(s,"Sources: odoo.com release notes/docs (search excerpts) cross-checked with partner blogs. Pharma scenarios (Quality, PLM, Shop Floor, Documents, Sign, Studio, AI/MCP) require Enterprise. Technical requirements: Python ≥ 3.12 · PostgreSQL ≥ 16.",6.45,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 12. Pharma module map
{ const s=p.addSlide(); titleBar(s,"05. ODOO 20","Pharma Odoo Module Map — What Standard Covers · What the Layer Adds"); const k=pg();
  const mods=[["Purchase","Approved suppliers · PO approval workflow · supplier quality rate · import documents · e-GP integration",C.NAVY2,"Standard + configuration"],
   ["Inventory","Lots/serials · 4 expiry-related dates · FEFO · quarantine locations · traceability report · barcodes",C.NAVY2,"Standard + configuration"],
   ["Manufacturing (MRP) · Shop Floor","BOM/formula · MPS · work orders · tablet execution · continuous production · yield · WIP",C.NAVY2,"Standard + eBMR layer"],
   ["Quality","QCP (incoming/in-process/final) · pass-fail/measurement · Quality Alerts · failure location · manager-only bypass",C.GREEN,"Standard + QMS layer"],
   ["Maintenance","Preventive/corrective maintenance · Gantt · MTBF/MTTR · calibration intervals",C.GREEN,"Standard + calibration-block layer"],
   ["PLM","Staged ECO approvals · BOM versions · Compare BoMs → formula change control",C.GREEN,"Standard + change-control link"],
   ["Documents · Sign · Knowledge","SOP versioning · group permissions · e-signature (SES) · internal knowledge Q&A",C.PURPLE,"Standard + Part 11 signature layer"],
   ["Accounting","AI invoice recognition · bank reconciliation · journal hash immutability · Mushak VAT · FY July–June",C.PURPLE,"Standard + localization"],
   ["AI · MCP · Studio","AI agents/Skills · AI fields · MCP server · automation rules · webhooks",C.GOLD,"AX connection surface"]];
  const cw=3.9, ch=1.45, gx=0.15, gy=0.15;
  mods.forEach((m,i)=>{ const col=i%3,row=Math.floor(i/3); const x=MX+col*(cw+gx), y=1.4+row*(ch+gy);
    s.addShape("roundRect",{x,y,w:cw,h:ch,rectRadius:0.07,fill:{color:C.TINT},line:{color:m[2],width:1.2}});
    s.addShape("rect",{x,y,w:0.08,h:ch,fill:{color:m[2]}});
    s.addText(m[0],{x:x+0.18,y:y+0.08,w:cw-0.3,h:0.35,fontFace:F,fontSize:12,bold:true,color:C.NAVY});
    s.addText(m[1],{x:x+0.18,y:y+0.45,w:cw-0.3,h:0.65,fontFace:F,fontSize:9.8,color:C.INK,valign:"top"});
    s.addText(m[3],{x:x+0.18,y:y+ch-0.33,w:cw-0.3,h:0.28,fontFace:F,fontSize:9,bold:true,color:m[2]}); });
  s.addShape("roundRect",{x:MX,y:6.25,w:12,h:0.6,rectRadius:0.06,fill:{color:C.LIGHTGOLD}});
  s.addText("Edition & hosting recommendation: Odoo Enterprise (Custom) · on-premise or Odoo.sh — SaaS auto-upgrades make re-validation hard to control and are unsuitable for regulated environments. Consider Light User licences for shop-floor staff to reduce cost.",{x:MX+0.2,y:6.25,w:11.6,h:0.6,fontFace:F,fontSize:10.5,color:C.INK,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 13. GMP gap analysis
section(p,"06","GMP Gap Analysis · GMP Layer · CSV","An honest gap → a designed reinforcement → verifiable evidence"); n++;
{ const s=p.addSlide(); titleBar(s,"06. GAP ANALYSIS","Standard Odoo vs. GMP Requirements — Gaps and Reinforcements"); const k=pg();
  table(s,["#","Gap (limits of standard Odoo)","Regulatory Basis","Reinforcement (GMP Layer)","Type"],[
    ["G1","Audit trail: Chatter tracks only tracked fields, is lost on delete, has no mandatory reason or review workflow; hash immutability only in Accounting","Annex 11 §9 · Part 11 §11.10(e)","OCA auditlog + custom: field-level old/new, UTC, user, mandatory reason; append-only; no deletion; pre-release review workflow","Cat. 5"],
    ["G2","E-signature: Sign is a document-level SES — no record re-authentication, signature meaning or permanent linkage","Annex 11 §14 · Part 11 Subpart C","Record e-signature module: ID + password re-authentication, signature meaning (performed/reviewed/approved), sealed metadata, invalidated on change","Cat. 5"],
    ["G3","eBMR/BPR: the MO printout is not a structured batch record","WHO §15.25–30","eBMR layer (based on partner module): step-level process, IPC, reconciliation, step signatures, deviation links, QA approval","Cat. 4/5"],
    ["G4","QMS: Quality Alert is ticket-level — no deviation/CAPA/change-control workflow","EU Ch. 1 · Ch. 8","QMS layer: deviation → classification → RCA → CAPA → effectiveness / change request → impact assessment → approval → re-validation","Cat. 5"],
    ["G5","No validation package — Odoo is not a GxP-certified product","Annex 11 §4 · Annex 15 · GAMP 5","CSV project: VMP, URS, risk assessment, FS/CS, IQ/OQ/PQ, traceability matrix · supplier assessment (Odoo SA, partners)","Deliverable"],
    ["G6","Annual major releases and SaaS auto-updates → re-validation hard to control","Annex 11 §10/§11","On-premise/Odoo.sh · change-control procedure · per-release impact assessment and regression tests · periodic review (annual)","Operations"],
    ["G7","No SOP lifecycle, forced retraining or blocking of equipment with expired calibration","EU Ch. 2/3/4","Documents + Sign approval flow · training matrix, untrained users blocked from process steps · calibration-expiry blocking rule","Cat. 4/5"],
    ["G8","No serialization (serial generation, aggregation, EPCIS)","GS1 · national T&T rules","Integration with an external serialization system (master data, dispatch) · pre-built GS1 data model","Interface"],
  ],MX,1.4,12,[0.5,4.0,2.0,4.6,0.9],{fs:9,rowH:0.55,center:[0,4]});
  note(s,"Cat. 4 (configured) / Cat. 5 (custom) follow GAMP 5 classification — customization is minimized to control validation cost. No public Part 11-grade Odoo case at a large GMP finished-dosage plant was identified, so this layer and the CSV are the keys to success.",6.45,{h:0.5});
  foot(s,k);
}

// ───────────────────────── 14. GMP layer design
{ const s=p.addSlide(); titleBar(s,"06. GMP LAYER","GMP Data Integrity Layer Design — Six Components"); const k=pg();
  const L=[["Audit Trail Engine",["Logs every change to GMP models (lots, moves, MOs, checks, BOMs, specs, suppliers) with old/new, UTC, user and reason","Append-only table · cannot be deleted or disabled · independent of users","Pre-release 'audit trail reviewed' check · readable report · retention = record retention period"],C.GREEN],
   ["Electronic Signature",["ID + password re-authentication at signing (two components) · signature meaning (performed/reviewed/approved) · timestamp","Permanently bound to the record; invalidated if the record changes","Batch release restricted to QA/QP roles — Annex 11 §15"],C.NAVY2],
   ["eBMR / BPR",["Approved master formula → electronic record auto-generated per batch","Dispensing · IPC · process parameters · yield reconciliation · line clearance","Step signatures · deviation links · QA review · printed copy = electronic copy"],C.TEAL],
   ["QMS (Deviation · CAPA · Change)",["Deviation → classification → root cause → CAPA → effectiveness check","Change request → impact assessment (re-validation?) → approval → implementation → closure","Linked to batches, equipment, documents, suppliers · metrics (closure time, recurrence rate)"],C.PURPLE],
   ["Material Status · FEFO · Calibration",["Quarantine / under test / released / rejected — changed by QC/QA only","System blocks issue and dispatch of quarantined, expired or retest-overdue lots","Blocks equipment/balances with expired calibration · blocks POs to non-approved suppliers"],C.GOLD],
   ["SOP · Training · Retention",["SOP draft → review → approval (e-signature) → effective → training → retirement · only effective versions visible","Role-based training matrix · retraining tasks on revision · untrained users blocked from process steps","Backup/restore tests · archiving · retention of expiry + 1 yr / QP certification + 5 yrs"],C.RED]];
  L.forEach((l,i)=>{ const col=i%3,row=Math.floor(i/3); card(s,MX+col*4.05,1.4+row*2.5,3.9,2.35,l[0],l[1],l[2],{fs:9.6}); });
  note(s,"Implementation principle: prefer OCA and proven partner modules and minimize customization — shrinking the GAMP Cat. 5 scope keeps validation cost and duration under control.",6.45);
  foot(s,k);
}

// ───────────────────────── 15. CSV
{ const s=p.addSlide(); titleBar(s,"06. CSV / CSA","CSV Plan — Complete Before Go-Live, Re-Validate on Every Upgrade"); const k=pg();
  flow(s,["VMP\nValidation Master Plan","URS\nUser Requirements","Risk Assessment\nGAMP Cat. 4/5","FS / CS\nFunctional & Config Specs","IQ\nInstallation Qualification","OQ\nOperational Qualification","PQ\nPerformance Qualification","Traceability Matrix\n· Validation Report"],MX,1.4,12,{h:0.95,fs:9.5});
  card(s,MX,2.6,3.9,2.3,"Scope & Classification",["Standard configuration (purchase, inventory, mfg, quality, maintenance, accounting) = Cat. 4 → configuration verification","GMP Layer (audit trail, e-signature, eBMR, QMS) = Cat. 5 → design and code review, full testing","Interfaces (LIMS, balances, labels, serialization, e-GP) = separate IQ/OQ","Supplier assessment: Odoo SA · implementation partner · module vendors"],C.NAVY2,{fs:9.8});
  card(s,MX+4.05,2.6,3.9,2.3,"Standards & Methods",["Designed to the EU Annex 11 2025 draft revision (strengthened audit trail)","FDA CSA (2025) risk-based: intended use → risk → assurance activities → objective evidence","PIC/S PI 041 data integrity · ALCOA+ checklist","WHO TRS 1019 Appendix 5 computerized system validation"],C.GREEN,{fs:9.8});
  card(s,MX+8.1,2.6,3.9,2.3,"Operational Controls",["Change control: config, permission and BOM-rule changes = ticket, approval, impact assessment","Release management: fixed version on-prem/Odoo.sh · annual periodic review · regression tests and partial re-validation on major upgrades","Incident management & BCP: backup/restore rehearsals · offline-queue verification for power cuts","Periodic audit-trail review SOP"],C.GOLD,{fs:9.8});
  table(s,["Deliverable","Content","Approval"],[
    ["VMP · URS · Risk Assessment","Scope, approach, schedule / requirements by function (GMP flags) / risk and test depth per function","Client QA sign-off"],
    ["FS/CS · Traceability Matrix","Design and configuration specifications / URS ↔ FS ↔ test-case mapping","Client QA sign-off"],
    ["IQ/OQ/PQ Protocols & Reports","Installation verification / function, boundary, security, audit-trail and signature tests / real-business scenario (one batch cycle)","Client QA & QP sign-off"],
    ["Validation Summary Report · SOP Set","Deviations, residual risk, go-live approval / system operation, change, backup and audit-trail review SOPs","Management & QA sign-off"],
  ],MX,5.05,12,[3.0,6.6,2.4],{fs:9.3,rowH:0.36,boldCol:0});
  foot(s,k);
}

// ───────────────────────── 16. To-Be architecture L1–L5
section(p,"07","AX Architecture","Transactions → Odoo 20 ledger → events & features → ontology & knowledge graph → agents — intelligence that humans approve"); n++;
{ const s=p.addSlide(); titleBar(s,"07. AX ARCHITECTURE","To-Be Architecture — Five Layers, One Trunk (GMP Layer Runs Through All)"); const k=pg();
  const layers=[["L5  AX Agents · Control Tower","Demand/production planning · material replenishment · quality deviation · predictive maintenance · batch release assistant · audit response → decision card → approval inbox (human) → written to Odoo",C.GOLD],
   ["L4  Ontology · Knowledge Graph","Semantically links products, formulas, batches, lots, processes, equipment, tests, deviations, suppliers and SOPs — evidence ladder · rule promotion/demotion loop",C.PURPLE],
   ["L3  Events · Features · Learning","Receipt, inspection, work, deviation and dispatch events → item × line × period features → demand forecasting, anomaly detection and predictive maintenance models (model cards · 30 regression checks)",C.TEAL],
   ["L2  Odoo 20 Single Ledger + GMP Layer","Purchase · inventory · manufacturing · quality · maintenance · PLM · accounting — a single PostgreSQL record + audit trail, e-signature, eBMR, QMS, status enforcement",C.NAVY2],
   ["L1  Transaction Sources","Receipts · QC results (LIMS) · dispensing (balances) · work orders (tablets) · IPC · packaging/labels · serialization · equipment sensors (IoT/OBox) · procurement (e-GP) · banking",C.GREEN]];
  let y=1.4; layers.forEach(([t,b,c])=>{ s.addShape("roundRect",{x:MX,y,w:12,h:0.9,rectRadius:0.07,fill:{color:C.TINT},line:{color:c,width:1.3}});
    s.addShape("rect",{x:MX,y,w:0.1,h:0.9,fill:{color:c}});
    s.addText(t,{x:MX+0.25,y,w:3.3,h:0.9,fontFace:F,fontSize:12.5,bold:true,color:c,valign:"middle"});
    s.addText(b,{x:MX+3.6,y,w:8.3,h:0.9,fontFace:F,fontSize:10.3,color:C.INK,valign:"middle"}); y+=0.98; });
  s.addShape("roundRect",{x:MX,y:6.35,w:12,h:0.5,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("Cross-cutting principles: numbers are computed by the graph (DB), the LLM only narrates · decisions are always human · every AI run is logged in the audit trail · writes only through approved (whitelisted) server actions",{x:MX+0.2,y:6.35,w:11.6,h:0.5,fontFace:F,fontSize:10.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 17. Agent portfolio
{ const s=p.addSlide(); titleBar(s,"07. AX AGENTS","AX Agent Portfolio — Six Workers, One Approval Inbox"); const k=pg();
  table(s,["Agent","Trigger","Action (draft generation)","Evidence · Inputs","Approver · Written to Odoo"],[
    ["Demand & Production Planning Agent","Daily after close / weekly","Draft next-month production plan (MPS) from public-procurement demand, seasonality and stock + stock-out risk items","Sales and procurement history, stock, lead times, campaigns","Production planner approves → MO drafts created (server action)"],
    ["Material Replenishment & Supplier Agent","ROP reached · retest date approaching · price spike","Draft POs (approved supplier, quality rate, lead-time rationale) · alerts on lots nearing retest/expiry","Stock, BOM demand, supplier quality rate, expiry dates","Purchasing approves → PO draft · quarantine maintained"],
    ["Quality Deviation & CAPA Agent","OOS · IPC excursion · Quality Alert raised","Draft deviation report · similar cases · root-cause hypotheses · CAPA candidates (with cited evidence)","Test results, process parameters, past deviations, SOPs","QA reviews and approves → QMS deviation record (human signature)"],
    ["Predictive Maintenance & Calibration Agent","Sensor anomaly · calibration due in 30 days","Inspection card on failure precursors (e.g., 13-day lead) · draft calibration schedule","Equipment sensors, maintenance history, MTBF/MTTR","Maintenance approves → maintenance request created"],
    ["Batch Release Assistant","Batch completed","Automated release-checklist summary (BMR complete, QC, deviations closed, audit trail reviewed) — 'the decision belongs to QA/QP'","eBMR, QC, QMS, audit log","Release only by QA/QP e-signature (no AI decision)"],
    ["Regulatory Documents & Audit Response Agent","Inspection query · PQR cycle","Search and summarize SOP/batch-record/traceability evidence · draft PQR data · draft responses to DGDA/WHO queries","Knowledge (SOPs), ledger, traceability report","Submitted after QA review"],
  ],MX,1.4,12,[2.0,2.0,3.6,2.3,2.1],{fs:9,rowH:0.65,boldCol:0});
  s.addShape("roundRect",{x:MX,y:6.0,w:12,h:0.8,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"Control Tower (War Room) · Approval Inbox  ",options:{bold:true,color:C.NAVY}},{text:"All agent outputs arrive in the inbox as 'decision cards' (cited evidence, confidence); role-based approvers approve, reject or roll back. Rejection reasons feed learning and rule demotion. AI execution records (Odoo 20 automated chat + AX audit log) are retained and reviewed.",options:{color:C.INK}}],{x:MX+0.2,y:6.0,w:11.6,h:0.8,fontFace:F,fontSize:10,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 18. AX ↔ Odoo 20 connectivity
{ const s=p.addSlide(); titleBar(s,"07. AX ↔ ODOO 20","AX Agents ↔ Odoo 20 Connectivity — Four Channels, One Control Principle"); const k=pg();
  const ch=[["① MCP Server (read · query)","Odoo 20 native /mcp · OAuth 2.1 or MCP-scoped API keys · default tools: Get Models/Fields, Search, Read group · AX agents query the ledger 'within their permission scope'",["Least-privilege dedicated user (ax_reader)","No write tools exposed (default)","Call logs retained"],C.GREEN],
   ["② JSON-2 API + Server Actions (write)","Only approved decision cards → whitelisted server actions (create MO draft, PO draft, maintenance request, deviation record) · Bearer API key · X-Odoo-Database",["Writes create 'draft' records only","E-signatures and state transitions by humans","Changes logged with user = approver"],C.NAVY2],
   ["③ Webhooks · Automation Rules (events)","Studio outbound webhooks/automations push receipts, failed checks, OOS, MO completion and sensor alerts to the AX pipeline (L3) · results received via inbound webhooks",["Idempotent design (duplicate triggers)","Versioned event schemas","PG logical replication (CDC) in parallel"],C.TEAL],
   ["④ Odoo AI Agents · Skills (internal)","Use Odoo 20 built-in agents for SOP Q&A, accounting queries and AI field extraction · automated chat audit log · Sign auto-signature request chains",["IAP credit budget per agent","Provider and data-export policy review (in-country hosting, Data Protection Ordinance)","No direct edits to GMP records"],C.GOLD]];
  ch.forEach((c,i)=>{ const col=i%2,row=Math.floor(i/2); const x=MX+col*6.075, y=1.4+row*2.45;
    s.addShape("roundRect",{x,y,w:5.925,h:2.3,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1.2}});
    s.addShape("rect",{x,y,w:0.09,h:2.3,fill:{color:c[3]}});
    s.addText(c[0],{x:x+0.2,y:y+0.08,w:5.6,h:0.36,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
    s.addText(c[1],{x:x+0.2,y:y+0.45,w:5.6,h:0.95,fontFace:F,fontSize:9.8,color:C.INK,valign:"top"});
    bullets(s,c[2],x+0.15,y+1.4,5.6,{fs:9.3,sa:2,h:0.9,color:c[3]}); });
  s.addShape("roundRect",{x:MX,y:6.35,w:12,h:0.5,rectRadius:0.06,fill:{color:C.LIGHTGREEN}});
  s.addText("Control principle: read broadly (MCP), write narrowly (approved server actions, drafts only), signatures, release and state transitions by humans only, every call in the audit trail — this is how AX and GMP coexist.",{x:MX+0.2,y:6.35,w:11.6,h:0.5,fontFace:F,fontSize:10.5,bold:true,color:C.GREEN,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 19. Ontology · pipeline
{ const s=p.addSlide(); titleBar(s,"07. ONTOLOGY · PIPELINE","Pharma Ontology and Data Pipeline — Which Records Become Which Intelligence"); const k=pg();
  table(s,["Transactions (L1→L2)","Events (L3)","Features & Learning (L3)","Intelligence Using It (L4·L5)"],[
    ["Procurement & sales (mandatory public-hospital purchase, tenders)","Demand events (item × institution × month)","Seasonality, campaign and procurement-cycle profiles","Demand Forecasting & Production Planning Agent"],
    ["Receipts · QC results · suppliers","Receipt / pass-fail / OOS events","Supplier quality rate, lead time, OOS rate","Material Replenishment & Supplier Qualification Agent"],
    ["Dispensing · work orders · IPC · yield","Process parameter and excursion events","Line × item yield · deviation leading indicators","Quality Deviation & CAPA Agent · Predictive Maintenance"],
    ["Equipment sensors · maintenance history","Vibration, temperature, failure events","MTBF · degradation trend · calibration expiry","Predictive Maintenance & Calibration Agent"],
    ["eBMR · QMS · audit log · SOPs","Batch completion, deviation closure, signature events","Release-checklist fulfilment rate · review time","Batch Release Assistant · Audit Response"],
  ],MX,1.4,12,[3.2,2.9,3.0,2.9],{fs:9.6,rowH:0.5,boldCol:0});
  s.addText("Pharma Domain Ontology — Classes and Relations (excerpt)",{x:MX,y:4.45,w:8,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
  const nodes=["Product (SKU)","Master Formula (BOM)","Batch / MO","Material Lot","Process · Work Center","Equipment · Balance","QC Test · Spec","Deviation · CAPA","Supplier","SOP · Training"];
  let x=MX; nodes.forEach((t,i)=>{ const w=1.14; s.addShape("roundRect",{x,y:4.85,w,h:0.55,rectRadius:0.1,fill:{color:[C.NAVY2,C.GREEN,C.TEAL,C.PURPLE,C.GOLD][i%5]}});
    s.addText(t,{x,y:4.85,w,h:0.55,fontFace:F,fontSize:9,bold:true,color:"FFFFFF",align:"center",valign:"middle"}); x+=w+0.065; });
  para(s,"Relations: hasFormula · consumesLot · producedOn (equipment) · testedBy (spec) · deviatesWith · suppliedBy · governedBy (SOP) · releasedBy (QA signature)  —  Evidence ladder: question → decision card → rule/model → event → ledger record (audit trail), each level reachable by a click. Refuted rules are demoted automatically (30 regression checks run continuously).",MX,5.5,12,0.9,{fs:10.3});
  foot(s,k);
}

// ───────────────────────── 20. Benchmark ① Odoo in pharma
section(p,"08","International Benchmarks","Odoo in pharma · global eBR/MES results · lessons from state-owned and emerging-market manufacturers"); n++;
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ①","Odoo in Pharma — Official Customer Cases and Partner-Reported Results"); const k=pg();
  table(s,["Company","Country · Sector","Scope","Results · Highlights","Source Type"],[
    ["Brand for Pharmaceutical Industries","Egypt · pharma group (manufacturing)","V10 Community (2018) → V13 Enterprise (2019) · many modules incl. manufacturing & quality · BI","Phased expansion, rapid user growth (2020)","Odoo official case"],
    ["Magis Pharma Group (Qualenica)","Belgium · personalized medicines","Regulated production (cold storage, batch tracking) · group accounting","7 tools → 1 · live in 2 weeks · 40+ users across 4 companies","Odoo official + partner (Hadron)"],
    ["Laboratorio Fito Medic's","Colombia (est.) · pharma & cosmetics","Manufacturing · quality · WMS","Operational efficiency +20% · productivity +18% (self-reported)","Odoo official case"],
    ["Fraver NV / Viomix / EFA Laboratorios","Belgium / — / Uruguay","Compounding, APIs, finished goods / APIs & medicines / specialty pharma","Paper and spreadsheets → real-time management reporting","Odoo official case"],
    ["Abydos Pharma (CMO)","Europe · contract manufacturing","Manufacturing · inventory · quality · Documents","Batch release −40% · manual errors −85%","Partner report (SDLC)"],
    ["Anonymous pharma manufacturer/distributor","Canada (est.)","Odoo 18 · 16 modules","Reconciliation 40–50 h → 5–8 h · WO-level QC cut rework cost 60% · ROI 77% (6.8 months)","Partner report (Ksolves)"],
    ["Pharmalife Research","Italy · pharma & nutraceuticals","Manufacturing · quality","Throughput +30% · fewer QA delays","Partner report"],
  ],MX,1.4,12,[2.5,2.1,3.0,3.0,1.4],{fs:9,rowH:0.54,boldCol:0});
  s.addShape("roundRect",{x:MX,y:5.75,w:12,h:1.05,rectRadius:0.06,fill:{color:C.LIGHTGOLD}});
  s.addText([{text:"An honest reading  ",options:{bold:true,color:C.GOLD}},{text:"Public cases are mostly small and mid-sized manufacturers, compounders and distributors; no public case of Odoo validated to Part 11 / Annex 11 level at a large GMP finished-dosage plant was identified. This proposal therefore positions 'Odoo = proven ERP core + GMP Layer + CSV project', and partner figures are cited as 'partner-reported'.",options:{color:C.INK}}],{x:MX+0.2,y:5.75,w:11.6,h:1.05,fontFace:F,fontSize:10.3,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 21. Benchmark ② Global
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ②","Global Results — eBR/MES Integration, Not the ERP Core, Drives the Impact"); const k=pg();
  kpiTiles(s,[{v:"−75%",l:"Paper documents\nCipla Patalganga (PAS-X MES + SAP)"},{v:"20 d → 1 d",l:"Batch record review\nValent BioSciences (eBR)"},{v:"−25% / +60%",l:"Production errors / review speed\nFerring Kiel (eBR)"},{v:"4 wk → 6 h",l:"Batch release (RBE)\nGlobal biopharma (Emerson)"},{v:"3–5 days",l:"Best-in-class batch release\n(industry avg. 12–18 days)"}],MX,1.4,12,{h:1.5,vfs:17,lfs:9.3});
  table(s,["Company","Country · Type","Solution · Approach","Lesson"],[
    ["Vinphaco","Vietnam · GMP-WHO","SAP S/4HANA Cloud (FPT) — Phase 1 in 6 months (MM, PP, QM, FICO, SD) → Phase 2 PM, e-banking → Phase 3 WM, QR","Phased rollout brought Phase 1 live within 6 months"],
    ["Incepta / Beximco","Bangladesh · private leaders","SAP (2021, 'first in the country') / Oracle EBS R12 + GxP validation (KPMG)","Even domestic leaders ran separate GxP validation — beware legacy integration cost (Beximco)"],
    ["Pharmaniaga","Malaysia · government-linked company","S/4HANA plant go-live (production orders, QM, delivery, costing)","A GLC also chose global standard ERP + QM integration"],
    ["Cipla · Dr. Reddy's","India · large","PAS-X MES integrated with SAP, SCADA, BMS, IPQC, WMS / template reuse, 5-month build","MES/eBR integration, not ERP alone, drives impact → basis for our L3 and eBMR layer"],
    ["McKinsey QC study","Global","Digital and automated QC: lead time −60–70% · paper −80% · investigations −90% · deviations −65% (some sites)","QC lab digitalization removes the release lead-time bottleneck"],
  ],MX,3.1,12,[1.9,2.1,5.0,3.0],{fs:9.3,rowH:0.56,boldCol:0});
  note(s,"Sources: Körber (Cipla, Ferring), Emerson/ISA, FPT IS, Wikipedia/Zensar, ABeam, McKinsey — vendor-reported figures are not independently verified.",6.5);
  foot(s,k);
}

// ───────────────────────── 22. Benchmark ③ State-owned / emerging markets
{ const s=p.addSlide(); titleBar(s,"08. BENCHMARK ③","Lessons from State-Owned Peers — ERP ≠ Control; GMP Investment Pays"); const k=pg();
  table(s,["Case","Country · Type","What They Did","Outcome","Lesson"],[
    ["Kimia Farma","Indonesia · state-owned","SAP implementation (2015–16)","Only 4 of 9 modules used → 2024 subsidiary accounting fraud, Rp 8.7 trillion restructuring","ERP alone does not stop fraud without procurement, inventory and receivables controls and audit trails · utilization KPIs are essential"],
    ["EIPICO","Egypt · semi-state (ACDIMA 51%)","SAP started 2021 + tracking system on 53 lines · QM batch expiry and quarantine control","ERP and line tracking built in parallel","Put ERP and traceability (serialization) on the same roadmap"],
    ["Vinapharm","Vietnam · 65% state","Investment in 26 GMP-EU/PIC/S lines","2025 pre-tax profit +62%, a record high","High-grade GMP drives profitability and exports"],
    ["KAPL vs HAL · IDPL","India · pharma PSUs","Only KAPL invested in WHO-GMP facilities / the others received financial bailouts only","KAPL the only profitable one · HAL/IDPL revival failed","Financial rescue without facility and quality investment fails"],
    ["SPMC","Sri Lanka · state-owned","JICA new plant (2018) + operational improvement","2025 record 3.6 billion tablets · new warehouse 2026","Bilateral ODA + phased modernization lifts productivity"],
    ["Nepal Drugs","Nepal · state-owned","10-year shutdown → phased restart from ORS (2016)","Revival starting with a limited product range","Start small with core products and core processes"],
  ],MX,1.4,12,[1.6,1.8,3.0,2.9,2.7],{fs:9,rowH:0.56,boldCol:0});
  card(s,MX,5.5,12,1.3,"Five Implications for a State-Owned GMP Plant Proposal",["① Even when starting with finance, include procurement, inventory and batch internal controls (approvals, audit trail) in Phase 1   ② Put GMP facility investment and software (eBMR, QMS) on the same roadmap   ③ Avoid module over-adoption — budget for utilization, training and hypercare   ④ Pilot on core products and lines → scale out   ⑤ Link to bilateral/multilateral funding such as ADB and EDCF"],C.GREEN,{fs:10});
  foot(s,k);
}

// ───────────────────────── 23. Requirements ①
section(p,"09","Requirements · Localization · Roadmap · KPIs","Preliminary requirements → local conditions → phased build → performance measurement → governance"); n++;
{ const s=p.addSlide(); titleBar(s,"09. REQUIREMENTS ①","Requirements (Preliminary) — Company · Procurement · Materials · Production"); const k=pg();
  table(s,["No","Category","Item","Requirement (figures and processes to be finalized in the analysis phase)","TBD"],[
    ["1","Company & IT","Scale · sites","Multi-site (Dhaka, Bogura, Gopalganj, Khulna) multi-company/multi-warehouse · several hundred users incl. Light Users assumed",""],
    ["2","Company & IT","Hosting","In-country data hosting (national sovereign cloud or on-premise) · fixed Odoo Enterprise version · re-validation control","TBD"],
    ["3","Company & IT","Language · currency","Bangla/English UI · BDT with lakh/crore notation · fiscal year 1 July – 30 June",""],
    ["4","Procurement","e-GP · approvals","PPR 2025/e-GP integration · purchase request → PO → receipt → invoice approval workflow · block POs to non-approved suppliers · beneficial-owner data",""],
    ["5","Procurement","Supplier qualification","Approved supplier list (material × supplier × manufacturing site) · audit cycle and expiry alerts · supplier quality rate · CoA management",""],
    ["6","Materials & Inventory","Lots · expiry","Lot/mfg date/expiry/retest date mandatory · FEFO enforced · block dispatch of expired or retest-overdue lots · automatic quarantine location",""],
    ["7","Materials & Inventory","Status control","Quarantine / under test / released / rejected — changed by QC/QA only (e-signature) · system block on issuing quarantined stock",""],
    ["8","Materials & Inventory","Traceability · recall","Two-way genealogy: material lot → intermediate → finished product → customer · instant recall impact scoping · mock-recall records",""],
    ["9","Production","BMR/eBMR","Batch record auto-generated from the approved formula · dispensing (balance interface), IPC, yield reconciliation · step signatures · deviation links","TBD"],
    ["10","Production","Planning · execution","Demand- and procurement-based MPS → work orders → shop-floor tablet execution · continuous/campaign production · block equipment with expired calibration",""],
    ["11","Production","Packaging · serialization","Packaging orders · label reconciliation · GS1 GTIN/lot/expiry master data · serialization interface","TBD"],
  ],MX,1.4,12,[0.5,1.2,1.5,8.1,0.7],{fs:9,rowH:0.44,center:[0,4]});
  foot(s,k);
}

// ───────────────────────── 24. Requirements ②
{ const s=p.addSlide(); titleBar(s,"09. REQUIREMENTS ②","Requirements (Preliminary) — Quality · Finance · KPIs · Integration · CSV"); const k=pg();
  table(s,["No","Category","Item","Requirement","TBD"],[
    ["12","Quality","QC · release","Incoming/in-process/finished QCP · pass-fail/measurement · OOS flag · CoA · LIMS integration · QA release checklist + QA/QP e-signature",""],
    ["13","Quality","QMS","Deviation → classification → RCA → CAPA → effectiveness · change control (impact assessment, re-validation) · complaints & recalls · links to batch/equipment/document/supplier",""],
    ["14","Quality","Audit trail · signature","Field-level old/new, reason, UTC on GMP models · no deletion · user-independent · pre-release review · record e-signature re-authentication",""],
    ["15","Quality","SOP · training","SOP versioning, approval (e-signature), effective date, retirement · role-based training matrix · retraining on revision · untrained users blocked","TBD"],
    ["16","Equipment","Maintenance · calibration","Preventive/corrective maintenance · calibration intervals and expiry blocking · MTBF/MTTR · sensor (IoT) integration",""],
    ["17","Accounting","Localization","Mushak 6.3 VAT e-invoicing and retention (Finance Bill 2026) · VDS · FY July–June · review of iBAS++ public-accounting integration","TBD"],
    ["18","Accounting","Controls","AP/AR approvals · journal hash immutability · cost and P&L by project/plant · procurement–accounting 3-way matching",""],
    ["19","Performance","KPIs","Dashboards: batch release cycle time, RFT, deviation rate, CAPA closure, inventory accuracy, expiry write-offs, OEE, FDA quality metrics (LAR, PQCR, IOOSR)",""],
    ["20","AX","Agents","6 agents · decision cards & approval inbox · MCP read / server-action write · AI execution audit log · IAP credit budget","TBD"],
    ["21","Integration","Interfaces","LIMS · balances/label printers · serialization · e-GP · banks · legacy data migration (partners, items, BOMs, stock, open items)","TBD"],
    ["22","Validation","CSV","VMP, URS, risk assessment, IQ/OQ/PQ, traceability matrix, summary report · operational SOPs · upgrade re-validation procedure",""],
  ],MX,1.4,12,[0.5,1.2,1.5,8.1,0.7],{fs:9,rowH:0.44,center:[0,4]});
  foot(s,k);
}

// ───────────────────────── 25. Localization · infrastructure · security
{ const s=p.addSlide(); titleBar(s,"09. LOCALIZATION · INFRA","Localization · Infrastructure · Security — Designed for Bangladesh Realities"); const k=pg();
  card(s,MX,1.4,3.9,2.55,"Localization Requirements",["Bangla Unicode UI and reports · English in parallel","BDT · lakh/crore notation · fiscal year 1 July – 30 June","Mushak 6.3 tax invoices e-issued and retained in ERP (Finance Bill 2026) · VDS Rules 2025","e-GP fully mandatory (PPR 2025) → procurement module alignment · beneficial-owner disclosure","Possible iBAS++ public-accounting integration (to discuss)"],C.NAVY2,{fs:9.8});
  card(s,MX+4.05,1.4,3.9,2.55,"Infrastructure & Availability",["In-country hosting: National Data Center (Kaliakoir Tier-IV, 99.995%) / Oracle sovereign region / on-premise","3–4 h daily outages in industrial belts (2026) → UPS and generators + Odoo 20 offline mode (local queue → sync) + shop-floor tablets","Separate production/test/development environments · fixed version · backup/restore rehearsals (RTO/RPO)","Mobile 4G-centric → lightweight screens and barcode app"],C.GREEN,{fs:9.8});
  card(s,MX+8.1,1.4,3.9,2.55,"Security & Data Governance",["Compliance with the 2025 Personal Data Protection, Data Governance and Cyber Protection Ordinances → in-country hosting assumed","RBAC (Odoo 20 ir.access) · individual accounts · MFA · session policy · account lifecycle logs","AI data-export policy: scope of external LLM use, masking, in-country model (GPU server) option","WAF · network segmentation · DB access control · change control"],C.RED,{fs:9.8});
  table(s,["Component","Role","Recommended Spec (draft)","Notes"],[
    ["Production App/DB","Odoo 20 Enterprise + PostgreSQL 16","8–16 vCPU · 64 GB · SSD · Ubuntu LTS","Scale with multi-site user count"],
    ["Test/Validation","CSV and upgrade regression environment","4–8 vCPU · 32 GB","Same configuration as production (validation prerequisite)"],
    ["AX Server","Event pipeline · knowledge graph · agents · approval inbox","8 vCPU · 32 GB (+ GPU option: in-country LLM)","Connected to Odoo via MCP/JSON-2/webhooks"],
    ["Shop Floor","Tablets · barcodes · balances/labels · IoT (OBox)","Tablets per line · UPS","Offline mode verified"],
  ],MX,4.15,12,[2.0,4.0,3.3,2.7],{fs:9.5,rowH:0.4,boldCol:0});
  note(s,"Hosting choice (national DC, sovereign cloud, on-premise) to be finalized at kick-off based on the latest Data Protection Ordinance amendments and procurement conditions.",6.5);
  foot(s,k);
}

// ───────────────────────── 26. Roadmap
{ const s=p.addSlide(); titleBar(s,"09. ROADMAP","Roadmap — Prove on Core Lines, Then Scale Plant-Wide (≈12–18 Months)"); const k=pg();
  const ph=[["0  Assessment · CSV Plan","1–2 months",["Site assessment (process, data flows, GMP gaps)","URS · VMP · risk assessment · KPI baseline","Confirm EOI/ADB track, hosting and partners"],C.SUB],
   ["1  Odoo 20 Core","3–4 months",["Purchase · inventory (lot/FEFO/quarantine) · manufacturing · quality · maintenance · accounting · localization","Approval workflows · e-GP · data migration","IQ/OQ round 1 · pilot line go-live"],C.NAVY2],
   ["2  GMP Layer","3–4 months",["Audit trail · e-signature · eBMR · QMS · SOP/training · status enforcement","LIMS, balance and label interfaces","OQ/PQ · one-batch-cycle PQ · validation close-out · Go-Live"],C.GREEN],
   ["3  AX Intelligence","3–4 months",["Event pipeline · ontology · knowledge graph","6 agents · approval inbox · control tower · MCP/server-action connections","KPI loop · rule promotion/demotion in operation"],C.GOLD],
   ["4  Scale & Enhance","Ongoing",["Plant-wide rollout · serialization · MES review","Feed digital GMP design into the ADB vaccine plant","Support DGDA ML3 and WHO GMP re-certification · annual periodic review"],C.PURPLE]];
  const cw=2.3, gap=0.125; ph.forEach((c,i)=>{ const x=MX+i*(cw+gap);
    s.addShape("roundRect",{x,y:1.4,w:cw,h:0.8,rectRadius:0.07,fill:{color:c[3]}});
    s.addText(c[0],{x,y:1.4,w:cw,h:0.5,fontFace:F,fontSize:11.5,bold:true,color:"FFFFFF",align:"center",valign:"middle"});
    s.addText(c[1],{x,y:1.85,w:cw,h:0.3,fontFace:F,fontSize:9.5,color:"E6EEF3",align:"center"});
    s.addShape("roundRect",{x,y:2.3,w:cw,h:2.75,rectRadius:0.07,fill:{color:C.TINT},line:{color:c[3],width:1}});
    bullets(s,c[2],x+0.08,2.4,cw-0.15,{fs:9.6,sa:4,h:2.6});
    if(i<ph.length-1) s.addText("▶",{x:x+cw-0.02,y:1.4,w:gap+0.06,h:0.8,fontFace:F,fontSize:9,color:C.SUB,align:"center",valign:"middle"}); });
  table(s,["Gate","Pass Criteria (examples)"],[
    ["G1 Design Approval","QA sign-off on URS, VMP and risk assessment · hosting and procurement track confirmed"],
    ["G2 Core Live","Pilot-line inventory accuracy ≥ 98% · all approval workflows live · IQ/OQ passed"],
    ["G3 GMP Go-Live","PQ (one batch cycle) · all audit-trail and signature tests passed · validation summary report · SOPs and training complete"],
    ["G4 AX in Operation","Decision-card approval rate and rejection feedback · one KPI loop cycle · AI audit log reviewed"],
  ],MX,5.2,12,[2.2,9.8],{fs:9.5,rowH:0.33,boldCol:0});
  foot(s,k);
}

// ───────────────────────── 27. Project management · risks
{ const s=p.addSlide(); titleBar(s,"09. PROJECT MGMT · RISK","Project Management & Risk — Managed Jointly with the Client"); const k=pg();
  table(s,["No","Risk","Expected Impact","Management & Response"],[
    ["1","Requirement changes and scope creep (EOI modules + GMP + AX)","Schedule delay · more Cat. 5 · re-validation","Requirements freeze at end of analysis · change requests · defer unfinished features to the next phase"],
    ["2","Validation burden and regulatory change (Annex 11 2025 revision, DGDA ML3, e-invoicing)","Go-live delay · re-validation","CSV as a first-class WBS item · design to the draft revision · regulatory monitoring · per-release impact assessment"],
    ["3","Low user adoption and utilization (Kimia Farma lesson)","Unused modules · parallel paper · duplicate data","Role-based training (Bangla) · key users · hypercare · module utilization KPI ≥ 80%"],
    ["4","Unstable power and network (3–4 h daily outages)","Shop-floor entry stops · data gaps","UPS and generators · offline-mode queue verification · controlled reasons for late entries"],
    ["5","Procurement and governance (PPR 2025, e-GP, beneficial ownership, audit history)","Contract delays · audit findings","Local partner consortium · e-GP registration · transparent procurement dashboard · approval workflows in Phase 1"],
    ["6","Data localization and AI data export","Regulatory breach · project suspension","In-country hosting · AI usage policy · masking · in-country LLM option"],
    ["7","Interface cost and schedule (LIMS, balances, serialization, legacy — Beximco lesson)","Budget overrun · delay","Minimum viable integration in Phase 1 · build after scope is clear · separate uncertain items as options"],
  ],MX,1.4,12,[0.5,3.4,2.6,5.5],{fs:9.3,rowH:0.52,center:[0]});
  card(s,MX,5.55,5.9,1.3,"Client Participation",["Dedicated PM + key users per function (QA, QC, production, warehouse, purchasing, accounting, IT)","Provide current SOPs, batch records and data · interviews (1–3 per function)","Join sprint reviews, UAT and PQ · QA/QP sign-off"],C.NAVY2,{fs:9.6});
  card(s,MX+6.1,5.55,5.9,1.3,"Delivery Methodology",["Discovery → Blueprint → Realization (Agile, 3–4 sprints) → Testing (SIT/UAT + CSV) → Training → Go-Live/MA","Signed-off deliverables per phase · hypercare · annual periodic review"],C.GREEN,{fs:9.6});
  foot(s,k);
}

// ───────────────────────── 28. KPIs
{ const s=p.addSlide(); titleBar(s,"09. KPI","Expected Benefits — KPIs and Draft Targets (Fixed After Baseline)"); const k=pg();
  kpiTiles(s,[{v:"−30~50%",l:"Batch release cycle time"},{v:"−80%",l:"Batch record errors"},{v:"≤30 d · ≥90%",l:"Deviation closure · on-time rate"},{v:"≥99% · 100%",l:"Inventory accuracy · FEFO compliance"},{v:"−30%",l:"Expiry write-off value"},{v:"100% · 0",l:"Audit-trail review · shared accounts"}],MX,1.4,12,{h:1.35,vfs:16,lfs:9.5});
  table(s,["Area","KPI","Definition · Rationale","Benchmark"],[
    ["Regulatory & Quality","LAR · PQCR · IOOSR · APR on-time rate","FDA Quality Metrics (lot acceptance rate, product quality complaint rate, invalidated OOS rate)","FDA guidance"],
    ["Production & Release","Batch release cycle time · batch record review time · RFT · OEE","Manufacturing complete → QA release / share of lots without deviations","Best 3–5 days vs. avg. 12–18 · OEE 60–70%"],
    ["Quality System","Deviation rate · CAPA closure time and recurrence · audit-trail review rate · inspection findings","Deviation rate leads defect rate by ~4 months (r = 0.83)","IPA study · Annex 11 §9"],
    ["Data Integrity","Late-entry ratio · zero shared accounts · access review cycle · backup restore success rate","PI 041 · TRS 1033","—"],
    ["Inventory & Supply","Inventory accuracy · turnover · expiry write-offs · stock-out rate · supplier OTIF · zero unapproved purchases","Effect of FEFO and quarantine control","PLIVA inventory −30%+ (secondary)"],
    ["Equipment · Training · Adoption","Calibration on-time rate · PM compliance · MTBF/MTTR · SOP training completion · module utilization · ROI","Odoo Maintenance outputs · Kimia Farma lesson","Ksolves ROI 77% (partner)"],
  ],MX,2.95,12,[1.6,3.9,3.9,2.6],{fs:9.3,rowH:0.5,boldCol:0});
  note(s,"Results are aggregated automatically against targets in the AX Platform's 'Project & KPI Center' and published; agents propose improvement actions for metrics that fall short (honest monitoring).",6.5);
  foot(s,k);
}

// ───────────────────────── 29. Governance · partnering · funding
{ const s=p.addSlide(); titleBar(s,"09. STRUCTURE · FUNDING","Governance · Partnering · Funding — Structured for State-Owned Procurement"); const k=pg();
  card(s,MX,1.4,3.9,2.6,"Delivery Structure (Draft)",["Prime: local consortium (official Odoo partners such as Metamorphosis/VS ONE, or a local consulting firm) — meets national-firm and e-GP conditions","ASC: design and build of GMP Layer, CSV and AX Platform — technical subcontractor/solution provider","Client: dedicated PM, QA/QP, key users, operations organization","Precedent: Vietnam's FPT IS won SAP-based ERP for Bangladeshi state-owned EGCB (US$8.8M) and GTCL (US$9.1M)"],C.NAVY2,{fs:9.6});
  card(s,MX+4.05,1.4,3.9,2.6,"Funding & Procurement Tracks",["① EDCL self-funded ERP (EOI May 2026) — propose the GMP-layer complement once the award is known","② ADB US$336.5M vaccine & therapeutics project — international competitive procurement; digital GMP package (MES/eBR, LIMS, QMS)","③ Korea EDCF US$3B (2023–27) · KOICA 2026–28 US$96M — candidate health/pharma digitalization project (ERD proposal)","④ World Bank health PforR · US$55M procurement digitalization — indirect linkage"],C.GOLD,{fs:9.6});
  card(s,MX+8.1,1.4,3.9,2.6,"ASC Differentiators",["A working AX Platform (M0–M7: decision cards, approval inbox, KPI Center) — a real system, not a concept","Odoo 20 MCP/JSON-2/webhook connection design in hand · in-country GPU LLM option","PI 041 data integrity package · GS1 serialization pre-built · Mushak 6.3 and e-GP integration","Offline-resilient, sovereign-cloud-compatible design"],C.GREEN,{fs:9.6});
  table(s,["Phase","Client Preparation & Participation","Purpose"],[
    ["All phases","Dedicated PM with decision authority · QA/QP · named key users per function · decision deadlines met","Avoid delays · single communication channel"],
    ["Analysis–Design","Current SOPs, batch records, item/BOM/partner data · process interviews (1–3 per function) · joint GMP gap confirmation","Prevent missed requirements"],
    ["Build–Validation","Sprint reviews · UAT · PQ participation (one batch cycle) · validation sign-off","Secure quality · avoid rework"],
    ["Transition","Operations organization, SOPs and training complete · hypercare · agreed periodic review cycle","Avoid post-go-live confusion"],
  ],MX,4.2,12,[1.5,7.5,3.0],{fs:9.5,rowH:0.42,boldCol:0});
  note(s,"PPR 2025 details such as mandatory local agents for foreign firms and domestic-preference clauses require legal review before kick-off.",6.5);
  foot(s,k);
}

// ───────────────────────── 30. About the proposer
{ const s=p.addSlide(); titleBar(s,"ABOUT ASC","About ASC (AX Platform) — Not a Methodology, a System Already Running"); const k=pg();
  card(s,MX,1.4,5.9,2.5,"AX Platform (odooaierp.com) — Built and in Live Operation",["M0 common foundation (SSO, backup, registry, export gate) · M1 ingestion (CDC, Excel, forms, IoT) · M2 standard datasets and quality gates","M3 analytics studio · M4 learning engine (demand forecasting, anomaly detection, predictive maintenance; model cards) · M5 knowledge graph (4M, confidence loop)","M6 LLM judgement (GraphRAG, decision cards, 30 regression checks) · M7 agents and control (approval inbox, War Room) · Project & KPI Center","Odoo integration: CDC logical replication · approval card → PO draft · Odoo approval-inbox add-on · dual PostgreSQL backend · 150+ automated tests"],C.NAVY2,{fs:9.6});
  card(s,MX+6.1,1.4,5.9,2.5,"Demonstrated Results (Synthetic and Real-Data Demos)",["Demand forecast WAPE 7.0% · equipment failure precursor 13 days ahead (OVEN-2) · 11 decision cards approved end-to-end","Project & KPI Center: 4 business goals + 9 technical KPIs — automatic attainment tracking, honest shortfall display","Tailored proposal and demo for a bakery manufacturer (raw-material lots, FEFO, multi-site, B2B)","Operations: Cloudflare tunnel · backup/recovery drills · uptime monitoring · billing · tenant management"],C.GREEN,{fs:9.6});
  s.addText("What ASC Adds for Pharma GMP Deployment",{x:MX,y:4.05,w:8,h:0.35,fontFace:F,fontSize:12.5,bold:true,color:C.NAVY});
  flow(s,["GMP Layer\n(audit trail · e-sign · eBMR · QMS)","CSV Package\n(VMP to PQ · traceability)","Odoo 20 Connectivity\n(MCP · JSON-2 · webhooks)","6 Pharma Agents\n+ approval inbox · control tower","Localization\n(Bangla · Mushak · e-GP)","Training · Hypercare\n· Periodic Review"],MX,4.5,12,{h:0.95,fs:9.5});
  s.addShape("roundRect",{x:MX,y:5.7,w:12,h:1.1,rectRadius:0.06,fill:{color:C.HEAD}});
  s.addText([{text:"In one sentence  ",options:{bold:true,color:C.NAVY}},{text:"\"What lives in a document depends on people to uphold it; what becomes a platform is upheld by structure.\" — GMP data integrity, procurement transparency and AI judgement are all designed on the same principle. We designed this for you, and the design is already running.",options:{color:C.INK,italic:true}}],{x:MX+0.2,y:5.7,w:11.6,h:1.1,fontFace:F,fontSize:11,valign:"middle"});
  foot(s,k);
}

// ───────────────────────── 31. Next steps
{ const s=p.addSlide(); titleBar(s,"NEXT STEP","Next Steps — What to Confirm, What to Do Together"); const k=pg();
  card(s,MX,1.4,5.9,2.9,"Pre-Kick-off Checklist (your side · to be researched)",["Your exact legal entity, scale, products and plants (EDCL or not) · current systems and extent of paper processes","Outcome of the May 2026 ERP EOI (award/RFP stage), module scope and prime-contract structure","ADB vaccine plant project procurement plan and digital GMP scope","Latest DGDA GMP, data integrity/CSV guidelines and serialization plans","Hosting (national DC / sovereign cloud / on-premise) · latest Data Protection Ordinance amendments","PPR 2025 conditions for foreign participation · local partner candidates"],C.RED,{fs:9.8});
  card(s,MX+6.1,1.4,5.9,2.9,"Proposed Roadmap (Next 90 Days)",["Week 1: review and feedback on this preliminary proposal · reply to the checklist","Weeks 2–4: online workshops (QA, production, warehouse, purchasing, accounting) — first-cut GMP gaps and requirements","Weeks 4–8: site assessment (optional) · draft URS and VMP · scope, schedule and quotation · partner structure confirmed","Weeks 8–12: pilot-line scope sign-off · kick-off","In parallel: AX Platform live demo (app.odooaierp.com) · pharma scenario demo data"],C.GREEN,{fs:9.8});
  s.addShape("roundRect",{x:MX,y:4.5,w:12,h:1.2,rectRadius:0.07,fill:{color:C.NAVY}});
  s.addText([{text:"Proposal & Enquiries   ",options:{bold:true,color:"9FC7BD"}},{text:"ASC (AX Platform) · AX Platform Business Team   ·   odooaierp.com   ·   asclhg@gmail.com\n",options:{color:"FFFFFF"}},{text:"Live demo: app.odooaierp.com (accounts issued on request)  ·  Korean-language version of this proposal available separately",options:{color:"C9D9E3",fontSize:10}}],{x:MX+0.3,y:4.5,w:11.4,h:1.2,fontFace:F,fontSize:12.5,valign:"middle"});
  note(s,"Figures, schedule and scope in this document are a preliminary outline; research is based on web sources as of 22 Oct 2026 (see Appendix). Regulatory citations will be verified against EudraLex/eCFR/WHO primary texts before the final submission.",5.9,{h:0.6,fs:9.5});
  foot(s,k);
}

// ───────────────────────── 32. Appendix — sources
{ const s=p.addSlide(); titleBar(s,"APPENDIX","Appendix — Key Sources (researched 22 Oct 2026)"); const k=pg();
  const cols=[["Regulation & Standards",["WHO TRS 986 Annex 2 · TRS 1033 Annex 4 · TRS 1019 Annex 3","EU GMP Annex 11 (2011 / 2025 draft) · Annex 15 · Ch. 1/4/8","FDA 21 CFR Part 11 · CSA guidance (2025)","PIC/S PI 041-1 (2021) · ISPE GAMP 5 2nd ed.","TGA ALCOA+ mapping"]],
   ["Odoo 20",["odoo.com release notes (20, 19.x) · Meet Odoo 20 blog","Odoo 20 docs: MCP server, AI fields, external RPC API, Studio automation, offline mode, manufacturing/inventory","Partners: Braintec, iVentureTeam, Octura, Macopedia, Cybrosys, etc.","OCA auditlog · quality_control_oca · partner eBMR/audit-trail modules"]],
   ["Bangladesh",["BPPA EOI EDCL/Dhaka/EOI/Tender/2026/168 · EDCL portal · Wikipedia · MCCI","ADB 4388-BAN (US$336.5M) · ADB Brief 302 · WHO Bangladesh NRA","TBS, Daily Star, Dhaka Tribune, FE, Prothom Alo (industry, GMP, outages, PPR 2025, EDCF)","Drugs & Cosmetics Act 2023 · tralac/RAPID (LDC) · DataReportal 2026"]],
   ["Benchmarks & KPIs",["Odoo official customer cases (Brand Pharma, Magis, Fito Medic's, Fraver, etc.) · SDLC, Ksolves (partners)","Körber (Cipla, Ferring) · Emerson/ISA · FPT IS (Vinphaco) · ABeam (Pharmaniaga)","Kimia Farma studies (UGM/Telkom) · EIPICO AR · Vinapharm · SPMC · India PSUs","FDA Quality Metrics · IPA deviation study · McKinsey QC · intuitionlabs KPIs"]]];
  cols.forEach((c,i)=>{ card(s,MX+(i%2)*6.075,1.4+Math.floor(i/2)*2.6,5.925,2.45,c[0],c[1],[C.NAVY2,C.GREEN,C.GOLD,C.PURPLE][i],{fs:9.3}); });
  note(s,"The full URL list (~300 entries) is contained in three separate research reports (research_odoo20, research_pharma_gmp, research_bangladesh) — available on request. Due to research-environment constraints, findings rely on search excerpts and partner cross-verification rather than direct access to primary texts.",6.5,{h:0.5});
  foot(s,k);
}

const out="/home/user/thirdbrain-web/docs/presentations/Bangladesh_StateOwned_Pharma_Odoo20_GMP_AX_Proposal_EN.pptx";
p.writeFile({fileName:out}).then(()=>console.log("DECK",out,"slides",n));
