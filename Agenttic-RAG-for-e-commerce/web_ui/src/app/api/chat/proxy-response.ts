export interface FormattedErrorResponse {
  error: {
    code: string;
    message: string;
  };
}

export function formatBackend4xxError(status: number): FormattedErrorResponse {
  switch (status) {
    case 401:
      return {
        error: {
          code: 'UNAUTHENTICATED',
          message: 'Phiên làm việc đã hết hạn hoặc không hợp lệ. Vui lòng đăng nhập lại.',
        },
      };
    case 403:
      return {
        error: {
          code: 'FORBIDDEN',
          message: 'Bạn không có quyền thực hiện yêu cầu này.',
        },
      };
    case 422:
      return {
        error: {
          code: 'INVALID_REQUEST',
          message: 'Dữ liệu yêu cầu không hợp lệ hoặc vượt quá giới hạn cho phép.',
        },
      };
    default:
      return {
        error: {
          code: 'BAD_REQUEST',
          message: 'Yêu cầu không hợp lệ. Vui lòng kiểm tra lại thông tin.',
        },
      };
  }
}

export function formatBackend503Error(): FormattedErrorResponse {
  return {
    error: {
      code: 'BACKEND_UNAVAILABLE',
      message: 'Hệ thống AI tư vấn hiện đang tạm thời gián đoạn kết nối. Vui lòng thử lại sau ít phút hoặc tạo ticket để nhân viên hỗ trợ trực tiếp.',
    },
  };
}
