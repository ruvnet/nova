import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".ruv"
CONFIG_FILE = CONFIG_DIR / "config.json"

def login():
    """Login to E2B using API key from environment"""
    api_key = os.getenv("E2B_API_KEY")
    if not api_key:
        print("Error: E2B_API_KEY environment variable not set")
        return False
        
    try:
        # Create config directory if it doesn't exist
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Store API key
        config = {"api_key": api_key}
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f)
            
        print("Successfully logged in to E2B")
        return True
        
    except IOError as e:
        print(f"Error writing config file: {str(e)}")
        # Clean up partial files if they exist
        if CONFIG_FILE.exists():
            try:
                CONFIG_FILE.unlink()
            except IOError:
                pass
        return False
    except Exception as e:
        print(f"Unexpected error during login: {str(e)}")
        return False

def logout():
    """Clear stored credentials"""
    if not CONFIG_FILE.exists():
        print("No active session found")
        return False
        
    try:
        CONFIG_FILE.unlink()
        print("Successfully logged out from E2B")
        
        # Try to remove config directory if empty
        try:
            CONFIG_DIR.rmdir()
        except (IOError, OSError):
            # Directory not empty or other error, ignore
            pass
            
        return True
        
    except IOError as e:
        print(f"Error removing config file: {str(e)}")
        return False
    except Exception as e:
        print(f"Unexpected error during logout: {str(e)}")
        return False