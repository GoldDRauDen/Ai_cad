# plan_claude_fix.md — Kiểm toán TrainAiCad và kế hoạch sửa

- Repo: `GoldDRauDen/TrainAiCad`, nhánh `main`, commit `7c78d3c` (V4.34 CAD reliability)
- Phạm vi: đọc toàn bộ entry point, router, coverage, tool, test, workflow CI; chạy các công cụ có sẵn của repo.
- Trạng thái: **chỉ là kế hoạch**. Không sửa rule production, không commit, không push. Theo `AGENTS.md` §6, mọi thay đổi production cần user duyệt (`DUYỆT` / `PUSH`).

---

## 0. Kết luận ngắn

1. **Đây không phải RAG.** Không có embedding, vector hay BM25 nào trong repo (đã grep `tools/` và `services/`). Cơ chế thực tế: AI đọc `SKILL.md` → `AI_BOOTSTRAP.md` → `AI_ENTRYPOINT.md` → `ROUTER.yaml`, rồi tự mở các file markdown theo đường dẫn router liệt kê. `tools/build_rule_index.py` tạo `RAG_INDEX.yaml` nhưng docstring của chính nó ghi rõ "not vector search". Tên gọi này gây hiểu lầm và nên đổi.
2. **Hệ thống chạy được về mặt kỹ thuật** (245/245 test pass, `audit_rule_coverage` PASS, resolver tất định hoạt động). Tuy nhiên có **3 lỗi có thể khiến AI bỏ qua rule thật** mà không có test nào bắt được.
3. **Chi phí token rất lớn**: riêng rule đã tốn khoảng 60k–105k token mỗi job, trước khi AI mở PDF. Benchmark của repo cũng thừa nhận phần "tiết kiệm" chỉ áp dụng cho giai đoạn khởi động.
4. **Có một rủi ro engineering cần kỹ sư xác nhận**: gộp `SECC = ボンデ → SS` trong `AI_ENTRYPOINT.md`.

---

## 1. Các lỗi nghiêm trọng (Critical)

### F1 — Rule V4.34 không được nối vào router
- **Bằng chứng:** `MATERIAL_ALIASES.yaml`, `material_resolver.py`, `slot_anchor.py`, `dimension_witness.py`, `CANONICAL_INPUT_SCHEMA_V434.md` không xuất hiện trong `ROUTER.yaml`, `RULE_COVERAGE.yaml`, `FEATURE_CENSUS.md`. Chỉ có `MATERIAL_ALIASES` được nhắc trong đầu `AI_ENTRYPOINT.md`.
- **Hệ quả:** một AI đi theo router sẽ không bao giờ nạp bảng alias vật liệu, quy tắc HL/grain, quy tắc witness/slot anchor. `ROUTER.yaml` vẫn ghi `release: V4.33`.
- **Vì sao không ai phát hiện:** `audit_rule_coverage.py` chỉ kiểm tra block `V4.33`, nên báo PASS giả. Commit V4.34 đã thêm 19 file (code + test + vài dòng con trỏ) nhưng **không sửa router**.
- **Cách tái hiện:** `grep -c MATERIAL_ALIASES skills/lispcad/router/ROUTER.yaml` → `0`.

### F2 — Hai contract song song, gate V4.34 có thể bị bỏ qua
- **Bằng chứng:** `tools/canonical_contract.py` chấp nhận cả `TrainAiCad-CANONICAL-V4.31` và `V4.34` (`SUPPORTED_CONTRACTS`). Toàn bộ kiểm tra vật liệu, HL grain, witness bắt buộc, và `REVIEW` có điều kiện chỉ chạy trong nhánh `if contract == CONTRACT_V434:` (khoảng dòng 204–230).
- **Hệ quả:** một job tự khai `canonical_contract: V4.31` sẽ **bỏ qua hoàn toàn** các gate V4.34, và exporter không cảnh báo gì. Trong khi đó tài liệu mâu thuẫn: `AI_ENTRYPOINT.md` dòng 2 nói "job mới dùng V4.34", còn §2 dòng 94 nói "V4.33 … tiếp tục dùng V4.31". AI sẽ chọn theo câu nào nó đọc trước.
- **Mức độ:** đây là "bỏ qua rule" theo nghĩa đen. Cần sửa về mặt code, không chỉ sửa tài liệu.

