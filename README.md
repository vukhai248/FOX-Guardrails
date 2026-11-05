# 🦊 FOX-Guardrails

Hệ thống **AI Guardrails** phát hiện **Prompt Injection** và ngăn ngừa rò rỉ **thông tin cá nhân (PII)** cho ứng dụng mô hình ngôn ngữ lớn.

Guardrails giám sát **3 điểm chạm** của một ứng dụng hỏi đáp RAG — đầu vào người dùng, ngữ cảnh truy xuất (tài liệu, email, kết quả công cụ) và đầu ra của mô hình — kết hợp **luật phát hiện + mô hình phân loại + bộ nhận diện PII** để đánh giá rủi ro, từ đó **cho phép / che thông tin / chặn / chuyển người kiểm duyệt**. Mọi quyết định được lưu kèm **bằng chứng và lý do**; bản ghi giám sát được **che PII trước khi lưu trữ**.

> 📌 **Kế hoạch chính của đồ án (kiến trúc, công nghệ, tính năng, schema, các lớp bảo mật, thực nghiệm, bảng tick tiến độ): [`docs/DU-AN.md`](docs/DU-AN.md)** — đọc file này trước.
>
> 📄 Ghi chú đề tài nguyên văn: [`docs/de-tai.md`](docs/de-tai.md)

---

## 🏗️ Kiến trúc

```text
                    ┌────────────────────────────────────────────────────────┐
                    │                     FOX-Guardrails                     │
                    │  luật phát hiện · mô hình phân loại · nhận diện PII    │
                    └────────────────────────────────────────────────────────┘
Người dùng ──▶ [Guard: INPUT] ──▶ Retriever ──▶ [Guard: CONTEXT] ──▶ Prompt ──▶ LLM
                    │                                   │                            │
                    │                                   │  loại/che tài liệu có      │
                    │  chặn/chuyển nếu jailbreak        │  chỉ dẫn thao túng         ▼
                    │                                   │                     [Guard: OUTPUT]
                    ▼                                   ▼                            │
              Nhật ký quyết định (đã che PII)  ◀────────┴────────────────────────────┘
                    │
                    ▼
              Dashboard: cảnh báo · xem lại quyết định · thống kê hiệu quả
```

- **INPUT** — phát hiện yêu cầu đối kháng trực tiếp (jailbreak, ghi đè chỉ dẫn).
- **CONTEXT** — phân biệt *nội dung phục vụ tác vụ* và *chỉ dẫn có khả năng thao túng* trong dữ liệu bên ngoài.
- **OUTPUT** — phát hiện & che PII, chặn câu trả lời nguy hiểm.

Chi tiết: [`docs/plans/00-tong-quan.md`](docs/plans/00-tong-quan.md) §3 và [`docs/plans/B-guardrails.md`](docs/plans/B-guardrails.md)

## 📁 Cấu trúc repo

```text
FOX-Guardrails/
├── pyproject.toml         # package fox_guard, console script `fox-guard`, nhóm phụ thuộc core/ml/pii/dash/dev
├── requirements.txt       # Danh sách phụ thuộc + phiên bản đã kiểm trên env conda DL
├── fox-guard.yaml         # Cấu hình mặc định (ngưỡng, allowlist, model)
├── .env.example           # Mẫu biến môi trường
├── .github/workflows/     # CI: ruff + pytest (bỏ test cần model)
├── src/fox_guard/         # Lõi FOX-Guard (normalize, detectors, pii, policy, audit, adapters) — dựng theo gói B1–B8
├── dashboard/             # Streamlit (B10)
├── tests/                 # pytest
├── eval/                  # Phần C: dữ liệu, runner, báo cáo
├── notebooks/             # Notebook khám phá & phân tích
├── docs/                  # Đề tài, plan, research; docs/hoc/ = tài liệu học từng lớp bảo mật
└── data/                  # Dữ liệu: raw/ (tải về) · processed/ (đã chuẩn hóa) — không commit
```

Cấu trúc đích chi tiết: [`docs/plans/B-guardrails.md`](docs/plans/B-guardrails.md) §0.

## 🗺️ Lộ trình

Plan v2 (02/11/2026), 4 tuần + 1 tuần đệm, chia 3 phần chạy song song:

| Phần | Nội dung | Tài liệu |
| --- | --- | --- |
| A | Hoàn thiện web e-commerce làm ứng dụng thử nghiệm (thanh toán, review, ghi chú đơn, tool ghi, log) | [`docs/plans/A-hoan-thien-web.md`](docs/plans/A-hoan-thien-web.md) |
| B | FOX-Guard: chuẩn hoá, luật, classifier, PII, policy, audit, SDK/sidecar/proxy, dashboard | [`docs/plans/B-guardrails.md`](docs/plans/B-guardrails.md) |
| C | Dữ liệu (BIPIA, JailbreakBench, CSKH tiếng Việt, PII) và thực nghiệm | [`docs/plans/C-du-lieu-va-thuc-nghiem.md`](docs/plans/C-du-lieu-va-thuc-nghiem.md) |

Chi tiết và lịch: [`docs/plans/00-tong-quan.md`](docs/plans/00-tong-quan.md)

## ⚙️ Môi trường & công cụ

Máy phát triển dùng env conda **`DL`** (Python 3.13, dùng chung với `rag-service` của web). Package hỗ trợ Python ≥ 3.11.

```bash
# Ổ C gần đầy: cache pip và model đặt sang ổ D
export PIP_CACHE_DIR=D:/create/DATN/.cache/pip HF_HOME=D:/create/DATN/FOX-Guardrails/.cache/hf
C:/Users/Admin/anaconda3/envs/DL/python.exe -m pip install -e ".[core,ml,pii,dash,dev]"
C:/Users/Admin/anaconda3/envs/DL/python.exe -m pytest -q -m "not model"
fox-guard --help
```

Cài thêm thư viện vào `DL` thì phải chạy lại pytest của `rag-service` để chắc web không vỡ.

## 🗃️ Dữ liệu

- **BIPIA** (arXiv [2312.14197](https://arxiv.org/abs/2312.14197)) — nguồn chính: tấn công injection gián tiếp nhúng trong dữ liệu bên ngoài.
- **JailbreakBench** (NeurIPS 2024, [jailbreakbench.github.io](https://jailbreakbench.github.io/)) — bổ sung: yêu cầu đối kháng trực tiếp.

Hai nhóm tấn công được báo cáo **riêng**. Xem [`data/README.md`](data/README.md) và [`docs/plans/C-du-lieu-va-thuc-nghiem.md`](docs/plans/C-du-lieu-va-thuc-nghiem.md).

## 📚 Tài liệu

| Tài liệu | Nội dung |
| --- | --- |
| [`docs/de-tai.md`](docs/de-tai.md) | Ghi chú đề tài nguyên văn |
| [`docs/plans/`](docs/plans/README.md) | Plan v2: tổng quan, tấn công & phòng thủ, phần A/B/C, học & vấn đáp |
| [`docs/research/`](docs/research/) | Survey 2602.10453, bản đồ phương pháp, phân loại paper CSKH |
| [`docs/archive/`](docs/archive/) | Plan v1 (đã thay thế) |
