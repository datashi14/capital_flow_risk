# Capital Flow & Credit Risk Model — Australia & US (2025)

**Author:** Ben Bones (Benjamin Benmas)

A comprehensive capital flow and credit risk modeling framework for Australian and US financial markets. This project demonstrates transparent, industry-standard credit risk analytics including PD/LGD/EAD models, Expected Credit Loss (ECL) calculations, Risk-Weighted Assets (RWA), and macro stress testing — all with an interactive Streamlit dashboard.

---

## 🎯 What This Project Does

This model enables:

1. **Data Ingestion:** Automated fetching of macro-financial data from RBA, APRA, ABS (Australia) and FRED, FDIC, BLS (United States)
2. **Credit Risk Modeling:** Industry-standard PD/LGD/EAD calculations following Basel III and IFRS 9
3. **Portfolio Analysis:** ECL estimation, RWA calculation, and capital adequacy assessment
4. **Stress Testing:** Multiple scenario frameworks (tightening, soft landing, funding shock, severe recession)
5. **Interactive Dashboard:** Streamlit-based UI for exploring data, comparing countries, and running stress scenarios

---

## 📊 Key Features

### Credit Risk Metrics
- **Credit Availability Index (CAI):** Composite macro indicator of credit conditions
- **Probability of Default (PD):** Simple macro model + Merton structural approach
- **Loss Given Default (LGD):** Secured and unsecured, with downturn adjustments
- **Exposure at Default (EAD):** Credit conversion factors and stressed utilization
- **Expected Credit Loss (ECL):** 12-month and lifetime calculations (IFRS 9 stages)

### Portfolio Analytics
- **Segment-level analysis:** Mortgages, personal loans, SME, commercial real estate, etc.
- **Risk-Weighted Assets (RWA):** Basel III IRB Foundation formula
- **Capital Requirements:** CET1, Tier 1, Total Capital with regulatory buffers

### Stress Testing
- **Pre-defined scenarios:** Monetary tightening, soft landing, funding shock, severe recession
- **Custom scenarios:** User-defined macro shocks via interactive sliders
- **Impact analysis:** ECL and RWA changes under stress, segment-level breakdown

### Visualization & Reporting
- **Time series charts:** Policy rates, unemployment, credit growth, defaults, CAI
- **Cross-country comparison:** Australia vs. United States side-by-side
- **Portfolio breakdown:** Exposure, ECL, and RWA by segment
- **Stress testing:** Baseline vs. stressed metrics with percentage changes
- **Scenario Insights & Projections:** Professional risk report narratives with:
  - Automated narrative generation from model outputs
  - Metrics comparison tables (CAI, PD, LGD, ECL, RWA, CET1)
  - Segment-level deep-dive analysis
  - Recommended management actions based on severity
  - Exportable scenario reports (TXT format)

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download this repository
cd capital_flow_risk

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- pandas, numpy, scipy, scikit-learn, xgboost
- statsmodels, matplotlib, plotly
- streamlit (for dashboard)
- fredapi (optional, for real US data)
- openpyxl, xlrd (for Excel file reading)

### 2. (Optional) Set Up FRED API

To fetch real US data from FRED:

1. Get a free API key: https://fred.stlouisfed.org/docs/api/api_key.html
2. Open `src/ingest_us.py`
3. Set `FRED_API_KEY = "your_key_here"` at the top

Without a FRED API key, the model uses realistic synthetic data.

### 3. Run the Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

This launches an interactive web app at http://localhost:8501

### 4. Explore the Modules

**Test data ingestion:**
```bash
python src/ingest_au.py
python src/ingest_us.py
```

**Test modeling:**
```bash
python src/modeling/core.py
python src/modeling/portfolio.py
```

**Test stress scenarios:**
```bash
python src/stress/scenarios.py
```

---

## 📁 Project Structure

```
capital_flow_risk/
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── docs/
│   └── methodology.md              # Detailed formulas and methodology
├── src/
│   ├── __init__.py
│   ├── ingest_au.py                # Australian data loaders (RBA, APRA, ABS)
│   ├── ingest_us.py                # US data loaders (FRED, FDIC, BLS)
│   ├── modeling/
│   │   ├── __init__.py
│   │   ├── core.py                 # CAI, PD/LGD/EAD, ECL calculations
│   │   └── portfolio.py            # Portfolio aggregation, RWA, capital
│   └── stress/
│       ├── __init__.py
│       └── scenarios.py            # Stress testing scenarios
├── dashboards/
│   └── streamlit_app.py            # Interactive Streamlit dashboard
└── notebooks/
    ├── 01_ingest_AU.ipynb          # AU data exploration
    ├── 01_ingest_US.ipynb          # US data exploration
    └── 02_model_AU_US.ipynb        # Joint modeling notebook
```