### F3 — Định danh release không nhất quán
| Nguồn | Giá trị |
|---|---|
| `ROUTER.yaml`, `RULE_COVERAGE.yaml` | `V4.33` |
| `AI_ENTRYPOINT.md` dòng 6 | "Current production release is **V4.33**" |
| `AI_ENTRYPOINT.md` dòng 1–2 | "supplement V4.34", job mới dùng V4.34 |
| `SKILL.md` dòng 75 | schema `V431` |
| `AI_ENTRYPOINT.md` §2 | "V4.33 … tiếp tục V4.31" |
| `skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md` | `V4.24` |

Không có "nguồn chân lý" duy nhất cho release. Các lỗi F1, F2, F5 đều bắt nguồn từ đây.

### F4 — Test và audit xanh giả (false green)
- 245/245 test pass nhưng có **khoảng 31/39 file test không import code tool nào** (heuristic: chỉ đọc văn bản). Ví dụ `test_v431_release_wiring` chỉ kiểm tra chuỗi `"- **V4.31:**" in entry`.
- Không có test nào kiểm tra: (a) mọi tool có tác động CAD đã được route hay được đánh dấu audit-only; (b) release trong router = release trong entry point = release trong MCP; (c) job mới mặc định dùng contract mới nhất.
- Hệ quả: CI xanh không chứng minh được AI sẽ áp dụng đúng rule.

---

## 2. Lỗi mức cao (High)

### F5 — Pin release của MCP chắc chắn lỗi (theo code, chưa chạy)
- `services/trainaicad-mcp/src/core.ts` `readReleasePin()`: so khớp `Current production release is **V4.33**` (từ `AI_ENTRYPOINT.md`) với header `# SKILL_LISPCAD V4.24 PORTABLE` (từ `CURRENT`). Hai giá trị khác nhau nên hàm **luôn throw** `SKILL_FRESHNESS_UNVERIFIED`.
- MCP README vẫn quảng cáo "Runtime production-release pinning". MCP được ghi là research-only, nên đây là lỗi thấp về ảnh hưởng production nhưng là dấu hiệu rõ của việc "snapshot portable" đang được coi là authority.
- Cần chạy `npm test` trong `services/trainaicad-mcp` để xác nhận trước khi sửa.

### F6 — Gộp vật liệu SECC/ボンデ vào nhóm SS (rủi ro engineering)
- `AI_ENTRYPOINT.md` dòng 2 ghi "SECC=ボンデ → SS". `references/MATERIAL_ALIASES.yaml` lại ghi rõ các nhóm là "process routing, NOT assertions of chemical equivalence". `MATERIAL_RULES.md` dòng 18 cũng ghi "this routing is not proof that different exact grades are interchangeable".
- Góc nhìn kỹ sư kim loại tấm: SECC (mạ kẽm điện, thép mềm cỡ SPCC) và SS400 (thép cán nóng kết cấu) khác nhau về cường độ, độ đàn hồi hồi phục (springback), hệ số K và bán kính uốn tối thiểu. Nhóm SS cũng gom SK (thép dụng cụ, rất cứng) và S45C/S48C (thép carbon trung bình/cao), vốn có khả năng uốn rất khác nhau.
- Hiện repo **chưa thấy** bảng hệ số K/springback nào tra theo nhóm (đã kiểm tra `MATERIAL_RULES.md`). Vì vậy rủi ro hiện tại thấp hơn mô tả, nhưng câu trong `AI_ENTRYPOINT.md` quá mạnh và có thể bị hiểu là tương đương vật lý. **Cần kỹ sư/user xác nhận.**

### F7 — Resolver tất định là tùy chọn, và phụ thuộc census đầy đủ
- `SKILL.md` §2.3 và `AI_BOOTSTRAP.md` §2.6 cho phép bỏ qua `tools/resolve_rules.py` nếu thiếu Python/PyYAML, khi đó "follow the Router directly". Đây là đường dẫn thủ công, dễ sai.
- Resolver yêu cầu census đầy đủ 21 family. Census thiếu → `ROUTING_COVERAGE_GAP` (hành vi đúng), nhưng AI phải tự sinh đủ 21 khóa mỗi lần, rất dễ lệch.
- Schema census (`FEATURE_CENSUS.md` dòng 91–119) và `customer_code`, `reference_present` đang nằm rải rác ở ba nơi.

---

## 3. Chi phí token (đo được)

Đo bằng `tools/resolve_rules.py` và `tools/benchmark_rule_routes.py` (byte UTF-8 chính xác; token ước lượng ≈ byte ÷ 3,5 vì tài liệu trộn tiếng Nhật/Việt/Anh).

