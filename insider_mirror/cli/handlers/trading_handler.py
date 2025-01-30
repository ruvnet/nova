"""Handler for trading commands."""

import os
import sys
import logging
from typing import Dict, Any
from ...crew import InsiderMirrorCrew
from ..formatters import OutputFormatter

class TradingCommandHandler:
    """Handler for trading commands"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli.TradingCommandHandler")

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle trading commands"""
        if args["subcommand"] == "execute":
            await self._handle_execute(args)
        elif args["subcommand"] == "status":
            await self._handle_status(args)

    async def _handle_execute(self, args: Dict[str, Any]) -> None:
        """Handle trade execution command"""
        # Get analyzed trades first
        data_result = await self.crew.data_agent.execute(
            api_key=os.environ.get("FINNHUB_API_KEY"),
            endpoint=os.environ.get("FINNHUB_ENDPOINT"),
            api_type="finnhub"
        )
        
        if data_result["status"] != "success":
            print(self.formatter.format_error(f"Error fetching data: {data_result.get('error')}"))
            sys.exit(1)
        
        analysis_result = await self.crew.analysis_agent.execute(
            trades=data_result["data"]
        )
        
        if analysis_result["status"] != "success":
            print(self.formatter.format_error(f"Error analyzing trades: {analysis_result.get('error')}"))
            sys.exit(1)
        
        # Execute trades
        if analysis_result["filtered_trades"]:
            portfolio_value = float(os.environ.get("INITIAL_PORTFOLIO_VALUE", "100000"))
            result = await self.crew.trading_agent.execute(
                trades=analysis_result["filtered_trades"],
                portfolio_value=portfolio_value
            )
            
            if result["status"] == "success":
                print(self.formatter.format_trading_results(result))
            else:
                print(self.formatter.format_error(result.get("error", "Unknown error")))
                sys.exit(1)
        else:
            print(self.formatter.format_header("No trades to execute", "INFO"))

    async def _handle_status(self, args: Dict[str, Any]) -> None:
        """Handle portfolio status command"""
        portfolio = self.crew.trading_agent.get_portfolio_summary()
        print(self.formatter.format_portfolio_status(portfolio))