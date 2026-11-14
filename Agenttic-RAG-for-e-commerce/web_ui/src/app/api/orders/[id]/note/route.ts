import { createOrderHandlers } from '@/lib/server/order-handlers';
import { paymentDependencies } from '@/lib/server/payment-runtime';

export const runtime = 'nodejs';
export async function PATCH(request: Request, context: { params: Promise<{ id: string }> }) {
  return createOrderHandlers(paymentDependencies).note(request, (await context.params).id);
}
