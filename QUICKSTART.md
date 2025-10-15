# Quick Start Guide

Get up and running with the Capital Flow & Credit Risk Model in 5 minutes.

---

## Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- Data processing: pandas, numpy, scipy
- Modeling: scikit-learn, statsmodels, xgboost
- Visualization: matplotlib, plotly, streamlit
- Data access: fredapi (for US data), openpyxl (for Excel)

---

## Step 2: Verify Installation

```bash
python test_all.py
```

This runs a comprehensive test of all modules:
- Data ingestion (AU & US)
- Credit risk models (CAI, PD, LGD, EAD, ECL)
- Portfolio analytics (RWA, capital)
- Stress testing scenarios
- Dashboard dependencies

**Expected output:**
```
============================================================
CAPITAL FLOW & CREDIT RISK MODEL - SYSTEM TEST
============================================================

[1/5] Testing Data Ingestion...
  ✓ AU data: 60 months, 18 columns
  ✓ US data: 60 months, 16 columns

[2/5] Testing Core Credit Risk Models...
  ✓ CAI range: 38.5 - 61.2
  ✓ PD range: 0.89% - 2.45%
  ✓ LGD range: 15.3% - 28.7%
  ✓ ECL for $100k exposure: $342.56

[3/5] Testing Portfolio Analytics...
  ✓ AU Portfolio - 4 segments
    Total EAD: $28.0B
    Total ECL: $125.4M
    Total RWA: $14.2B
    CET1 Required: $1.49B

[4/5] Testing Stress Scenarios...
  ✓ Loaded 4 scenarios
  ✓ Tightening scenario impact on AU portfolio:
    Baseline ECL: $125.4M
    Stressed ECL: $198.7M
    Increase: +58.5%

[5/5] Testing Dashboard Imports...
  ✓ Streamlit version: 1.xx.x
  ✓ Dashboard ready to launch

============================================================
ALL TESTS PASSED ✓
============================================================
```

---

## Step 3: Launch the Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

The dashboard will open in your browser at http://localhost:8501

---

## Step 4: Explore the Dashboard

### Country Selection (Sidebar)
- **Australia:** RBA cash rate, housing credit, APRA data
- **United States:** FRED data (Fed funds, unemployment, delinquency)
- **Compare Both:** Side-by-side charts

### Scenario Selection (Sidebar)
- **Baseline:** No stress
- **Monetary Tightening:** +200bps rates, +2pp unemployment, -10% housing
- **Soft Landing:** +50bps rates, +0.5pp unemployment, flat housing
- **Funding Shock:** +75bps spreads, -15% credit growth
- **Custom:** Use sliders to define your own shocks

### Tabs
1. **Macro Trends:** Time series of rates, unemployment, credit growth, GDP
2. **Credit Risk Metrics:** CAI, PD, LGD evolution over time
3. **Portfolio Analysis:** Segment breakdown, EAD/ECL/RWA, capital requirements
4. **Stress Testing:** Baseline vs. stressed scenarios with impact analysis

---

## Step 5: (Optional) Set Up Real US Data

The model uses synthetic US data by default. To fetch real data from FRED:

1. **Get a free FRED API key:**
   - Visit: https://fred.stlouisfed.org/docs/api/api_key.html
   - Sign up (free)
   - Copy your API key

2. **Configure the model:**
   - Open `src/ingest_us.py`
   - Find line 16: `FRED_API_KEY = None`
   - Change to: `FRED_API_KEY = "your_api_key_here"`

3. **Restart the dashboard:**
   ```bash
   streamlit run dashboards/streamlit_app.py
   ```

The model will now fetch real Fed funds rate, unemployment, delinquency rates, and more from FRED.

---

## Testing Individual Modules

You can run each module independently to see detailed output:

### Data Ingestion
```bash
python src/ingest_au.py
python src/ingest_us.py
```

**Output:** Summary of fetched data, date ranges, and key statistics

### Core Modeling
```bash
python src/modeling/core.py
```

**Output:** 
- CAI calculation example
- PD model calibration
- LGD scenarios
- ECL computation
- RWA calculation

### Portfolio Analytics
```bash
python src/modeling/portfolio.py
```

**Output:**
- AU and US portfolio summaries
- Segment-level EAD, ECL, RWA
- Capital requirements
- AU vs. US comparison

### Stress Testing
```bash
python src/stress/scenarios.py
```

**Output:**
- Scenario definitions
- Macro variable shocks
- Impact on unemployment, rates, housing prices

---

## Common Issues & Solutions

### Issue: "ModuleNotFoundError: No module named 'fredapi'"
**Solution:** Install missing dependency
```bash
pip install fredapi
```

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution:** Install streamlit
```bash
pip install streamlit plotly
```

### Issue: Dashboard shows "Error loading data"
**Solution:** 
1. Check internet connection (for real data APIs)
2. Verify FRED API key is correct (if using real US data)
3. The model will fall back to synthetic data if APIs fail

### Issue: Pandas FutureWarning about fillna method
**Solution:** This is a warning, not an error. The code works fine. To suppress:
```python
import warnings
warnings.filterwarnings('ignore')
```

---

## Next Steps

### 1. Understand the Methodology
Read `docs/methodology.md` for:
- Mathematical formulas for PD/LGD/EAD/ECL/RWA
- Basel III and IFRS 9 implementation details
- Data sources and references
- Model limitations and validation approach

### 2. Customize the Model

**Add a new portfolio segment:**
```python
from src.modeling.portfolio import Portfolio

portfolio = Portfolio("My Bank")
portfolio.add_segment(
    segment_name="Auto Loans",
    n_loans=50000,
    avg_exposure=25000,
    avg_pd=0.02,
    avg_lgd=0.35,
    correlation=0.15,
    segment_type='retail'
)
```

**Create a custom scenario:**
```python
from src.stress.scenarios import CustomScenario

brexit_shock = CustomScenario("Brexit Shock", {
    'cash_rate': -0.5,  # -50bps rate cut
    'unemployment_rate': 1.5,  # +1.5pp unemployment
    'housing_price_growth': -5.0  # -5% housing
})

stressed = portfolio.stress_portfolio(pd_shock=1.4, lgd_shock=1.2)
```

### 3. Explore the Notebooks

Jupyter notebooks are provided in the `notebooks/` directory:
- `01_ingest_AU.ipynb` - Australian data exploration
- `01_ingest_US.ipynb` - US data exploration
- `02_model_AU_US.ipynb` - Joint modeling and analysis

Launch Jupyter:
```bash
jupyter notebook notebooks/
```

### 4. Integrate Real Bank Data

To use your own portfolio data:
1. Replace synthetic portfolios in `src/modeling/portfolio.py`
2. Load loan-level data with actual PD/LGD/EAD
3. Calibrate models using historical defaults and losses
4. Run back-testing to validate model performance

---

## Resources

- **Methodology:** `docs/methodology.md`
- **Main README:** `README.md`
- **Test Script:** `test_all.py`
- **Data Sources:**
  - RBA: https://www.rba.gov.au/statistics/
  - APRA: https://www.apra.gov.au/
  - FRED: https://fred.stlouisfed.org/

---

## Support

If you encounter issues:
1. Check this guide first
2. Review error messages carefully
3. Ensure all dependencies are installed
4. Verify Python version (3.8+ required)

For questions or collaboration:
- Open an issue on GitHub
- Contact the author: Ben Bones (Benjamin Benmas)

---

**You're all set!** 🚀

Run `streamlit run dashboards/streamlit_app.py` and start exploring Australian and US credit risk dynamics.

