"""Base agent class with common functionality."""

import logging
import yaml
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

class BaseAgent:
    """Base class for all agents"""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize base agent"""
        self.name = name
        self.config = config if isinstance(config, dict) else {}
        self.validation_status = {
            "reasoning": [],
            "actions": []
        }
        self.progress_tracker = {
            "current_step": 0,
            "total_steps": 0,
            "status": ""
        }
        self.log = logging.getLogger(f"insider_mirror.agents.{name}")

    def load_config(self, path: str) -> Dict[str, Any]:
        """Load YAML configuration file"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            self.log.error(f"Error loading config from {path}: {str(e)}")
            raise RuntimeError(f"Failed to load config: {str(e)}")

    def validate_reasoning(self, reasoning: Union[str, Dict[str, Any]]) -> bool:
        """Validate agent reasoning"""
        if not self.config.get("react_validation", {}).get("thought_required", False):
            return True
            
        if isinstance(reasoning, dict):
            reasoning_text = reasoning.get("thought", "")
        else:
            reasoning_text = reasoning
            
        if not reasoning_text or len(reasoning_text.strip()) == 0:
            return False
            
        depth = self.config.get("react_validation", {}).get("reasoning_depth", 1)
        sentences = [s.strip() for s in reasoning_text.split(".") if s.strip()]
        
        if len(sentences) < depth:
            return False
            
        self.validation_status["reasoning"].append(reasoning_text)
        return True

    def validate_action(self, action: Union[str, Dict[str, Any]]) -> bool:
        """Validate agent action"""
        if not self.config.get("react_validation", {}).get("action_validation", False):
            return True
            
        if isinstance(action, dict):
            action_text = action.get("action", "")
        else:
            action_text = action
            
        if not action_text or len(action_text.strip()) == 0:
            return False
            
        self.validation_status["actions"].append(action_text)
        return True

    def track_progress(self, step: Union[int, str], status: str) -> None:
        """Track agent progress"""
        if not self.config.get("verbose", False):
            return
            
        if isinstance(step, str):
            current_step = self.progress_tracker["current_step"] + 1
        else:
            current_step = step
            
        self.progress_tracker["current_step"] = current_step
        self.progress_tracker["status"] = status
        
        # Print progress update
        print(f"""
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
📊 Progress Update - {self.name}:
➤ Step {current_step}: {status}
▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
""")

    def update_progress(self, current: int, total: int, status: str) -> None:
        """Update progress tracker"""
        self.progress_tracker["current_step"] = current
        self.progress_tracker["total_steps"] = total
        self.progress_tracker["status"] = status
        
        if self.config.get("verbose", False):
            self.log.info(f"Progress: {current}/{total} - {status}")

    def cleanup(self) -> None:
        """Clean up agent resources"""
        if self.config.get("verbose", False):
            self.log.info(f"Cleaning up {self.name} agent resources")
            
        self.validation_status = {
            "reasoning": [],
            "actions": []
        }
        self.progress_tracker = {
            "current_step": 0,
            "total_steps": 0,
            "status": ""
        }