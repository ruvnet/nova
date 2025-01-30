import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv("e2b-agent/.env")

class DataAgent:
    """Agent for data analysis operations"""
    def __init__(self, name: str = "DataAgent"):
        self.name = name
        
    def log(self, message: str):
        """Print a log message with agent name prefix"""
        print(f"[{self.name}] {message}")
        
    def run(self, operation: str, file_path: Optional[str] = None, columns: Optional[list] = None) -> str:
        """Execute data operation"""
        try:
            if operation == "load":
                return self._load_data(file_path)
            elif operation == "describe":
                return self._describe_data(file_path, columns)
            elif operation == "plot":
                return self._plot_data(file_path, columns)
            else:
                raise ValueError(f"Unknown operation: {operation}")
        except Exception as e:
            self.log(f"Error executing operation: {str(e)}")
            return ""
            
    def _load_data(self, file_path: Optional[str]) -> str:
        """Load data from file"""
        if not file_path:
            raise ValueError("File path required for load operation")
            
        # In real implementation, this would load data using pandas
        return f"Loaded data from {file_path}"
        
    def _describe_data(self, file_path: Optional[str], columns: Optional[list]) -> str:
        """Generate descriptive statistics"""
        if not file_path:
            raise ValueError("File path required for describe operation")
            
        # In real implementation, this would use pandas describe()
        cols = ", ".join(columns) if columns else "all columns"
        return f"Generated statistics for {cols} in {file_path}"
        
    def _plot_data(self, file_path: Optional[str], columns: Optional[list]) -> str:
        """Create data visualization"""
        if not file_path:
            raise ValueError("File path required for plot operation")
            
        # In real implementation, this would use matplotlib/seaborn
        cols = ", ".join(columns) if columns else "all columns"
        return f"Created plot for {cols} in {file_path}"

def run_data_operation(operation: str, file_path: Optional[str] = None, columns: Optional[list] = None) -> bool:
    """Execute data analysis operation"""
    if not operation:
        print("[ERROR] No operation specified for data agent.")
        return False
        
    try:
        agent = DataAgent()
        result = agent.run(operation, file_path, columns)
        if result:
            agent.log(result)
            return True
        return False
        
    except Exception as e:
        print(f"[ERROR] Data operation failed: {str(e)}")
        return False