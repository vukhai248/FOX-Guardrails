## Slide 1. AI GUARDRAILS

Phòng chống Prompt Injection

****

Khảo sát các nhóm tấn công, cơ chế phòng thủ và hướng thực hiện đồ án.
Bản trình bày chi tiết để đọc và trao đổi với giảng viên.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 2. Phạm vi đề tài

AI Guardrails và phần nhóm tập trung

**AI Guardrails**

Lớp kiểm tra và thực thi chính sách quanh ứng dụng LLM. Guardrails có thể xử lý nội dung không an toàn, lệch chủ đề, dữ liệu nhạy cảm, định dạng đầu ra và chỉ dẫn chèn. Đây là các bài toán có tiêu chí đánh giá khác nhau.

**Trọng tâm của nhóm**

Phòng chống Prompt Injection: phát hiện chỉ dẫn đến từ nguồn không đáng tin, giảm khả năng LLM làm theo và kiểm tra hành vi đầu ra. Bảo vệ PII là lớp hỗ trợ khi tấn công hướng tới thông tin cá nhân.

**Mức đề xuất hiện tại**

Trình bày phương pháp và cách kiểm chứng, chưa chọn model hoặc thuật toán triển khai cụ thể. Môi trường minh họa là ứng dụng LLM tổng quát, không phụ thuộc một website có sẵn.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 3. Tài liệu khảo sát và số lượng

Các tập tài liệu cần phân biệt

**Survey nền**

The Landscape of Prompt Injection Threats in LLM Agents, arXiv:2602.10453v1. Tác giả báo cáo 78 công trình: 37 về tấn công và 41 về phòng thủ, khóa tìm kiếm ngày 20/10/2025.

**Hai nhóm tạo tấn công**

Heuristic-based: 23 bài. Optimization-based: 14 bài. Đây là phân loại theo cách tạo payload, không phải hai nhóm duy nhất của toàn bộ lĩnh vực guardrails.

**Phần bổ sung trong file nghiên cứu**

14 hồ sơ ADD năm 2026 nằm ngoài tập gốc. D01–D40 là mã phương pháp phòng thủ của tài liệu. 96 mục bibliography còn bao gồm benchmark và nguồn nền tảng, không phải 96 phương pháp riêng.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 4. Cấu trúc hai nhóm tấn công

Theo Table 1 của survey

**Nhóm 1: heuristic-based, 23 bài**

Manual template: 16 bài H01–H16. LLM generation: 3 bài G01–G03. Structural encoding: 4 bài S01–S04. Các slide sau trình bày riêng từng bài, hai trang cho mỗi hồ sơ.

**Nhóm 2: optimization-based, 14 bài**

Gradient: 6 bài. Genetic/evolutionary và tìm kiếm dựa phản hồi: 6 bài. Sampling: 2 bài. Mỗi bài có slide riêng về nguyên lý, điều kiện tiếp cận và giới hạn.

**Cách hiểu nhãn của survey**

Một bài có thể kết hợp nhiều kỹ thuật. Ví dụ một hồ sơ template vẫn có bước tìm kiếm thích nghi. G03 được xếp ở nhóm attack nhưng đóng góp chính là phòng thủ bộ chấm.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 5. Prompt Injection hoạt động như thế nào?

Dữ liệu thấp quyền bị hiểu thành chỉ dẫn

**Nhiệm vụ hợp lệ**

Người dùng giao một nhiệm vụ. Ứng dụng nạp thêm tài liệu, trang web, kết quả truy xuất hoặc phản hồi công cụ để LLM có dữ kiện xử lý.

**Điểm attacker can thiệp**

Attacker sửa một nguồn mà LLM sẽ đọc và lồng chỉ dẫn: đổi nhiệm vụ, giả quyền ưu tiên, sửa tiêu chí chấm, xin thêm dữ liệu hoặc gửi dữ liệu ra ngoài. Attacker không nhất thiết sửa được system prompt.

**Điểm thất bại**

LLM coi nội dung ngoài là thẩm quyền điều khiển. Câu trả lời hoặc hành động vì thế phục vụ mục tiêu attacker thay cho mục tiêu được ủy quyền. Có từ khóa đáng ngờ chưa đủ chứng minh tấn công thành công.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 6. Các chiều phân loại chéo

Không cộng các chiều này thành số paper mới

**Đường vào và quyền attacker**

Direct: qua đầu vào trực tiếp. Indirect: qua tài liệu, web, memory hoặc tool result. Supply-chain: tác động nguồn RAG hay dữ liệu huấn luyện theo threat model. Quyền có thể là black-box hoặc truy cập nội bộ mạnh hơn.

**Mục tiêu bảo mật**

Integrity: sửa đáp án, điểm, kế hoạch hoặc hành động. Confidentiality: tiết lộ dữ liệu hoặc truyền sai đích. Availability: làm gián đoạn nhiệm vụ hoặc suy luận. Một payload có thể gây nhiều hậu quả.

**Khả năng nhìn thấy**

Payload có thể hiện rõ, hòa vào ngữ cảnh, mã hóa, ẩn qua định dạng hoặc nằm trong ảnh. Hiệu quả phụ thuộc thứ pipeline thực sự đưa vào LLM, không chỉ thứ con người nhìn thấy.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 7. Cách đọc slide của từng paper

Cơ chế, bằng chứng và đề xuất được ghi riêng

**Trang cơ chế**

Nêu quyền attacker, nguồn bị kiểm soát, cách chỉ dẫn chuyển thành tác động và mục tiêu cần quan sát. Đây là điều kiện để hiểu paper có phù hợp một hệ thống cụ thể hay không.

**Trang phòng thủ và kiểm chứng**

Ghi phòng thủ đã được paper thử hoặc nêu rõ paper chưa đánh giá phòng thủ đầy đủ. Phần “dấu hiệu đề xuất” là gợi ý xây ca kiểm thử, chưa phải detector có độ chính xác được xác nhận.

**Nguồn và giới hạn**

Mỗi slide có mã H/G/S hoặc D/ADD, ref của survey và liên kết nguồn. Nội dung diễn giải dựa trên file research. Kết quả của tác giả không phải kết quả nhóm đã tái lập.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 8. AI²: điều hướng hành động

H01 · Ref [91] · Manual template · 1/2

**Nguồn và quyền attacker**

Attacker đầu độc tri thức mà ứng dụng dùng để lập kế hoạch. Họ không cần kiểm soát system prompt, nhưng cần đặt nội dung vào nguồn ứng dụng sẽ đọc.

**Cơ chế tấn công**

Khai thác tri thức liên quan hành động, tạo ứng viên payload rồi ghép với câu hỏi mục tiêu. Nội dung giả có thể khiến LLM chọn kế hoạch hoặc hành động attacker mong muốn.

**Đích quan sát**

Đo action hijacking trong các ứng dụng dùng tri thức để quyết định. Survey xếp manual template, dù công trình có bước chọn/tối ưu ứng viên. Kế hoạch sai chưa đồng nghĩa hành động đã thực thi.

Nguồn: https://arxiv.org/abs/2412.10807

---

## Slide 9. AI²: điều hướng hành động

H01 · Ref [91] · Manual template · 2/2

**Phòng thủ được khảo sát**

Paper kiểm tra khả năng vượt các lớp như luật, bộ phân loại an toàn và viết lại bằng LLM. Các lớp này là đối tượng stress test, không phải bảo đảm ngăn mọi payload.

**Dấu hiệu đề xuất**

So sánh hành động được đề xuất với nhiệm vụ gốc và nguồn bằng chứng. Đánh dấu khi một đoạn dữ kiện tự nhận quyền thay đổi quy trình hoặc yêu cầu hành động không được người dùng ủy quyền.

**Giới hạn và bài học**

Cần log kế hoạch, lời gọi công cụ và kết quả thực thi riêng. Lọc nội dung nguy hiểm và kiểm tra hành động phục vụ mục tiêu là hai lớp bổ trợ, không thể thay nhau.

Nguồn: https://arxiv.org/abs/2412.10807

---

## Slide 10. MAD-Spear: đồng thuận giả

H02 · Ref [17] · Manual template · 1/2

**Nguồn và quyền attacker**

Nạn nhân là hệ multi-agent debate. Attacker tác động một thành viên hoặc thông điệp mà các thành viên khác sẽ nhận trong quá trình thảo luận.

**Cơ chế tấn công**

Payload khai thác xu hướng tuân theo số đông và thẩm quyền trong tranh luận. Một ý kiến giả có thể tạo cảm giác đã có đồng thuận rồi kéo các agent còn lại theo đáp án hoặc lập luận sai.

**Đích quan sát**

Paper thử trên các tác vụ lập luận và đánh giá sự lan truyền ảnh hưởng giữa agent. Cần theo dõi ai đưa ra chỉ dẫn đầu tiên và kết luận thay đổi sau từng vòng.

Nguồn: https://arxiv.org/abs/2507.13038

---

## Slide 11. MAD-Spear: đồng thuận giả

H02 · Ref [17] · Manual template · 2/2

**Phòng thủ trong hồ sơ**

Hồ sơ không mô tả một bộ phòng thủ hoàn chỉnh được so sánh hệ thống. Không suy ra nhiều agent tự động an toàn hơn một agent.

**Dấu hiệu đề xuất**

Thông điệp viện dẫn “mọi thành viên đã đồng ý”, yêu cầu bỏ bằng chứng hoặc đổi mục tiêu. Đối chiếu nguồn và bằng chứng độc lập thay vì coi số lần lặp cùng ý là độ tin cậy.

**Giới hạn và bài học**

Threat model đòi hỏi nhiều agent trao đổi. Chỉ áp dụng cơ chế này khi có luồng giao tiếp tương ứng. Phòng thủ đề xuất là lưu provenance và giới hạn quyền của thông điệp giữa agent.

Nguồn: https://arxiv.org/abs/2507.13038

---

## Slide 12. Prompt Infection: lây qua hội thoại

H03 · Ref [37] · Manual template · 1/2

**Nguồn và quyền attacker**

Attacker đặt payload vào thông điệp hoặc bộ nhớ một agent có thể đọc. Các agent tiếp tục giao tiếp nên chỉ dẫn có thể xuất hiện lại trong nguồn của agent khác.

**Cơ chế tấn công**

Payload yêu cầu lặp lại hoặc lan truyền chỉ dẫn, có thể giả thông tin quan trọng cần lưu memory. Tóm tắt và chuyển tiếp làm nội dung thấp quyền tiếp tục tác động các vòng sau.

**Đích quan sát**

Theo dõi mức nhiễm qua số agent và số lượt trao đổi, không chỉ một câu trả lời. “Infection” ở đây là lan truyền nội dung điều khiển, không phải worm ở hệ điều hành.

Nguồn: https://arxiv.org/abs/2410.07283

---

## Slide 13. Prompt Infection: lây qua hội thoại

H03 · Ref [37] · Manual template · 2/2

**Phòng thủ đã thử**

Hồ sơ ghi nhận gắn dấu nguồn, gắn nhãn bằng LLM và chỉ dẫn phòng thủ. Một tổ hợp đạt ASR bằng 0 trong thiết lập của tác giả, chưa chứng minh chống mọi payload thích nghi.

**Dấu hiệu đề xuất**

Cùng chỉ dẫn xuất hiện qua nhiều agent, tự yêu cầu giữ lâu trong memory hoặc tự nâng mức quan trọng. Lưu nguồn gốc qua cả bước tóm tắt, không xóa nhãn khi chuyển tiếp.

**Giới hạn và bài học**

Bộ lọc một lần ở đầu vào có thể bỏ sót nội dung được tái tạo sau đó. Nếu hệ có memory hoặc nhiều agent, cần kiểm tra lại tại ranh giới truyền và ghi bộ nhớ.

Nguồn: https://arxiv.org/abs/2410.07283

---

## Slide 14. Simple PI: rò dữ liệu qua công cụ

H04 · Ref [2] · Manual template · 1/2

**Nguồn và quyền attacker**

Agent được ủy quyền xem PII giả lập để làm nhiệm vụ. Attacker chỉ sửa một phần tool observation, không giả định đã biết dữ liệu cá nhân có trong context của agent.

**Cơ chế tấn công**

Chèn thông báo ưu tiên, yêu cầu TODO hoặc chỉ dẫn tự nhiên vào phản hồi công cụ. Agent có thể dùng quyền đọc dữ liệu của mình để gửi thông tin qua công cụ email đến đích attacker.

**Đích quan sát**

Paper dùng kịch bản banking của AgentDojo và PII tổng hợp. Thành công phải dựa trên dữ liệu thực sự đi qua thao tác gửi, đồng thời đo nhiệm vụ hợp lệ còn hoàn tất hay không.

Nguồn: https://arxiv.org/abs/2506.01055

---

## Slide 15. Simple PI: rò dữ liệu qua công cụ

H04 · Ref [2] · Manual template · 2/2

**Phòng thủ đã thử**

Nhắc lại yêu cầu user, detector, lọc tool và delimiters. Một cấu hình chặn mạnh giảm ASR nhưng cũng giảm utility đáng kể. Vì vậy mức chặn cao chưa đủ chứng minh một defense tốt.

**Dấu hiệu đề xuất**

Tool result yêu cầu gửi thông tin, đổi người nhận hoặc tự nhận quyền của user. Kiểm tra dữ liệu trong tham số tool và đích gửi trước thực thi, không chỉ dò PII trong câu trả lời cuối.

