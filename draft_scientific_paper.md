---
title: "Individual habits vs Urban Gravity: Scale-dependent mobility transition in Singapore"
author: "Technical Research Report"
date: "April 2026"
---

# Individual habits vs Urban Gravity: Scale-dependent mobility transition in Singapore

## 1. Abstract
Quy luật di chuyển của con người là một trong những chủ đề gây tranh cãi nhất trong vật lý đô thị, thường xoay quanh sự đối lập giữa lý thuyết lũy thừa (power-law) và phân vùng lognormal. Nghiên cứu này cung cấp bằng chứng thực nghiệm từ dữ liệu di chuyển thực tế tại Singapore để khẳng định sự tồn tại của **Quy luật Di chuyển phụ thuộc Quy mô (Scale-Dependent Mobility Law)**. Bằng việc so sánh 5 mô hình (Lognormal, Shifted Power-Law, Gamma, Exponential, TLF) qua 4 nấc thang không gian từ vi mô đến vĩ mô, chúng tôi phát hiện một tiến trình chuyển pha liền mạch: tại cấp độ Subzone, **Lognormal** khớp hình dáng tốt nhất ($R^2 = 0.8199$) thể hiện thói quen cá nhân, dẫn đầu BIC tại 28% số vùng; tại cấp độ trung gian, **Gamma** đóng vai trò vùng đệm chiếm ưu thế BIC tại 38% số nhóm vùng; và tại cấp độ District/Global, các đặc tính hệ thống trỗi dậy khiến **Exponential** và **Shifted Power-Law** chiếm ưu thế (mỗi mô hình đạt BIC tốt nhất tại 40–50% số quận). Kết quả nghiên cứu xác nhận rằng không có một quy luật đơn nhất cho di chuyển đô thị; thay vào đó, sự tương tác giữa thói quen cá nhân và lực hấp dẫn hệ thống được quyết định bởi mức độ tổng hợp không gian, mở ra hướng đi mới cho việc quy hoạch đô thị đa quy mô.


## Nomenclature (Ký hiệu và Từ viết tắt)

**Variables & Parameters:**
- $r$: Khoảng cách Euclidean di chuyển (km)
- $P(r)$: Xác suất di chuyển (Probability Density) tại khoảng cách $r$
- $k$: Số lượng tham số của mô hình (Number of parameters)
- $M$: Số lượng mô hình ứng viên đặt trong so sánh
- $n$: Số lượng đơn vị không gian khảo sát (subzones, groups, districts)

**Models & Distributions:**
- **LN**: Lognormal Distribution (Phân phối Lognormal)
- **SPL**: Shifted Power-Law (Quy luật lũy thừa có dịch chuyển)
- **TLF**: Truncated Lévy Flight (Quy luật Lévy Flight có giới hạn)
- **Exp**: Exponential Distribution (Phân phối hàm mũ)
- **Gamma**: Gamma Distribution (Phân phối Gamma)

**Metrics & Statistics:**
- **BIC**: Bayesian Information Criterion (Tiêu chuẩn thông tin Bayes)
- **BIC Winner (%)**: Tỷ lệ phần trăm số vùng mà mô hình đạt BIC thấp nhất (tốt nhất)
- **$R^2$**: Hệ số xác định (Coefficient of determination) đánh giá độ khớp hình dạng
- **KS-stat**: Thống kê Kolmogorov-Smirnov (Độ lệch tối đa giữa CDF thực nghiệm và lý thuyết)
- **CI**: Confidence Interval (Khoảng tin cậy, thường sử dụng 95% Bootstrap CI)

**Model Parameters:**
- $C$: Hằng số chuẩn hóa xác suất của các mô hình
- $\mu, \sigma$: Tham số trung giá trị (mean) và độ lệch chuẩn (standard deviation) của Lognormal
- $r_0, \beta$: Tham số khoảng cách dịch (shift) và số mũ phân kỳ (exponent) của Shifted Power-Law
- $\lambda$: Tham số phân rã (decay parameter) của Exponential và Gamma
- $\alpha$: Tham số hình dáng (shape parameter) của Gamma
- $\kappa$: Tham số giới hạn cắt (truncating constant) của Truncated Lévy Flight

**Abbreviations & Metrics:**
- **POI**: Point of Interest (Điểm tiện ích đô thị từ nguồn OpenStreetMap)
- **BIC Best (%)**: Tỷ lệ phần trăm số vùng mà mô hình đạt BIC thấp nhất (tốt nhất)
- **$R^2$**: Hệ số xác định (Coefficient of determination), thể hiện tỷ lệ phương sai giải thích được
- **KS-stat**: Kolmogorov-Smirnov statistic (Khoảng cách cực đại giữa hàm phân phối tích lũy của dữ liệu và mô hình)
- **EMD**: Earth Mover's Distance (Khoảng cách Wasserstein) đánh giá độ lệc phân phối
- **GT**: Ground Truth (Dữ liệu di chuyển đa nguồn đã chuẩn hóa làm chuẩn)

## 2. Introduction & Hypothesis
### 2.1. Research Gap (Khoảng trống nghiên cứu)

Mặc dù quy luật Truncated Lévy Flight (TLF) được coi là "phổ quát" trong Human Mobility [1, 2], hầu hết các nghiên cứu kinh điển đều tập trung vào các quốc gia có diện tích lớn hoặc các siêu đô thị (Mega-cities) ở phương Tây. Hiện tại:
- **Thiếu các nghiên cứu tại đô thị cực nén và nhỏ ở Châu Á:** Singapore là một điển hình của đô thị đảo với giới hạn địa lý nghiêm ngặt (~50 km). Nhiều nghiên cứu cho rằng giới hạn này ảnh hưởng trực tiếp đến tham số cắt (truncation) của TLF [5], nhưng ít công trình đi sâu vào sự chuyển dịch mô hình tại đây so với các đô thị phương Tây [8].
- **Sự chuyển dịch mô hình theo quy mô chưa được định lượng rõ ràng:** Mặc dù các nghiên cứu kinh điển chỉ ra quy luật chung, nhưng sự thay đổi của mô hình tối ưu khi thay đổi độ phân giải quan sát (từ cấp độ khu phố đến toàn thành phố) vẫn là một câu hỏi mở, đặc biệt là trong môi trường đô thị nén nơi các ranh giới hành chính và hạ tầng đan xen chặt chẽ.

