# KH 646 — customer bend Nobi
Source: `伸び下穴経路一覧.xlsx`, `アイコクアルファ`. Apply **only if numeric customer_code=646** on the job statistics sheet. Do not confuse with unrelated historical job-family '646' DATA handling.

## Standard steel (90° bend default)
| t | punch R | V | Nobi | min L | source cells |
|---:|---:|---|---:|---:|---|
|0.8|0.6|V8|1.68|7.5|B10:B15|
|1.2|0.6|V8|2.14|7.5|C10:C15|
|1.6|0.6|V8|2.64|7.5|D10:D15|
|2.3|3|V18|4.62|12.8|E10:E15|
|3.2|3|V18|5.78|12.8|F10:F15|
|4.5|3|V25|7.84|17.8|G10:G15|
|6|3|V25|9.78|17.8|I10:I15|
|9|3|V40|14.62|28.4|J10:J15|
|12|6|V80|20.48|57|K10:K15|

For explicitly ordered R2 tooling ONLY: t2.3 R2/V18 Nobi4.44, t3.2 R2/V18 Nobi5.56, t4.5 R2/V25 Nobi7.72 (C4:F8). When a near-bend hole deforms, t4.5 R3/V18 Nobi7.48/minL12.8 is listed in H9:H15, but **do not infer** tooling change merely from proximity.

## SUS304
| t | punch R | V | Nobi | L range | source |
|---:|---:|---|---:|---|---|
|1|0.6|V8|2.14|standard|B20:B24|
|2|0.6|V12|3.68|standard|C20:C24|
|3|3|V18|5.70|standard|D20:D24|
|5|3|V32|9.58|L ≤750 mm (approved application)|E20:E24|
|5|3|V40|10.20|751–1000 mm|F20:F24|
|6|3|V32|10.72|standard|G20:G24|
|9|6|V80|19.08|standard|H20:H24|

R10 special steel: t0.8/V25/Nobi5.44, t1.2/V25/Nobi6.02; t2.3/3.2/4.5 are 確認 (REVIEW). R10 SUS304 t4 Nobi10.06. R10 machine reach/shape restrictions are manufacturing WARN if shape otherwise proved. For missing Nobi or out-of-range length, local REVIEW, **no** fallback to general 旭 Nobi. For unclear non-90° bend, retain separate views for manual reassembly, not 90° Nobi. Clear handwritten PDF Nobi overrides this table; difference recorded only as nonblocking evidence.
