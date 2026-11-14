import React from 'react';

export default function ReturnPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-slate-300">
      <h1 className="text-3xl font-extrabold text-white mb-8 border-b border-slate-800 pb-4">
        Chính Sách Đổi Trả Và Hoàn Tiền
      </h1>

      <p className="mb-6 leading-relaxed">
        Nhằm mang lại sự an tâm tuyệt đối khi mua sắm tại cửa hàng của chúng tôi, chúng tôi áp dụng chính sách đổi trả sản phẩm linh hoạt và minh bạch. Qúy khách vui lòng đọc kỹ các điều khoản dưới đây để biết rõ điều kiện đổi mới hoặc hoàn tiền đối với từng dòng sản phẩm.
      </p>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">1. Quy Định Đổi Trả Theo Thời Gian (Lỗi Nhà Sản Xuất)</h2>
        <p className="mb-4">Nếu sản phẩm phát sinh lỗi kỹ thuật từ nhà sản xuất trong thời gian đầu sử dụng, quý khách được quyền đổi mới sản phẩm miễn phí hoặc hoàn trả lấy tiền mặt theo bảng thời hạn sau:</p>
        
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-left border-collapse border border-slate-850">
            <thead>
              <tr className="bg-slate-900 text-white">
                <th className="p-3 border border-slate-800">Loại sản phẩm</th>
                <th className="p-3 border border-slate-800">Thời gian đổi trả miễn phí</th>
                <th className="p-3 border border-slate-800">Chính sách xử lý</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800">
                <td className="p-3 font-semibold text-white">Laptop & Điện thoại</td>
                <td className="p-3">30 ngày đầu tiên kể từ ngày nhận hàng</td>
                <td className="p-3">Đổi sản phẩm mới cùng dòng hoặc hoàn tiền 100% nếu hết hàng</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="p-3 font-semibold text-white">Đồng hồ thông minh & Tai nghe</td>
                <td className="p-3">15 ngày đầu tiên kể từ ngày nhận hàng</td>
                <td className="p-3">1 đổi 1 sang sản phẩm mới cùng model</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-white">Phụ kiện công nghệ</td>
                <td className="p-3">7 ngày đầu tiên kể từ ngày nhận hàng</td>
                <td className="p-3">Đổi mới phụ kiện cùng loại</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">2. Điều Kiện Để Được Đổi Trả Sản Phẩm</h2>
        <p className="mb-3">Sản phẩm hoàn trả phải đáp ứng đầy đủ các tiêu chuẩn kiểm định sau:</p>
        <ul className="list-disc pl-6 space-y-2 leading-relaxed">
          <li>Sản phẩm phải còn nguyên trạng thái như khi nhận: Không trầy xước vỏ, không móp méo, không có vết nứt vỡ cơ học.</li>
          <li>Đầy đủ vỏ hộp ban đầu (hộp phải trùng khớp số Serial/IMEI với thân máy), các xốp chèn bảo vệ bên trong hộp.</li>
          <li>Có đầy đủ các phụ kiện kèm theo trong hộp (Cáp sạc, củ sạc, sách hướng dẫn sử dụng, tai nghe tặng kèm nếu có).</li>
          <li>Quà tặng kèm theo chương trình khuyến mãi (nếu có) phải được trả lại cùng sản phẩm chính. Nếu không trả lại quà tặng, chúng tôi sẽ trừ tiền quà tặng theo giá trị niêm yết khi hoàn tiền.</li>
          <li>Có đầy đủ hóa đơn mua hàng (Hóa đơn đỏ VAT hoặc hóa đơn điện tử gửi qua email của quý khách).</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">3. Chính Sách Đổi Trả Theo Nhu Cầu (Không Có Lỗi Kỹ Thuật)</h2>
        <p className="mb-3">Trường hợp sản phẩm hoạt động hoàn toàn bình thường nhưng quý khách muốn đổi sang màu khác, dòng khác hoặc hoàn trả do thay đổi nhu cầu cá nhân (Không áp dụng cho phụ kiện giá dưới 500k hoặc sản phẩm đã bị bóc seal hộp đối với điện thoại/tai nghe):</p>
        <ul className="list-disc pl-6 space-y-2 leading-relaxed">
          <li><strong>Trong vòng 7 ngày đầu:</strong> Hỗ trợ trả lại sản phẩm thu phí khấu hao 10% giá trị sản phẩm trên hóa đơn. Hoặc đổi sang sản phẩm khác bằng hoặc cao tiền hơn miễn phí (quý khách tự bù tiền chênh lệch).</li>
          <li><strong>Từ ngày thứ 8 đến ngày thứ 15:</strong> Hỗ trợ trả lại sản phẩm thu phí khấu hao 20% giá trị sản phẩm.</li>
          <li><strong>Sau 15 ngày:</strong> Chúng tôi từ chối tiếp nhận đổi trả sản phẩm đối với các trường hợp đổi trả không do lỗi phần cứng nhà sản xuất.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">4. Quy Trình Trả Hàng Và Nhận Hoàn Tiền</h2>
        <ol className="list-decimal pl-6 space-y-3 leading-relaxed">
          <li>
            <strong className="text-white">Bước 1: Đăng ký yêu cầu.</strong> Quý khách gọi hotline hỗ trợ hoặc thông báo cho chatbot trên website yêu cầu đổi/trả hàng. Bạn cần cung cấp mã đơn hàng (OrderID) để kiểm tra thời gian hợp lệ.
          </li>
          <li>
            <strong className="text-white">Bước 2: Gửi hàng về trung tâm.</strong> Đóng gói sản phẩm cẩn thận kèm đầy đủ hộp và phụ kiện để chuyển phát về kho bảo quản chính hoặc đem tới cửa hàng trực tiếp.
          </li>
          <li>
            <strong className="text-white">Bước 3: Thẩm định chất lượng.</strong> Bộ phận kiểm kho sẽ nhận hàng và tiến hành thẩm định ngoại quan + test phần cứng của thiết bị trong vòng 24 giờ.
          </li>
          <li>
            <strong className="text-white">Bước 4: Thực hiện hoàn tiền.</strong> Sau khi sản phẩm được chấp thuận hoàn trả, chúng tôi sẽ thực hiện chuyển khoản lại tiền cho khách hàng:
            <ul className="list-disc pl-6 mt-2 space-y-1">
              <li>Hoàn tiền qua ví điện tử hoặc chuyển khoản ngân hàng: Nhận lại tiền trong <strong>3 đến 5 ngày làm việc</strong>.</li>
              <li>Hoàn tiền qua thẻ tín dụng (nếu thanh toán qua Stripe): Tiền sẽ hoàn lại vào hạn mức thẻ trong vòng <strong>5 đến 10 ngày làm việc</strong> tùy thuộc vào ngân hàng phát hành thẻ của quý khách.</li>
            </ul>
          </li>
        </ol>
      </section>
    </div>
  );
}
