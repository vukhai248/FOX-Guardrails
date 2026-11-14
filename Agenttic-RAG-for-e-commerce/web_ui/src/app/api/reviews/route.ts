import { createReviewHandler } from '@/lib/server/review-handlers';
import { paymentDependencies } from '@/lib/server/payment-runtime';

export const POST = createReviewHandler(paymentDependencies);
