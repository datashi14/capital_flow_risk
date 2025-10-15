# Scenario Insights & Projections Guide

## Overview

The **Insights & Projections** feature transforms raw model outputs into professional risk report narratives. Instead of just seeing numbers, you get:

1. **Automated storytelling** from your scenario results
2. **Structured comparison tables** with deltas and percentages
3. **Actionable recommendations** based on severity
4. **Exportable reports** for documentation

---

## How It Works

### 1. Data Flow

```
Scenario → Model → Raw Outputs → Narrative Generator → Professional Report
```

**Raw Outputs:**
- CAI, PD, LGD, EAD, ECL, RWA, CET1 changes

**Narrative Generator:**
- Template-based insights
- Segment attribution
- Severity classification
- Management action suggestions

**Professional Report:**
- Executive summary
- Metrics comparison table
- Key insights (3-5 bullets)
- Recommended actions
- Downloadable TXT file

### 2. Accessing Insights

**In the Dashboard:**
1. Select a country (Australia or United States)
2. Choose a stress scenario from the sidebar
3. Navigate to the **"📊 Insights & Projections"** tab
4. View automatically generated insights
5. Download the report for documentation

**Programmatically:**
```python
from src.reporting.insights import generate_scenario_insights, create_risk_report

# Generate insights for one scenario
report = generate_scenario_insights(portfolio, df_macro, scenario, baseline_metrics)

# Or generate a full risk report with multiple scenarios
risk_report = create_risk_report(portfolio, df_macro, scenarios, country="Australia")
```

---

## Report Structure

### A. Scenario Summary

**Example:**
```
Scenario: Monetary Tightening
Description: Aggressive rate hikes to combat inflation

Headline: CAI -14.3%, ECL +56.2%, CET1 -0.7pp
```

### B. Metrics Comparison Table

| Metric | Baseline | Scenario | Δ (abs) | Δ (%) |
|--------|----------|----------|---------|-------|
| CAI | 0.83 | 0.71 | -0.12 | -14.3% |
| ECL | $1.25B | $1.95B | +$0.70B | +56.2% |
| RWA | $14.5B | $18.3B | +$3.8B | +26.2% |
| CET1 | 11.2% | 10.5% | -0.7pp | — |

### C. Key Insights

**Narrative templates automatically fill based on your data:**

1. **CAI:** "Credit conditions tighten materially; CAI falls 14.3%, driven by funding cost increase and unemployment +2pp."

2. **ECL:** "ECL rises +56.2%, with ~60% from LGD (collateral erosion) vs 40% from PD. Residential Mortgages contributes 65% of the increase."

3. **Capital:** "CET1 compresses 0.7pp under stress; headroom to regulatory minimum 6.0pp, to target 0.0pp — threshold management or RWA optimization required."

4. **Liquidity:** "LCR proxy dips below 1.0 under +50bps funding spread shock, implying elevated short-term liquidity risk."

### D. Segment Analysis

Deep-dive by portfolio segment:

| Segment | Baseline ECL | Stressed ECL | Change |
|---------|--------------|--------------|--------|
| Residential Mortgages | $18.5M | $30.1M | +62.7% |
| SME Lending | $12.3M | $17.0M | +38.2% |
| Personal Loans | $15.2M | $18.4M | +21.1% |

### E. Recommended Actions

**Severity-based recommendations:**

**High Severity** (ECL change > 40%):
- Tighten underwriting standards (LVR/LTI limits)
- Increase provisions proactively
- Review and potentially reduce exposures to high-risk segments
- Enhance monitoring frequency for vulnerable borrowers
- Consider portfolio rebalancing to reduce concentration risk

**Moderate Severity** (ECL change 20-40%):
- Monitor credit metrics closely (monthly vs. quarterly)
- Adjust pricing for risk (increase spreads for riskier segments)
- Maintain elevated provisions above baseline
- Review collateral valuations more frequently

**Mild Impact** (ECL change < 20%):
- Continue normal monitoring cadence
- No immediate action required
- Document scenario for stress testing records

---

## Pre-Defined Scenarios

### 1. Monetary Tightening

**Shocks:**
- Rates: +200 bps
- Unemployment: +2.0 pp
- Housing: -10%
- Spreads: +50 bps

**Expected Narrative:**
> "Under +200 bps and housing -10%, AU CAI falls ~15-20%; mortgage ECL dominates the loss expansion. US CAI also declines but dispersion is sectoral—SME PD leads while mortgage remains comparatively muted."

