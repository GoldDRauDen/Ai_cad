# TrainAiCad — GPT Web Project Instructions

Repo `GoldDRauDen/TrainAiCad` là production authority cho CAD.

Với mọi job PDF / ảnh / customer DXF DATA hoặc khi user chỉ nói `E2E` / `đọc repo TrainAiCad làm E2E`:

1. Truy cập current `GoldDRauDen/TrainAiCad` bằng GitHub connector/plugin khả dụng.
2. Đọc `AI_BOOTSTRAP.md`, sau đó làm đúng current `AI_ENTRYPOINT.md`, Router/Census/Coverage và routed modules/references mà repo yêu cầu.
3. Chạy E2E đến mức tối đa; không dừng ở census/report nếu vẫn còn CAD/QA executable.
4. Không dùng memory/chat/Project Instructions để thay current repo; không tự fallback sang portable/history.
5. Nếu repo hoặc source/tool bắt buộc không truy cập được, báo blocker thật theo current repo; không giả vờ đã đọc repo hoặc đã tạo/QA DXF.
6. Reference/sample chỉ dùng theo current repo audit/calibration contract; không reverse-fit. Sample FLAG/Magenta/pending không phải approved production geometry nếu chưa được source/user xác nhận.
7. Không sửa/push production repo nếu user chưa trực tiếp nói `DUYỆT` hoặc `PUSH`.
8. Canonical/export/read-back, FLAG/PREVIEW/VIEWS_ONLY, QA và format báo cáo đều theo **current repo**, không hardcode lại ở Project Instructions.

Project Instructions này chỉ là bootstrap pointer. Nếu nội dung ở đây mâu thuẫn với engineering rules của current repo, current repo authority thắng, trừ explicit instruction hiện tại của user.
