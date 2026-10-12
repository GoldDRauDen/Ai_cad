# Customer CAD manufacturing rules — implementation checkpoint (2026-10-12)

Branch: `fix/customer-cad-rules-20261012`, based exclusively on PR #24 `refactor/rule-brain-20261012` commit `fe9e84d6063fcca1e4e87153737db10b81413ef0`. Do not merge to `main` without separate approval.

## Grounding and scope
- `CAD_顧客別 0911 .xlsm`: **ONLY** `顧客別情報一覧`; 469 rows, 107 numeric customers with entries in the technical-note/pierce columns J-M. Current catalog contains **25 individually curated codes**; it is NOT complete coverage of all relevant customer technical notes. Raw workbook, staff names, contact info, administrative and NC records are NOT committed.
- `伸び下穴経路一覧.xlsx`: ONLY `一覧表2026.07.30`, `旭26-9-18`, `アイコクアルファ`, `タップ下穴`, `皿ザグリ`. Finely pitched pilot table transcribes 94 source entries; course pitch remains existing table.
- Fixed SUS t3 L1801-2400 V40 2B 8.54 → **7.84**, #1 7.80. Default to 2B without surface note.
- SS >=19 R3 only OUTER contour including concave corners of outer contour; customer source overrides. Existing numeric Nobi algorithm untouched; handwritten Nobi is higher authority, mismatches only audited.
- Customer 646 standard tooling R3 (R0.6 for specified thin gauges); steel t4.5 V25/Nobi7.84, SUS t5 L751-1000 V40/Nobi10.20; missing Nobi/non-90 bend follows REVIEW/separate view.
- Correct customer-code routing is distinct from historical job-family '646' requiring DATA.
- Data-authoritative customers 829/240 skip numerical PDF/DATA dimensional conflict only, not missing or conflicting HOLE QA.
- Laser NC lead-in/out/joint/pierce starts explicitly deferred; only existing CAD PIERCING semantics remain active.

## Verification and limits
Tests added for customer routing, general fallback, reject inferred customer IDs, 646 Nobi, SS R3, fine-pitch and counterbore. Run all existing tests and V4.19-V4.33 approved regressions before treating the branch as production-ready. Any user file not explicitly authorized must never be opened. Remaining 82 J-M note-bearing customer codes need independent technical-only curation before claiming a complete workbook migration; a known customer whose technical exception was not curated must be checked against source when it is relevant. If source workbook unavailable, do not assert the customer has no exceptions.
