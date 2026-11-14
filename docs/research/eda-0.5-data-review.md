# EDA 0.5 · Nhật ký sàng lọc dữ liệu FOX-Guardrails

Phạm vi là INPUT đa lĩnh vực cho Prompt Guard 2, nhãn 0/1 và cân bằng VI–EN.
EDA 0.5 quyết định giữ nguồn nào trước khi xây tập huấn luyện. TMĐT là một lát cắt.

Quy trình gồm tải theo revision, kiểm digest, chạy từng notebook rồi cập nhật nhật ký.
Số liệu tính theo dòng nguồn. Với hội thoại, đơn vị text là lượt người dùng.
Đối chiếu benchmark dùng các trường tham chiếu trong manifest EDA 01.

| Nguồn và notebook | Tình trạng | Dòng gốc | Text duy nhất | Lượt khớp benchmark¹ | Đề xuất |
|---|---|---:|---:|---:|---|
| [SecAI](../../notebooks/00_5_eda_data/00_5_secai.ipynb) | 2 lượt đọc | 1,388 | 1,388 | 1 | Giữ ứng viên INPUT |
| [VI–EN](../../notebooks/00_5_eda_data/00_5_vi_en.ipynb) | 2 lượt đọc | 1,000 | 989 | 0 | Giữ ứng viên INPUT |
| [GuardSpec](../../notebooks/00_5_eda_data/00_5_guardspec.ipynb) | 2 lượt đọc | 36,647 | 36,487 | 0 | Giữ một phần |
| [Aya Dataset](../../notebooks/00_5_eda_data/00_5_aya.ipynb) | 2 lượt đọc | 204,112 | 167,117 | 0 | Giữ một phần |
| [OpenAssistant OASST2](../../notebooks/00_5_eda_data/00_5_oasst2.ipynb) | 2 lượt đọc | 135,174 | 48,994 | 66 | Giữ một phần |
| [Prompt Safety Multilingual v2](../../notebooks/00_5_eda_data/00_5_nailyk.ipynb) | 6 lượt đọc | 1,329,536 | 1,291,394 | 1,302 | Tạm giữ để lọc |
| [ZN Prompt-Injection Bench](../../notebooks/00_5_eda_data/00_5_zn.ipynb) | 3 lượt đọc | 23,699 | 23,699 | 144 | Loại khỏi pilot |
| [Tensor Trust v2](../../notebooks/00_5_eda_data/00_5_tensor_trust.ipynb) | 2 lượt đọc | 681,726 | 344,885 | 2,714 | Tạm giữ |
| [WildJailbreak](../../notebooks/00_5_eda_data/00_5_wildjailbreak.ipynb) | 403 · chỉ metadata | 0 | 0 | — | Chờ quyền truy cập |
| [HackAPrompt](../../notebooks/00_5_eda_data/00_5_hackaprompt.ipynb) | 403 · chỉ metadata | 0 | 0 | — | Chờ quyền truy cập |
| [deepset Prompt Injections](../../notebooks/00_5_eda_data/00_5_deepset.ipynb) | 1 lượt đọc | 546 | 546 | 0 | Giữ một phần |
| [SPML](../../notebooks/00_5_eda_data/00_5_spml.ipynb) | 1 lượt đọc | 16,012 | 15,913 | 0 | Tạm giữ để rà |
| [Lakera Gandalf](../../notebooks/00_5_eda_data/00_5_gandalf.ipynb) | 1 lượt đọc | 777 | 776 | 0 | Tạm giữ |
| [Lakera Mosscap](../../notebooks/00_5_eda_data/00_5_mosscap.ipynb) | 1 lượt đọc | 223,533 | 171,249 | 170 | Tạm giữ |
| [jackhhao Jailbreak Classification](../../notebooks/00_5_eda_data/00_5_jackhhao.ipynb) | 1 lượt đọc | 1,044 | 1,031 | 0 | Giữ một phần |
| [TrustAIRLab In-the-Wild](../../notebooks/00_5_eda_data/00_5_trustairlab.ipynb) | 2 lượt đọc | 15,140 | 14,477 | 18 | Giữ một phần |
| [PIGuard](../../notebooks/00_5_eda_data/00_5_piguard.ipynb) | 1 lượt đọc | 76,735 | 73,489 | 276 | Tạm giữ để lọc |
| [Neuralchemy](../../notebooks/00_5_eda_data/00_5_neuralchemy.ipynb) | 1 lượt đọc | 4,391 | 4,389 | 130 | Tạm giữ để lọc |
| [5CD Hội thoại TMĐT](../../notebooks/00_5_eda_data/00_5_5cd.ipynb) | 1 lượt đọc | 1,482 | 8,934 | 0 | Tạm giữ cho TMĐT |
| [BKAI Vi-Alpaca](../../notebooks/00_5_eda_data/00_5_vi_alpaca.ipynb) | 1 lượt đọc | 50,006 | 50,006 | 0 | Tạm giữ, chờ quyền dùng |
| [VinAI PhoATIS](../../notebooks/00_5_eda_data/00_5_phoatis.ipynb) | 3 lượt đọc | 5,871 | 5,629 | 0 | Đánh giá nội bộ |
| [NVIDIA Aegis 2.0](../../notebooks/00_5_eda_data/00_5_aegis.ipynb) | 2 lượt đọc | 30,007 | 23,018 | 76 | Loại khỏi pilot INPUT |
| [BeaverTails](../../notebooks/00_5_eda_data/00_5_beavertails.ipynb) | 1 lượt đọc | 300,567 | 16,140 | 2,544 | Loại khỏi pilot INPUT |
| [NVIDIA Nemotron Agentic IPI](../../notebooks/00_5_eda_data/00_5_nemotron.ipynb) | 1 lượt đọc | 1,272 | 676 | 0 | Giữ cho CONTEXT |
| [LLMail Phase 1](../../notebooks/00_5_eda_data/00_5_llmail.ipynb) | 1 lượt đọc | 160,741 | 154,410 | 0 | Giữ cho CONTEXT |
| [InjecAgent](../../notebooks/00_5_eda_data/00_5_injecagent.ipynb) | 4 lượt đọc | 2,108 | 2,108 | 0 | Giữ làm benchmark |
| [BIPIA](../../notebooks/00_5_eda_data/00_5_benchmark_bipia.ipynb) | 2 lượt đọc | 750 | 708 | — | Giữ benchmark đã khóa |
| [JailbreakBench](../../notebooks/00_5_eda_data/00_5_benchmark_jbb.ipynb) | 1 lượt đọc | 486 | 486 | — | Giữ benchmark đã khóa |
| [CyberSecEval](../../notebooks/00_5_eda_data/00_5_benchmark_cyberseceval.ipynb) | 2 lượt đọc | 1,255 | 1,220 | — | Giữ benchmark đã khóa |
| [LLMail Phase 2](../../notebooks/00_5_eda_data/00_5_benchmark_llmail.ipynb) | 1 lượt đọc | 600 | 477 | — | Giữ benchmark đã khóa |
| [MultiJail](../../notebooks/00_5_eda_data/00_5_benchmark_multijail.ipynb) | 1 lượt đọc | 315 | 630 | — | Giữ benchmark đã khóa |
| [NotInject](../../notebooks/00_5_eda_data/00_5_benchmark_notinject.ipynb) | 3 lượt đọc | 339 | 339 | — | Giữ benchmark đã khóa |
| [OpenPII VI / C1](../../notebooks/00_5_eda_data/00_5_benchmark_openpii.ipynb) | 1 lượt đọc | 1,000 | 1,000 | — | Giữ benchmark đã khóa |

