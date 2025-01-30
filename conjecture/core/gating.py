from typing import Any, Dict, Tuple

class GatingController:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.threshold = config.get('default_threshold', 0.75)
        self.adaptation_rate = config.get('adaptation_rate', 0.1)
        
    def decide(
        self, 
        neural_output: Tuple[int, float], 
        symbolic_output: Tuple[int, str],
        confidence: float
    ) -> Tuple[int, str, float]:
        """
        Decide which output to use based on confidence and validation
        
        Args:
            neural_output: (prediction, confidence) from neural system
            symbolic_output: (prediction, reason) from symbolic system
            confidence: confidence score from neural system
            
        Returns:
            Tuple[int, str, float]: (final_prediction, source, confidence)
        """
        neural_pred, _ = neural_output
        symbolic_pred, reason = symbolic_output
        
        try:
            # If confidence is below threshold, use symbolic
            if confidence < self.threshold:
                return symbolic_pred, "symbolic", confidence
                
            # If predictions match, use neural (it's confident and agrees with rules)
            if neural_pred == symbolic_pred:
                return neural_pred, "neural", confidence
                
            # If predictions differ and confidence is high, trust neural
            if confidence > self.threshold + 0.1:
                return neural_pred, "neural", confidence
                
            # Default to symbolic in ambiguous cases
            return symbolic_pred, "symbolic", confidence
            
        except Exception as e:
            print(f"Error in gating decision: {e}")
            # Default to symbolic system on error
            return symbolic_pred, "symbolic", confidence
        
    def update_threshold(self, performance_metric: float):
        """
        Update threshold based on performance
        
        Args:
            performance_metric: float between 0 and 1 indicating performance
        """
        if performance_metric < 0.5:
            self.threshold += self.adaptation_rate
        else:
            self.threshold -= self.adaptation_rate
        
        # Keep threshold in reasonable bounds
        self.threshold = max(0.5, min(0.95, self.threshold))
