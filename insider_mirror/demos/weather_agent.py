"""Demo agent that fetches and analyzes weather data."""

import asyncio
import logging
import aiohttp
import os
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from ..agents.base_agent import BaseAgent
from ..cli.parser import ArgumentParser

class WeatherAgent(BaseAgent):
    """Agent that demonstrates API integration and LLM analysis"""
    
    def __init__(self, agent_config: Dict[str, Any]):
        self.name = "weather_agent"  # Set name before super().__init__
        super().__init__(self.name, agent_config)
        self.session = None
        self.model = agent_config.get("model", ArgumentParser.DEFAULT_MODEL)

    async def _init_session(self) -> None:
        """Initialize aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def _close_session(self) -> None:
        """Close aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()

    async def _fetch_weather(self, city: str, country_code: Optional[str] = None) -> Dict[str, Any]:
        """Fetch weather data from OpenWeatherMap API"""
        try:
            await self._init_session()
            
            # Build query
            location = f"{city}"
            if country_code:
                location = f"{city},{country_code}"
            
            api_key = os.getenv("OPENWEATHER_API_KEY")
            if not api_key:
                raise ValueError("OPENWEATHER_API_KEY environment variable is required")
            
            params = {
                "q": location,
                "appid": api_key,
                "units": "metric"  # Use metric units
            }
            
            self.log.info(f"Fetching weather data for {location}")
            async with self.session.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"API error: {error_text}")
                    
        except Exception as e:
            self.log.error(f"Error fetching weather: {str(e)}")
            raise
            
        finally:
            await self._close_session()

    async def _analyze_weather(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather data using OpenRouter LLM"""
        try:
            # Format weather data for analysis
            prompt = f"""Analyze this weather data and provide insights:
Location: {weather_data['name']}, {weather_data['sys']['country']}
Temperature: {weather_data['main']['temp']}°C
Conditions: {weather_data['weather'][0]['description']}
Humidity: {weather_data['main']['humidity']}%
Wind Speed: {weather_data['wind']['speed']} m/s

Provide:
1. A brief description of current conditions
2. Notable weather patterns or concerns
3. Recommendations for outdoor activities
4. Any weather warnings or advisories
"""
            # Call OpenRouter API
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            
            await self._init_session()
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:3000",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            self.log.info(f"Analyzing weather data with LLM model: {self.model}")
            async with self.session.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    llm_response = await response.json()
                    analysis = llm_response["choices"][0]["message"]["content"]
                    return {
                        "status": "success",
                        "analysis": analysis,
                        "model": self.model
                    }
                else:
                    error_text = await response.text()
                    raise RuntimeError(f"OpenRouter API error: {error_text}")
                    
        except Exception as e:
            self.log.error(f"Error analyzing weather: {str(e)}")
            raise
            
        finally:
            await self._close_session()

    async def execute(
        self,
        city: str,
        country_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute weather agent tasks"""
        try:
            self.track_progress(1, "Fetching weather data")
            weather_data = await self._fetch_weather(city, country_code)
            
            self.track_progress(2, "Analyzing weather conditions")
            analysis = await self._analyze_weather(weather_data)
            
            self.track_progress(3, "Generating report")
            
            return {
                "status": "success",
                "data": {
                    "location": {
                        "city": weather_data["name"],
                        "country": weather_data["sys"]["country"]
                    },
                    "current": {
                        "temperature": weather_data["main"]["temp"],
                        "feels_like": weather_data["main"]["feels_like"],
                        "humidity": weather_data["main"]["humidity"],
                        "pressure": weather_data["main"]["pressure"],
                        "conditions": weather_data["weather"][0]["description"],
                        "wind_speed": weather_data["wind"]["speed"]
                    },
                    "analysis": analysis["analysis"],
                    "model": analysis["model"]
                },
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.log.error(f"Error executing weather agent: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

    def format_output(self, result: Dict[str, Any]) -> str:
        """Format weather data for display"""
        if result["status"] != "success":
            return f"""
╔══════════════════════════════════════════════════════════════════╗
║  ❌ Weather Data Error
╚══════════════════════════════════════════════════════════════════╝

Error: {result.get('error', 'Unknown error')}
Timestamp: {result['timestamp']}
"""
        
        data = result["data"]
        current = data["current"]
        
        return f"""
╔══════════════════════════════════════════════════════════════════╗
║  🌤️  Weather Report - {data['location']['city']}, {data['location']['country']}
╚══════════════════════════════════════════════════════════════════╝

📊 Current Conditions:
  • Temperature: {current['temperature']}°C (Feels like: {current['feels_like']}°C)
  • Conditions: {current['conditions']}
  • Humidity: {current['humidity']}%
  • Pressure: {current['pressure']} hPa
  • Wind Speed: {current['wind_speed']} m/s

🔍 Analysis (using {data['model']}):
{data['analysis']}

⏰ Last Updated: {result['timestamp']}
"""

    def cleanup(self) -> None:
        """Clean up resources"""
        super().cleanup()
        if self.session:
            asyncio.create_task(self._close_session())