import type Stripe from 'stripe';

export class OrderError extends Error {
  constructor(public code: string, public status: number, message: string) { super(message); }
}
export interface OrderInput {
  items: { product_id: number; quantity: number }[];
  payment_method: 'stripe' | 'cod';
  recipient_name: string; recipient_phone: string; address_line: string;
  ward: string; province: string; note: string;
}
export interface OrderRecord {
  id: string; user_id: string; status: string; payment_status: string;
  payment_method: 'stripe' | 'cod'; total: number;
  items: { product_id: number; name: string; price: number; quantity: number; image?: string | null }[];
  recipient_name: string | null; recipient_phone: string | null; address_line: string | null;
  ward: string | null; province: string | null; note: string; created_at: string;
}
export function invalidField(): never { throw new OrderError('INVALID_FIELD', 400, 'Thông tin đặt hàng không hợp lệ.'); }
export function parseNote(value: unknown): string {
  if (typeof value !== 'string' || Array.from(value).length > 500) invalidField();
  return value;
}
function field(value: unknown, max: number): string {
  if (typeof value !== 'string') invalidField();
  const text = value.trim();
  if (!text || Array.from(text).length > max) invalidField();
  return text;
}
export function parseOrderInput(value: unknown): OrderInput {
  if (!value || typeof value !== 'object' || Array.isArray(value)) invalidField();
  const body = value as Record<string, unknown>;
  if (!Array.isArray(body.items)) invalidField();
  if (!body.items.length) throw new OrderError('EMPTY_CART', 400, 'Giỏ hàng trống.');
  if (body.items.length > 100 || (body.payment_method !== 'stripe' && body.payment_method !== 'cod')) invalidField();
  const quantities = new Map<number, number>();
  for (const item of body.items) {
    if (!item || typeof item !== 'object') invalidField();
    const { product_id, quantity } = item;
    if (!Number.isSafeInteger(product_id) || product_id <= 0 || product_id > 2147483647
      || !Number.isSafeInteger(quantity) || quantity <= 0 || quantity > 10000) invalidField();
    const totalQuantity = (quantities.get(product_id) || 0) + quantity;
    if (totalQuantity > 10000) invalidField();
    quantities.set(product_id, totalQuantity);
  }
  return {
    items: Array.from(quantities, ([product_id, quantity]) => ({ product_id, quantity })),
    payment_method: body.payment_method,
    recipient_name: field(body.recipient_name, 200), recipient_phone: field(body.recipient_phone, 30),
    address_line: field(body.address_line, 500), ward: field(body.ward, 200), province: field(body.province, 200),
    note: body.note === undefined ? '' : parseNote(body.note),
  };
}
export function validOrderId(id: string): boolean {
  return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(id);
}
export function checkoutParams(order: OrderRecord, origin: string): Stripe.Checkout.SessionCreateParams {
  if (!validOrderId(order.id) || !order.items.length || !Number.isSafeInteger(Number(order.total))) throw Error('Invalid order snapshot');
  let total = 0;
  const line_items = order.items.map(item => {
    if (!Number.isSafeInteger(item.price) || item.price < 0 || !Number.isSafeInteger(item.quantity) || item.quantity <= 0) throw Error('Invalid order snapshot');
    total += item.price * item.quantity;
    return { price_data: { currency: 'vnd', product_data: { name: item.name }, unit_amount: item.price }, quantity: item.quantity };
  });
  if (total !== Number(order.total)) throw Error('Invalid order snapshot');
  return {
    mode: 'payment', payment_method_types: ['card'], line_items,
    metadata: { order_id: order.id }, client_reference_id: order.id,
    success_url: `${origin}/checkout-success?order_id=${order.id}&session_id={CHECKOUT_SESSION_ID}`,
    cancel_url: `${origin}/cart`,
  };
}
export function orderSummary(order: OrderRecord) {
  return { order_id: order.id, status: order.status, payment_status: order.payment_status, total: Number(order.total) };
}
export function orderDetail(order: OrderRecord) {
  return {
    ...orderSummary(order), payment_method: order.payment_method, items: order.items,
    recipient_name: order.recipient_name, recipient_phone: order.recipient_phone,
    address_line: order.address_line, ward: order.ward, province: order.province,
    note: order.note, created_at: order.created_at,
  };
}