**Giới hạn và bài học**

Tách PII có trong context, PII gửi tới dịch vụ LLM và PII gửi tới đích trái phép. Một hệ chỉ trả lời văn bản không tự có khả năng gửi email như threat model của paper.

Nguồn: https://arxiv.org/abs/2506.01055

---

## Slide 16. Breaking the Prompt Wall: chỉ dẫn nhẹ

H05 · Ref [3] · Manual template · 1/2

**Nguồn và quyền attacker**

Paper phân tích các tình huống ứng dụng ChatGPT và nội dung có thể ảnh hưởng đánh giá hoặc khuyến nghị. Attacker chèn được thông điệp mà hệ sẽ xử lý trong bối cảnh tác vụ.

**Cơ chế tấn công**

Đoạn chỉ dẫn ngắn và tự nhiên hòa với nội dung hợp lệ, khiến mô hình ưu ái một lựa chọn, đổi nhận định hoặc đưa gợi ý thiên lệch. Payload có thể không chứa câu “ignore previous instructions”.

**Đích quan sát**

Đây là các case study hành vi, không phải benchmark lớn có train/test và ASR thống nhất. Cần lưu đầu vào sạch và đầu vào chèn để phân biệt tác động với thiên lệch vốn có của model.

Nguồn: https://arxiv.org/abs/2504.16125

---

## Slide 17. Breaking the Prompt Wall: chỉ dẫn nhẹ

H05 · Ref [3] · Manual template · 2/2

**Phòng thủ trong hồ sơ**

Paper không cung cấp thí nghiệm phòng thủ đối chứng đầy đủ. Không nên dùng kết quả case study như bằng chứng một classifier cụ thể có thể phát hiện được loại này.

**Dấu hiệu đề xuất**

Nội dung nguồn yêu cầu người trả lời phải ca ngợi, ưu tiên hoặc khuyến nghị ngoài mục tiêu. Đối chiếu chỉ dẫn với vai trò nguồn và câu hỏi thật, thay vì chặn theo một cụm từ cố định.

**Giới hạn và bài học**

Dịch vụ thay đổi phiên bản nên tái lập có thể khác. Bộ test cần cả nội dung quảng bá lành và nội dung ra lệnh cho chatbot để đo khả năng phân biệt ngữ cảnh.

Nguồn: https://arxiv.org/abs/2504.16125

---

## Slide 18. Mantis: bẫy agent kiểm thử bảo mật

H06 · Ref [56] · Manual template · 1/2

**Nguồn và quyền attacker**

Nạn nhân là agent tấn công/kiểm thử bảo mật. Bên bảo vệ kiểm soát dịch vụ, log hoặc honeypot mà agent đó sẽ thăm dò và đọc qua công cụ.

**Cơ chế tấn công**

Đưa chỉ dẫn gây lệch vào phản hồi môi trường để agent bỏ mục tiêu hoặc thực hiện thao tác do bên bảo vệ mong muốn. Paper dùng Prompt Injection như một cơ chế phòng vệ chủ động trước agent.

**Đích quan sát**

Thử nghiệm gắn với các agent pentest và bài toán CTF. Tỷ lệ phòng vệ tác giả báo cáo mô tả khả năng làm lệch agent tấn công, không phải accuracy của detector Prompt Injection.

Nguồn: https://arxiv.org/abs/2410.20911

---

## Slide 19. Mantis: bẫy agent kiểm thử bảo mật

H06 · Ref [56] · Manual template · 2/2

**Phòng thủ và phạm vi**

Đóng góp là dùng injection để đối phó agent, không phải bộ guardrails bảo vệ hội thoại. Không chuyển nguyên mô hình “phản công” này thành chức năng của đồ án.

**Dấu hiệu đề xuất**

Banner, log hay phản hồi server bắt đầu ra lệnh thay vì cung cấp dữ kiện. Agent cần coi cả kết quả công cụ bảo mật là dữ liệu không đáng tin và kiểm tra thao tác độc lập.

**Giới hạn và bài học**

Quyền terminal và môi trường pentest là điều kiện quan trọng. Bài học tổng quát là kết quả tool không được tự cấp quyền thực thi, dù có vẻ xuất phát từ hệ thống kỹ thuật.

Nguồn: https://arxiv.org/abs/2410.20911

---

## Slide 20. Oncology: injection trong đầu vào đa phương thức

H07 · Ref [12] · Manual template · 1/2

**Nguồn và quyền attacker**

Mô hình hỗ trợ tác vụ y khoa nhận hình ảnh hoặc tài liệu. Attacker sửa được đầu vào có chỉ dẫn nhưng không kiểm soát quy tắc chính của hệ thống.

**Cơ chế tấn công**

Lồng thông điệp điều khiển vào dữ liệu đa phương thức để thay đổi nhận định. Mô hình có thể coi phần chữ trong ảnh hoặc tài liệu là yêu cầu phải làm theo thay vì thông tin cần phân tích.

**Đích quan sát**

Paper nghiên cứu các ca/hình ảnh trong oncology với nhiều hệ đa phương thức. Cần đo sai lệch kết luận dưới điều kiện tấn công và đối chứng sạch, không gọi mọi sai sót y khoa là injection.

Nguồn: https://arxiv.org/abs/2407.18981

---

## Slide 21. Oncology: injection trong đầu vào đa phương thức

H07 · Ref [12] · Manual template · 2/2

**Phòng thủ trong hồ sơ**

Trọng tâm là nghiên cứu tấn công. Hồ sơ không chứng minh một pipeline phòng thủ đa phương thức hoàn chỉnh. Không suy ra bộ lọc văn bản có thể bao phủ mọi tín hiệu hình ảnh.

**Dấu hiệu đề xuất**

Có câu ra lệnh cho người đánh giá trong vùng hình ảnh hoặc nội dung mô tả. Có thể đối chiếu chữ nhận dạng và tác vụ hợp lệ, nhưng đây là hướng kiểm tra cần đánh giá riêng.

**Giới hạn và bài học**

OCR có thể bỏ sót hoặc tự tạo lỗi. Nếu đồ án chỉ làm text thì giữ bài này ở Related Work, không tuyên bố đã bảo vệ dữ liệu hình ảnh.

Nguồn: https://arxiv.org/abs/2407.18981

---

## Slide 22. Preemptive Answer: neo vào đáp án sớm

H08 · Ref [81] · Manual template · 1/2

**Nguồn và quyền attacker**

Attacker đưa nội dung xuất hiện trước hoặc trong quá trình giải tác vụ lập luận. Mục tiêu là khiến nạn nhân dựa vào một đáp án được gợi sẵn.

**Cơ chế tấn công**

Cài câu trả lời hoặc lời kết luận trước khi mô hình tự hoàn thành lời giải. Hiệu ứng neo có thể làm mô hình hợp thức hóa đáp án sai hoặc rút ngắn quá trình suy luận cần thiết.

**Đích quan sát**

Các bài toán toán học, suy luận và QA. Survey liên hệ với CoT DoS, nhưng không phải mọi trường hợp đều dừng dịch vụ. Chấm cả độ đúng và việc hoàn tất nhiệm vụ.

Nguồn: https://arxiv.org/abs/2405.20902

---

## Slide 23. Preemptive Answer: neo vào đáp án sớm

H08 · Ref [81] · Manual template · 2/2

**Phòng thủ đã khảo sát**

Paper nghiên cứu các can thiệp như diễn đạt lại đề bài và self-reflection. Hiệu quả phụ thuộc thiết lập, không phải biện pháp tổng quát bảo đảm suy luận đúng.

**Dấu hiệu đề xuất**

Dữ liệu ngoài tự khẳng định đáp án cuối và yêu cầu bỏ kiểm chứng. Kiểm tra xem kết luận có được bằng chứng độc lập hỗ trợ hay chỉ lặp nội dung được đưa sẵn.

**Giới hạn và bài học**

Một dữ kiện sai có thể làm đáp án sai mà không phải PI. Bộ test phải phân biệt answer contamination, misinformation và chỉ dẫn điều khiển cách giải.

Nguồn: https://arxiv.org/abs/2405.20902

---

## Slide 24. Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks

H09 · Ref [68] · Manual template · 1/4

**Threat model**

LLM được giao dịch một đoạn văn bản; đối thủ kiểm soát đoạn nguồn cần dịch (dữ liệu) và cấy một lệnh khiến mô hình trả lời nội dung thay vì dịch. Đây là ví dụ rõ ràng về tấn công vượt ranh giới instruction vs input data.

**Cách tấn công**

Tác giả biến câu hỏi TruthfulQA thành văn bản cần dịch; thêm tiền tố kiểu "đừng dịch câu này, hãy trả lời câu hỏi" bằng tiếng Anh hoặc ngôn ngữ nguồn. Mô hình thành công ở tác vụ hợp lệ nếu tiếp tục *dịch* dù câu văn được dịch là câu hỏi/mệnh lệnh.

Nguồn: https://arxiv.org/abs/2403.09832

---

## Slide 25. Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks

H09 · Ref [68] · Manual template · 2/4

**Benchmark**

817 câu hỏi gốc từ TruthfulQA được dịch sang Đức, Pháp, Romania, Nga; sau lọc chất lượng tạo cặp ngôn ngữ En–De/Fr/Ro/Ru. Thử T5, FLAN-T5, GPT-3, InstructGPT, Llama2 và Llama2-chat ở nhiều kích thước; so sánh zero-shot và one-shot. Tác giả cho thấy BLEU một mình không đủ để đánh giá: một câu trả lời đúng chủ đề nhưng không phải bản dịch có thể đạt BLEU cao hơn bản dịch hợp lệ.

Nguồn: https://arxiv.org/abs/2403.09832

---

## Slide 26. Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks

H09 · Ref [68] · Manual template · 3/4

**Benchmark (tiếp)**

Vì vậy có thêm tiêu chí xem model *dịch* hay *trả lời* câu hỏi.

**Defense/giảm thiểu có đánh giá**

Bổ sung một ví dụ dịch (one-shot in-context example) có thể đảo ngược hiện tượng inverse scaling ở một số cấu hình Llama2; tác giả không xây một guardrail detector độc lập.

**Hạn chế/kết luận**

Mô hình lớn hơn đôi khi dễ mắc hơn khi zero-shot (inverse scaling), nhưng không phải trên mọi họ model/cấu hình.

Nguồn: https://arxiv.org/abs/2403.09832

---

## Slide 27. Scaling Behavior of Machine Translation with Large Language Models under Prompt Injection Attacks

H09 · Ref [68] · Manual template · 4/4

**Dấu hiệu đề xuất kiểm tra**

Văn bản cần dịch chuyển sang yêu cầu trả lời câu hỏi hoặc bỏ bước dịch. Chấm loại nhiệm vụ thực hiện, không chỉ độ giống bản dịch. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2403.09832

---

## Slide 28. “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors (AIShellJack)

H10 · Ref [46] · Manual template · 1/3

**Threat model**

Coding Agent có quyền đọc repo và gọi công cụ terminal/editor; attacker kiểm soát file hướng dẫn hoặc nội dung trong repository mà Agent đọc, nhưng không có quyền gửi system prompt trực tiếp. Mục tiêu là tạo hành động trên môi trường phát triển trái với yêu cầu người dùng.

**Kỹ thuật**

Chèn các quy tắc giả, thông điệp trong file cấu hình/instructions và biến thể payload nhằm làm coding agent tạo/chạy lệnh hoặc sửa file sai. Tấn công có thể dùng chỉ dẫn dưới dạng quy trình công việc tưởng chừng hợp lý, nên tool approval ở một bước không luôn đủ: Agent có thể tạo file nguy hiểm trước rồi thực thi ở bước sau.

Nguồn: https://arxiv.org/abs/2509.22040

---

## Slide 29. “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors (AIShellJack)

H10 · Ref [46] · Manual template · 2/3

**Benchmark**

Nghiên cứu 314 payload trải trên nhiều mục tiêu tấn công/thủ thuật (tác giả liên hệ 70 kỹ thuật MITRE ATT&CK), thử các editor/agent hỗ trợ code như Cursor và Copilot trong các cấu hình được trình bày. Bài báo có trường hợp ghi nhận ASR khoảng 84% cho cấu hình dễ tổn thương, nhưng không phải mỗi biến thể hay mỗi công cụ đều đạt mức đó.

Nguồn: https://arxiv.org/abs/2509.22040

---

## Slide 30. “Your AI, My Shell”: Demystifying Prompt Injection Attacks on Agentic AI Coding Editors (AIShellJack)

H10 · Ref [46] · Manual template · 3/3

**Defense**

Bàn và khảo sát các rào chắn như chặn/cho phép command, xin xác nhận người dùng, kiểm soát tool, nhưng các phép thử cho thấy không nên coi một whitelist lệnh đơn giản là giải pháp đầy đủ. Không suy diễn rằng mọi phòng thủ nêu trong phần discussion đều được bench độc lập.

**Hạn chế/kết luận**

Shell access làm mức độ hậu quả cao hơn chatbot hỏi đáp thông thường.

**Dấu hiệu đề xuất kiểm tra**

File repository giả quy tắc workflow để yêu cầu tạo/chạy lệnh ngoài nhiệm vụ. Cần theo dõi cả file được viết và hành động chạy ở lượt sau. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2509.22040

---

## Slide 31. EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System

