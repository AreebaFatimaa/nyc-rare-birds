"""
Helper script to load environment variables from .env file for local development.
"""

import os
from pathlib import Path

def load_env():
    """Load environment variables from .env file if it exists."""
    env_file = Path(__file__).parent.parent / '.env'

    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()
        print("Environment variables loaded")
    else:
        print(f"No .env file found at {env_file}")
        print("Using environment variables from system")

if __name__ == "__main__":
    load_env()
    api_key = os.environ.get('EBIRD_API_KEY', '')
    if api_key:
        print(f"EBIRD_API_KEY is set: {api_key[:8]}...")
    else:
        print("WARNING: EBIRD_API_KEY is not set!")