| Kịch bản | L0+L1 (khởi động) | Toàn bộ L0–L3 | Ước lượng token (toàn bộ) |
|---|---|---|---|
| flat | 142.639 B | 218.134 B | ~62k |
| flat + TAP | 142.639 B | 243.365 B | ~70k |
| bend + NOBI | 142.639 B | 296.426 B | ~85k |
| data + holes | 165.450 B | 261.916 B | ~75k |
| unknown / phức tạp | 165.450 B | 369.877 B | ~106k |

Ghi chú: benchmark ghi rõ "savings shown are startup/stage-specific only; full-job cumulative context may be close to previous eager loading". Tức là phần giảm 34–55% chỉ đúng lúc khởi động, không đúng cho cả job.

Các nguồn lãng phí cụ thể:

- **F8 — Khối luật luôn nạp (always-on):** `DRAWING_READING.md` 28 KB, nằm trong `default_load`.
- **F9 — `AI_ENTRYPOINT.md` 27,6 KB:** gồm §7 là chỉ mục release từ V4.3 đến V4.34 (lịch sử, không phải chỉ dẫn). Được đọc đầy đủ mỗi job. Tự ghi "not an instruction to load every listed regression" nhưng vẫn nằm trong đường đọc bắt buộc.
- **F10 — `RULE_COVERAGE.yaml` 9 KB:** file tự khai là "audit map, not an instruction to load every file", nhưng `AI_ENTRYPOINT.md` §1 và `AGENTS.md` bước 3 lại liệt kê là bắt buộc đọc.
- **F11 — Tám tài liệu entry trùng lặp:** `AGENTS.md`, `SKILL.md`, `AI_BOOTSTRAP.md`, `AI_ENTRYPOINT.md`, `README.md`, `QA_ENTRYPOINT.md`, `PROJECT_INSTRUCTIONS_GPT_WEB.md`, `docs/RULE_BRAIN.md` đều mô tả lại trình tự bootstrap với cách diễn đạt hơi khác. AI thường đọc 3–5 file trong số này, mỗi file một chút.
- **F12 — Nhân bản theo số code (chưa đo):** rule là theo job nhưng công việc là theo từng mã. Nếu AI nạp lại rule cho mỗi mã thì chi phí nhân lên theo số mã. Cần đo trên một job nhiều mã.

---

## 4. Vệ sinh repo (Medium/Low)

- **F13 — 3,6 MB trong `skills/`:** 22 bản snapshot trong `versions/` và `portable/SKILL_LISPCAD_CURRENT.md` **giống hệt byte-for-byte** `versions/V4.24` (cùng md5 `53bc8796…`). CURRENT đã lệch 10 release so với V4.33/V4.34. Không được nạp mặc định nên không tốn token, nhưng bản V4.24 làm công cụ chẩn đoán `ROUTING_COVERAGE_GAP` đưa ra kết luận sai cho các rule V4.25+. CURRENT vẫn bị sửa trong 24 trên 300 commit gần nhất dù không phải authority.
- **F14 — Tên gọi gây hiểu lầm:** `build_rule_index.py` tạo `RAG_INDEX.yaml`. Đổi thành `ROUTE_INDEX.yaml`.
- **F15 — Tool chưa được route:** `slot_anchor.py`, `cut_orientation.py`, `export_job_artifacts.py`, `datum_coordinates.py`, `error_catalog.py` không được router nhắc tới. Ba tool đầu có ảnh hưởng đến output CAD nên cần route hoặc đánh dấu rõ là audit-only. (Các tool `audit_*`, `benchmark_*`, `build_*` thì đúng là không cần route.)
- **F16 — Quy trình không có chốt chặn:** không có kiểm tra "module mới ⇒ phải có trong router + coverage + test". Đây là nguyên nhân trực tiếp của F1.
- **F17 — Churn cao ở đúng chỗ rủi ro nhất:** `AI_ENTRYPOINT.md` 40 commit, `ROUTER.yaml` 21, `RULE_COVERAGE.yaml` 14 (trên 271 commit). Ba file này phải luôn đồng bộ với nhau nhưng không có cơ chế bắt buộc.
- **F18 — Python deps chưa khóa:** `requirements.txt` dùng khoảng (`ezdxf>=1.4,<2`), không có lock. Output DXF có thể khác nhau giữa các máy/CI.

