import { createOrderHandlers } from '@/lib/server/order-handlers';
import { paymentDependencies } from '@/lib/server/payment-runtime';

export const runtime = 'nodejs';
export async function GET(request: Request, context: { params: Promise<{ id: string }> }) {
  return createOrderHandlers(paymentDependencies).detail(request, (await context.params).id);
}
