# CAC Agent Configuration Guide

## Runtime Configuration

The CAC agent supports real-time fine-tuning of its decision-making process through command-line options. This allows users to adjust system behavior without modifying configuration files or restarting the agent.

### Command-Line Options

```bash
# Basic prediction
cac predict 0.75

# Override confidence threshold
cac predict 0.75 --threshold 0.9

# Force specific system
cac predict 0.75 --force-system neural
cac predict 0.75 --force-system symbolic

# Show detailed reasoning
cac predict 0.75 --verbose
```

### Use Cases

1. **Confidence Threshold Adjustment**
   - Default threshold is 0.75
   - Increase for high-stakes decisions: `--threshold 0.9`
   - Decrease for exploratory analysis: `--threshold 0.6`
   ```bash
   # High-confidence requirement
   cac predict 0.75 --threshold 0.9
   ```

2. **System Selection**
   - Force neural system for pattern-based decisions
   - Force symbolic system for rule-based validation
   ```bash
   # Test neural system behavior
   cac predict 0.75 --force-system neural
   ```

3. **Detailed Analysis**
   - View step-by-step reasoning process
   - Understand system decisions
   ```bash
   # Show detailed reasoning steps
   cac predict 0.75 --verbose
   ```

## Static Configuration

### Main Agent Configuration (config/agents.yaml)

```yaml
cac_agent:
  name: "CAC Agent"
  version: "1.0.0"
  description: "Cohen's Agentic Conjecture implementation"
  
  systems:
    neural:
      model_type: "simple_mlp"
      confidence_threshold: 0.75
      
    symbolic:
      rules_file: "config/rules.yaml"
      
    gating:
      default_threshold: 0.75
      adaptation_rate: 0.1
```

### Rules Configuration (config/rules.yaml)

```yaml
rules:
  - name: "sign_rule"
    description: "Determine class based on sign of input"
    conditions:
      - "x < 0"
      - "class = 0"
      - "x >= 0"
      - "class = 1"
```

## Best Practices

1. **Threshold Selection**
   - Higher thresholds (>0.8) for critical decisions
   - Lower thresholds (<0.7) for exploratory analysis
   - Default (0.75) for general use

2. **System Selection**
   - Use neural system for pattern recognition
   - Use symbolic system for rule validation
   - Let gating decide for balanced decisions

3. **Verbose Output**
   - Use for debugging and analysis
   - Helpful for understanding edge cases
   - Useful for system validation

## Examples

### Critical Decision Making
```bash
# High confidence requirement with detailed reasoning
cac predict 0.75 --threshold 0.9 --verbose
```

### System Testing
```bash
# Compare system behaviors
cac predict 0.05 --force-system neural
cac predict 0.05 --force-system symbolic
```

### Edge Case Analysis
```bash
# Analyze decision boundary
cac predict 0.01 --verbose
cac predict -0.01 --verbose
```

## Troubleshooting

1. **Inconsistent Decisions**
   - Check confidence threshold
   - Verify rule configurations
   - Use verbose mode for analysis

2. **System Bias**
   - Adjust confidence threshold
   - Review symbolic rules
   - Force system for validation

3. **Performance Issues**
   - Monitor decision times
   - Check rule complexity
   - Adjust thresholds if needed
