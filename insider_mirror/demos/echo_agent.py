"""Demo agent that echoes input with formatting."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional

from ..agents.base_agent import BaseAgent
from ..cli.formatters import OutputFormatter

class EchoAgent(BaseAgent):
    """Simple agent that demonstrates basic message handling"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "echo_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.formatter = OutputFormatter()

    async def execute(
        self,
        message: str,
        style: Optional[str] = None,
        repeat: int = 1
    ) -> Dict[str, Any]:
        """Echo the input message with optional styling"""
        try:
            self.log.info(f"Processing message: {message}")
            self.track_progress(1, "Processing input message")
            
            # Apply style if specified
            if style == "uppercase":
                formatted_message = message.upper()
            elif style == "lowercase":
                formatted_message = message.lower()
            elif style == "title":
                formatted_message = message.title()
            else:
                formatted_message = message
            
            self.track_progress(2, f"Applied style: {style or 'none'}")
            
            # Repeat message if requested
            result = "\n".join([formatted_message] * repeat)
            self.track_progress(3, f"Generated output with {repeat} repetitions")
            
            return {
                "status": "success",
                "data": {
                    "original": message,
                    "formatted": result,
                    "style": style or "none",
                    "repeat": repeat
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Error in echo agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format echo result for display"""
        if result["status"] != "success":
            return self.formatter.format_error(result.get("error", "Unknown error"))
        
        data = result["data"]
        return f"""
{self.formatter.format_header(f"Echo Agent Demo - Style: {data['style']}")}

Original: {data['original']}
Formatted:
{data['formatted']}
"""

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()