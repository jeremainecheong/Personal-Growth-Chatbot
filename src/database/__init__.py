# This file makes the database directory a Python package
from .connection import connect_to_mongodb
from .models import User, PersonalSituation, AIAdvice, JournalEntry
