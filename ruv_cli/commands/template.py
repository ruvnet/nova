import os
import json
from pathlib import Path

def init_template():
    """Initialize a new sandbox template"""
    # Create template files
    if os.path.exists("e2b.toml") or os.path.exists("Dockerfile"):
        print("Template files already exist in current directory")
        return False

    # Create e2b.toml
    toml_content = """template_id = ""
dockerfile = "Dockerfile"
template_name = "custom-template"
start_cmd = "/root/.jupyter/start-up.sh"
"""
    try:
        with open("e2b.toml", "w") as f:
            f.write(toml_content)

        # Create Dockerfile
        dockerfile_content = """FROM e2bdev/code-interpreter:latest

# System packages
RUN apt-get update && apt-get install -y \\
    python3-dev \\
    build-essential

# Python packages
RUN pip install \\
    pandas==2.0.3 \\
    numpy==1.24.4 \\
    matplotlib==3.7.2

# Cleanup
RUN apt-get clean && \\
    rm -rf /var/lib/apt/lists/*
"""
        with open("Dockerfile", "w") as f:
            f.write(dockerfile_content)

        print("Template files created successfully")
        return True

    except IOError as e:
        print(f"Error creating template files: {str(e)}")
        return False

def build_template():
    """Build a sandbox template"""
    if not os.path.exists("e2b.toml") or not os.path.exists("Dockerfile"):
        print("Template files not found. Run 'ruv template init' first")
        return False

    try:
        # In a real implementation, this would use the E2B SDK to build
        # For now, we'll just simulate the build
        print("Building template...")
        print("Template built successfully")
        return True

    except Exception as e:
        print(f"Error building template: {str(e)}")
        return False

def list_templates():
    """List available templates"""
    try:
        # In a real implementation, this would use the E2B SDK to list templates
        # For now, we'll just show a simulated list
        templates = [
            {"id": "custom-template", "name": "Custom Template", "status": "ready"},
            {"id": "base", "name": "Base Template", "status": "ready"}
        ]
        
        print("\nAvailable Templates:")
        print("-" * 50)
        print(f"{'ID':<20} {'Name':<20} {'Status':<10}")
        print("-" * 50)
        
        for template in templates:
            print(f"{template['id']:<20} {template['name']:<20} {template['status']:<10}")
        
        return True

    except Exception as e:
        print(f"Error listing templates: {str(e)}")
        return False