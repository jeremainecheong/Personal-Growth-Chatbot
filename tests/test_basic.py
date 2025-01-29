import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
from mongoengine import connect, disconnect

from src.database.models import User, PersonalSituation, JournalEntry, AIAdvice
from src.ai.analyzer import ConflictAnalyzer
from src.utils.helpers import (
    format_duration,
    get_time_of_day_greeting,
    format_progress_data,
    get_reflection_prompt,
    parse_time,
    should_send_reflection_reminder
)

# Setup / Teardown
@pytest.fixture(autouse=True)
def setup_database():
    """Setup test database connection."""
    disconnect()  # Disconnect any existing connections
    connect('mongoenginetest', host='mongomock://localhost')
    yield
    disconnect()

@pytest.fixture
def mock_user():
    """Create a test user."""
    user = User(telegram_id=123456789).save()
    yield user
    user.delete()

@pytest.fixture
def mock_situation(mock_user):
    """Create a test situation."""
    situation = PersonalSituation(
        user=mock_user.telegram_id,
        topic="Test Topic",
        situation="Test situation description",
        desired_outcome="Test desired outcome",
        emotions=["Happy 😊", "Excited 🎉"],
        mood_rating=8
    ).save()
    yield situation
    situation.delete()

@pytest.fixture
def mock_journal_entry(mock_user):
    """Create a test journal entry."""
    entry = JournalEntry(
        user=mock_user.telegram_id,
        content="Test journal entry",
        mood_rating=7,
        tags=["Personal Growth 🌱"]
    ).save()
    yield entry
    entry.delete()

# Test Database Models
def test_user_creation(mock_user):
    """Test user creation and retrieval."""
    assert mock_user.telegram_id == 123456789
    assert mock_user.created_at is not None
    assert mock_user.last_active is not None

def test_situation_creation(mock_situation):
    """Test situation creation and retrieval."""
    assert mock_situation.topic == "Test Topic"
    assert len(mock_situation.emotions) == 2
    assert mock_situation.mood_rating == 8

def test_journal_entry_creation(mock_journal_entry):
    """Test journal entry creation and retrieval."""
    assert mock_journal_entry.content == "Test journal entry"
    assert mock_journal_entry.mood_rating == 7
    assert len(mock_journal_entry.tags) == 1

# Test AI Analyzer
@patch('openai.OpenAI')
def test_analyzer_initialization(mock_openai):
    """Test AI analyzer initialization."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key'}):
        analyzer = ConflictAnalyzer()
        assert analyzer.client is not None

@patch('src.ai.analyzer.ConflictAnalyzer._prepare_analysis_prompt')
@patch('src.ai.analyzer.ConflictAnalyzer._save_advice')
def test_analyze_situation(mock_save_advice, mock_prepare_prompt, mock_situation):
    """Test situation analysis."""
    analyzer = ConflictAnalyzer()
    mock_prepare_prompt.return_value = "Test prompt"
    
    with patch.object(analyzer.client.chat.completions, 'create') as mock_create:
        mock_create.return_value.choices[0].message.content = "Test advice"
        advice = analyzer.analyze_situation(mock_situation)
        assert advice == "Test advice"
        mock_save_advice.assert_called_once()

# Test Helper Functions
def test_format_duration():
    """Test duration formatting."""
    delta = timedelta(days=1, hours=2, minutes=30)
    formatted = format_duration(delta)
    assert "1 day" in formatted
    assert "2 hours" in formatted
    assert "30 minutes" in formatted

def test_get_time_of_day_greeting():
    """Test time-based greeting."""
    greeting = get_time_of_day_greeting()
    assert isinstance(greeting, str)
    assert len(greeting) > 0

def test_format_progress_data():
    """Test progress data formatting."""
    test_data = {
        'mood_trend': {
            'trend': 'improving',
            'average': 7.5,
            'change': 0.5
        },
        'common_emotions': {
            'Happy 😊': 3,
            'Excited 🎉': 2
        },
        'common_topics': {
            'Work': 2,
            'Personal': 1
        },
        'growth_areas': [
            {
                'area': 'Test Area',
                'suggestion': 'Test Suggestion'
            }
        ]
    }
    
    formatted = format_progress_data(test_data)
    assert '📊 Mood Trend' in formatted
    assert 'Happy 😊: 3' in formatted
    assert 'Work: 2' in formatted
    assert 'Test Suggestion' in formatted

def test_get_reflection_prompt():
    """Test reflection prompt generation."""
    prompt = get_reflection_prompt()
    assert isinstance(prompt, str)
    assert '?' in prompt
    assert any(emoji in prompt for emoji in ['😊', '🤔', '💪', '🙏', '🎯'])

def test_parse_time():
    """Test time string parsing."""
    result = parse_time('14:30')
    assert isinstance(result, datetime)
    assert result.hour == 14
    assert result.minute == 30
    
    invalid_result = parse_time('invalid')
    assert invalid_result is None

@patch('src.utils.helpers.datetime')
def test_should_send_reflection_reminder(mock_datetime):
    """Test reflection reminder timing."""
    # Test when it's time for reminder
    mock_now = datetime.now().replace(hour=21, minute=0)
    mock_datetime.now.return_value = mock_now
    assert should_send_reflection_reminder() is True
    
    # Test when it's not time for reminder
    mock_now = datetime.now().replace(hour=15, minute=0)
    mock_datetime.now.return_value = mock_now
    assert should_send_reflection_reminder() is False
