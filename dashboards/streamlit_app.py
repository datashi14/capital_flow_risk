"""
Capital Flow & Credit Risk Dashboard
Interactive Streamlit dashboard for AU/US credit risk modeling and stress testing
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.ingest_au import get_au_data
from src.ingest_us import get_us_data
from src.modeling.core import CreditAvailabilityIndex, PDModel, LGDModel, ECLCalculator
from src.modeling.portfolio import create_example_au_portfolio, create_example_us_portfolio
from src.stress.scenarios import (TighteningScenario, SoftLandingScenario, 
                                   FundingShockScenario, CustomScenario,
                                   apply_scenario_to_portfolio)
from src.reporting.insights import generate_scenario_insights, create_risk_report

# Theme colors
PRIMARY_COLOR = "#73AD6D"
SECONDARY_COLOR = "#5A8D52"
ACCENT_COLOR = "#8FC285"
BACKGROUND_COLOR = "#F8F9FA"
TEXT_COLOR = "#2C3E50"

# Page config
st.set_page_config(
    page_title="Capital Flow & Credit Risk — AU/US",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown(f"""
<style>
    .main {{
        background-color: {BACKGROUND_COLOR};
    }}
    .stButton>button {{
        background-color: {PRIMARY_COLOR};
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        font-weight: 600;
    }}
    .stButton>button:hover {{
        background-color: {SECONDARY_COLOR};
    }}
    h1, h2, h3 {{
        color: {TEXT_COLOR};
    }}
    .metric-card {{
        background-color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid {PRIMARY_COLOR};
    }}
    .stTabs [data-baseweb="tab-list"] {{
        gap: 2rem;
    }}
    .stTabs [data-baseweb="tab"] {{
        color: {TEXT_COLOR};
        font-weight: 600;
    }}
    .stTabs [aria-selected="true"] {{
        color: {PRIMARY_COLOR};
        border-bottom-color: {PRIMARY_COLOR};
    }}
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=3600)
def load_data():
    """Load AU and US data"""
    df_au = get_au_data()
    df_us = get_us_data()
    return df_au, df_us


@st.cache_resource
def load_portfolios():
    """Load portfolio examples"""
    portfolio_au = create_example_au_portfolio()
    portfolio_us = create_example_us_portfolio()
    return portfolio_au, portfolio_us


def create_time_series_chart(df, columns, title, ylabel, country_color):
    """Create time series chart"""
    fig = go.Figure()
    
    for col in columns:
        if col in df.columns:
            fig.add_trace(go.Scatter(
                x=df.index,
                y=df[col],
                mode='lines',
                name=col.replace('_', ' ').title(),
                line=dict(width=2, color=country_color if len(columns) == 1 else None)
            ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title=ylabel,
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_comparison_chart(df_au, df_us, var_au, var_us, title):
    """Create comparison chart for AU vs US"""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_au.index,
        y=df_au[var_au],
        mode='lines',
        name='Australia',
        line=dict(width=3, color=PRIMARY_COLOR)
    ))
    
    fig.add_trace(go.Scatter(
        x=df_us.index,
        y=df_us[var_us],
        mode='lines',
        name='United States',
        line=dict(width=3, color='#E74C3C')
    ))
    
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        hovermode='x unified',
        template='plotly_white',
        height=400,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig


def create_portfolio_breakdown(portfolio, color):
    """Create portfolio segment breakdown chart"""
    if 'ecl_12m' not in portfolio.exposures.columns:
        portfolio.calculate_ecl()
    
    fig = go.Figure(data=[
        go.Bar(
            x=portfolio.exposures['segment'],
            y=portfolio.exposures['total_ead'] / 1e9,
            name='Exposure (EAD)',
            marker_color=color,
            text=portfolio.exposures['total_ead'] / 1e9,
            texttemplate='$%{text:.1f}B',
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title=f"{portfolio.name} - Exposure by Segment",
        xaxis_title="Segment",
        yaxis_title="Exposure ($ Billions)",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def create_stress_comparison(baseline_ecl, stressed_ecl, scenario_name, color):
    """Create stress comparison chart"""
    categories = ['Baseline', scenario_name]
    values = [baseline_ecl / 1e9, stressed_ecl / 1e9]
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=values,
            marker_color=[color, '#E74C3C'],
            text=values,
            texttemplate='$%{text:.2f}B',
            textposition='outside'
        )
    ])
    
    increase_pct = (stressed_ecl / baseline_ecl - 1) * 100
    
    fig.update_layout(
        title=f"Expected Credit Loss Comparison<br><sub>Increase: +{increase_pct:.1f}%</sub>",
        yaxis_title="ECL ($ Billions)",
        template='plotly_white',
        height=400,
        showlegend=False
    )
    
    return fig


