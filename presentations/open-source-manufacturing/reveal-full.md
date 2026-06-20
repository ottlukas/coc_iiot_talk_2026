---
title: "Open Source for Regulated Manufacturing"
subtitle: "GMP‑Compliant IIoT Data Logging with Apache IoTDB"
author: "Lukas Ott"
event: "CommunityOverCode 2026"
date: "2026-10-11"
theme: "custom"
transition: "slide"
---

<link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&family=Roboto+Mono:wght@400;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/reveal-theme.css">

# Open Source for Regulated Manufacturing

**GMP‑Compliant IIoT Data Logging with Apache IoTDB**  
*Lukas Ott — CommunityOverCode 2026*  

---

## The 2026 Regulatory Storm

- **Annex 11 Overhaul:** ~1,500 → ~10,000 words; explicit IT security, cloud control, absolute data integrity.
- **Annex 22:** New regulation for AI-supported systems in GMP environments.

<div id="regChart" data-chart="regulatory" style="width:100%;max-width:900px;height:300px;margin-top:18px"></div>

---

## Compliance in 60 Seconds: FDA vs. EU

- **FDA 21 CFR Part 11** — Electronic records & signatures trustworthiness; secure validation; audit trails.
- **EU Annex 11** — Lifecycle validation & supplier governance; ALCOA+ data integrity.

---

## The Traditional Historian "Tax"

**Legacy (Before):**
- Proprietary per-tag licensing
- Vendor lock-in, scaling costs
- Weak native audit & metadata lineage

**Open Source (After):**
- Transparent governance
- Scalable community tools
- Native auditability & lineage

---

## ALCOA → ALCOA+

- Attributable, Legible, Contemporaneous, Original, Accurate
- ALCOA+: Complete, Consistent, Enduring, Available
- ALCOA++ emphasizes Integrity, Robustness, Transparency, Accountability

---

## Apache IoTDB as a GMP Historian

- High-throughput time-series ingestion
- Access controls, encryption, retention
- TSFile immutable storage format
- Integrates with Iceberg for cold storage

---

## Core Enabler: Apache TSFile

- Append-only, tamper-evident blocks
- Efficient validation boundaries
- Bridges hot/cold storage

---

## End-to-End Apache Pipeline

<div class="pipeline-interactive" style="display:flex;gap:12px;flex-wrap:wrap;align-items:center">
  <button class="pipeline-step" data-step="PLC4X">PLC4X</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="BifroMQ">BifroMQ</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="Kafka">Kafka</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="Flink/Beam">Flink / Beam</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="IoTDB">IoTDB (TSFile)</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="Iceberg">Iceberg (Cold)</button>
  <span class="arrow">→</span>
  <button class="pipeline-step" data-step="Superset">Superset</button>
</div>

<div id="pipeline-note" style="margin-top:14px;padding:12px;border-radius:6px;background:#fff;display:none"></div>

---

## CSV with GAMP 5

1. Define system boundaries & categorize software
2. Risk assessment & requirements specification
3. IQ/OQ/PQ test scripts
4. Continuous monitoring & supplier governance

---

## Key Takeaways

- Open Source is Superior — transparency enables verifiable validation
- IoTDB + TSFile + Iceberg = ALCOA++ architecture
- Act now: migrate away from legacy tag licensing

---

## Questions?

Thank you for attending — Lukas Ott

<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script src="assets/interactive.js"></script>
<script>
// create regulatory chart if present
(function(){
  const container = document.getElementById('regChart');
  if(!container) return;
  const canvas = document.createElement('canvas');
  canvas.id = 'regChartCanvas';
  container.appendChild(canvas);
  new Chart(canvas.getContext('2d'), {
    type:'bar',
    data:{labels:['Annex 11 (old)','Annex 11 (new)','Annex 22'],datasets:[{label:'Document size (words, approximate)',data:[1500,10000,1200],backgroundColor:['#4a90e2','#2c3e50','#7fb3d5']} ]},
    options:{responsive:true,maintainAspectRatio:false}
  });
})();
</script>