### 2.2. Hypothesis
Tại các đô thị nén (Compact City) như Singapore, các giả thuyết được đặt ra là:
1. **Có sự chuyển dịch dựa trên quy mô quan sát:**
    - **Quy mô Vi mô (Bottom-up):** Mô hình phân phối xác suất di chuyển phản ánh thói quen di chuyển ngắn của cá thể (Local optimization).
    - **Quy mô vĩ mô (Macro-scale):** Ở quy mô lớn hơn, mô hình sẽ bị thay đổi do bị chi phối bởi các đặc tính hệ thống và cấu trúc đô thị tổng thể.
2. **Quy luật TLF sẽ không còn đạt hiệu quả cao** với các đô thị lớn nhưng diện tích nhỏ như Singapore do các di chuyển dài bị dứt đoạn với hạn chế địa lý trong nhiều quy mô quan sát.

Để cung cấp cái nhìn tổng quan về các mô hình sẽ được phân tích, chúng tôi tóm tắt các đặc tính toán học và ý nghĩa của chúng trong Bảng 0.

**Table 0.** Summary of candidate mobility models ranked by tail strength.

| Rank (Tail Strength) | Model                           | Probability Distribution                                                  | Tail Behavior              | Generative Interpretation                           | Strength                                     | Weakness                                 |
| -------------------- | ------------------------------- | ------------------------------------------------------------------------- | -------------------------- | --------------------------------------------------- | -------------------------------------------- | ---------------------------------------- |
| 1                    | **Exponential**                 | $P(r) \propto \exp(-r/\lambda)$                                           | Very short tail            | Random movement with constant decay probability     | Simple baseline model                        | Cannot capture long-distance mobility    |
| 2                    | **Gamma**                       | $P(r) \propto r^{\alpha-1} \exp(-r/\lambda)$                              | Short exponential tail     | Aggregation of multiple stochastic travel processes | Flexible near short distances                | Tail still decays rapidly                |
| 3                    | **Lognormal**                   | $P(r) \propto \frac{1}{r} \exp\left(-\frac{(\ln r-\mu)^2}{2\sigma^2}\right)$ | Moderately heavy tail      | Multiplicative behavioral processes                 | Empirically fits many mobility datasets      | Weak theoretical mobility interpretation |
| 4                    | **Truncated Lévy Flight (TLF)** | $P(r) \propto (r+r_0)^{-\beta} \exp(-r/\kappa)$                           | Heavy tail with truncation | Lévy flight mobility constrained by spatial limits  | Strong theoretical basis in mobility studies | Sensitive to truncation scale            |
| 5                    | **Shifted Power Law (SPL)**     | $P(r) \propto (r+r_0)^{-\beta}$                                           | Heaviest tail              | Scale-free mobility with short-distance correction  | Captures heavy-tail structure well           | May overestimate long-distance trips     |

![Distribution Comparison](distribution_comparison.png)

## 3. Methodology

### 3.1. Quy trình Fitting Phân phối (Model Fitting Pipeline)

#### 3.1.1. Dữ liệu đầu vào và Tiền xử lý

Dữ liệu đầu vào là tập hợp các chuyến đi giữa các cặp subzone $(i, j)$, bao gồm số lượng chuyến đi $n_{ij}$ và khoảng cách Euclidean $r_{ij}$ (km). Với mỗi đơn vị không gian (subzone / group / district / city-wide), quá trình tiền xử lý bao gồm:

1. **Lọc dữ liệu:** Chỉ giữ các đơn vị có tổng chuyến đi $N = \sum_j n_{ij} \geq 100$ và ít nhất 5 cặp OD hợp lệ để đảm bảo ước lượng thống kê đáng tin cậy.
2. **Rời rạc hóa (Histogram binning):** Tạo histogram khoảng cách với số bins $B = \min(30, |\text{unique}(r)|)$ trên khoảng $[0, r_{\max}]$. Mỗi bin $b$ có tâm $\bar{r}_b$ và tần suất $h_b$ (tổng chuyến đi trong bin).
3. **Chuẩn hóa thành xác suất thực nghiệm:** $\hat{p}_b = h_b / N$, trong đó $N$ là tổng chuyến đi của đơn vị.
4. **Lọc bins rỗng:** Chỉ giữ các bins có $h_b > 0$. Yêu cầu tối thiểu 4 bins hợp lệ.

#### 3.1.2. Các mô hình phân phối ứng viên

Năm mô hình phân phối được so sánh, với số tham số $k$ tương ứng:

| Mô hình | Công thức $P(r)$ | $k$ | Tham số |
| :--- | :--- | :---: | :--- |
| **Exponential** | $C \cdot e^{-r/\lambda}$ | 2 | $C, \lambda$ |
| **Lognormal** | $\frac{C}{r \sigma \sqrt{2\pi}} \exp\!\left[-\frac{(\ln r - \mu)^2}{2\sigma^2}\right]$ | 3 | $C, \mu, \sigma$ |
| **Gamma** | $C \cdot r^{\alpha-1} e^{-r/\lambda}$ | 3 | $C, \alpha, \lambda$ |
| **Shifted Power-Law** | $C \cdot (r + r_0)^{-\beta}$ | 3 | $C, r_0, \beta$ |
| **Truncated Lévy Flight** | $C \cdot (r + r_0)^{-\beta} e^{-r/\kappa}$ | 4 | $C, r_0, \beta, \kappa$ |

#### 3.1.3. Thuật toán ước lượng tham số

Tham số của từng mô hình được ước lượng bằng phương pháp **Nonlinear Least Squares (NLS)** với thuật toán tối ưu **Levenberg-Marquardt**, triển khai qua hàm `scipy.optimize.curve_fit` (Python). Thuật toán tối thiểu hóa tổng bình phương sai số:

$$\hat{\theta} = \arg\min_{\theta} \sum_{b} \left[\hat{p}_b - P(\bar{r}_b; \theta)\right]^2$$

