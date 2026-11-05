"""Lớp 3 demo: một phiên chat đi qua 3 trạm, PII bị giả danh hoá rồi hoàn nguyên đúng chủ.

Chạy (tại D:/create/DATN/.worktrees/b-core): ./.venv/Scripts/python.exe -X utf8 scripts/demo_lop3.py
"""

from fox_guard import Guard, GuardContext

guard = Guard()
A = {"session_id": "demo", "user_ref": "khach-A"}


def show(title, decision):
    print(f"{title}\n   action={decision.action}  text={decision.text}")


show("1. INPUT  (khách A gõ, gửi LLM):",
     guard.check_input("SĐT mình 0 9 1 2 . 3 4 5 . 6 7 8, CCCD 079203001234, đổi giúp số nhận hàng",
                       GuardContext(station="input", **A)))
order = ("Người nhận: Nguyễn Văn An, SĐT 0987654321, "
         "12 Lý Thường Kiệt, phường Hàng Bài, quận Hoàn Kiếm, Hà Nội")
show("2. CONTEXT (tool tra đơn của khách A, hỏi 'đơn tới đâu rồi'):",
     guard.check_context(order, GuardContext(station="context", source="tool:order_lookup",
                                             intent="order_status", **A)))
show("3. CONTEXT (review của người khác):",
     guard.check_context("Anh Trần Minh Khoa sđt 0901234567 khen máy chạy êm",
                         GuardContext(station="context", source="review", **A)))
answer = "Dạ shop sẽ gọi <PHONE_1> để xác nhận, CCCD <CCCD_1> đã ghi nhận. Mã lạ: <PHONE_9>"
show("4. OUTPUT cho chính khách A:", guard.check_output(answer, GuardContext(station="output", **A)))
show("5. OUTPUT nếu người khác đọc được:",
     guard.check_output(answer, GuardContext(station="output", session_id="demo", user_ref="khach-B")))
show("6. OUTPUT bot lỡ in số thẻ và OTP:",
     guard.check_output("Thẻ 4242 4242 4242 4242, mã OTP là 482913", GuardContext(station="output", **A)))
print("7. LOG (che không hoàn nguyên được):\n  ",
      guard.redact_for_log("SĐT 0912345678, <PHONE_1>, thẻ 4242424242424242, mk: Abc@12345",
                           GuardContext(station="output", **A)))
