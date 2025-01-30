"""Command-line argument parser for the CLI."""

import argparse
from typing import Dict, Any, Optional

class ArgumentParser:
    """Parser for CLI arguments"""
    
    DEFAULT_MODEL = "anthropic/claude-3-opus-20240229"
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure argument parser"""
        parser = argparse.ArgumentParser(
            description="Insider Trading Mirror System CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Test API connectivity
  insider-mirror data test --api finnhub --verbose
  
  # Run echo demo
  insider-mirror demo echo --message "Hello World" --style uppercase --repeat 2
  
  # Run weather demo
  insider-mirror demo weather --city "London" --country "UK" --model "anthropic/claude-3-sonnet-20240229"
  
  # Run stock demo
  insider-mirror demo stock --symbol AAPL --model "anthropic/claude-3-opus-20240229"
  
  # Run news demo
  insider-mirror demo news --symbol GOOGL --days 7 --model "anthropic/claude-3-opus-20240229"
            """
        )
        
        subparsers = parser.add_subparsers(dest="command", metavar="COMMAND")
        
        # Add subcommands
        ArgumentParser._add_data_commands(subparsers)
        ArgumentParser._add_analysis_commands(subparsers)
        ArgumentParser._add_trading_commands(subparsers)
        ArgumentParser._add_reporting_commands(subparsers)
        ArgumentParser._add_system_commands(subparsers)
        ArgumentParser._add_demo_commands(subparsers)
        
        return parser

    @staticmethod
    def _add_verbose_flag(parser: argparse.ArgumentParser) -> None:
        """Add verbose flag to a parser"""
        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Enable verbose logging"
        )

    @staticmethod
    def _add_model_option(parser: argparse.ArgumentParser) -> None:
        """Add model selection option"""
        parser.add_argument(
            "--model",
            default=ArgumentParser.DEFAULT_MODEL,
            help=f"OpenRouter model to use (default: {ArgumentParser.DEFAULT_MODEL})"
        )

    @staticmethod
    def _add_demo_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add demo commands"""
        demo_parser = subparsers.add_parser("demo", help="Demo commands")
        demo_subparsers = demo_parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        
        # demo echo
        echo_parser = demo_subparsers.add_parser("echo", help="Run echo demo")
        echo_parser.add_argument(
            "--message",
            required=True,
            help="Message to echo"
        )
        echo_parser.add_argument(
            "--style",
            choices=["uppercase", "lowercase", "title"],
            help="Text transformation style"
        )
        echo_parser.add_argument(
            "--repeat",
            type=int,
            default=1,
            help="Number of times to repeat the message"
        )
        ArgumentParser._add_verbose_flag(echo_parser)
        
        # demo weather
        weather_parser = demo_subparsers.add_parser("weather", help="Run weather demo")
        weather_parser.add_argument(
            "--city",
            required=True,
            help="City name"
        )
        weather_parser.add_argument(
            "--country",
            help="Country code (e.g., US, UK)"
        )
        ArgumentParser._add_model_option(weather_parser)
        ArgumentParser._add_verbose_flag(weather_parser)
        
        # demo stock
        stock_parser = demo_subparsers.add_parser("stock", help="Run stock demo")
        stock_parser.add_argument(
            "--symbol",
            required=True,
            help="Stock symbol"
        )
        stock_parser.add_argument(
            "--interval",
            choices=["1d", "1h"],
            default="1d",
            help="Data interval"
        )
        ArgumentParser._add_model_option(stock_parser)
        ArgumentParser._add_verbose_flag(stock_parser)
        
        # demo news
        news_parser = demo_subparsers.add_parser("news", help="Run news demo")
        news_parser.add_argument(
            "--symbol",
            required=True,
            help="Stock symbol"
        )
        news_parser.add_argument(
            "--days",
            type=int,
            default=7,
            help="Number of days of news"
        )
        ArgumentParser._add_model_option(news_parser)
        ArgumentParser._add_verbose_flag(news_parser)

    @staticmethod
    def _add_data_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add data management commands"""
        data_parser = subparsers.add_parser("data", help="Data management commands")
        data_subparsers = data_parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        
        # data test
        test_parser = data_subparsers.add_parser("test", help="Test API connectivity")
        test_parser.add_argument(
            "--api",
            choices=["finnhub"],  # Removed tradefeeds option
            required=True,
            help="API to test"
        )
        ArgumentParser._add_verbose_flag(test_parser)
        
        # data fetch
        fetch_parser = data_subparsers.add_parser("fetch", help="Fetch insider trading data")
        fetch_parser.add_argument("--limit", type=int, default=50, help="Max records to fetch")
        ArgumentParser._add_verbose_flag(fetch_parser)
        
        # data validate
        validate_parser = data_subparsers.add_parser("validate", help="Validate existing data")
        validate_parser.add_argument("--strict", action="store_true", help="Use strict validation")
        ArgumentParser._add_verbose_flag(validate_parser)

    @staticmethod
    def _add_analysis_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add analysis commands"""
        analysis_parser = subparsers.add_parser("analyze", help="Analysis commands")
        analysis_subparsers = analysis_parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        
        # analyze trades
        trades_parser = analysis_subparsers.add_parser("trades", help="Analyze trades")
        trades_parser.add_argument("--min-value", type=int, help="Minimum trade value")
        trades_parser.add_argument("--min-shares", type=int, help="Minimum shares")
        ArgumentParser._add_verbose_flag(trades_parser)
        
        # analyze risks
        risks_parser = analysis_subparsers.add_parser("risks", help="Analyze risks")
        risks_parser.add_argument("--symbol", help="Focus on specific symbol")
        ArgumentParser._add_verbose_flag(risks_parser)

    @staticmethod
    def _add_trading_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add trading commands"""
        trading_parser = subparsers.add_parser("trade", help="Trading commands")
        trading_subparsers = trading_parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        
        # trade execute
        execute_parser = trading_subparsers.add_parser("execute", help="Execute trades")
        execute_parser.add_argument(
            "--mode", 
            choices=["paper", "live"], 
            default="paper",
            help="Trading mode"
        )
        ArgumentParser._add_verbose_flag(execute_parser)
        
        # trade status
        status_parser = trading_subparsers.add_parser("status", help="Check trade status")
        ArgumentParser._add_verbose_flag(status_parser)

    @staticmethod
    def _add_reporting_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add reporting commands"""
        report_parser = subparsers.add_parser("report", help="Reporting commands")
        report_subparsers = report_parser.add_subparsers(dest="subcommand", metavar="SUBCOMMAND")
        
        # report generate
        generate_parser = report_subparsers.add_parser("generate", help="Generate reports")
        generate_parser.add_argument(
            "--format",
            choices=["html", "csv"],
            default="html",
            help="Report format"
        )
        ArgumentParser._add_verbose_flag(generate_parser)
        
        # report metrics
        metrics_parser = report_subparsers.add_parser("metrics", help="Show metrics")
        ArgumentParser._add_verbose_flag(metrics_parser)

    @staticmethod
    def _add_system_commands(subparsers: argparse._SubParsersAction) -> None:
        """Add system commands"""
        run_parser = subparsers.add_parser("run", help="Run the complete system")
        run_parser.add_argument(
            "--interval",
            type=int,
            default=3600,
            help="Update interval in seconds"
        )
        ArgumentParser._add_verbose_flag(run_parser)

    @staticmethod
    def parse_args() -> Dict[str, Any]:
        """Parse command line arguments"""
        parser = ArgumentParser.create_parser()
        args = parser.parse_args()
        return vars(args)  # Convert to dictionary