H11 · Ref [62] · Manual template · 1/2

**Threat model**

Kẻ tấn công bên ngoài có thể gửi email/nội dung để Copilot sau đó retrieval vào context. Người sử dụng thật chỉ yêu cầu làm việc bình thường; payload theo đường email → retrieval → LLM → đầu ra/đường tải resource, không cần họ chủ động bấm một liên kết độc hại.

**Cách tấn công**

Chỉ dẫn xấu được ngụy trang trong nội dung email có vẻ liên quan câu hỏi; tìm cách biến thông tin bí mật đã truy xuất thành thành phần của URL/resource được render hoặc truy cập ra ngoài. Điểm then chốt là khả năng egress qua URL/image/link ngoài, kể cả khi mô hình không viết PII nguyên văn trong câu trả lời.

**Benchmark**

Case study một chuỗi exploit production, có phân tích biện pháp bảo vệ bị vượt qua (ví dụ kiểm tra XPIA, redaction/đường proxy). Đây không phải benchmark N=1.000 case có ASR tổng quát; không bịa tỷ lệ thành công cho mọi hệ thống.

Nguồn: https://arxiv.org/abs/2509.10540

---

## Slide 32. EchoLeak: The First Real-World Zero-Click Prompt Injection Exploit in a Production LLM System

H11 · Ref [62] · Manual template · 2/2

**Defense được mô tả/quan sát**

Các lớp kiểm tra injection, hạn chế URL/link và security boundary của sản phẩm được phân tích trong đường tấn công; không phải một thí nghiệm so sánh 4 classifier theo F1.

**Hạn chế/kết luận**

Một môi trường ứng dụng cụ thể có thể có lỗ hổng tích hợp đặc thù, không kết luận mọi chatbot đều có cùng lỗi.

**Dấu hiệu đề xuất kiểm tra**

Email/tài liệu yêu cầu đưa dữ liệu vào URL hay resource ngoài. Quan sát request khi render, vì câu trả lời cuối có thể không chứa PII rõ. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2509.10540

---

## Slide 33. Cybersecurity AI: Hacking the AI Hackers via Prompt Injection

H12 · Ref [51] · Manual template · 1/3

**Threat model**

Agent thực hiện kiểm thử bảo mật, được phép dùng terminal/curl để đọc nội dung từ server mục tiêu. Attacker sở hữu server/web response mà Agent đi quét và đặt các chỉ dẫn tưởng là "hướng dẫn xử lý lỗ hổng" trong phản hồi. Khi tool observation trở thành instruction, attacker có thể khiến Agent tự chạy thao tác ngoài ý muốn.

**Các kiểu được phân tích**

Chỉ dẫn trực tiếp; mã hóa Base64/nhiều lớp; Unicode homoglyph; shell/environment indirection; gợi Agent viết source code rồi chạy; nội dung trong banner/log/file comment. Cơ chế chung là chuyển dữ liệu từ nguồn bị kiểm soát sang quyền thực thi của Agent. Không đưa các lệnh shell nguy hiểm nguyên văn vào test ứng dụng LLM.

Nguồn: https://arxiv.org/abs/2508.21669

---

## Slide 34. Cybersecurity AI: Hacking the AI Hackers via Prompt Injection

H12 · Ref [51] · Manual template · 2/3

**Benchmark**

Bản HTML báo cáo 14 biến thể × 10 lần = 140 phép thử, tổng 128/140 (~91,4%) lần khai thác thành công khi không bảo vệ; các biến thể trực tiếp có thể đạt 100% ở nhóm thử cụ thể. Đây là nghiên cứu PoC trên CAI framework, không phải khảo sát ngẫu nhiên Agent trên thị trường.

**Defense thực nghiệm**

Bốn lớp: sandbox/container, kiểm tra tool-output curl/wget và gắn nhãn data-only, kiểm tra file/script được viết, và validation bổ sung trên input/output. Tác giả báo 0/140 lần thành công sau bộ defense được kiểm thử, với độ trễ tăng trung bình cỡ 12,3 ms, nhưng không thể suy diễn bảo đảm chống payload thích nghi chưa được thử.

**Hạn chế/kết luận**

Sandbox và pattern filter đều có giới hạn (sandbox escape, bypass pattern); quyền shell làm hậu quả nghiêm trọng hơn QA chatbot.

Nguồn: https://arxiv.org/abs/2508.21669

---

## Slide 35. Cybersecurity AI: Hacking the AI Hackers via Prompt Injection

H12 · Ref [51] · Manual template · 3/3

**Dấu hiệu đề xuất kiểm tra**

Banner hoặc tool result yêu cầu chạy script, giải mã nội dung rồi thực thi, hoặc sửa môi trường. Kiểm tra tool output và hành động sau đó. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2508.21669

---

## Slide 36. When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review

H13 · Ref [94] · Manual template · 1/3

**Threat model**

Reviewer tự động đọc PDF manuscript của tác giả; tác giả có thể chỉnh văn bản/bố cục và font mapping trong PDF nhưng không được chỉnh instruction reviewer. Mục tiêu tăng điểm và thay đổi kết luận bình duyệt.

**Cơ chế**

Chỉ dẫn được đưa vào PDF qua những kỹ thuật khó thấy bởi người đọc, gồm ánh xạ glyph/font để parser/LLM gặp nội dung khác nội dung người nhìn; các biến thể prompt đặt ở trường tổng quan hoặc trường đánh giá cụ thể. Đây là document-parsing / modality mismatch, không phải chỉ thay chữ màu trắng.

Nguồn: https://arxiv.org/abs/2509.09912

---

## Slide 37. When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review

H13 · Ref [94] · Manual template · 2/3

**Benchmark**

Tác giả phân tích 1.441 bài báo từ ICLR 2023 và NeurIPS 2022 ở quy trình đánh giá; thực nghiệm trên mô hình reviewer như GPT-5-mini. Tác động khác nhau theo chỗ đặt payload: ở một cấu hình field-specific, có thể khiến một tỷ lệ case đạt điểm tuyệt đối khi lặp lại, nhưng không thể diễn giải là "mọi PDF bị chèn đều qua mặt 100%". Một số so sánh cho thấy thay đổi điểm trung bình từ ~6,86 lên ~7,21 với kiểu attack rộng.

Nguồn: https://arxiv.org/abs/2509.09912

---

## Slide 38. When Your Reviewer Is an LLM: Biases, Divergence, and Prompt Injection Risks in Peer Review

H13 · Ref [94] · Manual template · 3/3

**Defense**

Bài tập trung đo bias/vulnerability; các khuyến nghị về parser nhất quán, provenance, xác minh bản render và audit là bài học/gợi ý, không phải một bộ detection được benchmark end-to-end.

**Hạn chế/kết luận**

Kết quả phụ thuộc PDF parser, dạng rubric, mô hình và cách đóng gói.

**Dấu hiệu đề xuất kiểm tra**

Văn bản parser trích khác nội dung người nhìn do glyph/font mapping. So sánh bản render, extracted text và trường rubric bị nhắm. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2509.09912

---

## Slide 39. Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections

H14 · Ref [50] · Manual template · 1/3

**Threat model**

LLM làm bộ chấm cho text/code/lập luận; attacker kiểm soát bài nộp hoặc nội dung đang được chấm, đôi khi thử tác động prompt của bộ chấm. Đích đến là đánh giá ưu ái nội dung sai hoặc cho điểm không trung thực.

**Attack**

Các dạng direct instruction, ngôn từ gây nhiễu, dẫn dắt ngữ cảnh và tìm kiếm/điều chỉnh câu tấn công theo feedback. Lưu ý: survey xếp Manual Template nhưng một số biến thể của công trình có yếu tố adaptive search, không được gọi tất cả là "thủ công thuần".

**Benchmark**

5 mô hình, gồm các dòng Gemma 3, Llama 3.2, GPT-4, Claude 3 Opus; 4 nhiệm vụ chấm với 50 prompt/mỗi điều kiện; xét tính chuyển giao giữa các mô hình. Abstract nêu ASR có trường hợp tới 73,8% và transferability 50,5–62,6%. Không áp các tỷ lệ này trực tiếp cho ứng dụng LLM.

Nguồn: https://arxiv.org/abs/2504.18333

---

## Slide 40. Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections

H14 · Ref [50] · Manual template · 2/3

**Defense ĐÃ được thử (Section IV và Table VI/VII)**

(i) perplexity-based detection, (ii) instruction filtering/sanitization, (iii) content moderation classifier (RoBERTa-base được fine-tune theo mô tả của tác giả), (iv) kết hợp ba cách, (v) multi-model committees. Trong Table VI, tỷ lệ *evasion* khi kết hợp ba bộ lọc còn 18,5–42,1% tùy attack BI/CWB/CM/ASA; không phải 0%.

**Defense ĐÃ được thử (Section IV và Table VI/VII) (tiếp)**

Table VII cho thấy committee 7 model khác kiến trúc còn ASR 10,2–19,3% theo kiểu attack, thấp hơn committee 3 model, nhưng có chi phí lớn hơn. Đây là số liệu *tác giả báo cáo*, không phải phép tái kiểm chứng độc lập.

**Hạn chế/kết luận**

Chất lượng metric phụ thuộc loại judge và cấu hình task; khó đo bằng một accuracy duy nhất.

Nguồn: https://arxiv.org/abs/2504.18333

---

## Slide 41. Adversarial Attacks on LLM-as-a-Judge Systems: Insights from Prompt Injections

H14 · Ref [50] · Manual template · 3/3

**Dấu hiệu đề xuất kiểm tra**

Bài nộp ra lệnh cho bộ chấm bỏ rubric hoặc tự cho điểm. Kiểm tra với oracle độc lập và mẫu chấm tay. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2504.18333

---

## Slide 42. Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign)

H15 · Ref [63] · Manual template · 1/3

**Threat model**

Attacker có khả năng đầu độc một phần dữ liệu dùng căn chỉnh mô hình trước khi model được triển khai, không chỉ sửa tin nhắn chat. Sau đó, model vẫn hoạt động bình thường ở nhiều tác vụ nhưng trở nên dễ làm theo chỉ dẫn được chèn từ nguồn thấp quyền.

**Cơ chế**

Alignment poisoning trong supervised fine-tuning/preference optimization tạo ra sự phụ thuộc có chủ đích để *prompt injection tiếp theo* đạt hiệu quả cao hơn. Đây là training supply chain; không phải một payload xuất hiện lần đầu trong mô tả sản phẩm.

Nguồn: https://arxiv.org/abs/2410.14827

---

## Slide 43. Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign)

H15 · Ref [63] · Manual template · 2/3

**Benchmark**

Các backbone Llama/Gemma/Falcon và tập alignment như HH-RLHF/ORCA-DPO; tác giả so sánh mô hình trước/sau poisoning trên Attack Success Value (ASV) và benchmark tác vụ bình thường (chẳng hạn MMLU, GSM8K, GPQA). Ví dụ một cấu hình Llama3 trong nguồn nêu ASV hard ~0,39 → ~0,66 sau poisoning, trong khi chất lượng nền không giảm mạnh tương ứng.

Nguồn: https://arxiv.org/abs/2410.14827

---

## Slide 44. Enhancing Prompt Injection Attacks to LLMs via Poisoning Alignment (PoisonedAlign)

H15 · Ref [63] · Manual template · 3/3

**Defense**

Nghiên cứu chủ yếu phơi bày điểm yếu của pipeline alignment, không chứng minh một detector prompt bên ngoài có thể sửa sự cố training. Các thảo luận về làm sạch dữ liệu/cẩn trọng nguồn training không nên gán nhãn là defense đã benchmark thành công.

**Hạn chế/kết luận**

Đòi hỏi attacker kiểm soát dữ liệu huấn luyện, khác với kịch bản black-box ứng dụng LLM.

**Dấu hiệu đề xuất kiểm tra**

Có dữ liệu alignment bị sửa trước triển khai, còn hành vi lành vẫn tốt. Đây là dấu hiệu cần kiểm toán supply chain, không phải chữ ký text runtime. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2410.14827

---

## Slide 45. Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods

H16 · Ref [9] · Manual template · 1/2

**Threat model**

Attacker tác động vào dữ liệu supervised fine-tuning, cấy một trigger/backdoor khiến model có thể tuân theo chỉ dẫn thấp quyền ngay cả sau khi áp dụng defense theo thứ bậc instruction.

**Cách tấn công**

Nhúng mẫu trigger trong một tỷ lệ nhỏ training data; khi trigger xuất hiện trong nội dung sau này, model xem instruction độc hại là đáng tin. Không đồng nhất tấn công này với Unicode obfuscation, vì nguyên nhân là model được huấn luyện thành có cửa hậu.

**Benchmark**

Các backbone open-weight như Llama-3-8B, Qwen-2-7B, Mistral-7B; kiểm thử nhiều dạng override/PI trên tập có kiểm soát (ví dụ phishing/ads hoặc rò rỉ system prompt tùy cấu hình). Tác giả phân tích sự đánh đổi giữa tỷ lệ poisoning, ASR khi trigger xuất hiện và hành vi bình thường không có trigger.

Nguồn: https://arxiv.org/abs/2510.03705

---

## Slide 46. Backdoor-Powered Prompt Injection Attacks Nullify Defense Methods

H16 · Ref [9] · Manual template · 2/2

**Defense**