def main():
    # Header
    st.title("📊 Capital Flow & Credit Risk Model")
    st.markdown(f"### Australia & United States Credit Risk Analysis (2025)")
    st.markdown("---")
    
    # Load data
    with st.spinner("Loading data..."):
        df_au, df_us = load_data()
        portfolio_au, portfolio_us = load_portfolios()
    
    # Sidebar
    st.sidebar.title("⚙️ Configuration")
    
    # Country selector
    country = st.sidebar.radio(
        "Select Country",
        options=["Australia", "United States", "Compare Both"],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Scenario Selection")
    
    scenario_type = st.sidebar.selectbox(
        "Stress Scenario",
        ["Baseline (No Stress)", "Monetary Tightening", "Soft Landing", 
         "Funding Shock", "Custom"]
    )
    
    # Custom scenario parameters
    if scenario_type == "Custom":
        st.sidebar.markdown("#### Custom Scenario Parameters")
        rate_shock = st.sidebar.slider("Rate Shock (bps)", -200, 400, 0, 25) / 100
        unemp_shock = st.sidebar.slider("Unemployment Shock (pp)", -2.0, 5.0, 0.0, 0.5)
        housing_shock = st.sidebar.slider("Housing Price Shock (%)", -30, 20, 0, 5)
        
        scenario = CustomScenario("Custom", {
            'cash_rate': rate_shock,
            'fed_funds_rate': rate_shock,
            'unemployment_rate': unemp_shock,
            'housing_price_growth': housing_shock
        })
    elif scenario_type == "Monetary Tightening":
        scenario = TighteningScenario()
    elif scenario_type == "Soft Landing":
        scenario = SoftLandingScenario()
    elif scenario_type == "Funding Shock":
        scenario = FundingShockScenario()
    else:
        scenario = None
    
    # Main content
    if country == "Compare Both":
        st.header("🌏 Australia vs United States Comparison")
        
        # Key metrics comparison
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "AU Cash Rate",
                f"{df_au['cash_rate'].iloc[-1]:.2f}%",
                f"{df_au['cash_rate'].iloc[-1] - df_au['cash_rate'].iloc[-12]:.2f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "US Fed Funds",
                f"{df_us['fed_funds_rate'].iloc[-1]:.2f}%",
                f"{df_us['fed_funds_rate'].iloc[-1] - df_us['fed_funds_rate'].iloc[-12]:.2f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "AU Unemployment",
                f"{df_au['unemployment_rate'].iloc[-1]:.1f}%",
                f"{df_au['unemployment_rate'].iloc[-1] - df_au['unemployment_rate'].iloc[-12]:.1f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "US Unemployment",
                f"{df_us['unemployment_rate'].iloc[-1]:.1f}%",
                f"{df_us['unemployment_rate'].iloc[-1] - df_us['unemployment_rate'].iloc[-12]:.1f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Comparison charts
        tab1, tab2, tab3 = st.tabs(["📈 Macro Indicators", "💰 Credit Risk", "🏦 Portfolios"])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_comparison_chart(
                    df_au, df_us,
                    'cash_rate', 'fed_funds_rate',
                    'Policy Rates Comparison'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_comparison_chart(
                    df_au, df_us,
                    'unemployment_rate', 'unemployment_rate',
                    'Unemployment Rate Comparison'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                if 'credit_growth_housing' in df_au.columns and 'credit_growth' in df_us.columns:
                    fig = create_comparison_chart(
                        df_au, df_us,
                        'credit_growth_housing', 'credit_growth',
                        'Credit Growth Comparison'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'default_rate_proxy' in df_au.columns and 'default_rate_proxy' in df_us.columns:
                    fig = create_comparison_chart(
                        df_au, df_us,
                        'default_rate_proxy', 'default_rate_proxy',
                        'Default Rate Proxy Comparison'
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Calculate CAI for both countries
            cai_model = CreditAvailabilityIndex()
            df_au['cai'] = cai_model.calculate(df_au)
            df_us['cai'] = cai_model.calculate(
                df_us, 
                rate_col='fed_funds_rate',
                credit_col='credit_growth',
                unemp_col='unemployment_rate',
                gdp_col='gdp_growth'
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_time_series_chart(
                    df_au, ['cai'],
                    'Australia - Credit Availability Index',
                    'CAI (0-100)',
                    PRIMARY_COLOR
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_time_series_chart(
                    df_us, ['cai'],
                    'United States - Credit Availability Index',
                    'CAI (0-100)',
                    '#E74C3C'
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🇦🇺 Australian Portfolio")
                portfolio_au.calculate_ecl()
                portfolio_au.calculate_rwa()
                capital_au = portfolio_au.calculate_capital()
                
                st.metric("Total Exposure", f"${portfolio_au.exposures['total_ead'].sum() / 1e9:.1f}B")
                st.metric("Total ECL (12m)", f"${portfolio_au.exposures['ecl_12m'].sum() / 1e9:.2f}B")
                st.metric("Total RWA", f"${portfolio_au.exposures['rwa'].sum() / 1e9:.1f}B")
                st.metric("CET1 Required", f"${capital_au['cet1_required'] / 1e9:.2f}B")
                
                fig = create_portfolio_breakdown(portfolio_au, PRIMARY_COLOR)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("🇺🇸 US Portfolio")
                portfolio_us.calculate_ecl()
                portfolio_us.calculate_rwa()
                capital_us = portfolio_us.calculate_capital()
                
                st.metric("Total Exposure", f"${portfolio_us.exposures['total_ead'].sum() / 1e9:.1f}B")
                st.metric("Total ECL (12m)", f"${portfolio_us.exposures['ecl_12m'].sum() / 1e9:.2f}B")
                st.metric("Total RWA", f"${portfolio_us.exposures['rwa'].sum() / 1e9:.1f}B")
                st.metric("CET1 Required", f"${capital_us['cet1_required'] / 1e9:.2f}B")
                
                fig = create_portfolio_breakdown(portfolio_us, '#E74C3C')
                st.plotly_chart(fig, use_container_width=True)
    
    else:
        # Single country view
        if country == "Australia":
            df = df_au
            portfolio = portfolio_au
            country_color = PRIMARY_COLOR
            country_emoji = "🇦🇺"
            rate_col = 'cash_rate'
            credit_col = 'credit_growth_housing'
        else:
            df = df_us
            portfolio = portfolio_us
            country_color = '#E74C3C'
            country_emoji = "🇺🇸"
            rate_col = 'fed_funds_rate'
            credit_col = 'credit_growth'
        
        st.header(f"{country_emoji} {country} Credit Risk Analysis")
        
        # Key metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Policy Rate",
                f"{df[rate_col].iloc[-1]:.2f}%",
                f"{df[rate_col].iloc[-1] - df[rate_col].iloc[-12]:.2f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.metric(
                "Unemployment",
                f"{df['unemployment_rate'].iloc[-1]:.1f}%",
                f"{df['unemployment_rate'].iloc[-1] - df['unemployment_rate'].iloc[-12]:.1f}pp"
            )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if credit_col in df.columns:
                st.metric(
                    "Credit Growth",
                    f"{df[credit_col].iloc[-1]:.1f}%",
                    f"{df[credit_col].iloc[-1] - df[credit_col].iloc[-12]:.1f}pp"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            if 'default_rate_proxy' in df.columns:
                st.metric(
                    "Default Rate Proxy",
                    f"{df['default_rate_proxy'].iloc[-1]:.2f}%",
                    f"{df['default_rate_proxy'].iloc[-1] - df['default_rate_proxy'].iloc[-12]:.2f}pp"
                )
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📈 Macro Trends", 
            "💰 Credit Risk Metrics", 
            "🏦 Portfolio Analysis",
            "⚠️ Stress Testing",
            "📊 Insights & Projections"
        ])
        
        with tab1:
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_time_series_chart(
                    df, [rate_col],
                    f'{country} Policy Rate',
                    'Rate (%)',
                    country_color
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_time_series_chart(
                    df, ['unemployment_rate'],
                    f'{country} Unemployment Rate',
                    'Unemployment (%)',
                    country_color
                )
                st.plotly_chart(fig, use_container_width=True)
            
            col3, col4 = st.columns(2)
            
            with col3:
                if credit_col in df.columns:
                    fig = create_time_series_chart(
                        df, [credit_col],
                        f'{country} Credit Growth',
                        'Growth (%)',
                        country_color
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col4:
                if 'gdp_growth' in df.columns:
                    fig = create_time_series_chart(
                        df, ['gdp_growth'],
                        f'{country} GDP Growth',
                        'Growth (%)',
                        country_color
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Calculate credit risk metrics
            cai_model = CreditAvailabilityIndex()
            pd_model = PDModel()
            lgd_model = LGDModel()
            
            df['cai'] = cai_model.calculate(
                df, rate_col=rate_col, credit_col=credit_col
            )
            df['pd'] = pd_model.calculate_simple(
                df, rate_col=rate_col
            )
            
            if country == "Australia" and 'housing_price_growth' in df.columns:
                df['lgd'] = lgd_model.calculate_simple(df, collateral_type='housing')
            else:
                df['lgd'] = 0.45  # Fixed LGD for simplicity
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_time_series_chart(
                    df, ['cai'],
                    'Credit Availability Index',
                    'CAI (0-100)',
                    country_color
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_time_series_chart(
                    df, ['pd'],
                    'Probability of Default (PD)',
                    'PD',
                    country_color
                )
                # Format as percentage
                fig.update_yaxes(tickformat=".1%")
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            st.subheader(f"{country} Portfolio Overview")
            
            portfolio.calculate_ecl()
            portfolio.calculate_rwa()
            capital = portfolio.calculate_capital()
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Exposure (EAD)",
                    f"${portfolio.exposures['total_ead'].sum() / 1e9:.1f}B"
                )
            
            with col2:
                st.metric(
                    "Total ECL (12-month)",
                    f"${portfolio.exposures['ecl_12m'].sum() / 1e9:.2f}B"
                )
            
            with col3:
                st.metric(
                    "Total RWA",
                    f"${portfolio.exposures['rwa'].sum() / 1e9:.1f}B"
                )
            
            with col4:
                st.metric(
                    "CET1 Capital Required",
                    f"${capital['cet1_required'] / 1e9:.2f}B"
                )
            
            st.markdown("---")
            
            # Portfolio breakdown
            fig = create_portfolio_breakdown(portfolio, country_color)
            st.plotly_chart(fig, use_container_width=True)
            
            # Detailed segment table
            st.subheader("Segment Details")
            display_df = portfolio.exposures[['segment', 'n_loans', 'avg_pd', 'avg_lgd', 
                                             'total_ead', 'ecl_12m', 'rwa']].copy()
            display_df['avg_pd'] = display_df['avg_pd'].apply(lambda x: f"{x:.2%}")
            display_df['avg_lgd'] = display_df['avg_lgd'].apply(lambda x: f"{x:.2%}")
            display_df['total_ead'] = display_df['total_ead'].apply(lambda x: f"${x/1e9:.2f}B")
            display_df['ecl_12m'] = display_df['ecl_12m'].apply(lambda x: f"${x/1e6:.1f}M")
            display_df['rwa'] = display_df['rwa'].apply(lambda x: f"${x/1e9:.2f}B")
            
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        with tab4:
            st.subheader(f"⚠️ Stress Testing: {scenario_type}")
            
            if scenario:
                st.info(f"**Scenario:** {scenario.description}")
                
                # Apply scenario
                stressed_results, df_stressed = apply_scenario_to_portfolio(
                    portfolio, scenario, df
                )
                
                # Show stressed macro variables
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    base_rate = df[rate_col].iloc[-1]
                    stress_rate = df_stressed[rate_col].iloc[-1]
                    st.metric(
                        "Policy Rate",
                        f"{stress_rate:.2f}%",
                        f"{stress_rate - base_rate:+.2f}pp"
                    )
                
                with col2:
                    base_unemp = df['unemployment_rate'].iloc[-1]
                    stress_unemp = df_stressed['unemployment_rate'].iloc[-1]
                    st.metric(
                        "Unemployment",
                        f"{stress_unemp:.1f}%",
                        f"{stress_unemp - base_unemp:+.1f}pp"
                    )
                
                with col3:
                    if credit_col in df_stressed.columns:
                        base_credit = df[credit_col].iloc[-1]
                        stress_credit = df_stressed[credit_col].iloc[-1]
                        st.metric(
                            "Credit Growth",
                            f"{stress_credit:.1f}%",
                            f"{stress_credit - base_credit:+.1f}pp"
                        )
                
                st.markdown("---")
                
                # Stressed portfolio metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    baseline_ecl = portfolio.exposures['ecl_12m'].sum()
                    stressed_ecl = stressed_results['ecl_stressed'].sum()
                    
                    fig = create_stress_comparison(
                        baseline_ecl, stressed_ecl,
                        scenario_type, country_color
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    baseline_rwa = portfolio.exposures['rwa'].sum()
                    stressed_rwa = stressed_results['rwa_stressed'].sum()
                    
                    categories = ['Baseline', scenario_type]
                    values = [baseline_rwa / 1e9, stressed_rwa / 1e9]
                    
                    fig = go.Figure(data=[
                        go.Bar(
                            x=categories,
                            y=values,
                            marker_color=[country_color, '#E74C3C'],
                            text=values,
                            texttemplate='$%{text:.1f}B',
                            textposition='outside'
                        )
                    ])
                    
                    increase_pct = (stressed_rwa / baseline_rwa - 1) * 100
                    
                    fig.update_layout(
                        title=f"Risk-Weighted Assets Comparison<br><sub>Increase: +{increase_pct:.1f}%</sub>",
                        yaxis_title="RWA ($ Billions)",
                        template='plotly_white',
                        height=400,
                        showlegend=False
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                # Segment-level stress
                st.subheader("Stressed Results by Segment")
                stress_df = stressed_results[['segment', 'ecl_stressed', 'rwa_stressed']].copy()
                stress_df = stress_df.merge(
                    portfolio.exposures[['segment', 'ecl_12m', 'rwa']],
                    on='segment'
                )
                stress_df['ecl_change'] = (stress_df['ecl_stressed'] / stress_df['ecl_12m'] - 1) * 100
                stress_df['rwa_change'] = (stress_df['rwa_stressed'] / stress_df['rwa'] - 1) * 100
                
                display_stress = stress_df[['segment', 'ecl_12m', 'ecl_stressed', 'ecl_change',
                                           'rwa', 'rwa_stressed', 'rwa_change']].copy()
                display_stress['ecl_12m'] = display_stress['ecl_12m'].apply(lambda x: f"${x/1e6:.1f}M")
                display_stress['ecl_stressed'] = display_stress['ecl_stressed'].apply(lambda x: f"${x/1e6:.1f}M")
                display_stress['ecl_change'] = display_stress['ecl_change'].apply(lambda x: f"{x:+.1f}%")
                display_stress['rwa'] = display_stress['rwa'].apply(lambda x: f"${x/1e9:.2f}B")
                display_stress['rwa_stressed'] = display_stress['rwa_stressed'].apply(lambda x: f"${x/1e9:.2f}B")
                display_stress['rwa_change'] = display_stress['rwa_change'].apply(lambda x: f"{x:+.1f}%")
                
                st.dataframe(display_stress, use_container_width=True, hide_index=True)
            
            else:
                st.info("Select a stress scenario from the sidebar to see results")
        
        with tab5:
            st.subheader("📊 Scenario Insights & Projections")
            
            st.markdown("""
            This tab provides professional risk report narratives and scenario comparisons.
            Select a scenario from the sidebar to see detailed insights.
            """)
            
            if scenario:
                # Calculate baseline metrics
                portfolio.calculate_ecl()
                portfolio.calculate_rwa()
                capital = portfolio.calculate_capital()
                
                # Calculate CAI
                cai_model = CreditAvailabilityIndex()
                df['cai'] = cai_model.calculate(df, rate_col=rate_col, credit_col=credit_col)
                
                baseline_metrics = {
                    'ecl': portfolio.exposures['ecl_12m'].sum(),
                    'rwa': portfolio.exposures['rwa'].sum(),
                    'cet1': 11.2,
                    'cai': df['cai'].iloc[-1]
                }
                
                # Generate scenario insights
                report = generate_scenario_insights(
                    portfolio, df, scenario, baseline_metrics
                )
                
                # Display scenario summary
                st.markdown(f"### Scenario: {report.scenario_name}")
                st.info(f"**Description:** {report.description}")
                
                # Key metrics comparison
                st.markdown("#### 📈 Key Metrics Comparison")
                comparison_df = report.get_comparison_table()
                
                # Style the dataframe
                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Narratives
                st.markdown("#### 💡 Key Insights")
                for i, narrative in enumerate(report.narratives, 1):
                    st.markdown(f"**{i}.** {narrative}")
                
                # Segment deep-dive
                st.markdown("#### 🏦 Segment Analysis")
                
                segment_metrics = []
                for metric_name, values in report.metrics.items():
                    if 'ECL' in metric_name and metric_name != 'ECL':
                        segment_metrics.append({
                            'Segment': metric_name.replace(' ECL', ''),
                            'Baseline ECL': f"${values['baseline']:.1f}{values['unit']}",
                            'Stressed ECL': f"${values['scenario']:.1f}{values['unit']}",
                            'Change': f"{values['delta_pct']:+.1f}%"
                        })
                
                if segment_metrics:
                    segment_df = pd.DataFrame(segment_metrics)
                    st.dataframe(segment_df, use_container_width=True, hide_index=True)
                
                # Management actions
                st.markdown("#### 🎯 Recommended Actions")
                
                ecl_change = report.metrics.get('ECL', {}).get('delta_pct', 0)
                
                if abs(ecl_change) > 40:
                    st.warning("**High Severity** - Immediate action required")
                    st.markdown("""
                    - Tighten underwriting standards (LVR/LTI limits)
                    - Increase provisions proactively
                    - Review and potentially reduce exposures to high-risk segments
                    - Enhance monitoring frequency for vulnerable borrowers
                    - Consider portfolio rebalancing to reduce concentration risk
                    """)
                elif abs(ecl_change) > 20:
                    st.info("**Moderate Severity** - Enhanced monitoring")
                    st.markdown("""
                    - Monitor credit metrics closely (monthly vs. quarterly)
                    - Adjust pricing for risk (increase spreads for riskier segments)
                    - Maintain elevated provisions above baseline
                    - Review collateral valuations more frequently
                    """)
                else:
                    st.success("**Mild Impact** - Business as usual with elevated vigilance")
                    st.markdown("""
                    - Continue normal monitoring cadence
                    - No immediate action required
                    - Document scenario for stress testing records
                    """)
                
                # Download report
                st.markdown("---")
                st.markdown("#### 📥 Export Report")
                
                report_text = f"""# {country} - {report.scenario_name} Scenario Report

## Scenario Description
{report.description}

## Key Metrics
{comparison_df.to_string(index=False)}

## Key Insights
"""
                for i, narrative in enumerate(report.narratives, 1):
                    report_text += f"{i}. {narrative}\n"
                
                st.download_button(
                    label="Download Scenario Report (TXT)",
                    data=report_text,
                    file_name=f"{country}_{report.scenario_name.replace(' ', '_')}_report.txt",
                    mime="text/plain"
                )
            
            else:
                st.info("👈 Select a stress scenario from the sidebar to generate insights")
                
                # Show example insights structure
                st.markdown("#### Example Insights Structure")
                st.markdown("""
                When you select a scenario, you'll see:
                
                1. **Metrics Comparison Table** - Baseline vs. Stressed for CAI, PD, LGD, ECL, RWA, CET1
                2. **Narrative Insights** - Automatically generated explanations of:
                   - Credit availability changes (CAI)
                   - Loss drivers (PD vs. LGD contribution)
                   - Capital impact (CET1 compression)
                   - Liquidity implications (LCR proxy)
                3. **Segment Analysis** - Deep-dive by portfolio segment
                4. **Recommended Actions** - Risk management responses based on severity
                5. **Exportable Report** - Download as text file for documentation
                """)
    
    # Footer
    st.markdown("---")
    st.markdown(
        f"""
        <div style='text-align: center; color: {TEXT_COLOR}; padding: 1rem;'>
            <p><strong>Capital Flow & Credit Risk Model — Australia & United States (2025)</strong></p>
            <p>Author: Ben Bones (Benjamin Benmas)</p>
            <p style='font-size: 0.9em;'>
                Transparent credit risk modeling with PD/LGD/EAD calculations, 
                ECL estimation, and macro stress testing
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
