import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import lognorm, gamma, expon

def lognormal_pdf(x, mu, sigma):
    return (1 / (x * sigma * np.sqrt(2 * np.pi))) * np.exp(- (np.log(x) - mu)**2 / (2 * sigma**2))

def gamma_pdf(x, alpha, lam):
    return (1 / (lam**alpha * gamma_fn(alpha))) * x**(alpha-1) * np.exp(-x/lam)

from scipy.special import gamma as gamma_fn

def spl_pdf(x, r0, beta):
    # This is a bit complex to normalize correctly as a PDF on [0, inf] 
    # but we can just use the formula and normalize in the plot range
    return (x + r0)**(-beta)

def generate_morphing():
    # We'll use representative parameters or aggregate stats
    # Based on the results:
    # Micro: Lognormal (mu~1, sigma~0.8)
    # Intermediate: Gamma (alpha~1.5, lam~3)
    # Macro: Exponential (lam~5) or Gamma with alpha close to 1
    # Global: SPL (r0~1, beta~2.5)
    
    x = np.linspace(0.1, 40, 1000)
    
    fig, axes = plt.subplots(1, 4, figsize=(24, 6), sharey=True)
    
    # 1. Micro Scale (Lognormal)
    mu, sigma = 1.0, 0.7
    y1 = lognormal_pdf(x, mu, sigma)
    axes[0].plot(x, y1, 'r-', lw=3, label='Lognormal (Best)')
    axes[0].set_title("1. Micro (Subzones)\nDominant: Lognormal", fontsize=16, weight='bold')
    axes[0].fill_between(x, y1, color='red', alpha=0.1)
    
    # 2. Intermediate Scale (Gamma)
    alpha, lam = 1.5, 3.0
    y2 = (x**(alpha-1) * np.exp(-x/lam))
    y2 /= np.trapz(y2, x)
    axes[1].plot(x, y2, 'orange', lw=3, label='Gamma (Best)')
    axes[1].set_title("2. Intermediate (Groups)\nDominant: Gamma", fontsize=16, weight='bold')
    axes[1].fill_between(x, y2, color='orange', alpha=0.1)
    
    # 3. Macro Scale (Exponential/Gamma transition)
    lam_exp = 5.0
    y3 = np.exp(-x/lam_exp)
    y3 /= np.trapz(y3, x)
    axes[2].plot(x, y3, 'green', lw=3, label='Exponential/Gamma')
    axes[2].set_title("3. Macro (Districts)\nDominant: Gamma/TLF", fontsize=16, weight='bold')
    axes[2].fill_between(x, y3, color='green', alpha=0.1)
    
    # 4. Global Scale (SPL)
    r0, beta = 2.0, 2.5
    y4 = (x + r0)**(-beta)
    y4 /= np.trapz(y4, x)
    axes[3].plot(x, y4, 'blue', lw=3, label='SPL (Best Tail)')
    axes[3].set_title("4. Global (City-wide)\nDominant: SPL / Lognormal", fontsize=16, weight='bold')
    axes[3].fill_between(x, y4, color='blue', alpha=0.1)
    
    # Common styling
    for ax in axes:
        ax.set_xlabel("Distance (km)", fontsize=12)
        ax.set_ylim(0, 0.45)
        ax.grid(alpha=0.3)
        
    axes[0].set_ylabel("Probability Density", fontsize=14)
    
    # Overlay logic: Add previous curves with high transparency to show morphing
    axes[1].plot(x, y1, 'r--', alpha=0.2)
    axes[2].plot(x, y2, 'orange', linestyle='--', alpha=0.2)
    axes[3].plot(x, y3, 'green', linestyle='--', alpha=0.2)

    plt.tight_layout()
    plt.savefig('/Users/nguyenquocthinh/Documents/test-probability-distribution/distribution_morphing.png', dpi=300)
    print("Saved morphing figure to distribution_morphing.png")

if __name__ == "__main__":
    generate_morphing()
