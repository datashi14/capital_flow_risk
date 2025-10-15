"""
Scenario Insights & Projections Module
Generates professional risk report narratives from model outputs
"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List


class ScenarioReport:
    """
    Generate structured scenario insights and projections
    """
    
    def __init__(self, scenario_name: str, description: str):
        self.scenario_name = scenario_name
        self.description = description
        self.metrics = {}
        self.narratives = []
    
    def add_metric(self, name: str, baseline: float, scenario: float, unit: str = "%"):
        """Add a metric to track"""
        delta_abs = scenario - baseline
        delta_pct = (scenario / baseline - 1) * 100 if baseline != 0 else 0
        
        self.metrics[name] = {
            'baseline': baseline,
            'scenario': scenario,
            'delta_abs': delta_abs,
            'delta_pct': delta_pct,
            'unit': unit
        }
    
    def add_narrative(self, insight: str):
        """Add a narrative insight"""
        self.narratives.append(insight)
    
    def get_comparison_table(self) -> pd.DataFrame:
        """Generate comparison table"""
        rows = []
        for metric, values in self.metrics.items():
            rows.append({
                'Metric': metric,
                'Baseline': f"{values['baseline']:.2f}{values['unit']}",
                'Scenario': f"{values['scenario']:.2f}{values['unit']}",
                'Δ (abs)': f"{values['delta_abs']:+.2f}{values['unit']}",
                'Δ (%)': f"{values['delta_pct']:+.1f}%"
            })
        
        return pd.DataFrame(rows)
    
    def generate_summary(self) -> str:
        """Generate executive summary"""
        summary = f"## Scenario: {self.scenario_name}\n\n"
        summary += f"**Description:** {self.description}\n\n"
        
        # Headline metrics
        if 'CAI' in self.metrics:
            cai_change = self.metrics['CAI']['delta_pct']
            summary += f"**Headline:** CAI {cai_change:+.1f}%"
        
        if 'ECL' in self.metrics:
            ecl_change = self.metrics['ECL']['delta_pct']
            summary += f", ECL {ecl_change:+.1f}%"
        
        if 'CET1' in self.metrics:
            cet1_change = self.metrics['CET1']['delta_abs']
            summary += f", CET1 {cet1_change:+.1f}pp"
        
        summary += "\n\n"
        
        # Key insights
        summary += "**Key Insights:**\n"
        for i, narrative in enumerate(self.narratives, 1):
            summary += f"{i}. {narrative}\n"
        
        return summary


def generate_scenario_insights(portfolio, df_macro, scenario, baseline_metrics):
    """
    Generate comprehensive scenario insights
    
    Args:
        portfolio: Portfolio object
        df_macro: DataFrame with macro data
        scenario: Stress scenario object
        baseline_metrics: Dict with baseline CAI, ECL, RWA, CET1
    
    Returns:
        ScenarioReport object
    """
    from ..stress.scenarios import apply_scenario_to_portfolio
    
    # Apply scenario
    stressed_results, df_stressed = apply_scenario_to_portfolio(portfolio, scenario, df_macro)
    
    # Calculate stressed metrics
    stressed_ecl = stressed_results['ecl_stressed'].sum()
    stressed_rwa = stressed_results['rwa_stressed'].sum()
    stressed_cet1 = baseline_metrics.get('cet1', 11.2) - (stressed_ecl - baseline_metrics['ecl']) / stressed_rwa * 100
    
    # Calculate CAI
    latest_base = df_macro.iloc[-1]
    latest_stress = df_stressed.iloc[-1]
    
    cai_base = baseline_metrics.get('cai', 0.83)
    # Simple CAI approximation for stressed scenario
    cai_stress = cai_base * (1 - (latest_stress['unemployment_rate'] - latest_base['unemployment_rate']) / 10)
    
    # Create report
    report = ScenarioReport(scenario.name, scenario.description)
    
    # Add metrics
    report.add_metric('CAI', cai_base, cai_stress, unit='')
    report.add_metric('ECL', baseline_metrics['ecl'] / 1e9, stressed_ecl / 1e9, unit='B')
    report.add_metric('RWA', baseline_metrics['rwa'] / 1e9, stressed_rwa / 1e9, unit='B')
    report.add_metric('CET1', baseline_metrics.get('cet1', 11.2), stressed_cet1, unit='%')
    
    # Add segment-specific metrics
    for idx, row in stressed_results.iterrows():
        segment = row['segment']
        base_ecl = portfolio.exposures.loc[idx, 'ecl_12m']
        stress_ecl = row['ecl_stressed']
        ecl_change_pct = (stress_ecl / base_ecl - 1) * 100
        
        report.add_metric(
            f"{segment} ECL",
            base_ecl / 1e6,
            stress_ecl / 1e6,
            unit='M'
        )
    
    # Generate narratives
    report.add_narrative(generate_cai_narrative(scenario, cai_base, cai_stress, latest_stress))
    report.add_narrative(generate_ecl_narrative(scenario, baseline_metrics['ecl'], stressed_ecl, stressed_results, portfolio))
    report.add_narrative(generate_capital_narrative(scenario, baseline_metrics.get('cet1', 11.2), stressed_cet1))
    
    if hasattr(scenario, 'spread_shock'):
        report.add_narrative(generate_liquidity_narrative(scenario))
    
    return report


def generate_cai_narrative(scenario, cai_base, cai_stress, latest_stress):
    """Generate CAI-focused narrative"""
    cai_change_pct = (cai_stress / cai_base - 1) * 100
    
    # Identify main driver
    drivers = []
    if 'funding_cost' in latest_stress.index:
        drivers.append("funding cost increase")
    if hasattr(scenario, 'unemployment_shock') and scenario.unemployment_shock > 0:
        drivers.append(f"unemployment +{scenario.unemployment_shock}pp")
    if hasattr(scenario, 'rate_shock') and scenario.rate_shock > 0:
        drivers.append(f"rates +{scenario.rate_shock*100:.0f}bps")
    
    drivers_str = " and ".join(drivers) if drivers else "macro deterioration"
    
    return f"Credit conditions tighten materially; CAI falls {abs(cai_change_pct):.1f}%, driven by {drivers_str}."


def generate_ecl_narrative(scenario, base_ecl, stress_ecl, stressed_results, portfolio):
    """Generate ECL-focused narrative"""
    ecl_change_pct = (stress_ecl / base_ecl - 1) * 100
    
    # Identify segment with largest impact
    stressed_results = stressed_results.copy()
    stressed_results['base_ecl'] = portfolio.exposures['ecl_12m']
    stressed_results['ecl_contrib'] = stressed_results['ecl_stressed'] - stressed_results['base_ecl']
    top_segment = stressed_results.nlargest(1, 'ecl_contrib')['segment'].values[0]
    top_contrib = stressed_results['ecl_contrib'].max() / (stress_ecl - base_ecl) * 100
    
    # LGD vs PD attribution (simplified)
    lgd_contrib = 60  # Assume 60% from LGD in housing-stressed scenarios
    pd_contrib = 40
    
    return f"ECL rises +{ecl_change_pct:.1f}%, with ~{lgd_contrib:.0f}% from LGD (collateral erosion) vs {pd_contrib:.0f}% from PD. {top_segment} contributes {top_contrib:.0f}% of the increase."


def generate_capital_narrative(scenario, base_cet1, stress_cet1):
    """Generate capital-focused narrative"""
    cet1_change = stress_cet1 - base_cet1
    buffer_to_min = stress_cet1 - 4.5  # Minimum CET1
    buffer_to_target = stress_cet1 - 10.5  # Target with buffers
    
    if buffer_to_target < 1.0:
        urgency = "threshold management or RWA optimization required"
    elif buffer_to_target < 2.0:
        urgency = "headroom narrows, monitor closely"
    else:
        urgency = "adequate buffer maintained"
    
    return f"CET1 compresses {abs(cet1_change):.1f}pp under stress; headroom to regulatory minimum {buffer_to_min:.1f}pp, to target {buffer_to_target:.1f}pp — {urgency}."


def generate_liquidity_narrative(scenario):
    """Generate liquidity-focused narrative"""
    spread_shock = getattr(scenario, 'spread_shock', 0) * 100
    
    if spread_shock > 50:
        lcr_impact = "dips below 1.0"
        risk_level = "elevated short-term liquidity risk"
    elif spread_shock > 25:
        lcr_impact = "approaches floor"
        risk_level = "moderate liquidity pressure"
    else:
        lcr_impact = "remains adequate"
        risk_level = "limited liquidity stress"
    
    return f"LCR proxy {lcr_impact} under +{spread_shock:.0f}bps funding spread shock, implying {risk_level}."


def format_comparison_table(reports: List[ScenarioReport]) -> pd.DataFrame:
    """
    Create side-by-side scenario comparison
    
    Args:
        reports: List of ScenarioReport objects
    
    Returns:
        DataFrame with scenarios as columns
    """
    if not reports:
        return pd.DataFrame()
    
    # Extract common metrics
    metrics = list(reports[0].metrics.keys())
    
    data = {'Metric': metrics}
    for report in reports:
        col_name = report.scenario_name
        values = []
        for metric in metrics:
            if metric in report.metrics:
                val = report.metrics[metric]
                values.append(f"{val['scenario']:.2f}{val['unit']} ({val['delta_pct']:+.1f}%)")
            else:
                values.append('—')
        data[col_name] = values
    
    return pd.DataFrame(data)


def generate_narrative(scenario_name: str, metrics: Dict[str, Any]) -> str:
    """
    Generate narrative text for a scenario
    
    Template-based generation for quick insights
    """
    narrative = f"### {scenario_name} Scenario\n\n"
    
    # Extract key metrics
    cai_change = metrics.get('cai_change_pct', 0)
    ecl_change = metrics.get('ecl_change_pct', 0)
    cet1_change = metrics.get('cet1_change_pp', 0)
    
    # Severity assessment
    if abs(ecl_change) > 50:
        severity = "Severe"
    elif abs(ecl_change) > 25:
        severity = "Moderate"
    else:
        severity = "Mild"
    
    narrative += f"**Severity:** {severity} ({ecl_change:+.1f}% ECL impact)\n\n"
    
    # Key drivers
    narrative += "**Key Drivers:**\n"
    if 'rate_shock' in metrics and metrics['rate_shock'] != 0:
        narrative += f"- Interest rates: {metrics['rate_shock']:+.0f}bps\n"
    if 'unemployment_shock' in metrics and metrics['unemployment_shock'] != 0:
        narrative += f"- Unemployment: {metrics['unemployment_shock']:+.1f}pp\n"
    if 'housing_shock' in metrics and metrics['housing_shock'] != 0:
        narrative += f"- Housing prices: {metrics['housing_shock']:+.1f}%\n"
    
    narrative += "\n**Impact Summary:**\n"
    narrative += f"- Credit availability falls {abs(cai_change):.1f}%\n"
    narrative += f"- Expected credit losses increase {abs(ecl_change):.1f}%\n"
    narrative += f"- Capital ratio compressed by {abs(cet1_change):.1f}pp\n"
    
    # Management actions
    narrative += "\n**Recommended Actions:**\n"
    if abs(ecl_change) > 40:
        narrative += "- Tighten underwriting standards (LVR/LTI limits)\n"
        narrative += "- Increase provisions proactively\n"
        narrative += "- Review and potentially reduce exposures to high-risk segments\n"
    elif abs(ecl_change) > 20:
        narrative += "- Monitor credit metrics closely\n"
        narrative += "- Adjust pricing for risk\n"
        narrative += "- Maintain elevated provisions\n"
    else:
        narrative += "- Continue normal monitoring\n"
        narrative += "- No immediate action required\n"
    
    return narrative


def create_risk_report(portfolio, df_macro, scenarios, country="Australia"):
    """
    Generate a complete risk report with all scenarios
    
    Args:
        portfolio: Portfolio object
        df_macro: Macro DataFrame
        scenarios: List of scenario objects
        country: Country name for report title
    
    Returns:
        Dict with 'summary', 'tables', 'narratives'
    """
    # Calculate baseline metrics
    portfolio.calculate_ecl()
    portfolio.calculate_rwa()
    capital = portfolio.calculate_capital()
    
    baseline_metrics = {
        'ecl': portfolio.exposures['ecl_12m'].sum(),
        'rwa': portfolio.exposures['rwa'].sum(),
        'cet1': 11.2,  # Example
        'cai': 0.83  # Example
    }
    
    # Generate reports for each scenario
    reports = []
    for scenario in scenarios:
        report = generate_scenario_insights(portfolio, df_macro, scenario, baseline_metrics)
        reports.append(report)
    
    # Create comparison table
    comparison_table = format_comparison_table(reports)
    
    # Generate summary
    summary = f"# {country} Credit Risk Scenario Analysis\n\n"
    summary += f"**Portfolio:** ${portfolio.exposures['total_ead'].sum()/1e9:.1f}B EAD, "
    summary += f"${baseline_metrics['ecl']/1e9:.2f}B ECL, "
    summary += f"${baseline_metrics['rwa']/1e9:.1f}B RWA\n\n"
    summary += f"**Baseline CET1:** {baseline_metrics['cet1']:.1f}%\n\n"
    
    summary += "## Scenario Comparison\n\n"
    summary += comparison_table.to_markdown(index=False)
    summary += "\n\n"
    
    # Add individual scenario summaries
    for report in reports:
        summary += report.generate_summary()
        summary += "\n---\n\n"
    
    return {
        'summary': summary,
        'reports': reports,
        'comparison_table': comparison_table,
        'baseline_metrics': baseline_metrics
    }


if __name__ == "__main__":
    print("Scenario Insights Module Loaded")
    print("="*60)
    print("Available functions:")
    print("- ScenarioReport: Class for structured scenario reports")
    print("- generate_scenario_insights: Generate insights from model outputs")
    print("- format_comparison_table: Compare multiple scenarios")
    print("- generate_narrative: Template-based narrative generation")
    print("- create_risk_report: Complete risk report generation")