### Điểm tốt đáng giữ
- Resolver tất định, có kiểm tra `ROUTING_COVERAGE_GAP` khi census lệch router.
- `audit_rule_coverage` kiểm tra `unreachable_active_modules` và `audit_rule_duplicates` kiểm tra trùng đoạn văn.
- Test V4.34 (`test_v434_material_witness_slot_orientation.py`) thực thi code thật, không chỉ grep.
- Tách rõ customer code với job family code; không có mã job hardcode trong `tools/`.
- Nguyên tắc "PDF điều khiển ngữ nghĩa, DATA điều khiển hình học", và "source-only snapshot trước reference" là thiết kế đúng.

---

## 5. Kế hoạch triển khai

Mỗi giai đoạn có tiêu chí chấp nhận rõ ràng. Giai đoạn 1 trở đi **cần `DUYỆT`** theo `AGENTS.md` §6.

### Giai đoạn 0 — Quyết định của user (không đổi file)
Cần trả lời trước khi làm:
1. **Contract mặc định cho job mới**: V4.34 (khuyến nghị) hay V4.31? Nếu V4.34 thì các fixture V4.31 cũ giữ nguyên theo đường `legacy_fixture`.
2. **SECC/ボンデ → SS**: kỹ sư xác nhận đây chỉ là nhóm gia công/tra cứu Laser R-hole, hay có ảnh hưởng đến uốn. Nếu có ảnh hưởng thì cần bảng hệ số K/springback theo mác, không theo nhóm.
3. **MCP**: sửa `readReleasePin` hay tạm tắt để tránh gây hiểu nhầm?
4. **Snapshot `versions/` và `portable/`**: chuyển sang tag/archive branch (giữ lịch sử, bỏ khỏi cây làm việc) hay giữ nguyên?

### Giai đoạn 1 — Đóng lỗ hổng routing và contract (F1, F2, F3, F15)
**Thay đổi:**
- Thêm block `V4.34` vào `ROUTER.yaml` (release, `default_load` hoặc `stage_routes` cho `MATERIAL_ALIASES`, `dimension_witness`, `slot_anchor`, `CANONICAL_INPUT_SCHEMA_V434`) và `RULE_COVERAGE.yaml` (block V4.34 + regression/test). Đổi `release` sang `V4.34`.
- Trong `canonical_contract.py`: với job mới, từ chối `V4.31` trừ khi có cờ `legacy_fixture: true` được ghi rõ. Không để im lặng bỏ qua gate.
- Route hoặc đánh dấu rõ các tool F15.

**Kiểm tra chấp nhận:**
- Test mới: `ROUTER.yaml` chứa mọi file được `tools/*.py` import hoặc tham chiếu có tác động CAD (trừ danh sách audit-only khai báo tường minh).
- Test mới: job mới khai `V4.31` bị từ chối; job `V4.34` có `SECC` và `HL` không có grain bị REVIEW đúng.
- `audit_rule_coverage.py` phải fail nếu một module V4.34 không có trong coverage (hiện nó PASS giả).
- Toàn bộ 245 test cũ vẫn pass; các fixture V4.31 đã duyệt vẫn pass nhờ đường `legacy_fixture`.

### Giai đoạn 2 — Một nguồn chân lý cho release (F3, F5, F11)
- Chọn `ROUTER.yaml` làm nguồn release duy nhất. `AI_ENTRYPOINT.md` chỉ có một dòng header sinh tự động hoặc được test kiểm tra khớp.
- Cập nhật con trỏ schema trong `SKILL.md` (V431 → V434).
- Test "đồng bộ phiên bản": `ROUTER`, `RULE_COVERAGE`, `AI_ENTRYPOINT`, `SKILL.md`, `readReleasePin` phải cùng một giá trị.
- Rút gọn `AGENTS.md`, `README.md`, `QA_ENTRYPOINT.md`, `PROJECT_INSTRUCTIONS_GPT_WEB.md` thành con trỏ ≤ 40 dòng tới `SKILL.md` + `ROUTER.yaml`. Không lặp lại trình tự bootstrap.
- Sửa MCP theo quyết định ở Giai đoạn 0.

