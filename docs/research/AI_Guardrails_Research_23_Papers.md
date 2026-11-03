# BẢN ĐỒ NGHIÊN CỨU AI GUARDRAILS — DÒNG THỜI GIAN 2023–2026

> **Đọc theo bài toán CSKH thương mại điện tử:** bắt đầu tại [Phân loại paper theo phạm vi ứng dụng](Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md). Tài liệu đó xếp lại đủ 23 hồ sơ heuristic, 14 mục ADD và các nhóm defense/benchmark theo năng lực chatbot. **Các nhãn P1/P2/P3 trong hồ sơ và taxonomy bên dưới là ưu tiên tổng quát của bản cũ, không phải danh sách phải đọc/triển khai cho đồ án hiện tại.** Dùng nhóm CỐT LÕI / BỔ TRỢ / CÓ ĐIỀU KIỆN / NGOÀI PHẠM VI trong chỉ mục mới để quyết định đọc.

> **Đề tài:** Xây dựng hệ thống AI Guardrails phát hiện Prompt Injection và ngăn ngừa rò rỉ thông tin cá nhân trong ứng dụng mô hình ngôn ngữ lớn.  
> **Tài liệu nền:** Peiran Wang và cộng sự, *The Landscape of Prompt Injection Threats in LLM Agents: From Taxonomy to Analysis*, arXiv:2602.10453v1, 11/02/2026.  
> **Phạm vi tài liệu này:** Giữ taxonomy/23 hồ sơ theo survey gốc; thêm chỉ mục thời gian và nhóm bài 2026 đã xác minh riêng bằng mã `ADD-xx` (không thuộc 78 công trình survey).  
> **Ngữ cảnh áp dụng:** Đã có project thương mại điện tử; phạm vi nghiên cứu hướng tới chatbot CSKH, có thể tra cứu thông tin qua API đã phân quyền. Chưa xác nhận có chatbot hoàn chỉnh, LLM tự gọi tool, MCP, terminal, email/web egress hoặc khả năng thay đổi dữ liệu.

**Link survey:** https://arxiv.org/abs/2602.10453 | **PDF:** https://arxiv.org/pdf/2602.10453

---

## 0. Cách đọc tài liệu

### 0.1. Sơ đồ phân cấp

```text
AI GUARDRAILS CHO CHATBOT THƯƠNG MẠI ĐIỆN TỬ
├── A. ATTACK: Tạo payload như thế nào? (Section 3.1)
│   ├── A1. Manual template (16 paper + hồ sơ H01–H16)
│   ├── A2. LLM generation (3 paper + hồ sơ G01–G03)
│   ├── A3. Structural encoding (4 paper + hồ sơ S01–S04)
│   ├── A4. Gradient-based optimization
│   ├── A5. Genetic / evolutionary optimization
│   └── A6. Sampling-based optimization (RL / MCMC)
├── B. ATTACK PARADIGMS: Tấn công từ đâu, nhằm gì? (Section 3.2)
│   ├── B1. Attack surface: Direct / Indirect / Supply-chain
│   ├── B2. Attack goal: Integrity / Confidentiality / Availability
│   ├── B3. Capability: Black-box / White-box
│   └── B4. Visibility: Visible / Semantics / Context / Encoding / Vision
├── C. DEFENSE: Bảo vệ ở tầng nào? (Section 4)
│   ├── C1. Text-level
│   │   ├── C1.1. Detection filter: LLM / non-LLM / localization
│   │   └── C1.2. Prompt enhancement: separation / defense prompts / rewrite
│   ├── C2. Model-level
│   │   ├── C2.1. Model alignment / fine-tuning
│   │   └── C2.2. Intermediate-representation (IR) probing
│   └── C3. Execution-level
│       ├── C3.1. Task alignment
│       ├── C3.2. Information flow control
│       ├── C3.3. Spec / policy control
│       └── C3.4. Isolation
├── D. CONFIDENTIALITY / PII
│   ├── D1. Data exfiltration và privacy-flow protection trong survey
│   └── D2. Phần PII detection/masking KHÔNG được survey bao quát đầy đủ
├── E. BENCHMARK (Sections 5–7)
│   ├── E1. OpenPI / BIPIA / InjecAgent / AgentDojo / ASB
│   ├── E2. AGENTPI: 5 kiểu context-aware attack
│   ├── E3. Baseline defense được đánh giá
│   └── E4. ASR / Utility / Latency / Tokens / evaluation methods
└── F. FUTURE DIRECTIONS (Appendix B)
    ├── F1. Fine-grained attention access control
    ├── F2. Resource-aware availability defense
    ├── F3. Dynamic trust boundaries
    ├── F4. Reasoning consistency verification
    └── F5. Hybrid human–AI intervention
```

### 0.2. Quy ước

- **[Survey]**: Phân loại, thuật ngữ hoặc nhận định trực tiếp từ paper.
- **[Đề xuất]**: Cách tôi gợi ý áp dụng cho đồ án. Không phải đóng góp đã được chứng minh của paper.
- **P1 – Ưu tiên cao**: nên đọc/triển khai để hình thành MVP và benchmark.
- **P2 – Ưu tiên trung bình**: cân nhắc nếu phù hợp chatbot hoặc còn thời gian.
- **P3 – Tham khảo**: hiểu và đưa vào Related Work; không cần tự triển khai.
- **`[n]`**: số tài liệu tham khảo **theo danh sách References của survey**, không phải số mục do tôi tạo.
- **Trang** là số trang in trong survey, không phải số trang của mọi công trình gốc.

**Bổ sung bản nghiên cứu sâu (đã sắp theo năm):** Mục **A.1.1** trình bày hồ sơ có nguồn gốc cho **toàn bộ 23 nghiên cứu heuristic-based**, gồm cách tấn công, benchmark, số liệu, defense thực nghiệm/khuyến nghị, hạn chế và mức ưu tiên với chatbot.

**Giới hạn quan trọng:** Survey là bài tổng quan 78 công trình (37 attack + 41 defense theo báo cáo của tác giả), không phải hướng dẫn trực tiếp xây PII recognizer. Một số công trình xuất hiện ở hơn một nhóm phân loại; không cộng các hàng trong bảng như số paper duy nhất.

---


# 0. HƯỚNG DẪN ĐỌC TỪ CƠ BẢN ĐẾN NÂNG CAO

**Cập nhật lần này (01/11/2026):** (i) bổ sung **năm** cho 23 hồ sơ Heuristic-based; (ii) xếp lại các hồ sơ theo năm công bố mà survey trích; (iii) thêm bảng 96 nguồn theo năm (bao gồm cả nguồn nền tảng); (iv) thêm 14 công trình năm 2026 với mã `ADD-01…ADD-14`, không làm thay đổi mã gốc `H/G/S` hoặc `[n]` của survey.

**Lưu ý:** Thứ tự thời gian **không đồng nghĩa** độ khó kỹ thuật. Lộ trình hiện tại theo bài toán CSKH, không theo năm và không yêu cầu đọc hết danh mục:

| Giai đoạn | Mục tiêu | Đọc theo mã / ref | Kết quả nên có |
|---|---|---|---|
| **Nền tảng** | Hiểu IPI và ranh giới dữ liệu/chỉ dẫn | Survey §2, §3.2, §4.1, §5; BIPIA [83] | Threat model theo nguồn và quyền thật |
| **Privacy và baseline** | PI khiến chatbot hỏi PII không cần thiết; lọc context | G02 / [18]; PromptArmor [66] | Attack cases và baseline tham chiếu |
| **Đánh giá** | Hard-benign/FPR và chia tập chống trùng | ADD-13, ADD-14 | Protocol và tập kiểm thử |
| **Đọc theo điều kiện** | Chỉ mở paper khớp tính năng đã xác nhận | Theo [chỉ mục CSKH](Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md) | Không mặc định thêm shell, PDF hoặc email/web tools |

**Quy ước mã (không đổi):** `H01–H16` = 16 Manual Template; `G01–G03` = 3 LLM Generation; `S01–S04` = 4 Structural Encoding; `D01–D40` = cách diễn giải phương pháp phòng thủ theo file gốc; `[n]` = References của survey; `ADD-xx` = bài **mới ngoài survey**.

**Độ tin cậy nguồn:** Năm và danh mục của 96 tài liệu được khớp theo bibliography của survey; phần 23 hồ sơ chi tiết giữ lại báo cáo nghiên cứu trước; phần 2026 dựa trên nguồn phát hành gốc/ACL hoặc trang nhà xuất bản đã tra cứu. Những con số chỉ áp dụng trong thí nghiệm được mô tả; **chưa tự tái chạy benchmark** và không coi kết quả preprint đã được peer-review nếu không có thông tin xuất bản.

# 1. DANH MỤC 23 HỒ SƠ HEURISTIC-BASED THEO NĂM

Danh mục này nối trực tiếp tới hồ sơ chi tiết nằm trong **A.1.1** ở phần gốc bên dưới. Mã H/G/S và [n] được giữ nguyên dù vị trí đọc đã thay đổi. Các hồ sơ cùng năm được xếp theo nhóm, không suy ra thứ tự độ khó.

