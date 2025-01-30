"""Handler for analysis commands."""

import sys
import logging
from typing import Dict, Any
from ...crew import InsiderMirrorCrew
from ..formatters import OutputFormatter

class AnalysisCommandHandler:
    """Handler for analysis commands"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli.AnalysisCommandHandler")

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle analysis commands"""
        if args["subcommand"] == "trades":
            await self._handle_trades(args)
        elif args["subcommand"] == "risks":
            await self._handle_risks(args)

    async def _handle_trades(self, args: Dict[str, Any]) -> None:
        """Handle trade analysis command"""
        # Get data first
        data_result = await self.crew.data_agent.execute(
            api_key=os.environ.get("FINNHUB_API_KEY"),
            endpoint=os.environ.get("FINNHUB_ENDPOINT"),
            api_type="finnhub"
        )
        
        if data_result["status"] != "success":
            print(self.formatter.format_error(f"Error fetching data: {data_result.get('error')}"))
            sys.exit(1)
        
        # Analyze trades
        result = await self.crew.analysis_agent.execute(trades=data_result["data"])
        
        if result["status"] == "success":
            print(self.formatter.format_trade_analysis(data_result, result))
        else:
            print(self.formatter.format_error(result.get("error", "Unknown error")))
            sys.exit(1)

    async def _handle_risks(self, args: Dict[str, Any]) -> None:
        """Handle risk analysis command"""
        # Implementation for risks command
        pass