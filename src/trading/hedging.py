"""
Hedging Strategies Module
Generates sophisticated hedging recommendations for credit risk positions
Incorporates market microstructure, basis risk, and execution considerations
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class HedgingStrategy:
    """Container for a hedging strategy recommendation"""
    name: str
    instrument: str
    direction: str  # "Buy" or "Sell"
    notional: float
    rationale: str
    execution_approach: str
    liquidity_score: int  # 1-10, higher = more liquid
    basis_risk: str  # "Low", "Medium", "High"
    market_impact: str  # "Low", "Medium", "High"
    time_horizon: str  # "Immediate", "1-2 weeks", "1 month+"
    pros: List[str]
    cons: List[str]
    crush_avoidance_rating: int  # 1-10, higher = better at avoiding crush


class CDSHedgeAnalyzer:
    """
    Analyzes CDS positions and generates hedging recommendations
    Focuses on avoiding 'crush' scenarios where hedging moves the market
    """
    
    def __init__(self, position_size: float, entity: str, current_spread: float):
        """
        Args:
            position_size: Notional in millions
            entity: Reference entity name
            current_spread: Current CDS spread in bps
        """
        self.position_size = position_size
        self.entity = entity
        self.current_spread = current_spread
    
    def recommend_index_hedge(self) -> HedgingStrategy:
        """
        Recommend credit index hedge (CDX/iTraxx)
        The go-to strategy for large positions
        """
        # Determine appropriate index based on entity
        index = "CDX.NA.IG" if "US" in self.entity or "North America" in self.entity else "iTraxx Europe"
        
        # Beta adjustment for hedge ratio
        hedge_ratio = 0.85  # Typical single-name to index beta
        hedge_notional = self.position_size * hedge_ratio
        
        return HedgingStrategy(
            name="Credit Index Hedge",
            instrument=f"{index} Index CDS",
            direction="Sell Protection",
            notional=hedge_notional,
            rationale=(
                f"Sell {hedge_notional:.0f}M of {index} to hedge {self.position_size:.0f}M "
                f"single-name long CDS exposure. Index markets are 10-20x more liquid than "
                f"single-name, allowing execution without crushing spreads."
            ),
            execution_approach=(
                "Execute via electronic platform (Bloomberg SEF, Tradeweb, MarketAxess) in "
                "single trade or 2-3 clips over one session. Market depth supports $500M+ "
                "without material spread movement (<0.5bp slip)."
            ),
            liquidity_score=9,
            basis_risk="Medium",
            market_impact="Low",
            time_horizon="Immediate",
            pros=[
                "Deepest liquidity in credit markets—execute $100M+ blocks instantly",
                "Index spread is average of 125 names; diversifies idiosyncratic risk",
                "Transparent pricing; tight bid-ask spreads (0.25-0.5bp)",
                "No single-name alpha signal leak—you're not revealing which name you own",
                "Can re-hedge dynamically as single-name spread moves"
            ],
            cons=[
                "Beta mismatch: index beta to single-name typically 0.7-0.9 (basis risk)",
                "Systemic events (market-wide spread moves) hedged, but not idiosyncratic",
                "Index rolls every 6 months—requires rebalancing to new series",
                "If your single-name is excluded from index (downgrade/default), hedge fails"
            ],
            crush_avoidance_rating=10
        )
    
    def recommend_bond_hedge(self, bond_available: bool = True) -> HedgingStrategy:
        """
        Recommend hedging via underlying corporate bond
        """
        if not bond_available:
            return None
        
        # Bond notional slightly higher due to recovery-adjusted equivalence
        # CDS protects $1 notional; bond pays (1 - Recovery) on default
        # Assume 40% recovery -> need $1.67 bond per $1 CDS
        bond_notional = self.position_size * 1.67
        
        return HedgingStrategy(
            name="Corporate Bond Hedge",
            instrument=f"{self.entity} Senior Unsecured Bond",
            direction="Buy",
            notional=bond_notional,
            rationale=(
                f"Buy {bond_notional:.0f}M of {self.entity} bonds to hedge {self.position_size:.0f}M "
                f"long CDS. If credit tightens (CDS loses value), bond price rises, offsetting loss. "
                f"Recovery adjustment: bond pays (1-R) on default vs. CDS par protection."
            ),
            execution_approach=(
                "Trade via dealer network (2-3 dealers for price competition) or electronic "
                "bond platforms (MarketAxess, Tradeweb). For $50M+, execute in 2-4 blocks "
                "over 1-2 days to avoid telegraphing large buy interest."
            ),
            liquidity_score=6,
            basis_risk="Low",
            market_impact="Medium",
            time_horizon="1-2 weeks",
            pros=[
                "Direct hedge—same reference entity, tight basis to CDS",
                "Bond market may be less transparent; dealers less likely to front-run",
                "Coupon income offsets CDS premium payment (carry positive)",
                "No counterparty risk on bond (vs. CDS counterparty credit risk)",
                "Regulatory capital treatment may be favorable (banking book asset)"
            ],
            cons=[
                "Less liquid than index CDS—harder to execute $100M+ without moving market",
                "Bid-ask spread wider (10-30bp vs. <1bp for index CDS)",
                "Basis risk: bond-CDS basis can widen/tighten independently of credit (technical factors)",
                "Recovery rate mismatch—need to calculate correct hedge ratio",
                "If bond trades special (repo squeeze), basis hedge breaks down"
            ],
            crush_avoidance_rating=7
        )
    
    def recommend_equity_hedge(self, equity_ticker: str) -> HedgingStrategy:
        """
        Recommend cross-asset hedge via equity (Merton model logic)
        """
        # Merton hedge ratio: ∂CDS/∂Equity ≈ -0.3 to -0.5 for IG names
        # Negative because equity up -> credit risk down -> CDS spread tightens
        equity_delta = -0.40
        equity_notional = self.position_size * abs(equity_delta)
        
        return HedgingStrategy(
            name="Equity Cross-Hedge",
            instrument=f"{equity_ticker} Common Stock",
            direction="Buy",
            notional=equity_notional,
            rationale=(
                f"Buy {equity_notional:.0f}M of {equity_ticker} equity to hedge {self.position_size:.0f}M "
                f"long CDS. Credit risk inversely correlated with equity (Merton model): "
                f"firm value up -> default risk down -> CDS tightens -> equity hedge gains offset CDS loss."
            ),
            execution_approach=(
                "Execute via VWAP algo over 1-2 days (target 10-15% ADV to minimize market impact). "
                "Use dark pools and smart order routing to avoid information leakage. "
                "Alternatively, use equity options (buy calls) for levered exposure."
            ),
            liquidity_score=10,
            basis_risk="High",
            market_impact="Low",
            time_horizon="1-2 weeks",
            pros=[
                "ZERO credit market impact—executed in completely separate market (equity exchange)",
                "Highest liquidity—can trade $100M+ in most large-cap names without issue",
                "No signal leak to credit traders; maintains confidentiality of CDS position",
                "Can use options for capital efficiency (buy ATM calls = synthetic long)",
                "Dynamic delta—equity responds faster than bonds/CDS to news"
            ],
            cons=[
                "High basis risk—correlation not perfect; equity driven by growth, CDS by credit",
                "Equity volatility >> credit volatility; requires frequent rebalancing",
                "Idiosyncratic factors: equity can fall while credit improves (e.g., margin compression)",
                "Merton hedge ratio unstable—changes with leverage, volatility, equity price",
                "Regulatory capital: equity held in trading book (higher RWA than bonds)"
            ],
            crush_avoidance_rating=10
        )
    
    def recommend_patient_closeout(self) -> HedgingStrategy:
        """
        Recommend gradual unwinding of CDS position
        """
        daily_notional = self.position_size / 10  # Spread over 10 days
        
        return HedgingStrategy(
            name="Gradual Unwind (Patient Approach)",
            instrument=f"{self.entity} CDS",
            direction="Sell Protection",
            notional=daily_notional,
            rationale=(
                f"Close {self.position_size:.0f}M long CDS position by selling protection in "
                f"{daily_notional:.0f}M clips over 10 trading days. Small trade sizes avoid "
                f"triggering spread tightening; use multiple dealers and platforms for stealth."
            ),
            execution_approach=(
                "Day 1-3: Trade 3x clips via Dealer A (D2D voice). "
                "Day 4-6: Trade 3x clips via Bloomberg SEF (anonymous). "
                "Day 7-9: Trade 3x clips via Dealer B (different time zones). "
                "Day 10: Final clip via Tradeweb. "
                "Keep each trade <15% of estimated daily volume. Use limit orders near mid."
            ),
            liquidity_score=4,
            basis_risk="None",
            market_impact="Low",
            time_horizon="2-3 weeks",
            pros=[
                "Perfect hedge—same instrument, zero basis risk",
                "Small clips reduce market impact; spreads stay stable",
                "Dealer rotation and platform diversification prevent information aggregation",
                "Flexibility to pause if spreads move against you; wait for better levels",
                "Can use algo tools (VWAP-style for CDS) if available on electronic platforms"
            ],
            cons=[
                "Time risk: position remains open for 2-3 weeks; market can move against you",
                "Execution risk: need consistent liquidity; illiquid names can't support daily clips",
                "Transaction costs: 10 trades = 10x bid-ask spread drag (vs. 1 block trade)",
                "Operational complexity: managing multiple dealers, platforms, settlement",
                "If market learns you're unwinding (dealer gossip), spread can still tighten"
            ],
            crush_avoidance_rating=8
        )
    
    def recommend_options_hedge(self) -> HedgingStrategy:
        """
        Recommend using CDS options (swaptions) for hedging
        """
        strike = self.current_spread * 0.90  # 10% OTM put
        notional = self.position_size
        
        return HedgingStrategy(
            name="CDS Put Swaption",
            instrument=f"{self.entity} CDS Payer Swaption (Strike {strike:.0f}bp)",
            direction="Sell",
            notional=notional,
            rationale=(
                f"Sell {notional:.0f}M of CDS payer swaptions (strike {strike:.0f}bp, "
                f"current spread {self.current_spread:.0f}bp) to monetize spread tightening risk. "
                f"If spreads tighten below strike, swaption expires OTM (you keep premium). "
                f"Acts as insurance premium collection."
            ),
            execution_approach=(
                "Trade OTC with 2-3 dealers; request competitive quotes. "
                "Typical premium: 10-30bp upfront for 6M-1Y tenor. "
                "Consider exotic structures (knock-in, barrier) to reduce premium."
            ),
            liquidity_score=3,
            basis_risk="Low",
            market_impact="Low",
            time_horizon="Immediate",
            pros=[
                "Premium income offsets potential CDS mark-to-market loss",
                "Non-linear payoff: capped downside if spreads tighten dramatically",
                "OTC structure allows customization (strike, tenor, notional)",
                "Smaller notional traded vs. outright CDS hedge (less market impact)"
            ],
            cons=[
                "Illiquid market—only available for large, liquid reference entities",
                "Wide bid-ask on premium (5-10bp spread); difficult to price",
                "Upfront cost: premium paid reduces P&L if spreads don't tighten",
                "Counterparty risk: need ISDA and CSA with dealers",
                "Complex Greeks: vega, theta require active management"
            ],
            crush_avoidance_rating=9
        )


class CrossAssetHedger:
    """
    Generates cross-asset hedging strategies based on correlation regimes
    """
    
    def __init__(self, credit_exposure: float, macro_scenario: Dict[str, float]):
        self.credit_exposure = credit_exposure
        self.macro_scenario = macro_scenario
    
    def recommend_rates_hedge(self) -> HedgingStrategy:
        """
        Hedge credit risk via rates (duration hedge)
        """
        dv01_credit = self.credit_exposure * 0.05  # Assume 5yr duration
        rates_notional = dv01_credit * 100  # Convert to notional
        
        return HedgingStrategy(
            name="Interest Rate Hedge (Duration Overlay)",
            instrument="5Y Treasury Futures (ZF) or IRS",
            direction="Receive Fixed",
            notional=rates_notional,
            rationale=(
                f"Credit spreads and risk-free rates negatively correlated during risk-off. "
                f"If credit deteriorates (spreads widen, our shorts profit), rates fall "
                f"(duration gains offset). Hedge ratio based on historical beta_credit_rates ~= -0.3."
            ),
            execution_approach=(
                "Execute 5Y IRS receive-fixed (pay floating) via cleared swap (LCH, CME). "
                "Highly liquid: $1B+ trades daily. Alternatively use Treasury futures "
                "(ZF contract, $100k DV01 per contract)."
            ),
            liquidity_score=10,
            basis_risk="Medium",
            market_impact="Negligible",
            time_horizon="Immediate",
            pros=[
                "Deepest market in the world—zero execution risk",
                "Hedges systematic risk-off scenarios (flight to quality)",
                "Central clearing reduces counterparty risk",
                "Can dynamically adjust duration as portfolio changes"
            ],
            cons=[
                "Basis risk: correlation breaks down in credit-specific events",
                "Negative carry in upward-sloping yield curve (pay floating > receive fixed)",
                "Requires constant rebalancing as rates move",
                "Doesn't hedge idiosyncratic credit risk"
            ],
            crush_avoidance_rating=10
        )
    
    def recommend_fx_hedge(self, foreign_exposure: bool = True) -> HedgingStrategy:
        """
        Hedge FX risk embedded in credit positions
        """
        if not foreign_exposure:
            return None
        
        fx_notional = self.credit_exposure * 0.5  # Assume 50% is FX-sensitive
        
        return HedgingStrategy(
            name="FX Hedge (Currency Overlay)",
            instrument="USD/AUD or USD/EUR FX Forward",
            direction="Sell Foreign Currency",
            notional=fx_notional,
            rationale=(
                f"Credit denominated in foreign currency creates FX exposure. "
                f"If foreign currency strengthens, credit losses amplified in USD terms. "
                f"Hedge via FX forwards or cross-currency swaps."
            ),
            execution_approach=(
                "Execute FX forward (3M, 6M, 1Y tenor) via EBS, Reuters, or voice broker. "
                "For larger notionals ($50M+), use cross-currency basis swap to also hedge funding."
            ),
            liquidity_score=9,
            basis_risk="Low",
            market_impact="Negligible",
            time_horizon="Immediate",
            pros=[
                "Eliminates FX translation risk on credit portfolio",
                "Highly liquid FX market—instant execution",
                "Can lock in forward points (carry trade if positive)",
                "Transparent pricing; tight spreads (1-3 pips for majors)"
            ],
            cons=[
                "Introduces funding basis risk if using cross-currency swaps",
                "Forward roll costs if holding long-term",
                "Doesn't address underlying credit risk—pure FX hedge",
                "Requires mark-to-market management as FX moves"
            ],
            crush_avoidance_rating=10
        )


def generate_hedging_recommendations(
    position: Dict[str, Any],
    scenario: str,
    market_conditions: Dict[str, float]
) -> List[HedgingStrategy]:
    """
    Generate comprehensive hedging recommendations based on position and scenario
    
    Args:
        position: Dict with 'type', 'notional', 'entity', 'spread', etc.
        scenario: Scenario name (e.g., "Tightening", "Soft Landing")
        market_conditions: Dict with 'liquidity_score', 'volatility', etc.
    
    Returns:
        List of HedgingStrategy objects, ranked by appropriateness
    """
    recommendations = []
    
    if position['type'] == 'long_cds':
        analyzer = CDSHedgeAnalyzer(
            position_size=position['notional'],
            entity=position['entity'],
            current_spread=position['spread']
        )
        
        # Always recommend index hedge (most appropriate)
        recommendations.append(analyzer.recommend_index_hedge())
        
        # Add bond hedge if entity has tradable bonds
        if position.get('bond_available', True):
            bond_hedge = analyzer.recommend_bond_hedge(bond_available=True)
            if bond_hedge:
                recommendations.append(bond_hedge)
        
        # Add equity hedge if entity is public
        if position.get('equity_ticker'):
            recommendations.append(analyzer.recommend_equity_hedge(position['equity_ticker']))
        
        # Add patient closeout
        recommendations.append(analyzer.recommend_patient_closeout())
        
        # Add options if available
        if market_conditions.get('options_market', False):
            recommendations.append(analyzer.recommend_options_hedge())
    
    # Cross-asset hedges
    cross_hedger = CrossAssetHedger(
        credit_exposure=position['notional'],
        macro_scenario=market_conditions
    )
    
    recommendations.append(cross_hedger.recommend_rates_hedge())
    
    if position.get('foreign_currency', False):
        fx_hedge = cross_hedger.recommend_fx_hedge(foreign_exposure=True)
        if fx_hedge:
            recommendations.append(fx_hedge)
    
    # Rank by appropriateness (liquidity + crush avoidance)
    recommendations.sort(
        key=lambda x: (x.liquidity_score + x.crush_avoidance_rating) / 2,
        reverse=True
    )
    
    return recommendations


def calculate_hedge_ratio(position_spread: float, hedge_spread: float, correlation: float = 0.85) -> float:
    """
    Calculate optimal hedge ratio for spread risk
    
    Hedge Ratio = (σ_position / σ_hedge) × ρ × (DV01_position / DV01_hedge)
    
    Simplified for CDS: HR ≈ correlation × spread_ratio
    """
    spread_ratio = position_spread / hedge_spread if hedge_spread > 0 else 1.0
    hedge_ratio = correlation * spread_ratio
    
    return np.clip(hedge_ratio, 0.5, 1.5)  # Reasonable bounds


def estimate_basis_risk(hedge_type: str, scenario: str) -> Dict[str, float]:
    """
    Estimate basis risk for different hedge types
    
    Returns:
        Dict with 'expected_tracking_error', 'worst_case_loss', 'r_squared'
    """
    basis_risk_matrix = {
        'index_cds': {
            'Tightening': {'tracking_error': 0.15, 'worst_case': 0.25, 'r_squared': 0.75},
            'Soft Landing': {'tracking_error': 0.10, 'worst_case': 0.18, 'r_squared': 0.82},
            'Funding Shock': {'tracking_error': 0.20, 'worst_case': 0.35, 'r_squared': 0.65}
        },
        'corporate_bond': {
            'Tightening': {'tracking_error': 0.08, 'worst_case': 0.15, 'r_squared': 0.90},
            'Soft Landing': {'tracking_error': 0.05, 'worst_case': 0.10, 'r_squared': 0.93},
            'Funding Shock': {'tracking_error': 0.25, 'worst_case': 0.45, 'r_squared': 0.55}
        },
        'equity': {
            'Tightening': {'tracking_error': 0.35, 'worst_case': 0.60, 'r_squared': 0.45},
            'Soft Landing': {'tracking_error': 0.25, 'worst_case': 0.40, 'r_squared': 0.60},
            'Funding Shock': {'tracking_error': 0.50, 'worst_case': 0.80, 'r_squared': 0.30}
        }
    }
    
    return basis_risk_matrix.get(hedge_type, {}).get(scenario, {'tracking_error': 0.20, 'worst_case': 0.40, 'r_squared': 0.70})


if __name__ == "__main__":
    print("="*80)
    print("HEDGING STRATEGIES MODULE - EXAMPLE")
    print("="*80)
    
    # Example: Bank is long $100M CDS on XYZ Corp
    position = {
        'type': 'long_cds',
        'notional': 100,  # $100M
        'entity': 'XYZ Corp (US)',
        'spread': 150,  # 150 bps
        'bond_available': True,
        'equity_ticker': 'XYZ',
        'foreign_currency': False
    }
    
    market_conditions = {
        'liquidity_score': 7,
        'volatility': 0.25,
        'options_market': True
    }
    
    recommendations = generate_hedging_recommendations(position, "Tightening", market_conditions)
    
    print(f"\nPosition: Long ${position['notional']}M CDS on {position['entity']} @ {position['spread']}bp")
    print(f"Scenario: Tightening (spreads expected to tighten -> CDS loses value)")
    print(f"\n{'='*80}")
    print("HEDGING RECOMMENDATIONS (Ranked by Appropriateness)")
    print(f"{'='*80}\n")
    
    for i, strategy in enumerate(recommendations, 1):
        print(f"{i}. {strategy.name}")
        print(f"   Instrument: {strategy.instrument}")
        print(f"   Direction: {strategy.direction} | Notional: ${strategy.notional:.0f}M")
        print(f"   Liquidity: {strategy.liquidity_score}/10 | Crush Avoidance: {strategy.crush_avoidance_rating}/10")
        print(f"   Basis Risk: {strategy.basis_risk} | Market Impact: {strategy.market_impact}")
        print(f"\n   Rationale: {strategy.rationale}")
        print(f"\n   Execution: {strategy.execution_approach}")
        print(f"\n   Pros: {', '.join(strategy.pros[:2])}")
        print(f"   Cons: {', '.join(strategy.cons[:2])}")
        print(f"\n{'-'*80}\n")

