import click
import yaml
import os
import warnings
from conjecture.agent import CACAgent

# Suppress pydantic warning
warnings.filterwarnings("ignore", message="Valid config keys have changed in V2")

@click.group()
def cli():
    """Cohen's Agentic Conjecture (CAC) Agent CLI"""
    pass

@cli.command()
@click.argument('value', type=float)
def predict(value):
    """Make a prediction for a given input value"""
    try:
        agent = CACAgent()
        result = agent.process(value)
        
        # Format output
        click.echo("\nPrediction Results:")
        click.echo("=" * 50)
        click.echo(f"Input Value: {value}")
        click.echo(f"Final Prediction: {result['prediction']}")
        click.echo(f"Confidence: {result['confidence']:.2f}")
        click.echo(f"Decision Source: {result['source']}")
        click.echo("\nSystem Details:")
        click.echo(f"Neural Prediction: {result['neural_prediction']}")
        click.echo(f"Symbolic Prediction: {result['symbolic_prediction']}")
        click.echo(f"Symbolic Reasoning: {result['reasoning']}")
        click.echo("=" * 50)
    except Exception as e:
        click.echo(f"Error during prediction: {e}")

@cli.command()
def info():
    """Display information about the CAC agent"""
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
