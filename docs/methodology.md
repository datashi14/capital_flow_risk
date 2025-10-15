# Methodology: Capital Flow & Credit Risk Model

**Author:** Ben Bones (Benjamin Benmas)  
**Version:** 1.0  
**Date:** 2025

---

## Overview

This document outlines the theoretical foundations and mathematical formulas used in the Capital Flow & Credit Risk Model for Australia and the United States. The model implements industry-standard credit risk metrics following Basel III, IFRS 9, and modern risk management practices.

---

## 1. Credit Availability Index (CAI)

### 1.1 Definition

The Credit Availability Index (CAI) measures the ease of credit access in the economy based on macro-financial conditions. A higher CAI indicates looser credit conditions.

### 1.2 Formula

```
CAI = 50 + 10 × Z

where:
Z = w₁×Z(rate) + w₂×Z(credit_growth) + w₃×Z(unemployment) + w₄×Z(GDP)

Z(x) = (x - μₓ) / σₓ  (z-score normalization)
```

**Default Weights:**
- w₁ (rate) = -0.3 (negative: higher rates reduce credit availability)
- w₂ (credit_growth) = 0.4 (positive: credit expansion signals availability)
- w₃ (unemployment) = -0.2 (negative: higher unemployment reduces credit)
- w₄ (GDP_growth) = 0.1 (positive: economic growth improves credit access)

**Scale:** 0-100, where 50 represents neutral conditions

### 1.3 Interpretation

- **CAI > 60:** Easy credit conditions
- **CAI 40-60:** Neutral conditions
- **CAI < 40:** Tight credit conditions

---

## 2. Probability of Default (PD)

### 2.1 Simple PD Model

The through-the-cycle PD is adjusted for point-in-time macro conditions:

```
PD = PD_base × exp(β₁×u_norm + β₂×r_norm + β₃×g_norm)

where:
u_norm = (unemployment - 5.0) / 2.0
r_norm = (interest_rate - 2.5) / 2.0
g_norm = (GDP_growth - 2.0) / 2.0
```

**Calibrated Coefficients:**
- β₁ = 0.4 (unemployment elasticity)
- β₂ = 0.2 (rate elasticity)
- β₃ = -0.15 (GDP elasticity)

**Bounds:** PD ∈ [0.1%, 15%]

### 2.2 Merton Structural Model

Alternative approach using Distance to Default (DD):

```
DD = [ln(V/D) - 0.5σ²T] / (σ√T)

PD = Φ(-DD)

where:
V = Asset value
D = Debt value
σ = Asset volatility
T = Time horizon (years)
Φ = Standard normal CDF
```

**Typical Parameters:**
- σ = 0.3 (30% asset volatility)
- T = 1 year
- V/D = 1.5 (leverage ratio)

### 2.3 Stage Classification (IFRS 9)

Loans are classified into three stages:

**Stage 1:** Performing loans (12-month ECL)
- No significant increase in credit risk (SICR)
- Days past due (DPD) ≤ 30

**Stage 2:** Underperforming loans (lifetime ECL)
- SICR detected
- PD_current > 2 × PD_origination
- 30 < DPD ≤ 90

**Stage 3:** Non-performing loans (lifetime ECL)
- Credit-impaired
- DPD > 90 or other evidence of impairment

---

## 3. Loss Given Default (LGD)

### 3.1 Secured Lending (Mortgages)

For collateralized loans:

```
LGD = max(0, LTV / RR - 1)

where:
LTV = Loan-to-Value ratio
RR = Recovery rate (typically 0.80 for housing)
```

**Example:**
- LTV = 90%, RR = 80% → LGD = 90%/80% - 1 = 12.5%
- LTV = 70%, RR = 80% → LGD = 0% (fully recovered)

### 3.2 Downturn LGD

Adjust for falling collateral values:

```
LGD_downturn = LGD_base × [1 / (1 + Δp)]

where:
Δp = percentage change in collateral price (housing)
```

If housing prices fall 20% (Δp = -0.20):
```
LGD_downturn = LGD_base / 0.80 = 1.25 × LGD_base
```

### 3.3 Unsecured Lending

For unsecured loans (credit cards, personal loans):

```
LGD = 0.45 - 0.70  (typical range)
```

Factors affecting unsecured LGD:
- Seniority of claim
- Borrower asset base
- Legal/recovery costs
- Economic conditions

---

## 4. Exposure at Default (EAD)

### 4.1 Basic Formula

```
EAD = Drawn + CCF × Undrawn

where:
Drawn = Current drawn balance
Undrawn = Committed but undrawn amount
CCF = Credit Conversion Factor
```