Instruction-hierarchy / alignment defenses chính là đối tượng bị stress test, không phải được đề xuất như giải pháp hoàn chỉnh; luận điểm là có thể bypass ngay cả khi lớp defense vẫn trông có tác dụng trên mẫu không có trigger.

**Hạn chế/kết luận**

Không thực tế để tự tái tạo trong vài tuần nếu không huấn luyện lại backbone; phiên bản training và bộ trigger ảnh hưởng mạnh đến kết quả.

**Dấu hiệu đề xuất kiểm tra**

Một trigger làm mô hình tuân theo chỉ dẫn thấp quyền bất thường. Cần thí nghiệm trigger/không trigger và nguồn gốc backbone. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2510.03705

---

## Slide 47. Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression

G01 · Ref [16] · LLM generation · 1/3

**Threat model**

LLM reasoning có cơ chế hiển thị/sinh bước "thinking". Đối thủ kiểm soát dữ liệu/prompt được đọc trước hoặc trong tác vụ giải bài, mục tiêu khiến mô hình ngừng reasoning quá sớm, bỏ lời giải hoặc cho đáp án không đầy đủ. Khác với attack hướng rò PII hay chuyển tool.

**Kỹ thuật**

Tạo một chuỗi nhắc mang tính "tiền kết luận" rồi rút ngắn/tối ưu độ dài token bằng LLM hỗ trợ, làm mô hình rơi vào trạng thái dừng suy luận (reasoning cessation). Đây là nhóm availability/DoS của dòng reasoning, nhưng không phải tấn công hạ tầng mạng.

Nguồn: https://arxiv.org/abs/2504.20493

---

## Slide 48. Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression

G01 · Ref [16] · LLM generation · 2/3

**Benchmark**

Các bài toán số học và phép tính (+, −, ×, ÷), đánh giá trên mô hình reasoning như DeepSeek-R1 và các mô hình hỗ trợ quá trình sinh/đánh giá. Metric: tỷ lệ dừng sai/suy luận không hoàn tất và độ dài/chi phí token của payload. Bài báo so sánh payload gốc và payload được nén; một số cấu hình có ASR cỡ hàng chục phần trăm, cần đọc bảng gốc trước khi trích một tỷ lệ cụ thể cho toàn bộ bài.

Nguồn: https://arxiv.org/abs/2504.20493

---

## Slide 49. Token-Efficient Prompt Injection Attack: Provoking Cessation in LLM Reasoning via Adaptive Token Compression

G01 · Ref [16] · LLM generation · 3/3

**Defense/khả năng chống**

Có khảo sát vài can thiệp nhỏ vào phần đầu prompt hoặc cấu trúc để phá hiệu ứng cắt reasoning ở một số mô hình; không có bộ PI classifier/RAG guardrail chung được chứng minh.

**Hạn chế/kết luận**

Hiện tượng có tính đặc thù với model/trạng thái reasoning; thiếu tổng quát cho hệ hỏi đáp.

**Dấu hiệu đề xuất kiểm tra**

Payload giả kết luận làm reasoning dừng sớm. Đo task completion và độ đúng, tránh coi mọi đáp án ngắn là tấn công. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2504.20493

---

## Slide 50. VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy

G02 · Ref [18] · LLM generation · 1/3

**Threat model**

Attacker không kiểm soát system prompt của ứng dụng hội thoại; chỉ chèn được một phần nội dung thấp quyền (thí dụ tài liệu, phản hồi từ nguồn ngoài). Mục tiêu khiến chatbot chủ động hỏi người dùng khai báo thêm thông tin cá nhân (tuổi, họ tên, liên hệ, sở thích...) thay vì chỉ làm nhiệm vụ gốc.

**Kỹ thuật**

Payload đưa vào các đoạn false memory giả như người dùng đã đồng ý cung cấp/chấp nhận quy trình thu thập thông tin; mô hình tiếp nhận câu chuyện đó và đề nghị người dùng tiết lộ PII theo nhóm. Tác giả phát triển cách tạo payload hiệu quả token, đánh giá với các kiểu rủi ro riêng tư khác nhau.

Nguồn: https://arxiv.org/abs/2510.04261

---

## Slide 51. VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy

G02 · Ref [18] · LLM generation · 2/3

**Benchmark**

6 LLM, bao gồm mô hình thường và reasoning, trên 4 benchmark (Math500, AIME2024, AIME2025, AICrypto) cùng một số ứng dụng nguồn mở; so sánh baseline payload, độ dài token và độ thành công trong việc khiến mô hình chủ động yêu cầu PII. Một phần đánh giá dùng LLM-as-a-Judge/tiêu chí tự động để đo mẫu yêu cầu riêng tư.

**Defense thử nghiệm**

Paper có mục Defenses riêng và kiểm tra các cách prevention by instruction và detection đối với injected content; mức hiệu quả thay đổi theo mô hình và kiểu câu hỏi. Không nên diễn giải "model đã hỏi PII" thành "người thật đã giao PII" hoặc "đã có PII bị gửi ra hacker".

**Hạn chế/kết luận**

Privacy solicitation khác exfiltration of PII already in agent context ([2], [62]); việc user có đồng ý/đưa dữ liệu thật không được đo hoàn toàn bằng một response LLM.

Nguồn: https://arxiv.org/abs/2510.04261

---

## Slide 52. VortexPIA: Indirect Prompt Injection Attack against LLMs for Efficient Extraction of User Privacy

G02 · Ref [18] · LLM generation · 3/3

**Dấu hiệu đề xuất kiểm tra**

Nguồn ngoài giả ký ức/đồng ý thu thập PII khiến bot chủ động xin thông tin không cần cho tác vụ. Chấm yêu cầu thu thập, chưa kết luận có dữ liệu bị rò. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2510.04261

---

## Slide 53. Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems

G03 · Ref [43] · LLM generation · 1/3

**Threat model**

LLM judge cần chấm câu trả lời được nộp; attacker kiểm soát câu trả lời đem chấm, nhưng không biết ground-truth. "Blind attack" là đoạn văn/bài nộp lừa judge phán "đúng" bất kể đáp án thật.

**Attack được formalize**

Các đáp án có câu chỉ dẫn bảo judge bỏ qua rubric, khẳng định sai thành đúng, hoặc diễn đạt đánh lạc hướng độc lập với ground truth. Đây là đối tượng phòng thủ, không phải một thuật toán sinh attack mới là kết quả chính.

Nguồn: https://arxiv.org/abs/2507.23453

---

## Slide 54. Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems

G03 · Ref [43] · LLM generation · 2/3

**Defense SE+CFE**

Chạy Standard Evaluation (SE) với đáp án đúng; đồng thời chạy Counterfactual Evaluation (CFE) với một *ground truth sai có chủ ý*. Nếu cùng một candidate vẫn được judge cho là "đúng" với cả hai điều kiện mâu thuẫn, đánh dấu dấu hiệu blind attack. Phương pháp cần thực hiện có kiểm soát vì chi phí hai lượt đánh giá và khả năng model judge tự sai.

Nguồn: https://arxiv.org/abs/2507.23453

---

## Slide 55. Counterfactual Evaluation for Blind Attack Detection in LLM-based Evaluation Systems

G03 · Ref [43] · LLM generation · 3/3

**Benchmark**

Sáu tập QA như GSM8K, HotpotQA, SQuAD, StrategyQA, TriviaQA, TruthfulQA (mỗi tập 100 mẫu, tổng 600) qua 7 model gồm Gemma-12B, Llama3.1-8B, Mistral-7B, GPT-3.5, GPT-4o-mini, GPT-4o, o1. Báo cáo ma trận nhầm lẫn correct/wrong/attack, so sánh SE và SE+CFE; cho thấy CFE phát hiện attack tốt hơn SE đơn thuần ở nhiều cấu hình.

**Hạn chế/kết luận**

Phát hiện "blind" không bao phủ toàn bộ tấn công biết ground truth; có thêm inference cost, và judge yếu có thể đánh giá sai.

**Dấu hiệu đề xuất kiểm tra**

Candidate được judge chấp nhận với cả ground truth đúng và sai có chủ ý. Tín hiệu mâu thuẫn này gắn với blind attack, không bao phủ mọi lỗi judge. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2507.23453

---

## Slide 56. Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Prompt-Injection Attacks

S01 · Ref [14] · Structural encoding · 1/3

**Threat model**

Tác giả gửi PDF paper cho reviewer dùng LLM; attacker có quyền sửa nội dung/file PDF mình nộp, không có quyền sửa system prompt của reviewer. Mục tiêu khiến reviewer chấp nhận, sửa điểm hoặc bỏ qua lỗi.

**Cơ chế**

Payload chỉ dẫn (ví dụ ép đánh giá tích cực) nằm trong chữ ẩn/chữ nhỏ, màu trùng nền, glyph/homoglyph hoặc bố cục tài liệu; khi parser trích xuất và gửi cho LLM, nội dung chỉ dẫn có thể lẫn với văn bản paper. Tác giả thử mục tiêu như ignore, detect và exploit tùy tác vụ/bối cảnh đánh giá.

Nguồn: https://arxiv.org/abs/2508.20863

---

## Slide 57. Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Prompt-Injection Attacks

S01 · Ref [14] · Structural encoding · 2/3

**Benchmark**

Các thiết lập reviewer với GPT/Gemini/Claude và nhiều cách đặt payload; so sánh PDF không chèn, PDF có chèn, nhiều vị trí/định dạng; metric theo mức thao túng đánh giá hoặc chọn đúng điều kiện đánh giá. Kết quả không đồng nhất: một số cấu hình có tỷ lệ làm lệch rõ, một số mẫu thực tế ít/không ảnh hưởng có ý nghĩa thống kê. Vì vậy không được ghi "chữ trắng luôn thắng".

Nguồn: https://arxiv.org/abs/2508.20863

---

## Slide 58. Publish to Perish / Misleading LLMs Used in Scientific Peer-Reviewing via Hidden Prompt-Injection Attacks

S01 · Ref [14] · Structural encoding · 3/3

**Defense**

Những hướng phòng thủ như kiểm tra visual layer vs text extraction, lọc đoạn ra lệnh và phân tách control/data được bàn đến; không có một scanner PDF end-to-end được chứng minh hoàn chỉnh trên mọi model.

**Hạn chế/kết luận**

Kết quả phụ thuộc parser, LLM, vị trí và mức ẩn chữ.

**Dấu hiệu đề xuất kiểm tra**

PDF có lệnh trong chữ ẩn, rất nhỏ hoặc trùng nền. So sánh raw text, parser và render, có đối chứng hidden text lành. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2508.20863

---

## Slide 59. Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions

S02 · Ref [24] · Structural encoding · 1/3

**Threat model**

Mô hình tự đọc PDF bài kiểm tra và phải trả lời đúng bài toán trắc nghiệm hoặc True/False cơ bản; attacker được sửa PDF bằng cách chèn chỉ dẫn yêu cầu chọn đáp án sai.

**Kỹ thuật**

So sánh 3 điều kiện no injected prompt, black-text prompt, white-on-white text vô hình đối với người đọc nhưng có thể được pipeline PDF trích cho LLM. Đây là case quan trọng về khác biệt giữa thứ được render và thứ parser thấy, không phải chứng minh mọi mô hình vision sẽ "nhìn thấy chữ trắng"; bài báo cho biết khi dùng screenshot thay PDF nhiều model không nhận thấy hidden prompt.

Nguồn: https://arxiv.org/abs/2508.13214

---

## Slide 60. Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions

S02 · Ref [24] · Structural encoding · 2/3

**Benchmark**

6 LLM: GPT-4o, GPT-o3, Gemini-2.5 Flash/Pro, DeepSeek-V3/R1; bộ câu hỏi phép toán và lựa chọn đơn giản, chạy theo từng điều kiện PDF. Không suy diễn các bảng theo từng câu hỏi thành ASR trên phân phối rộng.

**Defense thực nghiệm**

Tác giả thêm defensive prompt yêu cầu bỏ qua chỉ dẫn trong PDF và trả lời đúng. Trong một số tác vụ GPT-4o và DeepSeek-V3 được cải thiện rõ, trong khi Gemini-2.5 Flash vẫn thất bại ở một số điều kiện. Như vậy việc thêm instruction phòng thủ có thể giúp nhưng không ổn định giữa model.

**Hạn chế/kết luận**

Task rất nhỏ (số học/trắc nghiệm), loại model và cách đưa PDF/screenshot ảnh hưởng mạnh đến đánh giá.

Nguồn: https://arxiv.org/abs/2508.13214

---

## Slide 61. Too Easily Fooled? Prompt Injection Breaks LLMs on Frustratingly Simple Multiple-Choice Questions

S02 · Ref [24] · Structural encoding · 3/3

**Dấu hiệu đề xuất kiểm tra**

Đáp án đổi khi dùng PDF chứa chữ trắng nhưng không đổi khi dùng screenshot. Đối chiếu cùng câu hỏi ở các dạng đầu vào. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2508.13214

---

## Slide 62. Exploiting Web Search Tools of AI Agents for Data Exfiltration

S03 · Ref [61] · Structural encoding · 1/4

**Threat model**

Agent có quyền tìm kiếm web và xử lý tri thức doanh nghiệp nhạy cảm. Attacker kiểm soát một trang kết quả web/đoạn nội dung được search trả về rồi cài chỉ dẫn buộc Agent gọi web search/URL ra ngoài có kèm dữ liệu nhạy cảm. Đây là tool-result → tool-call exfiltration, không chỉ tóm tắt sai.

