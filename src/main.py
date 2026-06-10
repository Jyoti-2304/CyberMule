"""Main application entry point"""

import logging
import os
from pathlib import Path
from dotenv import load_dotenv
from src.api import create_api_server
from src.logging_config import configure_logging

# Configure logging
configure_logging()
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    logger.warning(f".env file not found at {env_path}")


def create_app():
    """Create and configure the FastAPI application"""
    
    # API configuration
    api_config = {
        'host': os.getenv('API_HOST', '0.0.0.0'),
        'port': int(os.getenv('API_PORT', 8000)),
        'debug': os.getenv('API_DEBUG', 'false').lower() == 'true'
    }
    
    # Create API server
    logger.info("Creating API server")
    api_server = create_api_server(api_config)
    
    return api_server.get_app()


def main():
    """Main application entry point"""
    logger.info("Starting Bank Fraud Detection API")
    
    api_config = {
        'host': os.getenv('API_HOST', '0.0.0.0'),
        'port': int(os.getenv('API_PORT', 8000)),
        'debug': os.getenv('API_DEBUG', 'false').lower() == 'true'
    }
    
    # Create and run API server
    api_server = create_api_server(api_config)
    api_server.run(
    host=api_config["host"],
    port=api_config["port"]
)


if __name__ == '__main__':
    main()
