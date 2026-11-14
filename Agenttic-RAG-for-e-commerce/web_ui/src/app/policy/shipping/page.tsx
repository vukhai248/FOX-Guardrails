import React from 'react';

export default function ShippingPolicyPage() {
  return (
    <div className="max-w-4xl mx-auto px-4 py-12 text-slate-300">
      <h1 className="text-3xl font-extrabold text-white mb-8 border-b border-slate-800 pb-4">
        Chính Sách Vận Chuyển Và Giao Nhận
      </h1>

      <p className="mb-6 leading-relaxed">
        Chúng tôi luôn nỗ lực tối đa để mang sản phẩm công nghệ đến tay quý khách một cách nhanh chóng, an toàn và tiết kiệm nhất. Dưới đây là quy định chi tiết về phí vận chuyển, thời gian giao nhận và các điều khoản đồng kiểm khi nhận hàng.
      </p>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">1. Phạm Vi Áp Dụng Và Phí Vận Chuyển</h2>
        <p className="mb-4">Chúng tôi hỗ trợ giao hàng tận nhà trên toàn quốc (tất cả 63 tỉnh thành Việt Nam) với mức phí cụ thể như sau:</p>
        
        <div className="overflow-x-auto mb-4">
          <table className="w-full text-left border-collapse border border-slate-850">
            <thead>
              <tr className="bg-slate-900 text-white">
                <th className="p-3 border border-slate-800">Giá trị đơn hàng</th>
                <th className="p-3 border border-slate-800">Phương thức vận chuyển</th>
                <th className="p-3 border border-slate-800">Cước phí giao hàng</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-slate-800">
                <td className="p-3 font-semibold text-white">Từ 1.000.000 VNĐ trở lên</td>
                <td className="p-3">Giao hàng tiêu chuẩn toàn quốc</td>
                <td className="p-3 text-emerald-400 font-semibold">MIỄN PHÍ VẬN CHUYỂN (Freeship)</td>
              </tr>
              <tr className="border-b border-slate-800">
                <td className="p-3 font-semibold text-white">Dưới 1.000.000 VNĐ</td>
                <td className="p-3">Giao hàng tiêu chuẩn toàn quốc</td>
                <td className="p-3">Đồng giá 30.000 VNĐ / Đơn hàng</td>
              </tr>
              <tr>
                <td className="p-3 font-semibold text-white">Mọi đơn hàng (Nội thành Hà Nội & TP.HCM)</td>
                <td className="p-3">Giao hàng hỏa tốc (nhận hàng trong 2 giờ)</td>
                <td className="p-3">Đồng giá 50.000 VNĐ / Đơn hàng</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">2. Thời Gian Giao Nhận Dự Kiến</h2>
        <p className="mb-3">Thời gian giao hàng tính từ lúc nhân viên gọi điện xác nhận đơn hàng thành công hoặc hệ thống nhận thanh toán tự động qua Stripe:</p>
        <ul className="list-disc pl-6 space-y-2 leading-relaxed">
          <li><strong>Giao hàng Hỏa tốc 2 giờ:</strong> Áp dụng cho các quận nội thành Hà Nội và TP.Hồ Chí Minh, nhận hàng trong vòng 2 giờ sau khi xác nhận. Thời gian tiếp nhận đơn hỏa tốc từ 8:00 đến 18:00 hàng ngày.</li>
          <li><strong>Khu vực Hà Nội và TP.Hồ Chí Minh (giao thường):</strong> Thời gian từ 1 đến 2 ngày làm việc.</li>
          <li><strong>Khu vực Trung tâm Tỉnh/Thành phố lớn khác:</strong> Thời gian từ 2 đến 3 ngày làm việc.</li>
          <li><strong>Khu vực Huyện/Xã vùng sâu vùng xa:</strong> Thời gian từ 3 đến 5 ngày làm việc.</li>
        </ul>
        <p className="mt-3 text-sm italic text-slate-400">Lưu ý: Thời gian giao hàng có thể kéo dài hơn dự kiến trong các dịp lễ Tết, thiên tai hoặc các sự kiện bất khả kháng do nhà vận chuyển gặp quá tải cục bộ.</p>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">3. Quy Định Đồng Kiểm Khi Nhận Hàng (Quan trọng)</h2>
        <p className="mb-3">Đối với các sản phẩm công nghệ giá trị cao (Điện thoại, Laptop, Đồng hồ), nhằm đảm bảo quyền lợi tối đa cho quý khách và tránh tranh chấp rủi ro trong quá trình vận chuyển:</p>
        <ul className="list-disc pl-6 space-y-2 leading-relaxed">
          <li>Quý khách hoàn toàn <strong>có quyền mở gói hàng kiểm tra ngoại quan sản phẩm</strong> (đúng mẫu mã, màu sắc, số lượng, hộp nguyên vẹn không móp méo) trước khi ký nhận hàng từ shipper.</li>
          <li><strong>Lưu ý:</strong> Không được phép tự ý bóc seal ni lông của sản phẩm điện thoại/máy tính hoặc cắm điện kích hoạt máy lên test thử khi chưa ký thanh toán/nhận hàng.</li>
          <li><strong className="text-white">Khuyến nghị đặc biệt:</strong> Quý khách nên <strong>quay lại video clip toàn bộ quá trình mở hộp hàng (unboxing)</strong>. Video này sẽ là bằng chứng thép có giá trị pháp lý cao nhất để chúng tôi hỗ trợ đổi trả hàng ngay lập tức nếu sản phẩm bị hư hại vật lý (nứt vỡ, móp méo) do đơn vị vận chuyển gây ra.</li>
        </ul>
      </section>

      <section className="mb-8">
        <h2 className="text-xl font-bold text-white mb-4">4. Xử Lý Rủi Ro Thất Lạc Hoặc Hư Hỏng</h2>
        <ul className="list-disc pl-6 space-y-2 leading-relaxed">
          <li>Nếu đơn hàng quá 5 ngày chưa được giao tới và không nhận được cuộc gọi từ shipper, quý khách vui lòng mở chat hỗ trợ và cung cấp mã đơn hàng để nhân viên hỗ trợ tra cứu hành trình hoặc làm việc với hãng vận chuyển (Giao Hàng Nhanh, Viettel Post...).</li>
          <li>Trong trường hợp xấu nhất hàng hóa bị xác nhận thất lạc do đơn vị giao vận, chúng tôi cam kết sẽ <strong>chuyển phát lại một sản phẩm mới tương đương</strong> hoặc <strong>hoàn trả 100% tiền thanh toán</strong> cho quý khách mà không chịu thêm bất cứ chi phí phát sinh nào.</li>
        </ul>
      </section>
    </div>
  );
}