**Kỹ thuật**

Các biến thể Base64, nhị phân, Unicode zero-width, emoji substitution, ký tự hoa-thường, ANSI escapes, chuyển ngôn ngữ, thay cách sắp xếp từ và các phiên bản payload lộ thiên; một số nội dung được giấu dưới dạng white-on-white. Vì thế nghiên cứu này *thực sự bao gồm nhiều use case obfuscation mà bạn quan tâm*, dù survey chỉ đặt tên lớp rộng Structural Encoding.

Nguồn: https://arxiv.org/abs/2510.09093

---

## Slide 63. Exploiting Web Search Tools of AI Agents for Data Exfiltration

S03 · Ref [61] · Structural encoding · 2/4

**Benchmark**

Môi trường giả lập với RAG/company knowledge và tool web search; thử nhiều model và biến thể payload, báo cáo ASR theo từng model/template (có model/cấu hình ASR trên 70%, như Grok-4 trong bảng của bản truy cập; nhiều model khác gần 0%). Không được kết luận Base64/obfuscation luôn tăng ASR: trong một số phép thử, payload văn bản rõ lại tốt hơn các biến thể mã hóa.

Nguồn: https://arxiv.org/abs/2510.09093

---

## Slide 64. Exploiting Web Search Tools of AI Agents for Data Exfiltration

S03 · Ref [61] · Structural encoding · 3/4

**Benchmark (tiếp)**

Các biến thể và số lần chạy trên mỗi cấu hình còn hạn chế.

**Defense**

Bài chủ yếu so sánh mức chống chịu tự nhiên của mô hình và đề nghị bảo mật tốt hơn ở training/test harness; không có một thí nghiệm đầy đủ so sánh rule-only/model-only/hybrid guardrails cho tất cả biến thể.

**Hạn chế/kết luận**

Một web-search mock và số lần thử hữu hạn chưa phản ánh mọi tổ chức; các quy tắc Unicode/encoding cần tránh false positive với nội dung lành tính.

Nguồn: https://arxiv.org/abs/2510.09093

---

## Slide 65. Exploiting Web Search Tools of AI Agents for Data Exfiltration

S03 · Ref [61] · Structural encoding · 4/4

**Dấu hiệu đề xuất kiểm tra**

Tool result yêu cầu tạo search/URL mới mang dữ liệu nhạy cảm, có thể mã hóa hoặc zero-width. Thành công cần xác nhận request tại sink. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2510.09093

---

## Slide 66. Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications

S04 · Ref [35] · Structural encoding · 1/3

**Threat model**

Hệ thống tự động nhận bài báo PDF và tạo đánh giá/khuyến nghị accept/reject. Attacker kiểm soát nội dung được reviewer xử lý; mục tiêu khiến LLM bình luận tích cực/tiêu cực bất kể chất lượng bài.

**Kỹ thuật/thiết lập**

PDF được parser/OCR trích xuất thành text/Markdown, sau đó nội dung mang chỉ dẫn theo mục tiêu đánh giá được đưa vào quá trình tạo review. Tác giả thử positive/negative injection tác động tới structured output. Chú ý: trong một số cấu hình, payload được tiêm ở text/prompt sau bước parser, chứ không phải tất cả đều giấu trực tiếp trong PDF gốc; không nên quảng bá là benchmark "PDF trắng" nếu file tấn công là text.

Nguồn: https://arxiv.org/abs/2509.10248

---

## Slide 67. Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications

S04 · Ref [35] · Structural encoding · 2/3

**Benchmark**

Khoảng 1.000 hồ sơ/bài ICLR 2024 và review được mô hình tạo; dùng nhiều LLM với yêu cầu trả về định dạng có cấu trúc. Một số cấu hình GPT-5-mini thay đổi rõ quyết định: tỷ lệ accept ở baseline khoảng 54%, dưới positive injection tới 100%, negative injection gần 0%; nhiều mô hình vốn có bias chấp nhận cao ngay cả khi không tấn công. Điều này là confounder quan trọng.

Nguồn: https://arxiv.org/abs/2509.10248

---

## Slide 68. Prompt Injection Attacks on LLM Generated Reviews of Scientific Publications

S04 · Ref [35] · Structural encoding · 3/3

**Defense**

Phân tích hợp lệ định dạng output và khả năng parser có trả đúng nội dung; không phải một mô hình guardrails chống PI được huấn luyện và đánh giá riêng. Không nhầm schema validation với bảo đảm prompt integrity.

**Hạn chế/kết luận**

Thiên lệch accept/reject sẵn có trong LLM có thể khiến ASR trông cao; cần baseline sạch và task utility.

**Dấu hiệu đề xuất kiểm tra**

Nội dung đem review yêu cầu accept/reject thay rubric. So sánh baseline sạch và cả hướng positive/negative steering để loại confounder bias. Đây là gợi ý kiểm tra, chưa phải detector đã được xác nhận.

Nguồn: https://arxiv.org/abs/2509.10248

---

## Slide 69. Tổng hợp 23 bài heuristic

Các hậu quả cần đo riêng

**Lệch nhiệm vụ và hành động**

AI², Translation, AIShellJack và Cybersecurity AI cho thấy chỉ dẫn ngoài có thể đổi tác vụ, kế hoạch hoặc thao tác. Quyền terminal chỉ xuất hiện trong những threat model có terminal.

**Quyền riêng tư**

H04, EchoLeak và Web Search Exfiltration nhắm dữ liệu đã có. VortexPIA khiến chatbot xin thêm PII. Yêu cầu cung cấp PII và thực sự truyền PII là hai kết quả khác nhau.

**Các môi trường chuyên biệt**

Multi-agent, PDF, evaluator, multimodal và training backdoor cần pipeline tương ứng. Không tuyên bố một input filter văn bản đã bao phủ các môi trường này.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 70. Nhóm 2: 14 bài optimization

6 gradient, 6 evolutionary/search, 2 sampling

**Điểm khác heuristic**

Payload được cập nhật theo mục tiêu và phản hồi thay vì chỉ viết một template cố định. Ngân sách truy vấn, khả năng truy cập mô hình và mức chuyển giao quyết định tính thực tế.

**Giới hạn thông tin**

File research liệt kê tên và nguyên lý theo nhóm cho 14 bài này, không có hồ sơ thực nghiệm chi tiết như 23 bài trước. Slide từng bài giữ đúng mức thông tin đó, không tự bổ sung số liệu hoặc defense chưa được xác minh.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 71. Automatic and Universal Prompt Injection Attacks Against Large Language Models

O01 · Ref [45] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2403.04957

---

## Slide 72. Fingerprinting LLMs via Prompt Injection

O02 · Ref [28] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2509.25448

---

## Slide 73. Neural Exec: Learning (and Learning from) Execution Triggers for Prompt Injection Attacks

O03 · Ref [57] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib57

---

## Slide 74. Optimization-Based Prompt Injection Attack to LLM-as-a-Judge

O04 · Ref [64] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib64

---

## Slide 75. May I Have Your Attention? Breaking Fine-Tuning Based Prompt Injection Defenses Using Architecture-Aware Attacks

O05 · Ref [55] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2507.07417

---

## Slide 76. HijackRAG: Hijacking Attacks Against Retrieval-Augmented Large Language Models

O06 · Ref [90] · Gradient-based Optimization 

**Vị trí trong khảo sát**

Tối ưu chuỗi đầu vào theo thông tin gradient hoặc tín hiệu nội bộ/surrogate. Tạo ứng viên nhằm tăng hành vi mục tiêu rồi đánh giá mức chuyển giao.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2410.22832

---

## Slide 77. Goal-Guided Generative Prompt Injection Attack on Large Language Models

O07 · Ref [88] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib88

---

## Slide 78. PromptFuzz: Harnessing Fuzzing Techniques for Robust Testing of Prompt Injection in LLMs

O08 · Ref [84] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2409.14729

---

## Slide 79. StruPhantom: Evolutionary Injection Attacks on Black-Box Tabular Agents Powered by Large Language Models

O09 · Ref [23] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2504.09841

---

## Slide 80. AEGIS: Automated Co-Evolutionary Framework for Guarding Prompt Injections Schema

O10 · Ref [44] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2509.00088

---

## Slide 81. Adaptive Attacks Break Defenses Against Indirect Prompt Injection Attacks on LLM Agents

O11 · Ref [85] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2503.00061

---

## Slide 82. Adversarial Search Engine Optimization for Large Language Models

O12 · Ref [52] · Genetic / Evolutionary Optimization 

**Vị trí trong khảo sát**

Sinh, sửa và chọn ứng viên theo kết quả nạn nhân. Nhóm của survey còn bao gồm fuzzing và tìm kiếm thích nghi, không phải mọi bài đều dùng genetic algorithm thuần.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2406.18382

---

## Slide 83. RL Is a Hammer and LLMs Are Nails: A Simple Reinforcement Learning Recipe for Strong Prompt Injection

O13 · Ref [77] · Sampling-based Optimization 

**Vị trí trong khảo sát**

Lấy mẫu và dùng reward/phản hồi để tìm payload hiệu quả. Nhóm gồm hướng reinforcement learning và activation-guided MCMC, không đồng nhất hai thuật toán.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/abs/2510.04885

---

## Slide 84. Transferable Direct Prompt Injection via Activation-Guided MCMC Sampling

O14 · Ref [41] · Sampling-based Optimization 

**Vị trí trong khảo sát**

Lấy mẫu và dùng reward/phản hồi để tìm payload hiệu quả. Nhóm gồm hướng reinforcement learning và activation-guided MCMC, không đồng nhất hai thuật toán.

**Điều kiện và phạm vi**

Cần xác định riêng attacker nhìn được gì, số lần thử, mục tiêu và cách chấm. File research chưa tóm tắt đầy đủ thực nghiệm riêng của bài này; cần đọc bài gốc trước khi tái lập.

**Bài học cho đồ án**

Đánh giá cả payload mới và payload thích nghi với defense. Cố định ngân sách tấn công, giữ test độc lập và báo cáo chi phí. Đây là hướng kiểm chứng chung, chưa phải lựa chọn thuật toán triển khai.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib41

---

## Slide 85. Ba tầng phương pháp phòng thủ

Theo Table 2, không phải hai nhóm tạo attack

**Text-level**

Detection filter và prompt enhancement. Phát hiện chỉ dẫn, định vị đoạn, loại bỏ/viết lại hoặc phân tách instruction/data. Có thể gắn quanh lời gọi LLM mà không đổi backbone.

**Model-level**

Fine-tuning/alignment hoặc sử dụng biểu diễn nội bộ như attention và hidden states. Cần quyền truy cập hoặc huấn luyện mà nhiều API không cung cấp.

**Execution-level**

Kiểm tra mục tiêu hành động, luồng dữ liệu, quyền và môi trường thực thi. Cần thấy tool call hoặc trạng thái ứng dụng. Một proxy chỉ thấy văn bản sẽ có điểm mù.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 86. Số lượng phương pháp phòng thủ

41 công trình theo báo cáo survey

**Các nhánh trong Table 2**

Text: 11 detection + 7 prompt enhancement. Model: 4 alignment + 3 IR. Execution: 2 task alignment + 7 information flow + 3 policy + 4 isolation.

**Vì sao tài liệu có D01–D40?**

D15 gộp hai bài [5] và [10]. Công trình [75] được trình bày ở cả rewriting và fine-tuning. Các hàng phân loại có thể chồng lấn, nên không dùng phép cộng hàng để khẳng định số paper duy nhất.

**Cách đọc phần tiếp theo**

Mỗi mã D có slide riêng về cơ chế ở mức survey và điểm cần kiểm tra khi áp dụng. Các gợi ý đánh giá là đề xuất của nhóm, chưa phải kết quả tái lập từng paper.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 87. PromptShield [30] (2024)

D01 · Text-level · LLM-based classification

**Cơ chế theo hồ sơ khảo sát**

Chấm nội dung có chứa chỉ dẫn chèn bằng một mô hình chuyên phát hiện.

**Điểm cần kiểm tra khi áp dụng**

Kiểm tra FPR trên đoạn lành có trích dẫn lệnh.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib30

---

## Slide 88. Pan et al. [54] (2025)

D02 · Text-level · Detection + generative explanation

**Cơ chế theo hồ sơ khảo sát**

Trả nhãn phát hiện cùng lời giải thích phục vụ điều tra.

**Điểm cần kiểm tra khi áp dụng**

Lời giải thích hợp lý chưa đủ chứng minh nhãn đúng.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2502.11006

---

## Slide 89. PromptArmor [66] (2025)

D03 · Text-level · Third-party input detection

**Cơ chế theo hồ sơ khảo sát**

Kiểm tra đầu vào bên thứ ba trước khi nạp vào LLM.

**Điểm cần kiểm tra khi áp dụng**

Đo cả khả năng phát hiện và utility sau xử lý.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2507.15219

---

## Slide 90. SecInfer [48] (2025)

D04 · Text-level · Inference-time scaling / self-inspection

**Cơ chế theo hồ sơ khảo sát**

Tăng suy luận tự kiểm tra ở thời điểm inference để nhận ra injection tinh vi.

**Điểm cần kiểm tra khi áp dụng**

Đo số lời gọi, token và độ trễ khi tăng mức kiểm tra.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2509.24967

---

