---
title: Open Source for Regulated Manufacturing
subtitle: GMP‑Compliant IIoT Data Logging with Apache IoTDB
author: Lukas Ott
event: CommunityOverCode 2026
date: 2026-10-11
---

# Slide 1: Title
## Open Source for Regulated Manufacturing
### GMP‑Compliant IIoT Data Logging with Apache IoTDB

* **Speaker:** Mr. Lukas Ott, Enterprise Architect
* **Track:** IIoT & Data Strategy (CommunityOverCode 2026)
* **Theme:** Building scalable, auditable, and compliant IIoT data platforms with ASF technologies.

---

# Slide 2: The Hook
## The 2026 Regulatory Storm

* **Annex 11 Overhaul:** Massive text expansion (1,500 to 10,000 words) demanding explicit IT security, cloud control, and absolute data integrity.
* **The New Annex 22:** Newly introduced specifically to govern and enforce AI-supported systems inside GMP environments.
* **The Collision:** High-frequency IIoT industrial data velocity meeting the absolute strictest compliance era in modern history.

---

# Slide 3: Core Framework
## Compliance in 60 Seconds: FDA vs. EU

* **🇺🇸 FDA 21 CFR Part 11 (US Regulation)**
  * Asks: *"Are your electronic records and signatures trustworthy?"*
  * Requires: Secure system validation, unalterable time-stamped audit trails, and training.
* **🇪🇺 EU Annex 11 (GMP Guideline)**
  * Asks: *"Is your entire computerized system lifecycle validated and controlled?"*
  * Requires: Full risk management, validation testing, supplier governance, and ALCOA+ data integrity.
* **The Unified Goal:** Moving safely away from paper into compliant, audit-ready digital processes.

---

# Slide 4: The Core Problem
## The Traditional Historian "Tax"

* **Commercial Constraints:** 
  * Proprietary volume-based and per-tag licensing structures.
  * Vendor lock-in patterns that choke out scaling efforts.
* **Architectural Limitations:**
  * Rigid operational data models lacking deep metadata lineage.
  * Weak native audit capabilities, requiring heavily customized add-on layers for ALCOA+.
* **The Burning Question:** Can open source serve as a reliable, highly compliant backbone for a modern industrial historian?

---

# Slide 5: The Standard of Truth
## Elevating to ALCOA++

* **ALCOA:** Attributable, Legible, Contemporaneous, Original, Accurate.
* **ALCOA+:** Adds Complete, Consistent, Enduring, and Available to the life cycle framework.
* **ALCOA++ (The 2026 Shift):** Focuses explicitly on system **Integrity**, technical **Robustness**, architectural **Transparency**, personal **Accountability**, and system **Reliability**.
* **The Open Source Angle:** Community governance natively bridges transparency and cross-sector auditability constraints.

---

# Slide 6: The Secret Weapon
## Apache IoTDB as a GMP Historian

* **Purpose-Built:** Crafted intentionally for extreme time-series ingestion rates and high-frequency industrial PLC sensors.
* **Security-Hardened:** Out-of-the-box user access controls (authentication, authorization), encryption layers, and automated retention management.
* **UN Recognition:** Formally selected as one of the **Top 60 Global Innovation Cases** by the United Nations STI Forum for real-time monitoring and data preservation.

---

# Slide 7: Unbending Ledger
## Core Enabler: Apache TSFile

* **Immutable by Design:** TSFile uses an unchangeable append-only model on disk, creating a resilient environment where records cannot be modified silently without breaking validation.
* **Data Segmentation:** Structuring raw storage into blocks directly allows targeted validation boundaries and efficient regulatory spot reviews.
* **Future-Proofing:** Bridges hot operational time-series data seamlessly into massive cold data lakes when integrated with an Apache Iceberg catalog.

---

# Slide 8: Blueprint Architecture
## The End-to-End Apache Pipeline

* **Ingestion/Edge:** Industrial equipment protocols communicate via **Apache PLC4X** directly into high-throughput **Apache BifroMQ** (MQTT broker).
* **Processing:** **Apache Kafka** pipelines real-time data streams into **Apache Flink** or **Apache Beam** for real-time compliance validation checking.
* **Storage:** **Apache IoTDB** acts as the high-availability hot historian, writing immutable **TSFiles** that pass downstream into **Apache Iceberg**.
* **Analytics/BI:** Compliance officers securely run reproducible queries utilizing **Apache Superset**.

---

# Slide 9: Validation Strategy
## Computer System Validation (CSV) with GAMP 5

* **Framework Mapping:** Aligning containerized open-source projects safely under GAMP 5 software categorization layers.
* **System Boundaries:** Clearly defining component isolation to ease structural Risk Assessment (Step 1) and Requirements Specifications (Step 3).
* **Lifecycle Validation:** Executing repeatable Installation, Operational, and Performance Qualification (IQ/OQ/PQ) testing scripts against the open architecture.

---

# Slide 10: Conclusion
## Key Takeaways

1. **Open Source is Superior:** The inherent transparency of open architectures like the ASF ecosystem makes data validation completely verifiable rather than a black box.
2. **The Power Combination:** Combining Apache IoTDB, TSFile, and Iceberg builds a bulletproof, modern, and cost-effective ALCOA++ architecture.
3. **Act Now:** Break out of legacy historian tag-licensing bottlenecks to survive the modern regulatory shift.

---

# Slide 11: Q&A
## Open Source for Regulated Manufacturing

* Thank you for attending!
* **Speaker:** Lukas Ott, Enterprise Architect
* **Project Details:** https://iotdb.apache.org/
* *Questions from the audience are welcome.*