**Key Insight:**
> Mortgage PD is more sensitive to housing shocks (+0.6pp) than SME to unemployment, highlighting collateral-led risk.

### 2. Soft Landing

**Shocks:**
- Rates: +50 bps
- Unemployment: +0.5 pp
- Housing: -2%

**Expected Narrative:**
> "CAI -3-5%; ECL +10-15% with capital ratios broadly stable (CET1 -0.1-0.2pp). Portfolio tilt to low-LVR mortgage/prime consumer preserves resilience."

**Key Insight:**
> Manageable impact with adequate capital buffers maintained.

### 3. Funding Shock

**Shocks:**
- Spreads: +75 bps
- Rates: flat
- Unemployment: +0.5 pp
- Housing: flat

**Expected Narrative:**
> "Funding spreads +75 bps compress CAI ~8-12% with limited PD drift; losses rise mostly via LGD and EAD mix. Liquidity buffers (LCR proxy) approach 1.0—watch refinancing windows."

**Key Insight:**
> Liquidity stress dominates over credit deterioration in this scenario.

### 4. Custom Scenarios

**Use sliders to define:**
- Rate shock: -200 to +400 bps
- Unemployment shock: -2 to +5 pp
- Housing price shock: -30% to +20%

**Insight generation adapts** to your custom parameters.

---

## Using Insights for Interviews

### Example Question: "How do you communicate model results to senior management?"

**Strong Answer Using This Feature:**

> "I use a structured scenario insights framework that transforms model outputs into executive summaries. For example, in a monetary tightening scenario, instead of just reporting 'ECL increased by $700M,' I provide:
>
> 1. **Headline metrics:** CAI -14%, ECL +56%, CET1 -0.7pp
> 2. **Attribution:** 60% of ECL increase from LGD (collateral erosion), 40% from PD
> 3. **Segment focus:** Residential mortgages drive 65% of the impact
> 4. **Actionable recommendations:** Tighten LVR bands, increase monitoring frequency
> 5. **Exportable report:** One-page summary for board papers
>
> This approach ensures executives understand not just *what* changed, but *why* it matters and *what* to do about it."

### Example Question: "How do you design stress scenarios?"

**Strong Answer:**

> "I implement four core scenarios aligned with APRA/Fed frameworks:
>
> 1. **Tightening (+200bps, -10% housing):** Tests rate sensitivity and collateral dependence
> 2. **Soft Landing (+50bps):** Baseline normalization path
> 3. **Funding Shock (+75bps spreads):** Liquidity stress without policy tightening
> 4. **Custom:** Board-defined scenarios (e.g., geopolitical risks)
>
> Each scenario generates automated narratives explaining CAI changes, PD/LGD attribution, and capital impacts. The insights module identifies which segments are most vulnerable and recommends risk mitigants. This makes scenarios actionable, not just analytical."

---

## Customizing Narratives

### Programmatic Customization

```python
from src.reporting.insights import ScenarioReport

# Create custom report
report = ScenarioReport("Brexit Shock", "UK referendum spillovers")

# Add metrics
report.add_metric('CAI', baseline=0.83, scenario=0.75, unit='')
report.add_metric('ECL', baseline=1.25, scenario=1.60, unit='B')

# Add custom narratives
report.add_narrative(
    "Brexit contagion hits AU exporters; SME PD +1.2pp on trade disruption."
)
report.add_narrative(
    "Housing insulated due to domestic demand; mortgage ECL +12% vs SME +45%."
)

# Generate summary
print(report.generate_summary())

# Export
comparison_table = report.get_comparison_table()
comparison_table.to_csv("brexit_scenario_metrics.csv")
```

### Template Editing

Modify narrative templates in `src/reporting/insights.py`:

```python
def generate_cai_narrative(scenario, cai_base, cai_stress, latest_stress):
    cai_change_pct = (cai_stress / cai_base - 1) * 100
    
    # Customize this template
    return f"Credit availability contracts {abs(cai_change_pct):.1f}% as [YOUR LOGIC HERE]."
```

---

## Best Practices

### 1. Scenario Documentation

Always export scenario reports for audit trail:
- Click "Download Scenario Report (TXT)"
- Save with date stamp: `AU_Tightening_2025-10-15.txt`
- Include in board papers or ICAAP submission

### 2. Comparative Analysis

