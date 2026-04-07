# Kết quả Chỉ số Đánh giá Cấu trúc Phân phối Nâng cao

Bộ Metrics chi tiết cho từng loại đường cong dựa trên tổng toàn bộ mạng lưới không gian:

| Mô hình               |   Số tham số (k) |   KS Test (D) |   Log-Likelihood |         AIC |         BIC |
|:----------------------|-----------------:|--------------:|-----------------:|------------:|------------:|
| Shifted Power-Law     |                3 |        0.0386 |     -2.12377e+07 | 4.24755e+07 | 4.24755e+07 |
| Truncated Levy Flight |                4 |        0.0386 |     -2.12377e+07 | 4.24755e+07 | 4.24756e+07 |
| Exponential           |                2 |        0.075  |     -2.12591e+07 | 4.25182e+07 | 4.25182e+07 |
| Lognormal             |                3 |        0.0466 |     -2.12634e+07 | 4.25267e+07 | 4.25268e+07 |
| Gamma                 |                3 |        0.1206 |     -2.16212e+07 | 4.32424e+07 | 4.32425e+07 |

### Đánh giá Likelihood Ratio cho Heavy-tail models (Lévy Flight vs. Shifted Power Law)
- **Likelihood Ratio (LR)**: 0.28
- **p-value ($\chi^2$)**: 5.9670e-01
$\Rightarrow$ Chênh lệch không quan trọng, Shifted Power-Law vốn có số tham số nhẹ hơn là phương án thiết kiệm và mạnh mẽ ngang ngửa Truncated Lévy Flight.