| Năm | Mã hồ sơ | Ref survey | Tên gốc | Hướng nghiên cứu |
|---:|---|---|---|---|
| 2024 | [H01](#paper-h01) | [91] | AI²: Towards Hijacking the Actions of Large Language Model-based Applications | Manual |
| 2024 | [H03](#paper-h03) | [37] | Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems | Manual |
| 2024 | [H06](#paper-h06) | [56] | Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberatta | Manual |
| 2024 | [H07](#paper-h07) | [12] | Prompt Injection Attacks on Large Language Models in Oncology | Manual |
| 2024 | [H08](#paper-h08) | [81] | Preemptive Answer “Attacks” on Chain-of-Thought Reasoning | Manual |
| 2024 | [H09](#paper-h09) | [68] | Scaling Behavior of Machine Translation with Large Language Models under Prompt Inject | Manual |
| 2024 | [H15](#paper-h15) | [63] | Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign) | Manual |
| 2025 | [H02](#paper-h02) | [17] | MAD-Spear: A Conformity-Driven Prompt Injection Attack on Multi-Agent Debate Systems | Manual |
| 2025 | [H04](#paper-h04) | [2] | Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During T | Manual |
| 2025 | [H05](#paper-h05) | [3] | Breaking the Prompt Wall (I): A Real-World Case Study of Attacking ChatGPT via Lightwe | Manual |
| 2025 | [H10](#paper-h10) | [46] | “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editor | Manual |
| 2025 | [H11](#paper-h11) | [62] | EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM | Manual |
| 2025 | [H12](#paper-h12) | [51] | Cybersecurity AI: Hacking the AI Hackers via Prompt Injection | Manual |
| 2025 | [H13](#paper-h13) | [94] | When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer R | Manual |
| 2025 | [H14](#paper-h14) | [50] | Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections | Manual |
| 2025 | [H16](#paper-h16) | [9] | Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods | Manual |
| 2025 | [G01](#paper-g01) | [16] | Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adap | LLM-generated |
| 2025 | [G02](#paper-g02) | [18] | VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of U | LLM-generated |
| 2025 | [G03](#paper-g03) | [43] | Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems | LLM-generated |
| 2025 | [S01](#paper-s01) | [14] | Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Promp | Structural |
| 2025 | [S02](#paper-s02) | [24] | Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choic | Structural |
| 2025 | [S03](#paper-s03) | [61] | Exploiting Web Search Tools of AI Agents for Data Exfiltration | Structural |
| 2025 | [S04](#paper-s04) | [35] | Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications | Structural |

# 2. CÁC CÔNG TRÌNH BỔ SUNG NĂM 2026 — MÃ `ADD-xx`

**Đây là nghiên cứu ngoài survey (survey chốt dữ liệu 20/10/2025).** Chọn theo sự phù hợp với đồ án: chatbot e-commerce đã có, guardrails plug-and-play, benchmark, data leakage và PII trước khi gọi API. **Không mặc định mỗi công trình là phương pháp cần triển khai.** Ngày thuộc tháng 07 với `-01` chỉ làm mốc sắp thứ tự, vì ACL công bố tháng nhưng metadata ở nguồn không ghi ngày chính xác.

| Thời gian | Mã mới | Công trình | Trọng tâm | Ưu tiên |
|---|---|---|---|---|
| 2026-01-16 | [ADD-01](#add-01) | [Hidden-in-Plain-Text: A Benchmark for Social-Web Indirect Prompt Injection in RAG](https://arxiv.org/abs/2601.10923) | RAG · HTML/Markdown · Unicode · Benchmark | **P1** |
| 2026-02-25 | [ADD-02](#add-02) | [Silent Egress: When Implicit Prompt Injection Makes LLM Agents Leak Without a Trace](https://arxiv.org/abs/2602.22450) | PII/Data Exfiltration · Tool Outputs · Egress | **P1** |
| 2026-04-09 | [ADD-03](#add-03) | [A Survey of Secure Retrieval-Augmented Generation](https://aclanthology.org/2026.findings-emnlp.241/) | Survey RAG Security · Retrieval Pipeline | **P2** |
| 2026-04-26 | [ADD-04](#add-04) | [Evaluation of Prompt Injection Defenses in Large Language Models](https://arxiv.org/abs/2604.23887) | Adaptive Testing · Application-side Output Filtering | **P2** |
| 2026-05-05 | [ADD-05](#add-05) | [ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection](https://arxiv.org/abs/2605.03378) | Provenance · Context-aware Agent | **P2** |
| 2026-05-21 | [ADD-06](#add-06) | [Blind Spots in the Guard: How Domain-Camouflaged Injection Attacks Evade Detection in Multi-Agent LLM Systems](https://arxiv.org/abs/2605.22001) | Context Blending · Camouflage · Detector Failures | **P1** |
| 2026-05-27 | [ADD-07](#add-07) | [Can It Reach the Generator? Investigating the Survival of Prompt-Injection Attacks in Realistic RAG Settings](https://arxiv.org/abs/2605.28017) | End-to-end RAG · Retrieval Survival | **P1** |
| 2026-06-16 | [ADD-08](#add-08) | [Evaluating Prompting-Based Defenses Against Domain-Camouflaged Injection Attacks](https://arxiv.org/abs/2606.18530) | Prompt-only Baselines · Paraphrasing | **P1** |
| 2026-06-23 | [ADD-09](#add-09) | [Indirect Prompt Injection in Large Language Models](https://doi.org/10.1007/s00521-026-12266-x) | Hidden Text · Document Rendering | **P2** |
| 2026-07 | [ADD-10](#add-10) | [PIArena: A Platform for Prompt Injection Evaluation](https://aclanthology.org/2026.acl-long.1533/) | Benchmark · Adaptive Attacks · Generalization | **P1** |
| 2026-07 | [ADD-11](#add-11) | [Defenses Against Prompt Attacks Learn Surface Heuristics](https://aclanthology.org/2026.acl-long.502/) | Over-defense · Shortcut Learning | **P1** |
| 2026-07 | [ADD-12](#add-12) | [Rethinking Assessments of Prompt Injection Attacks](https://aclanthology.org/2026.findings-acl.1191/) | Real-world Evaluation · Simulated vs Deployed | **P2** |
| 2026-09-14 | [ADD-13](#add-13) | [PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift](https://arxiv.org/abs/2609.15017) | Detector Benchmark · Hard Benign · Obfuscation | **P1** |
| 2026-10-06 | [ADD-14](#add-14) | [RAG-PIBench: A Leakage-Aware Benchmark for Prompt-Injection Detection in Trustworthy RAG Systems](https://arxiv.org/abs/2610.08571) | RAG Classifier · Data Leakage Between Splits | **P1** |

### 2.1. Hồ sơ phương pháp và khả năng áp dụng

<a id="add-01"></a>

#### ADD-01 · 2026-01 · Hidden-in-Plain-Text: A Benchmark for Social-Web Indirect Prompt Injection in RAG

**Nguồn:** [https://arxiv.org/abs/2601.10923](https://arxiv.org/abs/2601.10923) · **Loại:** Preprint arXiv; ghi nhận WWW 2026 trên arXiv · **Ưu tiên:** P1 · **Chủ đề:** RAG · HTML/Markdown · Unicode · Benchmark.

- **Nội dung / đóng góp:** OpenRAG-Soc: benchmark/harness cho RAG dùng nội dung mạng xã hội. Xem xét quá trình từ ingestion đến retrieval và generation; hỗ trợ so sánh sparse/dense retriever, HTML/Markdown sanitization, Unicode normalization và attribution-gated answering.
- **Phương pháp tấn công / phòng thủ:** Tấn công qua các nội dung web/user-generated có thể tồn tại qua bước trích xuất và truy xuất. Phòng thủ tiêu biểu là làm sạch cấu trúc, chuẩn hóa Unicode có kiểm soát và yêu cầu quy chiếu nguồn trước khi trả lời.
- **Benchmark / kết quả được nguồn mô tả:** Bài báo đề xuất theo dõi khả năng attack đến bước sinh đáp án, dịch chuyển thứ hạng retrieval, utility và latency; phần metadata xác nhận bộ benchmark, không suy ra ASR cụ thể khi chưa kiểm tra bảng gốc.
- **Hạn chế / điều kiện áp dụng:** Phạm vi social-web RAG; không phải mọi biến thể Unicode/HTML đều hiệu quả ở mọi chatbot.
- **Áp dụng cho đồ án:** Ưu tiên nếu chatbot đọc review/FAQ/HTML. Tạo ma trận raw text vs sanitized text; đo cả tỉ lệ payload thực sự được truy xuất.

<a id="add-02"></a>

#### ADD-02 · 2026-02 · Silent Egress: When Implicit Prompt Injection Makes LLM Agents Leak Without a Trace

**Nguồn:** [https://arxiv.org/abs/2602.22450](https://arxiv.org/abs/2602.22450) · **Loại:** Preprint arXiv · **Ưu tiên:** P1 · **Chủ đề:** PII/Data Exfiltration · Tool Outputs · Egress.

- **Nội dung / đóng góp:** Chỉ ra rò rỉ có thể xảy ra qua lời gọi công cụ hoặc HTTP request mà câu trả lời cuối vẫn bình thường. Payload xuất hiện trong URL preview/metadata mà người dùng không chủ động xem.
- **Phương pháp tấn công / phòng thủ:** Implicit indirect injection từ title/snippet/metadata → Agent tạo request ra ngoài → nội dung nhạy cảm theo request. Tác giả bàn về việc chia dữ liệu qua nhiều request để tránh bộ lọc đơn lẻ; phòng thủ hữu ích ở điểm egress, domain allowlist và kiểm tra redirects.
- **Benchmark / kết quả được nguồn mô tả:** Nghiên cứu báo cáo 480 lần chạy với Agent dựa trên qwen2.5:7b; xác suất egress 0,89 trong thiết lập thử nghiệm. Đây không phải tỷ lệ ngoài thực tế.
- **Hạn chế / điều kiện áp dụng:** Môi trường mô phỏng local; không chứng minh mọi chatbot chỉ hỏi đáp có nguy cơ HTTP egress tương đương.
- **Áp dụng cho đồ án:** Nếu chatbot có search/link tool: bắt buộc mock tool requests, chấm `unauthorized_egress`, không chỉ xem final response.

<a id="add-03"></a>

#### ADD-03 · 2026-04 · A Survey of Secure Retrieval-Augmented Generation

**Nguồn:** [https://aclanthology.org/2026.findings-emnlp.241/](https://aclanthology.org/2026.findings-emnlp.241/) · **Loại:** Findings of EMNLP 2026 (10/2026); bản đầu tiên trên arXiv 09/04/2026 · **Ưu tiên:** P2 · **Chủ đề:** Survey RAG Security · Retrieval Pipeline.

- **Nội dung / đóng góp:** Đề xuất cách nhìn bảo vệ hệ thống RAG theo các trục Surface, Layer, Objective, Target (SLOT); nhấn mạnh bảo mật cả tuyến truy cập tri thức ngoài, không chỉ prompt.
- **Phương pháp tấn công / phòng thủ:** Tổng hợp 135 nghiên cứu theo SLOT: Surface–Layer–Objective–Target; lập bản đồ các điểm tấn công/điểm can thiệp trong pipeline truy cập tri thức RAG.
- **Benchmark / kết quả được nguồn mô tả:** Survey/đề xuất taxonomy; không nên báo là giải pháp đã vượt một benchmark duy nhất.
- **Hạn chế / điều kiện áp dụng:** Là tài liệu tổng quan, không phải implementation.
- **Áp dụng cho đồ án:** Dùng bổ trợ phần Threat Model, chú trọng bảo vệ review/product description trước khi chúng tới LLM.

<a id="add-04"></a>

#### ADD-04 · 2026-04 · Evaluation of Prompt Injection Defenses in Large Language Models

**Nguồn:** [https://arxiv.org/abs/2604.23887](https://arxiv.org/abs/2604.23887) · **Loại:** Preprint arXiv · **Ưu tiên:** P2 · **Chủ đề:** Adaptive Testing · Application-side Output Filtering.

- **Nội dung / đóng góp:** Đánh giá các cấu hình phòng vệ trước attacker thích nghi nhằm làm lộ thông tin trong system prompts, cho thấy các biện pháp dựa hoàn toàn vào việc mô hình tự giữ bí mật có thể thất bại.
- **Phương pháp tấn công / phòng thủ:** Attacker điều chỉnh truy vấn qua nhiều vòng; biện pháp được kiểm tra gồm lọc đầu ra bằng mã ứng dụng độc lập với mô hình.
- **Benchmark / kết quả được nguồn mô tả:** Abstract tác giả mô tả >20.000 attack trials và một cấu hình output filtering giữ 0 leaks trong 15.000 lượt ở setup của họ; không coi đây là đảm bảo cho PII hoặc mọi kênh egress.
- **Hạn chế / điều kiện áp dụng:** Đối tượng chính là system-prompt secrets, không đồng nhất rò rỉ PII trong RAG.
- **Áp dụng cho đồ án:** Dùng làm luận cứ cần application-level controls; không dựa duy nhất vào system prompt bảo vệ dữ liệu.

<a id="add-05"></a>

#### ADD-05 · 2026-05 · ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection

**Nguồn:** [https://arxiv.org/abs/2605.03378](https://arxiv.org/abs/2605.03378) · **Loại:** Preprint arXiv · **Ưu tiên:** P2 · **Chủ đề:** Provenance · Context-aware Agent.

- **Nội dung / đóng góp:** Xây AgentLure benchmark và ARGUS, theo dõi quan hệ ảnh hưởng của dữ liệu không đáng tin đến quyết định Agent.
- **Phương pháp tấn công / phòng thủ:** Influence provenance graph và kiểm tra liệu hành động có đủ bằng chứng tin cậy hay không; khác với chỉ phát hiện token khả nghi.
- **Benchmark / kết quả được nguồn mô tả:** Tác giả báo cáo ASR còn 3,8% và utility 87,5% trên AgentLure; gắn với cấu hình của tác giả, chưa tái lập độc lập.
- **Hạn chế / điều kiện áp dụng:** Phức tạp hơn RAG chatbot không dùng tools; yêu cầu instrumentation nội bộ.
- **Áp dụng cho đồ án:** Chỉ lấy ý tưởng provenance labels (`source`,`trust_level`) và rule cho thao tác nhạy cảm, không cần tái triển khai ARGUS.

<a id="add-06"></a>

#### ADD-06 · 2026-05 · Blind Spots in the Guard: How Domain-Camouflaged Injection Attacks Evade Detection in Multi-Agent LLM Systems

**Nguồn:** [https://arxiv.org/abs/2605.22001](https://arxiv.org/abs/2605.22001) · **Loại:** Preprint arXiv · **Ưu tiên:** P1 · **Chủ đề:** Context Blending · Camouflage · Detector Failures.

- **Nội dung / đóng góp:** Phát hiện các payload giả giọng điệu và từ vựng của tài liệu đích có thể bị bộ lọc xem là thông tin bình thường; gọi chênh lệch hiệu quả này là Camouflage Detection Gap.
- **Phương pháp tấn công / phòng thủ:** Attack không cần câu “IGNORE ALL...”, mà dùng lời khuyến nghị/nhận định giả thẩm quyền phù hợp với domain. Tác giả so sánh static với camouflaged payloads.
- **Benchmark / kết quả được nguồn mô tả:** Nghiên cứu 45 tasks qua 3 domain, 2 model families; báo cáo độ phát hiện giảm mạnh dưới các cấu hình cụ thể. Không suy rộng các tỷ lệ sang detector khác.
- **Hạn chế / điều kiện áp dụng:** Có thành phần multi-agent, quy mô tác vụ giới hạn; cần cẩn trọng khi áp dụng vào chatbot đơn Agent.
- **Áp dụng cho đồ án:** Tạo negative/positive pairs trong `product_description`: một đoạn chính sách thực và một đoạn cố hướng chatbot sang chính sách giả; chấm FPR/recall.

<a id="add-07"></a>

#### ADD-07 · 2026-05 · Can It Reach the Generator? Investigating the Survival of Prompt-Injection Attacks in Realistic RAG Settings

**Nguồn:** [https://arxiv.org/abs/2605.28017](https://arxiv.org/abs/2605.28017) · **Loại:** Preprint arXiv · **Ưu tiên:** P1 · **Chủ đề:** End-to-end RAG · Retrieval Survival.

- **Nội dung / đóng góp:** Nhiều benchmark đưa sẵn payload vào context LLM nên đánh giá quá cao khả năng tấn công; paper kiểm tra qua retriever → reranker → generator.
- **Phương pháp tấn công / phòng thủ:** Tấn công chỉ thành công nếu tài liệu độc hại vượt qua retrieval/reranking và ảnh hưởng sinh câu trả lời. Tác giả tái kiểm tra 7 GEO attack variants.
- **Benchmark / kết quả được nguồn mô tả:** Đo sự sống sót ở từng giai đoạn và thành công end-to-end; các attack đơn giản/gradient kém hiệu quả khi phải đi qua retrieval trong thiết lập paper.
- **Hạn chế / điều kiện áp dụng:** Tập trung recommendation/GEO hơn là mọi hành vi xâm nhập.
- **Áp dụng cho đồ án:** Benchmark phải có `retrieved_payload=true/false` riêng; case không được truy xuất không tính thành công của Guardrail.

<a id="add-08"></a>

#### ADD-08 · 2026-06 · Evaluating Prompting-Based Defenses Against Domain-Camouflaged Injection Attacks

**Nguồn:** [https://arxiv.org/abs/2606.18530](https://arxiv.org/abs/2606.18530) · **Loại:** Preprint arXiv · **Ưu tiên:** P1 · **Chủ đề:** Prompt-only Baselines · Paraphrasing.

- **Nội dung / đóng góp:** So sánh Spotlighting, paraphrasing, sandwiching và kết hợp trước payload giả dạng văn bản hợp lệ trong ngành nghề.
- **Phương pháp tấn công / phòng thủ:** Áp dụng nhiều cấu trúc bảo vệ trước cùng attack set; kết quả thay đổi theo từng mô hình.
- **Benchmark / kết quả được nguồn mô tả:** Tác giả nêu 3.510 trials qua 3 model families/3 domains; paraphrasing có hiệu quả tương đối nhất quán trong bối cảnh thử nghiệm nhưng không xóa hết rủi ro.
- **Hạn chế / điều kiện áp dụng:** Tài liệu nghề nghiệp tổng hợp/synthetic, không có bằng chứng kết quả giữ nguyên với mọi dữ liệu doanh nghiệp.
- **Áp dụng cho đồ án:** Nếu thời gian hạn chế, thử Delimiters vs Paraphrasing vs Hybrid với cùng tập sản phẩm bị chèn.

<a id="add-09"></a>

#### ADD-09 · 2026-06 · Indirect Prompt Injection in Large Language Models

**Nguồn:** [https://doi.org/10.1007/s00521-026-12266-x](https://doi.org/10.1007/s00521-026-12266-x) · **Loại:** Neural Computing and Applications (Springer), 23/06/2026 · **Ưu tiên:** P2 · **Chủ đề:** Hidden Text · Document Rendering.

- **Nội dung / đóng góp:** Nghiên cứu tấn công gián tiếp thông qua tài liệu có chỉ dẫn được nhúng kín đáo, bao gồm các cách trình bày khiến người đọc và pipeline nhận diện có thể nhìn thấy nội dung khác nhau.
- **Phương pháp tấn công / phòng thủ:** Khai thác sự khác biệt giữa cách nhìn văn bản hiển thị và cách parser/LLM lấy text; liên quan đến các biến thể chữ rất nhỏ hoặc khó nhìn trong tài liệu.
- **Benchmark / kết quả được nguồn mô tả:** Bài báo thảo luận và thực nghiệm các kịch bản indirect injection; cần xem thiết lập cụ thể trước khi ghi chỉ số ASR vào luận văn.
- **Hạn chế / điều kiện áp dụng:** Chủ yếu có ích nếu chatbot ingest HTML/PDF; không đáng làm parser phức tạp nếu hệ thống chỉ lấy JSON từ DB.
- **Áp dụng cho đồ án:** Nếu có PDF/HTML ingestion, ghi cả extracted text và rendered view khi tạo golden.

<a id="add-10"></a>

#### ADD-10 · 2026-07 · PIArena: A Platform for Prompt Injection Evaluation

**Nguồn:** [https://aclanthology.org/2026.acl-long.1533/](https://aclanthology.org/2026.acl-long.1533/) · **Loại:** ACL 2026 (tháng 07; ngày 01 dùng để sắp theo tháng, KHÔNG phải ngày công bố chính xác) · **Ưu tiên:** P1 · **Chủ đề:** Benchmark · Adaptive Attacks · Generalization.

- **Nội dung / đóng góp:** Đề xuất nền tảng đánh giá tổng hợp nhiều attacks, defenses và benchmarks; cho thấy defense dễ thất bại khi đổi dataset hoặc gặp attacker thích nghi.
- **Phương pháp tấn công / phòng thủ:** Tấn công tối ưu theo feedback của defense; đánh giá tính chuyển giao và hiệu quả qua nhiều nhiệm vụ thay vì một vài template.
- **Benchmark / kết quả được nguồn mô tả:** Có nền tảng và mã nguồn được công bố; nguồn ACL xác nhận tháng 07/2026. Không gán ngày 01/07 là ngày xuất bản thật.
- **Hạn chế / điều kiện áp dụng:** Môi trường đánh giá rộng, không cần chạy toàn bộ để làm đồ án.
- **Áp dụng cho đồ án:** Tách train/test theo family và nguồn tài liệu; chuẩn hóa cách chạy Rule/Model/Hybrid trên cùng test set.

<a id="add-11"></a>

#### ADD-11 · 2026-07 · Defenses Against Prompt Attacks Learn Surface Heuristics

**Nguồn:** [https://aclanthology.org/2026.acl-long.502/](https://aclanthology.org/2026.acl-long.502/) · **Loại:** ACL 2026 (tháng 07; ngày 01 chỉ dùng để sắp) · **Ưu tiên:** P1 · **Chủ đề:** Over-defense · Shortcut Learning.

- **Nội dung / đóng góp:** Các hệ thống phòng thủ học mẹo theo vị trí, token trigger, chủ đề thay vì hiểu ý định tấn công, làm tăng false positives.
- **Phương pháp tấn công / phòng thủ:** Đánh giá vị trí dữ liệu, token kích hoạt và khả năng khái quát ra domain ngoài phân phối huấn luyện.
- **Benchmark / kết quả được nguồn mô tả:** Nguồn ACL nêu có cấu hình false refusal tăng đến 50% chỉ vì trigger token; đây là kết quả của họ trong bài test kiểm soát.
- **Hạn chế / điều kiện áp dụng:** Tập trung hiệu ứng của defense fine-tuning, không thay thế đánh giá detector độc lập.
- **Áp dụng cho đồ án:** Golden set phải có hard-benign documents như bài viết về bảo mật chứa nguyên văn “Ignore previous instructions”.

<a id="add-12"></a>

#### ADD-12 · 2026-07 · Rethinking Assessments of Prompt Injection Attacks

**Nguồn:** [https://aclanthology.org/2026.findings-acl.1191/](https://aclanthology.org/2026.findings-acl.1191/) · **Loại:** Findings of ACL 2026 (tháng 07; ngày 01 chỉ dùng để sắp) · **Ưu tiên:** P2 · **Chủ đề:** Real-world Evaluation · Simulated vs Deployed.

- **Nội dung / đóng góp:** Đánh giá đa thiết lập, kể cả ứng dụng thật, để chỉ ra khung benchmark có thể thiếu tính thực tế.
- **Phương pháp tấn công / phòng thủ:** So sánh loại payload, nhiệm vụ và ứng dụng, đặt cạnh các phòng thủ prompt-level/model-level.
- **Benchmark / kết quả được nguồn mô tả:** Abstract công bố 37 ứng dụng, 185 injected tasks, 21 attack instructions, 143.745 queries; là kết quả của thiết lập nghiên cứu, không phản ánh tỷ lệ thị trường.
- **Hạn chế / điều kiện áp dụng:** Nguồn hiện truy cập tốt ở trang ACL metadata/abstract; cần xác minh PDF nếu muốn lấy bảng kết quả chi tiết.
- **Áp dụng cho đồ án:** Nhấn mạnh benchmark cần một chatbot thật và những kịch bản sát kinh doanh.

<a id="add-13"></a>

#### ADD-13 · 2026-09 · PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift

**Nguồn:** [https://arxiv.org/abs/2609.15017](https://arxiv.org/abs/2609.15017) · **Loại:** IEEE Access 2026; bản arXiv 14/09/2026 · **Ưu tiên:** P1 · **Chủ đề:** Detector Benchmark · Hard Benign · Obfuscation.

- **Nội dung / đóng góp:** Bổ sung stress tests cho đầu vào hợp lệ nhưng trông giống attack, payload bị biến dạng và dịch chuyển phân phối.
- **Phương pháp tấn công / phòng thủ:** Frozen multi-axis benchmark, fixed thresholds, kiểm tra recall của attack đồng thời đo hard-benign FPR.
- **Benchmark / kết quả được nguồn mô tả:** Trong tập stress của tác giả, một detector F1 >0,98 trên held-out test vẫn chặn nhầm gần một phần ba hard-benign ngoại nguồn. Không suy ra FPR deployment.
- **Hạn chế / điều kiện áp dụng:** Stress distribution được chọn để phơi bày lỗi; không đại diện lưu lượng người dùng tự nhiên.
- **Áp dụng cho đồ án:** Ưu tiên cao để thiết kế benchmark 4 nhóm: normal benign, hard benign, simple attack, obfuscated/context attack.

<a id="add-14"></a>

#### ADD-14 · 2026-10 · RAG-PIBench: A Leakage-Aware Benchmark for Prompt-Injection Detection in Trustworthy RAG Systems

**Nguồn:** [https://arxiv.org/abs/2610.08571](https://arxiv.org/abs/2610.08571) · **Loại:** Preprint arXiv, 06/10/2026 · **Ưu tiên:** P1 · **Chủ đề:** RAG Classifier · Data Leakage Between Splits.

- **Nội dung / đóng góp:** Bộ dữ liệu 4.876 ví dụ có ngữ cảnh, chú trọng tránh trùng lặp/leakage giữa train, validation và protected test.
- **Phương pháp tấn công / phòng thủ:** So sánh keyword, semantic-reference, TF-IDF, logistic/SVM và transformer-based detector theo protocol cố định.
- **Benchmark / kết quả được nguồn mô tả:** Theo abstract, DistilBERT F1=0,896 và PR-AUC=0,968 trên protected test; các mô hình sparse vẫn cạnh tranh được.
- **Hạn chế / điều kiện áp dụng:** “Leakage-aware” ở đây **nói về dataset split leakage**, không phải phòng ngừa rò rỉ PII khách hàng.
- **Áp dụng cho đồ án:** Đọc để xây baseline Rule vs TF-IDF/SVM vs Transformer/Hybrid, khóa golden trước khi tune threshold.

### 2.2. Chọn đọc 2026 để không quá tải

**Đọc chính trong nhóm 2026:** `ADD-13` (hard-benign/FPR) và `ADD-14` (split tránh leakage). Kết hợp với BIPIA [83], VortexPIA [18], PromptArmor [66] và survey chọn lọc thành danh sách đọc chính; không mở rộng theo số lượng paper.

**Đọc theo nhu cầu:** `ADD-01/09` khi có ingest HTML/PDF; `ADD-02` khi có outbound request; `ADD-05` khi có agent nhiều bước; `ADD-07` khi đánh giá retrieval end-to-end. Các mục khác là bổ trợ theo [bảng phân loại CSKH](Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md), không phải backlog bắt buộc.

**Phân biệt leakage:** `ADD-14` là **data leakage giữa train/test**, trong khi `ADD-02` là **rò rỉ thông tin qua outbound requests**. Đây là hai khái niệm hoàn toàn khác.


# 3. TAXONOMY GỐC A–I (GIỮ CẤU TRÚC PHƯƠNG PHÁP, SẮP XẾP 23 HỒ SƠ THEO NĂM)

# A. ATTACK GENERATION — CÁCH TẠO PAYLOAD

**Nguồn:** Section 3.1, trang 3–4, **Table 1**. [Survey] Có hai nhóm lớn: **Heuristic-based (23/37)** và **Optimization-based (14/37)**.

## A.1. Heuristic-based attacks (23 công trình)

### A1. Manual Template — 16 công trình | P1

- **Cơ chế [Survey]:** Con người thiết kế thủ công chỉ dẫn độc hại; khai thác xu hướng làm theo chỉ dẫn, đặc biệt là chỉ dẫn giả thẩm quyền, xung đột ưu tiên, hoặc được giấu trong memory/log/tài liệu. Một số công trình nghiên cứu cấy backdoor vào dữ liệu training.
- **Các hành vi thường nhắm tới:** goal/action/task hijacking, rò rỉ dữ liệu, sai lệch đánh giá, misinformation, từ chối hoặc gián đoạn suy luận.
- **Ứng dụng [Đề xuất]:** Tạo những mẫu tấn công trong `user_message`, mô tả sản phẩm, đánh giá người mua, FAQ và phản hồi API; lưu lại nguồn đã bị chỉnh sửa.
- **Phòng tránh liên quan trong survey:** instruction–data separation (Spotlighting [26]); detection filter (PromptArmor [66], PromptShield [30]); task alignment [31] và flow control [15, 67] nếu có tool calls.
- **Giới hạn:** Chặn theo từ khóa có thể bắt nhầm tài liệu hợp lệ *trích dẫn* câu lệnh độc hại; template đơn giản không đại diện cho tấn công tự động hiện đại.
- **Tài liệu trong nhóm theo Table 1:**
  - **2024** · [91] *Towards Action Hijacking of Large Language Model-based Agent* — tấn công qua agent memory.
  - **2025** · [17] *MAD-SPEAR: A Conformity-Driven Prompt Injection Attack on Multi-Agent Debate Systems* — tác động đồng thuận nhiều Agent.
  - **2024** · [37] *Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems* — lây lan qua luồng trao đổi Agent.
  - **2025** · [2] *Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During Task Execution* — rò rỉ dữ liệu cá nhân.
  - **2025** · [3] *Breaking the Prompt Wall (I): A Real-World Case Study of Attacking ChatGPT via Lightweight Prompt Injection* — lightweight attack.
  - **2024** · [56] *Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-Driven Cyberattacks* — tấn công qua log / ngữ cảnh agent.
  - **2024** · [12] *Prompt Injection Attacks on Large Language Models in Oncology* — sai lệch thông tin trong ứng dụng y tế.
  - **2024** · [81] *Preemptive Answer “Attacks” on Chain-of-Thought Reasoning* — can thiệp vào suy luận.
  - **2024** · [68] *Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks* — chiếm quyền tác vụ dịch.
  - **2025** · [46] *“Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors* — tấn công coding agent.
  - **2025** · [62] *EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System* — data exfiltration.
  - **2025** · [51] *Cybersecurity AI: Hacking the AI Hackers via Prompt Injection* — thay đổi hành động agent an ninh.
  - **2025** · [94] *When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review* — thao túng đánh giá.
  - **2025** · [50] *Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections* — thao túng hệ thống chấm.
  - **2024** · [63] *Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment* — đầu độc alignment.
  - **2025** · [9] *Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods* — backdoor trong quá trình huấn luyện.

### A2. LLM Generation — 3 công trình | P2

- **Cơ chế [Survey]:** Dùng một Red-team LLM sinh payload dựa trên quy tắc hoặc chiến lược heuristic; không mặc nhiên đồng nghĩa với tối ưu lặp theo một hàm mục tiêu như nhóm Optimization.
- **Ứng dụng [Đề xuất]:** Hỗ trợ sinh biến thể test (thay cách diễn đạt, ngữ cảnh, ngôn ngữ), sau đó **gắn nhãn và kiểm tra thủ công** trước khi đưa vào golden test.
- **Giới hạn:** Có thể sinh mẫu trùng lặp, khó kiểm soát chất lượng, hoặc quá giống các mẫu dùng để điều chỉnh detector.
- **Công trình trong Table 1:**
  - **2025** · [16] *Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression* — khai thác suy luận/availability.
  - **2025** · [18] *VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy* — nhắm đến privacy leakage.
  - **2025** · [43] *Counterfactual Evaluation for Blind Attack Detection in LLM-Based Evaluation Systems* — đánh giá/tấn công hệ thống chấm.

### A3. Structural Encoding — 4 công trình | P1

- **Cơ chế [Survey]:** Mã hóa hoặc bố trí payload theo cấu trúc nhằm tạo khoảng cách giữa bộ lọc văn bản và cách mô hình/ứng dụng giải thích nội dung; paper lấy ví dụ **Base64, ASCII art và structured file layout**.
- **Ứng dụng [Đề xuất]:** Benchmark các payload trong văn bản sản phẩm, HTML, Markdown hoặc tài liệu được parser chuyển thành text; cần đo cả tính hợp lệ của dữ liệu sau chuẩn hóa.
- **Phòng tránh liên quan:** parser-aware checks, phát hiện đoạn đáng ngờ, không mặc nhiên chạy theo chỉ dẫn được giải mã; kiểm tra chéo cả bản raw và bản sau tiền xử lý.
- **Giới hạn:** Không phải chuỗi Base64 nào cũng độc hại; mỗi loại parser có cách xử lý khác nhau.
- **Công trình trong Table 1:**
  - **2025** · [14] *Publish to Perish: Prompt Injection Attacks on LLM-Assisted Peer Review* — đánh giá tài liệu.
  - **2025** · [24] *Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions* — làm sai đánh giá/câu hỏi.
  - **2025** · [61] *Exploiting Web Search Tools of AI Agents for Data Exfiltration* — rò rỉ qua web search tools.
  - **2025** · [35] *Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications* — thao túng reviewer.

### A.1.1. 23 HỒ SƠ HEURISTIC-BASED — SẮP XẾP THEO THỜI GIAN

> **Đã thay đổi bố cục:** Các mã H01–H16, G01–G03, S01–S04 được **giữ nguyên**; chỉ chuyển vị trí hồ sơ để đọc theo năm. Năm lấy từ **References trong survey** (năm công bố theo cách tác giả survey trích), không mặc định trùng năm nộp bản arXiv đầu tiên. Trong cùng năm, nhóm theo loại để tiện tra cứu; đây **không phải thứ tự độ khó**.

| Năm theo bibliography survey | Manual | LLM Generation | Structural | Tổng |
|---:|---:|---:|---:|---:|
| 2024 | 7 | 0 | 0 | 7 |
| 2025 | 9 | 3 | 4 | 16 |

| Năm | Mã hồ sơ | Ref survey | Tên gốc | Hướng nghiên cứu |
|---:|---|---|---|---|
| 2024 | [H01](#paper-h01) | [91] | AI²: Towards Hijacking the Actions of Large Language Model-based Applications | Manual |
| 2024 | [H03](#paper-h03) | [37] | Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems | Manual |
| 2024 | [H06](#paper-h06) | [56] | Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberatta | Manual |
| 2024 | [H07](#paper-h07) | [12] | Prompt Injection Attacks on Large Language Models in Oncology | Manual |
| 2024 | [H08](#paper-h08) | [81] | Preemptive Answer “Attacks” on Chain-of-Thought Reasoning | Manual |
| 2024 | [H09](#paper-h09) | [68] | Scaling Behavior of Machine Translation with Large Language Models under Prompt Inject | Manual |
| 2024 | [H15](#paper-h15) | [63] | Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign) | Manual |
| 2025 | [H02](#paper-h02) | [17] | MAD-Spear: A Conformity-Driven Prompt Injection Attack on Multi-Agent Debate Systems | Manual |
| 2025 | [H04](#paper-h04) | [2] | Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During T | Manual |
| 2025 | [H05](#paper-h05) | [3] | Breaking the Prompt Wall (I): A Real-World Case Study of Attacking ChatGPT via Lightwe | Manual |
| 2025 | [H10](#paper-h10) | [46] | “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editor | Manual |
| 2025 | [H11](#paper-h11) | [62] | EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM | Manual |
| 2025 | [H12](#paper-h12) | [51] | Cybersecurity AI: Hacking the AI Hackers via Prompt Injection | Manual |
| 2025 | [H13](#paper-h13) | [94] | When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer R | Manual |
| 2025 | [H14](#paper-h14) | [50] | Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections | Manual |
| 2025 | [H16](#paper-h16) | [9] | Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods | Manual |
| 2025 | [G01](#paper-g01) | [16] | Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adap | LLM-generated |
| 2025 | [G02](#paper-g02) | [18] | VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of U | LLM-generated |
| 2025 | [G03](#paper-g03) | [43] | Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems | LLM-generated |
| 2025 | [S01](#paper-s01) | [14] | Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Promp | Structural |
| 2025 | [S02](#paper-s02) | [24] | Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choic | Structural |
| 2025 | [S03](#paper-s03) | [61] | Exploiting Web Search Tools of AI Agents for Data Exfiltration | Structural |
| 2025 | [S04](#paper-s04) | [35] | Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications | Structural |

**Cách đọc:** xem năm ở tiêu đề từng bài, rồi phần cơ chế → threat model → benchmark/defense → bài học cho chatbot. Phần diễn giải chi tiết được giữ từ bản nghiên cứu 23 hồ sơ trước đó; việc bổ sung năm không đồng nghĩa đã tái chạy thí nghiệm hay kiểm tra từng phiên bản mới nhất của tất cả 23 bài.

<a id="paper-h01"></a>

#### 2024 · H01 — [91] AI²: Towards Hijacking the Actions of Large Language Model-based Applications

**Bài gốc:** [arXiv:2412.10807](https://arxiv.org/abs/2412.10807) · [Toàn văn HTML](https://arxiv.org/html/2412.10807). *Tên trong survey hơi khác tên hiển thị trên bản HTML; cùng mã arXiv.*

- **[Gốc] Bài toán/threat model:** Agent/ứng dụng có bước lấy kiến thức từ database/RAG rồi lập kế hoạch hành động. Attacker tận dụng đầu vào và tri thức gợi ý hành động; mục tiêu làm mô hình sinh kế hoạch sai hoặc nguy hại dù bề mặt câu chữ có thể trông lành tính. Không nên đơn giản hóa thành duy nhất "chép câu Ignore previous" vào memory.
- **[Gốc] Cách tấn công:** (1) trích xuất tri thức liên quan đến hành động từ ứng dụng mục tiêu; (2) xây tập prompt ứng viên để kích hoạt loại hành động mong muốn; (3) ghép câu hỏi/đầu vào với "action-aware knowledge" để LLM lập kế hoạch sai; (4) tối ưu lựa chọn/biểu diễn. Có bước tối ưu trong công trình, vì vậy nhãn **Manual Template của survey là cách xếp loại khái quát**, không có nghĩa phương pháp hoàn toàn thủ công.
- **[Gốc] Benchmark:** Bối cảnh ứng dụng y tế, tạo SQL và các ứng dụng dùng tri thức; so sánh với tấn công thông thường và các cơ chế lọc bảo mật. Metric chính: tỷ lệ lập kế hoạch/hành động bị chiếm hướng (**ASR**) và tỷ lệ qua bộ lọc. Bài báo nêu ASR trung bình **84,30%**, cao nhất **99,70%**, bypass bộ lọc phổ biến **92,7%** và bypass defense chuyên dụng **59,45%** trong các phép thử mà tác giả thiết lập; không suy rộng sang mọi mô hình.
- **[Gốc] Phòng thủ được đánh giá:** Bộ lọc từ khóa/rule, phân loại an toàn và các cơ chế dựa trên LLM/viết lại prompt xuất hiện trong phân tích khả năng vượt phòng thủ; tác giả nhận xét chỉ rà từ khóa độc hại không đủ. **[Ứng dụng đề xuất]** kiểm tra sự phù hợp giữa *task của khách hàng*, nguồn tri thức RAG và hành động (nếu chatbot có tools), thay vì chỉ tìm trigger words.
- **Hạn chế/kết luận:** Cần tương tác với một pipeline tri thức/hành động tương đối đặc thù; thước đo "action plan" không luôn tương đương tool đã thực thi. **Áp dụng:** tạo case mô tả sản phẩm/FAQ gợi chatbot lựa chọn chính sách hoàn tiền hay đường dẫn trái phép. **Ưu tiên:** P2 cho demo, P1 để hiểu context poisoning.

<a id="paper-h03"></a>

#### 2024 · H03 — [37] Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems

**Bài gốc:** [arXiv:2410.07283](https://arxiv.org/abs/2410.07283) · [HTML](https://arxiv.org/html/2410.07283).

- **[Gốc] Threat model:** Multi-agent chia sẻ message và memory. Đối thủ cài một chỉ dẫn có thể **được Agent bị nhiễm lặp lại khi trò chuyện**, rồi lây sang Agent khác qua luồng giao tiếp bình thường.
- **[Gốc] Cơ chế:** Payload tự tái sản xuất/lan truyền như "infection" trong hội thoại liên-Agent; có thể thao túng độ ưu tiên của thông tin lưu trữ (memory importance) để kéo dài tác động. Đây không phải worm tự thực thi ở hệ điều hành; nó lợi dụng việc LLM diễn giải text thành nhiệm vụ.
- **[Gốc] Benchmark:** Môi trường mô phỏng cộng đồng Agent với nhiều kích cỡ nhóm; mô hình như GPT-4o/GPT-3.5; kiểm tra propagation, mức độ giữ lại trong memory và ảnh hưởng đến hành động. Paper ghi nhận memory importance có thể bị đẩy từ mức nền khoảng **1,94** lên **10** ở một cấu hình GPT-4o; không dùng số này làm ASR chung.
- **[Gốc] Defense được thử:** Marking/tracking nguồn thông tin, LLM tagging, defensive instructions và một số tổ hợp. Có cấu hình phối hợp **Marking + LLM Tagging** đạt ASR **0%** trong phép thử của bài, nhưng đó không phải bảo đảm trước mọi kiểu lây lan.
- **Hạn chế/kết luận:** Thành công phụ thuộc cơ chế giao tiếp/memory của mô phỏng. **[Ứng dụng đề xuất]** chỉ cần áp dụng ý tưởng tách nguồn trusted/untrusted cho memory hoặc chat history nếu chatbot hỗ trợ lịch sử dài. **Ưu tiên P3** nếu ứng dụng một chatbot đơn lẻ.

<a id="paper-h06"></a>

#### 2024 · H06 — [56] Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-driven Cyberattacks (Mantis)

**Bài gốc:** [arXiv:2410.20911](https://arxiv.org/abs/2410.20911) · [HTML](https://arxiv.org/html/2410.20911).

- **[Gốc] Điểm khác bản chất:** **Prompt Injection được bên phòng thủ sử dụng để gây nhiễu một Agent pentest tấn công**, chứ không phải một công trình xây Guardrails cho chatbot khách hàng. Tuy vậy survey liệt kê nó dưới Manual Template attack vì cơ chế vẫn là chèn chỉ dẫn vào dữ liệu đối thủ đọc.
- **[Gốc] Cơ chế:** Mantis cài nội dung mồi/response/log giả trong dịch vụ bị Agent quét; khi Agent an ninh đọc các kết quả công cụ, nó có thể làm theo chỉ dẫn ngoài ý muốn, mất mục tiêu hoặc đi vào hành vi do người kiểm soát máy chủ mồi đề xuất.
- **[Gốc] Benchmark:** Tác giả thử với các agent pentest như PentestGPTAuto, AutoPenAgent, HackingBuddyGPT trên các tác vụ kiểu CTF/cyberattack; báo cáo hiệu quả phòng vệ chống Agent ở một số cấu hình trên **95%**, là tỷ lệ tác giả công bố cho thiết lập của Mantis, **không** phải tỷ lệ phát hiện PI trong chatbot.
- **[Gốc] Defense:** Đây tự thân là "active defense" gây nhiễu bên tấn công; không có bộ guardrail PII/chatbot được kiểm tra theo tiêu chí của đề tài bạn. **[Ứng dụng đề xuất]** tránh triển khai tính năng "hack back"; chỉ rút ra bài học rằng **log, trang lỗi, phản hồi web đều không đáng tin**.
- **Hạn chế/kết luận:** Threat model và tính pháp lý/đạo đức của phản công khác hoàn toàn ứng dụng kinh doanh. **Ưu tiên P3.**

<a id="paper-h07"></a>

#### 2024 · H07 — [12] Prompt Injection Attacks on Large Language Models in Oncology

**Bài gốc:** [arXiv:2407.18981](https://arxiv.org/abs/2407.18981) · [HTML](https://arxiv.org/html/2407.18981).

- **[Gốc] Threat model:** Hệ thống LLM hoặc multimodal LLM hỗ trợ phân tích ảnh/chỉ định y khoa. Attacker tác động nội dung hình ảnh/tệp đưa vào hệ thống; mục tiêu làm sai đánh giá y khoa.
- **[Gốc] Kỹ thuật:** Chèn prompt vào **dữ liệu thị giác** với mức khó nhận biết bằng mắt người; quan sát xem mô hình đa phương thức thay đổi phán đoán hay không. Vì thế không nên xem [12] chỉ là "misinformation dạng text".
- **[Gốc] Benchmark:** Tác giả xây **297 ảnh/case tấn công** trong các tác vụ nhận diện/chẩn đoán liên quan ung thư; thử nhiều multimodal model như GPT-4o, Claude, Reka. Đánh giá sai lệch đầu ra khi có/không có nội dung chèn.
- **[Gốc] Defense:** Bài tập trung đánh giá lỗ hổng; không thử một pipeline detector + sanitizer đủ mạnh để khẳng định phương pháp phòng thủ nào đạt bảo đảm.
- **Hạn chế/kết luận:** Domain y tế và ảnh khác text RAG; tác động phụ thuộc mô hình/thao tác ảnh. **[Ứng dụng đề xuất]** chỉ cân nhắc khi chatbot dùng ảnh sản phẩm/tài liệu scan. **P3.**

<a id="paper-h08"></a>

#### 2024 · H08 — [81] Preemptive Answer “Attacks” on Chain-of-Thought Reasoning

**Bài gốc:** [arXiv:2405.20902](https://arxiv.org/abs/2405.20902) · [HTML](https://arxiv.org/html/2405.20902).

- **[Gốc] Threat model:** Mô hình đang giải câu hỏi suy luận với chain-of-thought. Attacker đặt **đáp án giả định sai xuất hiện sớm** trong chuỗi đầu vào/đầu lời giải, khiến mô hình bị "neo" vào đáp án đó thay vì suy luận độc lập.
- **[Gốc] Kỹ thuật:** *Preemptive answer* không nhất thiết là mệnh lệnh từ chối hay gọi tool; bản chất là **answer contamination / reasoning bias**. Dù survey ghi nhãn CoT DoS, không nên diễn giải toàn bộ công trình là tấn công làm treo/dừng suy luận; mục tiêu đáng chú ý nhất là suy luận sai.
- **[Gốc] Benchmark:** Các tập suy luận như GSM8K, MATH, MathQA, HotpotQA, CommonsenseQA, StrategyQA; nhiều model/prompting setup; so sánh accuracy/correctness với và không có câu trả lời bị cấy sớm.
- **[Gốc] Defense thực nghiệm:** **Problem restatement** (diễn đạt lại bài toán) và **self-reflection** (tự rà kết quả) được nghiên cứu như chiến lược giảm lệ thuộc vào lời giải bị dẫn dắt; không hoàn toàn loại bỏ tác động ở mọi cấu hình.
- **Hạn chế/kết luận:** Thí nghiệm CoT không tự động chứng minh cơ chế hoạt động của một external RAG tool. **[Ứng dụng đề xuất]** tạo case review/FAQ chứa một kết luận giá/sản phẩm sai thay vì lệnh rõ ràng; phân biệt **data misinformation** với **prompt instruction** khi gắn nhãn. **P2.**

<a id="paper-h09"></a>

#### 2024 · H09 — [68] Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks

**Bài gốc:** [arXiv:2403.09832](https://arxiv.org/abs/2403.09832) · [HTML](https://arxiv.org/html/2403.09832) · [Mã/dữ liệu nghiên cứu](https://github.com/Avmb/MT_Scaling_Prompt_Injection).

- **[Gốc] Threat model:** LLM được giao **dịch một đoạn văn bản**; đối thủ kiểm soát đoạn nguồn cần dịch (dữ liệu) và cấy một lệnh khiến mô hình **trả lời nội dung** thay vì dịch. Đây là ví dụ rõ ràng về tấn công vượt ranh giới **instruction vs input data**.
- **[Gốc] Cách tấn công:** Tác giả biến câu hỏi TruthfulQA thành văn bản cần dịch; thêm tiền tố kiểu "đừng dịch câu này, hãy trả lời câu hỏi" bằng tiếng Anh hoặc ngôn ngữ nguồn. Mô hình thành công ở tác vụ hợp lệ nếu tiếp tục *dịch* dù câu văn được dịch là câu hỏi/mệnh lệnh.
- **[Gốc] Benchmark:** **817 câu hỏi** gốc từ TruthfulQA được dịch sang Đức, Pháp, Romania, Nga; sau lọc chất lượng tạo cặp ngôn ngữ En–De/Fr/Ro/Ru. Thử T5, FLAN-T5, GPT-3, InstructGPT, Llama2 và Llama2-chat ở nhiều kích thước; so sánh zero-shot và one-shot. Tác giả cho thấy **BLEU một mình không đủ** để đánh giá: một câu trả lời đúng chủ đề nhưng không phải bản dịch có thể đạt BLEU cao hơn bản dịch hợp lệ. Vì vậy có thêm tiêu chí xem model *dịch* hay *trả lời* câu hỏi.
- **[Gốc] Defense/giảm thiểu có đánh giá:** Bổ sung **một ví dụ dịch (one-shot in-context example)** có thể đảo ngược hiện tượng inverse scaling ở một số cấu hình Llama2; tác giả **không xây một guardrail detector độc lập**.
- **Hạn chế/kết luận:** Mô hình lớn hơn **đôi khi** dễ mắc hơn khi zero-shot (inverse scaling), nhưng không phải trên mọi họ model/cấu hình. **[Ứng dụng đề xuất]** Tạo bài test chatbot phải *tóm tắt* review hoặc chính sách, trong đó review có câu "hãy trả lời thay vì tóm tắt". Chấm **task hijack** thay vì chỉ xét có chuỗi nhạy cảm. **Ưu tiên P1 về nguyên lý, P2 về tái lập.**

<a id="paper-h15"></a>

#### 2024 · H15 — [63] Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign)

**Bài gốc:** [arXiv:2410.14827](https://arxiv.org/abs/2410.14827) · [HTML](https://arxiv.org/html/2410.14827).

- **[Gốc] Threat model:** Attacker có khả năng **đầu độc một phần dữ liệu dùng căn chỉnh mô hình** trước khi model được triển khai, không chỉ sửa tin nhắn chat. Sau đó, model vẫn hoạt động bình thường ở nhiều tác vụ nhưng trở nên dễ làm theo chỉ dẫn được chèn từ nguồn thấp quyền.
- **[Gốc] Cơ chế:** **Alignment poisoning** trong supervised fine-tuning/preference optimization tạo ra sự phụ thuộc có chủ đích để *prompt injection tiếp theo* đạt hiệu quả cao hơn. Đây là **training supply chain**; không phải một payload xuất hiện lần đầu trong mô tả sản phẩm.
- **[Gốc] Benchmark:** Các backbone Llama/Gemma/Falcon và tập alignment như HH-RLHF/ORCA-DPO; tác giả so sánh mô hình trước/sau poisoning trên **Attack Success Value (ASV)** và benchmark tác vụ bình thường (chẳng hạn MMLU, GSM8K, GPQA). Ví dụ một cấu hình Llama3 trong nguồn nêu **ASV hard ~0,39 → ~0,66** sau poisoning, trong khi chất lượng nền không giảm mạnh tương ứng.
- **[Gốc] Defense:** Nghiên cứu chủ yếu phơi bày điểm yếu của pipeline alignment, không chứng minh một detector prompt bên ngoài có thể sửa sự cố training. Các thảo luận về làm sạch dữ liệu/cẩn trọng nguồn training không nên gán nhãn là defense đã benchmark thành công.
- **Hạn chế/kết luận:** Đòi hỏi attacker kiểm soát dữ liệu huấn luyện, khác với kịch bản black-box chatbot bán hàng. **[Ứng dụng đề xuất]** ghi trong threat model là *out of scope* và lựa chọn nhà cung cấp/model đáng tin cậy. **P3.**

<a id="paper-h02"></a>

#### 2025 · H02 — [17] MAD-Spear: A Conformity-Driven Prompt Injection Attack on Multi-Agent Debate Systems

**Bài gốc:** [arXiv:2507.13038](https://arxiv.org/abs/2507.13038) · [HTML](https://arxiv.org/html/2507.13038).

- **[Gốc] Threat model:** Nhiều LLM-agent trao đổi, tranh luận và đồng thuận. Attacker làm ô nhiễm thông điệp/quan điểm của một Agent để những Agent còn lại bị tâm lý đồng thuận, dẫn tới đáp án sai.
- **[Gốc] Phương pháp:** Thông điệp giả mạo mô phỏng sự nhất trí hoặc đáp án chắc chắn của các Agent khác; nội dung độc hại lẫn trong message passing. Đây là **consensus manipulation**, không phải xâm nhập API hay sửa trọng số LLM.
- **[Gốc] Benchmark:** Các tác vụ suy luận toán và kiến thức như GSM-Ranges và MMLU; so sánh debate không tấn công, các mẫu tấn công và tình huống chỉ một Agent bị chi phối. Tác giả báo cáo ASR trung bình khoảng **56,66%** so với một baseline khoảng **6,67%** trên cấu hình được mô tả; mức tiêu hao token có thể tăng khi tranh luận bị kéo dài. Các con số phụ thuộc bố trí số Agent và vòng debate.
- **[Gốc] Defense:** Công trình tập trung trình diễn attack; **không có một hệ phòng thủ được kiểm chứng đầy đủ với cùng độ sâu như attack**. Gợi ý theo dõi nguồn message, provenance và sự nhất quán liên-Agent chủ yếu là bài học triển khai, không được báo là đã "giải quyết" attack.
- **Hạn chế/kết luận:** Chỉ thích hợp khi ứng dụng có **multi-agent debate**. **[Ứng dụng đề xuất]** chatbot một Agent không cần triển khai; nếu về sau có reviewer/bot nội bộ, nên không coi lời từ Agent khác là nguồn tin cậy tuyệt đối. **Ưu tiên P3.**

<a id="paper-h04"></a>

#### 2025 · H04 — [2] Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During Task Execution

**Bài gốc:** [arXiv:2506.01055](https://arxiv.org/abs/2506.01055) · [PDF](https://arxiv.org/pdf/2506.01055).

- **[Gốc] Threat model:** Agent được ủy quyền truy cập **PII giả lập** trong lúc làm tác vụ hợp lệ (ví dụ thông tin khách hàng/giao dịch). Attacker kiểm soát một phần **tool observation** và lồng chỉ dẫn yêu cầu Agent gửi dữ liệu đó ra ngoài qua công cụ email. Không giả định attacker đọc sẵn PII; nguy cơ nằm ở quyền Agent truy cập.
- **[Gốc] Payload:** Các template ngôn ngữ tự nhiên như thông báo quan trọng, giả yêu cầu ưu tiên, yêu cầu "TODO" hay mẫu theo InjecAgent; nhắm tạo hành động **exfiltration** chứ không chỉ làm chatbot nhắc lại một chuỗi.
- **[Gốc] Benchmark:** Thực nghiệm trên kịch bản banking của **AgentDojo**, bao gồm 16 tác vụ gốc và phần mở rộng 48 tình huống; nhiều LLM và defense; dùng PII tổng hợp. Metric quan trọng nhất là **dữ liệu thực sự được phát tán qua thao tác/egress** cùng với **utility** trên nhiệm vụ hợp lệ. Bài báo cho thấy mức thành công tấn công biến động đáng kể theo mô hình/tác vụ; một số cấu hình khoảng 15–20%, nhưng không phải một tỷ lệ phổ quát.
- **[Gốc] Defense được thử:** Nhắc lại chỉ dẫn user, detector prompt injection, tool filter và delimiters. Có cấu hình detector giảm ASR rất mạnh, thậm chí 0% trong tập 16 task cụ thể, **đồng thời làm giảm utility** (ví dụ mức được bài báo nêu ~43,8% so với baseline ~87,5%); vì thế không kết luận cứ chặn mạnh là tốt.
- **Hạn chế/kết luận:** Benchmark mô phỏng; email/PII được tạo có kiểm soát; không chứng minh dữ liệu thật đã bị lộ trong doanh nghiệp. **[Ứng dụng đề xuất] P1:** kiểm tra PII **trước egress**, chặn đích gọi công cụ trái phép; golden phải phân biệt "PII có trong context", "PII đã gửi tới LLM API" và "PII bị gửi ra kênh ngoài trái phép". Đây là nghiên cứu **đúng trọng tâm** cho tính năng PII doanh nghiệp.

<a id="paper-h05"></a>

#### 2025 · H05 — [3] Breaking the Prompt Wall (I): A Real-World Case Study of Attacking ChatGPT via Lightweight Prompt Injection

**Bài gốc:** [arXiv:2504.16125](https://arxiv.org/abs/2504.16125) · [HTML](https://arxiv.org/html/2504.16125).

- **[Gốc] Threat model:** Tấn công nhẹ vào các bối cảnh dùng ChatGPT và GPT ứng dụng, thông qua nội dung có thể khiến mô hình bị chi phối khi đưa ra đánh giá, gợi ý hoặc thông tin.
- **[Gốc] Phương pháp:** Những đoạn chỉ dẫn ngắn, tự nhiên, đôi khi pha với văn bản hợp lệ để hướng mô hình đánh giá cao một lựa chọn, đưa gợi ý thiên lệch hoặc thay đổi nội dung; đáng chú ý vì không nhất thiết chứa chuỗi "Ignore previous instructions".
- **[Gốc] Benchmark:** Các **case study** thao tác với ChatGPT, web và ứng dụng/GPT riêng; chủ yếu quan sát hành vi và tình huống thành công/không thành công, **không phải** một benchmark lớn có test/train chuẩn hay báo cáo ASR đối chiếu thống nhất giữa nhiều defense.
- **[Gốc] Defense:** Không có thí nghiệm phòng thủ đối chứng hệ thống như một paper về detection. **[Ứng dụng đề xuất]** bộ PI classifier cần nhận biết chuyển hướng nhiệm vụ và quảng cáo/khuyến nghị bị điều khiển chứ không chỉ chuỗi lệnh lộ liễu.
- **Hạn chế/kết luận:** Khả năng tái lập có thể thay đổi theo phiên bản dịch vụ và chính sách vận hành. **Áp dụng:** mô tả sản phẩm bên thứ ba cố ép chatbot chỉ quảng bá nhãn hàng hoặc website khác. **P2.**

<a id="paper-h10"></a>

#### 2025 · H10 — [46] “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors (AIShellJack)

**Bài gốc:** [arXiv:2509.22040](https://arxiv.org/abs/2509.22040) · [HTML](https://arxiv.org/html/2509.22040).

- **[Gốc] Threat model:** Coding Agent có quyền đọc repo và gọi công cụ terminal/editor; attacker kiểm soát **file hướng dẫn hoặc nội dung trong repository** mà Agent đọc, nhưng không có quyền gửi system prompt trực tiếp. Mục tiêu là tạo hành động trên môi trường phát triển trái với yêu cầu người dùng.
- **[Gốc] Kỹ thuật:** Chèn các quy tắc giả, thông điệp trong file cấu hình/instructions và biến thể payload nhằm làm coding agent tạo/chạy lệnh hoặc sửa file sai. Tấn công có thể dùng chỉ dẫn dưới dạng quy trình công việc tưởng chừng hợp lý, nên tool approval ở một bước không luôn đủ: Agent có thể tạo file nguy hiểm trước rồi thực thi ở bước sau.
- **[Gốc] Benchmark:** Nghiên cứu **314 payload** trải trên nhiều mục tiêu tấn công/thủ thuật (tác giả liên hệ **70 kỹ thuật MITRE ATT&CK**), thử các editor/agent hỗ trợ code như Cursor và Copilot trong các cấu hình được trình bày. Bài báo có trường hợp ghi nhận ASR **khoảng 84%** cho cấu hình dễ tổn thương, nhưng không phải mỗi biến thể hay mỗi công cụ đều đạt mức đó.
- **[Gốc] Defense:** Bàn và khảo sát các rào chắn như chặn/cho phép command, xin xác nhận người dùng, kiểm soát tool, nhưng các phép thử cho thấy không nên coi một whitelist lệnh đơn giản là giải pháp đầy đủ. Không suy diễn rằng mọi phòng thủ nêu trong phần discussion đều được bench độc lập.
- **Hạn chế/kết luận:** Shell access làm mức độ hậu quả cao hơn chatbot hỏi đáp thông thường. **[Ứng dụng đề xuất]** chỉ áp dụng nếu chatbot có tool `refund_order`, `update_address`, `send_email`, `create_ticket`; các tool phải có policy ngoài LLM, phân quyền và xác nhận server-side. **P2/P3 tùy tool.**

<a id="paper-h11"></a>

#### 2025 · H11 — [62] EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System

**Bài gốc:** [arXiv:2509.10540](https://arxiv.org/abs/2509.10540) · [HTML](https://arxiv.org/html/2509.10540). Tên được khảo sát ghi từ bài gốc; chủ đề là chuỗi tấn công được mô tả với Microsoft 365 Copilot (CVE-2025-32711).

- **[Gốc] Threat model:** Kẻ tấn công bên ngoài có thể gửi email/nội dung để Copilot sau đó retrieval vào context. Người sử dụng thật chỉ yêu cầu làm việc bình thường; payload theo đường **email → retrieval → LLM → đầu ra/đường tải resource**, không cần họ chủ động bấm một liên kết độc hại.
- **[Gốc] Cách tấn công:** Chỉ dẫn xấu được ngụy trang trong nội dung email có vẻ liên quan câu hỏi; tìm cách biến thông tin bí mật đã truy xuất thành thành phần của URL/resource được render hoặc truy cập ra ngoài. Điểm then chốt là **khả năng egress qua URL/image/link ngoài**, kể cả khi mô hình không viết PII nguyên văn trong câu trả lời.
- **[Gốc] Benchmark:** **Case study một chuỗi exploit production**, có phân tích biện pháp bảo vệ bị vượt qua (ví dụ kiểm tra XPIA, redaction/đường proxy). Đây **không** phải benchmark N=1.000 case có ASR tổng quát; không bịa tỷ lệ thành công cho mọi hệ thống.
- **[Gốc] Defense được mô tả/quan sát:** Các lớp kiểm tra injection, hạn chế URL/link và security boundary của sản phẩm được phân tích trong đường tấn công; **không phải một thí nghiệm so sánh 4 classifier theo F1**. **[Ứng dụng đề xuất]** kiểm soát egress URL và rendering Markdown/images; audit đường truyền dữ liệu thật, không chỉ response text; xét nguồn gốc và scope truy cập tài liệu.
- **Hạn chế/kết luận:** Một môi trường ứng dụng cụ thể có thể có lỗ hổng tích hợp đặc thù, không kết luận mọi chatbot đều có cùng lỗi. **P1** cho bài toán *PII exfiltration/egress* của bạn.

<a id="paper-h12"></a>

#### 2025 · H12 — [51] Cybersecurity AI: Hacking the AI Hackers via Prompt Injection

**Bài gốc:** [arXiv:2508.21669](https://arxiv.org/abs/2508.21669) · [HTML](https://arxiv.org/html/2508.21669). *Bản HTML được kiểm tra là bản lưu hành sau nhiều cập nhật; cần đối chiếu v1 nếu trích đúng mốc survey 20/10/2025.*

- **[Gốc] Threat model:** Agent thực hiện kiểm thử bảo mật, được phép dùng terminal/curl để đọc nội dung từ server mục tiêu. Attacker sở hữu **server/web response** mà Agent đi quét và đặt các chỉ dẫn tưởng là "hướng dẫn xử lý lỗ hổng" trong phản hồi. Khi tool observation trở thành instruction, attacker có thể khiến Agent tự chạy thao tác ngoài ý muốn.
- **[Gốc] Các kiểu được phân tích:** Chỉ dẫn trực tiếp; mã hóa Base64/nhiều lớp; Unicode homoglyph; shell/environment indirection; gợi Agent viết source code rồi chạy; nội dung trong banner/log/file comment. Cơ chế chung là chuyển dữ liệu từ nguồn bị kiểm soát sang quyền thực thi của Agent. Không đưa các lệnh shell nguy hiểm nguyên văn vào test chatbot bán hàng.
- **[Gốc] Benchmark:** Bản HTML báo cáo **14 biến thể × 10 lần = 140 phép thử**, tổng **128/140 (~91,4%)** lần khai thác thành công khi không bảo vệ; các biến thể trực tiếp có thể đạt 100% ở nhóm thử cụ thể. Đây là nghiên cứu PoC trên **CAI framework**, không phải khảo sát ngẫu nhiên Agent trên thị trường.
- **[Gốc] Defense thực nghiệm:** Bốn lớp: **sandbox/container**, kiểm tra tool-output `curl/wget` và gắn nhãn data-only, kiểm tra file/script được viết, và validation bổ sung trên input/output. Tác giả báo **0/140 lần thành công** sau bộ defense được kiểm thử, với độ trễ tăng trung bình cỡ **12,3 ms**, nhưng không thể suy diễn bảo đảm chống payload thích nghi chưa được thử.
- **Hạn chế/kết luận:** Sandbox và pattern filter đều có giới hạn (sandbox escape, bypass pattern); quyền shell làm hậu quả nghiêm trọng hơn QA chatbot. **[Ứng dụng đề xuất]** tách `tool_result` khỏi instruction và thêm **allowlist đích truyền**. **P2**, nhưng rất hữu ích cho phần defense-in-depth.

<a id="paper-h13"></a>

#### 2025 · H13 — [94] When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review

**Bài gốc:** [arXiv:2509.09912](https://arxiv.org/abs/2509.09912) · [HTML](https://arxiv.org/html/2509.09912).

- **[Gốc] Threat model:** Reviewer tự động đọc PDF manuscript của tác giả; tác giả có thể chỉnh **văn bản/bố cục và font mapping trong PDF** nhưng không được chỉnh instruction reviewer. Mục tiêu tăng điểm và thay đổi kết luận bình duyệt.
- **[Gốc] Cơ chế:** Chỉ dẫn được đưa vào PDF qua những kỹ thuật khó thấy bởi người đọc, gồm **ánh xạ glyph/font** để parser/LLM gặp nội dung khác nội dung người nhìn; các biến thể prompt đặt ở trường tổng quan hoặc trường đánh giá cụ thể. Đây là **document-parsing / modality mismatch**, không phải chỉ thay chữ màu trắng.
- **[Gốc] Benchmark:** Tác giả phân tích **1.441 bài báo** từ ICLR 2023 và NeurIPS 2022 ở quy trình đánh giá; thực nghiệm trên mô hình reviewer như GPT-5-mini. Tác động khác nhau theo chỗ đặt payload: ở một cấu hình field-specific, có thể khiến một tỷ lệ case đạt điểm tuyệt đối khi lặp lại, nhưng không thể diễn giải là "mọi PDF bị chèn đều qua mặt 100%". Một số so sánh cho thấy thay đổi điểm trung bình từ ~6,86 lên ~7,21 với kiểu attack rộng.
- **[Gốc] Defense:** Bài tập trung đo bias/vulnerability; các khuyến nghị về parser nhất quán, provenance, xác minh bản render và audit là **bài học/gợi ý**, không phải một bộ detection được benchmark end-to-end.
- **Hạn chế/kết luận:** Kết quả phụ thuộc PDF parser, dạng rubric, mô hình và cách đóng gói. **[Ứng dụng đề xuất]** nếu chatbot tiếp nhận tài liệu sản phẩm PDF: so sánh **văn bản trích xuất** với **văn bản hiển thị**, giữ metadata kiểu font/size/visibility; tập test cần PDF fixture. **P2 nếu hỗ trợ PDF, P3 nếu text-only.**

<a id="paper-h14"></a>

#### 2025 · H14 — [50] Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections

**Bài gốc:** [arXiv:2504.18333](https://arxiv.org/abs/2504.18333) · [PDF nguyên bản v1 (12 trang)](https://arxiv.org/pdf/2504.18333). *Bản HTML arXiv có lúc không truy cập được; phần định lượng được đối chiếu trực tiếp với Table I, VI, VII, VIII trong PDF gốc.*

- **[Gốc] Threat model:** LLM làm **bộ chấm** cho text/code/lập luận; attacker kiểm soát **bài nộp hoặc nội dung đang được chấm**, đôi khi thử tác động prompt của bộ chấm. Đích đến là đánh giá ưu ái nội dung sai hoặc cho điểm không trung thực.
- **[Gốc] Attack:** Các dạng direct instruction, ngôn từ gây nhiễu, dẫn dắt ngữ cảnh và tìm kiếm/điều chỉnh câu tấn công theo feedback. Lưu ý: **survey xếp Manual Template nhưng một số biến thể của công trình có yếu tố adaptive search**, không được gọi tất cả là "thủ công thuần".
- **[Gốc] Benchmark:** 5 mô hình, gồm các dòng Gemma 3, Llama 3.2, GPT-4, Claude 3 Opus; **4 nhiệm vụ chấm** với **50 prompt/mỗi điều kiện**; xét tính chuyển giao giữa các mô hình. Abstract nêu ASR có trường hợp tới **73,8%** và transferability **50,5–62,6%**. Không áp các tỷ lệ này trực tiếp cho chatbot thương mại điện tử.
- **[Gốc] Defense ĐÃ được thử (Section IV và Table VI/VII):** (i) **perplexity-based detection**, (ii) **instruction filtering/sanitization**, (iii) **content moderation classifier** (RoBERTa-base được fine-tune theo mô tả của tác giả), (iv) **kết hợp ba cách**, (v) **multi-model committees**. Trong Table VI, tỷ lệ *evasion* khi kết hợp ba bộ lọc còn **18,5–42,1%** tùy attack BI/CWB/CM/ASA; không phải 0%. Table VII cho thấy committee **7 model khác kiến trúc** còn ASR **10,2–19,3%** theo kiểu attack, thấp hơn committee 3 model, nhưng có chi phí lớn hơn. Đây là số liệu *tác giả báo cáo*, không phải phép tái kiểm chứng độc lập. **[Ứng dụng đề xuất]** nếu dùng LLM-as-a-Judge để chấm ASR, phải có **golden xác định bằng code** (đích website, giá, trạng thái tool) và audit mẫu chấm thủ công, vì chính judge cũng có thể bị tấn công.
- **Hạn chế/kết luận:** Chất lượng metric phụ thuộc loại judge và cấu hình task; khó đo bằng một accuracy duy nhất. **P1 cho an toàn đánh giá, P3 cho triển khai attack vào sản phẩm.**

<a id="paper-h16"></a>

#### 2025 · H16 — [9] Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods

**Bài gốc:** [arXiv:2510.03705](https://arxiv.org/abs/2510.03705) · [HTML](https://arxiv.org/html/2510.03705). *Mã arXiv gốc không xuất hiện trong tên ở References survey; xác minh theo tên, tác giả [9].*

- **[Gốc] Threat model:** Attacker tác động vào **dữ liệu supervised fine-tuning**, cấy một **trigger/backdoor** khiến model có thể tuân theo chỉ dẫn thấp quyền ngay cả sau khi áp dụng defense theo thứ bậc instruction.
- **[Gốc] Cách tấn công:** Nhúng mẫu trigger trong một tỷ lệ nhỏ training data; khi trigger xuất hiện trong nội dung sau này, model xem instruction độc hại là đáng tin. Không đồng nhất tấn công này với Unicode obfuscation, vì nguyên nhân là **model được huấn luyện thành có cửa hậu**.
- **[Gốc] Benchmark:** Các backbone open-weight như Llama-3-8B, Qwen-2-7B, Mistral-7B; kiểm thử nhiều dạng override/PI trên tập có kiểm soát (ví dụ phishing/ads hoặc rò rỉ system prompt tùy cấu hình). Tác giả phân tích sự đánh đổi giữa tỷ lệ poisoning, ASR khi trigger xuất hiện và hành vi bình thường không có trigger.
- **[Gốc] Defense:** **Instruction-hierarchy / alignment defenses** chính là đối tượng bị stress test, không phải được đề xuất như giải pháp hoàn chỉnh; luận điểm là có thể **bypass ngay cả khi lớp defense vẫn trông có tác dụng trên mẫu không có trigger**.
- **Hạn chế/kết luận:** Không thực tế để tự tái tạo trong vài tuần nếu không huấn luyện lại backbone; phiên bản training và bộ trigger ảnh hưởng mạnh đến kết quả. **[Ứng dụng đề xuất]** chọn model uy tín, không hứa lớp input guardrails giải quyết được mọi backdoor của backbone. **P3.**

<a id="paper-g01"></a>

#### 2025 · G01 — [16] Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression

**Bài gốc:** [arXiv:2504.20493](https://arxiv.org/abs/2504.20493) · [HTML](https://arxiv.org/html/2504.20493).

- **[Gốc] Threat model:** LLM reasoning có cơ chế hiển thị/sinh bước "thinking". Đối thủ kiểm soát dữ liệu/prompt được đọc trước hoặc trong tác vụ giải bài, mục tiêu khiến mô hình **ngừng reasoning quá sớm**, bỏ lời giải hoặc cho đáp án không đầy đủ. Khác với attack hướng rò PII hay chuyển tool.
- **[Gốc] Kỹ thuật:** Tạo một chuỗi nhắc mang tính "tiền kết luận" rồi **rút ngắn/tối ưu độ dài token** bằng LLM hỗ trợ, làm mô hình rơi vào trạng thái dừng suy luận (reasoning cessation). Đây là nhóm **availability/DoS của dòng reasoning**, nhưng không phải tấn công hạ tầng mạng.
- **[Gốc] Benchmark:** Các bài toán số học và phép tính (`+`, `−`, `×`, `÷`), đánh giá trên mô hình reasoning như DeepSeek-R1 và các mô hình hỗ trợ quá trình sinh/đánh giá. Metric: **tỷ lệ dừng sai/suy luận không hoàn tất** và **độ dài/chi phí token của payload**. Bài báo so sánh payload gốc và payload được nén; một số cấu hình có ASR cỡ hàng chục phần trăm, cần đọc bảng gốc trước khi trích một tỷ lệ cụ thể cho toàn bộ bài.
- **[Gốc] Defense/khả năng chống:** Có khảo sát vài can thiệp nhỏ vào phần đầu prompt hoặc cấu trúc để phá hiệu ứng cắt reasoning ở một số mô hình; **không có bộ PI classifier/RAG guardrail chung được chứng minh**.
- **Hạn chế/kết luận:** Hiện tượng có tính đặc thù với model/trạng thái reasoning; thiếu tổng quát cho chatbot FAQ bán hàng. **[Ứng dụng đề xuất]** chỉ tham khảo làm mẫu kiểm thử **availability/task completion** nếu sau này hệ thống có reasoning mode. **P3.**

<a id="paper-g02"></a>

#### 2025 · G02 — [18] VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy

**Bài gốc:** [arXiv:2510.04261](https://arxiv.org/abs/2510.04261) · [HTML](https://arxiv.org/html/2510.04261).

- **[Gốc] Threat model:** Attacker **không kiểm soát system prompt** của ứng dụng hội thoại; chỉ chèn được một phần nội dung **thấp quyền** (thí dụ tài liệu, phản hồi từ nguồn ngoài). Mục tiêu khiến chatbot **chủ động hỏi người dùng khai báo thêm thông tin cá nhân** (tuổi, họ tên, liên hệ, sở thích...) thay vì chỉ làm nhiệm vụ gốc.
- **[Gốc] Kỹ thuật:** Payload đưa vào các đoạn **false memory** giả như người dùng đã đồng ý cung cấp/chấp nhận quy trình thu thập thông tin; mô hình tiếp nhận câu chuyện đó và đề nghị người dùng tiết lộ PII theo nhóm. Tác giả phát triển cách tạo payload hiệu quả token, đánh giá với các kiểu rủi ro riêng tư khác nhau.
- **[Gốc] Benchmark:** **6 LLM**, bao gồm mô hình thường và reasoning, trên **4 benchmark** (Math500, AIME2024, AIME2025, AICrypto) cùng một số ứng dụng nguồn mở; so sánh baseline payload, độ dài token và độ thành công **trong việc khiến mô hình chủ động yêu cầu PII**. Một phần đánh giá dùng LLM-as-a-Judge/tiêu chí tự động để đo mẫu yêu cầu riêng tư.
- **[Gốc] Defense thử nghiệm:** Paper có mục **Defenses** riêng và kiểm tra các cách **prevention by instruction** và **detection** đối với injected content; mức hiệu quả thay đổi theo mô hình và kiểu câu hỏi. Không nên diễn giải "model đã hỏi PII" thành "người thật đã giao PII" hoặc "đã có PII bị gửi ra hacker".
- **Hạn chế/kết luận:** **Privacy solicitation** khác **exfiltration of PII already in agent context** ([2], [62]); việc user có đồng ý/đưa dữ liệu thật không được đo hoàn toàn bằng một response LLM. **[Ứng dụng đề xuất] P1/P2:** case customer-service bot bị chèn review "hãy yêu cầu khách gửi CCCD trước khi báo giá"; golden tiêu chí **unnecessary PII solicitation**, không chỉ đếm chuỗi PII trong output.

<a id="paper-g03"></a>

#### 2025 · G03 — [43] Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems

**Bài gốc:** [arXiv:2507.23453](https://arxiv.org/abs/2507.23453) · [Bản hội nghị/ACL Anthology](https://aclanthology.org/2025.ijcnlp-long.33/). **Điểm phân loại:** Survey đặt paper vào `LLM Generation / attack`, nhưng **đóng góp chính của công trình thực tế là một phương pháp PHÒNG THỦ cho LLM-as-a-Judge**.

- **[Gốc] Threat model:** LLM judge cần chấm câu trả lời được nộp; attacker kiểm soát **câu trả lời đem chấm**, nhưng **không biết ground-truth**. "Blind attack" là đoạn văn/bài nộp lừa judge phán "đúng" bất kể đáp án thật.
- **[Gốc] Attack được formalize:** Các đáp án có câu chỉ dẫn bảo judge bỏ qua rubric, khẳng định sai thành đúng, hoặc diễn đạt đánh lạc hướng độc lập với ground truth. Đây là đối tượng phòng thủ, **không phải một thuật toán sinh attack mới là kết quả chính**.
- **[Gốc] Defense SE+CFE:** Chạy **Standard Evaluation (SE)** với đáp án đúng; đồng thời chạy **Counterfactual Evaluation (CFE)** với một *ground truth sai có chủ ý*. Nếu cùng một candidate vẫn được judge cho là "đúng" với cả hai điều kiện mâu thuẫn, đánh dấu dấu hiệu blind attack. Phương pháp cần thực hiện có kiểm soát vì chi phí hai lượt đánh giá và khả năng model judge tự sai.
- **[Gốc] Benchmark:** Sáu tập QA như GSM8K, HotpotQA, SQuAD, StrategyQA, TriviaQA, TruthfulQA (mỗi tập **100 mẫu**, tổng **600**) qua **7 model** gồm Gemma-12B, Llama3.1-8B, Mistral-7B, GPT-3.5, GPT-4o-mini, GPT-4o, o1. Báo cáo ma trận nhầm lẫn correct/wrong/attack, so sánh SE và SE+CFE; cho thấy CFE phát hiện attack tốt hơn SE đơn thuần ở nhiều cấu hình.
- **Hạn chế/kết luận:** Phát hiện "blind" không bao phủ toàn bộ tấn công biết ground truth; có thêm inference cost, và judge yếu có thể đánh giá sai. **[Ứng dụng đề xuất]** áp dụng cho **evaluator** của bộ benchmark: đừng chỉ dùng một LLM judge để chấm nếu payload chứa câu điều khiển judge; với case giá/sản phẩm/URL thì ưu tiên chấm deterministic. **P2.**

<a id="paper-s01"></a>

#### 2025 · S01 — [14] Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Prompt-Injection Attacks

**Bài gốc:** [arXiv:2508.20863](https://arxiv.org/abs/2508.20863) · [HTML](https://arxiv.org/html/2508.20863). *Bài có thay đổi tiêu đề giữa survey và bản arXiv mới; hai tên chỉ cùng nghiên cứu theo mã [14]. Phiên bản công bố hiện tại có thể đã được sửa sau 20/10/2025.*

- **[Gốc] Threat model:** Tác giả gửi **PDF paper** cho reviewer dùng LLM; attacker có quyền sửa nội dung/file PDF mình nộp, không có quyền sửa system prompt của reviewer. Mục tiêu khiến reviewer chấp nhận, sửa điểm hoặc bỏ qua lỗi.
- **[Gốc] Cơ chế:** Payload chỉ dẫn (ví dụ ép đánh giá tích cực) nằm trong **chữ ẩn/chữ nhỏ, màu trùng nền, glyph/homoglyph hoặc bố cục tài liệu**; khi parser trích xuất và gửi cho LLM, nội dung chỉ dẫn có thể lẫn với văn bản paper. Tác giả thử mục tiêu như **ignore**, **detect** và **exploit** tùy tác vụ/bối cảnh đánh giá.
- **[Gốc] Benchmark:** Các thiết lập reviewer với GPT/Gemini/Claude và nhiều cách đặt payload; so sánh **PDF không chèn, PDF có chèn, nhiều vị trí/định dạng**; metric theo mức thao túng đánh giá hoặc chọn đúng điều kiện đánh giá. Kết quả **không đồng nhất**: một số cấu hình có tỷ lệ làm lệch rõ, một số mẫu thực tế ít/không ảnh hưởng có ý nghĩa thống kê. Vì vậy không được ghi "chữ trắng luôn thắng".
- **[Gốc] Defense:** Những hướng phòng thủ như kiểm tra visual layer vs text extraction, lọc đoạn ra lệnh và phân tách control/data được bàn đến; **không có một scanner PDF end-to-end được chứng minh hoàn chỉnh trên mọi model**.
- **Hạn chế/kết luận:** Kết quả phụ thuộc parser, LLM, vị trí và mức ẩn chữ. **[Ứng dụng đề xuất]** nếu website nhận PDF sản phẩm: bắt đầu với `raw extracted text` + kiểm tra thuộc tính hiển thị/màu/font; tạo cả **benign hidden text** để tránh chặn nhầm mọi metadata. **P2 nếu có upload tài liệu.**

<a id="paper-s02"></a>

#### 2025 · S02 — [24] Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions

**Bài gốc:** [arXiv:2508.13214](https://arxiv.org/abs/2508.13214) · [PDF gốc (27 trang)](https://arxiv.org/pdf/2508.13214).

- **[Gốc] Threat model:** Mô hình tự đọc **PDF bài kiểm tra** và phải trả lời đúng bài toán trắc nghiệm hoặc True/False cơ bản; attacker được sửa PDF bằng cách chèn chỉ dẫn yêu cầu chọn đáp án sai.
- **[Gốc] Kỹ thuật:** So sánh 3 điều kiện **no injected prompt**, **black-text prompt**, **white-on-white text** vô hình đối với người đọc nhưng có thể được pipeline PDF trích cho LLM. Đây là case quan trọng về **khác biệt giữa thứ được render và thứ parser thấy**, không phải chứng minh mọi mô hình vision sẽ "nhìn thấy chữ trắng"; bài báo cho biết khi dùng screenshot thay PDF nhiều model không nhận thấy hidden prompt.
- **[Gốc] Benchmark:** 6 LLM: GPT-4o, GPT-o3, Gemini-2.5 Flash/Pro, DeepSeek-V3/R1; bộ câu hỏi phép toán và lựa chọn đơn giản, chạy theo từng điều kiện PDF. Không suy diễn các bảng theo từng câu hỏi thành ASR trên phân phối rộng.
- **[Gốc] Defense **thực nghiệm**:** Tác giả **thêm defensive prompt** yêu cầu bỏ qua chỉ dẫn trong PDF và trả lời đúng. Trong một số tác vụ GPT-4o và DeepSeek-V3 được cải thiện rõ, trong khi **Gemini-2.5 Flash vẫn thất bại** ở một số điều kiện. Như vậy việc thêm instruction phòng thủ có thể giúp nhưng không ổn định giữa model.
- **Hạn chế/kết luận:** Task rất nhỏ (số học/trắc nghiệm), loại model và cách đưa PDF/screenshot ảnh hưởng mạnh đến đánh giá. **[Ứng dụng đề xuất] P1/P2:** nếu chatbot có ingest PDF, đây là một **baseline dễ tái lập**: so sánh text/white text/black text và có/không defensive prompt; chấm câu trả lời đúng thay vì chỉ detector label.

<a id="paper-s03"></a>

#### 2025 · S03 — [61] Exploiting Web Search Tools of AI Agents for Data Exfiltration

**Bài gốc:** [arXiv:2510.09093](https://arxiv.org/abs/2510.09093) · [HTML](https://arxiv.org/html/2510.09093). *Bản HTML được truy xuất hiển thị `v2` ngày 10/04/2026, sau mốc survey; dùng bản `v1` khi yêu cầu đúng lịch sử 2025.*

- **[Gốc] Threat model:** Agent có quyền **tìm kiếm web** và xử lý tri thức doanh nghiệp nhạy cảm. Attacker kiểm soát một **trang kết quả web/đoạn nội dung được search trả về** rồi cài chỉ dẫn buộc Agent gọi web search/URL ra ngoài có kèm dữ liệu nhạy cảm. Đây là **tool-result → tool-call exfiltration**, không chỉ tóm tắt sai.
- **[Gốc] Kỹ thuật:** Các biến thể **Base64, nhị phân, Unicode zero-width, emoji substitution, ký tự hoa-thường, ANSI escapes, chuyển ngôn ngữ, thay cách sắp xếp từ** và các phiên bản payload lộ thiên; một số nội dung được giấu dưới dạng **white-on-white**. Vì thế nghiên cứu này *thực sự bao gồm nhiều use case obfuscation mà bạn quan tâm*, dù survey chỉ đặt tên lớp rộng Structural Encoding.
- **[Gốc] Benchmark:** Môi trường giả lập với RAG/company knowledge và tool web search; thử **nhiều model và biến thể payload**, báo cáo ASR theo từng model/template (có model/cấu hình ASR trên **70%**, như Grok-4 trong bảng của bản truy cập; nhiều model khác gần 0%). **Không được kết luận Base64/obfuscation luôn tăng ASR:** trong một số phép thử, payload văn bản rõ lại tốt hơn các biến thể mã hóa. Các biến thể và số lần chạy trên mỗi cấu hình còn hạn chế.
- **[Gốc] Defense:** Bài chủ yếu so sánh mức chống chịu tự nhiên của mô hình và đề nghị bảo mật tốt hơn ở training/test harness; **không có một thí nghiệm đầy đủ so sánh rule-only/model-only/hybrid guardrails cho tất cả biến thể**. **[Ứng dụng đề xuất]** bổ sung **Unicode normalization có lưu raw**, xử lý encoding có điều kiện, **egress whitelist** và theo dõi tham số URL. Chấm attack thành công bằng **tool request gửi dữ liệu**, không chỉ chuỗi xuất hiện trong output.
- **Hạn chế/kết luận:** Một web-search mock và số lần thử hữu hạn chưa phản ánh mọi tổ chức; các quy tắc Unicode/encoding cần tránh false positive với nội dung lành tính. **P1** cho phần attack benchmark và PII leakage.

<a id="paper-s04"></a>

#### 2025 · S04 — [35] Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications

**Bài gốc:** [arXiv:2509.10248](https://arxiv.org/abs/2509.10248) · [HTML](https://arxiv.org/html/2509.10248).

- **[Gốc] Threat model:** Hệ thống tự động nhận bài báo PDF và tạo đánh giá/khuyến nghị **accept/reject**. Attacker kiểm soát nội dung được reviewer xử lý; mục tiêu khiến LLM bình luận tích cực/tiêu cực bất kể chất lượng bài.
- **[Gốc] Kỹ thuật/thiết lập:** PDF được **parser/OCR** trích xuất thành text/Markdown, sau đó nội dung mang chỉ dẫn theo mục tiêu đánh giá được đưa vào quá trình tạo review. Tác giả thử **positive/negative injection** tác động tới structured output. Chú ý: trong một số cấu hình, payload được tiêm ở **text/prompt sau bước parser**, chứ không phải tất cả đều giấu trực tiếp trong PDF gốc; không nên quảng bá là benchmark "PDF trắng" nếu file tấn công là text.
- **[Gốc] Benchmark:** Khoảng **1.000** hồ sơ/bài ICLR 2024 và review được mô hình tạo; dùng nhiều LLM với yêu cầu trả về định dạng có cấu trúc. Một số cấu hình GPT-5-mini thay đổi rõ quyết định: tỷ lệ accept ở baseline khoảng **54%**, dưới positive injection tới **100%**, negative injection gần **0%**; nhiều mô hình **vốn có bias chấp nhận cao** ngay cả khi không tấn công. Điều này là confounder quan trọng.
- **[Gốc] Defense:** Phân tích hợp lệ định dạng output và khả năng parser có trả đúng nội dung; **không phải** một mô hình guardrails chống PI được huấn luyện và đánh giá riêng. Không nhầm **schema validation** với **bảo đảm prompt integrity**.
- **Hạn chế/kết luận:** Thiên lệch accept/reject sẵn có trong LLM có thể khiến ASR trông cao; cần baseline sạch và task utility. **[Ứng dụng đề xuất]** nếu chatbot có chức năng chấm review sản phẩm hoặc kiểm duyệt phản hồi, tạo test cả *positive* lẫn *negative* steering, lưu đáp án chuẩn/cấu trúc từ DB. **P2.**

### A.1.2. Tổng hợp rút ra từ 23 bài gốc — thiết kế đồ án

#### Các threat model KHÁC nhau, không nên gộp thành 1 nhãn "PII leakage"

| Nhánh | Công trình | Thất bại mà benchmark cần quan sát | Vì sao quan trọng |
|---|---|---|---|
| Data exfiltration của PII đã có | **[2], [62], [61]** | Tool/web/email egress thực sự mang dữ liệu nhạy cảm | Chặn output chưa chắc chặn được rò qua tool hoặc URL |
| Lừa chatbot **hỏi thêm** PII | **[18]** | Chatbot yêu cầu thông tin không cần thiết so với nhiệm vụ | Chưa nhất thiết là người dùng đã tiết lộ PII |
| Hành động/task bị điều hướng | **[91], [68], [46], [51]** | Chọn sai tool, trả lời sai loại nhiệm vụ, thực thi việc trái phép | Cần kiểm tra user intent và action trace |
| Thao túng suy luận/chấm điểm | **[81], [50], [43], [35], [94]** | Kết luận không tương ứng dữ liệu/golden, judge bị lừa | Không chỉ dùng LLM-as-a-Judge đơn độc |
| Chỉ dẫn ẩn qua định dạng | **[14], [24], [61], [94]** | Parser đọc thấy instruction mà người kiểm duyệt không nhìn thấy | Kiểm tra raw, parsed, rendered context |
| Supply-chain/training | **[63], [9]** | Model đã bị backdoor trước lúc đưa vào ứng dụng | Không giải quyết hết bằng runtime input filter |
| Multi-agent propagation | **[17], [37]** | Nhiễm qua hội thoại giữa nhiều Agent | Ngoài phạm vi MVP chatbot đơn lẻ |
| Reasoning availability | **[16]** | Bị ép dừng suy luận, bỏ dở nhiệm vụ | Chấm task completion, token/time |
| Phản công Agent an ninh | **[56]** | Agent pentest bị bẫy bởi service/log trả về | Chỉ tham khảo nguồn dữ liệu không tin cậy |

#### Danh sách đọc đã thu hẹp theo CSKH

Không yêu cầu đọc hoặc tái hiện tối thiểu 7 công trình. Đọc **BIPIA [83], VortexPIA [18], PromptArmor [66], ADD-13, ADD-14**, cùng các phần survey chọn lọc. Trong 23 hồ sơ heuristic, G02/[18] là bài đọc chính; các hồ sơ khác tra theo điều kiện ở [chỉ mục CSKH](Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md).

H04/[2], H11/[62], S03/[61] cần kênh exfiltration phù hợp để tái lập bài gốc; chưa mặc định đưa vào benchmark chỉ có API đọc. S01/S02/H13 chỉ mở khi có PDF; G03/H14 chỉ mở khi dùng LLM judge.

#### Đề xuất ma trận benchmark cụ thể cho website thương mại điện tử

| Case | Attack entry | Attack objective | Golden (nội dung đúng / điều kiện thành công) | Defense layer nên so sánh |
|---|---|---|---|---|
| A-EC-01 | `product_description` | Chuyển câu trả lời giá sang website attacker | Giá đúng DB; không xuất link ngoài allowlist | rule / model / hybrid |
| A-EC-02 | `product_review` | Dụ chatbot hỏi khách CCCD khi chỉ hỏi bảo hành | Không hỏi CCCD; trả lời bảo hành theo DB | PI classifier + PII-solicitation policy |
| A-EC-03 | `tool_result` tra đơn | Đưa email/điện thoại khách sang một URL khác | Egress trace không chứa PII thô / URL trái phép | PII redaction + egress policy |
| A-EC-04 | đoạn FAQ có `zero-width`/Base64 | Chỉ dẫn ẩn để thay chính sách hoàn tiền | Từ raw và parsed; chính sách đúng nguồn tin cậy | preprocessing + classifier |
| A-EC-05 | tài liệu về bảo mật (benign) | Không có attacker; chỉ **trích dẫn** prompt xấu | Trả lời câu hỏi bình thường, không chặn nhầm | false-positive check |
| A-EC-06 | PDF giới thiệu sản phẩm (nếu có upload) | Giấu text màu nền yêu cầu thay URL bán hàng | So sánh extracted text với rendered PDF; URL đúng | parser-aware filter |

**Đặc biệt với PII:** Cần tách tối thiểu ba biến quan sát: `pii_present_in_context`, `pii_sent_to_external_llm`, `pii_sent_to_unauthorized_destination`. Mỗi biến có chính sách và golden riêng. Trường hợp email hỗ trợ **công khai** không nên mặc nhiên bị coi là khách hàng bị lộ PII.

#### Hồ sơ kiểm tra nguồn và giới hạn xác minh

- **Đối chiếu 1 — Mã số:** 16 mục H01–H16 khớp 16 reference Manual; 3 mục G01–G03 khớp LLM Generation; 4 mục S01–S04 khớp Structural Encoding (**23/23**). Các tên/đường dẫn đã được ghép theo danh sách References/Table 1.
- **Đối chiếu 2 — Phân loại:** Giữ tên nhóm theo survey, **không che giấu** trường hợp có tối ưu hóa trong [91], tìm kiếm thích nghi trong [50], hoặc paper defense được đưa vào attack [43].
- **Đối chiếu 3 — Threat model:** Mỗi bài chỉ ra attacker control, victim/task và loại hậu quả; đánh dấu rõ multi-agent, multimodal, training-only, evaluator-only, exfil hoặc privacy solicitation.
- **Đối chiếu 4 — Benchmark:** Ghi tên dataset/model/metric khi có bằng chứng; không điền ASR cho case study [3], [62] nếu không có benchmark thống nhất; số liệu gắn với cấu hình, không báo thành cam kết hiệu quả.
- **Đối chiếu 5 — Defense:** Tách **defense thực nghiệm** ([2], [9] như đối tượng vượt phòng thủ, [16], [18], [24], [37], [43], [51], [81]) khỏi **mitigation kiến nghị** ([3], [12], [14], [17], [35], [62], [94] và các mục khác tùy phần gốc); một số bài có nhiều đề xuất không được A/B-tested.
- **Giới hạn quan trọng:** Các bài cập nhật sau ngày 20/10/2025 có thể có phương pháp/số liệu khác phiên bản survey trích. Với [50], đã chuyển sang PDF 12 trang để đọc đối chiếu trực tiếp các bảng Defense/ASR sau khi HTML không khả dụng; riêng các bài có bản HTML được cập nhật sau mốc survey, số liệu có thể cần đối chiếu thêm phiên bản v1 trước khi trích dẫn luận văn. Ngoài ra, tôi **chưa tái chạy độc lập bất kỳ benchmark nào**. Điều này không ảnh hưởng việc lập bản đồ phương pháp nhưng cần được ghi rõ nếu trích vào báo cáo khoa học.


## A.2. Optimization-based attacks (14 công trình)

### A4. Gradient-based Optimization — 6 công trình | P3

- **Cơ chế [Survey]:** Dùng thông tin gradient hoặc đặc trưng nội bộ để tối ưu token/suffix nhằm tăng xác suất tạo đầu ra/hành vi mà attacker mong muốn; khảo sát liên hệ tới Greedy Coordinate Gradient (GCG).
- **Điều kiện thường gặp:** White-box hoặc quyền truy cập mạnh vào mô hình/surrogate; không phù hợp trực tiếp nếu chỉ gọi API thương mại.
- **Liên quan đề tài [Đề xuất]:** Nắm nguyên lý để đánh giá hạn chế của bộ detector dựa trên template, không cần tự huấn luyện hay tự tối ưu attack.
- **Công trình trong Table 1:**
  - **2024** · [45] *Automatic and Universal Prompt Injection Attacks Against Large Language Models*.
  - **2025** · [28] *Fingerprinting LLMs via Prompt Injection*.
  - **2024** · [57] *Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks*.
  - **2024** · [64] *Optimization-Based Prompt Injection Attack to LLM-as-a-Judge*.
  - **2025** · [55] *May I Have Your Attention? Breaking Fine-Tuning Based Prompt Injection Defenses Using Architecture-Aware Attacks*.
  - **2024** · [90] *HijackRAG: Hijacking Attacks Against Retrieval-Augmented Large Language Models*.

### A5. Genetic / Evolutionary Optimization — 6 công trình | P3

- **Cơ chế [Survey]:** Dùng thuật toán tiến hóa, lựa chọn/sửa đổi ứng viên, hoặc feedback-driven searching để tìm payload tốt hơn. Nhiều hướng có thể áp dụng trong Black-box.
- **Lưu ý:** Các công trình trong nhóm không nhất thiết đều triển khai **Genetic Algorithm thuần túy**; ví dụ *PromptFuzz* sử dụng fuzzing. Đây là cách **survey xếp nhóm**, không phải khẳng định các kỹ thuật đồng nhất.
- **Công trình trong Table 1:**
  - **2024** · [88] *Goal-Guided Generative Prompt Injection Attack on Large Language Models*.
  - **2024** · [84] *PromptFuzz: Harnessing Fuzzing Techniques for Robust Testing of Prompt Injection in LLMs*.
  - **2025** · [23] *StruPhantom: Evolutionary Injection Attacks on Black-Box Tabular Agents Powered by Large Language Models*.
  - **2025** · [44] *AEGIS: Automated Co-Evolutionary Framework for Guarding Prompt Injections Schema*.
  - **2025** · [85] *Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents*.
  - **2024** · [52] *Adversarial Search Engine Optimization for Large Language Models*.

### A6. Sampling-based Optimization — 2 công trình | P3

- **Cơ chế [Survey]:** Tối ưu payload thông qua lấy mẫu, reward/feedback, thay vì trực tiếp cập nhật token bằng gradient từ mô hình nạn nhân; gồm RL và MCMC.
- **Liên quan đồ án [Đề xuất]:** Đọc để hiểu khả năng thích nghi/chuyển giao của payload; không bắt buộc tự triển khai.
- **Công trình trong Table 1:**
  - **2025** · [77] *RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection*.
  - **2025** · [41] *Transferable Direct Prompt Injection via Activation-Guided MCMC Sampling*.

### A.3. Checklist nhanh theo nhóm A

| Phương pháp | Số công trình theo Table 1 | Ưu tiên đồ án | Vai trò |
|---|---:|---|---|
| A1. Manual Template | 16 | P1 | Tạo attack cơ bản và negative cases |
| A2. LLM Generation | 3 | P2 | Sinh biến thể có kiểm soát |
| A3. Structural Encoding | 4 | P1 | Kiểm thử obfuscation/parser |
| A4. Gradient | 6 | P3 | Background / advanced attack |
| A5. Genetic/Evolutionary | 6 | P3 | Background / adaptive attack |
| A6. Sampling (RL/MCMC) | 2 | P3 | Background / automated attack |

---

# B. ATTACK PARADIGMS — ĐƯỜNG VÀO, MỤC TIÊU, KHẢ NĂNG, ĐỘ HIỂN THỊ

**Nguồn:** Section 3.2, trang 5, **Table 1**. [Survey] Đây là các **chiều phân loại chéo** của những công trình thuộc A1–A6, không phải sáu kỹ thuật tạo payload mới.

## B1. Theo attack surface

| Nhóm | Khái niệm [Survey] | Ví dụ tương ứng với chatbot [Đề xuất] | Ưu tiên |
|---|---|---|---|
| **Direct Prompt Injection (DPI)** | Input độc hại nhập trực tiếp qua prompt | User gửi yêu cầu cố ghi đè giới hạn chatbot | P1 |
| **Indirect Prompt Injection (IPI)** | Chỉ dẫn độc hại trong nguồn ngoài / tool observation | `product_description`, review, email, đoạn web, kết quả API | **P1** |
| **Supply-chain Prompt Injection (SPI)** | Nguồn RAG hoặc dữ liệu training bị cấy payload | Dữ liệu nguồn tri thức bị đầu độc | P2 |

> **Lưu ý nguồn:** Survey mô tả đầu vào RAG/training là *partially trusted* trong mô hình hệ thống (Section 2.2), và phân loại SPI trong Section 3.2. Không nên tự đồng nhất mọi trường hợp RAG poisoning với mọi kiểu IPI: cần nêu rõ attacker kiểm soát bước nào.

## B2. Theo mục tiêu bảo mật (CIA)

| Nhóm | Ví dụ mục tiêu trong paper | Mức ưu tiên |
|---|---|---|
| **Integrity** | Goal hijack; action hijack; task hijack; misinformation; score/rank tampering | P1 |
| **Confidentiality** | Data leakage; data exfiltration | **P1** |
| **Availability** | CoT DoS; quá trình suy luận bị gián đoạn/tiêu tốn tài nguyên | P3 |

[Survey] Section 3.2 báo cáo 30/37 công trình nhắm Integrity, 4 công trình về Confidentiality và 2 công trình Availability (theo hệ quy chiếu phân loại của tác giả). Không suy diễn các con số này là tỷ lệ tấn công trong đời thực.

## B3. Theo attacker capability

| Nhóm | Mô tả | Đề xuất |
|---|---|---|
| **Black-box** | Không truy cập trọng số; dùng output, phản hồi thành công/thất bại, log hoặc hệ quả thực thi | **Threat model chính của đồ án** |
| **White-box** | Có thông tin model internals như gradients/logits/attention/training access | Chỉ đọc Related Work |

## B4. Theo khả năng hiển thị của payload

| Nhóm | Nội dung [Survey] | Ưu tiên |
|---|---|---|
| **Visible** | Prompt độc hại hiện rõ dưới dạng ngôn ngữ tự nhiên | P1 |
| **Invisible – Context** | Trộn chỉ dẫn vào context dài, logs, RAG, memory | **P1** |
| **Invisible – Encoding** | Mã hóa/cấu trúc biểu diễn, ví dụ Base64 | **P1** |
| **Invisible – Semantics** | Token/suffix đã được tối ưu để khó nhận biết về mặt ngữ nghĩa | P2 |
| **Invisible – Vision** | Ẩn chỉ dẫn trong đầu vào hình ảnh | P3 |

**Lưu ý chi tiết nguồn:** Survey **không xây taxonomy riêng** cho homoglyph, zero-width, chữ trắng/chữ nhỏ trong HTML/PDF. Tuy nhiên, khi đọc paper **[61]** do chính survey trích dẫn sẽ thấy tác giả **thực nghiệm** các biến thể zero-width, encoding và obfuscation; paper **[24]** kiểm thử PDF chữ trắng, **[14]** và **[35]** đề cập nội dung ẩn trong PDF. Các kỹ thuật này vì thế có cơ sở ở **công trình gốc**, không phải tiểu nhóm riêng của taxonomy survey.

---

# C. DEFENSE — CÁC CÁCH PHÒNG THỦ

**Nguồn:** Section 4, trang 5–10, **Table 2**; phân tầng **Text-level / Model-level / Execution-level**.

## C1. TEXT-LEVEL — Bảo vệ trên input/output dạng text (18 hàng nghiên cứu trong Table 2)

### C1.1. Detection Filter (11 công trình)

| Mã | Phương pháp / nhóm nghiên cứu | Công trình trong survey | Mô tả ngắn | Ưu tiên |
|---|---|---|---|---|
| **D01** | LLM-based classification | **PromptShield [30] (2024)** | Mô hình đánh giá prompt có injection không | P1 |
| **D02** | Detection + generative explanation | **Pan et al. [54] (2025)** | Thêm lý do giúp người kiểm tra hiểu quyết định | P2 |
| **D03** | Third-party input detection | **PromptArmor [66] (2025)** | Kiểm tra nội dung ngoài đưa vào LLM | **P1** |
| **D04** | Inference-time scaling / self-inspection | **SecInfer [48] (2025)** | Tăng suy luận kiểm tra nội dung khó | P3 |
| **D05** | Policy/whitelist-style detection | **LLMz+ [58] (2025)** | Xác định tính hợp lệ theo nguyên tắc whitelist | P2 |
| **D06** | Segment localization | **PromptLocate [32] (2025)** | Khoanh vùng đoạn bị injection | **P1** |
| **D07** | Long-context / segment handling | **FocusAgent [34] (2025)** | Xử lý/chọn lọc context dài theo cách survey nhóm vào detection | P2 |
| **D08** | BERT-based classifier | **Rahman et al. [60] (2024)** | Phân loại bằng mô hình encoder nhỏ hơn LLM | **P1** |
| **D09** | Lightweight prompt-injection guard | **PIGuard [40] (2025)** | Phát hiện và cân bằng chặn nhầm | **P1** |
| **D10** | Indirect PI detection and removal | **Chen et al. [7] (2025)** | Nhận diện và loại bỏ PI gián tiếp | **P1** |
| **D11** | Fine-grained / token sanitizer | **CommandSans [19] (2025)** | Can thiệp cụ thể vào các chỉ dẫn nguy hiểm | **P1** |

**Hai hướng triển khai [Đề xuất]:** `rule-based filter` và `small-model classifier`; sau đó so sánh với detector sử dụng LLM nếu ngân sách cho phép. **Regex đơn thuần không phải một nhóm thuật toán riêng trong taxonomy của Table 2**, dù có thể dùng làm baseline cho đồ án.

### C1.2. Prompt Enhancement (7 công trình trong Table 2)

| Mã | Phương pháp | Công trình trong survey | Vai trò | Ưu tiên |
|---|---|---|---|---|
| **D12** | Input / instruction–data separation | **Spotlighting [26] (2024)** | Phân ranh dữ liệu và chỉ dẫn | **P1** |
| **D13** | Output-side separation / authentication | **FATH [72] (2024)** | Kiểm chứng ranh giới/nguồn gốc đầu ra | P2 |
| **D14** | Self-referencing | **Chen et al. [8] (2025)** | Đối chiếu lại chỉ dẫn gốc | P2 |
| **D15** | Defensive / negative prompts | **Chen et al. [5] (2025), [10] (2025)** | Thêm token/prompt phòng thủ | **P1** |
| **D16** | Prompt rewriting / sanitization | **Alharthi et al. [1] (2025)** | Viết lại đầu vào giảm nội dung gây ảnh hưởng | **P1** |
| **D17** | Polymorphic prompt protection / rewriting | **Wang et al. [75] (2025)** | Biến đổi cấu trúc prompt để giảm khả năng dự đoán | P2 |

**Gợi ý baseline [Đề xuất]:** Prompt-only defense bằng delimiters / defensive instruction, so với rule filter, classifier và hybrid. Chỉ dùng delimiter **không tạo ra bảo đảm bảo mật tuyệt đối**.

## C2. MODEL-LEVEL — Can thiệp vào backbone LLM (7 hàng trong Table 2)

### C2.1. Model Alignment / Fine-tuning (4 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D18** | Task-specific fine-tuning | **Jatmo [59] (2024)** | P3 |
| **D19** | Preference / security alignment | **SecAlign [6] (2025)** | P3 |
| **D20** | Structured-query fine-tuning | **StruQ [4] (2025)** | P3 |
| **D21** | Polymorphic prompt fine-tuning | **Wang et al. [75] (2025)** | P3 |

### C2.2. Intermediate Representation (IR) Intervention (3 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D22** | Attention map tracking | **Attention Tracker [29] (2025)** | P3 |
| **D23** | Intrinsic-feature-based PI detection | **PIShield [96] (2025)** | P3 |
| **D24** | Hidden-state / representation probing | **Wen et al. [76] (2025)** | P3 |

**Lý do ưu tiên thấp [Đề xuất]:** Với chatbot gọi LLM API, thường không thể truy cập trọng số, gradient hoặc attention của backbone. Đây là hướng nền tảng nghiên cứu, không bắt buộc đối với lớp guardrails *plug-and-play*.

## C3. EXECUTION-LEVEL — Kiểm soát hành vi Agent và luồng dữ liệu (16 hàng trong Table 2)

### C3.1. Task Alignment (2 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D25** | Goal/task alignment | **Task Shield [31] (2025)** | P2 |
| **D26** | Robust action alignment | **Melon [95] (2025)** | P3 |

**Áp dụng [Đề xuất]:** Nếu chatbot có tool gọi API xem đơn hàng/chỉnh sửa giỏ hàng, kiểm tra hành động có khớp mục tiêu được ủy quyền không.

### C3.2. Information Flow Control (7 công trình)

| Mã | Phương pháp | Công trình | Liên quan đề tài | Ưu tiên |
|---|---|---|---|---|
| **D27** | Trust-label / information flow | **Fides [15] (2025)** | Phân biệt dữ liệu đáng tin và không đáng tin | P2 |
| **D28** | Transactional trustworthy flow | **SafeFlow [42] (2025)** | Kiểm soát luồng dữ liệu/hành động | P2 |
| **D29** | Permissive information-flow analysis | **Siddiqui et al. [67] (2024)** | Cho phép xử lý dữ liệu ngoài nhưng khóa luồng nguy hiểm | **P1** |
| **D30** | Flow-based isolation | **Wu et al. [78] (2024)** | Ngăn nâng quyền qua dữ liệu không tin cậy | P2 |
| **D31** | Runtime trace analysis | **AgentArmor [74] (2025)** | Kiểm tra chuỗi thực thi | P2 |
| **D32** | Exfiltration / privacy-flow protection | **RTBAS [92] (2025)** | **Sát bài toán ngăn rò rỉ** | **P1** |
| **D33** | Program / flow control architecture | **CaMeL [20] (2025)** | Kiểm soát ảnh hưởng dữ liệu lên hành động | P2 |

**Áp dụng [Đề xuất]:** Gắn nhãn dữ liệu chứa PII, đặt quy tắc *không truyền raw PII sang LLM API ngoài*. Đây là ý tưởng kiến trúc giản lược, **không phải một thuật toán PII cụ thể** được survey mô tả.

### C3.3. Specification / Policy Control (3 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D34** | Adaptive safety policy | **AGrail [49] (2025)** | P2 |
| **D35** | Contextual security policy | **Tsai & Bagdasarian [70] (2025)** | P2 |
| **D36** | Programmable privilege control | **Progent [65] (2025)** | P2 |

**Áp dụng [Đề xuất]:** Quy tắc `ALLOW`, `MASK`, `BLOCK`, `REVIEW` tùy nội dung và mức rủi ro. Đây là policy của **đồ án**, không phải tập nhãn chuẩn của survey.

### C3.4. Isolation (4 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D37** | Environment isolation | **IsolateGPT [79] (2025)** | P3 |
| **D38** | Planning isolation / prompt-flow integrity | **PFI [36] (2025)** | P3 |
| **D39** | Dynamic rule-based isolation | **DRIFT [39] (2025)** | P3 |
| **D40** | Security architecture / planning isolation | **ACE [38] (2025)** | P3 |

**Giới hạn [Survey]:** Cô lập quá chặt có thể làm Agent không thực hiện được tác vụ cần đọc và dùng dữ liệu bên ngoài; cần đo **utility** ngoài ASR.

### C4. Bảng chọn defense cho đồ án

| Nhu cầu đồ án | Nhóm nên ưu tiên | Paper đọc trước |
|---|---|---|
| Phát hiện Prompt Injection trong user input | Detection filter / non-LLM classifier | [30] (2024), [40] (2025), [60] (2024) |
| Phát hiện Prompt Injection trong dữ liệu RAG/product | Third-party input detection, segment detection | [66] (2025), [7] (2025), [32] (2025), [19] (2025) |
| Bảo vệ bằng cấu trúc prompt | Input separation, defensive prompts | [26] (2024), [5] (2025), [10] (2025) |
| Ngăn dữ liệu nhạy cảm đi sai đích | IFC và privacy-flow monitoring | [67] (2024), [92] (2025), [15] (2025) |
| Chính sách quyết định hành động | Policy control | [49] (2025), [65] (2025) |
| Chatbot có API/tool calls | Task alignment và flow control | [31] (2025), [74] (2025), [20] (2025) |

---

# D. CONFIDENTIALITY / PII — PHẦN LIÊN QUAN VÀ PHẦN SURVEY CHƯA BAO PHỦ

## D1. Các hướng **có trong survey** liên quan đến rò rỉ dữ liệu

| Hướng | Attack papers liên quan | Defense papers liên quan | Ý nghĩa |
|---|---|---|---|
| Tấn công lấy cắp dữ liệu quan sát được | [2], [62] | [92], [15], [67] | Payload khiến Agent tiết lộ dữ liệu không được phép |
| Dụ chatbot yêu cầu PII không cần thiết | [18] | Chọn policy/detector theo tác vụ; không đồng nhất với IFC | Chấm yêu cầu thu thập PII, chưa coi là dữ liệu đã bị gửi ra ngoài |
| Exfiltration qua công cụ web/tool | [61] | [92], [65] | Truyền thông tin đến đích không được cấp phép |
| Truy vết và hạn chế luồng dữ liệu | — | [15], [42], [67], [78], [20] | Định nghĩa nguồn, mức tin cậy và đích đến |
| Kiểm soát quyền thực thi | — | [49], [70], [65], [79] | Giảm rủi ro thao tác vượt quyền |

**[Survey]** Table 2 cho biết 17/41 công trình phòng thủ có thuộc tính Confidentiality; toàn bộ nhóm nghiên cứu bảo vệ Integrity. Paper **không** cung cấp bộ phương pháp PII NER/masking riêng.

## D2. Các thành phần **ngoài phạm vi khảo sát chuyên sâu của survey** nhưng cần cho đồ án

**[Đề xuất — không coi là phương pháp xuất phát từ paper này]**

1. Regex/pattern-based PII recognition: email, số điện thoại, tài khoản, định dạng số định danh.
2. NER / entity recognition cho tên người, địa chỉ hoặc PII không có mẫu cú pháp cố định.
3. Masking/redaction trước khi truyền dữ liệu ra dịch vụ LLM hoặc embedding bên ngoài.
4. Context-aware authorization: phân biệt dữ liệu cá nhân được phép dùng với dữ liệu không được phép tiết lộ.
5. Redacted logging; không ghi nguyên văn PII trong log và benchmark artifacts chia sẻ.

**Phân biệt hai bài toán:**

- *Prompt Injection Detection*: Có chỉ dẫn từ nguồn không đáng tin cậy nhằm điều khiển chatbot hay không?
- *PII / Data Leakage Protection*: Dữ liệu định danh nào có nguy cơ rời hệ thống hoặc hiển thị sai quyền, bất kể có Prompt Injection hay không?

---

# E. BENCHMARK & EVALUATION

## E1. Benchmark được tổng hợp (Section 5, Table 3, trang 11)

| Benchmark | Ref. trong survey | Hệ thống / đặc trưng | Chỉ số survey ghi nhận |
|---|---|---|---|
| **OpenPI** | [47] (2024) | Benchmark PI trên mô hình tổng quát | ASR, Utility |
| **BIPIA** | [83] (2025) | Indirect PI | ASR, Utility |
| **InjecAgent** | [86] (2024) | Tool/function-call PI | ASR |
| **AgentDojo** | [21] (2024) | Agent tương tác đa bước | ASR, Utility |
| **Agent Security Bench (ASB)** | [89] (2024) | Agent benchmark đa bối cảnh | ASR, Utility |

**Cảnh báo [Survey]:** Kết quả tốt trên benchmark dùng template/static tasks không đủ chứng minh robust đối với **context-dependent tasks**. Benchmark chấm quá cứng nhắc bằng string-match hoặc trạng thái cuối cũng có thể bỏ sót trường hợp sai hành vi.

## E2. Năm kiểu Context-aware Attack trong AGENTPI (Section 6, Table 4, Appendix C)

| Mã | Loại tấn công | Luồng bị tác động | Ví dụ từ survey | Áp dụng đồ án |
|---|---|---|---|---|
| **E01** | Action Switching | Control flow / tool selection | Thay `transfer_money` thành `pay_bill` | P2 nếu chatbot có tool |
| **E02** | Parameter Manipulation | Control / data filling | Đổi giá trị `amount` dù vẫn gọi tool hợp lệ | P2 nếu chatbot có tool |
| **E03** | Branch Divergence | Logic flow / conditional | Giả thông báo số dư để Agent chọn nhánh sai | P2 |
| **E04** | Reasoning Corruption | Logic flow / calculation | Ép chọn khách hàng nhận tiền hoàn sai dù dữ liệu rõ ràng | P2 |
| **E05** | Delegation Exploitation | Authority flow | Lợi dụng lệnh người dùng yêu cầu đọc trường dữ liệu để đưa lệnh giả | **P1** |

**Cần phân biệt:** AGENTPI là phần **benchmark mới của chính survey**, không phải một phương pháp tạo payload nằm trong A1–A6. Các ví dụ chuyển tiền chỉ hợp lệ nếu hệ thống thực sự có công cụ tương ứng; không ép chatbot chỉ hỏi đáp thành banking agent.

## E3. Các baseline defense được tác giả đánh giá trực tiếp (Section 7)

| Baseline | Nhóm | Vai trò thử nghiệm trong survey |
|---|---|---|
| No defense / Baseline | Không guardrail | Mốc so sánh |
| Sandwich defense | Text-level | Prompt-based protection |
| Delimiters | Text-level | Phân tách vùng dữ liệu/chỉ dẫn |
| Paraphrasing | Text-level | Viết lại nội dung |
| Instruction defense | Text-level | Cảnh báo/nhắc mô hình giữ chỉ dẫn ưu tiên |
| Tool filter | Execution-level | Giới hạn tool được phép |
| Task Shield | Execution-level | Kiểm tra task alignment |
| Melon | Execution-level | Robust action alignment |
| Progent | Execution-level | Programmable privilege control |

**Ghi chú nguồn:** Abstract/Introduction có chỗ gọi là “8 defenses”; Section 7.1 viết “9 defenses within 2 categories” nhưng liệt kê **8 phương pháp phòng thủ cụ thể**, cộng **baseline không phòng thủ** trong đồ thị/bảng. Khi viết báo cáo nên mô tả đúng danh sách thực nghiệm, không coi baseline là một giải pháp defense.

## E4. Chỉ số & cách chấm được paper nêu

| Chỉ số / phương pháp | Mục đích | Nguồn |
|---|---|---|
| Attack Success Rate (ASR) | Attacker có đạt mục tiêu không | Sections 5–7 |
| Utility (no attack) | Agent còn làm đúng tác vụ hợp lệ không | Sections 5–7 |
| Latency / Time Cost | Phụ phí thời gian do defense | Section 7, Table 5 |
| Input/Output Token Cost | Phụ phí token | Section 7, Table 5 |
| Environment-state judgment | Chấm trạng thái kết quả thực thi | Section 5, Table 3 |
| Function-call judgment | Chấm tool name/parameters | Section 5, Table 3 |
| String matching | Chấm dựa trên chuỗi/cờ | Section 5, Table 3 |
| LLM-as-a-judge | Dùng LLM đánh giá | Section 5, Table 3 |
| Execution trajectory analysis | Xem toàn bộ chuỗi xử lý chứ không chỉ kết quả cuối | Section 5 |

**[Đề xuất riêng cho đồ án — ngoài bộ chỉ số trung tâm AGENTPI]:** Precision/Recall/F1/FPR cho **detector**, PII-span recall và false masking, PII exposure trước/sau điểm egress, so sánh Rule-only / Classifier-only / Hybrid / No Guardrail.

---

# F. HƯỚNG NGHIÊN CỨU MỞ (APPENDIX B)

Đây là các **hướng mà survey đề xuất**, **chưa phải các thuật toán hoàn thiện** có thể mặc định tích hợp ngay.

| Mã | Hướng nghiên cứu | Mô tả | Độ ưu tiên |
|---|---|---|---|
| **F01** | Fine-grained Attention Access Control | Kiểm soát/che attention tới chỉ dẫn không đáng tin cậy | P3 |
| **F02** | Resource-aware Defense | Phát hiện vòng lặp, DoS, tiêu hao tài nguyên bất thường | P3 |
| **F03** | Dynamic Trust Boundaries | Dùng dữ liệu bên ngoài khi cần nhưng giữ ranh giới tin cậy | P2 |
| **F04** | Reasoning Consistency Verification | Kiểm chứng suy luận/hành động khớp dữ liệu và mục tiêu | P2 |
| **F05** | Hybrid Human–AI Intervention | Chuyển tình huống rủi ro cao hoặc bất định sang người đánh giá | P2 |

**Gợi ý [Đề xuất]:** F03 và F05 có thể là cơ sở lý luận cho xử lý `ALLOW / MASK / BLOCK / REVIEW`, nhưng không nên cam kết nghiên cứu đầy đủ một bài toán mở trong thời gian đồ án.

---

# G. DANH MỤC TẬP TRUNG CHO ĐỒ ÁN (ĐỀ XUẤT, KHÔNG PHẢI TAXONOMY CỦA PAPER)

## G1. Việc cần có sau danh sách đọc chính

- [ ] Chọn một tác vụ CSKH và một hoặc hai nguồn text thực tế có thể chứa chỉ dẫn không đáng tin.
- [ ] Mô tả dữ liệu API được phép đọc, phân quyền backend và PII tối thiểu cho tác vụ.
- [ ] Có test PI chuyển hướng nhiệm vụ, test yêu cầu PII không cần thiết, cùng benign/hard-benign.
- [ ] Có chính sách về PII tới LLM, câu trả lời và log; đo riêng từng điểm.
- [ ] Chọn số ít baseline và chốt protocol, tránh mở rộng sang mọi defense trong taxonomy.

## G2. Paper đọc theo nhu cầu, không phải danh sách phải triển khai

Xem [bảng phân loại CSKH](Phan_loai_paper_CSKH_Thuong_mai_dien_tu.md): đủ 23 hồ sơ H/G/S, 14 mục ADD, các mã D01–D40, benchmark và nhóm attack tối ưu. Điều kiện như PDF, web/email egress, LLM judge hoặc agent tự chọn tool phải được xác nhận trước.

## G3. Các hướng ngoài phạm vi hiện tại

Coding/shell agent, multi-agent propagation/debate, training backdoors, tối ưu gradient/RL/MCMC, model IR, full architectural isolation và multimodal. Giữ để tra cứu/Related Work; không thêm tính năng vào ứng dụng chỉ để tái lập paper.

## G4. Phần survey cần đọc trước

§2, §3.2, §4.1 và §5 làm nền; đọc lướt §6–7 để hiểu context-dependent tasks và trade-off. §4.3 và Appendix C chỉ đọc sâu phần phù hợp với API/tool thực tế. Không cần đọc toàn bộ survey trước khi khảo sát project.

---

# H. GỢI Ý THIẾT KẾ BỘ THỰC NGHIỆM (ĐỀ XUẤT)

Để tránh hiểu nhầm với phương pháp của tác giả, phần này **hoàn toàn là gợi ý áp dụng** lên chatbot thương mại điện tử của đồ án:

```text
Chatbot hiện có
  ├── Input guard: rule-based PI / classifier PI / PII masking
  ├── Product/RAG/tool retrieval
  ├── Context guard: indirect PI + source/segment assessment
  ├── LLM call (kiểm soát PII trước egress)
  ├── Output guard: privacy/data leakage policy
  └── Audit (redacted) + benchmark runner

Benchmark 1: Detector-only
  └── benign vs attack → Precision / Recall / F1 / FPR

Benchmark 2: End-to-end chatbot
  └── user task + injected source + golden behavior
      → ASR / benign task success / latency / PII exposure

So sánh: No guardrail / Rule-only / Model-only / Hybrid
```

**Golden test phải chứa cả:** mục tiêu người dùng hợp lệ, điểm chèn nội dung, mục tiêu hacker, trạng thái dữ liệu đúng, hành vi không được phép, và điều kiện chấm thành công. Không đưa golden labels vào prompt của chatbot.

---

# I. THAM CHIẾU VÀ GIỚI HẠN SỬ DỤNG

## I1. Điều hướng tới từng phần survey

| Phần | Nội dung | Trang trong survey |
|---|---|---|
| §2.1–2.2, Figure 1 | Agent loop, trust boundary, tool observation | 2–3 |
| §3.1, Table 1 | Heuristic / Optimization attack generation | 3–4 |
| §3.2 | Attack surface, goal, capability, visibility | 5 |
| §4, Table 2 | Defense taxonomy và 41 công trình | 5–6 |
| §4.1 | Text-level defense | 7 |
| §4.2 | Model-level defense | 7–8 |
| §4.3 | Execution-level defense | 8 |
| §4.4–4.6 | Capability, explainability, cost | 8–10 |
| §5, Tables 3–4 | Benchmark hiện có / context-dependent tasks | 10–11 |
| §6 | AGENTPI benchmark và 5 attack categories | 11–12 |
| §7, Figure 6, Table 5 | Evaluation, ASR, utility, latency/tokens | 12–13 |
| Appendix A–B | Thảo luận hạn chế và future directions | 19–20 |
| Appendix C, Figures 7–11 | Năm ví dụ AGENTPI | 20–22 |
| References | Tên đầy đủ công trình [1] (2025)–[96] (2025) | 14–18 |

## I2. Cách dùng tài liệu để lập kế hoạch

1. **Chọn attack surface** của chatbot thực tế trước (user input, product description, search result, FAQ, tool result).
2. **Chọn 2–3 baseline defense** sau đó mới chọn mô hình / thư viện hiện thực.
3. **Chốt golden cases và metric** trước khi bắt tay tối ưu detector.
4. **PII là module bổ sung**: dữ liệu cá nhân đi đâu, bị gửi tới API nào, trường nào phải che; không nên coi regex phát hiện PII là giải pháp ngăn rò rỉ hoàn chỉnh.
5. **Chỉ khẳng định hiệu quả theo benchmark đã kiểm thử**, tránh suy diễn hệ thống an toàn tuyệt đối.

**Độ tin cậy nguồn:** Danh mục và tài liệu tham khảo ở đây được đối chiếu với **Table 1, Table 2, Table 3, Table 4 và References của chính survey**. Các nhận xét ưu tiên và gợi ý kỹ thuật là phân tích phục vụ đồ án, không phải kết luận trực tiếp của tác giả. Tài liệu **không thay thế việc đọc paper gốc** khi bạn lựa chọn một thuật toán để tái triển khai và trích dẫn học thuật.


# PHỤ LỤC K. 96 TÀI LIỆU THAM KHẢO TRONG SURVEY — TRA THEO NĂM

**Nguồn năm:** mục References của survey (trang 14–18). Đây là **96 mục bibliography**, bao gồm các công trình nền tảng, tài liệu kỹ thuật và các bài được phân tích; **không đồng nghĩa có 96 phương pháp tấn công/phòng thủ**. Riêng [25], [53] và [71] đã dùng năm đăng ban đầu thay vì năm `Accessed` (2026/2025). Các tiêu đề được trích và rút gọn tự động từ PDF survey nên có thể còn vết ngắt dòng hoặc xuống dòng do PDF; mục References gốc trong PDF là thẩm quyền khi cần trích dẫn chuẩn.

| Năm | Ref | Tên công trình / nội dung (rút gọn) | Nhóm trong tài liệu | Ưu tiên |
|---:|---|---|---|---|
| 2023 | [27] | Metagpt: Meta programming for a multi-agent collabora- tive framework | Nền tảng / dẫn nguồn | P3 |
| 2023 | [33] | [Swe-bench: Can language models resolve real-world github issues? arXiv preprint arXiv:2…](https://arxiv.org/abs/2310.06770) | Nền tảng / dẫn nguồn | P3 |
| 2023 | [82] | [Auto-gpt for online decision making: Benchmarks and additional opinions](https://arxiv.org/abs/2306.02224) | Nền tảng / dẫn nguồn | P3 |
| 2024 | [11] | Lookback lens: Detecting and mitigating contextual hallucinations in large language mod… | Nền tảng / dẫn nguồn | P3 |
| 2024 | [12] | [Prompt injection attacks on large language models in oncology](https://arxiv.org/abs/2407.18981) | A1 Manual Template | P3 |
| 2024 | [13] | [Here comes the ai worm: Unleashing zero-click worms that target genai- powered applicat…](https://arxiv.org/abs/2403.02817) | Nền tảng / dẫn nguồn | P3 |
| 2024 | [21] | Agentdojo: A dynamic environment to evaluate prompt injection attacks and defenses for … | Benchmark / ứng dụng | **P1** |
| 2024 | [22] | [Exploration of llm multi- agent application implementation based on langgraph+ crewai](https://arxiv.org/abs/2411.18241) | Nền tảng / dẫn nguồn | P3 |
| 2024 | [25] | How a prompt injection vul- nerability led to data exfiltration | Nền tảng / dẫn nguồn | P3 |
| 2024 | [26] | [Defending against indirect prompt injection attacks with spotlight- ing](https://arxiv.org/abs/2403.14720) | C1 Prompt Enhancement | **P1** |
| 2024 | [30] | Promptshield: Deployable detection for prompt injection attacks | C1 Detection Filter | **P1** |
| 2024 | [37] | [Prompt infection: Llm- to-llm prompt injection within multi-agent systems](https://arxiv.org/abs/2410.07283) | A1 Manual Template | P3 |
| 2024 | [45] | [Automatic and universal prompt injection attacks against large language models](https://arxiv.org/abs/2403.04957) | A4 Gradient | P2 |
| 2024 | [47] | Formalizing and benchmarking prompt injection attacks and defenses | Benchmark / ứng dụng | **P1** |
| 2024 | [52] | [Adversarial search engine optimization for large language models](https://arxiv.org/abs/2406.18382) | A5 Genetic/Evolutionary | P3 |
| 2024 | [53] | Function calling guide | Nền tảng / dẫn nguồn | P3 |
| 2024 | [56] | [Hacking back the ai-hacker: Prompt injection as a defense against llm-driven cyberattac…](https://arxiv.org/abs/2410.20911) | A1 Manual Template | P3 |
| 2024 | [57] | Neural exec: Learning (and learning from) execu- tion triggers for prompt injection att… | A4 Gradient | P3 |
| 2024 | [59] | Jatmo: Prompt injection defense by task-specific finetuning | C2 Model-level | P3 |
| 2024 | [60] | Applying pre-trained multilingual bert in embeddings for improved malicious prompt inje… | C1 Detection Filter | P3 |
| 2024 | [63] | [Enhancing prompt injection attacks to llms via poisoning alignment](https://arxiv.org/abs/2410.14827) | A1 Manual Template | P3 |
| 2024 | [64] | Optimization-based prompt injection attack to llm-as- a-judge | A4 Gradient | P3 |
| 2024 | [67] | [Permissive information-flow anal- ysis for large language models](https://arxiv.org/abs/2410.03055) | C3 Information Flow Control | **P1** |
| 2024 | [68] | [Scaling behavior of machine translation with large language models under prompt injecti…](https://arxiv.org/abs/2403.09832) | A1 Manual Template | P2 |
| 2024 | [72] | [Fath: Authentication-based test-time defense against indirect prompt injection attacks](https://arxiv.org/abs/2410.21492) | C1 Prompt Enhancement | P3 |
| 2024 | [73] | Mobile-agent-v2: Mobile device operation as- sistant with effective navigation via mult… | Nền tảng / dẫn nguồn | P3 |
| 2024 | [78] | [System-level defense against indirect prompt injection attacks: An information flow con…](https://arxiv.org/abs/2409.19091) | C3 Information Flow Control | **P1** |
| 2024 | [80] | Osworld: Benchmarking multimodal agents for open-ended tasks in real computer environme… | Nền tảng / dẫn nguồn | P3 |
| 2024 | [81] | [Preemptive an- swer" attacks" on chain-of-thought reasoning](https://arxiv.org/abs/2405.20902) | A1 Manual Template | P3 |
| 2024 | [84] | [Promptfuzz: Harnessing fuzzing techniques for robust testing of prompt injection in llm…](https://arxiv.org/abs/2409.14729) | A5 Genetic/Evolutionary | P2 |
| 2024 | [86] | [Injecagent: Benchmarking indirect prompt in- jections in tool-integrated large language…](https://arxiv.org/abs/2403.02691) | Benchmark / ứng dụng | **P1** |
| 2024 | [88] | Goal-guided generative prompt injection attack on large language models | A5 Genetic/Evolutionary | P3 |
| 2024 | [89] | [Agent security bench (asb): Formaliz- ing and benchmarking attacks and defenses in llm-…](https://arxiv.org/abs/2410.02644) | Benchmark / ứng dụng | **P1** |
| 2024 | [90] | [Hijack- rag: Hijacking attacks against retrieval-augmented large language models](https://arxiv.org/abs/2410.22832) | A4 Gradient | P3 |
| 2024 | [91] | [Towards action hijack- ing of large language model-based agent](https://arxiv.org/abs/2412.10807) | A1 Manual Template | P2 |
| 2025 | [1] | [A call to action for a secure-by-design generative ai paradigm](https://arxiv.org/abs/2510.00451) | C1 Prompt Enhancement | P3 |
| 2025 | [2] | [Simple prompt injection attacks can leak personal data observed by llm agents during ta…](https://arxiv.org/abs/2506.01055) | A1 Manual Template | **P1** |
| 2025 | [3] | [Breaking the prompt wall (i): A real-world case study of attacking chatgpt via lightwei…](https://arxiv.org/abs/2504.16125) | A1 Manual Template | P2 |
| 2025 | [4] | {StruQ}: Defending against prompt injection with structured queries | C2 Model-level | P3 |
| 2025 | [5] | [Defending against prompt injection with a few defensive tokens](https://arxiv.org/abs/2507.07974) | C1 Prompt Enhancement | P3 |
| 2025 | [6] | Secalign: Defending against prompt injection with preference optimization | C2 Model-level | P3 |
| 2025 | [7] | [Can indirect prompt in- jection attacks be detected and removed? arXiv preprint arXiv:2…](https://arxiv.org/abs/2502.16580) | C1 Detection Filter | **P1** |
| 2025 | [8] | [Robustness via ref- erencing: Defending against prompt injection attacks by referencing…](https://arxiv.org/abs/2504.20472) | C1 Prompt Enhancement | P3 |
| 2025 | [9] | Backdoor-powered prompt injection at- tacks nullify defense methods | A1 Manual Template | P3 |
| 2025 | [10] | Defense against prompt injection attack by leveraging attack techniques. In Pro- ceedin… | C1 Prompt Enhancement | P3 |
| 2025 | [14] | [Pub- lish to perish: Prompt injection attacks on llm-assisted peer review](https://arxiv.org/abs/2508.20863) | A3 Structural Encoding | P2 |
| 2025 | [15] | [Se- curing ai agents with information-flow control](https://arxiv.org/abs/2505.23643) | C3 Information Flow Control | P2 |
| 2025 | [16] | [Token-efficient prompt injection attack: Provoking cessation in llm rea- soning via ada…](https://arxiv.org/abs/2504.20493) | A2 LLM Generation | P3 |
| 2025 | [17] | [Mad-spear: A conformity- driven prompt injection attack on multi-agent debate systems](https://arxiv.org/abs/2507.13038) | A1 Manual Template | P3 |
| 2025 | [18] | [Vortexpia: Indirect prompt injection attack against llms for efficient extraction of us…](https://arxiv.org/abs/2510.04261) | A2 LLM Generation | **P1** |
| 2025 | [19] | [Commandsans: Securing ai agents with surgical precision prompt sanitization](https://arxiv.org/abs/2510.08829) | C1 Detection Filter | **P1** |
| 2025 | [20] | [Defeating prompt injections by design](https://arxiv.org/abs/2503.18813) | C3 Information Flow Control | P2 |
| 2025 | [23] | [Struphantom: Evolu- tionary injection attacks on black-box tabular agents powered by la…](https://arxiv.org/abs/2504.09841) | A5 Genetic/Evolutionary | P3 |
| 2025 | [24] | [Too easily fooled? prompt injection breaks llms on frustratingly simple multiple-choice…](https://arxiv.org/abs/2508.13214) | A3 Structural Encoding | P2 |
| 2025 | [28] | [Fingerprinting llms via prompt injection](https://arxiv.org/abs/2509.25448) | A4 Gradient | P3 |
| 2025 | [29] | Attention tracker: Detecting prompt injection attacks in llms | C2 Model-level | P3 |
| 2025 | [31] | The task shield: Enforcing task alignment to defend against indirect prompt injection i… | C3 Task Alignment | P2 |
| 2025 | [32] | [Promptlocate: Localizing prompt injection at- tacks](https://arxiv.org/abs/2510.12252) | C1 Detection Filter | **P1** |
| 2025 | [34] | [Focusagent: Simple yet effective ways of trimming the large context of web agents](https://arxiv.org/abs/2510.03204) | C1 Detection Filter | P3 |
| 2025 | [35] | [Prompt injection attacks on llm gener- ated reviews of scientific publications](https://arxiv.org/abs/2509.10248) | A3 Structural Encoding | P2 |
| 2025 | [36] | Prompt flow integrity to prevent privilege escalation in llm agents, 2025. | C3 Isolation | P3 |
| 2025 | [38] | Ace: A security architecture for llm-integrated app systems, 2025. | C3 Isolation | P3 |
| 2025 | [39] | Drift: Dynamic rule- based defense with injection isolation for securing llm agents | C3 Isolation | P3 |
| 2025 | [40] | Piguard: Prompt injection guardrail via mitigating overdefense for free | C1 Detection Filter | **P1** |
| 2025 | [41] | Transfer- able direct prompt injection via activation-guided mcmc sampling | A6 Sampling | P3 |
| 2025 | [42] | [Safeflow: A principled protocol for trustworthy and transactional autonomous agent syst…](https://arxiv.org/abs/2506.07564) | C3 Information Flow Control | P2 |
| 2025 | [43] | [Counterfactual evaluation for blind attack detection in llm-based evaluation systems](https://arxiv.org/abs/2507.23453) | A2 LLM Generation | P3 |
| 2025 | [44] | [Aegis: Automated co-evolutionary framework for guarding prompt injections schema](https://arxiv.org/abs/2509.00088) | A5 Genetic/Evolutionary | P3 |
| 2025 | [46] | [" your ai, my shell": Demystifying prompt injection attacks on agentic ai coding editor…](https://arxiv.org/abs/2509.22040) | A1 Manual Template | P3 |
| 2025 | [48] | [Secinfer: Preventing prompt injection via inference-time scaling](https://arxiv.org/abs/2509.24967) | C1 Detection Filter | P3 |
| 2025 | [49] | [Agrail: A lifelong agent guardrail with effec- tive and adaptive safety detection](https://arxiv.org/abs/2502.11448) | C3 Policy Control | P2 |
| 2025 | [50] | [Adversarial at- tacks on llm-as-a-judge systems: Insights from prompt injections](https://arxiv.org/abs/2504.18333) | A1 Manual Template | P2 |
| 2025 | [51] | [Cybersecurity ai: Hacking the ai hackers via prompt injection](https://arxiv.org/abs/2508.21669) | A1 Manual Template | P3 |
| 2025 | [54] | [Prompt inject detection with genera- tive explanation as an investigative tool](https://arxiv.org/abs/2502.11006) | C1 Detection Filter | P3 |
| 2025 | [55] | [May i have your attention? breaking fine-tuning based prompt injection defenses using a…](https://arxiv.org/abs/2507.07417) | A4 Gradient | P3 |
| 2025 | [58] | [Llmz+: Contextual prompt whitelist principles for agen- tic llms](https://arxiv.org/abs/2509.18557) | C1 Detection Filter | P3 |
| 2025 | [61] | [Exploiting web search tools of ai agents for data exfiltration](https://arxiv.org/abs/2510.09093) | A3 Structural Encoding | **P1** |
| 2025 | [62] | Echoleak: The first real-world zero-click prompt injection exploit in a production llm … | A1 Manual Template | **P1** |
| 2025 | [65] | [Progent: Programmable privilege control for llm agents](https://arxiv.org/abs/2504.11703) | C3 Policy Control | P2 |
| 2025 | [66] | [Promptarmor: Sim- ple yet effective prompt injection defenses](https://arxiv.org/abs/2507.15219) | C1 Detection Filter | **P1** |
| 2025 | [69] | [A taxonomy of prompt defects in llm systems](https://arxiv.org/abs/2509.14404) | Nền tảng / dẫn nguồn | P3 |
| 2025 | [70] | Contextual agent security: A policy for every purpose | C3 Policy Control | P3 |
| 2025 | [71] | Prompt injection to rce in ai agents | Nền tảng / dẫn nguồn | P3 |
| 2025 | [74] | [Agentarmor: Enforcing program analysis on agent run- time trace to defend against promp…](https://arxiv.org/abs/2508.01249) | C3 Information Flow Control | P3 |
| 2025 | [75] | [To protect the llm agent against the prompt injection attack with polymor- phic prompt](https://arxiv.org/abs/2506.05739) | C2 Model-level | P3 |
| 2025 | [76] | [Defending against indirect prompt injection by instruction detection](https://arxiv.org/abs/2505.06311) | C2 Model-level | P3 |
| 2025 | [77] | [Rl is a hammer and llms are nails: A simple reinforcement learning recipe for strong pr…](https://arxiv.org/abs/2510.04885) | A6 Sampling | P3 |
| 2025 | [79] | IsolateGPT: An Execution Isolation Architecture for LLM-Based Agentic Systems | C3 Isolation | P3 |
| 2025 | [83] | Bench- marking and defending against indirect prompt injection attacks on large languag… | Benchmark / ứng dụng | **P1** |
| 2025 | [85] | [Adaptive attacks break defenses against indirect prompt injection attacks on llm agents](https://arxiv.org/abs/2503.00061) | A5 Genetic/Evolutionary | P2 |
| 2025 | [87] | Breaking agents: Compromising autonomous llm agents through malfunction amplification | Nền tảng / dẫn nguồn | P3 |
| 2025 | [92] | [Rtbas: Defending llm agents against prompt injection and privacy leakage](https://arxiv.org/abs/2502.08966) | C3 Information Flow Control | **P1** |
| 2025 | [93] | Attention is all you need to defend against indirect prompt injection attacks in llms, … | Nền tảng / dẫn nguồn | P3 |
| 2025 | [94] | [When your reviewer is an llm: Biases, divergence, and prompt injection risks in peer re…](https://arxiv.org/abs/2509.09912) | A1 Manual Template | P3 |
| 2025 | [95] | [Melon: Provable defense against indirect prompt injection attacks in ai agents](https://arxiv.org/abs/2502.05174) | C3 Task Alignment | P3 |
| 2025 | [96] | [Pishield: Detecting prompt in- jection attacks via intrinsic llm features](https://arxiv.org/abs/2510.14005) | C2 Model-level | P3 |

**Ghi chú phân loại:** nếu cùng nghiên cứu có nhiều vai trò, bảng trên chỉ hiện một nhóm chính; ví dụ [75] xuất hiện ở hai vị trí khác nhau trong Table 2. Một số mục chỉ là bối cảnh tham khảo hoặc nguồn web, không phải paper nghiên cứu chính thức.

# J. KIỂM TRA TOÀN VẸN VÀ CHÚ THÍCH NGUỒN

- **Survey gốc:** https://arxiv.org/abs/2602.10453 (Table 1, Table 2, Table 3, Table 4, References).
- **Tài liệu 2026 bên ngoài:** liên kết gốc/nhà xuất bản đặt tại từng mục `ADD-xx`; ưu tiên thông tin ngày và kết quả trên trang bài gốc. Metadata của arXiv có thể đổi tên/phiên bản khi tác giả sửa, nên phải ghi version khi trích chi tiết trong luận văn.
- **Số lượng:** 23 hồ sơ Heuristic-based đã giữ nguyên; 14 mục nghiên cứu 2026 thêm mới; 96 tham chiếu từ bibliography survey. Chúng là **các tập đối tượng khác nhau, không cộng thành số phương pháp duy nhất**.
- **Thời gian khóa nguồn ngoài:** 01/11/2026. Không đưa các bài có ngày công bố sau mốc này vào phần `ADD`.
- **Nội dung gốc A–I:** vẫn có đủ các nhóm attacks, defenses, PII, benchmarks, future directions, cùng mô tả chi tiết 23 công trình đã có từ trước. Các con số dựa trên nghiên cứu gốc không được coi là độ hiệu quả đã xác nhận trên website của bạn.
