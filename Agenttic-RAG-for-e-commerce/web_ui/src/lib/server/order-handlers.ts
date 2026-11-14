import 'server-only';
import type Stripe from 'stripe';
import { OrderError, checkoutParams, invalidField, orderDetail, orderSummary, parseNote, parseOrderInput, validOrderId, type OrderRecord } from './order-core';

export interface PaymentDependencies {
  authenticate(token: string): Promise<string | null>;
  rpc(name: string, args: Record<string, unknown>): Promise<unknown>;
  getOrder(id: string, userId: string): Promise<OrderRecord | null>;
  updateNote(id: string, userId: string, note: string): Promise<{ id: string; note: string } | null>;
  createCheckout(params: Stripe.Checkout.SessionCreateParams, key: string): Promise<{ id: string; url: string | null; livemode: boolean }>;
  expireCheckout(id: string): Promise<void>;
  verifyEvent(body: string, signature: string): Stripe.Event;
  shopOrigin(): string;
}
function errorResponse(error: unknown): Response {
  if (error instanceof OrderError) return Response.json({ error: { code: error.code, message: error.message } }, { status: error.status });
  const code = error instanceof Error ? error.message : '';
  if (['EMPTY_CART', 'INVALID_PRODUCT', 'OUT_OF_STOCK', 'INVALID_FIELD'].includes(code)) {
    const messages: Record<string, string> = {
      EMPTY_CART: 'Giỏ hàng trống.', INVALID_PRODUCT: 'Sản phẩm không hợp lệ.',
      OUT_OF_STOCK: 'Sản phẩm không đủ tồn kho.', INVALID_FIELD: 'Thông tin không hợp lệ.',
    };
    return Response.json({ error: { code, message: messages[code] } }, { status: 400 });
  }
  return Response.json({ error: { code: 'INTERNAL_ERROR', message: 'Không thể xử lý yêu cầu lúc này.' } }, { status: 500 });
}
async function readBody(request: Request): Promise<Record<string, unknown>> {
  try {
    const body = await request.json();
    if (!body || typeof body !== 'object' || Array.isArray(body)) invalidField();
    return body;
  } catch (error) {
    if (error instanceof OrderError) throw error;
    invalidField();
  }
}
export function createOrderHandlers(deps: PaymentDependencies) {
  async function user(request: Request): Promise<string> {
    const match = request.headers.get('authorization')?.match(/^Bearer\s+(\S+)$/i);
    const userId = match ? await deps.authenticate(match[1]) : null;
    if (!userId) throw new OrderError('UNAUTHENTICATED', 401, 'Vui lòng đăng nhập để tiếp tục.');
    return userId;
  }
  async function owned(id: string, userId: string) {
    const order = validOrderId(id) ? await deps.getOrder(id, userId) : null;
    if (!order) throw new OrderError('NOT_FOUND', 404, 'Không tìm thấy đơn hàng.');
    return order;
  }
  return {
    async create(request: Request): Promise<Response> {
      let order: OrderRecord | undefined;
      let session: { id: string; url: string | null; livemode: boolean } | undefined;
      let checkoutStarted = false;
      try {
        const userId = await user(request);
        const body = parseOrderInput(await readBody(request));
        order = await deps.rpc('create_shop_order', {
          p_user_id: userId, p_items: body.items, p_payment_method: body.payment_method,
          p_recipient_name: body.recipient_name, p_recipient_phone: body.recipient_phone,
          p_address_line: body.address_line, p_ward: body.ward, p_province: body.province, p_note: body.note,
        }) as OrderRecord;
        if (body.payment_method === 'cod') return Response.json(orderSummary(order), { status: 201 });
        checkoutStarted = true;
        session = await deps.createCheckout(checkoutParams(order, deps.shopOrigin()), `order:${order.id}`);
        if (session.livemode !== false || !session.id.startsWith('cs_test_') || !session.url) throw Error('Invalid test Checkout session');
        await deps.rpc('attach_stripe_session', { p_order_id: order.id, p_session_id: session.id });
        return Response.json({ ...orderSummary(order), checkout_url: session.url }, { status: 201 });
      } catch (error) {
        if (checkoutStarted && order) {
          // An uncertain expiration leaves an unpaid order for signed-webhook reconciliation.
          let canFailOrder = !session;
          if (session) {
            try { await deps.expireCheckout(session.id); canFailOrder = true; } catch { /* Retry/reconcile externally. */ }
          }
          if (canFailOrder) {
            try { await deps.rpc('fail_stripe_order', { p_order_id: order.id }); } catch { /* Preserve unpaid order for reconciliation. */ }
          }
          return errorResponse(new OrderError('PAYMENT_UNAVAILABLE', 503, 'Dịch vụ thanh toán tạm thời chưa sẵn sàng. Vui lòng thử lại sau.'));
        }
        return errorResponse(error);
      }
    },
    async detail(request: Request, id: string): Promise<Response> {
      try { return Response.json(orderDetail(await owned(id, await user(request)))); }
      catch (error) { return errorResponse(error); }
    },
    async note(request: Request, id: string): Promise<Response> {
      try {
        const userId = await user(request);
        const order = await owned(id, userId);
        const note = parseNote((await readBody(request)).note);
        if (order.status !== 'pending') throw new OrderError('NOT_EDITABLE', 409, 'Chỉ được sửa ghi chú của đơn đang chờ xử lý.');
        const updated = await deps.updateNote(id, userId, note);
        if (!updated) throw new OrderError('NOT_EDITABLE', 409, 'Đơn hàng không còn cho phép sửa ghi chú.');
        return Response.json({ order_id: updated.id, note: updated.note });
      } catch (error) { return errorResponse(error); }
    },
    async webhook(request: Request): Promise<Response> {
      let event: Stripe.Event;
      try {
        const signature = request.headers.get('stripe-signature');
        if (!signature) throw Error('Missing signature');
        event = deps.verifyEvent(await request.text(), signature);
      } catch (error) {
        if (error instanceof OrderError) return errorResponse(error);
        return errorResponse(new OrderError('INVALID_SIGNATURE', 400, 'Chữ ký webhook không hợp lệ.'));
      }
      if (event.livemode !== false) return errorResponse(new OrderError('INVALID_EVENT', 400, 'Chỉ chấp nhận Stripe test mode.'));
      if (!['checkout.session.completed', 'checkout.session.async_payment_succeeded', 'checkout.session.expired'].includes(event.type)) return Response.json({ received: true });
      const session = event.data.object as Stripe.Checkout.Session;
      if (!session || session.livemode !== false || session.mode !== 'payment' || typeof session.id !== 'string' || !session.id.startsWith('cs_test_')) {
        return errorResponse(new OrderError('INVALID_EVENT', 400, 'Checkout session không hợp lệ.'));
      }
      const expired = event.type === 'checkout.session.expired';
      if (expired && session.payment_status === 'paid') return Response.json({ received: true });
      if (!expired && session.payment_status !== 'paid') return Response.json({ received: true });
      const orderId = session.metadata?.order_id;
      if (typeof orderId !== 'string' || !validOrderId(orderId)
        || (!expired && (!Number.isSafeInteger(session.amount_total) || session.amount_total! < 0 || session.currency !== 'vnd'))) {
        return errorResponse(new OrderError('INVALID_EVENT', 400, 'Thông tin thanh toán không hợp lệ.'));
      }
      try {
        if (expired) {
          await deps.rpc('fail_stripe_order', { p_order_id: orderId, p_session_id: session.id });
        } else {
          await deps.rpc('finalize_stripe_order', {
            p_order_id: orderId, p_session_id: session.id, p_amount_total: session.amount_total, p_currency: session.currency,
          });
        }
        return Response.json({ received: true });
      } catch (error) {
        const code = error instanceof Error ? error.message : '';
        if (['PAYMENT_MISMATCH', 'NOT_FOUND', 'NOT_EDITABLE', 'INVALID_PRODUCT'].includes(code)) {
          console.error({ order_id: orderId, code });
          return Response.json({ received: true });
        }
        return errorResponse(new OrderError('WEBHOOK_RETRY', 503, 'Chưa thể xác nhận đơn hàng; webhook cần được gửi lại.'));
      }
    },
  };
}
