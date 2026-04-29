# ĐỀ XUẤT NGHIÊN CỨU

**Đề tài:** Đề xuất framework để sinh luồng di chuyển cho thành phố Hồ Chí Minh trong điều kiện ít dữ liệu quan sát dựa trên dữ liệu mở OSM.

---

### 1. Giới thiệu
* **Về human mobility:** Giới thiệu về human mobility, tại sao nó quan trọng trên thế giới.
* **Thực trạng tại TP.HCM:** Thành phố Hồ Chí Minh chưa có các nghiên cứu này trong khi nó quan trọng. Lý do tốn kém về thời gian tiền bạc cho quan trắc và lấy khảo sát như các nước phát triển. Liệu có các nào sinh ra mà ít tốn kém mà độ chính xác cao từ dữ liệu mở.

### 2. Các nghiên cứu liên quan
* **Traditional:** Gravity model, radiation model.
* **Machine learning/Deep learning:** Như deep gravity, học ảnh vệ tinh.
* **Mô hình chuyển giao:** Có thể thuận hay không kém.

### 3. Research Gap
* Các mô hình truyền thống độ chính xác thấp mặc dù dùng dữ liệu ít, mô hình hiện đại chính xác cao nhưng cần nhiều dữ liệu từ nhiều nguồn.
* Khả năng chuyển giao mở rộng còn hạn chế, cần xác định tính tương đồng.
* Chưa có nghiên cứu tận dụng nguồn dữ liệu xác suất di chuyển của Facebook (Meta).

### 4. Câu hỏi nghiên cứu
* Làm sao thiết kế mô hình sinh OD có thể duy trì độ chính xác khi dữ liệu quan sát bị giảm đáng kể?
* Các loại thông tin ngữ cảnh (POI, population, road network) đóng vai trò thế nào khi dữ liệu OD bị thiếu?
* Mô hình có thể sinh tốt khi áp dụng cho trường hợp zero-shot? Áp dụng mô hình tìm được như thế nào vào Hồ Chí Minh.

### 5. Cách thức thực hiện chi tiết
* **Đề xuất mô hình sinh OD mới:** Dựa vào phân bổ xác suất di chuyển nhằm đảm bảo tính ổn định của mô hình khi giảm dữ liệu quan sát (chỉ dùng 10% dữ liệu). Kiểm tra độ chính xác với các mô hình đã có.
* **Nghiên cứu mô hình Variational Autoencoder (VAE):** Tận dụng khả năng học đặc điểm ngữ cảnh giữa các thành phố thông qua dữ liệu mở để kiểm tra xem dữ liệu mở đóng vai trò như thế nào trong việc cung cấp thông tin dự báo. Dữ liệu mở sẽ được thêm bớt các thuộc tính để từ đó xác định các thuộc tính có ảnh hưởng lớn.
* **Áp dụng mô hình đề xuất:** Dựa theo dữ liệu phân phối xác suất di chuyển của Facebook và mô hình Variational Autoencoder (VAE) học trên các thành phố như Sgp, US, rồi test trên Seoul để đề xuất dữ liệu cho Hồ Chí Minh. So sánh kết quả hai mô hình để đưa ra dữ liệu dự báo tốt nhất cho thành phố Hồ Chí Minh.
*  **Thu thập dữ liệu luồng ở Hồ Chí Minh:** làm khảo sát cho 200 ứng viên để xem trong một tuần họ di chuyển đến những nơi nào trong thành phố. Từ đó có dữ liệu để kiểm tra mô hình đề xuất. 