---

## 🧮 Methodology Highlights

### Probability of Default (PD)

**Simple Model:**
```
PD = PD_base × exp(β₁×unemployment + β₂×rates + β₃×GDP)
```

**Merton Model:**
```
PD = Φ(-DD)
where DD = Distance to Default = [ln(V/D) - 0.5σ²T] / (σ√T)
```

### Loss Given Default (LGD)

**Secured (Mortgages):**
```
LGD = max(0, LTV / Recovery_Rate - 1)
```

**Downturn Adjustment:**
```
LGD_downturn = LGD_base / (1 + housing_price_change)
```

### Expected Credit Loss (ECL)

**12-month ECL (Stage 1):**
```
ECL = PD × LGD × EAD
```

**Lifetime ECL (Stage 2/3):**
```
ECL = Σ(PD_t × LGD_t × EAD_t × Discount_Factor_t)
```

### Risk-Weighted Assets (RWA)

**Basel III IRB Formula:**
```
RWA = EAD × K × 12.5

where K = LGD × N[...] (Vasicek formula)
R = Asset correlation (0.15 retail, 0.24 corporate)
```

See `docs/methodology.md` for full mathematical details, references, and data sources.

---

## 💡 Use Cases & Interview Talking Points

This project demonstrates:

1. **Quantitative Rigor:** Implementation of Basel III, IFRS 9, and Merton models with transparent math
2. **Systems Thinking:** End-to-end pipeline from data ingestion → feature engineering → modeling → stress testing → dashboard
3. **Cross-Market Capability:** Applying the same framework to two different economies (AU & US)
4. **Modern Stack:** Python, Streamlit, Plotly, pandas — industry-standard tools
5. **Real-World Data:** Public APIs from central banks and regulators (RBA, APRA, FRED)

### Example Interview Questions You Can Answer

**Q: How do you model credit risk in a portfolio?**
> "I built a full credit risk model using PD/LGD/EAD → ECL → RWA, calibrated to Australian and US macro data. The PD model is a log-linear function of unemployment, interest rates, and GDP growth. LGD varies with collateral values. I aggregate these at the portfolio level and calculate Basel III RWA using the Vasicek formula."

**Q: How do you stress test a loan portfolio?**
> "I implemented four scenarios: monetary tightening (+200bps rates), soft landing, funding shock, and severe recession. Each scenario applies shocks to macro variables, which flow through to PD and LGD increases. For example, in the tightening scenario, a 2pp unemployment rise increases PD by ~80% via the calibrated elasticity. I then recalculate ECL and RWA to measure capital impact."

**Q: How do you handle IFRS 9 staging?**
> "I classify loans into three stages based on SICR (significant increase in credit risk). Stage 1 uses 12-month ECL, Stage 2/3 use lifetime ECL. The simple rule is: Stage 3 if DPD > 90, Stage 2 if current PD > 2× origination PD, otherwise Stage 1. This is a simplified approach; in production you'd add qualitative overlays."

**Q: Can you explain the difference between through-the-cycle and point-in-time PD?**
> "Through-the-cycle PD is a long-run average, while point-in-time adjusts for current macro conditions. My model starts with a base PD (TTC) and multiplies by an exponential macro adjustment to get PIT. This makes PD responsive to unemployment, rates, and GDP without overfitting to short-term noise."

---

## 📈 Dashboard Features

The Streamlit dashboard includes:

### 1. Country Selection
- **Australia:** RBA cash rate, housing credit, unemployment, housing prices
- **United States:** Fed funds rate, total loans, unemployment, delinquency rates
- **Compare Both:** Side-by-side charts and metrics

### 2. Scenario Selection
- **Baseline:** No stress
- **Monetary Tightening:** +200bps rates, +2pp unemployment, -10% housing
- **Soft Landing:** +50bps rates, +0.5pp unemployment, flat housing
- **Funding Shock:** +75bps spreads, -15% credit growth
- **Custom:** User-defined sliders for rates, unemployment, housing shocks

