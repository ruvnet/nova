class BaseAgent:
    """Base class for all agent types"""
    
    def __init__(self, name: str = "BaseAgent"):
        self.name = name
        
    def log(self, message: str):
        """Print a log message with agent name prefix"""
        print(f"[{self.name}] {message}")
        
    def run(self, *args, **kwargs):
        """
        Base run method to be implemented by derived classes.
        Each agent type will implement its own run logic.
        """
        raise NotImplementedError("Agent must implement run method")