Cấu hình fitting:
- Số vòng lặp tối đa: `maxfev = 15,000`
- Ràng buộc tham số: tất cả tham số $> 0$; $\beta \leq 15$ để tránh đuôi phân kỳ; $\alpha \leq 20$ cho Gamma
- Giá trị khởi tạo: $p_0$ được chọn dựa trên đặc tính của từng mô hình (ví dụ: $\beta_0 = 2$, $\sigma_0 = 1$)

#### 3.1.4. Chuẩn hóa và Tính chỉ số Goodness-of-Fit

Sau khi ước lượng tham số $\hat{\theta}$, xác suất lý thuyết thô $\tilde{p}_b = P(\bar{r}_b; \hat{\theta})$ được chuẩn hóa thành PMF rời rạc:

$$\hat{p}^{\text{model}}_b = \frac{\tilde{p}_b}{\sum_{b'} \tilde{p}_{b'}}$$

Bốn chỉ số đánh giá được tính toán:

**(a) Hệ số xác định $R^2$** — đo độ khớp hình dáng:
$$R^2 = 1 - \frac{\sum_b (\hat{p}_b - \tilde{p}_b)^2}{\sum_b (\hat{p}_b - \bar{p})^2}$$

**(b) Log-Likelihood (LLH)** — đo tính hợp lý của mô hình:
$$\mathrm{LLH} = \sum_b h_b \cdot \ln(\hat{p}^{\text{model}}_b)$$

**(c) AIC và BIC** — đo hiệu quả thông tin có phạt độ phức tạp:
$$\mathrm{AIC} = 2k - 2\,\mathrm{LLH}$$
$$\mathrm{BIC} = k \ln N - 2\,\mathrm{LLH}$$
trong đó $N$ là tổng số chuyến đi của đơn vị không gian, $k$ là số tham số mô hình.

**(d) KS-statistic** — đo sai lệch tích lũy tối đa giữa CDF thực nghiệm và lý thuyết:
$$D_{\mathrm{KS}} = \max_b \left|\sum_{b'=1}^{b} \hat{p}_{b'} - \sum_{b'=1}^{b} \hat{p}^{\text{model}}_{b'}\right|$$

#### 3.1.5. Tiêu chí lựa chọn mô hình

Với mỗi đơn vị không gian, mô hình tốt nhất được xác định theo từng tiêu chí:
- **AIC/BIC**: mô hình có giá trị **thấp nhất** được chọn.
- **LLH**: mô hình có giá trị **cao nhất** (ít âm nhất) được chọn.
- **$R^2$**: mô hình có giá trị **cao nhất** được chọn.
- **KS-stat**: mô hình có giá trị **thấp nhất** được chọn.

Chỉ số **BIC Winner (%)** được định nghĩa là tỷ lệ phần trăm số đơn vị không gian mà một mô hình đạt BIC thấp nhất, dùng để so sánh ưu thế tổng hợp qua nhiều quy mô. Ngoài ra, phân tích **Đồng thuận (Consensus)** xác định mô hình thắng theo nhiều tiêu chí nhất tại mỗi đơn vị để có cái nhìn tổng hợp đa chiều.

**Lưu ý về tập dữ liệu:** Mặc dù hệ thống phân vùng của Singapore bao gồm **323 subzones**, nghiên cứu này chỉ tập trung phân tích trên **303 subzones** có dữ liệu di chuyển thực tế. 20 subzones còn lại (bao gồm các đảo và các vùng đệm chưa quy hoạch dân cư) không ghi nhận chuyến đi đáng kể trong tập dữ liệu, do đó được loại bỏ để đảm bảo tính nhất quán của các ước lượng thống kê.


### 3.2. Phân vùng cấp độ Trung gian (Intermediate-scale: 40 Groups)

Để làm rõ hơn lộ trình chuyển dịch từ vi mô sang vĩ mô, chúng tôi bổ sung một cấp độ quan sát trung gian bằng cách chia Singapore thành **40 khu vực địa lý** (40 groups).

**Phương pháp thực hiện:**
- Mỗi district trong số 5 district chính được chia nhỏ thành đúng **8 nhóm liền kề**.
- Sử dụng thuật toán **Agglomerative Clustering** với ràng buộc **Connectivity matrix** (dựa trên ma trận tiếp giáp không gian của 303 subzones). Ràng buộc này đảm bảo các subzone trong cùng một nhóm phải chạm nhau về mặt địa lý, tạo thành một vùng duy nhất.
- Thuật toán ưu tiên sự cân bằng về số lượng subzone và tối ưu hóa khoảng cách nội cụm (linkage strategy: complete).

Việc phân chia này tạo ra các thực thể địa lý có kích thước lớn hơn subzone (~7.5 subzones/group) nhưng nhỏ hơn district (~60.6 subzones/district). Ngoài ra, chúng tôi cũng thực hiện khảo sát trên **toàn bộ Singapore** (City-wide) để hoàn tất bức tranh chuyển dịch đa quy mô.

![Ba cấp độ phân vùng không gian tại Singapore](singapore_spatial_scales.png)
*Hình 1. Hệ thống phân vùng đa quy mô tại Singapore: (A) 303 Subzones (Vi mô), (B) 40 Nhóm trung gian, và (C) 5 Quận (Vĩ mô).*

### 3.3. Block Bootstrap với 40 Group-Blocks

Các subzone không độc lập về mặt không gian — các subzone lân cận chia sẻ hạ tầng giao thông và có phân phối di chuyển tương đồng. Bootstrap thông thường (resample từng subzone độc lập) sẽ **đánh giá thấp phương sai** do bỏ qua tương quan không gian, dẫn đến khoảng tin cậy hẹp giả tạo.

**Giải pháp:** Sử dụng **block bootstrap** với **40 group-blocks** (được phân cụm từ 303 subzones dựa trên khoảng cách và district) làm đơn vị resample. Việc tăng số lượng block từ 5 (districts) lên 40 giúp tăng độ phân giải của phân phối bootstrap, cung cấp khoảng tin cậy (CI) chính xác và đáng tin cậy hơn.

