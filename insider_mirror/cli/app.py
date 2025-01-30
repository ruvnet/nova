"""Main CLI application class."""

import asyncio
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from ..crew import InsiderMirrorCrew
from .parser import ArgumentParser
from .handlers import (
    DataCommandHandler,
    AnalysisCommandHandler,
    TradingCommandHandler,
    ReportingCommandHandler,
    SystemCommandHandler,
    DemoCommandHandler
)
from .formatters import OutputFormatter

class InsiderMirrorCLI:
    """Command-line interface for the system"""
    
    def __init__(self):
        self._load_environment()
        self.crew = InsiderMirrorCrew()
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli")
        
        # Initialize command handlers
        self.handlers = {
            "data": DataCommandHandler(self.crew),
            "analyze": AnalysisCommandHandler(self.crew),
            "trade": TradingCommandHandler(self.crew),
            "report": ReportingCommandHandler(self.crew),
            "run": SystemCommandHandler(self.crew),
            "demo": DemoCommandHandler()  # Demo handler doesn't need crew
        }

    def _load_environment(self) -> None:
        """Load environment variables from .env file"""
        # Find the root directory (where .env file is located)
        root_dir = Path(__file__).resolve().parents[3]  # Go up 3 levels from cli/app.py
        env_path = root_dir / ".env"
        
        if env_path.exists():
            load_dotenv(env_path)
            logging.debug(f"Loaded environment from {env_path}")
        else:
            logging.warning(f"No .env file found at {env_path}")

    def execute(self) -> None:
        """Execute CLI command"""
        try:
            # Parse arguments
            args = ArgumentParser.parse_args()
            
            # Configure logging
            if args.get("verbose", False):
                logging.getLogger().setLevel(logging.DEBUG)
                self.log.debug("Verbose logging enabled")
            
            # Show help if no command provided
            if not args.get("command"):
                ArgumentParser.create_parser().print_help()
                return
            
            # Execute command
            try:
                handler = self.handlers.get(args["command"])
                if handler:
                    asyncio.run(handler.handle(args))
                else:
                    self.log.error(f"Unknown command: {args['command']}")
                    print(self.formatter.format_error(f"Unknown command: {args['command']}"))
                    
            except KeyboardInterrupt:
                print("\nOperation cancelled by user")
                return
            except Exception as e:
                self.log.error(f"Error executing command: {str(e)}")
                print(self.formatter.format_error(str(e)))
                
        except SystemExit as e:
            # Re-raise SystemExit with code 1 for errors
            if e.code != 0:
                raise SystemExit(1)
            raise