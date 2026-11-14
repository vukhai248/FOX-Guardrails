import 'server-only';
import type { PaymentDependencies } from './order-handlers';

export function createReviewHandler(deps: Pick<PaymentDependencies, 'authenticate' | 'rpc'>) {
  return async function POST(request: Request): Promise<Response> {
    const error = (code: string, status: number, message: string) => Response.json({ error: { code, message } }, { status });
    try {
      const match = request.headers.get('authorization')?.match(/^Bearer\s+(\S+)$/i);
      const userId = match ? await deps.authenticate(match[1]) : null;
      if (!userId) return error('UNAUTHENTICATED', 401, 'Vui lòng đăng nhập để đánh giá.');
      let body;
      try { body = await request.json(); } catch { return error('INVALID_FIELD', 400, 'Thông tin đánh giá không hợp lệ.'); }
      if (!body || typeof body !== 'object' || Array.isArray(body)
        || !Number.isSafeInteger(body.product_id) || body.product_id < 1 || body.product_id > 2147483647
        || !Number.isInteger(body.rating) || body.rating < 1 || body.rating > 5
        || typeof body.comment !== 'string' || Array.from(body.comment).length > 1000) {
        return error('INVALID_FIELD', 400, 'Thông tin đánh giá không hợp lệ.');
      }
      const result = await deps.rpc('create_product_review', {
        p_user_id: userId, p_product_id: body.product_id, p_rating: body.rating, p_comment: body.comment,
      }) as { review_id: string };
      return Response.json({ review_id: result.review_id }, { status: 201 });
    } catch (cause) {
      const code = cause instanceof Error ? cause.message : '';
      if (code === 'NOT_PURCHASED') return error(code, 403, 'Chỉ khách đã mua sản phẩm mới được đánh giá.');
      if (['INVALID_FIELD', 'INVALID_PRODUCT'].includes(code)) return error(code, 400, 'Thông tin đánh giá không hợp lệ.');
      return error('INTERNAL_ERROR', 500, 'Không thể lưu đánh giá lúc này.');
    }
  };
}
