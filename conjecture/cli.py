import click
import yaml
import os
import warnings
from conjecture.agent import CACAgent

# Suppress pydantic warning
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")

HELP_TEXT = """Cohen's Agentic Conjecture (CAC) Agent CLI

A command-line interface for the CAC agent that implements dual-process cognitive architecture,
combining neural (System 1) and symbolic (System 2) reasoning through a dynamic gating mechanism.

Commands:
  predict  Make predictions with configurable system behavior
  info     Display agent configuration and settings

Examples:
  1. Basic Prediction:
     $ cac predict --value 0.75

  2. Detailed Analysis:
     $ cac predict --value 0.75 --verbose

  3. Override Confidence Threshold:
     $ cac predict --value -0.5 --threshold 0.9
     (Uses higher threshold for more conservative decisions)

  4. Force Specific System:
     $ cac predict --value 0.05 --force-system neural
     (Forces use of neural system regardless of confidence)
     $ cac predict --value 0.05 --force-system symbolic
     (Forces use of symbolic system for rule-based decision)

  5. Combine Options:
     $ cac predict --value -0.05 --threshold 0.8 --force-system neural --verbose
     (Full control over system behavior with detailed output)

  6. View System Information:
     $ cac info
"""

@click.group(help=HELP_TEXT)
def cli():
    """Cohen's Agentic Conjecture (CAC) Agent CLI"""
    pass

@cli.command()
@click.option('--value', type=float, required=True, help='Input value to classify (can be positive or negative)')
@click.option('--threshold', type=float, help='Override confidence threshold (0.0 to 1.0, default: 0.75)')
@click.option('--force-system', type=click.Choice(['neural', 'symbolic']), 
              help='Force specific system (neural: pattern-based, symbolic: rule-based)')
@click.option('--verbose', is_flag=True, help='Show detailed reasoning and analysis')
def predict(value, threshold, force_system, verbose):
    """Make a prediction with optional runtime configuration

    The predict command allows you to classify a numeric value using the CAC agent's
    dual-process architecture. The agent combines neural network predictions with
    symbolic reasoning, using a gating mechanism to choose between them.

    Options:
      --value FLOAT          The input value to classify (required)
      --threshold FLOAT      Override the confidence threshold (0.0 to 1.0)
      --force-system TEXT    Force using either 'neural' or 'symbolic' system
      --verbose             Show detailed reasoning and analysis

    The system uses:
    - Neural system for pattern-based decisions
    - Symbolic system for rule-based decisions
    - Gating mechanism to choose between them based on confidence

    Examples:
      $ cac predict --value 0.75 --verbose
      $ cac predict --value -0.5 --threshold 0.8
      $ cac predict --value 0.05 --force-system symbolic
    """
    try:
        agent = CACAgent()
        result = agent.process(
            value,
            threshold=threshold,
            force_system=force_system,
            verbose=verbose
        )
        
        # Format output
        click.echo("\nPrediction Results:")
        click.echo("=" * 50)
        click.echo(f"Input Value: {value}")
        click.echo(f"Final Prediction: {result['prediction']}")
        click.echo(f"Confidence: {result['confidence']:.2f}")
        click.echo(f"Decision Source: {result['source']}")
        
        if verbose:
            click.echo("\nDetailed Analysis:")
            click.echo("-" * 30)
            click.echo("Neural System:")
            click.echo(f"  Prediction: {result['detailed_reasoning']['neural']['prediction']}")
            click.echo(f"  Confidence: {result['detailed_reasoning']['neural']['confidence']:.2f}")
            
            click.echo("\nSymbolic System:")
            click.echo(f"  Prediction: {result['detailed_reasoning']['symbolic']['prediction']}")
            click.echo(f"  Reasoning: {result['detailed_reasoning']['symbolic']['reasoning']}")
            
            click.echo("\nGating Decision:")
            click.echo(f"  Threshold: {result['detailed_reasoning']['gating']['threshold']:.2f}")
            click.echo(f"  Selected System: {result['detailed_reasoning']['gating']['selected_system']}")
            click.echo(f"  Final Confidence: {result['detailed_reasoning']['gating']['final_confidence']:.2f}")
        else:
            click.echo("\nSystem Details:")
            click.echo(f"Neural Prediction: {result['neural_prediction']}")
            click.echo(f"Symbolic Prediction: {result['symbolic_prediction']}")
            click.echo(f"Symbolic Reasoning: {result['reasoning']}")
            
        click.echo("=" * 50)
    except Exception as e:
        click.echo(f"Error during prediction: {e}")

@cli.command()
def info():
    """Display information about the CAC agent

    Shows the current configuration and settings of the CAC agent, including:
    - Agent name and version
    - System description
    - Neural system threshold
    - Gating system threshold
    
    Example:
      $ cac info
    """
    try:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(package_dir, 'config', 'agents.yaml')
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
            agent_config = config['cac_agent']
            
        click.echo("\nCAC Agent Information:")
        click.echo("=" * 50)
        click.echo(f"Name: {agent_config['name']}")
        click.echo(f"Version: {agent_config['version']}")
        click.echo(f"Description: {agent_config['description']}")
        click.echo("\nSystem Configurations:")
        click.echo(f"Neural Threshold: {agent_config['systems']['neural']['confidence_threshold']}")
        click.echo(f"Gating Threshold: {agent_config['systems']['gating']['default_threshold']}")
        click.echo("=" * 50)
    except Exception as e:
        click.echo(f"Error reading configuration: {e}")

if __name__ == '__main__':
    cli()
