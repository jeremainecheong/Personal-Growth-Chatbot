"""
Test package for the Personal Growth Assistant Bot.

This package contains test modules for various components of the bot:
- Database models and connections
- AI analysis functionality
- Helper utilities
- Bot conversation handlers
"""

import os
import sys
import logging
from pathlib import Path

# Add the src directory to Python path for imports
src_path = str(Path(__file__).parent.parent / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Configure logging for tests
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Ensure required environment variables are set for testing
os.environ.setdefault('MONGODB_URI', 'mongomock://localhost/test_db')
os.environ.setdefault('OPENAI_API_KEY', 'test_key')
os.environ.setdefault('TELEGRAM_BOT_TOKEN', 'test_token')
os.environ.setdefault('MAX_MESSAGE_LENGTH', '4096')
os.environ.setdefault('DAILY_REFLECTION_TIME', '21:00')
os.environ.setdefault('MAX_SITUATIONS_HISTORY', '50')
os.environ.setdefault('MAX_JOURNAL_ENTRIES', '100')
os.environ.setdefault('ANALYSIS_WINDOW_DAYS', '30')
