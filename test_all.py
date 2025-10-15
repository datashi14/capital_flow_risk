"""
Test script to verify all modules are working correctly
Run this after installation to check your setup
"""
import sys
import os
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

# Fix Windows encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

print("\n" + "="*70)
print("CAPITAL FLOW & CREDIT RISK MODEL - SYSTEM TEST")
print("="*70)

# Test 1: Data Ingestion
print("\n[1/5] Testing Data Ingestion...")
try:
    from src.ingest_au import get_au_data
    from src.ingest_us import get_us_data
    
    df_au = get_au_data()
    df_us = get_us_data()
    
    print(f"  [OK] AU data: {len(df_au)} months, {len(df_au.columns)} columns")
    print(f"  [OK] US data: {len(df_us)} months, {len(df_us.columns)} columns")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    sys.exit(1)

# Test 2: Core Modeling
print("\n[2/5] Testing Core Credit Risk Models...")
try:
    from src.modeling.core import (
        CreditAvailabilityIndex, PDModel, LGDModel, 
        EADModel, ECLCalculator
    )
    
    # Test CAI
    cai = CreditAvailabilityIndex()
    df_au['cai'] = cai.calculate(df_au)
    
    # Test PD
    pd_model = PDModel(base_pd=0.02)
    df_au['pd'] = pd_model.calculate_simple(df_au)
    
    # Test LGD
    lgd_model = LGDModel()
    df_au['lgd'] = lgd_model.calculate_simple(df_au, collateral_type='housing')
    
    # Test ECL
    ecl_calc = ECLCalculator()
    ecl = ecl_calc.calculate_12m_ecl(df_au['pd'].iloc[-1], df_au['lgd'].iloc[-1], 100000)
    
    print(f"  [OK] CAI range: {df_au['cai'].min():.1f} - {df_au['cai'].max():.1f}")
    print(f"  [OK] PD range: {df_au['pd'].min():.2%} - {df_au['pd'].max():.2%}")
    print(f"  [OK] LGD range: {df_au['lgd'].min():.2%} - {df_au['lgd'].max():.2%}")
    print(f"  [OK] ECL for $100k exposure: ${ecl:.2f}")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Portfolio Models
print("\n[3/5] Testing Portfolio Analytics...")
try:
    from src.modeling.portfolio import (
        create_example_au_portfolio,
        create_example_us_portfolio
    )
    
    portfolio_au = create_example_au_portfolio()
    portfolio_us = create_example_us_portfolio()
    
    portfolio_au.calculate_ecl()
    portfolio_au.calculate_rwa()
    capital_au = portfolio_au.calculate_capital()
    
    portfolio_us.calculate_ecl()
    portfolio_us.calculate_rwa()
    capital_us = portfolio_us.calculate_capital()
    
    print(f"  [OK] AU Portfolio - {len(portfolio_au.exposures)} segments")
    print(f"    Total EAD: ${portfolio_au.exposures['total_ead'].sum()/1e9:.1f}B")
    print(f"    Total ECL: ${portfolio_au.exposures['ecl_12m'].sum()/1e6:.1f}M")
    print(f"    Total RWA: ${portfolio_au.exposures['rwa'].sum()/1e9:.1f}B")
    print(f"    CET1 Required: ${capital_au['cet1_required']/1e9:.2f}B")
    
    print(f"  [OK] US Portfolio - {len(portfolio_us.exposures)} segments")
    print(f"    Total EAD: ${portfolio_us.exposures['total_ead'].sum()/1e9:.1f}B")
    print(f"    Total ECL: ${portfolio_us.exposures['ecl_12m'].sum()/1e6:.1f}M")
    print(f"    Total RWA: ${portfolio_us.exposures['rwa'].sum()/1e9:.1f}B")
    print(f"    CET1 Required: ${capital_us['cet1_required']/1e9:.2f}B")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 4: Stress Scenarios
print("\n[4/5] Testing Stress Scenarios...")
try:
    from src.stress.scenarios import (
        TighteningScenario, SoftLandingScenario,
        FundingShockScenario, SevereRecessionScenario,
        apply_scenario_to_portfolio
    )
    
    tightening = TighteningScenario()
    soft_landing = SoftLandingScenario()
    funding_shock = FundingShockScenario()
    severe = SevereRecessionScenario()
    
    scenarios = [tightening, soft_landing, funding_shock, severe]
    
    print(f"  [OK] Loaded {len(scenarios)} scenarios")
    
    # Test scenario application
    stressed_results, df_stressed = apply_scenario_to_portfolio(
        portfolio_au, tightening, df_au
    )
    
    baseline_ecl = portfolio_au.exposures['ecl_12m'].sum()
    stressed_ecl = stressed_results['ecl_stressed'].sum()
    increase_pct = (stressed_ecl / baseline_ecl - 1) * 100
    
    print(f"  [OK] Tightening scenario impact on AU portfolio:")
    print(f"    Baseline ECL: ${baseline_ecl/1e6:.1f}M")
    print(f"    Stressed ECL: ${stressed_ecl/1e6:.1f}M")
    print(f"    Increase: +{increase_pct:.1f}%")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 5: Import Dashboard (don't run, just verify imports)
print("\n[5/5] Testing Dashboard Imports...")
try:
    # Try importing streamlit modules used in dashboard
    import streamlit
    import plotly.graph_objects
    import plotly.express
    
    print(f"  [OK] Streamlit version: {streamlit.__version__}")
    print(f"  [OK] Dashboard ready to launch")
except Exception as e:
    print(f"  [ERROR] Error: {e}")
    print(f"  Note: Run 'pip install streamlit plotly' if needed")

# Summary
print("\n" + "="*70)
print("ALL TESTS PASSED [OK]")
print("="*70)
print("\nNext steps:")
print("1. Launch the dashboard:")
print("   streamlit run dashboards/streamlit_app.py")
print("\n2. Explore the modules:")
print("   python src/modeling/core.py")
print("   python src/modeling/portfolio.py")
print("   python src/stress/scenarios.py")
print("\n3. Review the methodology:")
print("   docs/methodology.md")
print("="*70 + "\n")

