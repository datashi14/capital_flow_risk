"""
Reporting Package
Scenario insights and narrative generation for risk reports
"""

from .insights import (
    ScenarioReport,
    generate_scenario_insights,
    format_comparison_table,
    generate_narrative
)

__all__ = [
    'ScenarioReport',
    'generate_scenario_insights',
    'format_comparison_table',
    'generate_narrative'
]


