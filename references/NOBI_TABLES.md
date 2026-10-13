# Nobi Allowance Reference Tables

## Approved 2026-10-12 recalibration from `旭26-9-18`
Use the existing TrainAiCad unfolding formulas, NOT a new bend algorithm. `SUS` without documented 2B/#1 uses **2B** by default; an explicit #1 on source overrides. SUS304 t3 L1801–2400 V40 2B **7.84** (was erroneous 8.54) and #1 **7.80**. A legible handwritten PDF Nobi is higher authority and any table mismatch is an audit record, not QA REVIEW. 旭 Nobi does NOT backfill missing values for numeric customer code 646. Machine min L/Z is nonblocking feasibility WARN when proved geometry is correct. NC operations are excluded.


Source: approved V4.3 Nobi values, with approved L09 material-routing clarification on 2026-09-25. **SUS430 uses SS/SUS430/BRASS Nobi ONLY; use workbook group SUS, 他 for Laser R, hole limits and White Piercing in `references/MATERIAL_RULES.md`. All Nobi numbers remain unchanged.**

### 7.3 Nobi Allowance Standards Tables *(fully restored from V1 — including the previously-dropped Copper table and all intermediate L-brackets)*

#### 1. SS, SUS430, BRASS ($R=0.6$ for $t \le 4.5$, $R=3.0$ for $t=5.0 \sim 9.0$, $R=6.0$ for $t=12.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **0.5** | ~ 2400 | V8 | 1.36 |
| **0.8** | ~ 2400 | V8 | 1.68 |
| **1.0** | ~ 2400 | V8 | 1.90 |
| **1.2** | ~ 2400 | V8 | 2.14 |
| **1.5** | ~ 2400 | V8 | 2.54 |
| **1.6** | ~ 2400 | V8 | 2.64 |
| **2.0** | ~ 2400 | V12 | 3.44 |
| **2.3** | ~ 2400 | V12 | 3.80 |
| **3.0** | ~ 1000 | V12 | 4.66 |
| **3.0** | 1001 ~ 1900 | V18 | 5.28 |
| **3.0** | 1901 ~ 2400 | V25 | 5.98 |
| **3.2** | ~ 1800 | V18 | 5.50 |
| **3.2** | 1801 ~ 2400 | V25 | 5.72 |
| **4.0** | ~ 1200 | V18 | 6.42 |
| **4.5** | ~ 1200 | V25 | 7.76 |
| **4.5** | 1201 ~ 1600 | V32 | 8.10 |
| **4.5** | 1601 ~ 2300 | V40 | 8.48 |
| **5.0** | ~ 1000 | V25 | 8.32 |
| **5.0** | 1001 ~ 1300 | V32 | 9.04 |
| **5.0** | 1301 ~ 1600 | V40 | 9.86 |
| **6.0** | ~ 700 | V25 | 9.78 |
| **6.0** | 701 ~ 900 | V32 | 10.22 |
| **6.0** | 901 ~ 1150 | V40 | 10.94 |
| **9.0** | ~ 400 | V40 | 14.62 |
| **9.0** | 401 ~ 800 | V80 | 15.50 |
| **12.0**| ~ 550 | V80 | 20.48 |