**Quy trình:**
1. **Định nghĩa block:** 40 groups địa lý liền kề (trung bình ~7.5 subzones/block).
2. **Resample:** Chọn ngẫu nhiên 40 blocks **có hoàn lại** (with replacement).
3. **Tổng hợp:** Gom tất cả subzones từ các blocks được chọn → tập dữ liệu bootstrap.
4. **Tính toán:** Trên mỗi mẫu bootstrap, tính lại BIC Best %, Mean $R^2$, Mean KS-stat cho 5 mô hình.
5. **Lặp lại:** 1000 lần tái lấy mẫu.
6. **Khoảng tin cậy:** 95% CI = percentile [2.5%, 97.5%] từ 1000 giá trị bootstrap.

**Lợi ích:** Việc sử dụng 40 blocks giúp CI phản ánh sát thực tế hơn so với việc chỉ dùng 5 districts (vốn mang tính bảo thủ cao do số lượng block quá ít).


## 4. Results: The Scale-Transition

### 4.1. Khảo sát tại Cấp Vi mô - Subzone (Micro-scale)
Tại quy mô nhỏ, hành vi di chuyển bị chi phối bởi các lựa chọn cá nhân dựa trên sự tiện lợi cục bộ.

**Table 1.** Hiệu quả của các mô hình tại quy mô Subzone (n = 303 subzones).

| Model | $k$ | Mean LLH | Mean AIC | Mean BIC | Mean $R^2$ [95% CI] | Mean KS [95% CI] |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 3 | -75.5k | 151.0k | 151.0k | **0.8199** [0.796, 0.846] | 0.1492 [0.126, 0.192] |
| **Shifted Power-Law** | 3 | -66.5k | 133.0k | 133.0k | 0.6998 [0.661, 0.725] | 0.0935 [0.088, 0.108] |
| **Gamma** | 3 | -104.1k| 208.3k | 208.3k | 0.8022 [0.782, 0.830] | 0.1911 [0.168, 0.230] |
| **Exponential** | 2 | -70.1k | 140.1k | 140.1k | 0.6919 [0.650, 0.715] | 0.1216 [0.100, 0.155] |
| **Trun. Lévy Flight** | 4 | **-66.5k** | **132.9k** | **132.9k**| 0.7026 [0.664, 0.728] | **0.0898** [0.084, 0.105] |

**Table 1b.** Tỉ lệ số phân khu (Subzones) mà mỗi mô hình chiếm ưu thế theo từng chỉ số.