¹ Tổng lượt theo từng benchmark. Một dòng có thể khớp nhiều benchmark.

## Nhận xét từng nguồn

- **SecAI.** Cả hai lớp có nhãn injection nguồn. Giữ group skeleton và kiểm phần jailbreak. Intent và PII phục vụ tác vụ riêng.
  Khớp benchmark: LLMail Phase 2: 1.
- **VI–EN.** Có nhãn nhị phân và phần trộn VI–EN. Rà Refusal Bypass, source split và cụm template vì thiếu ID gốc. Train có 75 dòng gắn Mixed, gồm 53 INJECTION và 22 BENIGN. Giữ dòng Mixed phù hợp trước và bổ sung cả mẫu âm; không nhân bản để đủ chỉ tiêu.
- **GuardSpec.** Chọn direct và mẫu âm khó theo nhãn đã rà. Giữ license từng dòng, giới hạn biến thể và tách indirect sang CONTEXT. Train có 6.468 dòng VI gắn variant=orig. Trong đó 1.298 dòng có tag direct/jailbreak/prompt_extraction và không có indirect/tool_poisoning; 4.116 dòng chỉ có tag benign. Đây là số ứng viên theo tag, cần soát nhãn. Hai blob train/val tại HEAD c3fd2723983b7abc7fa9527f158f7606453768bd vẫn khớp bản đang có.
  Cặp split nhiều text trùng nhất (train / val) có 4 text và 0 ID nhóm trùng.