Run all four scenarios and compare:
```python
scenarios = [
    TighteningScenario(),
    SoftLandingScenario(),
    FundingShockScenario(),
    SevereRecessionScenario()
]

comparison = format_comparison_table([
    generate_scenario_insights(portfolio, df, s, baseline) 
    for s in scenarios
])

print(comparison)
```

### 3. Regular Updates

Re-run insights quarterly as macro data updates:
- Baseline metrics shift with portfolio composition
- Scenario calibrations may need adjustment
- Narrative priorities change (e.g., housing vs. unemployment focus)

### 4. Stakeholder Customization

Tailor narratives for different audiences:
- **Board:** High-level CAI/ECL/CET1 + actions
- **Risk Committee:** Segment attribution + PD/LGD drivers
- **Treasury:** Liquidity impacts + funding cost sensitivity
- **Business Units:** Segment-specific ECL changes + origination guidance

---

## Technical Implementation

### Architecture

```
┌─────────────┐
│   Scenario  │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌──────────────────┐
│  Portfolio  │─────▶│ apply_scenario   │
│  + Macro    │      │ _to_portfolio()  │
└─────────────┘      └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ Stressed Metrics │
                     │ (ECL, RWA, CAI)  │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │ generate_scenario│
                     │ _insights()      │
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  ScenarioReport  │
                     │  (with narratives│
                     └────────┬─────────┘
                              │
                              ▼
                     ┌──────────────────┐
                     │  Dashboard Tab   │
                     │  or Export       │
                     └──────────────────┘
```

### Key Classes

**`ScenarioReport`**: Container for metrics and narratives
- Methods: `add_metric()`, `add_narrative()`, `get_comparison_table()`, `generate_summary()`

**`generate_scenario_insights()`**: Main orchestration function
- Applies scenario → Calculates metrics → Generates narratives → Returns `ScenarioReport`

**`generate_*_narrative()`**: Template functions for specific insights
- `generate_cai_narrative()` - Credit availability
- `generate_ecl_narrative()` - Loss attribution
- `generate_capital_narrative()` - CET1 impact
- `generate_liquidity_narrative()` - Funding stress

---

## Extending the System

### Add New Narrative Types

1. Create new generator function:
```python
def generate_profitability_narrative(scenario, base_nim, stress_nim):
    nim_change = stress_nim - base_nim
    return f"Net interest margin compresses {abs(nim_change):.1f}bps under scenario."
```

2. Call in `generate_scenario_insights()`:
```python
report.add_narrative(generate_profitability_narrative(scenario, nim_base, nim_stress))
```

3. Add to dashboard tab for display

### Multi-Horizon Projections

Extend to 1/3/6 month horizons:
```python
for horizon in [1, 3, 6]:
    report = generate_scenario_insights(
        portfolio, df, scenario, baseline_metrics, horizon=horizon
    )
    reports.append((horizon, report))

# Compare accuracy across horizons
```

### Integration with External Systems

Export to common formats:
- **Word/PDF:** Use `python-docx` or `reportlab` to generate formatted reports
- **Email:** Automate distribution to risk committee
- **SharePoint:** Upload scenario reports for centralized access

---

##FAQ

**Q: Can I customize the narrative templates?**  
A: Yes! Edit functions in `src/reporting/insights.py` to change wording, add logic, or include additional metrics.

**Q: How do I compare AU vs. US scenarios?**  
A: Run `generate_scenario_insights()` for both countries and use `format_comparison_table()` to create side-by-side view.

**Q: Can I use this for regulatory stress testing (APRA/CCAR)?**  
A: Yes, as a starting point. You'll need to add:
- Multi-year projections (not just instant shock)
- Pre-provision net revenue (PPNR) modeling
- Detailed capital planning with dividend/buyback assumptions
- Regulatory-specific templates (APS 110/CCAR formats)

**Q: How accurate are the narratives?**  
A: They're template-based with parameterized logic. Review and customize for your specific context. Use as a first draft, not final output.

**Q: Can I export to Excel?**  
A: Yes:
```python
comparison_table.to_excel("scenario_comparison.xlsx", index=False)
```

---

## Summary

The **Insights & Projections** feature transforms your capital flow & credit risk model from a calculation engine into a **decision support system**. By automatically generating professional narratives, comparison tables, and actionable recommendations, it:

✅ **Saves time** - No manual report writing  
✅ **Ensures consistency** - Same structure across scenarios  
✅ **Improves communication** - Technical outputs → executive language  
✅ **Demonstrates expertise** - Shows you can operationalize models  

Perfect for interviews, board presentations, and regulatory submissions! 🚀


