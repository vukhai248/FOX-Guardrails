# Phân loại paper cho chatbot chăm sóc khách hàng thương mại điện tử

Ngày rà soát: 01/11/2026.

Tài liệu này là **chỉ mục đọc chính cho phạm vi hiện tại**, thay cho các danh sách P1/P2/P3 quá rộng trong [bản đồ nghiên cứu](AI_Guardrails_Research_23_Papers.md). Các mã H/G/S, ADD và số [n] được giữ nguyên để tra hồ sơ gốc. Phân loại dưới đây là đánh giá mức phù hợp với đồ án, không thay đổi taxonomy của survey.

## 1. Bối cảnh và giả định làm việc

Thông tin người làm đồ án đã xác nhận:

- Có project thương mại điện tử để làm nền.
- Muốn tập trung prompt injection và bảo vệ PII trong bối cảnh CSKH.
- Chưa xác định chatbot có cơ chế agent, skill hoặc MCP; có khả năng tra cứu khách hàng/thông tin qua một số công cụ đã phân quyền rõ ràng.

Giả định để lọc tài liệu, **cần xác nhận khi khảo sát project, không phải chức năng đã hiện thực**:

- Chatbot xử lý văn bản; trả lời về sản phẩm, giao hàng, đổi trả/bảo hành và có thể tra cứu đơn hàng của khách đã đăng nhập.
- Backend giữ quyền xác thực, kiểm tra chủ sở hữu và phạm vi dữ liệu được trả về. Không giao việc quyết định quyền truy cập cho LLM.
- Chỉ đọc dữ liệu trong phạm vi ban đầu. Chưa giả định có terminal, thực thi code, gửi email, web search, tải URL tùy ý, thay đổi đơn hàng hoặc hoàn tiền.
- Chưa đưa PDF/OCR, ảnh, multi-agent, fine-tuning backbone và dữ liệu huấn luyện bị đầu độc vào bộ thực nghiệm chính.

**Hướng nghiên cứu đề xuất:** Phát hiện prompt injection gián tiếp trong dữ liệu phục vụ CSKH và bảo vệ việc sử dụng thông tin khách hàng, trong khi vẫn hoàn thành tác vụ hợp lệ.

Đây là phạm vi ứng dụng để chọn paper; chưa phải thiết kế kỹ thuật hay cam kết triển khai mọi chức năng nêu trên.

## 2. Tool, skill và MCP liên quan thế nào?

| Khái niệm | Cách hiểu trong đồ án | Hệ quả đối với phạm vi |
|---|---|---|
| Tool | Hàm/API mà ứng dụng có thể gọi, ví dụ tra đơn hàng. Nếu backend tự gọi rồi đưa kết quả cho LLM, đó vẫn là nguồn dữ liệu ngoài cần kiểm tra, dù LLM không tự chọn tool | Không cần có terminal để nghiên cứu injection trong dữ liệu trả về |
| Skill | Cách đóng gói hướng dẫn/quy trình/tài nguyên tái sử dụng, tùy framework | Chưa cần xây hay nghiên cứu cơ chế này |
| MCP | Giao thức tích hợp công cụ và tài nguyên; bản thân nó không quyết định quyền nghiệp vụ của chatbot | Không phải điều kiện để làm đồ án; chưa cần thêm vào hệ thống |

Phải phân biệt **API hợp lệ để truy cập dữ liệu** và **nội dung bên trong response có quyền ra lệnh hay không**. Một API đã phân quyền có thể trả về cùng lúc trường trạng thái đơn hàng và ghi chú do người dùng nhập. Không tự động xem ghi chú đó là chỉ dẫn đáng tin vì nó đến từ API nội bộ.

Nếu backend phân quyền đúng, lời yêu cầu của LLM truy cập đơn hàng người khác phải bị từ chối ở backend. Đây là kiểm tra nền tảng; không dùng một lỗi phân quyền API để chứng minh detector prompt injection hiệu quả hay thất bại.

## 3. Ba nhóm kết quả cần phân biệt

| Nhóm | Ví dụ đề xuất cho CSKH | Vai trò |
|---|---|---|
| Nhiệm vụ bị điều hướng | Đang hỏi chính sách giao hàng nhưng ghi chú/review ra lệnh chuyển khách sang website khác | Đánh giá PI trong context và mức hoàn thành nhiệm vụ |
| Thu thập PII không cần thiết | Nội dung truy xuất giả quy trình xác minh, yêu cầu CCCD khi khách chỉ hỏi thời gian giao hàng | Nhánh privacy gắn trực tiếp với PI; không cần tool gửi dữ liệu |
| Sử dụng/tiết lộ PII vượt chính sách | Dữ liệu trả về chứa số điện thoại/địa chỉ không cần cho câu hỏi nhưng được đưa nguyên văn tới LLM bên ngoài hoặc ghi vào log | Nhánh bảo vệ dữ liệu; có thể xảy ra cả khi không có PI |

