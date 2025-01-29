import logging
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from telegram import Update
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

def format_message(text: str, max_length: Optional[int] = None) -> str:
    """Format message text to respect Telegram's message limits."""
    if not max_length:
        max_length = int(os.getenv('MAX_MESSAGE_LENGTH', '4096'))
    
    if len(text) <= max_length:
        return text
    
    # Split message while trying to maintain markdown formatting
    parts = []
    current_part = ""
    
    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part.strip())
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part.strip())
    
    return parts[0]  # Return first part, remaining parts could be sent separately if needed

def format_duration(delta: timedelta) -> str:
    """Format a timedelta into a human-readable string."""
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    parts = []
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if not parts:
        return "just now"
    
    return ", ".join(parts) + " ago"

def get_time_of_day_greeting() -> str:
    """Return an appropriate greeting based on the time of day."""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "Good morning"
    elif 12 <= hour < 17:
        return "Good afternoon"
    elif 17 <= hour < 22:
        return "Good evening"
    else:
        return "Hello"

def format_progress_data(data: Dict[str, Any], limit: int = 3) -> str:
    """Format progress data for display."""
    sections = []
    
    # Format mood trend
    if 'mood_trend' in data:
        mood = data['mood_trend']
        sections.append(
            "📊 Mood Trend\n"
            f"Status: {mood['trend'].title()}\n"
            f"Average: {mood['average']:.1f}/10\n"
            f"Change: {mood['change']:+.1f}"
        )
    
    # Format emotions
    if 'common_emotions' in data:
        emotions = list(data['common_emotions'].items())[:limit]
        sections.append(
            "😊 Common Emotions\n" +
            "\n".join(f"• {emotion}: {count} times" for emotion, count in emotions)
        )
    
    # Format topics
    if 'common_topics' in data:
        topics = list(data['common_topics'].items())[:limit]
        sections.append(
            "💭 Frequent Topics\n" +
            "\n".join(f"• {topic}: {count} times" for topic, count in topics)
        )
    
    # Format growth areas
    if 'growth_areas' in data:
        areas = data['growth_areas'][:limit]
        sections.append(
            "🌱 Growth Areas\n" +
            "\n".join(f"• {area['area']}\n  {area['suggestion']}" for area in areas)
        )
    
    return "\n\n".join(sections)

def get_reflection_prompt() -> str:
    """Generate a random reflection prompt for journaling."""
    prompts = [
        "What made you smile today? 😊",
        "What's something you learned about yourself recently? 🤔",
        "What's a challenge you're facing, and how are you handling it? 💪",
        "What are you grateful for today? 🙏",
        "What's something you'd like to improve about yourself? 🎯",
        "How did you take care of yourself today? 💝",
        "What's something you're looking forward to? 🌟",
        "What's a recent accomplishment you're proud of? 🏆",
        "How have your feelings evolved throughout the day? 🎭",
        "What's something that challenged your perspective recently? 🤯"
    ]
    
    from random import choice
    return choice(prompts)

def parse_time(time_str: str) -> Optional[datetime]:
    """Parse time string in HH:MM format."""
    try:
        hour, minute = map(int, time_str.split(':'))
        now = datetime.now()
        return now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    except (ValueError, TypeError):
        return None

def should_send_reflection_reminder() -> bool:
    """Check if it's time to send a daily reflection reminder."""
    reminder_time = os.getenv('DAILY_REFLECTION_TIME', '21:00')
    target_time = parse_time(reminder_time)
    
    if not target_time:
        return False
    
    now = datetime.now()
    time_diff = abs((now - target_time).total_seconds())
    
    # Return True if within 5 minutes of target time
    return time_diff <= 300

async def send_paginated_message(update: Update, text: str) -> None:
    """Send a long message in multiple parts if needed."""
    max_length = int(os.getenv('MAX_MESSAGE_LENGTH', '4096'))
    
    if len(text) <= max_length:
        await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        return
    
    parts = []
    current_part = ""
    
    for line in text.split('\n'):
        if len(current_part) + len(line) + 1 <= max_length:
            current_part += line + '\n'
        else:
            if current_part:
                parts.append(current_part)
            current_part = line + '\n'
    
    if current_part:
        parts.append(current_part)
    
    for i, part in enumerate(parts, 1):
        header = f"(Part {i}/{len(parts)})\n" if len(parts) > 1 else ""
        await update.message.reply_text(
            header + part,
            parse_mode=ParseMode.MARKDOWN
        )
