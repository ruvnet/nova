from typing import Dict, Any, Optional
import asyncio
import yaml
from datetime import datetime, timezone
import os
from pathlib import Path

from .agents.data_agent import DataAgent
from .agents.analysis_agent import AnalysisAgent
from .agents.trading_agent import TradingAgent
from .agents.reporting_agent import ReportingAgent

class InsiderMirrorCrew:
    """
    Orchestrates the insider trading mirror system agents using ReACT methodology.
    Coordinates data fetching, analysis, trading, and reporting.
    """
    def __init__(self):
        # Load configurations
        self.agents_config = self._load_config("src/insider_mirror/config/agents.yaml")
        self.tasks_config = self._load_config("src/insider_mirror/config/tasks.yaml")
        
        # Initialize agents
        self.data_agent = DataAgent(self.agents_config["data_agent"])
        self.analysis_agent = AnalysisAgent(self.agents_config["analysis_agent"])
        self.trading_agent = TradingAgent(self.agents_config["trading_agent"])
        self.reporting_agent = ReportingAgent(self.agents_config["reporting_agent"])
        
        # Initialize state
        self.portfolio_value = float(os.getenv("INITIAL_PORTFOLIO_VALUE", "100000"))
        self.is_running = False

    def _load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading configuration from {path}: {str(e)}")

    async def run_cycle(self) -> Dict[str, Any]:
        """
        Run a complete cycle of the insider trading mirror system
        
        Returns:
            Dictionary containing cycle results
        """
        try:
            # Step 1: Fetch Data
            data_result = await self.data_agent.execute(
                api_key=os.getenv("FINNHUB_API_KEY"),
                endpoint=os.getenv("FINNHUB_ENDPOINT")
            )
            
            if data_result["status"] != "success":
                raise RuntimeError(f"Data fetch failed: {data_result.get('error')}")
            
            # Step 2: Analyze Trades
            analysis_result = await self.analysis_agent.execute(
                trades=data_result["data"]
            )
            
            if analysis_result["status"] != "success":
                raise RuntimeError(f"Analysis failed: {analysis_result.get('error')}")
            
            # Step 3: Execute Trades
            if analysis_result["filtered_trades"]:
                trading_result = await self.trading_agent.execute(
                    trades=analysis_result["filtered_trades"],
                    portfolio_value=self.portfolio_value
                )
                
                if trading_result["status"] != "success":
                    raise RuntimeError(f"Trading failed: {trading_result.get('error')}")
                
                # Update portfolio value
                self.portfolio_value = trading_result["portfolio"]["total_value"]
            else:
                trading_result = {
                    "status": "success",
                    "executions": [],
                    "portfolio": self.trading_agent.get_portfolio_summary()
                }
            
            # Step 4: Generate Reports
            reporting_result = await self.reporting_agent.execute(
                trades=trading_result["executions"],
                portfolio_summary=trading_result["portfolio"]
            )
            
            if reporting_result["status"] != "success":
                raise RuntimeError(f"Reporting failed: {reporting_result.get('error')}")
            
            return {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "data": {
                    "trades_fetched": len(data_result["data"]),
                    "trades_analyzed": len(analysis_result["filtered_trades"]),
                    "trades_executed": len(trading_result["executions"]),
                    "portfolio_value": self.portfolio_value,
                    "reports": reporting_result["reports"]
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "error": str(e)
            }

    async def start(self, interval_seconds: int = 3600) -> None:
        """
        Start the insider trading mirror system
        
        Args:
            interval_seconds: Seconds between cycles
        """
        self.is_running = True
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 INSIDER TRADING MIRROR SYSTEM v1.0                           ║
║     INITIALIZING ALL SUBSYSTEMS...                               ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
📡 DATA FEED: ACTIVE
🧮 ANALYSIS ENGINE: ONLINE
💹 TRADING SYSTEM: READY
📊 REPORTING MODULE: INITIALIZED
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

[SYS]: Starting main operation loop...
""")
        
        try:
            while self.is_running:
                cycle_result = await self.run_cycle()
                
                if cycle_result["status"] == "success":
                    print(f"""
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cycle completed:
- Trades Fetched: {cycle_result['data']['trades_fetched']}
- Trades Analyzed: {cycle_result['data']['trades_analyzed']}
- Trades Executed: {cycle_result['data']['trades_executed']}
- Portfolio Value: ${cycle_result['data']['portfolio_value']:,.2f}
- Reports Generated: {', '.join(cycle_result['data']['reports'].keys())}
""")
                else:
                    print(f"""
[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Cycle failed:
Error: {cycle_result['error']}
""")
                
                # Reset daily tracking at market close
                if datetime.now().hour == 16:  # 4 PM
                    self.trading_agent.reset_daily_tracking()
                
                await asyncio.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            await self.stop()
        except Exception as e:
            print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️ SYSTEM ERROR DETECTED                                       ║
╚══════════════════════════════════════════════════════════════════╝
Error: {str(e)}
""")
            await self.stop()

    async def stop(self) -> None:
        """Stop the insider trading mirror system"""
        self.is_running = False
        
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🛑 SHUTTING DOWN INSIDER TRADING MIRROR SYSTEM                  ║
╚══════════════════════════════════════════════════════════════════╝
⚡ Stopping all agents...
💾 Saving system state...
🔌 Closing connections...
✨ Shutdown complete.
""")
        
        # Cleanup agents
        self.data_agent.cleanup()
        self.analysis_agent.cleanup()
        self.trading_agent.cleanup()
        self.reporting_agent.cleanup()

def main():
    """Entry point for the insider trading mirror system"""
    crew = InsiderMirrorCrew()
    
    try:
        # Get interval from environment or use default
        interval = int(os.getenv("UPDATE_INTERVAL_SECONDS", "3600"))
        asyncio.run(crew.start(interval))
    except KeyboardInterrupt:
        print("\nShutdown requested...")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
    finally:
        asyncio.run(crew.stop())

if __name__ == "__main__":
    main()