Trong nhóm cuối, cần tách **dữ liệu được gửi tới nhà cung cấp LLM**, **dữ liệu hiển thị trong câu trả lời**, **dữ liệu lưu trong log**. Không gọi mọi lần xuất hiện PII là rò rỉ: cần quy tắc về mục đích, người nhận và mức chi tiết được phép.

Một câu “hãy cung cấp CCCD” chưa chứa số CCCD thật. PII recognizer/masking không thay thế kiểm tra việc chatbot yêu cầu thông tin không cần thiết. Ngược lại, detector PI không thay thế việc nhận diện PII trong một câu hỏi hoàn toàn hợp lệ.

## 4. Quy tắc xếp nhóm đọc

| Nhóm | Ý nghĩa | Cách sử dụng |
|---|---|---|
| **CỐT LÕI** | Trực tiếp phục vụ attack, baseline hoặc đánh giá trong phạm vi hiện tại | Đọc phần phương pháp và đánh giá liên quan; không phải tái hiện toàn bộ |
| **BỔ TRỢ** | Có ý tưởng hữu ích nhưng chưa cần để bắt đầu | Chỉ mở khi có câu hỏi cụ thể chưa giải quyết được |
| **CÓ ĐIỀU KIỆN** | Chỉ sát bài toán nếu ứng dụng có tính năng/quyền tương ứng | Xác nhận điều kiện trước khi đọc sâu hay đưa vào benchmark |
| **NGOÀI PHẠM VI** | Cần môi trường/quyền/mục tiêu khác | Để Related Work hoặc Future Work; bỏ khỏi backlog hiện tại |

Quy tắc dừng: một paper không giúp trả lời câu hỏi nghiên cứu, tạo test, chọn baseline hoặc định nghĩa metric thì chưa cần đọc tiếp. Không lấy số paper đã đọc làm mục tiêu đồ án.

## 5. Danh sách đọc chính: 5 bài + survey chọn lọc

