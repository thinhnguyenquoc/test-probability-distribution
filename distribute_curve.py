import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm, gamma, expon

# Thiết lập thông số cho các phân phối (được điều chỉnh để dễ so sánh)
x = np.linspace(0.1, 20, 1000)

# 1. Exponential
pdf_expon = expon.pdf(x, scale=2)

# 2. Gamma
pdf_gamma = gamma.pdf(x, a=2, scale=1.5)

# 3. Lognormal
pdf_lognorm = lognorm.pdf(x, s=0.8, scale=2)

# 4. Shifted Power-Law (SPL) - f(x) = (x + x0)^-alpha
x0, alpha = 0.5, 1.5
pdf_spl = (x + x0)**(-alpha)
pdf_spl /= np.trapezoid(pdf_spl, x) # Chuẩn hóa diện tích = 1

# 5. Truncated Lévy Flight (TLF) - f(x) = x^-alpha * exp(-lambda*x)
alpha_tlf, lam = 1.2, 0.3
pdf_tlf = (x**-alpha_tlf) * np.exp(-lam * x)
pdf_tlf /= np.trapezoid(pdf_tlf, x) # Chuẩn hóa diện tích = 1

# --- VẼ BIỂU ĐỒ ---
plt.figure(figsize=(14, 6))

# Đồ thị 1: Linear Scale (So sánh hình dạng đỉnh)
plt.subplot(1, 2, 1)
plt.plot(x, pdf_expon, label='Exponential', lw=2)
plt.plot(x, pdf_gamma, label='Gamma', lw=2)
plt.plot(x, pdf_lognorm, label='Lognormal', lw=2)
plt.plot(x, pdf_spl, label='Shifted Power-Law', lw=2, linestyle='--')
plt.plot(x, pdf_tlf, label='Truncated Lévy Flight', lw=2, linestyle='-.')
plt.title('Linear Scale: Comparison of Distributions')
plt.xlabel('Value (e.g., Distance)')
plt.ylabel('Probability Density')
plt.legend()
plt.grid(alpha=0.3)

# Đồ thị 2: Log-Log Scale (So sánh độ dày của đuôi)
plt.subplot(1, 2, 2)
plt.loglog(x, pdf_expon, label='Exponential', lw=2)
plt.loglog(x, pdf_gamma, label='Gamma', lw=2)
plt.loglog(x, pdf_lognorm, label='Lognormal', lw=2)
plt.loglog(x, pdf_spl, label='Shifted Power-Law', lw=2, linestyle='--')
plt.loglog(x, pdf_tlf, label='Truncated Lévy Flight', lw=2, linestyle='-.')
plt.title('Log-Log Scale: Tail Behavior')
plt.xlabel('Log Value')
plt.ylabel('Log Probability Density')
plt.legend()
plt.grid(True, which="both", ls="-", alpha=0.2)

plt.tight_layout()

# Xuất ra hình png
plt.savefig('distribution_comparison.png', dpi=300)
print("Đã lưu hình tại: distribution_comparison.png")

plt.show()
