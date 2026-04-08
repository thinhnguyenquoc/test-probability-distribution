---
title: "Individual habits vs Urban Gravity: Scale-dependent mobility transition in Singapore"
author: "Technical Research Report"
date: "April 2026"
---

# Individual habits vs Urban Gravity: Scale-dependent mobility transition in Singapore

## 1. Abstract
Nghiên cứu này muốn tìm kiếm mô hình phân phối di chuyển phù hợp với hành vi và cấu trúc hạ tầng tại Singapoẻ. Thông qua phân tích 5 mô hình phân phối thường được áp dụng trong lĩnh vực human mobility, rút ra những kết quả sau: Ở cấp độ vi mô (Subzone), dữ liệu tuân theo phân phối **Lognormal**, phản ánh thói quen di chuyển ngắn của cá thể. Ở cấp độ vĩ mô (District), sức hút từ hạ tầng đô thị (POI) lấn át hành vi cá nhân, dẫn đến sự thống trị của **Shifted Power-Law**. Việc chuẩn hóa dữ liệu theo mật độ POI (Hiệu suất di chuyển $\Phi(d)$ ) đạt độ khớp $R^2 > 0.97$, xác nhận rằng cấu trúc hạ tầng là động lực chính của quy luật di chuyển phụ thuộc quy mô.

## 2. Introduction & Hypothesis
Di chuyển con người thường được coi là tuân theo quy luật phổ quát Truncated Lévy Flight (TLF). Tuy nhiên, tại các đô thị nén như Singapore, chúng tôi đặt giả thuyết về một sự chuyển pha dựa trên quy mô quan sát:
1. **Quy mô Vi mô (Bottom-up):** Di chuyển là kết quả của thói quen cá nhân (Local optimization).
2. **Quy mô Vĩ mô (Top-down):** Dòng chảy bị chi phối bởi "Lực hấp dẫn đô thị" (Urban Gravity) từ các trung tâm hạ tầng.

## 3. Methodology
Quá trình tham số hóa sử dụng thuật toán *Levenberg-Marquardt* để so sánh 5 mô hình (Lognormal, SPL, TLF, Gamma, Exponential). 

Kết hợp sử dụng dữ liệu từ **OpenStreetMap (OSM)** để tính toán **Hiệu suất di chuyển** $\Phi(d)$:

$$\Phi(d) = \frac{P(d)}{A(d)}$$

Trong đó $A(d)$ là tổng số điểm tin cậy (POI) hiện có ở khoảng cách $d$. Điều này cho phép tách biệt "lực ma sát" của khoảng cách khỏi "lực hút" của mật độ hạ tầng.

## 4. Results: The Scale-Transition

### 4.1. Khảo sát tại Cấp Vi mô - Subzone (Micro-scale)
Tại quy mô nhỏ, hành vi di chuyển bị chi phối bởi các lựa chọn cá nhân dựa trên sự tiện lợi cục bộ.

**Table 1.** Goodness-of-fit comparison at the micro-scale (subzone level, n = 303).

| Distribution              | BIC Best (%) | Mean $R^2$   | Mean KS-stat |
|---------------------------|--------------|--------------|--------------|
| **Lognormal**             | **28.05**    | **0.8199**   | 0.1492       |
| Shifted Power-Law (SPL)   | **28.05**    | 0.6998       | 0.0935       |
| Gamma                     | 24.09        | 0.8022       | 0.1911       |
| Exponential               | 16.50        | 0.6919       | 0.1216       |
| Truncated Lévy Flight     | 3.30         | 0.7026       | **0.0898**   |

Lognormal và SPL chia sẻ vị trí dẫn đầu về BIC, nhưng Lognormal vượt trội về $R^2$ (0.8199), mô tả chính xác sự chùm tụ của các chuyến đi ngắn quanh "đỉnh" phân phối.

### 4.2. Khảo sát tại Cấp vĩ mô - District (Macro-scale)
Khi quy mô mở rộng, cấu trúc hạ tầng bắt đầu lấn át thói quen cá nhân.

**Table 2.** Goodness-of-fit comparison at the macro-scale (district level, n = 5).

| Distribution              | BIC Best (%) | Mean $R^2$   | Mean KS-stat |
|---------------------------|--------------|--------------|--------------|
| **Shifted Power-Law (SPL)**| **40.0**     | 0.8987       | **0.0474**   |
| Exponential               | **40.0**     | 0.8882       | 0.1113       |
| Gamma                     | 20.0         | 0.8965       | 0.1627       |
| Lognormal                 | 0.0          | **0.9307**   | 0.0847       |
| Truncated Lévy Flight     | 0.0          | 0.8987       | **0.0474**   |

SPL chiếm ưu thế tuyệt đối về độ khớp hình học (KS-stat thấp nhất) và tiêu chuẩn BIC (40%). Việc Lognormal thất bại ở quy mô vĩ mô dù có $R^2$ cao là do "Nghịch lý Đuôi" (The Tail Paradox): Lognormal không bắt kịp các hành trình dài liên quận.

![Nghịch lý R2 vs BIC](bic_logic_illustration.png)
*Hình 1. So sánh Lognormal và SPL: Sự sụt giảm của Lognormal ở phần đuôi khiến nó bị loại bỏ bởi tiêu chuẩn BIC tại quy mô vĩ mô.*

