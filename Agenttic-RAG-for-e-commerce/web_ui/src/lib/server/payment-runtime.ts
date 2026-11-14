import 'server-only';
import { createClient } from '@supabase/supabase-js';
import Stripe from 'stripe';
import { OrderError, type OrderRecord } from './order-core';
import type { PaymentDependencies } from './order-handlers';

function required(name: string): string {
  const value = process.env[name];
  if (!value) throw new OrderError('SERVICE_UNAVAILABLE', 503, 'Chưa cấu hình dịch vụ phía server.');
  return value;
}
function database(admin: boolean) {
  return createClient(required('NEXT_PUBLIC_SUPABASE_URL'), required(admin ? 'SUPABASE_SERVICE_ROLE_KEY' : 'NEXT_PUBLIC_SUPABASE_ANON_KEY'), {
    auth: { autoRefreshToken: false, persistSession: false },
  });
}
export function testStripeClient(): Stripe {
  const key = required('STRIPE_SECRET_KEY');
  if (!key.startsWith('sk_test_')) throw new OrderError('SERVICE_UNAVAILABLE', 503, 'Thanh toán chỉ cho phép Stripe test mode.');
  return new Stripe(key, { maxNetworkRetries: 2, timeout: 20000 });
}
export function shopOrigin(): string {
  const url = new URL(process.env.APP_URL || 'http://localhost:3000');
  if (url.username || url.password || (url.protocol !== 'https:' && !(url.protocol === 'http:' && ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)))) {
    throw new OrderError('SERVICE_UNAVAILABLE', 503, 'APP_URL không hợp lệ.');
  }
  return url.origin;
}
const columns = 'id,user_id,status,payment_status,payment_method,total,items,recipient_name,recipient_phone,address_line,ward,province,note,created_at';
export const paymentDependencies: PaymentDependencies = {
  async authenticate(token) {
    const { data, error } = await database(false).auth.getUser(token);
    return error ? null : data.user?.id || null;
  },
  async rpc(name, args) {
    const { data, error } = await database(true).rpc(name, args);
    if (error) throw new Error(error.message);
    return data;
  },
  async getOrder(id, userId) {
    const { data, error } = await database(true).from('orders').select(columns).eq('id', id).eq('user_id', userId).maybeSingle();
    if (error) throw Error('Order read failed');
    return data as OrderRecord | null;
  },
  async updateNote(id, userId, note) {
    const { data, error } = await database(true).from('orders').update({ note }).eq('id', id).eq('user_id', userId).eq('status', 'pending').select('id,note').maybeSingle();
    if (error) throw Error('Order note update failed');
    return data;
  },
  async createCheckout(params, key) { return testStripeClient().checkout.sessions.create(params, { idempotencyKey: key }); },
  async expireCheckout(id) { await testStripeClient().checkout.sessions.expire(id); },
  verifyEvent(body, signature) { return testStripeClient().webhooks.constructEvent(body, signature, required('STRIPE_WEBHOOK_SECRET')); },
  shopOrigin,
};
