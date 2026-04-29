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
* Thông tin về xác suất di chuyển của Facebook chưa chính xác với dữ liệu ground truth, liệu sai lệch này có tính hệ thống, làm sao hiệu chỉnh cho Hồ Chí Minh thông qua dữ liệu của các thành phố khác: SGP, Seoul, thành phố US?
* Mô hình có thể sinh tốt khi áp dụng cho trường hợp zero-shot? Áp dụng mô hình tìm được như thế nào vào Hồ Chí Minh.

### 5. Cách thức thực hiện chi tiết
* **Đề xuất mô hình sinh OD mới:** Dựa vào phân bổ xác suất di chuyển nhằm đảm bảo tính ổn định của mô hình khi giảm dữ liệu quan sát (chỉ dùng 10% dữ liệu). Kiểm tra độ chính xác với các mô hình đã có.
* **Nghiên cứu Domain Adaptation / Transfer Learning:** Dùng dữ liệu mỡ để học cách điều chỉnh từ phân bố xác suất của Facebook về xác suất thật. Phương pháp sử dụng: Meta-regression để học từ các thành phố khác và chuyển giao về cho Hồ Chí Minh.
* **Nghiên cứu các ước lượng tổng số lường đi ra từ một vùng** Dùng mô hình Variational Autoencoder (VAE) học trên các thành phố như Sgp, US, rồi test trên Seoul để đề xuất tổng số luồng đi ra từ một subzone dựa trên quy mô dân số và các đặc trưng dữ liệu mở của các vùng liền kề.
* **Áp dụng mô hình đề xuất:**
  - Dựa theo dữ liệu phân phối xác suất di chuyển của Facebook đã hiệu chỉnh ở bước trên để bổ sung thông số cho hàm phân bổ cho mô hình đã đề xuất.
  - Tổng số luồng ra ước lượng 
  - Sử dụng mô hình đề xuất để ước lượng các luồng di chuyển trong thành phố Hồ Chí Minh.
    
* Bổ sung một khảo sát nhỏ ở thành phố Hồ Chí Minh: khảo sát 200 người trong một đến hai quận để xem họ đi đâu trong tuần. Từ đó làm dữ liệu ground truth để kiểm tra tính đúng đắn của mô hình, hoặc tìm kiếm nguồn thay thế từ sở giao thông thành phố.

