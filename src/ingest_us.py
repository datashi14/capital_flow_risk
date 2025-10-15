"""
US Data Ingestion Module
Fetches data from FRED (Federal Reserve Economic Data), FDIC, and BLS
"""
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# FRED API - users can get free API key at https://fred.stlouisfed.org/docs/api/api_key.html
FRED_API_KEY = None  # Set this to use real FRED data

try:
    from fredapi import Fred
    if FRED_API_KEY:
        fred = Fred(api_key=FRED_API_KEY)
    else:
        fred = None
except ImportError:
    fred = None


def fetch_fred_series(series_id, name, start_date='2020-01-01'):
    """
    Fetch a single FRED series
    """
    if fred:
        try:
            data = fred.get_series(series_id, observation_start=start_date)
            return pd.DataFrame({name: data})
        except Exception as e:
            print(f"Error fetching {series_id}: {e}")
            return None
    return None


def generate_synthetic_us_data(start_date='2020-01-01', end_date='2024-12-31'):
    """
    Generate realistic synthetic US data when FRED API is not available
    """
    dates = pd.date_range(start=start_date, end=end_date, freq='MS')
    
    # Fed Funds Rate: realistic path from 0.25% to 5.5% and back down
    n = len(dates)
    fed_rate = np.concatenate([
        np.linspace(0.25, 0.25, n//4),  # Low rates 2020-2021
        np.linspace(0.25, 5.5, n//4),   # Rapid hikes 2022
        np.linspace(5.5, 5.0, n//4),    # Peak
        np.linspace(5.0, 4.5, n - 3*(n//4))  # Slight cuts
    ])
    
    # Unemployment: 14% in 2020, down to 3.5-4%
    unemployment = np.concatenate([
        np.linspace(14.0, 8.0, n//4),
        np.linspace(8.0, 4.5, n//4),
        np.linspace(4.5, 3.7, n//2)
    ])
    
    # Delinquency rate: 3-11% range, correlated with unemployment
    delinquency = 2.0 + 0.5 * (unemployment - 4) + np.random.normal(0, 0.3, n)
    delinquency = np.clip(delinquency, 1.5, 11)
    
    # Total loans: $10T to $12T range
    total_loans = 10000000 + np.linspace(0, 2000000, n) + np.random.normal(0, 50000, n)
    
    # CPI: 2% baseline with 2022 spike
    cpi_base = 250
    cpi_growth = np.concatenate([
        np.linspace(0, 0.1, n//3),
        np.linspace(0.1, 0.25, n//6),  # Inflation spike
        np.linspace(0.25, 0.15, n - n//3 - n//6)
    ])
    cpi = cpi_base * np.cumprod(1 + cpi_growth/12)
    
    # GDP growth: quarterly, annualized
    gdp_dates = pd.date_range(start=start_date, end=end_date, freq='QS')
    gdp_growth = np.random.uniform(-2, 4, len(gdp_dates))
    gdp_df = pd.DataFrame({'gdp_growth': gdp_growth}, index=gdp_dates)
    gdp_df = gdp_df.resample('MS').ffill()
    
    # BAA spread (credit spread): 2-5%
    baa_spread = np.random.uniform(2.0, 5.0, n)
    
    # Tier 1 capital ratio: 12-14%
    tier1_ratio = np.random.uniform(12.0, 14.0, n)
    
    # Net charge-off rate: 0.3-2.5%
    charge_off = 0.5 + 0.15 * (unemployment - 4) + np.random.normal(0, 0.2, n)
    charge_off = np.clip(charge_off, 0.3, 2.5)
    
    df = pd.DataFrame({
        'fed_funds_rate': fed_rate,
        'unemployment_rate': unemployment,
        'delinquency_rate': delinquency,
        'total_loans': total_loans,
        'cpi': cpi,
        'baa_spread': baa_spread,
        'tier1_capital_ratio': tier1_ratio,
        'charge_off_rate': charge_off
    }, index=dates)
    
    # Add GDP growth
    df = df.join(gdp_df, how='left')
    df = df.fillna(method='ffill')
    
    return df


def fetch_us_fred_data():
    """
    Fetch key US economic indicators from FRED
    Series IDs:
    - FEDFUNDS: Federal Funds Effective Rate
    - UNRATE: Unemployment Rate
    - DRALACBS: Delinquency Rate on Loans, All Commercial Banks
    - TOTLL: Total Loans, All Commercial Banks
    - CPIAUCSL: Consumer Price Index
    - BAA10Y: Moody's BAA Corporate Bond Yield
    - DDOI06USA156NWDB: Bank Capital to Assets Ratio (proxy for Tier 1)
    """
    if not fred:
        print("FRED API not available or no API key set. Using synthetic data.")
        print("To use real data, install fredapi and set FRED_API_KEY in src/ingest_us.py")
        return generate_synthetic_us_data()
    
    try:
        print("Fetching US data from FRED...")
        
        # Fetch each series
        fed_rate = fetch_fred_series('FEDFUNDS', 'fed_funds_rate')
        unemployment = fetch_fred_series('UNRATE', 'unemployment_rate')
        delinquency = fetch_fred_series('DRALACBS', 'delinquency_rate')
        loans = fetch_fred_series('TOTLL', 'total_loans')
        cpi = fetch_fred_series('CPIAUCSL', 'cpi')
        baa = fetch_fred_series('BAA10Y', 'baa_spread')
        
        # Combine all series
        dfs = [df for df in [fed_rate, unemployment, delinquency, loans, cpi, baa] if df is not None]
        
        if dfs:
            df_us = pd.concat(dfs, axis=1)
            df_us = df_us.resample('MS').mean()
            df_us = df_us.fillna(method='ffill').fillna(method='bfill')
            
            # Add synthetic columns not easily available from FRED
            df_us['tier1_capital_ratio'] = np.random.uniform(12.0, 14.0, len(df_us))
            df_us['charge_off_rate'] = df_us['delinquency_rate'] * 0.4  # Approximation
            
            # Add GDP growth (quarterly)
            gdp = fetch_fred_series('GDPC1', 'gdp')
            if gdp is not None:
                gdp['gdp_growth'] = gdp['gdp'].pct_change(4) * 100
                df_us = df_us.join(gdp[['gdp_growth']], how='left')
                df_us['gdp_growth'] = df_us['gdp_growth'].fillna(method='ffill')
            
            return df_us
        else:
            print("Could not fetch FRED data, using synthetic data")
            return generate_synthetic_us_data()
            
    except Exception as e:
        print(f"Error fetching FRED data: {e}")
        return generate_synthetic_us_data()


def get_us_data():
    """
    Main function to fetch and combine all US data
    Returns: Clean monthly DataFrame with all US indicators
    """
    print("Fetching US data...")
    
    df_us = fetch_us_fred_data()
    
    # Calculate derived metrics
    df_us['credit_growth'] = df_us['total_loans'].pct_change(12) * 100
    df_us['inflation_rate'] = df_us['cpi'].pct_change(12) * 100
    
    # Real interest rate
    df_us['real_rate'] = df_us['fed_funds_rate'] - df_us['inflation_rate']
    
    # Funding cost (Fed Funds + spread)
    if 'baa_spread' in df_us.columns:
        df_us['funding_cost'] = df_us['fed_funds_rate'] + (df_us['baa_spread'] - df_us['fed_funds_rate']) * 0.3
    else:
        df_us['funding_cost'] = df_us['fed_funds_rate'] + 1.5
    
    # Default rate proxy
    df_us['default_rate_proxy'] = df_us['delinquency_rate'] * 0.5
    
    # Capital adequacy buffer (distance from minimum 8%)
    df_us['capital_buffer'] = df_us['tier1_capital_ratio'] - 8.0
    
    print(f"[OK] Fetched US data: {len(df_us)} months, {df_us.columns.size} indicators")
    print(f"  Date range: {df_us.index.min().strftime('%Y-%m')} to {df_us.index.max().strftime('%Y-%m')}")
    
    return df_us


def compare_au_us(df_au, df_us):
    """
    Create a comparison dataframe for AU and US indicators
    """
    comparison = pd.DataFrame({
        'AU_cash_rate': df_au['cash_rate'],
        'US_fed_rate': df_us['fed_funds_rate'],
        'AU_unemployment': df_au['unemployment_rate'],
        'US_unemployment': df_us['unemployment_rate'],
        'AU_default_proxy': df_au['default_rate_proxy'],
        'US_default_proxy': df_us['default_rate_proxy'],
        'AU_credit_growth': df_au['credit_growth_housing'],
        'US_credit_growth': df_us['credit_growth']
    })
    
    return comparison


if __name__ == "__main__":
    df = get_us_data()
    print("\nUS Data Summary:")
    print(df.tail())
    print("\nColumns:", df.columns.tolist())