**Typical CCFs (Basel III):**
- Committed credit lines: 0.75
- Uncommitted credit lines: 0.00
- Letters of credit: 0.50

### 4.2 Stressed EAD

Under stress, assume higher utilization:

```
EAD_stressed = Drawn + CCF_stressed × Undrawn

CCF_stressed = min(1.0, CCF × stress_factor)

stress_factor ∈ [1.2, 1.5]  (20-50% increase in usage)
```

---

## 5. Expected Credit Loss (ECL)

### 5.1 12-Month ECL (Stage 1)

```
ECL_12m = PD_12m × LGD × EAD
```

### 5.2 Lifetime ECL (Stage 2/3)

```
ECL_lifetime = Σ(t=1 to T) [PD_t × LGD_t × EAD_t × DF_t]

where:
PD_t = Marginal PD in year t
DF_t = Discount factor = 1/(1+r)^t
T = Remaining maturity
r = Effective interest rate (typically 5%)
```

**Simplified approach:**
```
ECL_lifetime ≈ 5 × ECL_12m

for typical loan maturity of 5 years with uniform default distribution
```

### 5.3 Portfolio ECL

```
ECL_portfolio = Σ(i=1 to N) ECL_i

where i indexes individual exposures or segments
```

**Coverage Ratio:**
```
Coverage_ratio = ECL_portfolio / Total_EAD × 100%

Typical range: 0.5% - 2.5%
```

---

## 6. Risk-Weighted Assets (RWA)

### 6.1 Basel III IRB Foundation Formula

```
RWA = EAD × K × 12.5

where K = capital requirement calculated as:

K = LGD × N[(1-R)^(-0.5) × G(PD) + (R/(1-R))^0.5 × G(0.999)] - PD × LGD

where:
N(x) = Standard normal CDF
G(x) = Standard normal inverse CDF (quantile)
R = Asset correlation
```

### 6.2 Asset Correlation

```
R = 0.12 × (1-exp(-50×PD))/(1-exp(-50)) + 0.24 × [1-(1-exp(-50×PD))/(1-exp(-50))]

Simplified:
R ≈ 0.15  (retail mortgages)
R ≈ 0.20  (SME lending)
R ≈ 0.24  (large corporate)
```

### 6.3 Maturity Adjustment

```
b = [0.11852 - 0.05478 × ln(PD)]²

MA = [1 + (M-2.5) × b] / [1 - 1.5 × b]

K_adjusted = K × MA

where M = effective maturity (years)
```

**Typical values:**
- Residential mortgages: M = 2.5 (no adjustment)
- Corporate loans: M = 1-5 years

### 6.4 Capital Ratios

**Minimum CET1 Capital:**
```
CET1_min = RWA × 4.5%
```

**Regulatory Capital Requirement (with buffers):**
```
Capital_required = RWA × (CET1 + CCB + CCyB + D-SIB buffer)

where:
CET1 = 4.5% (minimum)
CCB = 2.5% (capital conservation buffer)
CCyB = 0-2.5% (countercyclical buffer)
D-SIB = 0-3.5% (domestic systemically important bank)

Typical total: 10.5% - 13%
```

---

## 7. Stress Testing Scenarios

### 7.1 Tightening Scenario

**Shocks:**
- Interest rates: +200 bps
- Unemployment: +2.0 pp
- Housing prices: -10%
- Credit growth: -50%

**Impact on PD:**
```
PD_stressed = PD_base × exp(0.4×2/2 + 0.2×2/2) = PD_base × 1.82
```

### 7.2 Soft Landing Scenario

**Shocks:**
- Interest rates: +50 bps
- Unemployment: +0.5 pp
- Housing prices: 0%
- Credit growth: -15%

**Impact on PD:**
```
PD_stressed = PD_base × exp(0.4×0.5/2 + 0.2×0.5/2) = PD_base × 1.15
```

### 7.3 Funding Shock Scenario

**Shocks:**
- Bank funding spreads: +75 bps
- Credit growth: -15%
- Liquidity ratio: -10%

**Impact on Capital:**
- Higher funding costs reduce net interest margin
- Tighter credit reduces loan growth
- Capital buffer pressure from stressed assets

### 7.4 Severe Recession Scenario

**Shocks:**
- Unemployment: → 10%+ (spike of +5 pp)
- Housing crash: -25%
- Rates cut: -3 to -4%
- Credit collapse: -20% growth

**Impact:**
```
PD_stressed = PD_base × exp(0.4×5/2) = PD_base × 2.72
LGD_stressed = LGD_base × 1.25
ECL_stressed = ECL_base × 3.4
```

---

## 8. Data Sources

### 8.1 Australia

