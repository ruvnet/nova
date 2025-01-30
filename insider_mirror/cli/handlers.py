"""Command handlers for the CLI."""

import os
import sys
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from ..crew import InsiderMirrorCrew
from .formatters import OutputFormatter

class CommandHandler(ABC):
    """Base class for command handlers"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger(f"insider_mirror.cli.{self.__class__.__name__}")

    @abstractmethod
    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle command execution"""
        pass

    def _get_env_var(self, var_name: str, required: bool = True) -> Optional[str]:
        """Get environment variable with error handling"""
        value = os.environ.get(var_name)
        if required and not value:
            self.log.error(f"{var_name} not set in environment")
            print(self.formatter.format_error(f"{var_name} environment variable is required"))
            sys.exit(1)
        return value

class DataCommandHandler(CommandHandler):
    """Handler for data management commands"""
    
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
        
        print(self.formatter.format_api_test_result(args["api"].upper(), result))
        if result["status"] != "success":
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

class AnalysisCommandHandler(CommandHandler):
    """Handler for analysis commands"""
    
    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle analysis commands"""
        if args["subcommand"] == "trades":
            await self._handle_trades(args)
        elif args["subcommand"] == "risks":
            await self._handle_risks(args)

    async def _handle_trades(self, args: Dict[str, Any]) -> None:
        """Handle trade analysis command"""
        # Get data first
        api_key = self._get_env_var("FINNHUB_API_KEY")
        endpoint = self._get_env_var("FINNHUB_ENDPOINT")
        
        data_result = await self.crew.data_agent.execute(
            api_key=api_key,
            endpoint=endpoint,
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

class TradingCommandHandler(CommandHandler):
    """Handler for trading commands"""
    
    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle trading commands"""
        if args["subcommand"] == "execute":
            await self._handle_execute(args)
        elif args["subcommand"] == "status":
            await self._handle_status(args)

    async def _handle_execute(self, args: Dict[str, Any]) -> None:
        """Handle trade execution command"""
        # Get analyzed trades first
        api_key = self._get_env_var("FINNHUB_API_KEY")
        endpoint = self._get_env_var("FINNHUB_ENDPOINT")
        
        data_result = await self.crew.data_agent.execute(
            api_key=api_key,
            endpoint=endpoint,
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
            portfolio_value = float(self._get_env_var("INITIAL_PORTFOLIO_VALUE", False) or "100000")
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

class ReportingCommandHandler(CommandHandler):
    """Handler for reporting commands"""
    
    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle reporting commands"""
        if args["subcommand"] == "generate":
            await self._handle_generate(args)
        elif args["subcommand"] == "metrics":
            await self._handle_metrics(args)

    async def _handle_generate(self, args: Dict[str, Any]) -> None:
        """Handle report generation command"""
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

class SystemCommandHandler(CommandHandler):
    """Handler for system commands"""
    
    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle system commands"""
        if args["command"] == "run":
            await self._handle_run(args)

    async def _handle_run(self, args: Dict[str, Any]) -> None:
        """Handle system run command"""
        await self.crew.start(interval_seconds=args["interval"])