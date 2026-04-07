# Công thức các hàm phân phối di chuyển (Mobility Distribution Models)

Dưới đây là phương trình toán học của 4 loại mô hình phân phối đại diện cho xác suất $P(\Delta r)$ theo khoảng cách di chuyển $\Delta r$:

### 1. Phân phối Lognormal (Lognormal Distribution)
Đáng chú ý nhất vì đây là hàm có mức độ khớp cao nhất cho cấp độ Zone tự do. Nó mô tả xuất sắc hành vi trong đó người dân thường di chuyển tới một khoảng cách cốt lõi "ưa thích" rồi lượng đi lại dãn ra và rơi dần đi ở khoảng cách xa.

$$ P(\Delta r) = \frac{1}{\Delta r \cdot \sigma \sqrt{2\pi}} \exp\left( - \frac{(\ln \Delta r - \mu)^2}{2\sigma^2} \right) $$

*Với dữ liệu được khớp (hằng số $C$ gộp hệ số dãn), dạng tổng quát là:*
$$ P(\Delta r) = \frac{C}{\Delta r \cdot \sigma \sqrt{2\pi}} \exp\left( - \frac{(\ln \Delta r - \mu)^2}{2\sigma^2} \right) $$

- $\mu$: Giá trị trung bình của log tự nhiên khoảng cách.
- $\sigma$: Độ lệch chuẩn của log tự nhiên khoảng cách.

---

### 2. Phân phối Gamma (Gamma Distribution)
Hàm Gamma là một dạng linh hoạt hơn hàm Exponential, có tham số dạng hình $\alpha$ cho phép đường cong có thể đi lên ở phạm vi vi mô trước khi bắt đầu hạ xuống.

Mô hình gốc:
$$ P(\Delta r) = \frac{1}{\Gamma(\alpha) \lambda^\alpha} (\Delta r)^{\alpha - 1} \exp\left(-\frac{\Delta r}{\lambda}\right) $$

Trong lập trình ta có thể gộp hằng số chuẩn hóa về một tham số gộp (tham số tự do $C$):
$$ P(\Delta r) = C \cdot (\Delta r)^{\alpha - 1} \exp\left(-\frac{\Delta r}{\lambda}\right) $$

- $\alpha$: Tham số hình dáng (shape parameter).
- $\lambda$: Tham số tỷ lệ / quãng đường đặc trưng (scale parameter).

---

### 3. Phân phối Mũ (Exponential Distribution)
Giả định cơ hội kết thúc hành trình xảy ra liên tục và xác suất này tỉ lệ thuận rất nhanh với quãng đường. Tồi hơn ở đỉnh xuất phát nhưng cực kỳ chính xác cho các chặng rơi ngắn.

$$ P(\Delta r) = C \cdot \exp\left(-\frac{\Delta r}{\lambda}\right) $$

- $\lambda$: Khoảng cách phân rã đặc trưng, hằng số suy thoái.
- $C$: Hằng số tỷ lệ.

---

### 4. Phân phối Power-Law Dịch Chuyển (Shifted Power-Law / rễ từ Truncated Lévy Flight)
Mô phỏng những chặng du hành dạng Lévy Flight (khoảng cách cực đoan). Trong một mạng lưới thu nhỏ như Singapore, tham số gián đoạn vùng ven ($\kappa$) trôi dạt về mức gần vô cực, nên hàm số gút lại thành dạng **Shifted Power-law**:

Công thức gốc (Truncated Lévy Flight):
$$ P(\Delta r) = C \cdot (\Delta r + \Delta r_0)^{-\beta} \exp\left(-\frac{\Delta r}{\kappa}\right) $$

Công thức khi mất giới hạn cắt cụt (Shifted Power-Law):
$$ P(\Delta r) = C \cdot (\Delta r + \Delta r_0)^{-\beta} $$

- $\Delta r_0$: Khoảng cách bù gốc (offset distance) được dùng nhằm tránh điểm nổ gián đoạn nơi $\Delta r = 0$.
- $\beta$: Chữ số mũ đặc trưng phản ánh độ dốc suy thoái của khoảng cách nhảy vọt (càng lớn thì hành trình càng mau kết thúc).
- $\kappa$: Điểm cắt giới hạn mũ (Exponential Cut-off) ở bìa hệ thống (khi tính toán thực tế trên quy mô thành phố nhỏ, thành phần $\exp\left(-\Delta r/\kappa\right) \approx 1$).