| Data Point | Source | Frequency |
|------------|--------|-----------|
| Cash Rate | RBA Table F1 | Monthly |
| Housing/Business Credit | RBA Table D1 | Monthly |
| Housing Price Index | RBA Table F7 | Quarterly |
| Unemployment | ABS 6202.0 | Monthly |
| GDP Growth | ABS 5206.0 | Quarterly |
| ADI Statistics | APRA Monthly | Monthly |
| Capital Ratios | APRA Quarterly | Quarterly |

**RBA URL:** https://www.rba.gov.au/statistics/  
**APRA URL:** https://www.apra.gov.au/monthly-authorised-deposit-taking-institution-statistics

### 8.2 United States

| Data Point | Source | Series ID | Frequency |
|------------|--------|-----------|-----------|
| Fed Funds Rate | FRED | FEDFUNDS | Monthly |
| Unemployment | FRED | UNRATE | Monthly |
| Delinquency Rate | FRED | DRALACBS | Quarterly |
| Total Loans | FRED | TOTLL | Weekly |
| CPI | FRED | CPIAUCSL | Monthly |
| BAA Spread | FRED | BAA10Y | Daily |
| GDP | FRED | GDPC1 | Quarterly |

**FRED API:** https://fred.stlouisfed.org/docs/api/  
**FRED API Key:** Free registration required

---

## 9. Model Validation & Limitations

### 9.1 Back-Testing

Compare predicted PD/LGD vs. realized defaults:

```
Accuracy_ratio = 2 × (AUC - 0.5)

where AUC = Area Under ROC Curve
```

**Acceptance criteria:**
- AR > 0.6 for retail models
- AR > 0.7 for corporate models

### 9.2 Calibration

```
Hosmer-Lemeshow test:
χ² = Σ(O_i - E_i)² / E_i

where:
O_i = Observed defaults in bucket i
E_i = Expected defaults in bucket i
```

### 9.3 Known Limitations

1. **Synthetic Data:** Current implementation uses synthetic data when real APIs are unavailable
2. **Simplified Correlations:** Asset correlations are fixed; actual correlations are time-varying
3. **No Credit Migration:** Model assumes binary default/non-default; no intermediate rating migrations
4. **Macro Sensitivity:** Linear/log-linear relationships may understate tail risk
5. **Data Quality:** Real-time data may have revisions, lags, or measurement errors

---

## 10. Implementation Notes

### 10.1 FRED API Setup

To use real US data:

```python
# Install fredapi
pip install fredapi

# Get free API key from https://fred.stlouisfed.org/docs/api/api_key.html
# Set in src/ingest_us.py:
FRED_API_KEY = "your_api_key_here"
```

### 10.2 Running the Model

```bash
# Install dependencies
pip install -r requirements.txt

# Run data ingestion tests
python src/ingest_au.py
python src/ingest_us.py

# Run modeling tests
python src/modeling/core.py
python src/modeling/portfolio.py
python src/stress/scenarios.py

# Launch dashboard
streamlit run dashboards/streamlit_app.py
```

### 10.3 Extending the Model

**Add new scenarios:**
```python
from src.stress.scenarios import StressScenario

class MyScenario(StressScenario):
    def apply(self, df_base):
        df_stressed = df_base.copy()
        # Apply custom shocks
        return df_stressed
```

**Add new portfolio segments:**
```python
portfolio.add_segment(
    segment_name="New Product",
    n_loans=10000,
    avg_exposure=50000,
    avg_pd=0.02,
    avg_lgd=0.40,
    correlation=0.15
)
```

---

## 11. References

1. **Basel Committee on Banking Supervision (2017).** "Basel III: Finalising post-crisis reforms"
2. **IFRS Foundation (2014).** "IFRS 9 Financial Instruments"
3. **Merton, R.C. (1974).** "On the Pricing of Corporate Debt: The Risk Structure of Interest Rates"
4. **Vasicek, O. (2002).** "Loan Portfolio Value," Risk Magazine
5. **Gordy, M.B. (2003).** "A Risk-Factor Model Foundation for Ratings-Based Bank Capital Rules"
6. **APRA (2023).** "Prudential Standard APS 220: Credit Risk Management"
7. **Federal Reserve (2023).** "Capital Planning and Stress Testing"

---

## 12. Contact & Attribution

**Author:** Ben Bones (Benjamin Benmas)  
**Purpose:** Demonstration of transparent credit risk modeling for AU & US markets  
**License:** Educational/Portfolio Use

This model implements industry-standard methodologies but is not intended for regulatory capital calculation without proper validation, governance, and bank-specific calibration.

For questions or collaboration opportunities, please reach out via GitHub or professional channels.

---

*Last Updated: October 2025*
