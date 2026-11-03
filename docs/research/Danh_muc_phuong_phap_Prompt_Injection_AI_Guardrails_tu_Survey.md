# BẢN ĐỒ PHƯƠNG PHÁP CHO ĐỒ ÁN AI GUARDRAILS

> **Đề tài:** Xây dựng hệ thống AI Guardrails phát hiện Prompt Injection và ngăn ngừa rò rỉ thông tin cá nhân trong ứng dụng mô hình ngôn ngữ lớn.  
> **Tài liệu nền:** Peiran Wang và cộng sự, *The Landscape of Prompt Injection Threats in LLM Agents: From Taxonomy to Analysis*, arXiv:2602.10453v1, 11/02/2026.  
> **Phạm vi tài liệu này:** Chỉ hệ thống hóa **những phương pháp / nghiên cứu được survey nhắc đến**. Không bổ sung nghiên cứu mới sau thời điểm khảo sát của bài.  
> **Ngữ cảnh áp dụng:** Đồ án tích hợp Guardrails vào chatbot của website thương mại điện tử đã có sẵn, triển khai trong thời gian hạn chế.

**Link survey:** https://arxiv.org/abs/2602.10453 | **PDF:** https://arxiv.org/pdf/2602.10453

---

## 0. Cách đọc tài liệu

### 0.1. Sơ đồ phân cấp

