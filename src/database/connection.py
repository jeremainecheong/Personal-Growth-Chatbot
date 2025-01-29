import os
import logging
from typing import Optional
from mongoengine import connect, disconnect
from pymongo.errors import ConnectionFailure
from datetime import datetime

logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Manages MongoDB database connection."""
    
    _instance: Optional['DatabaseConnection'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.last_connected = None
        self.connection = None
        self._initialized = True
    
    def connect(self) -> None:
        """Connect to MongoDB using environment variables."""
        try:
            # Get MongoDB URI from environment variables
            mongodb_uri = os.getenv('MONGODB_URI')
            if not mongodb_uri:
                raise ValueError("MongoDB URI not found in environment variables")

            # Disconnect if there's an existing connection
            self.disconnect()

            # Connect to MongoDB with configuration options
            self.connection = connect(
                host=mongodb_uri,
                tz_aware=True,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10,
                maxIdleTimeMS=300000,  # 5 minutes
                retryWrites=True
            )
            
            # Test the connection
            self.connection.server_info()
            
            self.last_connected = datetime.utcnow()
            logger.info(
                f"Successfully connected to MongoDB database: {mongodb_uri.split('/')[-1]}"
            )
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred while connecting to MongoDB: {e}")
            raise
    
    def disconnect(self) -> None:
        """Safely disconnect from MongoDB."""
        try:
            disconnect()
            self.connection = None
            self.last_connected = None
            logger.info("Disconnected from MongoDB")
        except Exception as e:
            logger.error(f"Error disconnecting from MongoDB: {e}")
    
    def ensure_indexes(self) -> None:
        """Ensure all database indexes are created."""
        try:
            # Import here to avoid circular imports
            from .models import User, PersonalSituation, AIAdvice, JournalEntry
            
            # This will create all indexes defined in the models
            User.ensure_indexes()
            PersonalSituation.ensure_indexes()
            AIAdvice.ensure_indexes()
            JournalEntry.ensure_indexes()
            
            logger.info("Database indexes have been created/updated")
        except Exception as e:
            logger.error(f"Error ensuring database indexes: {e}")
            raise
    
    def is_connected(self) -> bool:
        """Check if the database connection is active."""
        if not self.connection:
            return False
        try:
            # Ping the database to check connection
            self.connection.server_info()
            return True
        except:
            return False
    
    def cleanup_old_data(self) -> None:
        """Clean up old data based on configuration limits."""
        try:
            from .models import PersonalSituation, JournalEntry
            
            # Get limits from environment variables
            max_situations = int(os.getenv('MAX_SITUATIONS_HISTORY', '50'))
            max_entries = int(os.getenv('MAX_JOURNAL_ENTRIES', '100'))
            
            # Clean up old situations
            total_situations = PersonalSituation.objects.count()
            if total_situations > max_situations:
                # Keep the most recent situations
                old_situations = PersonalSituation.objects.order_by('-created_at')[max_situations:]
                for situation in old_situations:
                    # Also delete associated advice
                    AIAdvice.objects(situation=situation.id).delete()
                    situation.delete()
            
            # Clean up old journal entries
            total_entries = JournalEntry.objects.count()
            if total_entries > max_entries:
                # Keep the most recent entries
                old_entries = JournalEntry.objects.order_by('-created_at')[max_entries:]
                for entry in old_entries:
                    entry.delete()
            
            logger.info("Old data cleanup completed")
        except Exception as e:
            logger.error(f"Error during data cleanup: {e}")
            raise

def connect_to_mongodb():
    """Convenience function to connect to MongoDB."""
    db = DatabaseConnection()
    db.connect()
    db.ensure_indexes()
    return db
