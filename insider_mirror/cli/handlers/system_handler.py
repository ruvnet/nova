"""Handler for system commands."""

import logging
from typing import Dict, Any
from ...crew import InsiderMirrorCrew
from ..formatters import OutputFormatter

class SystemCommandHandler:
    """Handler for system commands"""
    
    def __init__(self, crew: InsiderMirrorCrew):
        self.crew = crew
        self.formatter = OutputFormatter()
        self.log = logging.getLogger("insider_mirror.cli.SystemCommandHandler")

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle system commands"""
        if args["command"] == "run":
            await self._handle_run(args)

    async def _handle_run(self, args: Dict[str, Any]) -> None:
        """Handle system run command"""
        try:
            print(self.formatter.format_header("Starting Insider Trading Mirror System", "INFO"))
            await self.crew.start(interval_seconds=args["interval"])
            
        except KeyboardInterrupt:
            print("\nShutdown requested...")
            await self.crew.stop()
            
        except Exception as e:
            print(self.formatter.format_error(f"Fatal error: {str(e)}"))
            await self.crew.stop()