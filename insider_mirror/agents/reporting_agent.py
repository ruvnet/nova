"""Reporting agent for generating performance reports."""

import os
import logging
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional

from .base_agent import BaseAgent

class ReportingAgent(BaseAgent):
    """Agent responsible for generating performance reports"""
    
    def __init__(self, config: Dict[str, Any]):
        self.name = "reporting_agent"  # Set name before super().__init__
        super().__init__(self.name, config)
        self.reports_dir = Path("reports")
        self.reports_dir.mkdir(exist_ok=True)
        self.report_config = {
            "formats": ["html", "csv"],
            "metrics": ["win_rate", "profit_factor", "sharpe_ratio", "max_drawdown"]
        }
        self.log = logging.getLogger(__name__)

    def _calculate_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate performance metrics from trades"""
        if not trades:
            return {
                "win_rate": 0.0,
                "profit_factor": 0.0,
                "sharpe_ratio": 0.0,
                "max_drawdown": 0.0
            }
        
        df = pd.DataFrame(trades)
        daily_returns = df.groupby(pd.to_datetime(df['timestamp']).dt.date)['pnl'].sum()
        
        # Win rate
        winning_trades = len([t for t in trades if t['pnl'] > 0])
        win_rate = winning_trades / len(trades)
        
        # Profit factor
        gains = sum(t['pnl'] for t in trades if t['pnl'] > 0)
        losses = abs(sum(t['pnl'] for t in trades if t['pnl'] < 0))
        profit_factor = gains / losses if losses > 0 else float('inf')
        
        # Sharpe ratio (annualized, assuming 252 trading days)
        returns = daily_returns / daily_returns.shift(1) - 1
        sharpe_ratio = np.sqrt(252) * returns.mean() / returns.std() if len(returns) > 1 else 0
        
        # Maximum drawdown
        max_drawdown = abs(min(t['pnl'] for t in trades)) if trades else 0
        
        return {
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown
        }

    def _generate_html_report(self, data: Dict[str, Any]) -> str:
        """Generate HTML report"""
        trades_df = pd.DataFrame(data["trades"])
        metrics = data["metrics"]
        
        # Format metrics for display
        formatted_metrics = {
            "Win Rate": f"{metrics['win_rate']:.2%}",
            "Profit Factor": f"{metrics['profit_factor']:.2f}",
            "Sharpe Ratio": f"{metrics['sharpe_ratio']:.2f}",
            "Max Drawdown": f"${metrics['max_drawdown']:,.2f}"
        }
        
        # Generate HTML content
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Insider Trading Mirror Report - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f5f5f5;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 20px;
                    border-radius: 5px;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                }}
                h1, h2 {{
                    color: #333;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                th, td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #ddd;
                }}
                th {{
                    background-color: #f8f9fa;
                }}
                .metrics {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .metric-value {{
                    font-size: 24px;
                    font-weight: bold;
                    color: #007bff;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Insider Trading Mirror Report</h1>
                <p>Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                
                <h2>Performance Metrics</h2>
                <div class="metrics">
        """
        
        # Add metric cards
        for name, value in formatted_metrics.items():
            html_content += f"""
                    <div class="metric-card">
                        <div>{name}</div>
                        <div class="metric-value">{value}</div>
                    </div>
            """
        
        # Add trades table
        html_content += """
                </div>
                
                <h2>Recent Trades</h2>
        """
        html_content += trades_df.to_html(classes='table')
        
        # Close HTML
        html_content += """
            </div>
        </body>
        </html>
        """
        
        return html_content

    def _generate_csv_report(self, data: Dict[str, Any]) -> str:
        """Generate CSV report"""
        trades_df = pd.DataFrame(data["trades"])
        metrics_df = pd.DataFrame([data["metrics"]])
        
        # Combine trades and metrics
        report_df = pd.concat([
            pd.DataFrame([{"Report Type": "Metrics"}]),
            metrics_df,
            pd.DataFrame([{"Report Type": "Trades"}]),
            trades_df
        ])
        
        return report_df.to_csv(index=False)

    def save_report(self, content: str, format: str) -> str:
        """Save report to file"""
        timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
        filepath = self.reports_dir / f"report_{timestamp}.{format}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(filepath)

    async def execute(
        self,
        trades: List[Dict[str, Any]],
        portfolio_summary: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute reporting tasks"""
        try:
            self.track_progress(1, "Calculating metrics")
            metrics = self._calculate_metrics(trades)
            
            self.track_progress(2, "Generating reports")
            data = {
                "trades": trades,
                "metrics": metrics,
                "portfolio": portfolio_summary
            }
            
            reports = {}
            for format in self.report_config["formats"]:
                if format == "html":
                    content = self._generate_html_report(data)
                elif format == "csv":
                    content = self._generate_csv_report(data)
                else:
                    continue
                
                filepath = self.save_report(content, format)
                reports[format] = filepath
            
            self.track_progress(3, "Reports generated")
            
            return {
                "status": "success",
                "metrics": metrics,
                "reports": reports,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Error executing reporting agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()