- **Aya Dataset.** Ưu tiên inputs VI/EN do người viết hoặc chỉnh sửa, chọn nguồn âm sau gán nhãn; targets và demographics ngoài phạm vi. Train có 8.676 dòng VI và 3.942 dòng EN theo language_code. Toàn nguồn có 503 nội dung trùng train/test. Ưu tiên phần VI đã rà nhãn và lọc trùng.
  Cặp split nhiều text trùng nhất (test / train) có 503 text và 0 ID nhóm trùng.
- **OpenAssistant OASST2.** Chọn prompter VI/EN đã duyệt, chưa xóa, không synthetic. Rà nhãn, giữ nhóm hội thoại và lọc phần trùng GuardSpec. Có 21.654 lượt train VI/EN qua bộ lọc prompter, đã review, chưa xóa và không synthetic. Chỉ 55 lượt VI. Trong tập con này có 30 dòng khớp văn bản LLMail Phase 2 và 514 nội dung trùng GuardSpec train.
  Khớp benchmark: LLMail Phase 2: 66.
  Cặp split nhiều text trùng nhất (train / validation) có 35 text và 0 ID nhóm trùng.
- **Prompt Safety Multilingual v2.** Có VI/EN và provenance theo dòng. Soát source_split, license thành phần, bản dịch, độ chính xác nhãn và dữ liệu chồng lặp trước khi giữ từng lát cắt. Tạm giữ ngoài pool chính. Trong 6.929 dòng VI ở train, 5.919 mang source_dataset Necent, 2.120 có translation_of_id và 90 khai báo source_split=test. Toàn nguồn có 1.302 lượt khớp benchmark. Chỉ xét lát cắt có lineage và quyền dùng rõ ràng.
  Khớp benchmark: JailbreakBench: 303, MultiJail: 565, BIPIA · test: 295, BIPIA · dev: 138, CyberSecEval EN: 1.
  Cặp split nhiều text trùng nhất (train / validation) có 39 text và 0 ID nhóm trùng.
- **ZN Prompt-Injection Bench.** Nhãn ataque chứa dòng lấy theo Aegis unsafe. Có thể khảo sát riêng hard-negative từ nguồn gốc, thay vì dùng nhãn cả tập. Thêm 1.729 dòng ataque từ Aegis và 2.794 dòng ataque từ InjecAgent trong split train. Tên lớp không đủ để suy ra tương thích với FOX INPUT. Bỏ khỏi pilot; chỉ cân nhắc lấy mẫu âm từ nguồn gốc.
  Khớp benchmark: MultiJail: 43, JailbreakBench: 100, BIPIA · dev: 1.
- **Tensor Trust v2.** Corpus game do người chơi tạo. Outcome thắng/thua không đo nhãn attack; thống kê tách attacks và defenses. Cần làm rõ điều khoản áp dụng tới raw dump. Raw v2 có 563.349 lượt attack và 118.377 defense. 561.771 lượt attack có text, rút còn 271.348 nội dung khác nhau sau chuẩn hóa. Quyền dùng raw chưa rõ; bản dump chốt 2024-02-16 nên chỉ phù hợp khảo sát bổ sung.
  Khớp benchmark: LLMail Phase 2: 2,700, CyberSecEval EN: 14.
  Cặp split nhiều text trùng nhất (attacks / defenses) có 546 text và 34,972 ID nhóm trùng.
- **WildJailbreak.** Tệp TSV trả 403. Khi có dữ liệu, xem text adversarial, tactics và nhóm vanilla, gán lại nhãn phù hợp FOX.
- **HackAPrompt.** Tệp Parquet trả 403. Khi có dữ liệu, phân biệt user_input với full prompt và kết quả correct.
- **deepset Prompt Injections.** Có text/label nhưng corpus nhỏ và xuất hiện ở nguồn gộp. Chọn nguồn gốc một lần và rà ca đổi tác vụ hợp lệ.
- **SPML.** Nhãn phụ thuộc cặp system và user. Chọn ca có dấu hiệu rõ khi chỉ nhìn user; Degree đo vi phạm quy tắc nguồn.
- **Lakera Gandalf.** Nguồn game dương tiềm năng nhưng thiếu lớp âm và nhãn theo dòng. Đã nằm trong GuardSpec; dùng nguồn gốc một lần.
- **Lakera Mosscap.** Nhiều lượt chơi trong cùng khuôn. Level là cấp chơi; response và kết quả thử không dùng làm nhãn INPUT.
  Khớp benchmark: LLMail Phase 2: 111, CyberSecEval EN: 57, BIPIA · dev: 1, JailbreakBench: 1.