## Slide 91. LLMz+ [58] (2025)

D05 · Text-level · Policy/whitelist-style detection

**Cơ chế theo hồ sơ khảo sát**

Đối chiếu nội dung với nguyên tắc whitelist và ngữ cảnh được cho phép.

**Điểm cần kiểm tra khi áp dụng**

Whitelist cần phản ánh nhiệm vụ thật, tránh khóa hết dữ liệu ngoài.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2509.18557

---

## Slide 92. PromptLocate [32] (2025)

D06 · Text-level · Segment localization

**Cơ chế theo hồ sơ khảo sát**

Định vị đoạn bị chèn thay vì gán một nhãn cho toàn bộ tài liệu.

**Điểm cần kiểm tra khi áp dụng**

Đo span detection và thông tin hợp lệ bị xóa nhầm.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2510.12252

---

## Slide 93. FocusAgent [34] (2025)

D07 · Text-level · Long-context / segment handling

**Cơ chế theo hồ sơ khảo sát**

Chọn lọc hoặc cắt context dài trong web agent. Survey đặt ở detection.

**Điểm cần kiểm tra khi áp dụng**

Context trimming không tự chứng minh đã nhận diện mọi injection.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2510.03204

---

## Slide 94. Rahman et al. [60] (2024)

D08 · Text-level · BERT-based classifier

**Cơ chế theo hồ sơ khảo sát**

Dùng encoder để phân loại nội dung thay cho một lần sinh bằng LLM lớn.

**Điểm cần kiểm tra khi áp dụng**

Đo khả năng tổng quát qua nguồn và ngôn ngữ ngoài tập huấn luyện.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib60

---

## Slide 95. PIGuard [40] (2025)

D09 · Text-level · Lightweight prompt-injection guard

**Cơ chế theo hồ sơ khảo sát**

Tập trung phát hiện injection đồng thời giảm over-defense.

**Điểm cần kiểm tra khi áp dụng**

Cần hard-benign gần bề mặt tấn công để đo chặn nhầm.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib40

---

## Slide 96. Chen et al. [7] (2025)

D10 · Text-level · Indirect PI detection and removal

**Cơ chế theo hồ sơ khảo sát**

Kết hợp phát hiện indirect injection và loại bỏ nội dung bị chèn.

**Điểm cần kiểm tra khi áp dụng**

Tách chất lượng detector khỏi chất lượng tác vụ sau loại bỏ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2502.16580

---

## Slide 97. CommandSans [19] (2025)

D11 · Text-level · Fine-grained / token sanitizer

**Cơ chế theo hồ sơ khảo sát**

Sanitize ở mức hạt mịn nhằm can thiệp vào phần chỉ dẫn nguy hiểm.

**Điểm cần kiểm tra khi áp dụng**

Kiểm tra token/đoạn bị sửa và độ bảo toàn ý nghĩa.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2510.08829

---

## Slide 98. Spotlighting [26] (2024)

D12 · Text-level · Input / instruction–data separation

**Cơ chế theo hồ sơ khảo sát**

Biến đổi và đánh dấu dữ liệu ngoài để phân ranh control/data.

**Điểm cần kiểm tra khi áp dụng**

Delimiter và dấu nguồn phụ thuộc khả năng model tuân theo.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2403.14720

---

## Slide 99. FATH [72] (2024)

D13 · Text-level · Output-side separation / authentication

**Cơ chế theo hồ sơ khảo sát**

Dùng cơ chế authentication ở thời điểm chạy để kiểm tra ranh giới đầu ra.

**Điểm cần kiểm tra khi áp dụng**

Xác minh cơ chế kiểm tra, không coi định dạng đúng là nội dung an toàn.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2410.21492

---

## Slide 100. Chen et al. [8] (2025)

D14 · Text-level · Self-referencing

**Cơ chế theo hồ sơ khảo sát**

Yêu cầu tham chiếu lại chỉ dẫn gốc để duy trì trọng tâm nhiệm vụ.

**Điểm cần kiểm tra khi áp dụng**

Đo hành động có bám nhiệm vụ, không chỉ kiểm tra đã trích dẫn.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2504.20472

---

## Slide 101. Chen et al. [5] (2025), [10] (2025)

D15 · Text-level · Defensive / negative prompts

**Cơ chế theo hồ sơ khảo sát**

Thêm defensive token hoặc negative prompt để giảm ảnh hưởng payload. Hai bài được gộp ở mã D15.

**Điểm cần kiểm tra khi áp dụng**

Chạy đối chứng cùng attack set và thử payload thích nghi.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2507.07974

---

## Slide 102. Alharthi et al. [1] (2025)

D16 · Text-level · Prompt rewriting / sanitization

**Cơ chế theo hồ sơ khảo sát**

Viết lại hoặc sanitize nội dung trước bước reasoning.

**Điểm cần kiểm tra khi áp dụng**

Đo dữ kiện đúng bị thay đổi và injection còn tồn tại.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2510.00451

---

## Slide 103. Wang et al. [75] (2025)

D17 · Text-level · Polymorphic prompt protection / rewriting

**Cơ chế theo hồ sơ khảo sát**

Thay đổi cấu trúc prompt/delimiter để attacker khó dự đoán.

**Điểm cần kiểm tra khi áp dụng**

Giữ riêng tác dụng rewriting với phần fine-tuning của cùng công trình.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2506.05739

---

## Slide 104. Jatmo [59] (2024)

D18 · Model-level · Task-specific fine-tuning

**Cơ chế theo hồ sơ khảo sát**

Fine-tune theo tác vụ để mô hình ưu tiên nhiệm vụ và ranh giới được huấn luyện.

**Điểm cần kiểm tra khi áp dụng**

Cần dữ liệu huấn luyện, tài nguyên và kiểm tra ngoài tác vụ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib59

---

## Slide 105. SecAlign [6] (2025)

D19 · Model-level · Preference / security alignment

**Cơ chế theo hồ sơ khảo sát**

Preference/security alignment để ưu tiên đầu ra tuân thủ nhiệm vụ hợp lệ.

**Điểm cần kiểm tra khi áp dụng**

Cần quyền huấn luyện và thử tấn công không có trong dữ liệu alignment.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib6

---

## Slide 106. StruQ [4] (2025)

D20 · Model-level · Structured-query fine-tuning

**Cơ chế theo hồ sơ khảo sát**

Kết hợp structured query và huấn luyện để phân biệt instruction với data.

**Điểm cần kiểm tra khi áp dụng**

Chỉ thêm ký hiệu vào prompt không tương đương tái lập StruQ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib4

---

## Slide 107. Wang et al. [75] (2025)

D21 · Model-level · Polymorphic prompt fine-tuning

**Cơ chế theo hồ sơ khảo sát**

Huấn luyện với nhiều cấu trúc prompt nhằm tăng chống chịu với biến thể.

**Điểm cần kiểm tra khi áp dụng**

Cần tách đóng góp format, dữ liệu và huấn luyện.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2506.05739

---

## Slide 108. Attention Tracker [29] (2025)

D22 · Model-level · Attention map tracking

**Cơ chế theo hồ sơ khảo sát**

Theo dõi attention để tìm ảnh hưởng bất thường từ vùng không tin cậy.

**Điểm cần kiểm tra khi áp dụng**

Cần truy cập attention. Không coi mọi attention cao là tấn công.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib29

---

## Slide 109. PIShield [96] (2025)

D23 · Model-level · Intrinsic-feature-based PI detection

**Cơ chế theo hồ sơ khảo sát**

Dùng đặc trưng nội tại của LLM để phát hiện injection.

**Điểm cần kiểm tra khi áp dụng**

Kiểm tra độ chuyển giao khi đổi backbone và nhiệm vụ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2510.14005

---

## Slide 110. Wen et al. [76] (2025)

D24 · Model-level · Hidden-state / representation probing

**Cơ chế theo hồ sơ khảo sát**

Khai thác hidden state/representation để phát hiện dấu hiệu tuân theo lệnh ngoài.

**Điểm cần kiểm tra khi áp dụng**

Cần hook inference và hiệu chuẩn trên mô hình đích.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2505.06311

---

## Slide 111. Task Shield [31] (2025)

D25 · Execution-level · Goal/task alignment

**Cơ chế theo hồ sơ khảo sát**

So sánh tool call với mục tiêu người dùng và các bước cần cho nhiệm vụ.

**Điểm cần kiểm tra khi áp dụng**

Chặn hành động lệch mục tiêu nhưng vẫn cho phép dùng dữ kiện ngoài.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib31

---

## Slide 112. Melon [95] (2025)

D26 · Execution-level · Robust action alignment

**Cơ chế theo hồ sơ khảo sát**

Tăng độ bền quá trình chọn hành động trước perturbation/injection.

**Điểm cần kiểm tra khi áp dụng**

Các bảo đảm phụ thuộc giả định của paper, không áp cho mọi agent.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2502.05174

---

## Slide 113. Fides [15] (2025)

D27 · Execution-level · Trust-label / information flow

**Cơ chế theo hồ sơ khảo sát**

Gắn nhãn mức tin cậy và theo dõi ảnh hưởng của dữ liệu qua vòng đời agent.

**Điểm cần kiểm tra khi áp dụng**

Nhãn phải tồn tại qua biến đổi, tóm tắt và kết hợp nguồn.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2505.23643

---

## Slide 114. SafeFlow [42] (2025)

D28 · Execution-level · Transactional trustworthy flow

**Cơ chế theo hồ sơ khảo sát**

Dùng giao thức trustworthy/transactional để kiểm soát luồng dữ liệu và thao tác.

**Điểm cần kiểm tra khi áp dụng**

Cần tích hợp nội bộ và kiểm tra thay đổi trạng thái.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2506.07564

---

## Slide 115. Siddiqui et al. [67] (2024)

D29 · Execution-level · Permissive information-flow analysis

**Cơ chế theo hồ sơ khảo sát**

Cho phép xử lý dữ liệu không tin cậy nhưng ngăn luồng đến sink nguy hiểm.

**Điểm cần kiểm tra khi áp dụng**

Định nghĩa nguồn, nhãn và sink theo chính sách cụ thể.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2410.03055

---

## Slide 116. Wu et al. [78] (2024)

D30 · Execution-level · Flow-based isolation

**Cơ chế theo hồ sơ khảo sát**

Cô lập luồng để dữ liệu thấp quyền không nâng thành quyền điều khiển.

**Điểm cần kiểm tra khi áp dụng**

Kiểm tra luồng ẩn qua biến trung gian và kết quả công cụ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2409.19091

---

## Slide 117. AgentArmor [74] (2025)

D31 · Execution-level · Runtime trace analysis

**Cơ chế theo hồ sơ khảo sát**

Phân tích execution trace như chương trình để nhận ra chuỗi thực thi bất thường.

**Điểm cần kiểm tra khi áp dụng**

Cần đủ trace nhiều bước, không chỉ câu trả lời cuối.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2508.01249

---

## Slide 118. RTBAS [92] (2025)

D32 · Execution-level · Exfiltration / privacy-flow protection

**Cơ chế theo hồ sơ khảo sát**

Theo dõi luồng đầu ra để ngăn exfiltration và privacy leakage.

**Điểm cần kiểm tra khi áp dụng**

Chấm dữ liệu tại đích truyền, gồm tool arguments và request.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2502.08966

---

## Slide 119. CaMeL [20] (2025)

D33 · Execution-level · Program / flow control architecture

**Cơ chế theo hồ sơ khảo sát**

Tách control/data flow và kiểm soát ảnh hưởng của dữ liệu lên hành động.

**Điểm cần kiểm tra khi áp dụng**

Đổi kiến trúc sâu hơn một bộ lọc text quanh API.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2503.18813

---

## Slide 120. AGrail [49] (2025)

D34 · Execution-level · Adaptive safety policy

**Cơ chế theo hồ sơ khảo sát**

Sinh hoặc cập nhật chính sách an toàn theo ngữ cảnh tác vụ.

**Điểm cần kiểm tra khi áp dụng**

Bộ sinh policy cũng cần bảo vệ trước nội dung không tin cậy.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2502.11448

---

## Slide 121. Tsai & Bagdasarian [70] (2025)

D35 · Execution-level · Contextual security policy

**Cơ chế theo hồ sơ khảo sát**

Ràng buộc hành vi bằng chính sách bảo mật phù hợp mục đích.

**Điểm cần kiểm tra khi áp dụng**

Xác định ai cấp quyền và khi nào chính sách được thay đổi.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib70

---

## Slide 122. Progent [65] (2025)

D36 · Execution-level · Programmable privilege control

**Cơ chế theo hồ sơ khảo sát**

Cho người dùng/hệ thống mô tả quyền hành động bằng quy tắc lập trình.

**Điểm cần kiểm tra khi áp dụng**

Thực thi quyền ở ngoài LLM, kiểm tra đúng tài nguyên và tham số.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/abs/2504.11703

---

## Slide 123. IsolateGPT [79] (2025)

D37 · Execution-level · Environment isolation

**Cơ chế theo hồ sơ khảo sát**

Cô lập môi trường thực thi và giao tiếp giữa các ngữ cảnh.

**Điểm cần kiểm tra khi áp dụng**

Isolation có chi phí và có thể hạn chế tác vụ cần chia sẻ dữ liệu.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib79

---

## Slide 124. PFI [36] (2025)

D38 · Execution-level · Planning isolation / prompt-flow integrity