| Thứ tự | Paper / mã | Đọc để lấy gì? | Kết quả đọc cần có |
|---|---|---|---|
| 0 | [Survey 2602.10453](https://arxiv.org/abs/2602.10453), §2, §3.2, §4.1, §5; đọc lướt §6–7 | Ranh giới dữ liệu/chỉ dẫn, IPI, text-level defense, đánh giá security/utility | Một trang mô tả nguồn dữ liệu và quyền của chatbot; chưa tái lập toàn bộ AGENTPI |
| 1 | [BIPIA — [83]](https://arxiv.org/abs/2312.14197) | Injection trong nội dung ngoài, cách đặt tác vụ và baseline phân tách/nhắc chỉ dẫn | Mẫu test: user task + context sạch/nhiễm + kết quả hợp lệ/mục tiêu attacker |
| 2 | [VortexPIA — G02 / [18]](https://arxiv.org/abs/2510.04261) | Injection khiến chatbot chủ động hỏi thông tin riêng tư; giả lịch sử/đồng ý | Test CSKH hỏi PII không cần thiết và quy tắc phân biệt yêu cầu hợp lệ |
| 3 | [PromptArmor — D03 / [66]](https://arxiv.org/abs/2507.15219) | Baseline dùng LLM phát hiện/loại chỉ dẫn chèn trước xử lý | Một baseline tham chiếu; cân nhắc chi phí và dữ liệu gửi tới detector bên ngoài |
| 4 | [PIDS-Bench — ADD-13](https://arxiv.org/abs/2609.15017) | Chặn nhầm, nội dung hợp lệ giống attack, obfuscation và đổi phân phối | Bộ hard-benign và cách báo cáo recall/FPR theo nhóm |
| 5 | [RAG-PIBench — ADD-14](https://arxiv.org/abs/2610.08571) | Chia tập tránh trùng lặp, baseline sparse/transformer cho detector | Quy tắc chia dữ liệu và danh sách baseline gọn |

**Lưu ý ADD-14:** “leakage-aware” nói về dữ liệu trùng/lọt giữa train và test, không phải phương pháp ngăn lộ PII khách hàng.

Đọc danh sách trên để thiết kế nghiên cứu, không cam kết tự dựng lại mọi model/dataset trong cả 5 bài. Nếu cần baseline prompt-only sâu hơn, đọc Spotlighting [26] trước khi mở rộng sang nhiều defense khác.

## 6. Xếp lại toàn bộ 23 hồ sơ heuristic-based

Tên rút gọn dùng để tra cứu. Cơ chế/số liệu chi tiết và liên kết gốc giữ tại hồ sơ tương ứng trong bản đồ nghiên cứu.

| Mã | Ref | Paper | Nhóm mới | Lý do / điều kiện |
|---|---|---|---|---|
| H01 | [91] | AI² / Action Hijacking | BỔ TRỢ | Lấy nguyên lý dữ liệu gợi hành động; không cần tái hiện pipeline lập kế hoạch đặc thù |
| H02 | [17] | MAD-Spear | NGOÀI PHẠM VI | Cần multi-agent debate/đồng thuận |
| H03 | [37] | Prompt Infection | NGOÀI PHẠM VI | Nghiên cứu lây qua trao đổi/memory nhiều agent |
| H04 | [2] | Simple PI Attacks Can Leak Personal Data | CÓ ĐIỀU KIỆN | Benchmark gốc có tool exfiltration/email. Khi chỉ có API đọc, lấy ý tưởng luồng PII; không coi là tái lập exfiltration gốc |
| H05 | [3] | Breaking the Prompt Wall | BỔ TRỢ | Case study chuyển hướng nội dung/khuyến nghị; hữu ích cho review/mô tả sản phẩm |
| H06 | [56] | Mantis / Hacking Back the AI-Hacker | NGOÀI PHẠM VI | Bẫy agent pentest, khác mục tiêu CSKH |
| H07 | [12] | PI in Oncology | NGOÀI PHẠM VI | Bối cảnh y tế và đầu vào thị giác ngoài giả định text hiện tại |
| H08 | [81] | Preemptive Answer Attacks | NGOÀI PHẠM VI | Nghiên cứu bias suy luận; chưa cần khi trọng tâm là IPI/PII trong CSKH |
| H09 | [68] | Machine Translation under PI | BỔ TRỢ | Ví dụ dễ hiểu về data/instruction và task hijack; không cần dựng benchmark dịch |
| H10 | [46] | Your AI, My Shell / AIShellJack | NGOÀI PHẠM VI | Cần coding editor/repository/terminal; không thêm các quyền này để dùng paper |
| H11 | [62] | EchoLeak | CÓ ĐIỀU KIỆN | Chỉ ưu tiên nếu frontend/backend thực sự tải resource/link ngoài; sinh URL chưa đồng nghĩa request đã xảy ra |
| H12 | [51] | Cybersecurity AI | NGOÀI PHẠM VI | Shell và agent an ninh; chỉ giữ bài học dữ liệu tool không được ra lệnh |
| H13 | [94] | When Your Reviewer Is an LLM | CÓ ĐIỀU KIỆN | Nếu ingest PDF và nghiên cứu khác biệt parser/render; không cần cho JSON/text |
| H14 | [50] | Attacks on LLM-as-a-Judge | CÓ ĐIỀU KIỆN | Đọc cho bộ đánh giá nếu dùng LLM judge; không phải chức năng chatbot |
| H15 | [63] | PoisonedAlign | NGOÀI PHẠM VI | Attacker sửa dữ liệu alignment/training, khác lớp guard runtime |
| H16 | [9] | Backdoor-Powered PI | NGOÀI PHẠM VI | Cần backbone bị cấy backdoor; không tái huấn luyện trong phạm vi này |
| G01 | [16] | Token-Efficient PI / Reasoning Cessation | NGOÀI PHẠM VI | Mục tiêu dừng reasoning/availability, chưa phải trọng tâm |
| G02 | [18] | VortexPIA | CỐT LÕI | Nối trực tiếp IPI và việc chatbot yêu cầu PII không cần thiết |
| G03 | [43] | Counterfactual Evaluation | CÓ ĐIỀU KIỆN | Phòng thủ cho evaluator; chỉ đọc nếu chọn LLM-as-a-Judge |
| S01 | [14] | Publish to Perish | CÓ ĐIỀU KIỆN | Hidden prompt trong PDF; mở khi có PDF ingestion |
| S02 | [24] | Too Easily Fooled? | CÓ ĐIỀU KIỆN | PDF white/black text; không đưa vào bộ test text thuần |
| S03 | [61] | Web Search Tools for Exfiltration | CÓ ĐIỀU KIỆN | Cần web search/URL egress. Có thể mượn biến thể encoding, nhưng không báo đã tái lập exfiltration |
| S04 | [35] | PI on Generated Scientific Reviews | CÓ ĐIỀU KIỆN | Khi có chức năng chấm/kiểm duyệt nội dung bằng LLM; không phải chatbot tra đơn |

H04/H11/S03 được hạ từ ưu tiên rộng về PII xuống **có điều kiện** vì quyền email/web/resource fetching chưa được xác nhận. Đây là điều chỉnh theo ứng dụng, không phải đánh giá chất lượng paper.

## 7. Xếp lại 14 công trình ADD năm 2026

| Mã | Tên rút gọn | Nhóm mới | Lý do / điều kiện |
|---|---|---|---|
| ADD-01 | Hidden-in-Plain-Text / OpenRAG-Soc | CÓ ĐIỀU KIỆN | Hữu ích khi ingest review/HTML/Markdown từ nguồn ngoài; chỉ lấy dữ liệu JSON đã chọn trường thì chưa cần toàn bộ harness |
| ADD-02 | Silent Egress | CÓ ĐIỀU KIỆN | Cần outbound request/tool/URL preview; không giả định chatbot có kênh này |
| ADD-03 | Survey of Secure RAG | BỔ TRỢ | Tra threat model khi cần; đã có survey nền, chưa đọc thêm toàn bộ |
| ADD-04 | Evaluation of PI Defenses | BỔ TRỢ | Bài toán system-prompt secrets khác PII nghiệp vụ; lấy ý kiểm soát ở mã ứng dụng |
| ADD-05 | ARGUS | CÓ ĐIỀU KIỆN | Khi mở rộng nhiều bước/tool và cần provenance graph; hiện chưa triển khai kiến trúc này |
| ADD-06 | Blind Spots / Domain Camouflage | BỔ TRỢ | Mượn ý payload giống văn bản nghiệp vụ; không tái tạo multi-agent |
| ADD-07 | Can It Reach the Generator? | BỔ TRỢ | Đọc khi xây thử nghiệm RAG end-to-end qua retrieval/reranking; chưa cần để chạy detector trên context đã chọn |
| ADD-08 | Prompting Defenses against Camouflage | BỔ TRỢ | Mở khi so sánh prompt-only baseline trước nội dung ngụy trang |
| ADD-09 | Indirect PI / Document Rendering | CÓ ĐIỀU KIỆN | PDF/HTML và khác biệt hiển thị/trích xuất |
| ADD-10 | PIArena | BỔ TRỢ | Lấy protocol đánh giá thích nghi; không chạy toàn bộ nền tảng |
| ADD-11 | Defenses Learn Surface Heuristics | BỔ TRỢ | Phân tích chặn nhầm/shortcut; đọc sau PIDS-Bench nếu cần giải thích lỗi |
| ADD-12 | Rethinking Assessments | BỔ TRỢ | Tham khảo tính thực tế khi viết phần hạn chế/đánh giá |
| ADD-13 | PIDS-Bench | CỐT LÕI | Hard-benign, obfuscation và FPR |
| ADD-14 | RAG-PIBench | CỐT LÕI | Detector RAG, baseline và split chống trùng dữ liệu |

## 8. Lọc defense và benchmark trong survey

### 8.1. Toàn bộ mã defense D01–D40

Các hàng là **nhóm đọc**, không phải danh sách cần hiện thực. D15 ghép hai reference; [75] xuất hiện ở D17 và D21. Không cộng số mã D thành số công trình duy nhất.

| Mã defense | Ref survey | Nhóm mới | Quyết định đọc |
|---|---|---|---|
| D03 | [66] | CỐT LÕI | PromptArmor làm baseline tham chiếu |
| D12 | [26] | BỔ TRỢ | Spotlighting nếu cần hiểu sâu baseline tách dữ liệu/chỉ dẫn |
| D01, D08, D09 | [30], [60], [40] | BỔ TRỢ | Chọn một khi cần detector nhỏ/chi phí thấp; không đọc và huấn luyện cả ba |
| D06, D10, D11 | [32], [7], [19] | BỔ TRỢ | Chỉ mở khi chặn cả context làm mất utility và cần localization/sanitization |
| D02 | [54] | BỔ TRỢ | Nếu cần nghiên cứu explanation; audit log cơ bản chưa đòi hỏi tái lập paper |
| D05, D14, D15, D16 | [58], [8], [5], [10], [1] | BỔ TRỢ | Các cách whitelist/referencing/defensive prompting/rewrite; chưa thêm vào shortlist |
| D04, D07 | [48], [34] | CÓ ĐIỀU KIỆN | Khi context dài hoặc tăng suy luận kiểm tra là vấn đề đo được |
| D13 | [72] | BỔ TRỢ | Output authentication; chưa cần cho baseline đầu tiên |
| D17, D21 | [75] | NGOÀI PHẠM VI | Polymorphic prompt/fine-tuning thêm độ phức tạp chưa cần thiết |
| D18, D19, D20 | [59], [6], [4] | NGOÀI PHẠM VI | Fine-tuning backbone. Không nhầm với huấn luyện classifier PI nhỏ, vốn vẫn có thể nằm trong đồ án |
| D22, D23, D24 | [29], [96], [76] | NGOÀI PHẠM VI | Cần model internals/IR; không phù hợp giả định gọi LLM qua API |
| D25, D26 | [31], [95] | CÓ ĐIỀU KIỆN | Khi LLM tự chọn hành động/tool qua nhiều bước; chưa cần cho backend tra cứu cố định |
| D27, D29, D30, D32 | [15], [67], [78], [92] | BỔ TRỢ | Lấy mô hình source/sink và luồng PII nếu cần; không tái tạo toàn bộ IFC/runtime monitor |
| D28, D31, D33 | [42], [74], [20] | CÓ ĐIỀU KIỆN | Khi có workflow giao dịch hoặc agent runtime nhiều bước cần theo dõi |
| D34, D35, D36 | [49], [70], [65] | CÓ ĐIỀU KIỆN | Khi chính sách tool/action phức tạp; không thay backend authorization hiện có |
| D37, D38, D39, D40 | [79], [36], [39], [38] | NGOÀI PHẠM VI | Cô lập môi trường/planner và thay kiến trúc agent vượt phạm vi hiện tại |

### 8.2. Benchmark và các attack tối ưu

| Nguồn / ref | Nhóm mới | Cách dùng |
|---|---|---|
| BIPIA [83] | CỐT LÕI | Cấu trúc đánh giá IPI; chuyển tình huống sang CSKH và ghi rõ dữ liệu đã điều chỉnh |
| OpenPI [47] | BỔ TRỢ | Tra formalization khi chưa rõ nhãn hoặc tiêu chí attack success |
| AgentDojo [21], InjecAgent [86], ASB [89] | CÓ ĐIỀU KIỆN | Chọn khi thực sự đánh giá tool calling/multi-step; không cần chạy cả ba |
| AGENTPI trong survey | CÓ ĐIỀU KIỆN | Đọc để hiểu tấn công context-dependent; các case tool/action chỉ dùng nếu khớp năng lực chatbot |
| PromptFuzz [84], Adaptive Attacks [85] | BỔ TRỢ | Nếu cần xây vòng sửa payload theo feedback; không bắt buộc dựng framework gốc |
| Gradient: [45], [28], [57], [64], [55], [90] | NGOÀI PHẠM VI | Chưa nghiên cứu tối ưu gradient/model internals hoặc poisoning retrieval bằng thuật toán gốc |
| Genetic: [88], [23], [44], [52] | NGOÀI PHẠM VI | Không dựng evolutionary search/tabular/search-ranking benchmark trong phạm vi CSKH này |
| Sampling: [77], [41] | NGOÀI PHẠM VI | Không huấn luyện attacker RL hay tối ưu MCMC |

Không cần đọc hết 96 mục bibliography: nhiều mục chỉ cung cấp nền tảng hoặc nói về hệ thống khác. Các ref không được chọn ở trên không tự động trở thành backlog nghiên cứu.

## 9. Những gì cần chốt khi khảo sát project

1. Backend tự truy vấn rồi đưa dữ liệu vào prompt hay LLM được tự gọi hàm? Cả hai đều có thể nghiên cứu IPI, nhưng chỉ trường hợp sau cần đánh giá lựa chọn tool.
2. Dữ liệu nào thực sự chứa nội dung do khách/nhà bán hàng nhập: review, mô tả sản phẩm, ghi chú đơn, nội dung ticket? Chọn một hoặc hai nguồn có thật; không giả định attacker sửa được bảng chính sách chính thức.
3. Nguồn chính sách nào đáng tin, ai được sửa? Sửa thẳng dữ liệu chuẩn và chỉ chèn chỉ dẫn vào một trường tự do là hai threat model khác nhau.
4. API trả những trường PII nào và tác vụ cần những trường nào? Xác định dữ liệu tối thiểu trước khi gọi LLM; detector LLM bên ngoài cũng là một điểm nhận dữ liệu.
5. Có render Markdown/image, URL preview, search hoặc HTTP fetch không? Nếu chưa có, H11/S03/ADD-02 chưa vào thực nghiệm chính. Link trong câu trả lời được chấm riêng với request thực sự gửi dữ liệu.
6. Ngôn ngữ nào được hỗ trợ? Nếu có tiếng Việt, phải có mẫu hợp lệ và attack tiếng Việt; không suy diễn hiệu quả từ benchmark tiếng Anh.

## 10. Bộ câu hỏi nghiên cứu và kiểm thử để giữ phạm vi gọn

**Câu hỏi chính:** Khi một nguồn văn bản phục vụ CSKH bị chèn chỉ dẫn, guardrails có giảm việc chatbot làm theo chỉ dẫn đó và yêu cầu/tiết lộ PII vượt chính sách, đồng thời vẫn hoàn thành tác vụ hợp lệ không?

Các gợi ý sau giúp chọn bài đọc; chưa phải implementation plan:

- Chọn một tác vụ đầu tiên, ví dụ hỏi trạng thái giao hàng kèm chính sách liên quan; chỉ dùng tác vụ tra đơn khi đã xác nhận API phù hợp.
- Chọn một hoặc hai điểm chèn có thật, chẳng hạn review hoặc ghi chú tự do trong response. Trường dữ liệu nghiệp vụ đã kiểm chứng vẫn cần được sử dụng đúng.
- Nhóm attack: giả thẩm quyền, ngụy trang nghiệp vụ, giả lịch sử/đồng ý; thêm một số biến thể diễn đạt/Unicode để kiểm tra né bộ lọc. Cách biểu diễn không phải một mục tiêu tấn công mới.
- Tách direct attack trong user message thành nhóm bổ sung; không mở rộng sang toàn bộ jailbreak/harmful-content benchmark.
- Có cặp context sạch/nhiễm và hard-benign. Văn bản hướng dẫn khách thao tác hợp lệ không mặc nhiên là injection; chỉ chứa dữ kiện sai cũng chưa đủ để gắn nhãn PI.
- Đo detector recall/FPR, ASR theo mục tiêu attacker, task success khi sạch và khi nhiễm, PII exposure theo từng điểm truyền/hiển thị/lưu, tỷ lệ yêu cầu PII không cần thiết và latency.
- Nếu đánh giá RAG end-to-end, ghi payload có được truy xuất không. Báo riêng tỷ lệ tới context và ASR có điều kiện trên context nhiễm; không ghi công cho guardrail khi retriever chưa lấy payload.
- Nếu thử API đơn hàng khác chủ sở hữu, ghi là kiểm tra authorization của backend; không gộp kết quả này vào thành tích detector PI.

## 11. Khoảng trống PII và giới hạn nguồn

Các paper được chọn chưa tạo thành nền tảng đầy đủ cho nhận diện tên người/địa chỉ tiếng Việt, span-level PII detection hoặc masking. Cần chọn bổ sung nguồn chuyên về PII sau khi biết schema và ngôn ngữ thật. Chưa đặt tên thư viện/model PII để tránh chọn trước nhu cầu dữ liệu.

Chỉ định phạm vi PII ban đầu ở vài trường có thật (ví dụ email, điện thoại, địa chỉ giao hàng); dùng dữ liệu tổng hợp cho benchmark. CCCD trong ví dụ solicitation là thông tin không nên yêu cầu cho tác vụ đó, không phải trường bắt buộc phải thêm vào database.

Phân loại dựa trên các hồ sơ của bản đồ nghiên cứu và thông tin ứng dụng trong cuộc trao đổi. Nguồn gốc của danh sách đọc chính đã được kiểm tra trên trang paper; không tuyên bố đã đọc lại toàn văn tất cả nguồn ADD/96 reference hoặc tái chạy benchmark. Hiệu quả báo cáo trong paper không phải hiệu quả đã xác nhận trên project thương mại điện tử.

Khi hoàn tất danh sách đọc chính và viết được threat model/test/baseline, chuyển sang khảo sát project và chốt thiết kế. Chỉ mở paper bổ trợ khi có một khoảng trống cụ thể cần giải quyết.