- **jackhhao Jailbreak Classification.** Có jailbreak/benign. Truy upstream và chỉ giữ một bản khi đã có hàng tương ứng ở PIGuard hoặc GuardSpec. Trùng 1.031 nội dung với PIGuard train và 748 với GuardSpec train. Ưu tiên truy về bản upstream và tính mỗi họ prompt một lần.
- **TrustAIRLab In-the-Wild.** Có hai tập regular/jailbreak từ thực tế. Chia và rà họ prompt, loại PII thật nếu xác nhận; đối chiếu phần gốc của jackhhao. Trùng 11.466 nội dung với lát cắt VI/EN ở Nailyk train. Có 18 lượt khớp LLMail Phase 2 trong hai subset cục bộ.
  Khớp benchmark: LLMail Phase 2: 18.
  Cặp split nhiều text trùng nhất (jailbreak_2023_12_25 / regular_2023_12_25) có 42 text và 0 ID nhóm trùng.
- **PIGuard.** Kiểm theo upstream source; cách ly thành phần BIPIA, InjecAgent và các nguồn đã có. Kiểm license từng nguồn và cả lớp âm khó. Có 276 lượt khớp BIPIA dev/test và MultiJail toàn nguồn, cùng 1.031 nội dung trùng với jackhhao và 546 nội dung trùng với deepset trên các bản train cục bộ.
  Khớp benchmark: BIPIA · dev: 211, BIPIA · test: 31, MultiJail: 34.
- **Neuralchemy.** Có group_id và provenance nhưng là nguồn gộp. Kiểm quyền từng thành phần; giới hạn biến thể cùng mẫu gốc. Có 130 lượt khớp JailbreakBench. So với lát cắt VI/EN của train Nailyk có 3.674 nội dung trùng. Giữ bên staging để đối chiếu nguồn gốc.
  Khớp benchmark: JailbreakBench: 130.
- **5CD Hội thoại TMĐT.** Đơn vị ứng viên là lượt human/user. Cần làm rõ provenance và gán nhãn; chỉ bổ sung lát cắt TMĐT.
- **BKAI Vi-Alpaca.** Giữ instruction với input để rà. Chưa có nhãn injection và chưa xác minh quyền dùng bản phát hành cho fine-tune.
- **VinAI PhoATIS.** Chỉ nghiên cứu/giáo dục, hạn chế phân phối. Gán lại nhãn cho lát cắt âm du lịch rồi đo nội bộ.
  Cặp split nhiều text trùng nhất (train / dev) có 13 text và 0 ID nhóm trùng.
- **NVIDIA Aegis 2.0.** Nhãn prompt/response là safety, phù hợp OUTPUT/moderation. Tách yêu cầu unsafe thông thường khỏi hành vi prompt attack.
  Khớp benchmark: MultiJail: 73, LLMail Phase 2: 3.
  Cặp split nhiều text trùng nhất (train / refusals_train) có 3,361 text và 0 ID nhóm trùng.
- **BeaverTails.** Nhãn là safety theo cặp prompt/response; xem riêng khi làm OUTPUT.
  Khớp benchmark: MultiJail: 2,544.
- **NVIDIA Nemotron Agentic IPI.** Payload gắn với environment và target tool. Chọn cho CONTEXT khi phân biệt được dữ liệu ngoài với user input.
- **LLMail Phase 1.** Đây là lượt tấn công trong email. Phân biệt outcome challenge với nhãn injection, lọc theo benchmark Phase 2.
- **InjecAgent.** Các tệp là test cases và biến thể base/enhanced. Tách khỏi pilot huấn luyện để giữ giá trị kiểm thử.
- **BIPIA.** Bản chuẩn hóa FOX của BIPIA dev/test. Giữ benchmark gián tiếp; hai split này nằm trong danh sách đối chiếu.
  Cặp split nhiều text trùng nhất (dev / test) có 11 text và 0 ID nhóm trùng.
- **JailbreakBench.** Phân biệt các loại nhãn gốc và outcome jailbroken. Giữ bản chuẩn hóa FOX làm test chính cho INPUT tiếng Anh.
- **CyberSecEval.** Giữ nguyên benchmark. Bản đa ngôn ngữ là bản dịch, cần tính chung họ prompt_id nếu so tiếng Anh và tiếng Việt.
  Cặp split nhiều text trùng nhất (english / multilingual) có 8 text và 0 ID nhóm trùng.
