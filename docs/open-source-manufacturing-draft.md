title: "Open Source for Regulated Manufacturing"
subtitle: "GMP‑Compliant IIoT Data Logging with Apache IoTDB"
author: "Lukas Ott"
event: "CommunityOverCode 2026"
date: "2026-10-11"
theme: "white"
highlightTheme: "github"
revealOptions:
  controls: true
  progress: true
  history: true
  center: true
  slideNumber: true
---

<!-- ####################### -->
<!-- Slide 1: Title (CommunityOverCode 2026) -->
<!-- ####################### -->

# **Open Source for Regulated Manufacturing**
## *GMP‑Compliant IIoT Data Logging with Apache IoTDB*

- **Speaker:** Mr. Lukas Ott, Enterprise Architect
- **Track:** IIoT & Data Strategy (CommunityOverCode 2026)
- **Theme:** Building scalable, auditable, and compliant IIoT data platforms with ASF technologies.

**Visual:** Title slide with gradient background (e.g., `#0066cc` → `#003366`)

---

<!-- ####################### -->
<!-- Slide 2: The Hook (CommunityOverCode 2026) -->
<!-- ####################### -->

## **The 2026 Regulatory Storm**

- **Annex 11 Overhaul:**
  - Massive text expansion (1,500 → 10,000 words)
  - Demands **explicit IT security**, **cloud control**, and **absolute data integrity**
- **The New Annex 22:**
  - Governance for **AI-supported systems** in GMP environments
- **The Collision:**
  - High-frequency **IIoT industrial data velocity** meets the **strictest compliance era**

---

<!-- ####################### -->
<!-- Slide 3: Core Framework (FDA vs. EU) -->
<!-- ####################### -->

## **Compliance in 60 Seconds: FDA vs. EU**

### **🇺🇸 FDA 21 CFR Part 11 (US Regulation)**
- Asks: *"Are your electronic records and signatures trustworthy?"*
- Requires:
  - Secure system validation
  - Unalterable time-stamped audit trails
  - Training

### **🇪🇺 EU Annex 11 (GMP Guideline)**
- Asks: *"Is your entire computerized system lifecycle validated and controlled?"*
- Requires:
  - Full risk management
  - Validation testing
  - Supplier governance
  - **ALCOA+ data integrity**

### **The Unified Goal**
Moving safely from **paper to compliant, audit-ready digital processes**

**Visual:** Side-by-side comparison of FDA and EU requirements

---

<!-- ####################### -->
<!-- Slide 4: The Core Problem (Traditional Historians) -->
<!-- ####################### -->

## **The Traditional Historian "Tax"**

### **Commercial Constraints**
- Proprietary volume-based and per-tag licensing
- **Vendor lock-in** that limits scaling
- High costs for validation and customization

### **Architectural Limitations**
- Rigid data models with **limited metadata lineage**
- Weak native audit capabilities → requires heavy customization for **ALCOA+**
- Poor integration with modern streaming and analytics

### **The Burning Question**
*Can open source serve as a reliable, highly compliant backbone for a modern industrial historian?*

---

<!-- ####################### -->
<!-- Slide 5: The Standard of Truth (ALCOA++) -->
<!-- ####################### -->

## **Elevating to ALCOA++**

### **ALCOA Framework**
- **Attributable**
- **Legible**
- **Contemporaneous**
- **Original**
- **Accurate**

### **ALCOA+ (Added)**
- **Complete**
- **Consistent**
- **Enduring**
- **Available**

### **ALCOA++ (The 2026 Shift)**
Focuses explicitly on:
- **System Integrity**
- **Technical Robustness**
- **Architectural Transparency**
- **Personal Accountability**
- **System Reliability**

### **The Open Source Angle**
- **Community governance** bridges transparency and cross-sector auditability
- **Verifiable validation** replaces black-box systems

**Visual:** ALCOA → ALCOA+ → ALCOA++ infographic

---

<!-- ####################### -->
<!-- Slide 6: The Secret Weapon (Apache IoTDB) -->
<!-- ####################### -->

## **Apache IoTDB as a GMP Historian**

### **Purpose-Built for IIoT**
- Designed for **extreme time-series ingestion rates**
- Optimized for **high-frequency industrial PLC sensors**

### **Security-Hardened**
- **Authentication & Authorization** (RBAC)
- **Encryption** (at rest & in transit)
- **Automated retention management**

### **UN Recognition**
- **Top 60 Global Innovation Cases** by the **United Nations STI Forum**
- [Apache IoTDB Project](https://iotdb.apache.org/)

**Visual:** IoTDB logo and UN STI Forum badge

---

<!-- ####################### -->
<!-- Slide 7: Unbending Ledger (Apache TSFile) -->
<!-- ####################### -->

## **Core Enabler: Apache TSFile**

### **Immutable by Design**
- **Append-only model** on disk
- Records **cannot be modified silently** without breaking validation

### **Data Segmentation**
- Structuring raw storage into blocks enables:
  - Targeted validation boundaries
  - Efficient regulatory spot reviews

### **Future-Proofing**
- Bridges **hot operational time-series data** into **cold data lakes**
- Seamless integration with **Apache Iceberg**

**Visual:** TSFile architecture diagram

---
<!-- ####################### -->
<!-- Slide 8: Blueprint Architecture (End-to-End Pipeline) -->
<!-- ####################### -->

## **The End-to-End Apache Pipeline**

```mermaid
graph TD
  A[Industrial Equipment] -->|OPC-UA/MQTT| B[Apache PLC4X]
  B --> C[Apache BifroMQ]
  C --> D[Apache Kafka]
  D --> E[Apache Flink/Beam]
  E --> F[Apache IoTDB]
  F -->|TSFile| G[Apache Iceberg]
  G --> H[Apache Superset]

### **Key Components**

| Component            | Function                                      |
|----------------------|-----------------------------------------------|
| Apache PLC4X         | Industrial protocol integration (OPC-UA/MQTT) |
| Apache BifroMQ       | High-throughput MQTT broker                   |
| Apache Kafka         | Real-time data streaming                     |
| Apache Flink/Beam    | Real-time compliance validation               |
| Apache IoTDB         | High-availability hot historian (TSFile)      |
| Apache Iceberg       | Cold data lake catalog                        |
| Apache Superset      | Compliance-ready BI & analytics               |

---

### **Computer System Validation (CSV) with GAMP 5**

#### **Framework Mapping**
Aligning containerized open-source projects under GAMP 5 software categories:

| System Boundary      | Isolation for:                                  |
|----------------------|-------------------------------------------------|
| Risk Assessment      | (Step 1)                                        |
| Requirements Specifications | (Step 3)                                |
| Lifecycle Validation |                                                 |
| IQ/OQ/PQ             | Installation/Operation/Performance Qualification |