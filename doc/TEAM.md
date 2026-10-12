# Bài cá nhân K4 Track 3B

Tên nhóm: NguyenBaoSon

Repo chung: https://github.com/NguyenBaoSonTLU/K4-Day24-Eval-Guard-NguyenBaoSon-2A202602402

Trưởng nhóm/người nộp: Nguyễn Bảo Sơn — 2A202602402

Ngày lab/deadline áp dụng: 23:59 ngày 13/10/2026 — Asia/Ho_Chi_Minh (UTC+07:00),
theo deadline mặc định trong `doc/RULES.md`.

Commit dùng để chấm: commit HEAD mới nhất của nhánh `main` tại thời điểm nộp;
SHA được gửi cùng link repo qua kênh coach.

Bài được thực hiện cá nhân; repo chỉ có một thành viên và một mục INDIVIDUAL.

## Thành viên và phân công

| STT | Họ và tên | MSSV | Vai trò / công việc thật | Bằng chứng |
|---|---|---|---|---|
| 1 | Nguyễn Bảo Sơn | 2A202602402 | Chuẩn bị pipeline m1–m5; implement Tasks 1–12 trong Phase A/B/C; tích hợp môi trường, Qdrant và tests | Commit `94e174c`; support tests 60 passed; phase tests 26 passed; `artifacts/answers_50q.json` lưu local |

Người tích hợp/chạy batch/nộp link: Nguyễn Bảo Sơn — 2A202602402; cấu hình
Python 3.11/Qdrant/models, chạy setup 50 answers, kiểm tra schema và push source
lên `origin/main`.

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

Thông tin đóng góp cá nhân duy nhất của repo:

### NguyenBaoSon-2A202602402

- Phần được giao và phần thực tế đã làm: toàn bộ bài cá nhân. Viết adapter
  `src/m1_chunking.py` đến `src/m5_enrichment.py`; implement Tasks 1–12 trong
  `src/phase_a_ragas.py`, `src/phase_b_judge.py`, `src/phase_c_guard.py`; chuẩn
  bị Python 3.11, dependencies, spaCy, Qdrant, embedding/reranker và 50 answers.
- Bằng chứng: commit `94e174c`; collection Qdrant `lab24_production` có 26 points
  trạng thái `green`; `artifacts/answers_50q.json` local có 50 ids đúng phân phối
  20 factual/20 multi_hop/10 adversarial và đã pass `validate_answers`.
- Cách kiểm tra: `python -m pytest tests/ -m support -q` đạt 60 tests;
  `python -m pytest tests/test_phase_a.py tests/test_phase_b.py
  tests/test_phase_c.py -q` đạt 26 tests; `pip check` không có dependency lỗi.
- Điều đã học: giữ provenance giữa question/answer/contexts/reference; phân biệt
  pairwise winner với binary label; quy đổi A/B sau swap; tính Cohen's kappa;
  kiểm tra cả attack và clean controls; đo latency tuần tự từ raw samples.
- Giới hạn/cách xử lý: Phase A/B/C live chưa chạy nên chưa có
  `ragas_50q.json`, `judge_results.json`, `guard_results.json` hoặc số liệu báo
  cáo cuối. Không dùng kết quả mock/unit test để tuyên bố ba phase đã hoàn tất.
- Nguồn/AI hỗ trợ nếu có: OpenAI Codex hỗ trợ viết code, cấu hình môi trường và
  chạy kiểm tra. Nguyễn Bảo Sơn đối chiếu hợp đồng starter, fixtures, validator,
  kết quả test và setup thực tế trước khi commit.

## Cập nhật sau khi nộp

Chưa có cập nhật sau khi nộp.
