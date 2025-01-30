"""Data agent for fetching and validating insider trading data."""

import os
import aiohttp
import asyncio
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from .base_agent import BaseAgent

class DataAgent(BaseAgent):
    """Agent responsible for data acquisition and validation"""
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "data_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.tasks_config = self.load_config("src/insider_mirror/config/tasks.yaml")
        self.session = None
        # Set logging level to DEBUG
        self.log.setLevel("DEBUG")
        self.session = None

    async def _init_session(self) -> None:
        """Initialize aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _close_session(self) -> None:
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def test_api(
        self,
        api_key: str,
        endpoint: str,
        api_type: str = "finnhub"
    ) -> Dict[str, Any]:
        """Test API connectivity and get response metrics"""
        self.log.info(f"Testing {api_type.upper()} API connectivity")
        
        if not api_key or not endpoint:
            return {
                "status": "error",
                "error": "API key and endpoint are required",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        await self._init_session()
        
        # Configure headers and params based on API type
        if api_type == "finnhub":
            headers = {
                "X-Finnhub-Token": api_key,
                "Content-Type": "application/json"
            }
            params = None
        else:  # tradefeeds
            headers = {
                "Content-Type": "application/json"
            }
            params = {
                "key": api_key
            }
        
        try:
            start_time = time.time()
            self.log.info("Sending API request...")
            
            async with self.session.get(endpoint, headers=headers, params=params) as response:
                response_time = int((time.time() - start_time) * 1000)  # Convert to milliseconds
                
                self.log.info(f"Response status: {response.status}")
                self.log.debug(f"Response headers: {dict(response.headers)}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # Handle different API response formats
                    if api_type == "finnhub":
                        rate_limit = response.headers.get('X-RateLimit-Remaining', 'N/A')
                    else:  # tradefeeds
                        rate_limit = data.get('status', {}).get('rate_limit_remaining', 'N/A')
                    
                    self.log.info("API test successful")
                    return {
                        "status": "success",
                        "response_time": response_time,
                        "rate_limit_remaining": rate_limit,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    error_text = await response.text()
                    self.log.error(f"API test failed with status {response.status}: {error_text}")
                    return {
                        "status": "error",
                        "error": f"HTTP {response.status}: {error_text}",
                        "response_time": response_time,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
        except aiohttp.ClientError as e:
            self.log.error(f"API test failed with client error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        finally:
            await self._close_session()

    async def fetch_data(
        self,
        api_key: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        api_type: str = "finnhub"
    ) -> Dict[str, Any]:
        """Fetch data from API"""
        if not api_key or not endpoint:
            raise ValueError("API key and endpoint are required")
            
        await self._init_session()
        
        # Configure headers and params based on API type
        if api_type == "finnhub":
            headers = {
                "X-Finnhub-Token": api_key,
                "Content-Type": "application/json"
            }
            request_params = params
        else:  # tradefeeds
            headers = {
                "Content-Type": "application/json"
            }
            request_params = {
                "key": api_key,
                **(params or {})
            }
        
        try:
            async with self.session.get(endpoint, headers=headers, params=request_params) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Handle different API response formats
                if api_type == "finnhub":
                    self.log.debug(f"Finnhub raw response type: {type(data)}")
                    self.log.debug(f"Finnhub raw response keys: {data.keys() if isinstance(data, dict) else 'Not a dict'}")
                    raw_data = data.get('data', []) if isinstance(data, dict) else []
                    self.log.debug(f"Number of raw records: {len(raw_data)}")
                    if raw_data:
                        self.log.debug(f"First record example: {raw_data[0]}")
                        self.log.debug(f"First record keys: {raw_data[0].keys() if isinstance(raw_data[0], dict) else 'Not a dict'}")
                    # Map Finnhub fields to our expected format
                    return [{
                        'symbol': record.get('symbol', ''),
                        'transaction_type': 'PURCHASE' if record.get('transactionCode') == '38' else 'SALE',
                        'shares': abs(float(record.get('change', 0))),
                        'price': float(record.get('transactionPrice', 0)),
                        'value': abs(float(record.get('change', 0)) * float(record.get('transactionPrice', 0))),
                        'filing_date': record.get('filingDate', '')
                    } for record in raw_data]
                else:  # tradefeeds
                    return data.get('results', {}).get('output', {}).get('holdings', [])
                
        except aiohttp.ClientError as e:
            self.log.error(f"API request failed: {str(e)}")
            raise

    def validate_data(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate fetched data"""
        self.log.debug(f"Validating data type: {type(data)}")
        if not isinstance(data, list):
            self.log.error(f"Invalid data format: expected list, got {type(data)}")
            self.log.debug(f"Data content: {str(data)[:500]}...")  # First 500 chars
            return []
            
        required_fields = {
            "symbol": str,
            "transaction_type": str,
            "shares": (int, float),
            "price": float,
            "value": float,
            "filing_date": str
        }
        
        valid_records = []
        for record in data:
            try:
                # Check required fields and types with detailed logging
                valid = True
                for field, field_type in required_fields.items():
                    if field not in record:
                        self.log.debug(f"Missing field: {field} in record {record}")
                        valid = False
                        break
                    if not isinstance(record[field], field_type):
                        self.log.debug(f"Invalid type for {field}: expected {field_type}, got {type(record[field])} in record {record}")
                        valid = False
                        break
                
                if not valid:
                    continue
                    
                # Additional validation rules
                if record["shares"] <= 0 or record["price"] <= 0:
                    continue
                    
                if record["value"] != record["shares"] * record["price"]:
                    continue
                    
                # Validate date format
                try:
                    datetime.fromisoformat(record["filing_date"].replace('Z', '+00:00'))
                except ValueError:
                    continue
                    
                valid_records.append(record)
                
            except Exception as e:
                self.log.error(f"Record validation failed: {str(e)}")
                continue
                
        return valid_records

    async def execute(
        self,
        api_key: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        api_type: str = "finnhub"
    ) -> Dict[str, Any]:
        """Execute data agent tasks"""
        try:
            self.track_progress(1, "Initiating API request")
            
            # Fetch data
            data = await self.fetch_data(api_key, endpoint, params, api_type)
            self.track_progress(2, f"Retrieved {len(data)} records")
            
            # Validate data
            valid_data = self.validate_data(data)
            self.track_progress(3, f"Validated {len(valid_data)} records")
            
            return {
                "status": "success",
                "data": valid_data,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Error executing data agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()
        if self.session:
            asyncio.create_task(self._close_session())