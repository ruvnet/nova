"""Output formatters for the CLI."""

from typing import Dict, Any, List

class OutputFormatter:
    """Format CLI output with consistent styling"""
    
    @staticmethod
    def format_header(title: str, status: str = "INFO") -> str:
        """Format a header box"""
        status_icon = {
            "SUCCESS": "✅",
            "ERROR": "❌",
            "INFO": "ℹ️",
            "WARNING": "⚠️"
        }.get(status, "ℹ️")
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  {status_icon} {title.upper()}                     
╚══════════════════════════════════════════════════════════════════╝
"""

    @staticmethod
    def format_api_test_result(api_name: str, result: Dict[str, Any]) -> str:
        """Format API test results"""
        if result["status"] == "success":
            header = OutputFormatter.format_header(f"API TEST SUCCESSFUL - {api_name}", "SUCCESS")
            return f"""{header}
📊 Test Results:
➤ Status: {result['status']}
➤ Response Time: {result.get('response_time', 'N/A')}ms
➤ Rate Limit Remaining: {result.get('rate_limit_remaining', 'N/A')}
➤ Timestamp: {result['timestamp']}
"""
        else:
            header = OutputFormatter.format_header(f"API TEST FAILED - {api_name}", "ERROR")
            return f"""{header}
❗ Error Details:
➤ Status: {result['status']}
➤ Error: {result.get('error')}
➤ Timestamp: {result['timestamp']}
"""

    @staticmethod
    def format_trade_analysis(data_result: Dict[str, Any], analysis_result: Dict[str, Any]) -> str:
        """Format trade analysis results"""
        header = OutputFormatter.format_header("TRADE ANALYSIS RESULTS", "SUCCESS")
        return f"""{header}
📈 Analysis Summary:
➤ Input Trades: {len(data_result['data'])}
➤ Filtered Trades: {len(analysis_result['filtered_trades'])}
➤ Risk Metrics: {analysis_result.get('risk_metrics', {})}
"""

    @staticmethod
    def format_trading_results(result: Dict[str, Any]) -> str:
        """Format trading execution results"""
        header = OutputFormatter.format_header("TRADING RESULTS", "SUCCESS")
        return f"""{header}
💹 Execution Summary:
➤ Executions: {len(result['executions'])}
➤ Portfolio Value: ${result['portfolio']['total_value']:,.2f}
➤ Position Count: {result['portfolio']['position_count']}
"""

    @staticmethod
    def format_portfolio_status(portfolio: Dict[str, Any]) -> str:
        """Format portfolio status"""
        header = OutputFormatter.format_header("PORTFOLIO STATUS", "INFO")
        return f"""{header}
📊 Current Portfolio:
➤ Total Value: ${portfolio['total_value']:,.2f}
➤ Positions: {portfolio['position_count']}
➤ Daily Trades: {portfolio['daily_trades']}
➤ Daily P&L: ${portfolio['daily_pnl']:,.2f}
"""

    @staticmethod
    def format_report_generation(result: Dict[str, Any]) -> str:
        """Format report generation results"""
        header = OutputFormatter.format_header("REPORT GENERATION COMPLETE", "SUCCESS")
        return f"""{header}
📋 Report Summary:
➤ Generated Reports: {', '.join(result['reports'].keys())}
➤ Metrics Calculated: {len(result['metrics'])}
➤ Report Locations:
{chr(10).join(f'  • {format}: {path}' for format, path in result['reports'].items())}
"""

    @staticmethod
    def format_error(error: str) -> str:
        """Format error message"""
        header = OutputFormatter.format_header("ERROR", "ERROR")
        return f"""{header}
❗ Error Details:
➤ {error}
"""

    @staticmethod
    def format_progress(step: int, total: int, message: str) -> str:
        """Format progress message"""
        progress = "=" * (step * 20 // total)
        remaining = " " * (20 - len(progress))
        percentage = step * 100 // total
        
        return f"""
Progress: [{progress}{remaining}] {percentage}%
➤ {message}
"""