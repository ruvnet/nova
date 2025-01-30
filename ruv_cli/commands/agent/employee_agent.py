import os
import time
import threading
from typing import Dict, Optional
from dotenv import load_dotenv
from .base_agent import BaseAgent

# Load environment variables from .env file
load_dotenv("e2b-agent/.env")

# Global store for running agents
AGENT_THREADS: Dict[str, threading.Thread] = {}
AGENT_STATES: Dict[str, bool] = {}
ROLE_TO_ID: Dict[str, str] = {}  # Map roles to agent IDs

class EmployeeAgent(BaseAgent):
    """Agent for long-running specialized tasks"""
    def __init__(self, name: str = "EmployeeAgent", role: str = ""):
        super().__init__(name=name)
        self.role = role
        self.active = True
        
    def run(self, start: bool = False, stop: bool = False, status: bool = False) -> str:
        """Execute employee agent operations"""
        try:
            if start:
                return self._start_agent()
            elif stop:
                return self._stop_agent()
            elif status:
                return self._get_status()
            else:
                raise ValueError("Must specify start/stop/status")
        except Exception as e:
            self.log(f"Error executing operation: {str(e)}")
            return ""
            
    def _start_agent(self) -> str:
        """Start the agent thread"""
        agent_id = f"{self.role}_{id(self)}"
        
        # Check if role already has a running agent
        if self.role in ROLE_TO_ID:
            existing_id = ROLE_TO_ID[self.role]
            if existing_id in AGENT_THREADS and AGENT_THREADS[existing_id].is_alive():
                return f"Agent {self.role} already running"
            # Clean up old agent
            if existing_id in AGENT_THREADS:
                del AGENT_THREADS[existing_id]
            if existing_id in AGENT_STATES:
                del AGENT_STATES[existing_id]
            del ROLE_TO_ID[self.role]
            
        AGENT_STATES[agent_id] = True
        thread = threading.Thread(target=self._run_loop, args=(agent_id,))
        thread.daemon = True
        thread.start()
        
        AGENT_THREADS[agent_id] = thread
        ROLE_TO_ID[self.role] = agent_id
        return f"Started agent {self.role}"
        
    def _stop_agent(self) -> str:
        """Stop the agent thread"""
        agent_id = ROLE_TO_ID.get(self.role)
        if not agent_id:
            return f"Agent {self.role} not running"
            
        if agent_id not in AGENT_THREADS:
            if self.role in ROLE_TO_ID:
                del ROLE_TO_ID[self.role]
            return f"Agent {self.role} not running"
            
        AGENT_STATES[agent_id] = False
        thread = AGENT_THREADS[agent_id]
        thread.join(timeout=5.0)
        
        if agent_id in AGENT_THREADS:
            del AGENT_THREADS[agent_id]
        if agent_id in AGENT_STATES:
            del AGENT_STATES[agent_id]
        if self.role in ROLE_TO_ID:
            del ROLE_TO_ID[self.role]
            
        return f"Stopped agent {self.role}"
        
    def _get_status(self) -> str:
        """Get agent status"""
        agent_id = ROLE_TO_ID.get(self.role)
        if not agent_id:
            return f"Agent {self.role} is not running"
            
        if agent_id in AGENT_THREADS and AGENT_THREADS[agent_id].is_alive():
            return f"Agent {self.role} is running"
            
        # Clean up stale entries
        if agent_id in AGENT_THREADS:
            del AGENT_THREADS[agent_id]
        if agent_id in AGENT_STATES:
            del AGENT_STATES[agent_id]
        if self.role in ROLE_TO_ID:
            del ROLE_TO_ID[self.role]
            
        return f"Agent {self.role} is not running"
        
    def _run_loop(self, agent_id: str):
        """Main agent loop"""
        self.log(f"Starting {self.role} loop")
        
        while AGENT_STATES.get(agent_id, False):
            try:
                # In real implementation, this would do actual work
                # For testing, we'll just sleep
                if agent_id in AGENT_STATES:  # Check if we should still be running
                    time.sleep(1)
                    self.log(f"{self.role} working...")
                
            except Exception as e:
                self.log(f"Error in agent loop: {str(e)}")
                time.sleep(5)  # Back off on error
                
        self.log(f"Stopping {self.role} loop")
        if agent_id in AGENT_THREADS:
            del AGENT_THREADS[agent_id]
        if agent_id in AGENT_STATES:
            del AGENT_STATES[agent_id]
        if self.role in ROLE_TO_ID and ROLE_TO_ID[self.role] == agent_id:
            del ROLE_TO_ID[self.role]

def manage_employee_agent(role: str, start: bool = False, stop: bool = False, status: bool = False) -> bool:
    """Manage employee agent lifecycle"""
    if not role:
        print("[ERROR] Role is required")
        return False
        
    try:
        agent = EmployeeAgent(role=role)
        result = agent.run(start=start, stop=stop, status=status)
        if result:
            agent.log(result)
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] Employee agent operation failed: {str(e)}")
        return False