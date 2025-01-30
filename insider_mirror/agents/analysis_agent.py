"""Analysis agent for analyzing insider trading patterns."""

import logging
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent

class AnalysisAgent(BaseAgent):
    """Agent responsible for analyzing trading patterns"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "analysis_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.analysis_config = self.load_config("src/insider_mirror/config/analysis.yaml")
        self.log = logging.getLogger(__name__)

    def convert_to_dataframe(self, trades: List[Dict[str, Any]]) -> pd.DataFrame:
        """Convert trades list to pandas DataFrame"""
        df = pd.DataFrame(trades)
        df['filing_date'] = pd.to_datetime(df['filing_date'])
        return df

    def filter_significant_trades(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter trades based on significance criteria"""
        self.track_progress(1, "Applying significance filters")
        
        if not trades:
            return []
            
        df = self.convert_to_dataframe(trades)
        
        # Apply filters from config
        filters = self.analysis_config.get("filters", {})
        min_value = filters.get("min_value", 100000)
        min_shares = filters.get("min_shares", 1000)
        
        # Filter significant trades
        significant = df[
            (df['value'] >= min_value) &
            (df['shares'] >= min_shares)
        ]
        
        filtered_trades = significant.to_dict('records')
        self.track_progress(2, f"Identified {len(filtered_trades)} significant trades")
        
        return filtered_trades

    def analyze_patterns(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading patterns"""
        self.track_progress(1, "Analyzing trading patterns")
        
        if not trades:
            return {}
            
        df = self.convert_to_dataframe(trades)
        
        # Time-based patterns
        time_patterns = {
            "daily_volume": df.groupby(df['filing_date'].dt.date)['value'].sum().to_dict(),
            "hourly_distribution": df.groupby(df['filing_date'].dt.hour)['value'].sum().to_dict()
        }
        
        # Symbol patterns
        symbol_patterns = {
            "symbol_frequency": df['symbol'].value_counts().to_dict(),
            "value_by_symbol": df.groupby('symbol')['value'].sum().to_dict()
        }
        
        return {
            "time_patterns": time_patterns,
            "symbol_patterns": symbol_patterns
        }

    def analyze_clusters(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trade clusters"""
        if not trades:
            return {}
            
        df = self.convert_to_dataframe(trades)
        
        # Time-based clustering
        time_clusters = df.groupby([
            df['filing_date'].dt.date,
            'symbol'
        ]).agg({
            'value': 'sum',
            'shares': 'sum'
        }).reset_index()
        
        return {
            "time_clusters": time_clusters.to_dict('records')
        }

    def analyze_trends(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze trading trends"""
        if not trades:
            return {}
            
        df = self.convert_to_dataframe(trades)
        
        # Calculate daily trends
        daily_trends = df.groupby(df['filing_date'].dt.date).agg({
            'value': 'sum',
            'shares': 'sum'
        })
        
        # Calculate moving averages
        window_sizes = [3, 7, 14]
        moving_averages = {
            f"{window}d_ma": daily_trends['value'].rolling(window=window).mean().to_dict()
            for window in window_sizes
        }
        
        return {
            "daily_trends": daily_trends.to_dict('records'),
            "moving_averages": moving_averages
        }

    def analyze_correlations(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze correlations between different metrics"""
        if not trades:
            return {}
            
        df = self.convert_to_dataframe(trades)
        
        # Calculate correlations
        numeric_cols = ['shares', 'price', 'value']
        correlations = df[numeric_cols].corr().to_dict()
        
        return {
            "metric_correlations": correlations
        }

    def calculate_risk_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate risk metrics"""
        self.track_progress(1, "Calculating risk metrics")
        
        if not trades:
            return {}
            
        df = self.convert_to_dataframe(trades)
        
        # Value at Risk (VaR)
        values = df['value'].values
        var_95 = np.percentile(values, 5)
        var_99 = np.percentile(values, 1)
        
        # Concentration risk
        total_value = df['value'].sum()
        symbol_concentration = (
            df.groupby('symbol')['value']
            .sum()
            .apply(lambda x: x / total_value)
            .to_dict()
        )
        
        return {
            "var_95": var_95,
            "var_99": var_99,
            "symbol_concentration": symbol_concentration
        }

    async def execute(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute analysis tasks"""
        try:
            # Step 1: Filter significant trades
            filtered_trades = self.filter_significant_trades(trades)
            
            if not filtered_trades:
                return {
                    "status": "success",
                    "message": "No significant trades found",
                    "filtered_trades": [],
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
            
            # Step 2: Analyze patterns
            self.track_progress(3, "Analyzing trading patterns")
            patterns = self.analyze_patterns(filtered_trades)
            
            # Step 3: Calculate risk metrics
            self.track_progress(4, "Calculating risk metrics")
            risk_metrics = self.calculate_risk_metrics(filtered_trades)
            
            return {
                "status": "success",
                "filtered_trades": filtered_trades,
                "patterns": patterns,
                "risk_metrics": risk_metrics,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Error executing analysis agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()