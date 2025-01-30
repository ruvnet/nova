"""Handler for demo agent commands."""

import logging
from typing import Dict, Any
from ...demos.echo_agent import EchoAgent
from ...demos.stock_agent import StockAgent
from ..formatters import OutputFormatter

class DemoCommandHandler:
    """Handler for demo commands"""
    
    def __init__(self):
        self.log = logging.getLogger("insider_mirror.cli.DemoCommandHandler")
        self.formatter = OutputFormatter()

    async def handle(self, args: Dict[str, Any]) -> None:
        """Handle demo commands"""
        if args["subcommand"] == "echo":
            await self._handle_echo(args)
        elif args["subcommand"] == "stock":
            await self._handle_stock(args)

    async def _handle_echo(self, args: Dict[str, Any]) -> None:
        """Handle echo demo command"""
        try:
            self.log.info(f"Running echo demo with message: {args['message']}")
            
            # Initialize echo agent
            agent = EchoAgent({
                "verbose": args.get("verbose", False),
                "react_validation": {
                    "thought_required": True,
                    "reasoning_depth": 1,
                    "action_validation": True
                }
            })
            
            result = await agent.execute(
                message=args["message"],
                style=args.get("style"),
                repeat=args.get("repeat", 1)
            )
            
            print(agent.format_output(result))
            
        except Exception as e:
            self.log.error(f"Error in echo demo: {str(e)}")
            print(self.formatter.format_error(str(e)))

    async def _handle_stock(self, args: Dict[str, Any]) -> None:
        """Handle stock demo command"""
        try:
            self.log.info(f"Running stock demo for {args['symbol']}")
            
            # Initialize stock agent
            agent = StockAgent({
                "verbose": args.get("verbose", False),
                "model": args.get("model"),  # Pass model from CLI args
                "react_validation": {
                    "thought_required": True,
                    "reasoning_depth": 1,
                    "action_validation": True
                }
            })
            
            result = await agent.execute(
                symbol=args["symbol"]
            )
            
            print(agent.format_output(result))
            
        except Exception as e:
            self.log.error(f"Error in stock demo: {str(e)}")
            print(self.formatter.format_error(str(e)))