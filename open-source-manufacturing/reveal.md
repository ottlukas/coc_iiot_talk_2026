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
<link rel="stylesheet" href="style.css">

<!-- Title Slide (dark) -->
---
<!-- .title-slide -->
<section class="title-slide">
  <div class="title-inner">
    <h1>Open Source for Regulated Manufacturing</h1>
    <h2>GMP‑Compliant IIoT Data Logging with Apache IoTDB</h2>
    <p class="meta"><strong>Speaker:</strong> Lukas Ott &nbsp; • &nbsp; <strong>Event:</strong> CommunityOverCode 2026 &nbsp; • &nbsp; <strong>Date:</strong> 2026-10-11</p>
    <p class="lead">Building scalable, auditable, and compliant IIoT data platforms with ASF technologies.</p>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Introduce yourself, summarize talk goals: explain need for auditable IIoT platforms and how ASF tooling helps.</aside>
</section>

---

<!-- Slide 2: The Hook -->
<section>
  <h2>The 2026 Regulatory Storm</h2>
  <div class="row two-icons">
    <div class="card fragment" data-fragment-index="1">
      <h3>Annex 11 Overhaul</h3>
      <p>Massive expansion (from ~1,500 words to ~10,000): explicit IT security, cloud control, absolute data integrity.</p>
    </div>
    <div class="card fragment" data-fragment-index="2">
      <h3>Annex 22</h3>
      <p>New regulation governing AI-supported systems inside GMP environments.</p>
    </div>
  </div>
  <div id="regChart" style="width:100%;max-width:900px;height:280px;margin-top:18px"></div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Show chart illustrating regulatory text expansion and explain why this raises validation and traceability requirements.</aside>
</section>

---

<!-- Slide 3: Core Framework -->
<section>
  <h2>Compliance in 60 Seconds: FDA vs. EU</h2>
  <div class="split">
    <div class="col">
      <h3>🇺🇸 FDA — 21 CFR Part 11</h3>
      <ul class="fragment" data-fragment-index="1">
        <li>Electronic records & signatures trustworthiness</li>
        <li>Secure validation, time-stamped audit trails</li>
        <li>Training & procedural controls</li>
      </ul>
    </div>
    <div class="col">
      <h3>🇪🇺 EU — Annex 11</h3>
      <ul class="fragment" data-fragment-index="2">
        <li>Lifecycle validation & supplier governance</li>
        <li>Full risk management and ALCOA+ data integrity</li>
        <li>Operational controls for cloud & AI</li>
      </ul>
    </div>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Contrast the two regulations and emphasize the unified goal: audit-ready digital systems.</aside>
</section>

---

<!-- Slide 4: Core Problem -->
<section>
  <h2>The Traditional Historian "Tax"</h2>
  <div class="before-after">
    <div class="panel left fragment" data-fragment-index="1">
      <h4>Legacy (Before)</h4>
      <ul>
        <li>Proprietary licensing (per-tag)</li>
        <li>Vendor lock-in, scaling costs</li>
        <li>Weak native audit & metadata lineage</li>
      </ul>
    </div>
    <div class="panel right fragment" data-fragment-index="2">
      <h4>Open Source (After)</h4>
      <ul>
        <li>Transparent code and governance</li>
        <li>Scalable, community-driven tools</li>
        <li>Native auditability and data lineage</li>
      </ul>
    </div>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Paint the picture: legacy vendor lock-in vs. open, auditable toolchains.</aside>
</section>

---

<!-- Slide 5: ALCOA++ -->
<section>
  <h2>ALCOA → ALCOA+</h2>
  <div class="grid">
    <div class="tile fragment" data-fragment-index="1"><div class="icon">A</div><h4>Attributable</h4><p>Who created/modified the record.</p></div>
    <div class="tile fragment" data-fragment-index="2"><div class="icon">L</div><h4>Legible</h4><p>Readable and interpretable.</p></div>
    <div class="tile fragment" data-fragment-index="3"><div class="icon">C</div><h4>Contemporaneous</h4><p>Recorded at the time of event.</p></div>
    <div class="tile fragment" data-fragment-index="4"><div class="icon">O</div><h4>Original</h4><p>Source or certified copy preserved.</p></div>
    <div class="tile fragment" data-fragment-index="5"><div class="icon">A</div><h4>Accurate</h4><p>Free from error and fully documented.</p></div>
    <div class="tile fragment" data-fragment-index="6"><div class="icon">+</div><h4>Complete / Consistent / Enduring / Available</h4><p>ALCOA+ expands the lifecycle guarantees.</p></div>
  </div>
  <svg class="timeline" viewBox="0 0 800 120" preserveAspectRatio="xMidYMid meet">
    <rect x="40" y="40" width="720" height="6" fill="#e6eef8"/>
    <text x="60" y="30" class="tl">Attributable</text>
    <text x="180" y="30" class="tl">Legible</text>
    <text x="300" y="30" class="tl">Contemporaneous</text>
    <text x="420" y="30" class="tl">Original</text>
    <text x="540" y="30" class="tl">Accurate</text>
  </svg>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Walk through each ALCOA element, then explain ALCOA+ extension and importance for audits.</aside>
</section>

---