#### 2. Stainless Steel (SUS Except SUS430) ($R=0.6$ for $t \le 5.0$, $R=3.0$ for $t=6.0 \sim 8.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi 2B (mm) | Nobi #1 (mm) |
| :--- | :--- | :--- | :--- | :--- |
| **0.5** | ~ 2400 | V8 | 1.36 | - |
| **0.8** | ~ 2400 | V8 | 1.82 | 1.74 |
| **1.0** | ~ 2400 | V8 | 2.14 | 1.94 |
| **1.2** | ~ 2400 | V8 | 2.32 | 2.18 |
| **1.5** | ~ 2400 | V8 | 2.64 | 2.54 |
| **2.0** | ~ 1300 | V12 | 3.68 | 3.50 |
| **2.0** | 1301 ~ 2400 | V18 | 4.00 | 4.18 |
| **2.5** | ~ 1300 | V12 | 4.24 | 4.08 |
| **2.5** | 1301 ~ 2000 | V18 | 5.06 | 4.78 |
| **2.5** | 2001 ~ 2400 | V25 | 5.84 | 5.52 |
| **3.0** | ~ 750 | V12 | 4.80 | 4.68 |
| **3.0** | 751 ~ 1250 | V18 | 5.64 | 5.36 |
| **3.0** | 1251 ~ 1800 | V25 | 6.46 | 6.10 |
| **3.0** | 1801 ~ 2400 | V40 | 7.84 | 7.80 |
| **4.0** | ~ 650 | V18 | 6.78 | 6.50 |
| **4.0** | 651 ~ 1000 | V25 | 7.66 | 7.28 |
| **4.0** | 1001 ~ 1650 | V40 | 8.44 | 8.90 |
| **4.5** | ~ 550 | V18 | 7.30 | 7.30 |
| **5.0** | ~ 550 | V25 | 8.82 | 8.46 |
| **5.0** | ~ 750 | V32 | 9.68 | 9.18 |
| **5.0** | 751 ~ 1000 | V40 | 10.74 | 10.06 |
| **6.0** | ~ 500 | V32 | 10.72 | 9.82 |
| **6.0** | 501 ~ 650 | V40 | 11.88 | 10.12 |
| **8.0** | ~ 350 | V40 | 14.06 | 13.50 |
| **8.0** | 351 ~ 700 | V80 | 19.46 | 16.94 |
| **9.0** | ~ 550 | V80 | 20.54 | 18.08 |

#### 3. Aluminum (AL) ($R=0.6$ for $t \le 4.0$, $R=3.0$ for $t \ge 5.0$)

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **0.8** | ~ 2400 | V8 | 1.84 |
| **1.0** | ~ 2400 | V8 | 1.90 |
| **1.5** | ~ 2400 | V8 | 2.40 |
| **2.0** | ~ 2400 | V12 | 3.20 |
| **3.0** | ~ 1200 | V12 | 4.56 |
| **3.0** | ~ 1900 | V18 | 4.78 |
| **3.0** | 1901 ~ 2400 | V25 | Confirm |
| **4.0** | ~ 1200 | V18 | 6.10 |
| **4.0** | 1201 ~ 1700 | V25 | 6.42 |
| **4.0** | 1701 ~ 2000 | V32 | 6.84 |
| **4.0** | 2001 ~ 2400 | V40 | 7.40 |
| **5.0** | ~ 1000 | V25 | 8.26 |
| **5.0** | 1001 ~ 1300 | V32 | 8.44 |
| **5.0** | 1301 ~ 1600 | V40 | 8.74 |
| **6.0** | ~ 700 | V25 | 9.62 |
| **6.0** | 701 ~ 900 | V32 | 9.80 |
| **6.0** | 901 ~ 1150 | V40 | 10.06 |
| **8.0** | ~ 650 | V40 | 12.78 |
| **8.0** | 651 ~ 800 | V80 | 14.90 |
| **9.0** | ~ 400 | V40 | 14.12 |
| **9.0** | 401 ~ 800 | V80 | 16.20 |
| **10.0**| ~ 800 | V80 | 17.52 |

#### 4. Copper (Cu) *(restored — was missing from V2 entirely)*

| $t$ (mm) | Bend Length $L$ (mm) | V-Die | Nobi Deduction (mm) |
| :--- | :--- | :--- | :--- |
| **3.0** | ~ 1900 | V18 | 5.10 |

> **Note (`3.0mm / 1901~2400 / V25` for Aluminum, row above)**: Source table marks this cell `Confirm` — no numeric Nobi value available. Per Section 4.7 Rule 4 (No Table Match), treat as `is_flagged = true` and maintain flat blank at OD.

---
