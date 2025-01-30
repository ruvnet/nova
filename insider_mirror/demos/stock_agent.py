"""Demo agent that analyzes stock data using Finnhub and OpenRouter with ReACT methodology."""

import asyncio
import logging
import aiohttp
import json
import os
import ssl
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from ..agents.base_agent import BaseAgent
from ..cli.parser import ArgumentParser

# ANSI color codes for formatted output
CYAN = '\033[0;36m'
GREEN = '\033[0;32m'
NC = '\033[0m'  # No Color

class StockAgent(BaseAgent):
    """Agent that demonstrates market data analysis"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "stock_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.session = None
        self.model = agent_config.get("model", ArgumentParser.DEFAULT_MODEL)

    async def _init_session(self) -> None:
        """Initialize aiohttp session with SSL context"""
        if self.session is None or self.session.closed:
            # Configure SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = True
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            
            # Configure connection timeout
            timeout = aiohttp.ClientTimeout(total=30)
            
            # Create session with SSL context
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            self.session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )

    async def _close_session(self) -> None:
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Fetch stock data from Finnhub API"""
        try:
            await self._init_session()
            
            api_key = os.getenv("FINNHUB_API_KEY")
            if not api_key:
                raise ValueError("FINNHUB_API_KEY environment variable is required")
            
            headers = {
                "X-Finnhub-Token": api_key
            }
            
            # Fetch quote data
            self.log.info(f"Fetching quote data for {symbol}")
            async with self.session.get(
                f"https://finnhub.io/api/v1/quote?symbol={symbol}",
                headers=headers
            ) as response:
                if response.status == 200:
                    quote_data = await response.json()
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Quote API error: {error_text}")
            
            # Fetch company profile
            self.log.info(f"Fetching company profile for {symbol}")
            async with self.session.get(
                f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}",
                headers=headers
            ) as response:
                if response.status == 200:
                    profile_data = await response.json()
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"Profile API error: {error_text}")
            
            return {
                "quote": quote_data,
                "profile": profile_data
            }
            
        except Exception as e:
            self.log.error(f"Error fetching stock data: {str(e)}")
            raise
            
        finally:
            await self._close_session()

    async def _stream_openrouter_response(self, messages: List[Dict[str, str]]) -> str:
        """Stream responses from OpenRouter with ReACT methodology"""
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")
        
        await self._init_session()
        
        try:
            # Configure enterprise-grade connection parameters
            connector = aiohttp.TCPConnector(
                ssl=ssl.create_default_context(),
                limit=100,
                limit_per_host=20,
                use_dns_cache=True
            )
            
            async with aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=45)
            ) as session:
                async with session.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "http://localhost:3000",
                        "X-Title": "Insider Mirror System"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": True,
                        "temperature": 0.7
                    },
                    timeout=None
                ) as response:
                    full_response = ""
                    async for line in response.content:
                        if line:
                            try:
                                line_str = line.decode('utf-8')
                                if line_str.startswith('data: '):
                                    chunk_data = json.loads(line_str[6:])
                                    if chunk_data != '[DONE]':
                                        if 'choices' in chunk_data and len(chunk_data['choices']) > 0:
                                            delta = chunk_data['choices'][0].get('delta', {})
                                            if 'content' in delta:
                                                content = delta['content']
                                                print(content, end='', flush=True)
                                                full_response += content
                            except (json.JSONDecodeError, UnicodeDecodeError):
                                continue
                    
                    return full_response
                
        except aiohttp.ClientConnectionError as e:
            self.log.error(
                f"Connection failed: {str(e)}\n"
                "Troubleshooting Steps:\n"
                "1. Verify OPENROUTER_API_KEY in .env\n"
                "2. Check internet connection\n"
                "3. Test DNS: curl -I https://openrouter.ai\n"
                "4. Validate firewall rules"
            )
            raise RuntimeError(f"Network error: {str(e)}") from e
        except aiohttp.ClientPayloadError as e:
            self.log.error(f"Data streaming error: {str(e)}")
            raise RuntimeError("Analysis interrupted") from e
        except asyncio.TimeoutError as e:
            self.log.error("Request timed out after 45 seconds")
            raise RuntimeError("Service unavailable") from e
        except Exception as e:
            self.log.error(f"Critical error: {str(e)}")
            raise RuntimeError("Analysis failed") from e
            
        finally:
            await self._close_session()

    async def _analyze_stock(self, stock_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze stock data using OpenRouter LLM with ReACT methodology"""
        try:
            quote = stock_data["quote"]
            profile = stock_data["profile"]
            
            # Format data for ReACT analysis
            system_prompt = """You are an expert stock market analyst using ReACT methodology to analyze market data.
Follow this structure:

[THOUGHT] First, analyze the company profile and market position
[ACTION] Review the provided market data and technical indicators
[OBSERVATION] Document key findings from the data
[REFLECTION] Synthesize insights and form recommendations

Format your response using these sections clearly."""

            user_prompt = f"""Analyze this stock data:
Company: {profile.get('name', 'Unknown')} ({profile.get('ticker', 'Unknown')})
Industry: {profile.get('finnhubIndustry', 'Unknown')}
Market Cap: ${profile.get('marketCapitalization', 0):,.2f}M

Current Price: ${quote.get('c', 0):,.2f}
Previous Close: ${quote.get('pc', 0):,.2f}
Day Change: {((quote.get('c', 0) - quote.get('pc', 0)) / quote.get('pc', 1) * 100):,.2f}%
Day High: ${quote.get('h', 0):,.2f}
Day Low: ${quote.get('l', 0):,.2f}

Provide a comprehensive analysis using the ReACT methodology."""

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            print("""
╔══════════════════════════════════════════════════════════════════╗
║  🧠 INITIALIZING MARKET ANALYSIS WITH ReACT METHODOLOGY          ║
╚══════════════════════════════════════════════════════════════════╝

▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
📊 DATA LOADED
🔄 ReACT PROCESS STARTING
💡 STREAMING ANALYSIS...
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀

""")
            
            analysis = await self._stream_openrouter_response(messages)
            
            return {
                "status": "success",
                "analysis": analysis,
                "model": self.model
            }
                    
        except Exception as e:
            self.log.error(f"Error analyzing stock: {str(e)}")
            raise
            
        finally:
            await self._close_session()

    async def execute(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """Execute stock agent tasks with ReACT methodology"""
        try:
            print(f"""
╔══════════════════════════════════════════════════════════════════╗
║  🚀 STOCK ANALYSIS SYSTEM v2.0 - {self.model}
║     INITIALIZING ReACT PROTOCOLS...
╚══════════════════════════════════════════════════════════════════╝

{CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
📡 MARKET DATA FEED: CONNECTING
🧮 ANALYSIS ENGINE: WARMING UP
🔍 ReACT CORE: ONLINE
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀{NC}
""")
            # Step 1: Data Collection
            print(f"{GREEN}[ReACT] Phase 1: Market Data Collection{NC}")
            print("🔄 Fetching real-time market data...")
            stock_data = await self._fetch_stock_data(symbol)
            print("✅ Market data retrieved successfully\n")
            
            # Step 2: Analysis with ReACT
            print(f"{GREEN}[ReACT] Phase 2: Neural Analysis{NC}")
            print("🧠 Initializing ReACT analysis framework...")
            analysis = await self._analyze_stock(stock_data)
            print("\n✅ Analysis complete\n")
            
            # Step 3: Report Generation
            print(f"{GREEN}[ReACT] Phase 3: Report Synthesis{NC}")
            print("📊 Compiling insights and recommendations...\n")
            
            result = {
                "status": "success",
                "data": {
                    "symbol": symbol,
                    "company": stock_data["profile"].get("name", "Unknown"),
                    "quote": {
                        "current": stock_data["quote"]["c"],
                        "previous_close": stock_data["quote"]["pc"],
                        "change_percent": ((stock_data["quote"]["c"] - stock_data["quote"]["pc"]) / stock_data["quote"]["pc"] * 100),
                        "high": stock_data["quote"]["h"],
                        "low": stock_data["quote"]["l"]
                    },
                    "profile": {
                        "industry": stock_data["profile"].get("finnhubIndustry", "Unknown"),
                        "market_cap": stock_data["profile"].get("marketCapitalization", 0),
                        "exchange": stock_data["profile"].get("exchange", "Unknown")
                    },
                    "analysis": analysis["analysis"],
                    "model": analysis["model"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

            print(f"""
{CYAN}▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀
✨ ANALYSIS COMPLETE
📈 INSIGHTS READY
🎯 RECOMMENDATIONS AVAILABLE
▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀▀{NC}
""")
            return result
            
        except Exception as e:
            self.log.error(f"Error executing stock agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format stock data for display"""
        if result["status"] != "success":
            return f"""
╔══════════════════════════════════════════════════════════════════╗
║  ❌ Stock Analysis Error
╚══════════════════════════════════════════════════════════════════╝

Error: {result.get('error', 'Unknown error')}
Timestamp: {result['timestamp']}
"""
        
        data = result["data"]
        quote = data["quote"]
        profile = data["profile"]
        
        # Determine trend emoji
        trend = "��" if quote["change_percent"] > 0 else "🔴" if quote["change_percent"] < 0 else "⚪"
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  📊 Stock Analysis - {data['company']} ({data['symbol']})
╚══════════════════════════════════════════════════════════════════╝

📈 Market Data:
  • Current Price: ${quote['current']:,.2f}
  • Previous Close: ${quote['previous_close']:,.2f}
  • Day Change: {trend} {quote['change_percent']:+.2f}%
  • Day Range: ${quote['low']:,.2f} - ${quote['high']:,.2f}

🏢 Company Profile:
  • Industry: {profile['industry']}
  • Market Cap: ${profile['market_cap']:,.2f}M
  • Exchange: {profile['exchange']}

🔍 Analysis (using {data['model']}):
{data['analysis']}

⏰ Last Updated: {result['timestamp']}
"""

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()
        if self.session:
            asyncio.create_task(self._close_session())