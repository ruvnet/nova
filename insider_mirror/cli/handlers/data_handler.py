"""Handler for data management commands."""

import os
import sys
import logging
from typing import Dict, Any
from ...crew import InsiderMirrorCrew
from ..formatters import OutputFormatter

class DataCommandHandler:
    """Handler for data commands"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli.DataCommandHandler")

    def _get_env_var(self, var_name: str, required: bool = True) -> str:
        """Get environment variable with error handling"""
        value = os.environ.get(var_name)
        if required and not value:
            self.log.error(f"{var_name} not set in environment")
            print(self.formatter.format_error(f"{var_name} environment variable is required"))
            sys.exit(1)
        return value

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle data commands"""
        if args["subcommand"] == "test":
            await self._handle_test(args)
        elif args["subcommand"] == "fetch":
            await self._handle_fetch(args)
        elif args["subcommand"] == "validate":
            await self._handle_validate(args)

    async def _handle_test(self, args: Dict[str, Any]) -> None:
        """Handle API test command"""
        self.log.info(f"Testing {args['api'].upper()} API connectivity...")
        
        if args["api"] == "finnhub":
            api_key = self._get_env_var("FINNHUB_API_KEY")
            endpoint = self._get_env_var("FINNHUB_ENDPOINT")
            result = await self.crew.data_agent.test_api(
                api_key=api_key,
                endpoint=endpoint,
                api_type="finnhub"
            )
        else:  # tradefeeds
            api_key = self._get_env_var("TRADEFEEDS_API_KEY")
            endpoint = self._get_env_var("TRADEFEEDS_ENDPOINT")
            result = await self.crew.data_agent.test_api(
                api_key=api_key,
                endpoint=endpoint,
                api_type="tradefeeds"
            )
        
        if result["status"] == "success":
            print(self.formatter.format_api_test_result(args["api"].upper(), result))
        else:
            print(self.formatter.format_error(result.get("error", "Unknown error")))
            sys.exit(1)

    async def _handle_fetch(self, args: Dict[str, Any]) -> None:
        """Handle data fetch command"""
        api_key = self._get_env_var("FINNHUB_API_KEY")
        endpoint = self._get_env_var("FINNHUB_ENDPOINT")
        
        result = await self.crew.data_agent.execute(
            api_key=api_key,
            endpoint=endpoint,
            api_type="finnhub"
        )
        
        if result["status"] == "success":
            print(self.formatter.format_header(f"Successfully fetched {len(result['data'])} records", "SUCCESS"))
        else:
            print(self.formatter.format_error(result.get("error", "Unknown error")))
            sys.exit(1)

    async def _handle_validate(self, args: Dict[str, Any]) -> None:
        """Handle data validation command"""
        # Implementation for validate command
        pass