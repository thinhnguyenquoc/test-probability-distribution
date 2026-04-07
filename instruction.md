1. Tính toán khoảng cách di chuyển (Δr) Đầu tiên, bạn sử dụng tọa độ lat-lon của zone 1 và zone 2 để tính khoảng cách không gian thực tế, ký hiệu là Δr, cho từng cặp origin-destination (O-D) trong dữ liệu của bạn
.
2. Xây dựng hàm mật độ xác suất P(Δr) Sử dụng cột count làm tần suất (số lượng chuyến đi cho mỗi khoảng cách Δr). Bạn chia số lượng này cho tổng số chuyến đi trong toàn bộ tập dữ liệu để tìm ra xác suất P(Δr)
. Sau đó, hãy vẽ đồ thị biểu diễn phân phối P(Δr) này trên thang đo log-log (cả trục tung và trục hoành đều là logarit)
.
3. Khớp mô hình với hàm Truncated Lévy Flight Mô hình di chuyển con người hiếm khi là một Lévy flight thuần túy mà thường là mô hình bị cắt cụt (truncated Lévy flight) ở phần đuôi do giới hạn về không gian địa lý
. Bạn hãy sử dụng các phần mềm thống kê để kiểm tra xem phân phối của bạn có khớp với phương trình sau hay không: P(Δr)=(Δr+Δr_0)^(-β) * exp(-Δr/κ)
.
Nếu dữ liệu khớp với phương trình này (có số mũ β đặc trưng và phần cắt κ), bạn có thể kết luận rằng mô hình di chuyển tổng thể của quần thể tại Singapore tuân theo dạng chuyến bay Lévy bị cắt cụt