<!-- Slide 6: Apache IoTDB -->
<section>
  <h2>Apache IoTDB as a GMP Historian</h2>
  <div class="two-col">
    <div class="left fragment" data-fragment-index="1">
      <ul class="checklist">
        <li>⚡ High-throughput time-series ingestion</li>
        <li>🔐 Access controls, encryption, retention</li>
        <li>🗃️ TSFile immutable storage format</li>
        <li>🔁 Integrates with Iceberg for cold storage</li>
      </ul>
    </div>
    <div class="right fragment" data-fragment-index="2">
      <!-- Simple architecture SVG -->
      <svg viewBox="0 0 600 240" class="arch">
        <rect x="10" y="20" width="110" height="40" rx="6" fill="#eaf4ff" stroke="#4a90e2"/>
        <text x="25" y="45">PLC4X</text>
        <rect x="140" y="20" width="110" height="40" rx="6" fill="#eaf4ff" stroke="#4a90e2"/>
        <text x="170" y="45">BifroMQ</text>
        <rect x="270" y="20" width="110" height="40" rx="6" fill="#eaf4ff" stroke="#4a90e2"/>
        <text x="300" y="45">Kafka</text>
        <rect x="400" y="20" width="110" height="40" rx="6" fill="#eaf4ff" stroke="#4a90e2"/>
        <text x="430" y="45">IoTDB</text>
        <path d="M120 40 L140 40" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M250 40 L270 40" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrow)"/>
        <path d="M380 40 L400 40" stroke="#4a90e2" stroke-width="2" marker-end="url(#arrow)"/>
        <defs>
          <marker id="arrow" markerWidth="10" markerHeight="10" refX="0" refY="3" orient="auto">
            <path d="M0,0 L0,6 L6,3 z" fill="#4a90e2" />
          </marker>
        </defs>
      </svg>
    </div>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Explain IoTDB strengths and how TSFile supports immutability and auditability.</aside>
</section>

---

<!-- Slide 7: TSFile -->
<section>
  <h2>Core Enabler: Apache TSFile</h2>
  <div class="comparison">
    <div class="col frag" data-fragment-index="1">
      <h4>Traditional Storage</h4>
      <ul>
        <li>Mutable files, patching allowed</li>
        <li>Hard to verify original record</li>
      </ul>
    </div>
    <div class="col frag" data-fragment-index="2">
      <h4>TSFile (Immutable)</h4>
      <ul>
        <li>Append-only blocks, tamper-evident</li>
        <li>Efficient validation boundaries</li>
      </ul>
    </div>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Contrast storage models and show why immutability helps with ALCOA++ and regulatory reviews.</aside>
</section>

---

<!-- Slide 8: Blueprint Architecture -->
<section>
  <h2>End-to-End Apache Pipeline</h2>
  <div class="pipeline">
    <div class="step">PLC4X</div>
    <div class="arrow">→</div>
    <div class="step">BifroMQ</div>
    <div class="arrow">→</div>
    <div class="step">Kafka</div>
    <div class="arrow">→</div>
    <div class="step">Flink / Beam</div>
    <div class="arrow">→</div>
    <div class="step">IoTDB (TSFile)</div>
    <div class="arrow">→</div>
    <div class="step">Iceberg (Cold)</div>
    <div class="arrow">→</div>
    <div class="step">Superset</div>
  </div>
  <pre class="code">
# Example Kafka -> IoTDB pipeline (conceptual)
producer.send(topic="sensor", key=tag, value=payload)
// Flink job validates, enriches, writes to IoTDB
  </pre>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Walk through each pipeline stage and highlight where validation and audit hooks are inserted.</aside>
</section>

---

<!-- Slide 9: Validation Strategy -->
<section>
  <h2>CSV with GAMP 5</h2>
  <ol class="fragment" data-fragment-index="1">
    <li>Define system boundaries & categorize software</li>
    <li>Risk assessment & requirements specification</li>
    <li>IQ/OQ/PQ test scripts for automation</li>
    <li>Continuous monitoring & supplier governance</li>
  </ol>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Explain how containerized open-source components fit GAMP 5 and how to structure IQ/OQ/PQ for pipelines.</aside>
</section>

---

<!-- Slide 10: Conclusion -->
<section>
  <h2>Key Takeaways</h2>
  <div class="takeaways">
    <div class="tk fragment" data-fragment-index="1"><h3>Open Source is Superior</h3><p>Transparency enables verifiable validation.</p></div>
    <div class="tk fragment" data-fragment-index="2"><h3>Power Combination</h3><p>IoTDB + TSFile + Iceberg = ALCOA++ architecture.</p></div>
    <div class="tk fragment" data-fragment-index="3"><h3>Act Now</h3><p>Migrate away from legacy tag licensing to scale compliantly.</p></div>
  </div>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Call to action: proof-of-concept migration & validation playbook.</aside>
</section>

---

<!-- Slide 11: Q&A -->
<section class="thank-you">
  <h2>Questions?</h2>
  <p>Thank you for attending — Lukas Ott</p>
  <p><a href="https://iotdb.apache.org/">https://iotdb.apache.org/</a></p>
  <div class="footer">CommunityOverCode 2026 • 2026-10-11</div>
  <aside class="notes">Invite questions and point to project resources and contact details.</aside>
</section>

<!-- Scripts: Chart.js for regulatory expansion chart -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<script>
// Regulatory expansion bar chart
const ctx = document.createElement('canvas');
ctx.id = 'regChartCanvas';
document.getElementById('regChart').appendChild(ctx);
new Chart(ctx.getContext('2d'), {
  type: 'bar',
  data: {
    labels: ['Annex 11 (old)', 'Annex 11 (new)', 'Annex 22'],
    datasets: [{
      label: 'Document size (words, approximate)',
      data: [1500, 10000, 1200],
      backgroundColor: ['#4a90e2', '#2c3e50', '#7fb3d5']
    }]
  },
  options: { responsive: true, maintainAspectRatio: false }
});
</script>
