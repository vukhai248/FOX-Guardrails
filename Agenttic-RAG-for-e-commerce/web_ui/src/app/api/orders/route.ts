import { createOrderHandlers } from '@/lib/server/order-handlers';
import { paymentDependencies } from '@/lib/server/payment-runtime';

export const runtime = 'nodejs';
export async function POST(request: Request) {
  return createOrderHandlers(paymentDependencies).create(request);
}
