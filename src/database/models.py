from datetime import datetime
from mongoengine import (
    Document, 
    LongField, 
    StringField, 
    DateTimeField, 
    ListField,
    BooleanField,
    IntField
)

class User(Document):
    """Represents a user in the system."""
    telegram_id = LongField(required=True, unique=True)
    created_at = DateTimeField(default=datetime.utcnow)
    last_active = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'users',
        'indexes': [
            {'fields': ['telegram_id']},
        ]
    }

    def __str__(self):
        return f"User({self.telegram_id})"

class PersonalSituation(Document):
    """Represents a personal situation or challenge."""
    user = LongField(required=True)  # telegram_id
    topic = StringField(required=True, max_length=255)
    situation = StringField(required=True)
    emotions = ListField(StringField(), default=list)
    desired_outcome = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    resolved_at = DateTimeField()
    resolution = StringField()
    reflection = StringField()
    mood_rating = IntField(min_value=1, max_value=10)
    
    meta = {
        'collection': 'personal_situations',
        'indexes': [
            {'fields': ['user']},
            {'fields': ['created_at']},
            {'fields': ['resolved_at']},
        ]
    }

    def __str__(self):
        return f"PersonalSituation({self.topic}, User: {self.user})"

class AIAdvice(Document):
    """Represents AI-generated advice for a personal situation."""
    situation = LongField(required=True)  # personal_situation_id
    advice = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    was_helpful = BooleanField()
    
    meta = {
        'collection': 'ai_advice',
        'indexes': [
            {'fields': ['situation']},
            {'fields': ['created_at']},
        ]
    }

    def __str__(self):
        return f"AIAdvice({self.situation}, helpful: {self.was_helpful})"

class JournalEntry(Document):
    """Represents a personal journal entry."""
    user = LongField(required=True)  # telegram_id
    content = StringField(required=True)
    mood_rating = IntField(min_value=1, max_value=10)
    created_at = DateTimeField(default=datetime.utcnow)
    tags = ListField(StringField(), default=list)
    
    meta = {
        'collection': 'journal_entries',
        'indexes': [
            {'fields': ['user']},
            {'fields': ['created_at']},
        ]
    }

    def __str__(self):
        return f"JournalEntry(User: {self.user}, Date: {self.created_at})"