### 3. Visualization Tabs
- **Macro Trends:** Time series of rates, unemployment, credit growth, GDP
- **Credit Risk Metrics:** CAI, PD evolution, LGD sensitivity
- **Portfolio Analysis:** Segment breakdown, EAD/ECL/RWA, capital requirements
- **Stress Testing:** Baseline vs. stressed ECL/RWA, percentage changes by segment

---

## 🌐 Data Sources

### Australia
- **Reserve Bank of Australia (RBA):** Cash rate, lending volumes, housing prices
  - https://www.rba.gov.au/statistics/
- **Australian Prudential Regulation Authority (APRA):** ADI statistics, capital ratios
  - https://www.apra.gov.au/monthly-authorised-deposit-taking-institution-statistics
- **Australian Bureau of Statistics (ABS):** Unemployment, GDP, CPI
  - https://www.abs.gov.au/

### United States
- **Federal Reserve Economic Data (FRED):** Fed funds, unemployment, delinquency, loans, CPI
  - https://fred.stlouisfed.org/
  - Series: FEDFUNDS, UNRATE, DRALACBS, TOTLL, CPIAUCSL, BAA10Y, GDPC1
- **FDIC:** Quarterly Banking Profile, capital ratios
- **BLS:** Labor market data

---

## 🔧 Extending the Model

### Add a New Portfolio Segment

```python
from src.modeling.portfolio import Portfolio

portfolio = Portfolio("My Bank")
portfolio.add_segment(
    segment_name="New Product",
    n_loans=10000,
    avg_exposure=50000,
    avg_pd=0.025,
    avg_lgd=0.40,
    correlation=0.15,
    segment_type='retail'
)
portfolio.calculate_ecl()
portfolio.calculate_rwa()
```

### Create a Custom Stress Scenario

```python
from src.stress.scenarios import CustomScenario

my_scenario = CustomScenario("Brexit-Style Shock", {
    'cash_rate': 0.0,  # No rate change
    'unemployment_rate': 3.0,  # +3pp unemployment
    'housing_price_growth': -15.0  # -15% housing
})

stressed_portfolio = portfolio.stress_portfolio(pd_shock=1.8, lgd_shock=1.3)
```

### Integrate Real Bank Data

Replace the synthetic portfolios in `src/modeling/portfolio.py` with:
- Loan-level data or segment aggregates
- Origination dates and LTV ratios
- Historical default/loss experience for calibration

---

## 📚 References

1. **Basel Committee on Banking Supervision (2017).** Basel III: Finalising post-crisis reforms
2. **IFRS Foundation (2014).** IFRS 9 Financial Instruments
3. **Merton, R.C. (1974).** On the Pricing of Corporate Debt
4. **Vasicek, O. (2002).** Loan Portfolio Value, Risk Magazine
5. **APRA Prudential Standard APS 220:** Credit Risk Management
6. **Federal Reserve:** Comprehensive Capital Analysis and Review (CCAR)

---

## 🤝 Contributing & Feedback

This is a portfolio/demonstration project. If you:
- Find a bug or modeling error
- Have suggestions for improvement
- Want to collaborate on extensions

Please open an issue or reach out directly.

---

## ⚖️ License & Disclaimer

**Purpose:** Educational and portfolio demonstration  
**Not for Production Use:** This model is not validated for regulatory capital calculation or commercial risk management without proper governance, back-testing, and bank-specific calibration.

All data sources are publicly available. No proprietary or confidential information is used.

---

## 👤 Author

**Ben Bones (Benjamin Benmas)**

This project showcases end-to-end credit risk modeling skills applicable to:
- Risk Analytics roles in banks/fintechs
- Quantitative Finance positions
- Credit Portfolio Management
- Regulatory Capital & Stress Testing teams

---

## 🎓 Next Steps

1. **Run the dashboard** and explore the interactive features
2. **Review `docs/methodology.md`** for mathematical details
3. **Test the modules** individually to understand each component
4. **Customize scenarios** to match your hypotheses about AU/US credit cycles
5. **Integrate real data** if you have access to proprietary loan datasets

---

**Built with:** Python • Streamlit • Plotly • Pandas • NumPy • Scikit-learn • FRED API

**Last Updated:** October 2025
