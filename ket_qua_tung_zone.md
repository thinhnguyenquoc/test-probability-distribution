# Tổng kết phân phối chuyến đi cho từng Zone riêng biệt

Sau khi quét qua các phân khu (zone) và chỉ phân tích các zone có lượng chuyến đi trên 500 (tổng cộng 301 zones), các mô hình khớp tốt nhất (dựa trên $R^2$) là:

- **Lognormal**: Phù hợp nhất cho 209 zones (69.4%)
- **Gamma**: Phù hợp nhất cho 80 zones (26.6%)
- **Shifted Power-Law**: Phù hợp nhất cho 12 zones (4.0%)

Nhìn chung, hiện tượng đa số các zone tuân theo phân phối **Lognormal** hoặc **Gamma** lại một lần nữa chứng minh rằng trong quy mô thành phố nhỏ lẻ, hành vi con người thích đi xa dần đến một mốc nào đó (đỉnh của lognormal) rồi mới suy giảm theo cấp số, thay vì suy giảm ngay lập tức.