**Cơ chế theo hồ sơ khảo sát**

Bảo vệ prompt-flow integrity để kế hoạch không bị dữ liệu thấp quyền chi phối.

**Điểm cần kiểm tra khi áp dụng**

Cần theo dõi ranh giới giữa planning và execution.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib36

---

## Slide 125. DRIFT [39] (2025)

D39 · Execution-level · Dynamic rule-based isolation

**Cơ chế theo hồ sơ khảo sát**

Kết hợp quy tắc động và cô lập injection trong kiến trúc agent.

**Điểm cần kiểm tra khi áp dụng**

Đo utility khi kế hoạch thật cần phụ thuộc quan sát môi trường.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib39

---

## Slide 126. ACE [38] (2025)

D40 · Execution-level · Security architecture / planning isolation

**Cơ chế theo hồ sơ khảo sát**

Tổ chức kiến trúc và planning isolation để giữ nguồn quyền điều khiển.

**Điểm cần kiểm tra khi áp dụng**

Tích hợp kiến trúc cần xác nhận khả năng thực thi, không chỉ mô tả sơ đồ.

**Đề xuất đánh giá**

So sánh có/không phương pháp trên cùng nhiệm vụ và payload. Báo cáo mức giảm tấn công, nhiệm vụ hợp lệ còn hoàn tất, lỗi chặn nhầm và chi phí. Hồ sơ MD chỉ tóm tắt nhóm này, cần đọc bài gốc trước tái lập chi tiết.

Nguồn: https://arxiv.org/html/2602.10453v1#bib.bib38

---

## Slide 127. Hidden-in-Plain-Text: A Benchmark for Social-Web Indirect Prompt Injection in RAG

ADD-01 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

OpenRAG-Soc: benchmark/harness cho RAG dùng nội dung mạng xã hội. Xem xét quá trình từ ingestion đến retrieval và generation; hỗ trợ so sánh sparse/dense retriever, HTML/Markdown sanitization, Unicode normalization và attribution-gated answering.

**Phương pháp tấn công / phòng thủ**

Tấn công qua các nội dung web/user-generated có thể tồn tại qua bước trích xuất và truy xuất. Phòng thủ tiêu biểu là làm sạch cấu trúc, chuẩn hóa Unicode có kiểm soát và yêu cầu quy chiếu nguồn trước khi trả lời.

**Benchmark / kết quả được nguồn mô tả**

Bài báo đề xuất theo dõi khả năng attack đến bước sinh đáp án, dịch chuyển thứ hạng retrieval, utility và latency; phần metadata xác nhận bộ benchmark, không suy ra ASR cụ thể khi chưa kiểm tra bảng gốc.

Nguồn: https://arxiv.org/abs/2601.10923

---

## Slide 128. Hidden-in-Plain-Text: A Benchmark for Social-Web Indirect Prompt Injection in RAG

ADD-01 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Phạm vi social-web RAG; không phải mọi biến thể Unicode/HTML đều hiệu quả ở mọi chatbot.

Nguồn: https://arxiv.org/abs/2601.10923

---

## Slide 129. Silent Egress: When Implicit Prompt Injection Makes LLM Agents Leak Without a Trace

ADD-02 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Chỉ ra rò rỉ có thể xảy ra qua lời gọi công cụ hoặc HTTP request mà câu trả lời cuối vẫn bình thường. Payload xuất hiện trong URL preview/metadata mà người dùng không chủ động xem.

**Phương pháp tấn công / phòng thủ**

Implicit indirect injection từ title/snippet/metadata → Agent tạo request ra ngoài → nội dung nhạy cảm theo request. Tác giả bàn về việc chia dữ liệu qua nhiều request để tránh bộ lọc đơn lẻ; phòng thủ hữu ích ở điểm egress, domain allowlist và kiểm tra redirects.

**Benchmark / kết quả được nguồn mô tả**

Nghiên cứu báo cáo 480 lần chạy với Agent dựa trên qwen2.5:7b; xác suất egress 0,89 trong thiết lập thử nghiệm. Đây không phải tỷ lệ ngoài thực tế.

Nguồn: https://arxiv.org/abs/2602.22450

---

## Slide 130. Silent Egress: When Implicit Prompt Injection Makes LLM Agents Leak Without a Trace

ADD-02 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Môi trường mô phỏng local; không chứng minh mọi chatbot chỉ hỏi đáp có nguy cơ HTTP egress tương đương.

Nguồn: https://arxiv.org/abs/2602.22450

---

## Slide 131. A Survey of Secure Retrieval-Augmented Generation

ADD-03 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Đề xuất cách nhìn bảo vệ hệ thống RAG theo các trục Surface, Layer, Objective, Target (SLOT); nhấn mạnh bảo mật cả tuyến truy cập tri thức ngoài, không chỉ prompt.

**Phương pháp tấn công / phòng thủ**

Tổng hợp 135 nghiên cứu theo SLOT: Surface–Layer–Objective–Target; lập bản đồ các điểm tấn công/điểm can thiệp trong pipeline truy cập tri thức RAG.

**Benchmark / kết quả được nguồn mô tả**

Survey/đề xuất taxonomy; không nên báo là giải pháp đã vượt một benchmark duy nhất.

Nguồn: https://aclanthology.org/2026.findings-emnlp.241/

---

## Slide 132. A Survey of Secure Retrieval-Augmented Generation

ADD-03 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Là tài liệu tổng quan, không phải implementation.

Nguồn: https://aclanthology.org/2026.findings-emnlp.241/

---

## Slide 133. Evaluation of Prompt Injection Defenses in Large Language Models

ADD-04 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Đánh giá các cấu hình phòng vệ trước attacker thích nghi nhằm làm lộ thông tin trong system prompts, cho thấy các biện pháp dựa hoàn toàn vào việc mô hình tự giữ bí mật có thể thất bại.

**Phương pháp tấn công / phòng thủ**

Attacker điều chỉnh truy vấn qua nhiều vòng; biện pháp được kiểm tra gồm lọc đầu ra bằng mã ứng dụng độc lập với mô hình.

**Benchmark / kết quả được nguồn mô tả**

Abstract tác giả mô tả >20.000 attack trials và một cấu hình output filtering giữ 0 leaks trong 15.000 lượt ở setup của họ; không coi đây là đảm bảo cho PII hoặc mọi kênh egress.

Nguồn: https://arxiv.org/abs/2604.23887

---

## Slide 134. Evaluation of Prompt Injection Defenses in Large Language Models

ADD-04 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Đối tượng chính là system-prompt secrets, không đồng nhất rò rỉ PII trong RAG.

Nguồn: https://arxiv.org/abs/2604.23887

---

## Slide 135. ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection

ADD-05 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Xây AgentLure benchmark và ARGUS, theo dõi quan hệ ảnh hưởng của dữ liệu không đáng tin đến quyết định Agent.

**Phương pháp tấn công / phòng thủ**

Influence provenance graph và kiểm tra liệu hành động có đủ bằng chứng tin cậy hay không; khác với chỉ phát hiện token khả nghi.

**Benchmark / kết quả được nguồn mô tả**

Tác giả báo cáo ASR còn 3,8% và utility 87,5% trên AgentLure; gắn với cấu hình của tác giả, chưa tái lập độc lập.

Nguồn: https://arxiv.org/abs/2605.03378

---

## Slide 136. ARGUS: Defending LLM Agents Against Context-Aware Prompt Injection

ADD-05 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Phức tạp hơn RAG chatbot không dùng tools; yêu cầu instrumentation nội bộ.

Nguồn: https://arxiv.org/abs/2605.03378

---

## Slide 137. Blind Spots in the Guard: How Domain-Camouflaged Injection Attacks Evade Detection in Multi-Agent LLM Systems

ADD-06 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Phát hiện các payload giả giọng điệu và từ vựng của tài liệu đích có thể bị bộ lọc xem là thông tin bình thường; gọi chênh lệch hiệu quả này là Camouflage Detection Gap.

**Phương pháp tấn công / phòng thủ**

Attack không cần câu “IGNORE ALL...”, mà dùng lời khuyến nghị/nhận định giả thẩm quyền phù hợp với domain. Tác giả so sánh static với camouflaged payloads.

**Benchmark / kết quả được nguồn mô tả**

Nghiên cứu 45 tasks qua 3 domain, 2 model families; báo cáo độ phát hiện giảm mạnh dưới các cấu hình cụ thể. Không suy rộng các tỷ lệ sang detector khác.

Nguồn: https://arxiv.org/abs/2605.22001

---

## Slide 138. Blind Spots in the Guard: How Domain-Camouflaged Injection Attacks Evade Detection in Multi-Agent LLM Systems

ADD-06 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Có thành phần multi-agent, quy mô tác vụ giới hạn; cần cẩn trọng khi áp dụng vào chatbot đơn Agent.

Nguồn: https://arxiv.org/abs/2605.22001

---

## Slide 139. Can It Reach the Generator? Investigating the Survival of Prompt-Injection Attacks in Realistic RAG Settings

ADD-07 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Nhiều benchmark đưa sẵn payload vào context LLM nên đánh giá quá cao khả năng tấn công; paper kiểm tra qua retriever → reranker → generator.

**Phương pháp tấn công / phòng thủ**

Tấn công chỉ thành công nếu tài liệu độc hại vượt qua retrieval/reranking và ảnh hưởng sinh câu trả lời. Tác giả tái kiểm tra 7 GEO attack variants.

**Benchmark / kết quả được nguồn mô tả**

Đo sự sống sót ở từng giai đoạn và thành công end-to-end; các attack đơn giản/gradient kém hiệu quả khi phải đi qua retrieval trong thiết lập paper.

Nguồn: https://arxiv.org/abs/2605.28017

---

## Slide 140. Can It Reach the Generator? Investigating the Survival of Prompt-Injection Attacks in Realistic RAG Settings

ADD-07 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Tập trung recommendation/GEO hơn là mọi hành vi xâm nhập.

Nguồn: https://arxiv.org/abs/2605.28017

---

## Slide 141. Evaluating Prompting-Based Defenses Against Domain-Camouflaged Injection Attacks

ADD-08 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

So sánh Spotlighting, paraphrasing, sandwiching và kết hợp trước payload giả dạng văn bản hợp lệ trong ngành nghề.

**Phương pháp tấn công / phòng thủ**

Áp dụng nhiều cấu trúc bảo vệ trước cùng attack set; kết quả thay đổi theo từng mô hình.

**Benchmark / kết quả được nguồn mô tả**

Tác giả nêu 3.510 trials qua 3 model families/3 domains; paraphrasing có hiệu quả tương đối nhất quán trong bối cảnh thử nghiệm nhưng không xóa hết rủi ro.

Nguồn: https://arxiv.org/abs/2606.18530

---

## Slide 142. Evaluating Prompting-Based Defenses Against Domain-Camouflaged Injection Attacks

ADD-08 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Tài liệu nghề nghiệp tổng hợp/synthetic, không có bằng chứng kết quả giữ nguyên với mọi dữ liệu doanh nghiệp.

Nguồn: https://arxiv.org/abs/2606.18530

---

## Slide 143. Indirect Prompt Injection in Large Language Models

ADD-09 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Nghiên cứu tấn công gián tiếp thông qua tài liệu có chỉ dẫn được nhúng kín đáo, bao gồm các cách trình bày khiến người đọc và pipeline nhận diện có thể nhìn thấy nội dung khác nhau.

**Phương pháp tấn công / phòng thủ**

Khai thác sự khác biệt giữa cách nhìn văn bản hiển thị và cách parser/LLM lấy text; liên quan đến các biến thể chữ rất nhỏ hoặc khó nhìn trong tài liệu.

**Benchmark / kết quả được nguồn mô tả**

Bài báo thảo luận và thực nghiệm các kịch bản indirect injection; cần xem thiết lập cụ thể trước khi ghi chỉ số ASR vào luận văn.

Nguồn: https://doi.org/10.1007/s00521-026-12266-x](https://doi.org/10.1007/s00521-026-12266-x

---

## Slide 144. Indirect Prompt Injection in Large Language Models

ADD-09 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Chủ yếu có ích nếu chatbot ingest HTML/PDF; không đáng làm parser phức tạp nếu hệ thống chỉ lấy JSON từ DB.

Nguồn: https://doi.org/10.1007/s00521-026-12266-x](https://doi.org/10.1007/s00521-026-12266-x

---

## Slide 145. PIArena: A Platform for Prompt Injection Evaluation

ADD-10 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Đề xuất nền tảng đánh giá tổng hợp nhiều attacks, defenses và benchmarks; cho thấy defense dễ thất bại khi đổi dataset hoặc gặp attacker thích nghi.

**Phương pháp tấn công / phòng thủ**

Tấn công tối ưu theo feedback của defense; đánh giá tính chuyển giao và hiệu quả qua nhiều nhiệm vụ thay vì một vài template.

**Benchmark / kết quả được nguồn mô tả**

Có nền tảng và mã nguồn được công bố; nguồn ACL xác nhận tháng 07/2026. Không gán ngày 01/07 là ngày xuất bản thật.

Nguồn: https://aclanthology.org/2026.acl-long.1533/

---

## Slide 146. PIArena: A Platform for Prompt Injection Evaluation

ADD-10 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Môi trường đánh giá rộng, không cần chạy toàn bộ để làm đồ án.

Nguồn: https://aclanthology.org/2026.acl-long.1533/

