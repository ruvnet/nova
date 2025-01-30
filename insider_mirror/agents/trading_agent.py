"""Trading agent for executing trades."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from .base_agent import BaseAgent

class TradingAgent(BaseAgent):
    """Agent responsible for trade execution"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "trading_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.risk_config = {
            "max_position_size": 0.05,  # 5% of portfolio
            "max_daily_trades": 10,
            "max_concentration": 0.20  # 20% per symbol
        }
        self.daily_trades = []
        self.positions = {}  # {symbol: {"shares": float, "value": float}}
        self.daily_pnl = 0.0  # Initialize daily P&L
        self.log = logging.getLogger(__name__)

    def check_risk_limits(
        self,
        trade: Dict[str, Any],
        portfolio_value: float
    ) -> tuple[bool, Optional[str]]:
        """Check if trade passes risk limits"""
        trade_value = trade["shares"] * trade["price"]
        
        # Daily trade limit check
        if len(self.daily_trades) >= self.risk_config["max_daily_trades"]:
            return False, "Daily trade limit reached"
            
        # Concentration check
        symbol = trade["symbol"]
        current_value = self.positions.get(symbol, {}).get("value", 0)
        new_value = current_value + trade_value
        concentration = new_value / portfolio_value
        
        if concentration > self.risk_config["max_concentration"]:
            return False, f"Symbol concentration {concentration:.2%} exceeds limit of {self.risk_config['max_concentration']:.2%}"
            
        # Position size check
        position_size = trade_value / portfolio_value
        if position_size > self.risk_config["max_position_size"]:
            return False, f"Position size {position_size:.2%} exceeds limit of {self.risk_config['max_position_size']:.2%}"
            
        return True, None

    def update_position(self, trade: Dict[str, Any]) -> None:
        """Update position tracking"""
        symbol = trade["symbol"]
        trade_value = trade["shares"] * trade["price"]
        
        if trade["transaction_type"] == "SALE":
            # For a sale, we need to match the shares with the current position
            current_position = self.positions.get(symbol, {"shares": 0, "value": 0})
            current_shares = current_position["shares"]
            
            if abs(current_shares - trade["shares"]) < 0.01:  # Full position sale
                del self.positions[symbol]
            else:
                new_shares = current_shares - trade["shares"]
                new_value = new_shares * trade["price"]
                self.positions[symbol] = {
                    "shares": new_shares,
                    "value": new_value
                }
        else:
            # For a purchase, simply add to position
            current_position = self.positions.get(symbol, {"shares": 0, "value": 0})
            new_shares = current_position["shares"] + trade["shares"]
            new_value = new_shares * trade["price"]
            self.positions[symbol] = {
                "shares": new_shares,
                "value": new_value
            }

    async def execute_trade(
        self,
        trade: Dict[str, Any],
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Execute a single trade"""
        self.track_progress(1, f"Processing trade for {trade['symbol']}")
        
        # Check risk limits
        passes_risk, risk_message = self.check_risk_limits(trade, portfolio_value)
        
        if not passes_risk:
            self.log.warning(f"Trade rejected for {trade['symbol']}: {risk_message}")
            return {
                "status": "rejected",
                "reason": risk_message,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        # Execute trade
        try:
            # Update position tracking
            self.update_position(trade)
            
            # Record trade
            trade_record = {
                **trade,
                "execution_time": datetime.now(timezone.utc).isoformat(),
                "portfolio_value": portfolio_value
            }
            self.daily_trades.append(trade_record)
            
            # Update daily P&L
            if trade["transaction_type"] == "SALE":
                self.daily_pnl += trade["shares"] * (trade["price"] - trade.get("avg_price", trade["price"]))
            
            return {
                "status": "executed",
                "trade": trade_record,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Trade execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def get_portfolio_summary(self) -> Dict[str, Any]:
        """Get current portfolio summary"""
        total_value = sum(pos["value"] for pos in self.positions.values())
        
        return {
            "total_value": total_value,
            "position_count": len(self.positions),
            "daily_trades": len(self.daily_trades),
            "daily_pnl": self.daily_pnl,
            "positions": {symbol: pos["value"] for symbol, pos in self.positions.items()}
        }

    async def execute(
        self,
        trades: List[Dict[str, Any]],
        portfolio_value: float
    ) -> Dict[str, Any]:
        """Execute trading tasks"""
        try:
            execution_results = []
            
            for trade in trades:
                # Step 1: Analyze Trade
                reasoning_step = {
                    "thought": f"Analyzing trade for {trade['symbol']}",
                    "parameters": {
                        "symbol": trade['symbol'],
                        "type": trade['transaction_type'],
                        "value": trade['shares'] * trade['price']
                    }
                }
                self.validate_reasoning(reasoning_step)
                
                # Step 2: Execute Trade
                action_step = {
                    "action": "execute_trade",
                    "parameters": {
                        "trade": trade,
                        "portfolio_value": portfolio_value
                    }
                }
                self.validate_action(action_step)
                
                result = await self.execute_trade(trade, portfolio_value)
                execution_results.append(result)
            
            # Step 3: Generate Summary
            reasoning_step = {
                "thought": "Generating execution summary",
                "parameters": {"trade_count": len(trades)}
            }
            self.validate_reasoning(reasoning_step)
            
            action_step = {
                "action": "get_portfolio_summary",
                "parameters": {}
            }
            self.validate_action(action_step)
            
            portfolio_summary = self.get_portfolio_summary()
            
            return {
                "status": "success",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "executions": execution_results,
                "portfolio": portfolio_summary
            }
            
        except Exception as e:
            self.log.error(f"Error executing trading agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def reset_daily_tracking(self) -> None:
        """Reset daily tracking data"""
        self.daily_trades = []
        self.daily_pnl = 0.0

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()
        self.reset_daily_tracking()
        self.positions = {}