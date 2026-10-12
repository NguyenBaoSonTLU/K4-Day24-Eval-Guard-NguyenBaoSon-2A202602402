# Nhóm thực hiện K4 Track 3B

Tên nhóm: {{Tên nhóm}}

Repo chung: https://github.com/NguyenBaoSonTLU/K4-Day24-Eval-Guard-NguyenBaoSon-2A202602402

Trưởng nhóm/người nộp: {{Họ tên và MSSV}}

Ngày lab/deadline áp dụng: {{Ngày giờ theo thông báo lớp}} — Asia/Ho_Chi_Minh (UTC+07:00)

Commit dùng để chấm: {{Commit SHA}}

Mỗi nhóm nộp một repo. Điền đủ thành viên và một mục INDIVIDUAL cho từng người.
Thêm/xóa rows để khớp nhóm thật; mẫu ba rows không ép nhóm phải có ba người.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 2 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |
| 3 | {{Họ tên}} | {{MSSV}} | {{Phase/file/hàm}} | {{Commit/PR/report}} |

Người tích hợp/chạy batch/nộp link: {{Họ tên, công việc và bằng chứng}}.

## Môi trường và chuẩn bị trước lớp

OS/Python/compiler (kiểm tra 13/10/2026): Windows, CPython 3.11.16; MSVC
14.39.33519 và Windows SDK 10.0.22621.0 đã build thành công `annoy==1.17.3`.
Do ổ D thiếu dung lượng, `.venv` là junction tới virtualenv trên ổ C; vẫn dùng
đúng lệnh `.\.venv\Scripts\python.exe` từ gốc repo.

Virtualenv/dependencies/imports: `.\.venv\Scripts\python.exe -m pip check`
trả `No broken requirements found`. Import thật đã chạy được RAGAS 0.1.22,
NeMo Guardrails 0.10.0, Presidio, spaCy 3.8.16, Annoy, Qdrant client và Sentence
Transformers; `en_core_web_lg` 3.8.0 đã tải và load được. Để tương thích NumPy
1.26.4/Windows, môi trường dùng PyArrow 16.1.0, Torch 2.2.2+cpu, Transformers
4.46.3 và Sentence Transformers 3.3.1 như constraints của repo.

Models/Qdrant/50 answers đã chuẩn bị: BGE-M3 đã encode 26 chunks; collection
`lab24_production` trên Qdrant v1.9.7 có 26 points, trạng thái `green`.
Cross-encoder `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1` đã load và rerank
50 queries thật. `scripts/setup_answers.py --live` tạo
`artifacts/answers_50q.json` hợp lệ: 50 ids, phân phối 20 factual/20 multi_hop/10
adversarial, answer/contexts không rỗng và question/distribution/ground_truth
khớp fixture. Cả 50 rows có `generation_mode=llm`; provider báo model
`gpt-4o-mini-2024-07-18`; không có `extractive_fallback` trong lượt này.

Giới hạn: lượt setup trên chỉ chứng minh pipeline retrieval/rerank/generation và
imports trong cùng môi trường. NeMo rails và Presidio analyzer chưa được chạy
end-to-end; không dùng `pip check` hay unit tests để tuyên bố Phase C đã chạy.

## INDIVIDUAL

Sao chép mẫu cho mỗi thành viên; tiêu đề họ tên không dấu-MSSV.

### {{HoVaTen}}-{{MSSV}}

- Phần được giao và phần thực tế đã làm: {{Nhiệm vụ, file/hàm, mục đích}}.
- Bằng chứng: {{Commit/PR và artifacts/reports liên quan}}.
- Cách kiểm tra: {{Unit mock hoặc live experiment, lệnh và kết quả}}.
- Điều đã học: {{Khái niệm và cách thể hiện trong bài}}.
- Giới hạn/cách xử lý: {{Vấn đề và kiểm chứng}}.
- Nguồn/AI hỗ trợ nếu có: {{Công cụ, phạm vi, cách tự kiểm chứng}}.

## Cập nhật sau khi nộp

{{Ghi phiên bản nộp; nếu sửa sau deadline, ghi commit/thời điểm/lý do và thông báo
coach cho phép áp dụng bản cập nhật. Nếu không có cập nhật, ghi rõ không có.}}
