# Claude review C1/C2 — 03/11/2026

Base: ad5658d, feat/a-backend. Source: FOX-Guardrails/docs/plans/prompts/codex-phanA.md, nghiệm thu Claude 03/11.

## Đã làm gì

- C1: kiểm chứng catch của finalize_stripe_order luôn trả 503. Phân biệt PAYMENT_MISMATCH/NOT_FOUND/NOT_EDITABLE để acknowledge 200 và console.error chỉ có order_id/mã lỗi; lỗi kho/kết nối/không xác định vẫn retry 503.
- C2: nhận đính chính hợp đồng admin chat-logs chuẩn là object `{chat_logs,total,limit,offset}`; sửa requests.md, không sửa route frontend.

## File đổi

- web_ui/src/lib/server/order-handlers.ts, __tests__/orders.test.cjs.
- docs/reports/requests.md và báo cáo này.

## Kiểm thử

Tại repo root, TDD RED: orders.test.cjs **3 failed, 32 passed** (các lỗi vĩnh viễn trả 503).

```powershell
$env:PGLITE_MODULE_PATH='D:/create/DATN/.test-tools/a2/node_modules/@electric-sql/pglite'
node --test web_ui/src/lib/server/__tests__/*.test.cjs
```

GREEN: **57 tests, 57 pass, 0 fail, 0 skipped**. TypeScript `npx.cmd tsc --noEmit --incremental false` và eslint `src/lib/server/order-handlers.ts` exit 0 tại web_ui. Test kiểm lỗi thiếu kho và lỗi kết nối vẫn 503, lỗi vĩnh viễn 200, log chỉ chứa order_id/mã đã nhận diện; không log raw lỗi DB/PII.

## Còn mở

- Acknowledge lỗi vĩnh viễn không tự sửa dữ liệu/thanh toán; cần đối soát qua order_id và mã lỗi được ghi.
- Không chạy SQL, migration, Stripe thật hoặc thay UI. A5-backend là gói kế tiếp; A7 ghi credentials tại gốc repo, role admin trong user_roles như review.