| Model | AIC (n/%) | BIC (n/%) | KS (n/%) | LLH (n/%) | $R^2$ (n/%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 85 (28%) | 85 (28%) | 59 (19%) | 86 (28%) | **210 (69%)** |
| **Shifted Power-Law** | 80 (26%) | 85 (28%) | **99 (33%)** | 71 (23%) | 7 (2%) |
| **Gamma** | 74 (24%) | 73 (24%) | 69 (23%) | 74 (24%) | 78 (26%) |
| **Exponential** | 49 (16%) | 50 (17%) | 53 (17%) | 40 (13%) | 0 (0%) |
| **Trun. Lévy Flight** | 15 (5%) | 10 (3%) | 23 (8%) | 32 (11%) | 8 (3%) |

![Model Dominance Subzone](model_dominance_subzone.png)
*Hình 4. Thống kê số lượng Subzone mà mỗi mô hình đạt kết quả tốt nhất theo 5 tiêu chí khác nhau.*

**Note on Metrics:** 
- **Log-likelihood (LLH)**: Giá trị log của hàm hợp lý, LLH càng cao (ít âm hơn) mô hình càng khớp.
- **AIC / BIC**: Các chỉ số thông tin (Akaike/Bayesian), dùng để chọn mô hình tối ưu bằng cách phạt số lượng tham số ($k$). Giá trị thấp hơn chứng tỏ sự đánh đổi tốt hơn giữa độ khớp và độ đơn giản.
- **$R^2$**: Độ khớp về hình dáng (shape-fitting).
- **KS-stat**: Độ lệch tối đa giữa phân phối thực tế và lý thuyết.

Phân tích chi tiết tại từng subzone làm nổi bật hai chiều cạnh song song:
- **Khớp hình dáng ($R^2$):** Lognormal chiếm ưu thế tuyệt đối tại **69%** số phân khu (210/303), Gamma đứng thứ hai với 26% — bỏ xa SPL (2%) và Exponential (0%). Điều này xác nhận người dân di chuyển theo thói quen cá nhân có đỉnh rõ rệt ở khoảng cách ngắn-trung bình.
- **Khớp thống kê (AIC/BIC):** Cuộc chiến hoàn toàn khác: **LN và SPL hòa nhau** (đều 28%), theo sát là Gamma (24%). Quan trọng hơn, **SPL thắng KS-stat tại 33%** số vùng — có nghĩa là tại 1/3 số phân khu, SPL mô tả phân phối tích lũy (phần đuôi khoảng cách xa) chính xác hơn mọi mô hình khác.

Phân tích **đồng thuận (Consensus)** cho thấy thứ tự: **Lognormal (85 vùng) > SPL (80 vùng) > Gamma (74 vùng)**. Khoảng cách giữa LN và SPL (85 vs 80) rất nhỏ, cho thấy ngay ở quy mô vi mô, **sức hút lực hấp dẫn đô thị (SPL) đã cạnh tranh trực tiếp với thói quen cá nhân (LN)** tại một tỉ lệ đáng kể các phân khu.

### 4.2. Khảo sát tại Cấp Trung gian - 40 Groups (Intermediate-scale)

Khi dữ liệu được gom nhóm lên cấp độ 40 vùng địa lý (trung bình ~7.5 subzones/vùng), đặc tính cá nhân bắt đầu bị triệt tiêu dần bởi phép cộng gộp, nhưng vẫn giữ được độ phân giải không gian cao hơn cấp quận.

**Table 2.** So sánh hiệu quả tại quy mô trung gian (40 Groups, n = 40).

| Model | $k$ | Mean LLH | Mean AIC | Mean BIC | Mean $R^2$ | Mean KS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 3 | -600.1k | 1.20M | 1.20M | **0.8370** | 0.1195 |
| **Shifted Power-Law** | 3 | -568.4k | 1.14M | 1.14M | 0.7739 | 0.0777 |
| **Gamma** | 3 | -703.3k | 1.41M | 1.41M | 0.8289 | 0.1287 |
| **Exponential** | 2 | -581.6k | 1.16M | 1.16M | 0.7653 | 0.1008 |
| **Trun. Lévy Flight** | 4 | **-567.5k** | **1.13M** | **1.13M**| 0.7774 | **0.0724** |

**Table 2b.** Tỉ lệ số nhóm (40 Groups) mà mỗi mô hình chiếm ưu thế theo từng chỉ số.

| Model | AIC (n/%) | BIC (n/%) | KS (n/%) | LLH (n/%) | $R^2$ (n/%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 8 (24%) | 7 (21%) | 5 (15%) | 8 (24%) | **20 (59%)** |
| **Exponential** | 8 (24%) | 9 (26%) | 7 (21%) | 8 (24%) | 1 (3%) |
| **Gamma** | **13 (38%)** | **13 (38%)** | **11 (32%)** | **13 (38%)** | 11 (32%) |
| **Shifted Power-Law** | 2 (6%) | 3 (9%) | 8 (24%) | 2 (6%) | 1 (3%) |
| **Trun. Lévy Flight** | 3 (9%) | 2 (6%) | 3 (9%) | 3 (9%) | 1 (3%) |

![Group Dominance 40](group_40_dominance_by_metric.png)
*Hình 5. Thống kê mức độ ưu thế của các mô hình tại quy mô trung gian (40 Groups).*

Tại quy mô này, **Gamma thống trị tuyệt đối** trên cả 4 chỉ số thống kê (AIC 38%, BIC 38%, KS 32%, LLH 38%), đóng vai trò "vùng đệm lý thuyết" rõ rệt. Có hai hiện tượng bất ngờ cần chú ý:

1. **SPL sụp đổ đột ngột:** Từ vị thế hòa cùng LN ở cấp Subzone (BIC 28%), SPL chỉ còn chiếm **6–9%** ở quy mô này. Điều này gợi ý rằng SPL không hoạt động theo cơ chế tuyến tính — nó phát huy hiệu quả ở hai thái cực (vi mô và vĩ mô) nhưng suy giảm mạnh ở quy mô trung gian.

2. **Exponential trỗi dậy sớm:** Exp đã tăng từ 17% (Subzone) lên **26% (BIC)** ở quy mô này, ngang bằng với LN trong Consensus (8 vùng mỗi bên). Đây là tín hiệu báo trước sự chuyển dịch sang quy luật hệ thống ở các quy mô lớn hơn.

Lognormal vẫn duy trì $R^2$ cao nhất (59%), nhưng khoảng cách với Gamma (32%) đã thu hẹp đáng kể so với cấp Subzone (69% vs 26%). Consensus: **Gamma (13 vùng) > Exp (8) = LN (8)** — lần đầu tiên Exponential ngang ngửa Lognormal trong phân tích đồng thuận.

![So sánh phân phối 40 nhóm](group_40_distribution_comparison.png)
*Hình 2. Phân bổ các mô hình tối ưu (BIC) tại quy mô 40 nhóm, thể hiện trạng thái quá độ giữa vi mô và vĩ mô.*

### 4.3. Khảo sát tại Cấp Vĩ mô - District (Macro-scale)

Khi quy mô mở rộng lên 5 districts, đặc tính hệ thống và cấu trúc đô thị bắt đầu lấn át hoàn toàn thói quen cá nhân đơn lẻ.

**Table 3.** Hiệu quả mô hình tại quy mô vĩ mô (District level, n = 5).

| Model | $k$ | Mean LLH | Mean AIC | Mean BIC | Mean $R^2$ | Mean KS |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 3 | -4.52M | 9.04M | 9.04M | **0.9307** | 0.0847 |
| **Shifted Power-Law** | 3 | -4.50M | 9.01M | 9.01M | 0.8987 | 0.0474 |
| **Gamma** | 3 | -4.78M | 9.55M | 9.55M | 0.8965 | 0.1627 |
| **Exponential** | 2 | -4.56M | 9.13M | 9.13M | 0.8882 | 0.1113 |
| **Trun. Lévy Flight** | 4 | **-4.50M** | **9.00M** | **9.00M**| 0.8987 | **0.0465** |

**Table 3b.** Tỉ lệ số quận (5 Districts) mà mỗi mô hình chiếm ưu thế theo từng chỉ số.

| Model | AIC (n/%) | BIC (n/%) | KS (n/%) | LLH (n/%) | $R^2$ (n/%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Exponential** | **2 (40%)** | **2 (40%)** | 1 (20%) | **2 (40%)** | 0 (0%) |
| **Shifted Power-Law** | **2 (40%)** | **2 (40%)** | **3 (60%)** | 0 (0%) | 1 (20%) |
| **Gamma** | 1 (20%) | 1 (20%) | 0 (0%) | 1 (20%) | 0 (0%) |
| **Lognormal** | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | **4 (80%)** |
| **Trun. Lévy Flight** | 0 (0%) | 0 (0%) | 1 (20%) | **2 (40%)** | 0 (0%) |

![District Dominance](district_dominance_by_metric.png)
*Hình 6. Thống kê mức độ ưu thế của các mô hình tại quy mô vĩ mô (5 Districts).*

Tại cấp độ District, thực tế là một **cuộc tranh giành ba bên**, không phải hai bên:
- **Exponential**: Thắng AIC/BIC tại 40% quận, LLH tại 40% quận — mô hình tối giản nhưng hiệu quả thông tin cao.
- **Shifted Power-Law**: Thắng AIC/BIC tại 40% quận, và **dẫn đầu KS-stat tại 60% quận** (3/5) — có khả năng bao phủ phân phối tích lũy (phần đuôi) tốt nhất ở quy mô này.
- **Truncated Lévy Flight (TLF)**: Bất ngờ **thắng LLH tại 40% quận** (2/5) — thực tế TLF không hề thất bại, nó vẫn là mô hình hợp lý nhất về mặt xác suất tại một số quận có cấu trúc di chuyển phức tạp.

**Lognormal** mất hoàn toàn vị thế thống kê (AIC/BIC = 0%), nhưng duy trì nghịch lý $R^2$ tại **80% quận** (4/5) — chứng tỏ nó khớp hình dáng phân phối tốt, nhưng thất bại trong việc ước lượng xác suất toàn bộ phân phối. Gamma chỉ thắng tại **1 quận duy nhất** (20%), vai trò vùng đệm của nó đã kết thúc ở quy mô này.

![Nghịch lý R2 vs BIC](bic_logic_illustration.png)
*Hình 3. So sánh hiệu quả của 5 mô hình tại cấp District: SPL và TLF thể hiện sự ưu việt ở phần đuôi (log-log scale), trong khi Lognormal và Gamma mặc dù khớp phần thân tốt (Linear scale) nhưng sụt giảm nhanh ở khoảng cách xa.*

### 4.4. Khảo sát tại Cấp Toàn thành phố - Global (City-wide)

Ở cấp độ gộp cao nhất (toàn bộ Singapore), toàn bộ các đặc tính hành vi cá nhân và hạ tầng cụ thể bị triệt tiêu, chỉ còn lại quy luật "ma sát khoảng cách" cơ bản nhất (distance decay).

**Table 4.** Goodness-of-fit comparison at the global scale (Singapore-wide, n = 1).

**Table 4.** Hiệu quả mô hình tại quy mô toàn thành phố (Global scale, n = 1).

| Model | $k$ | LLH | AIC | BIC | $R^2$ | KS-stat |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lognormal** | 3 | -19.61M | 39.23M | 39.23M | **0.9286** | 0.1291 |
| **Shifted Power-Law** | 3 | -19.67M | 39.34M | 39.34M | 0.7820 | **0.0697** |
| **Gamma** | 3 | -22.53M | 45.06M | 45.06M | 0.8532 | 0.2460 |
| **Exponential** | 2 | -19.55M | **39.10M** | **39.10M** | 0.7856 | 0.0698 |
| **Trun. Lévy Flight** | 4 | **-19.55M** | **39.10M** | **39.10M** | 0.7856 | 0.0698 |

Tại thang đo toàn thành phố, **Exponential và TLF cùng hòa nhau** về AIC/BIC (~39.10M) — đây là kết quả bất ngờ khi TLF, vốn bị coi là yếu ở quy mô nhỏ, lại phục hồi thành tích ở quy mô lớn nhất. **Lognormal** vẫn duy trì $R^2$ cao nhất (0.9286) nhưng BIC cao hơn (39.23M) và KS tệ nhất (0.1291), phản ánh nhất quán xu hướng xuyên suốt: LN khớp phần thân nhưng thất bại ở phần đuôi. **SPL** bất ngờ có KS tốt nhất (0.0697) nhưng BIC tệ nhất trong nhóm dẫn đầu (39.34M). **Gamma** là mô hình tệ nhất ở Global với BIC 45.06M và KS 0.2460.

Để minh chứng cho đặc tính "đuôi" của dữ liệu di chuyển toàn thành phố, chúng tôi thực hiện các biểu đồ trực quan hóa quan trọng sau:


![Phân bố khoảng cách (Histogram)](distance_histogram.png)
![Biểu đồ Log-Log với các đường khớp mô hình](distance_loglog.png)
![Hàm phân phối tích lũy bổ sung (CCDF)](distance_ccdf.png)

*Hình 6. Phân tích trực quan về hành vi di chuyển toàn thành phố (Global Scale): (A) Histogram tuyến tính, (B) Log-Log plot so sánh Exponential vs Power-Law, và (C) CCDF phân tích đặc tính heavy-tail.*

**Nhận xét từ trực quan hóa:**
- **Histogram:** Cho thấy sự sụt giảm nhanh chóng của các chuyến đi ngắn, nhưng vẫn duy trì các chuyến đi dài ở khoảng cách >20 km.
- **Log-Log Plot:** Đường khớp **Exponential** (màu đỏ) cho thấy độ dốc khá gắt, trong khi **Shifted Power-Law** (màu xanh) khớp tốt hơn ở phần đuôi dữ liệu. Điều này giải thích tại sao ở quy mô này, các mô hình hệ thống bắt đầu vượt lên.
- **CCDF:** Biểu đồ CCDF trên thang log-log xác nhận sự tồn tại của cấu trúc heavy-tail, tuy nhiên bị giới hạn bởi diện tích hòn đảo (~50 km), minh chứng cho sự cần thiết của thành phần "Truncated" trong các mô hình Lévy Flight.


### 4.5. Tổng hợp So sánh: Sự chuyển dịch theo 4 quy mô không gian

Việc khảo sát qua 4 nấc thang không gian cho thấy một bức tranh chuyển dịch liền mạch từ cá nhân đến hệ thống.

**Table 5.** Transition of model dominance (BIC Winner %) across four spatial scales.

| Distribution              | Subzone (303) | 40 Groups (34) | District (5) | Global (1)  |
|---------------------------|:-------------:|:--------------:|:------------:|:-----------:|
| **Lognormal**             | **0.2805**    | 0.2059         | 0.0000       | 0.0000      |
| **Gamma**                 | 0.2409        | **0.3824**     | 0.2000       | 0.0000      |
| **Shifted Power-Law**     | **0.2805**    | 0.0882         | **0.4000**   | 0.0000      |
| **Exponential**           | 0.1650        | 0.2647         | **0.4000**   | **~0.5000** |
| Truncated Lévy Flight     | 0.0330        | 0.0588         | 0.0000       | **~0.5000** |

*Lưu ý: Tại Global (n=1), Exp và TLF hòa nhau về AIC/BIC (~39.10M). Tỉ lệ 0.5/0.5 phản ánh sự hòa.*

**Quy luật Chuyển dịch (The Transition Path):**
1. **Micro (LN ≈ SPL)**: LN thắng về hình dáng ($R^2$), LN và SPL **hòa nhau** về thống kê (BIC 28% mỗi bên); SPL dẫn KS (33%).
2. **Intermediate (Gamma dominates, SPL collapses)**: Gamma thống trị rõ rệt (AIC/BIC/LLH 38%). SPL sụt giảm đột ngột từ 28% → 9% (BIC) do mất hiệu quả ở scale trung gian.
3. **Macro (Exp ≈ SPL; TLF phục hồi)**: Exp và SPL **hòa nhau** (AIC/BIC 40% mỗi bên); TLF bất ngờ thắng LLH tại 40% quận; SPL thắng KS (60%).
4. **Global (Exp = TLF)**: Exp và TLF **hòa nhau** về AIC/BIC; SPL có KS tốt nhất; LN có $R^2$ tốt nhất nhưng thông tin kém.



## 5. Discussion

### 5.1. Đánh giá các Giả thuyết

Dựa trên bằng chứng thực nghiệm từ 303 subzones qua 4 cấp độ quy mô không gian (Tables 1–5), chúng tôi đánh giá lại hai giả thuyết đã đặt ra ở Mục 2.2.

---

**Giả thuyết 1 — Có sự chuyển dịch mô hình tối ưu dựa trên quy mô quan sát:** ✅ **XÁC NHẬN**

*1a. Vi mô phản ánh thói quen cá nhân (Local optimization):*

Dữ liệu xác nhận. Tại cấp Subzone (Table 1b), Lognormal — mô hình đặc trưng cho hành vi cá nhân có đỉnh rõ rệt — thống trị $R^2$ tại **69% số vùng** (210/303), bỏ xa Gamma (26%) và SPL (2%). Tuy nhiên, bức tranh thống kê phức tạp hơn giả thuyết ban đầu: về BIC, **LN và SPL hòa nhau** (28% mỗi bên), và SPL dẫn đầu KS-stat tại 33%. Điều này cho thấy ngay ở quy mô nhỏ nhất, cơ chế hệ thống (SPL) đã cạnh tranh trực tiếp với thói quen cá nhân (LN) tại khoảng một phần ba số phân khu.

*1b. Vĩ mô bị chi phối bởi đặc tính hệ thống:*

Xác nhận hoàn toàn. Tại cấp District (Table 3b), Lognormal **mất toàn bộ vị thế thống kê** (AIC/BIC/KS/LLH = 0%), nhường chỗ cho Exponential (AIC/BIC 40%), SPL (AIC/BIC 40%, KS 60%) và TLF (LLH 40%). Tại Global (Table 4), Exp và TLF cùng đạt AIC/BIC tốt nhất (~39.10M), xác nhận sự chi phối hoàn toàn của quy luật hệ thống.

*Phát hiện bổ sung — Vùng đệm Gamma ở quy mô trung gian:*

Giả thuyết ban đầu chỉ dự đoán hai thái cực (vi mô vs vĩ mô). Dữ liệu bổ sung thêm một giai đoạn trung gian: tại cấp 40 Groups (Table 2b), **Gamma thống trị tuyệt đối** (AIC/BIC/LLH đều 38%), đóng vai trò "vùng đệm" nơi thói quen cá nhân bắt đầu bị gộp lại nhưng chưa bị hệ thống hóa hoàn toàn.

*Tổng hợp xu hướng chuyển pha (Table 5 — BIC Winner %):*

| Mô hình | Subzone | 40 Groups | District | Global | Xu hướng |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **LN** | **28%** | 21% | 0% | 0% | ↘ Suy giảm đơn điệu |
| **Gamma** | 24% | **38%** | 20% | 0% | ↗↘ Đạt đỉnh ở trung gian |
| **SPL** | **28%** | 9% | **40%** | 0% | ↘↗ Hiệu ứng "skip-scale" |
| **Exp** | 17% | 26% | **40%** | **~50%** | ↗ Tăng đơn điệu |
| **TLF** | 3% | 6% | 0% | **~50%** | ↗ Phục hồi ở quy mô lớn |

---

**Giả thuyết 2 — TLF sẽ không còn đạt hiệu quả cao tại đô thị nén Singapore:** ⚠️ **Chưa đúng hoàn toàn**

Giả định ban đầu cho rằng giới hạn địa lý (~50 km) của Singapore sẽ làm các di chuyển dài bị dứt đoạn, khiến TLF mất hiệu quả ở **nhiều quy mô quan sát**. Dữ liệu cho thấy điều này chỉ đúng một phần:

| Quy mô | TLF BIC | TLF LLH | TLF AIC | Đánh giá |
| :--- | :---: | :---: | :---: | :--- |
| **Subzone** | 3% | 11% | 5% | ✅ Đúng — TLF rất yếu |
| **40 Groups** | 6% | 9% | 9% | ✅ Đúng — TLF vẫn yếu |
| **District** | 0% | **40%** | 0% | ❌ Sai — TLF phục hồi LLH tại 2/5 quận |
| **Global** | **~50%** | **~50%** | **~50%** | ❌ Sai — TLF **hòa với mô hình tốt nhất** |

**Phân tích nguyên nhân:** Sự thất bại của TLF ở quy mô nhỏ **không phải do giới hạn địa lý**, mà do **over-parameterization**:
- TLF có **4 tham số** ($C, r_0, \beta, \kappa$) — nhiều nhất trong 5 mô hình. Tại mỗi subzone, số điểm dữ liệu chỉ có vài chục bin, khiến BIC phạt nặng mô hình phức tạp.
- Khi dữ liệu tăng lên hàng triệu chuyến đi (District, Global), 4 tham số được ước lượng chính xác hơn và hình phạt BIC trở nên tương đối nhỏ. Lúc này, tham số truncation $\kappa$ thực sự phản ánh giới hạn ~50 km của Singapore, giúp TLF cạnh tranh ngang bằng Exponential.

**Kết luận điều chỉnh:** Giả định 2 đúng ở quy mô vi mô và trung gian, nhưng sai ở quy mô vĩ mô và toàn thành phố. Phát biểu chính xác hơn: *"Tại đô thị nén, TLF mất tính phổ quát xuyên quy mô — nó chỉ phát huy khi khối lượng dữ liệu đủ lớn để bộc lộ đồng thời cả cấu trúc heavy-tail lẫn truncation."*




### 5.2. Cơ chế Chuyển dịch

- **Cấp độ cá nhân (Subzone):** Người dân tối ưu hóa tiện ích cục bộ — chọn điểm đến gần và quen thuộc, tạo ra hình dáng Lognormal với đỉnh rõ rệt. Tuy nhiên, một tỉ lệ đáng kể ~28% vùng đã có dấu hiệu cơ chế SPL ngay từ quy mô nhỏ nhất, có thể là các phân khu có kết nối MRT tốt hoặc nằm gần các hub trung tâm.
- **Vùng đệm (40 Groups):** Khi gộp ~7.5 subzone lại, các đặc tính cá nhân đa dạng triệt tiêu nhau, để lộ cấu trúc tổng hợp của Gamma — phân phối "trung bình" của nhiều thói quen cá nhân xếp chồng nhau. Đây cũng là quy mô mà Exp bắt đầu xuất hiện (26%), báo hiệu sự cứng lại của hệ thống.
- **Cấp độ hệ thống (District):** Các trung tâm trọng điểm (CBD, Jurong East, Tampines) chi phối toàn bộ luồng di chuyển cấp quận. SPL mô tả tốt nhất phân phối tích lũy (KS 60%) vì nó nắm bắt sức hút power-law của các hub đô thị. TLF cạnh tranh được vì tham số $\kappa$ của nó phù hợp với giới hạn địa lý Singapore (~50 km).
- **Hiện tượng SPL "skip-scale":** SPL hoạt động tốt ở hai thái cực (Subzone BIC 28%, District BIC 40%) nhưng sụp đổ ở quy mô trung gian (40G BIC 9%). Điều này gợi ý SPL mô tả **hai cơ chế khác nhau**: ở vi mô là hành vi "khám phá ngẫu nhiên" cục bộ, ở vĩ mô là sức hút trung tâm đô thị — cả hai đều có cấu trúc power-law nhưng từ nguồn gốc khác nhau.

## 6. Conclusion

Nghiên cứu này đã thành công trong việc giải mã sự mâu thuẫn giữa các quy luật di chuyển tại Singapore thông qua lăng kính quy mô không gian, với các kết luận chính sau:

1. **Không có người thắng cuộc tuyệt đối ở bất kỳ quy mô nào.** Mỗi quy mô là sự tranh giành giữa 2–3 mô hình theo từng tiêu chí đánh giá khác nhau. Ở quy mô vi mô, **Lognormal và SPL hòa nhau** về BIC (28% mỗi bên). Ở quy mô District, **Exp, SPL, và TLF** đều cạnh tranh. Ở Global, **Exp và TLF hòa nhau**. Đây là bằng chứng cho thấy hành vi di chuyển đô thị không thể tóm gọn bằng một mô hình duy nhất.

2. **Bốn giai đoạn chuyển pha** được xác lập từ dữ liệu thực nghiệm 303 subzones: (i) *Vi mô*: LN thắng hình dáng, LN–SPL hòa thống kê; (ii) *Trung gian*: Gamma thống trị, SPL sụp đổ, Exp trỗi dậy; (iii) *Vĩ mô*: Exp–SPL hòa BIC, TLF phục hồi LLH; (iv) *Global*: Exp–TLF hòa BIC, LN duy trì $R^2$ cao nhất nhưng kém thông tin nhất.

3. **Nghịch lý $R^2$ vs BIC là nhất quán xuyên suốt.** Lognormal duy trì vị trí #1 về $R^2$ ở tất cả 4 quy mô (69% → 59% → 80% → 0.929), trong khi thứ hạng BIC của nó suy giảm đơn điệu: #1 → #3 → #5 → #5. Đây là minh chứng định lượng rõ ràng nhất cho sự mâu thuẫn giữa độ khớp hình học và hiệu quả thông tin xác suất.

4. **TLF không thất bại tại đô thị nén — nó chỉ cần đủ dữ liệu.** Ở quy mô nhỏ (Subzone: BIC 3%), TLF yếu kém. Nhưng ở quy mô lớn hơn, TLF phục hồi: thắng LLH tại 40% quận (District) và hòa BIC với Exp ở Global. Điều này cho thấy TLF không thất bại vì giới hạn địa lý, mà vì nó cần một lượng chuyến đi đủ lớn để bộc lộ đặc tính heavy-tail với truncation.

5. **Hiện tượng SPL "skip-scale"** là phát hiện mới: SPL hiệu quả ở vi mô (BIC 28%) và vĩ mô (BIC 40%) nhưng sụp đổ ở trung gian (BIC 9%). Điều này gợi ý SPL mô tả hai cơ chế khác nhau — hành vi khám phá cục bộ và lực hút trung tâm đô thị — đều có cấu trúc power-law nhưng ẩn đi ở quy mô trung gian khi Gamma chi phối.

6. **Ý nghĩa thực tiễn cho quy hoạch:** Dùng **Lognormal** khi quy hoạch cấp phường (ước tính tần suất sử dụng POI cục bộ). Dùng **SPL** khi thiết kế hành lang giao thông liên quận (phân phối tích lũy KS tốt nhất ở District). Dùng **Exponential** làm baseline cho mô hình toàn đô thị (thống kê hiệu quả nhất ở Global). Không dùng một mô hình duy nhất cho mọi quy mô.

---
## 7. References
1. Brockmann, D. et al (2006). *Nature*. DOI: 10.1038/nature04292
2. González, M. C. et al (2008). *Nature*. DOI: 10.1038/nature06958
3. Song, C. et al (2010). *Science*. DOI: 10.1126/science.1177170
4. Liang, X. et al (2013). *Transportation Research Part C*. DOI: 10.1016/j.trc.2012.12.004
5. Barbosa, H. et al (2018). *Physics Reports*. DOI: 10.1016/j.physrep.2018.01.001
6. Marquardt, D. W. (1963). *SIAM*. DOI: 10.1137/0111030
7. Noulas, A. et al (2012). A Tale of Many Cities: Universal Patterns in Human Urban Mobility. *PLOS ONE*. DOI: 10.1371/journal.pone.0037027
8. Sun, L. et al (2013). Efficient-community-based mobility model for Singapore's public transport system. *IEEE Trans. on Intelligent Transportation Systems*. DOI: 10.1109/TITS.2013.2272201
9. Liu, Y. et al (2012). Understanding individual mobility patterns from urban taxi trips. *Cities*. DOI: 10.1016/j.cities.2012.01.002
