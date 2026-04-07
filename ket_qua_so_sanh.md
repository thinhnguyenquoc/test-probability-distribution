# So sánh các mô hình phân phối cho lượng di chuyển

Dưới đây là một số mô hình có thể mô tả tập dữ liệu chuyến đi, sắp xếp theo mức độ phù hợp trên thang đo logarit (chú trọng phần đuôi phân bố):

### Exponential 
- Độ chính xác $R^2$ (tính trên log space): **0.9522**
- Độ chính xác $R^2$ (tuyến tính thông thường): **0.9354**
- Các tham số tối ưu: `[0.1716, 4.7526]`

### Gamma 
- Độ chính xác $R^2$ (tính trên log space): **0.8881**
- Độ chính xác $R^2$ (tuyến tính thông thường): **0.9387**
- Các tham số tối ưu: `[0.1886, 1.1433, 3.6187]`

### Shifted Power-Law 
- Độ chính xác $R^2$ (tính trên log space): **0.6264**
- Độ chính xác $R^2$ (tuyến tính thông thường): **0.9390**
- Các tham số tối ưu: `[10136976.1119, 22.7835, 5.7102]`

### Lognormal 
- Độ chính xác $R^2$ (tính trên log space): **0.5667**
- Độ chính xác $R^2$ (tuyến tính thông thường): **0.9750**
- Các tham số tối ưu: `[0.8314, 1.2181, 1.1666]`