### Giai đoạn 3 — Giảm token mà không giảm tuân thủ (F8–F12)
- Chuyển §7 của `AI_ENTRYPOINT.md` (chỉ mục release) và phần lịch sử sang `docs/RELEASE_INDEX.md`, không nằm trong đường đọc bắt buộc. Mục tiêu `AI_ENTRYPOINT.md` ≤ 8 KB.
- Bỏ `RULE_COVERAGE.yaml` khỏi danh sách đọc bắt buộc; giữ như công cụ audit.
- Xem xét tách `DRAWING_READING.md` 28 KB thành các phần nạp theo census (cần đánh giá rủi ro vì nó là always-on).
- Thêm **ngân sách token** vào test: `benchmark_rule_routes.py` phải fail nếu L0+L1 vượt ngưỡng đặt trước (ví dụ ≤ 110 KB) hoặc toàn bộ job vượt ngưỡng đã chốt.
- Đo F12 trên một job nhiều mã trước và sau khi sửa.

**Rủi ro:** thay đổi nội dung nạp có thể làm thay đổi output CAD. Phải chạy toàn bộ regression và so sánh output trên ít nhất hai job đã duyệt trước khi merge.

### Giai đoạn 4 — Chuyển test từ grep văn bản sang hành vi (F4)
- Với 31 file test chỉ grep văn bản: giữ lại nhưng thêm test hành vi tương ứng gọi tool trên fixture trong `regression/`.
- Thêm test "routing completeness" và test "không có module V4.x nào thiếu trong coverage" (sửa cho F1).
- Mục tiêu: mỗi release mới phải có ít nhất một test chạy code thật, không chỉ kiểm tra chuỗi.

### Giai đoạn 5 — Rà soát engineering (F6)
- Kỹ sư xác nhận bảng nhóm vật liệu và phạm vi dùng của từng nhóm (tra Laser R, hole, Nobi, bán kính uốn, springback, K).
- Nếu nhóm SS ảnh hưởng đến uốn: tạo bảng theo **mác cụ thể**, không theo nhóm. Đây là thay đổi production nên cần `DUYỆT` riêng, kèm regression.
- Giữ nguyên quy tắc HL: không có grain chứng minh được thì REVIEW.

### Giai đoạn 6 — Vệ sinh repo (F13, F14, F17, F18)
- Đổi `build_rule_index.py` output sang `ROUTE_INDEX.yaml`.
- Xử lý snapshot theo quyết định ở Giai đoạn 0 (tag/archive), giảm `skills/` về phần đang dùng.
- Khóa phiên bản Python deps (lock file), để output DXF tái lập được.
- Thêm checklist bắt buộc khi thêm module: router + coverage + test + tool route, kiểm tra bằng CI.

### Giai đoạn 7 — Kiểm chứng cuối bằng một job thật
- Chạy E2E trên một job đã duyệt (ví dụ fixture `521007-07`) trước và sau cải tiến.
- Đo: số byte rule thực nạp, số lần AI mở file ngoài danh sách router, có hay không rule V4.34 được áp dụng, output DXF có giống baseline không.
- Chỉ đóng kế hoạch khi tất cả chỉ số đạt.

---

## 6. Rủi ro tổng thể

- **Đổi router có thể đổi output CAD.** Bắt buộc có regression so sánh trước khi merge.
- **Ép V4.34 cho job mới** có thể làm một số job đang chạy dở bị từ chối. Cần đường `legacy_fixture` và thông báo cho user.
- **Cắt token có thể làm AI bỏ qua rule** nếu cắt sai chỗ. Đo tuân thủ trước khi cắt, không cắt theo cảm tính.
- **Các thay đổi production (rule, bảng vật liệu)** không được làm trong lúc chạy E2E. Theo `AGENTS.md` §6, chỉ làm sau `DUYỆT`.

---

## 7. Phụ lục — Cách tái kiểm chứng

```bash
cd /home/claude/trainaicad
grep -c MATERIAL_ALIASES skills/lispcad/router/ROUTER.yaml        # F1 → 0
python3 -m pytest -q -p no:cacheprovider                          # 245 passed
python3 tools/audit_rule_coverage.py | head -5                    # PASS (giả, không thấy V4.34)
python3 tools/audit_rule_duplicates.py                            # 0 trùng
md5sum skills/lispcad/portable/SKILL_LISPCAD_CURRENT.md \
       skills/lispcad/versions/V4.24/SKILL_LISPCAD_V4_24_PORTABLE.md   # F13 → trùng
python3 tools/benchmark_rule_routes.py                            # số byte giai đoạn
git fetch --depth=300 origin                                      # lịch sử đã kéo 271 commit
```

Số liệu đo trong phiên này: resolver `bend_nobi` (HOLE+KEGAKI+MATERIAL_RULES+NOBI) nạp 37 file, ~328 KB; benchmark các kịch bản như bảng ở mục 3.