```text
AI GUARDRAILS CHO CHATBOT THƯƠNG MẠI ĐIỆN TỬ
├── A. ATTACK: Tạo payload như thế nào? (Section 3.1)
│   ├── A1. Manual template
│   ├── A2. LLM generation
│   ├── A3. Structural encoding
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

**Giới hạn quan trọng:** Survey là bài tổng quan 78 công trình (37 attack + 41 defense theo báo cáo của tác giả), không phải hướng dẫn trực tiếp xây PII recognizer. Một số công trình xuất hiện ở hơn một nhóm phân loại; không cộng các hàng trong bảng như số paper duy nhất.

---

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
  - [91] *Towards Action Hijacking of Large Language Model-based Agent* — tấn công qua agent memory.
  - [17] *MAD-SPEAR: A Conformity-Driven Prompt Injection Attack on Multi-Agent Debate Systems* — tác động đồng thuận nhiều Agent.
  - [37] *Prompt Infection: LLM-to-LLM Prompt Injection within Multi-Agent Systems* — lây lan qua luồng trao đổi Agent.
  - [2] *Simple Prompt Injection Attacks Can Leak Personal Data Observed by LLM Agents During Task Execution* — rò rỉ dữ liệu cá nhân.
  - [3] *Breaking the Prompt Wall (I): A Real-World Case Study of Attacking ChatGPT via Lightweight Prompt Injection* — lightweight attack.
  - [56] *Hacking Back the AI-Hacker: Prompt Injection as a Defense Against LLM-Driven Cyberattacks* — tấn công qua log / ngữ cảnh agent.
  - [12] *Prompt Injection Attacks on Large Language Models in Oncology* — sai lệch thông tin trong ứng dụng y tế.
  - [81] *Preemptive Answer “Attacks” on Chain-of-Thought Reasoning* — can thiệp vào suy luận.
  - [68] *Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks* — chiếm quyền tác vụ dịch.
  - [46] *“Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors* — tấn công coding agent.
  - [62] *EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System* — data exfiltration.
  - [51] *Cybersecurity AI: Hacking the AI Hackers via Prompt Injection* — thay đổi hành động agent an ninh.
  - [94] *When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review* — thao túng đánh giá.
  - [50] *Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections* — thao túng hệ thống chấm.
  - [63] *Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment* — đầu độc alignment.
  - [9] *Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods* — backdoor trong quá trình huấn luyện.

### A2. LLM Generation — 3 công trình | P2

- **Cơ chế [Survey]:** Dùng một Red-team LLM sinh payload dựa trên quy tắc hoặc chiến lược heuristic; không mặc nhiên đồng nghĩa với tối ưu lặp theo một hàm mục tiêu như nhóm Optimization.
- **Ứng dụng [Đề xuất]:** Hỗ trợ sinh biến thể test (thay cách diễn đạt, ngữ cảnh, ngôn ngữ), sau đó **gắn nhãn và kiểm tra thủ công** trước khi đưa vào golden test.
- **Giới hạn:** Có thể sinh mẫu trùng lặp, khó kiểm soát chất lượng, hoặc quá giống các mẫu dùng để điều chỉnh detector.
- **Công trình trong Table 1:**
  - [16] *Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression* — khai thác suy luận/availability.
  - [18] *VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy* — nhắm đến privacy leakage.
  - [43] *Counterfactual Evaluation for Blind Attack Detection in LLM-Based Evaluation Systems* — đánh giá/tấn công hệ thống chấm.

### A3. Structural Encoding — 4 công trình | P1

- **Cơ chế [Survey]:** Mã hóa hoặc bố trí payload theo cấu trúc nhằm tạo khoảng cách giữa bộ lọc văn bản và cách mô hình/ứng dụng giải thích nội dung; paper lấy ví dụ **Base64, ASCII art và structured file layout**.
- **Ứng dụng [Đề xuất]:** Benchmark các payload trong văn bản sản phẩm, HTML, Markdown hoặc tài liệu được parser chuyển thành text; cần đo cả tính hợp lệ của dữ liệu sau chuẩn hóa.
- **Phòng tránh liên quan:** parser-aware checks, phát hiện đoạn đáng ngờ, không mặc nhiên chạy theo chỉ dẫn được giải mã; kiểm tra chéo cả bản raw và bản sau tiền xử lý.
- **Giới hạn:** Không phải chuỗi Base64 nào cũng độc hại; mỗi loại parser có cách xử lý khác nhau.
- **Công trình trong Table 1:**
  - [14] *Publish to Perish: Prompt Injection Attacks on LLM-Assisted Peer Review* — đánh giá tài liệu.
  - [24] *Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions* — làm sai đánh giá/câu hỏi.
  - [61] *Exploiting Web Search Tools of AI Agents for Data Exfiltration* — rò rỉ qua web search tools.
  - [35] *Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications* — thao túng reviewer.

## A.2. Optimization-based attacks (14 công trình)

### A4. Gradient-based Optimization — 6 công trình | P3

- **Cơ chế [Survey]:** Dùng thông tin gradient hoặc đặc trưng nội bộ để tối ưu token/suffix nhằm tăng xác suất tạo đầu ra/hành vi mà attacker mong muốn; khảo sát liên hệ tới Greedy Coordinate Gradient (GCG).
- **Điều kiện thường gặp:** White-box hoặc quyền truy cập mạnh vào mô hình/surrogate; không phù hợp trực tiếp nếu chỉ gọi API thương mại.
- **Liên quan đề tài [Đề xuất]:** Nắm nguyên lý để đánh giá hạn chế của bộ detector dựa trên template, không cần tự huấn luyện hay tự tối ưu attack.
- **Công trình trong Table 1:**
  - [45] *Automatic and Universal Prompt Injection Attacks Against Large Language Models*.
  - [28] *Fingerprinting LLMs via Prompt Injection*.
  - [57] *Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks*.
  - [64] *Optimization-Based Prompt Injection Attack to LLM-as-a-Judge*.
  - [55] *May I Have Your Attention? Breaking Fine-Tuning Based Prompt Injection Defenses Using Architecture-Aware Attacks*.
  - [90] *HijackRAG: Hijacking Attacks Against Retrieval-Augmented Large Language Models*.

### A5. Genetic / Evolutionary Optimization — 6 công trình | P3

- **Cơ chế [Survey]:** Dùng thuật toán tiến hóa, lựa chọn/sửa đổi ứng viên, hoặc feedback-driven searching để tìm payload tốt hơn. Nhiều hướng có thể áp dụng trong Black-box.
- **Lưu ý:** Các công trình trong nhóm không nhất thiết đều triển khai **Genetic Algorithm thuần túy**; ví dụ *PromptFuzz* sử dụng fuzzing. Đây là cách **survey xếp nhóm**, không phải khẳng định các kỹ thuật đồng nhất.
- **Công trình trong Table 1:**
  - [88] *Goal-Guided Generative Prompt Injection Attack on Large Language Models*.
  - [84] *PromptFuzz: Harnessing Fuzzing Techniques for Robust Testing of Prompt Injection in LLMs*.
  - [23] *StruPhantom: Evolutionary Injection Attacks on Black-Box Tabular Agents Powered by Large Language Models*.
  - [44] *AEGIS: Automated Co-Evolutionary Framework for Guarding Prompt Injections Schema*.
  - [85] *Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents*.
  - [52] *Adversarial Search Engine Optimization for Large Language Models*.

### A6. Sampling-based Optimization — 2 công trình | P3

- **Cơ chế [Survey]:** Tối ưu payload thông qua lấy mẫu, reward/feedback, thay vì trực tiếp cập nhật token bằng gradient từ mô hình nạn nhân; gồm RL và MCMC.
- **Liên quan đồ án [Đề xuất]:** Đọc để hiểu khả năng thích nghi/chuyển giao của payload; không bắt buộc tự triển khai.
- **Công trình trong Table 1:**
  - [77] *RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection*.
  - [41] *Transferable Direct Prompt Injection via Activation-Guided MCMC Sampling*.

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

**Không gán nhầm nguồn:** Homoglyph, zero-width characters, chữ trắng hoặc chữ rất nhỏ trong HTML/PDF là ví dụ **có thể đưa vào kế hoạch mở rộng**, nhưng survey này không xây taxonomy chi tiết riêng cho từng kỹ thuật đó.

---

# C. DEFENSE — CÁC CÁCH PHÒNG THỦ

**Nguồn:** Section 4, trang 5–10, **Table 2**; phân tầng **Text-level / Model-level / Execution-level**.

## C1. TEXT-LEVEL — Bảo vệ trên input/output dạng text (18 hàng nghiên cứu trong Table 2)

### C1.1. Detection Filter (11 công trình)

| Mã | Phương pháp / nhóm nghiên cứu | Công trình trong survey | Mô tả ngắn | Ưu tiên |
|---|---|---|---|---|
| **D01** | LLM-based classification | **PromptShield [30]** | Mô hình đánh giá prompt có injection không | P1 |
| **D02** | Detection + generative explanation | **Pan et al. [54]** | Thêm lý do giúp người kiểm tra hiểu quyết định | P2 |
| **D03** | Third-party input detection | **PromptArmor [66]** | Kiểm tra nội dung ngoài đưa vào LLM | **P1** |
| **D04** | Inference-time scaling / self-inspection | **SecInfer [48]** | Tăng suy luận kiểm tra nội dung khó | P3 |
| **D05** | Policy/whitelist-style detection | **LLMz+ [58]** | Xác định tính hợp lệ theo nguyên tắc whitelist | P2 |
| **D06** | Segment localization | **PromptLocate [32]** | Khoanh vùng đoạn bị injection | **P1** |
| **D07** | Long-context / segment handling | **FocusAgent [34]** | Xử lý/chọn lọc context dài theo cách survey nhóm vào detection | P2 |
| **D08** | BERT-based classifier | **Rahman et al. [60]** | Phân loại bằng mô hình encoder nhỏ hơn LLM | **P1** |
| **D09** | Lightweight prompt-injection guard | **PIGuard [40]** | Phát hiện và cân bằng chặn nhầm | **P1** |
| **D10** | Indirect PI detection and removal | **Chen et al. [7]** | Nhận diện và loại bỏ PI gián tiếp | **P1** |
| **D11** | Fine-grained / token sanitizer | **CommandSans [19]** | Can thiệp cụ thể vào các chỉ dẫn nguy hiểm | **P1** |

**Hai hướng triển khai [Đề xuất]:** `rule-based filter` và `small-model classifier`; sau đó so sánh với detector sử dụng LLM nếu ngân sách cho phép. **Regex đơn thuần không phải một nhóm thuật toán riêng trong taxonomy của Table 2**, dù có thể dùng làm baseline cho đồ án.

### C1.2. Prompt Enhancement (7 công trình trong Table 2)

| Mã | Phương pháp | Công trình trong survey | Vai trò | Ưu tiên |
|---|---|---|---|---|
| **D12** | Input / instruction–data separation | **Spotlighting [26]** | Phân ranh dữ liệu và chỉ dẫn | **P1** |
| **D13** | Output-side separation / authentication | **FATH [72]** | Kiểm chứng ranh giới/nguồn gốc đầu ra | P2 |
| **D14** | Self-referencing | **Chen et al. [8]** | Đối chiếu lại chỉ dẫn gốc | P2 |
| **D15** | Defensive / negative prompts | **Chen et al. [5], [10]** | Thêm token/prompt phòng thủ | **P1** |
| **D16** | Prompt rewriting / sanitization | **Alharthi et al. [1]** | Viết lại đầu vào giảm nội dung gây ảnh hưởng | **P1** |
| **D17** | Polymorphic prompt protection / rewriting | **Wang et al. [75]** | Biến đổi cấu trúc prompt để giảm khả năng dự đoán | P2 |

**Gợi ý baseline [Đề xuất]:** Prompt-only defense bằng delimiters / defensive instruction, so với rule filter, classifier và hybrid. Chỉ dùng delimiter **không tạo ra bảo đảm bảo mật tuyệt đối**.

## C2. MODEL-LEVEL — Can thiệp vào backbone LLM (7 hàng trong Table 2)

### C2.1. Model Alignment / Fine-tuning (4 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D18** | Task-specific fine-tuning | **Jatmo [59]** | P3 |
| **D19** | Preference / security alignment | **SecAlign [6]** | P3 |
| **D20** | Structured-query fine-tuning | **StruQ [4]** | P3 |
| **D21** | Polymorphic prompt fine-tuning | **Wang et al. [75]** | P3 |

### C2.2. Intermediate Representation (IR) Intervention (3 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D22** | Attention map tracking | **Attention Tracker [29]** | P3 |
| **D23** | Intrinsic-feature-based PI detection | **PIShield [96]** | P3 |
| **D24** | Hidden-state / representation probing | **Wen et al. [76]** | P3 |

**Lý do ưu tiên thấp [Đề xuất]:** Với chatbot gọi LLM API, thường không thể truy cập trọng số, gradient hoặc attention của backbone. Đây là hướng nền tảng nghiên cứu, không bắt buộc đối với lớp guardrails *plug-and-play*.

## C3. EXECUTION-LEVEL — Kiểm soát hành vi Agent và luồng dữ liệu (16 hàng trong Table 2)

### C3.1. Task Alignment (2 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D25** | Goal/task alignment | **Task Shield [31]** | P2 |
| **D26** | Robust action alignment | **Melon [95]** | P3 |

**Áp dụng [Đề xuất]:** Nếu chatbot có tool gọi API xem đơn hàng/chỉnh sửa giỏ hàng, kiểm tra hành động có khớp mục tiêu được ủy quyền không.

### C3.2. Information Flow Control (7 công trình)

| Mã | Phương pháp | Công trình | Liên quan đề tài | Ưu tiên |
|---|---|---|---|---|
| **D27** | Trust-label / information flow | **Fides [15]** | Phân biệt dữ liệu đáng tin và không đáng tin | P2 |
| **D28** | Transactional trustworthy flow | **SafeFlow [42]** | Kiểm soát luồng dữ liệu/hành động | P2 |
| **D29** | Permissive information-flow analysis | **Siddiqui et al. [67]** | Cho phép xử lý dữ liệu ngoài nhưng khóa luồng nguy hiểm | **P1** |
| **D30** | Flow-based isolation | **Wu et al. [78]** | Ngăn nâng quyền qua dữ liệu không tin cậy | P2 |
| **D31** | Runtime trace analysis | **AgentArmor [74]** | Kiểm tra chuỗi thực thi | P2 |
| **D32** | Exfiltration / privacy-flow protection | **RTBAS [92]** | **Sát bài toán ngăn rò rỉ** | **P1** |
| **D33** | Program / flow control architecture | **CaMeL [20]** | Kiểm soát ảnh hưởng dữ liệu lên hành động | P2 |

**Áp dụng [Đề xuất]:** Gắn nhãn dữ liệu chứa PII, đặt quy tắc *không truyền raw PII sang LLM API ngoài*. Đây là ý tưởng kiến trúc giản lược, **không phải một thuật toán PII cụ thể** được survey mô tả.

### C3.3. Specification / Policy Control (3 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D34** | Adaptive safety policy | **AGrail [49]** | P2 |
| **D35** | Contextual security policy | **Tsai & Bagdasarian [70]** | P2 |
| **D36** | Programmable privilege control | **Progent [65]** | P2 |

**Áp dụng [Đề xuất]:** Quy tắc `ALLOW`, `MASK`, `BLOCK`, `REVIEW` tùy nội dung và mức rủi ro. Đây là policy của **đồ án**, không phải tập nhãn chuẩn của survey.

### C3.4. Isolation (4 công trình)

| Mã | Phương pháp | Công trình | Ưu tiên |
|---|---|---|---|
| **D37** | Environment isolation | **IsolateGPT [79]** | P3 |
| **D38** | Planning isolation / prompt-flow integrity | **PFI [36]** | P3 |
| **D39** | Dynamic rule-based isolation | **DRIFT [39]** | P3 |
| **D40** | Security architecture / planning isolation | **ACE [38]** | P3 |

**Giới hạn [Survey]:** Cô lập quá chặt có thể làm Agent không thực hiện được tác vụ cần đọc và dùng dữ liệu bên ngoài; cần đo **utility** ngoài ASR.

### C4. Bảng chọn defense cho đồ án

| Nhu cầu đồ án | Nhóm nên ưu tiên | Paper đọc trước |
|---|---|---|
| Phát hiện Prompt Injection trong user input | Detection filter / non-LLM classifier | [30], [40], [60] |
| Phát hiện Prompt Injection trong dữ liệu RAG/product | Third-party input detection, segment detection | [66], [7], [32], [19] |
| Bảo vệ bằng cấu trúc prompt | Input separation, defensive prompts | [26], [5], [10] |
| Ngăn dữ liệu nhạy cảm đi sai đích | IFC và privacy-flow monitoring | [67], [92], [15] |
| Chính sách quyết định hành động | Policy control | [49], [65] |
| Chatbot có API/tool calls | Task alignment và flow control | [31], [74], [20] |

---

# D. CONFIDENTIALITY / PII — PHẦN LIÊN QUAN VÀ PHẦN SURVEY CHƯA BAO PHỦ

## D1. Các hướng **có trong survey** liên quan đến rò rỉ dữ liệu

| Hướng | Attack papers liên quan | Defense papers liên quan | Ý nghĩa |
|---|---|---|---|
| Tấn công lấy cắp dữ liệu quan sát được | [2], [18], [62] | [92], [15], [67] | Payload khiến Agent tiết lộ dữ liệu không được phép |
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
| **OpenPI** | [47] | Benchmark PI trên mô hình tổng quát | ASR, Utility |
| **BIPIA** | [83] | Indirect PI | ASR, Utility |
| **InjecAgent** | [86] | Tool/function-call PI | ASR |
| **AgentDojo** | [21] | Agent tương tác đa bước | ASR, Utility |
| **Agent Security Bench (ASB)** | [89] | Agent benchmark đa bối cảnh | ASR, Utility |

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

## G1. Ưu tiên P1 — chọn làm nền tảng trước

- [ ] **A1 — Manual Template:** Xây bộ attack mẫu.
- [ ] **A3 — Structural Encoding:** Xây bộ attack obfuscated tối thiểu.
- [ ] **B1/B4 — Indirect Injection + Context/Encoding:** Chọn attack surface ở dữ liệu sản phẩm/FAQ/tool result.
- [ ] **D08/D09 — Classifier nhỏ:** Baseline model-based detection.
- [ ] **D03/D10 — Third-party / Indirect PI Detection:** Thiết kế cách phát hiện nội dung truy xuất.
- [ ] **D06/D11 — Segment/Token-level:** Nghiên cứu biện pháp chặn chọn lọc, tránh chặn cả tài liệu.
- [ ] **D12/D15 — Separation + Defensive Prompt:** Baseline phòng thủ đơn giản.
- [ ] **D29/D32 — IFC + Exfiltration Control:** Tách rule xử lý PII khỏi logic phát hiện PI.
- [ ] **E1/E3/E4 — Benchmark & metrics:** Có golden cases và so sánh baseline.

## G2. Ưu tiên P2 — sau khi MVP hoàn thành

- [ ] A2 — LLM-generated attack variants.
- [ ] D02 — Explanation / audit trail.
- [ ] D25 — Task Alignment nếu chatbot có tool.
- [ ] D34–D36 — Policy Control.
- [ ] E01–E05 — Chọn context-aware attacks khớp tool thực tế.
- [ ] F03/F05 — Trust boundary và human review.

## G3. Ưu tiên P3 — chỉ cần tổng quan / future work

- [ ] A4–A6 — Gradient / Evolutionary / RL / MCMC attack.
- [ ] D18–D24 — Backbone fine-tuning và attention/IR probes.
- [ ] D37–D40 — Full architectural isolation.
- [ ] F01/F02 — Attention firewall và resource-aware defense.
- [ ] Vision/multimodal injections.

## G4. Trình tự đọc survey nhanh

| Bước | Đọc phần | Mục tiêu |
|---|---|---|
| 1 | **Section 4.1** | Chọn guardrails text-level / classifier / prompt-enhancement |
| 2 | **Sections 3.1–3.2** | Chọn payload và threat model |
| 3 | **Section 4.3** | Thiết kế chính sách và kiểm soát rò rỉ |
| 4 | **Section 5** | Hiểu benchmark, limitations của cách chấm |
| 5 | **Section 6 + Appendix C** | Tạo tình huống golden end-to-end |
| 6 | **Section 4.2, 4.4–4.6** | Viết Related Work và phân tích trade-off |
| 7 | **Appendix A–B** | Nêu giới hạn và hướng phát triển |

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
| References | Tên đầy đủ công trình [1]–[96] | 14–18 |

## I2. Cách dùng tài liệu để lập kế hoạch

1. **Chọn attack surface** của chatbot thực tế trước (user input, product description, search result, FAQ, tool result).
2. **Chọn 2–3 baseline defense** sau đó mới chọn mô hình / thư viện hiện thực.
3. **Chốt golden cases và metric** trước khi bắt tay tối ưu detector.
4. **PII là module bổ sung**: dữ liệu cá nhân đi đâu, bị gửi tới API nào, trường nào phải che; không nên coi regex phát hiện PII là giải pháp ngăn rò rỉ hoàn chỉnh.
5. **Chỉ khẳng định hiệu quả theo benchmark đã kiểm thử**, tránh suy diễn hệ thống an toàn tuyệt đối.

**Độ tin cậy nguồn:** Danh mục và tài liệu tham khảo ở đây được đối chiếu với **Table 1, Table 2, Table 3, Table 4 và References của chính survey**. Các nhận xét ưu tiên và gợi ý kỹ thuật là phân tích phục vụ đồ án, không phải kết luận trực tiếp của tác giả. Tài liệu **không thay thế việc đọc paper gốc** khi bạn lựa chọn một thuật toán để tái triển khai và trích dẫn học thuật.
