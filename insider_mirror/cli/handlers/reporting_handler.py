"""Handler for reporting commands."""

import sys
import logging
from typing import Dict, Any
from ...crew import InsiderMirrorCrew
from ..formatters import OutputFormatter

class ReportingCommandHandler:
    """Handler for reporting commands"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli.ReportingCommandHandler")

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle reporting commands"""
        if args["subcommand"] == "generate":
            await self._handle_generate(args)
        elif args["subcommand"] == "metrics":
            await self._handle_metrics(args)

    async def _handle_generate(self, args: Dict[str, Any]) -> None:
        """Handle report generation command"""
        # Get trading results first
        portfolio = self.crew.trading_agent.get_portfolio_summary()
        
        result = await self.crew.reporting_agent.execute(
            trades=self.crew.trading_agent.daily_trades,
            portfolio_summary=portfolio
        )
        
        if result["status"] == "success":
            print(self.formatter.format_report_generation(result))
        else:
            print(self.formatter.format_error(result.get("error", "Unknown error")))
            sys.exit(1)

    async def _handle_metrics(self, args: Dict[str, Any]) -> None:
        """Handle metrics display command"""
        portfolio = self.crew.trading_agent.get_portfolio_summary()
        print(self.formatter.format_portfolio_status(portfolio))