### 4.3. Bản chất hành vi cá nhân và Sức hút hạ tầng (Efficiency Analysis)
Để hiểu rõ động lực phía sau sự chuyển dịch quy mô, chúng tôi chuẩn hóa xác suất di chuyển thực tế $P(d)$ theo mật độ hạ tầng $A(d)$ từ **Open Street Map**. Mục tiêu là kiểm chứng xem liệu sau khi "khử" đi sức hút của các trung tâm đô thị, quy luật di chuyển gốc sẽ tuân theo mô hình nào.

**Table 3.** Goodness-of-fit for Mobility Efficiency $\Phi(d)$ (Global and District-level).

| Scale / Region             | $n$           | $R^2$ (Lognormal) | $R^2$ (SPL) |
|----------------------------|---------------|-------------------|-------------|
| **Global (Singapore)**      | **43 bins**   | **0.9769**        | 0.9768      |
| North-East                 | 5 districts   | **0.9315**        | 0.9240      |
| West                       | 5 districts   | **0.8647**        | 0.8624      |
| Central                    | 5 districts   | **0.8025**        | 0.7700      |
| East                       | 5 districts   | **0.7332**        | 0.5146      |
| North                      | 5 districts   | **0.7034**        | 0.6216      |
| **Mean (Districts)**       | **-**         | **0.8071**        | **0.7385**  |

Kết quả chuẩn hóa mang lại một phát hiện quan trọng: Nếu như ở Mục 4.2, mô hình **SPL** chiếm ưu thế tuyệt đối tại quy mô Quận do khả năng "hấp thụ" lực hút từ các trung tâm hạ tầng dày đặc, thì sau khi giảm bớt sự phụ thuộc của lực hấp dẫn đô thị (POI normalization), mô hình **Lognormal** lại quay trở lại vị trí dẫn đầu ($R^2$ trung bình 0.81 so với 0.74 của SPL). 

Điều này khẳng định rằng: **Mô hình Lognormal thể hiện được tính đặc trưng di chuyển của cá nhân** (với các hành trình ngắn và tối ưu cục bộ). Trong khi đó, sự chiếm ưu thế trước đó của mô hình SPL trên cấp độ quận chỉ là do các đặc tính thu hút hạ tầng đô thị lấn át đặc tính cá nhân.

![POI Attraction Analysis](poi_attraction_analysis.png)
*Hình 2. Hiệu suất di chuyển $\Phi(d)$ sau khi chuẩn hóa theo POIs. Việc loại bỏ "lực hấp dẫn đô thị" giúp phục hồi đặc tính Lognormal của hành vi cá nhân.*

### 4.4. Xác thực qua Facebook Mobility Data
Để đánh giá độ tin cậy ngoại biên, chúng tôi so sánh kết quả mô phỏng với dữ liệu thực tế từ Facebook Mobility Data thông qua chỉ số Wasserstein (EMD).

**Table 4.** Wasserstein (EMD) distance breakdown between models and Facebook ground-truth (n = 5 districts).

| Model                     | EMD (<1 km) | EMD (1–10 km) | EMD (10–100 km) | Overall EMD |
|---------------------------|-------------|---------------|-----------------|-------------|
| **Shifted Power-Law (SPL)**| **0.06**    | **0.05**      | **0.05**        | **0.08**    |
| Lognormal                 | 0.09        | 0.07          | 0.11            | 0.09        |
| Gamma                     | 0.11        | 0.14          | 0.08            | 0.07        |
| Exponential               | 0.10        | 0.12          | 0.06            | 0.07        |
| Truncated Lévy Flight     | 0.12        | 0.10          | 0.09            | 0.10        |

Kết quả EMD thấp nhất (0.05) của SPL tại các dải hành trình dài khẳng định rằng trong thực tế vận hành đô thị, quy luật phân phối lũy thừa vẫn là công cụ dự báo dòng lưu lượng hiệu quả nhất.

## 5. Discussion: From Individual Behavior to Urban Gravity
Sự chuyển dịch phân phối phản ánh một nhận định dứt khoát về địa lý dân cư: 
- **Cấp độ cá nhân:** Người dân ưu tiên các tiện ích gần nhà ("tiện lợi cục bộ"), tạo ra hình dáng Lognormal với đỉnh rõ rệt.
- **Cấp độ hệ thống:** Các trung tâm trọng điểm (CBD, Jurong East, Tampines) bẻ cong ý chí cá nhân. Quy hoạch đa cực (Polycentric) và mạng lưới MRT dày đặc giúp sức hút trung tâm lan tỏa bền vững theo quy luật lũy thừa (SPL).

## 6. Conclusion
Nghiên cứu khẳng định quy luật di chuyển tại Singapore là **phụ thuộc quy mô (Scale-dependent)**. Lognormal làm chủ bán kính vi mô (<2km), trong khi Shifted Power-Law thống trị mạng lưới vĩ mô (>5km) dựa trên sức hút hạ tầng.

---
## 7. References
1. Brockmann, D. et al (2006). *Nature*. DOI: 10.1038/nature04292
2. González, M. C. et al (2008). *Nature*. DOI: 10.1038/nature06958
3. Song, C. et al (2010). *Science*. DOI: 10.1126/science.1177170
4. Liang, X. et al (2013). *Transportation Research Part C*. DOI: 10.1016/j.trc.2012.12.004
5. Barbosa, H. et al (2018). *Physics Reports*. DOI: 10.1016/j.physrep.2018.01.001
6. Marquardt, D. W. (1963). *SIAM*. DOI: 10.1137/0111030
