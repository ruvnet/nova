import yaml
import os
from typing import Any, Dict, Tuple

class SymbolicSubsystem:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.rules = self._load_rules()
        
    def _load_rules(self):
        """Load rules from configuration file"""
        rules_file = self.config.get('rules_file', 'config/rules.yaml')
        try:
            package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            rules_path = os.path.join(package_dir, 'config', 'rules.yaml')
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading rules: {e}")
            return {"rules": []}
            
    def reason(self, x) -> Tuple[int, str]:
        """
        Apply symbolic reasoning to input
        
        Args:
            x: Input value
            
        Returns:
            Tuple[int, str]: (prediction, reasoning)
        """
        try:
            value = float(x)
            
            # Apply sign rule
            if value < 0:
                reasoning = f"Value {value} is negative, therefore class 0"
                return 0, reasoning
            else:
                reasoning = f"Value {value} is non-negative, therefore class 1"
                return 1, reasoning
                
        except Exception as e:
            print(f"Error in symbolic reasoning: {e}")
            # Return default values
            return 0, "error in reasoning"
            
    def validate(self, neural_output: Tuple[int, float], confidence: float) -> bool:
        """
        Validate neural output using confidence rule
        
        Args:
            neural_output: (prediction, confidence) from neural system
            confidence: confidence score from neural system
            
        Returns:
            bool: True if should use symbolic output, False otherwise
        """
        prediction, _ = neural_output
        
        if confidence < self.config.get('confidence_threshold', 0.75):
            # Low confidence, use symbolic
            return True
        return False