- **LLMail Phase 2.** Giữ mẫu Phase 2 làm benchmark email. Chủ đề hoặc phần thân trùng riêng được ghi nhận ở phép đối chiếu nguồn ngoài.
- **MultiJail.** Giữ đánh giá an toàn đa ngôn ngữ. Một dòng chứa các bản dịch của cùng seed; không coi nội dung có hại đơn thuần là injection.
- **NotInject.** Giữ để đo gắn cờ nhầm trên hard negatives. Các cấu hình phân theo số từ kích hoạt.
- **OpenPII VI / C1.** Bản chuẩn hóa FOX của OpenPII. Giữ cho đánh giá PII; nhãn PII khác nhãn injection.

Xem [manifest tải](../../notebooks/00_5_eda_data/downloads.json) và [quy tắc đọc từng nguồn](../../notebooks/00_5_eda_data/sources.json).

## Quyết định sau đối chiếu

| Vai trò | Nguồn ưu tiên | Công việc còn lại |
|---|---|---|
| INPUT có nhãn cho vòng đầu | SecAI, VI–EN, phần direct và âm khó của GuardSpec | Rà nhãn theo định nghĩa FOX, chống trùng theo họ và kiểm phân bố theo ngôn ngữ |
| Câu tự nhiên đa lĩnh vực | Aya cho VI/EN, OASST2 chủ yếu cho EN | Duyệt nhãn, bỏ trùng và tách theo nhóm hội thoại của OASST2 |
| Attack EN và câu đối chứng | TrustAIRLab, deepset hoặc jackhhao theo từng nguồn gốc | Dùng một bản đại diện, giới hạn họ prompt nguồn game và nhập vai |
| Nguồn bổ sung cần rà sâu | Tensor Trust, PIGuard, Neuralchemy, Nailyk, SPML, Gandalf, Mosscap | Chọn lát cắt có nhãn tương thích, nguồn gốc truy được và đủ quyền dùng |
| Để ngoài pilot INPUT | ZN, Aegis, BeaverTails, Vi-Alpaca chưa rõ quyền | Giữ hồ sơ và raw trong staging. Aegis và BeaverTails có thể xét khi làm moderation/OUTPUT |
| Các phép đo và trạm khác | InjecAgent và benchmark đã khóa, LLMail, Nemotron, PhoATIS, 5CD | Giữ theo vai trò ghi ở từng notebook |
| Cần quyền tải Hugging Face | WildJailbreak, HackAPrompt | Đăng nhập và chấp nhận điều kiện của từng trang nguồn, rồi tải lại đúng revision trong manifest |

Trong bản phân tích INPUT, số lượng tính được hiện là tầng ứng viên. Không dùng số raw để khẳng định
đã đủ 40.000 mẫu. Aya và OASST2 chưa có nhãn injection. VI–EN chỉ có 75 dòng Mixed ở split train,
vì vậy cần kiểm lại độ phủ mẫu trộn trước khi chốt tỷ lệ.

Các khớp benchmark được tính trên text sau chuẩn hóa. Chúng có thể là nội dung ngắn như chủ đề email,
không tự chứng minh hai tình huống là cùng một cuộc tấn công. Khi đưa vào train, rà nguồn gốc,
so lại payload/template và xử lý xung đột nhãn. Chưa đo near-duplicate, paraphrase hay dịch qua ngôn ngữ.
Các đếm giao nhau giữa nguồn dùng text duy nhất của split train gốc, với Aya/OASST2/Nailyk lọc sơ bộ VI/EN
và OASST2 thêm các cờ prompter/reviewed/chưa xóa/không synthetic.

Ưu tiên bản mới nhất theo **tệp dữ liệu**, đồng thời xét độ đa dạng và độ tin cậy. SecAI, VI–EN và
Neuralchemy đang ở revision công bố hiện tại khi kiểm. GuardSpec có commit mới hơn nhưng hai blob
train/val vẫn giống bản đã tải. Bản mới hơn của một bộ gộp không làm cho các mẫu upstream độc lập hơn.

Tải mới lưu ở `data/raw/eda05/`. Các đường dẫn `data/raw/eda01/`, `data/raw/eda01_vi/` và các thư mục
benchmark còn được EDA 01 và repo tham chiếu. Giữ các đường dẫn này trong vòng sàng lọc để notebook cũ
và các phép đo vẫn chạy được.

Chạy lại một notebook từ thư mục repo bằng `python notebooks/00_5_eda_data/run_eda05.py <id_nguồn>`.
Chạy không đối số để thực hiện lần lượt tất cả nguồn trong manifest. Cần Jupyter kernel `python3`,
`nbformat`, `nbclient`, `pandas`, `pyarrow` và các phụ thuộc của EDA 01.