---

## Slide 147. Defenses Against Prompt Attacks Learn Surface Heuristics

ADD-11 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Các hệ thống phòng thủ học mẹo theo vị trí, token trigger, chủ đề thay vì hiểu ý định tấn công, làm tăng false positives.

**Phương pháp tấn công / phòng thủ**

Đánh giá vị trí dữ liệu, token kích hoạt và khả năng khái quát ra domain ngoài phân phối huấn luyện.

**Benchmark / kết quả được nguồn mô tả**

Nguồn ACL nêu có cấu hình false refusal tăng đến 50% chỉ vì trigger token; đây là kết quả của họ trong bài test kiểm soát.

Nguồn: https://aclanthology.org/2026.acl-long.502/

---

## Slide 148. Defenses Against Prompt Attacks Learn Surface Heuristics

ADD-11 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Tập trung hiệu ứng của defense fine-tuning, không thay thế đánh giá detector độc lập.

Nguồn: https://aclanthology.org/2026.acl-long.502/

---

## Slide 149. Rethinking Assessments of Prompt Injection Attacks

ADD-12 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Đánh giá đa thiết lập, kể cả ứng dụng thật, để chỉ ra khung benchmark có thể thiếu tính thực tế.

**Phương pháp tấn công / phòng thủ**

So sánh loại payload, nhiệm vụ và ứng dụng, đặt cạnh các phòng thủ prompt-level/model-level.

**Benchmark / kết quả được nguồn mô tả**

Abstract công bố 37 ứng dụng, 185 injected tasks, 21 attack instructions, 143.745 queries; là kết quả của thiết lập nghiên cứu, không phản ánh tỷ lệ thị trường.

Nguồn: https://aclanthology.org/2026.findings-acl.1191/

---

## Slide 150. Rethinking Assessments of Prompt Injection Attacks

ADD-12 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Nguồn hiện truy cập tốt ở trang ACL metadata/abstract; cần xác minh PDF nếu muốn lấy bảng kết quả chi tiết.

Nguồn: https://aclanthology.org/2026.findings-acl.1191/

---

## Slide 151. PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift

ADD-13 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Bổ sung stress tests cho đầu vào hợp lệ nhưng trông giống attack, payload bị biến dạng và dịch chuyển phân phối.

**Phương pháp tấn công / phòng thủ**

Frozen multi-axis benchmark, fixed thresholds, kiểm tra recall của attack đồng thời đo hard-benign FPR.

**Benchmark / kết quả được nguồn mô tả**

Trong tập stress của tác giả, một detector F1 >0,98 trên held-out test vẫn chặn nhầm gần một phần ba hard-benign ngoại nguồn. Không suy ra FPR deployment.

Nguồn: https://arxiv.org/abs/2609.15017

---

## Slide 152. PIDS-Bench: Evaluating Prompt-Injection Detectors Under Over-Defense, Obfuscation, and Distribution Shift

ADD-13 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

Stress distribution được chọn để phơi bày lỗi; không đại diện lưu lượng người dùng tự nhiên.

Nguồn: https://arxiv.org/abs/2609.15017

---

## Slide 153. RAG-PIBench: A Leakage-Aware Benchmark for Prompt-Injection Detection in Trustworthy RAG Systems

ADD-14 · Nghiên cứu bổ sung ngoài survey · 1/2

**Nội dung / đóng góp**

Bộ dữ liệu 4.876 ví dụ có ngữ cảnh, chú trọng tránh trùng lặp/leakage giữa train, validation và protected test.

**Phương pháp tấn công / phòng thủ**

So sánh keyword, semantic-reference, TF-IDF, logistic/SVM và transformer-based detector theo protocol cố định.

**Benchmark / kết quả được nguồn mô tả**

Theo abstract, DistilBERT F1=0,896 và PR-AUC=0,968 trên protected test; các mô hình sparse vẫn cạnh tranh được.

Nguồn: https://arxiv.org/abs/2610.08571

---

## Slide 154. RAG-PIBench: A Leakage-Aware Benchmark for Prompt-Injection Detection in Trustworthy RAG Systems

ADD-14 · Nghiên cứu bổ sung ngoài survey · 2/2

**Hạn chế / điều kiện áp dụng**

“Leakage-aware” ở đây nói về dataset split leakage, không phải phòng ngừa rò rỉ PII khách hàng.

Nguồn: https://arxiv.org/abs/2610.08571

---

## Slide 155. Hướng thực hiện của nhóm

Phương pháp tổng quát, chưa chọn model

**Lõi bảo vệ văn bản**

Tiếp nhận nội dung cùng nhãn nguồn và nhiệm vụ. Kết hợp luật kiểm tra chính sách, bộ phát hiện chỉ dẫn chèn và cơ chế phân tách dữ liệu/chỉ dẫn. Quyết định cho qua, xử lý nội dung hoặc chặn theo chính sách.

**Bảo vệ thông tin cá nhân**

Xác định dữ liệu cần bảo vệ, quyền xem và đích được phép truyền. Nhận diện PII chỉ là một bước, cần kiểm tra tại đầu vào, trước dịch vụ ngoài, đầu ra và log.

**Giới hạn cam kết**

Tập trung direct/indirect text ở runtime. PDF, đa phương thức, multi-agent, terminal, training backdoor và kiến trúc isolation đầy đủ là hướng khảo sát hoặc mở rộng theo điều kiện.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 156. Vị trí tích hợp

Lõi độc lập và adapter ở ranh giới ứng dụng

**Thư viện/package**

Lõi nhận text, provenance và policy, trả quyết định có lý do. Adapter gọi lõi trước khi đưa dữ liệu ngoài vào context và trước khi trả kết quả. Cách này cho phép thấy ngữ cảnh ứng dụng.

**Gateway/proxy**

Phù hợp kiểm tra request/response đi qua một endpoint. Chỉ có thể bảo vệ dữ liệu quan sát được, không tự biết tool nội bộ, quyền backend hoặc trạng thái thực thi.

**Hook thực thi nếu có tool**

Kiểm tra trước tool call và sau tool result. Tool vẫn phải kiểm tra phân quyền phía server. Tool/skill/MCP là cách cung cấp khả năng, không tự tạo bảo đảm chống injection.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 157. Các cấu hình so sánh

Mỗi lớp cần có đối chứng

**Mốc tham chiếu**

Không guardrail và prompt-only để đo nền. So sánh rule-only, detector-only, cùng cấu hình kết hợp để biết phần nào tạo tác dụng. Chưa cố định model hoặc thuật toán cho detector.

**Ablation**

Bỏ từng thành phần như provenance, xử lý nội dung, PII policy hoặc kiểm tra hành động nếu có. Giữ cùng dữ liệu và cấu hình victim để hạn chế yếu tố gây nhiễu.

**Trade-off**

Giảm ASR phải đi cùng utility, chặn nhầm, latency và chi phí. Cấu hình chặn mọi yêu cầu có thể có ASR thấp nhưng không đáp ứng mục tiêu đồ án.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 158. Nguồn dữ liệu và chia tập

Tách dữ liệu tác vụ khỏi nhãn đánh giá

**Dữ liệu tác vụ**

Dùng tài liệu công khai hoặc dữ liệu tổng hợp có nguồn và quyền sử dụng rõ ràng. PII dùng dữ liệu giả. Mỗi episode có yêu cầu hợp lệ, nguồn ngoài, điểm chèn và điều kiện đúng.

**Dữ liệu tấn công và lành**

Tạo ca theo các cơ chế đã khảo sát, biến thể tiếng Việt/Anh và hard negatives. Có cả đoạn nghiên cứu trích payload, chính sách hợp lệ yêu cầu liên hệ và nội dung kỹ thuật chứa lệnh.

**Chống rò giữa các tập**

Chia theo tác vụ gốc, template và nguồn sinh. Không để bản diễn đạt lại của cùng payload nằm cả train/dev/test. Khóa test trước khi tối ưu và giữ một phần ca viết tay độc lập.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 159. Benchmark detector và hệ thống

Hai câu hỏi đánh giá khác nhau

**Detector-only**

Đo precision, recall, F1 và FPR tại ngưỡng được chọn trên dev. Báo cáo riêng hard-benign, obfuscation, tiếng Việt và dữ liệu khác nguồn. Nhãn PI đúng chưa chứng minh tác vụ được bảo vệ.

**End-to-end**

Chấm attacker có đạt mục tiêu tại đầu ra hoặc sink cụ thể. Đồng thời chấm nhiệm vụ hợp lệ và secure task success. Lưu raw/parsed context cùng trace đã che dữ liệu nhạy cảm.

**Cổng pilot**

Nếu victim nền gần như không bị tấn công trên dev, cần xem lại độ mạnh payload hoặc độ phù hợp tác vụ trước khi khóa test. Không sửa test để tạo kết quả đẹp.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 160. Benchmark công cộng để đối chiếu

Chọn theo threat model, không cộng điểm khác chuẩn

**Văn bản gián tiếp**

BIPIA phục vụ indirect injection. Nếu chuyển dữ liệu thành episode riêng thì ghi BIPIA-derived. Detector benchmark cần kiểm tra split, hard-benign và điều kiện cấp phép.

**Tool và agent**

InjecAgent và AgentDojo phù hợp khi có tool calls và trạng thái thực thi. AgentPI của survey nhấn mạnh tác vụ cần phụ thuộc ngữ cảnh. Chỉ chạy khi harness hỗ trợ đúng khả năng.

**Cách báo cáo**

Tách kết quả chạy nguyên benchmark, kết quả bản chuyển đổi và bộ tự xây. Ghi phiên bản, manifest, ngân sách, cấu hình và oracle. Không gọi bộ tự xây là benchmark công cộng.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 161. Oracle và các ca không kết luận

Tránh để judge quyết định mọi kết quả

**Điều kiện xác định bằng code**

Dùng dữ kiện chuẩn, tên tool, tham số, quyền và request tại sink để chấm khi có thể. PII bị hỏi, PII xuất hiện và PII truyền sai đích phải có nhãn riêng.

**Ca cần diễn giải**

Nếu dùng người hoặc LLM judge cho ý định và chất lượng, cần rubric, kiểm tra mẫu và xử lý bất đồng. H14/G03 cho thấy chính nội dung bị chấm có thể điều khiển judge.

**Bất định thống kê**

Giữ nhãn inconclusive khi không đủ bằng chứng. Bootstrap theo tác vụ gốc và báo cáo khoảng tin cậy. Các họ có ít mẫu chỉ phân tích mô tả, không kết luận vượt trội riêng từng họ.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 162. Các bước triển khai và nghiệm thu

Chỉ đánh dấu hoàn tất khi có bằng chứng hoạt động

**Bước 1 và 2**

Chốt threat model, chính sách PII và tiêu chí thành công. Tạo harness, dữ liệu pilot, oracle và mốc không guardrail trước khi ghép nhiều lớp phòng thủ.

**Bước 3 và 4**

Tích hợp từng lớp phương pháp. Kiểm tra backend từng điểm chặn. Nếu có UI thì CUA khi cần để xác nhận luồng thật. Chỉ tick ACCEPTED khi có log hoặc kết quả tái chạy được.

**Bước 5**

Khóa protocol và test, chạy so sánh/ablation, phân tích lỗi rồi viết báo cáo. Theo dõi từng việc bằng trạng thái TODO, DOING, VERIFIED, ACCEPTED cùng người nghiệm thu và đường dẫn bằng chứng.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 163. Các phần nhóm cần hiểu trước khi làm

Reading gates để tránh triển khai hộp đen

**Cơ chế và phạm vi**

Đọc survey §2–4, giải thích được nguồn nào là dữ liệu và ai có quyền giao chỉ dẫn. Dùng H04/G02/S03 để phân biệt task hijack, privacy solicitation và exfiltration.

**Phòng thủ**

Đọc bài gốc của phương pháp dự định dùng: phát hiện/loại bỏ, phân tách instruction/data và policy. Nêu được phương pháp nhìn thấy gì, bỏ sót gì và có thể chặn nhầm thế nào.

**Đánh giá**

Đọc BIPIA và các hồ sơ đánh giá liên quan trong research. Giải thích được split leakage, over-defense, oracle và giới hạn judge trước khi chốt bộ thí nghiệm.

Nguồn: https://arxiv.org/abs/2602.10453

---

## Slide 164. Nội dung xin ý kiến giảng viên

Chốt phạm vi và câu hỏi nghiên cứu

**Phạm vi đề xuất**

AI Guardrails phòng chống Prompt Injection ở mức văn bản. Trọng tâm giảm việc làm theo chỉ dẫn chèn mà vẫn giữ khả năng hoàn tất nhiệm vụ. PII là chính sách hỗ trợ được đo riêng.

**Câu hỏi nghiên cứu**

Các lớp phát hiện, phân tách nội dung và thực thi chính sách kết hợp ra sao? Mức giảm tấn công đánh đổi bao nhiêu utility, chặn nhầm và chi phí? Các biến thể tiếng Việt ảnh hưởng thế nào?

**Quyết định chưa chốt**

Model, thuật toán cụ thể, quy mô dữ liệu và môi trường minh họa sẽ chọn sau khi thống nhất phạm vi và pilot. Phần khảo sát rộng dùng để giải thích lựa chọn, không phải cam kết tái triển khai mọi paper.

Nguồn: https://arxiv.org/abs/2602.10453