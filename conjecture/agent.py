import yaml
import dspy
import os
from typing import Dict, Any

from conjecture.core.neural import NeuralSubsystem
from conjecture.core.symbolic import SymbolicSubsystem
from conjecture.core.gating import GatingController

class CACAgent:
    def __init__(self, config_path: str = None):
        """
        Initialize the CAC agent with its neural and symbolic subsystems
        
        Args:
            config_path: Path to the agent configuration file
        """
        if config_path is None:
            # Use default config path relative to package
            package_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(package_dir, 'config', 'agents.yaml')
            
        self.config = self._load_config(config_path)
        self._initialize_systems()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config['cac_agent']
        except Exception as e:
            print(f"Error loading config: {e}")
            return {}
            
    def _initialize_systems(self):
        """Initialize the neural, symbolic, and gating systems"""
        # Load prompts
        try:
            package_dir = os.path.dirname(os.path.abspath(__file__))
            prompts_path = os.path.join(package_dir, 'config', 'prompts.yaml')
            with open(prompts_path, 'r') as f:
                prompts = yaml.safe_load(f)
                dspy.settings.configure(
                    neural_system_prompt=prompts['neural_system_prompt'],
                    symbolic_system_prompt=prompts['symbolic_system_prompt']
                )
        except Exception as e:
            print(f"Error loading prompts: {e}")
        
        # Initialize subsystems with default config if none loaded
        default_config = {
            'systems': {
                'neural': {'confidence_threshold': 0.75},
                'symbolic': {'rules_file': os.path.join(package_dir, 'config', 'rules.yaml')},
                'gating': {'default_threshold': 0.75, 'adaptation_rate': 0.1}
            }
        }
        
        config = self.config or default_config
        
        # Initialize subsystems
        self.system1 = NeuralSubsystem(config['systems']['neural'])
        self.system2 = SymbolicSubsystem(config['systems']['symbolic'])
        self.gating = GatingController(config['systems']['gating'])
        
    def process(self, x: float) -> Dict[str, Any]:
        """
        Process input using both systems and gating
        
        Args:
            x: Input value to classify
            
        Returns:
            Dict containing prediction results and metadata
        """
        # Get neural prediction
        neural_pred, confidence = self.system1.predict(x)
        
        # Get symbolic prediction
        symbolic_pred, reason = self.system2.reason(x)
        
        # Get gating decision
        final_pred, source, conf = self.gating.decide(
            (neural_pred, confidence),
            (symbolic_pred, reason),
            confidence
        )
        
        return {
            'prediction': final_pred,
            'confidence': conf,
            'source': source,
            'neural_prediction': neural_pred,
            'symbolic_prediction': symbolic_pred,
            'reasoning': reason,
            'input_value': x
        }
        
    def update_performance(self, performance_metric: float):
        """
        Update system based on performance feedback
        
        Args:
            performance_metric: float between 0 and 1 indicating performance
        """
        self.gating.update_threshold(performance_metric)
