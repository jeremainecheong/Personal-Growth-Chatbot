import logging
from datetime import datetime
from typing import Dict, Optional, List

from telegram import Update, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from database.models import User, PersonalSituation, AIAdvice, JournalEntry
from ai.analyzer import ConflictAnalyzer
from .keyboards import (
    get_main_menu_keyboard,
    get_emotions_keyboard,
    get_mood_rating_keyboard,
    get_confirmation_keyboard,
    get_rating_keyboard,
    get_journal_tags_keyboard
)
from .states import ConversationState, EMOTION_OPTIONS, MENU_OPTIONS, MOOD_RATINGS

logger = logging.getLogger(__name__)

# Initialize AI analyzer
analyzer = ConflictAnalyzer()

# User session storage
user_data: Dict[int, Dict] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and create user if needed."""
    user = update.message.from_user
    logger.info(f"User {user.id} started the bot")
    
    # Create or get user
    db_user = User.objects(telegram_id=user.id).first()
    if not db_user:
        db_user = User(telegram_id=user.id).save()
        welcome_text = (
            "Welcome to your Personal Growth Assistant! 🌟\n\n"
            "I'm here to help you navigate life's challenges, track your personal growth, "
            "and provide thoughtful advice for your situations.\n\n"
            "You can:\n"
            "• Share situations you'd like guidance on 💭\n"
            "• Keep a personal journal 📝\n"
            "• Track your progress over time 📊\n"
            "• Get AI-powered advice 🤖\n"
            "• Reflect on past experiences 📚\n\n"
            "What would you like to do?"
        )
    else:
        db_user.last_active = datetime.utcnow()
        db_user.save()
        welcome_text = "Welcome back! What would you like to do?"
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationState.SELECTING_ACTION

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = (
        "Here's how to use your Personal Growth Assistant:\n\n"
        "1. 💭 Share a Situation - Describe a situation you'd like guidance on\n"
        "2. 📝 Write in Journal - Record your thoughts and feelings\n"
        "3. 📊 View Progress - See your growth and patterns over time\n"
        "4. 🤖 Get AI Advice - Receive personalized guidance\n"
        "5. 📚 Past Situations - Review previous situations and outcomes\n"
        "6. ✨ Daily Reflection - Take time for self-reflection\n\n"
        "Commands:\n"
        "/start - Start/restart the bot\n"
        "/help - Show this help message\n"
        "/cancel - Cancel current operation"
    )
    await update.message.reply_text(help_text)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel and end the conversation."""
    user = update.message.from_user
    logger.info(f"User {user.id} canceled the conversation")
    
    await update.message.reply_text(
        "Operation cancelled. What would you like to do?",
        reply_markup=get_main_menu_keyboard()
    )
    
    # Clear any stored temporary data
    if user.id in user_data:
        user_data.pop(user.id)
    
    return ConversationState.SELECTING_ACTION

async def handle_menu_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle main menu selection."""
    user = update.message.from_user
    selection = update.message.text
    
    if selection == "Share a Situation 💭":
        await update.message.reply_text(
            "What's the main topic or theme of your situation?\n\n"
            "For example: 'Career Decision', 'Personal Growth', 'Life Change', etc."
        )
        return ConversationState.RECORDING_TOPIC
    
    elif selection == "Write in Journal 📝":
        await update.message.reply_text(
            "Write your journal entry below. You can share your thoughts, feelings, "
            "experiences, or reflections from your day."
        )
        return ConversationState.WRITING_JOURNAL
    
    elif selection == "View Progress 📊":
        return await handle_progress_view(update, context)
    
    elif selection == "Get AI Advice 🤖":
        # Show recent situations to get advice for
        situations = PersonalSituation.objects(
            user=user.id,
            resolved_at=None
        ).order_by('-created_at')[:5]
        
        if not situations:
            await update.message.reply_text(
                "You don't have any active situations to get advice for. "
                "Would you like to share a new situation?",
                reply_markup=get_main_menu_keyboard()
            )
            return ConversationState.SELECTING_ACTION
        
        keyboard = []
        for situation in situations:
            keyboard.append([InlineKeyboardButton(
                situation.topic,
                callback_data=f"advice_{situation.id}"
            )])
        
        await update.message.reply_text(
            "Which situation would you like advice for?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return ConversationState.SELECTING_ACTION
    
    elif selection == "Past Situations 📚":
        return await handle_past_situations(update, context)
    
    elif selection == "Daily Reflection ✨":
        await update.message.reply_text(
            "Take a moment to reflect on your day. How are you feeling right now?",
            reply_markup=get_mood_rating_keyboard()
        )
        return ConversationState.RATING_MOOD

async def handle_topic(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the topic input for a new situation."""
    user = update.message.from_user
    topic = update.message.text
    
    # Store topic in user data
    if user.id not in user_data:
        user_data[user.id] = {}
    user_data[user.id]['topic'] = topic
    
    await update.message.reply_text(
        "Please describe your situation in detail. What's happening? "
        "What are your thoughts and concerns about it?"
    )
    return ConversationState.RECORDING_SITUATION

async def handle_situation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the situation description."""
    user = update.message.from_user
    situation = update.message.text
    
    user_data[user.id]['situation'] = situation
    
    await update.message.reply_text(
        "What outcome would you like to achieve in this situation? "
        "What's your ideal resolution or goal?"
    )
    return ConversationState.RECORDING_DESIRED_OUTCOME

async def handle_desired_outcome(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the desired outcome input."""
    user = update.message.from_user
    desired_outcome = update.message.text
    
    user_data[user.id]['desired_outcome'] = desired_outcome
    
    await update.message.reply_text(
        "What emotions are you experiencing with this situation?",
        reply_markup=get_emotions_keyboard()
    )
    return ConversationState.SELECTING_EMOTIONS

async def handle_emotion_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle emotion selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if 'emotions' not in user_data[user_id]:
        user_data[user_id]['emotions'] = []
    
    if query.data == "emotions_done":
        if not user_data[user_id]['emotions']:
            await query.message.edit_text(
                "Please select at least one emotion.",
                reply_markup=get_emotions_keyboard()
            )
            return ConversationState.SELECTING_EMOTIONS
        
        await query.message.edit_text(
            "How would you rate your current mood (1-10)?",
            reply_markup=get_mood_rating_keyboard()
        )
        return ConversationState.RATING_MOOD
    
    emotion = next(e for e in EMOTION_OPTIONS if e.split()[0].lower() == query.data.split('_')[1])
    if emotion not in user_data[user_id]['emotions']:
        user_data[user_id]['emotions'].append(emotion)
    
    # Update message with selected emotions
    await query.message.edit_text(
        f"Selected emotions: {', '.join(user_data[user_id]['emotions'])}\n"
        "Select more or press Done when finished.",
        reply_markup=get_emotions_keyboard()
    )
    return ConversationState.SELECTING_EMOTIONS

async def handle_mood_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle mood rating selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    rating = int(query.data.split('_')[1])
    user_data[user_id]['mood_rating'] = rating
    
    # Prepare situation summary
    summary = (
        f"Topic: {user_data[user_id]['topic']}\n\n"
        f"Situation: {user_data[user_id]['situation']}\n\n"
        f"Desired Outcome: {user_data[user_id]['desired_outcome']}\n\n"
        f"Emotions: {', '.join(user_data[user_id]['emotions'])}\n"
        f"Current Mood: {rating}/10 - {MOOD_RATINGS[rating]}\n\n"
        "Would you like to save this situation and get advice?"
    )
    
    await query.message.edit_text(
        summary,
        reply_markup=get_confirmation_keyboard()
    )
    return ConversationState.CONFIRMING_SITUATION

async def handle_situation_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle situation confirmation and save to database."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if query.data == "confirm_yes":
        # Save situation to database
        situation = PersonalSituation(
            user=user_id,
            topic=user_data[user_id]['topic'],
            situation=user_data[user_id]['situation'],
            desired_outcome=user_data[user_id]['desired_outcome'],
            emotions=user_data[user_id]['emotions'],
            mood_rating=user_data[user_id]['mood_rating']
        ).save()
        
        # Generate and save AI advice
        advice = analyzer.analyze_situation(situation)
        
        await query.message.edit_text(
            f"I've saved your situation. Here's my advice:\n\n{advice}\n\n"
            "Was this advice helpful?",
            reply_markup=get_rating_keyboard()
        )
        return ConversationState.RATING_ADVICE
    
    else:  # User chose not to save
        await query.message.edit_text(
            "No problem. What would you like to do instead?",
            reply_markup=get_main_menu_keyboard()
        )
        user_data.pop(user_id, None)
        return ConversationState.SELECTING_ACTION

async def handle_advice_rating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the rating of AI advice."""
    query = update.callback_query
    await query.answer()
    
    was_helpful = query.data == "rate_helpful"
    user_id = query.from_user.id
    
    # Update the advice rating in database
    situation = PersonalSituation.objects(user=user_id).order_by('-created_at').first()
    if situation:
        advice = AIAdvice.objects(situation=situation.id).order_by('-created_at').first()
        if advice:
            advice.was_helpful = was_helpful
            advice.save()
    
    await query.message.edit_text(
        "Thank you for your feedback! What would you like to do next?",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationState.SELECTING_ACTION

async def handle_journal_entry(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle new journal entry."""
    user = update.message.from_user
    content = update.message.text
    
    if user.id not in user_data:
        user_data[user.id] = {}
    user_data[user.id]['journal_content'] = content
    
    await update.message.reply_text(
        "How would you rate your mood right now?",
        reply_markup=get_mood_rating_keyboard()
    )
    return ConversationState.RATING_MOOD

async def handle_journal_mood(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle mood rating for journal entry."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    rating = int(query.data.split('_')[1])
    user_data[user_id]['mood_rating'] = rating
    
    await query.message.edit_text(
        "Would you like to add any tags to your journal entry?",
        reply_markup=get_journal_tags_keyboard()
    )
    return ConversationState.TAGGING_ENTRY

async def handle_journal_tags(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle journal entry tags selection."""
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if 'tags' not in user_data[user_id]:
        user_data[user_id]['tags'] = []
    
    if query.data == "tags_done":
        # Save journal entry
        entry = JournalEntry(
            user=user_id,
            content=user_data[user_id]['journal_content'],
            mood_rating=user_data[user_id]['mood_rating'],
            tags=user_data[user_id]['tags']
        ).save()
        
        await query.message.edit_text(
            "Journal entry saved! What would you like to do next?",
            reply_markup=get_main_menu_keyboard()
        )
        user_data.pop(user_id, None)
        return ConversationState.SELECTING_ACTION
    
    tag = query.data.split('_')[1]
    if tag not in user_data[user_id]['tags']:
        user_data[user_id]['tags'].append(tag)
    
    await query.message.edit_text(
        f"Selected tags: {', '.join(user_data[user_id]['tags'])}\n"
        "Select more or press Done when finished.",
        reply_markup=get_journal_tags_keyboard()
    )
    return ConversationState.TAGGING_ENTRY

async def handle_progress_view(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle progress view request."""
    user_id = update.message.from_user.id
    
    # Get user's progress analysis
    progress = analyzer.analyze_patterns(user_id)
    
    if not progress:
        await update.message.reply_text(
            "I don't have enough data to show your progress yet. "
            "Continue sharing situations and writing in your journal to track your growth!",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationState.SELECTING_ACTION
    
    # Format progress report
    mood_trend = progress['mood_trend']
    report = (
        "📊 Your Progress Report\n\n"
        f"Mood Trend: {mood_trend['trend'].title()} "
        f"(Average: {mood_trend['average']}/10)\n\n"
        "Common Emotions:\n"
        f"{format_dict(progress['common_emotions'], limit=3)}\n\n"
        "Frequent Topics:\n"
        f"{format_dict(progress['common_topics'], limit=3)}\n\n"
        f"Resolution Rate: {progress['resolution_rate']:.1f}%\n"
        f"Journal Consistency: {progress['journal_consistency']:.1f} entries/month\n\n"
        "Growth Areas:\n"
    )
    
    for area in progress['growth_areas'][:3]:
        report += f"• {area['area']}: {area['suggestion']}\n"
    
    await update.message.reply_text(
        report,
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationState.SELECTING_ACTION

async def handle_past_situations(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle past situations view request."""
    user_id = update.message.from_user.id
    
    situations = PersonalSituation.objects(user=user_id).order_by('-created_at')[:5]
    
    if not situations:
        await update.message.reply_text(
            "You haven't shared any situations yet. Would you like to share one now?",
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationState.SELECTING_ACTION
    
    response = "Your Recent Situations:\n\n"
    for i, situation in enumerate(situations, 1):
        status = "✅ Resolved" if situation.resolved_at else "🔄 Active"
        response += (
            f"{i}. {situation.topic} ({status})\n"
            f"Created: {situation.created_at.strftime('%Y-%m-%d')}\n"
            f"Emotions: {', '.join(situation.emotions)}\n\n"
        )
    
    await update.message.reply_text(
        response,
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationState.SELECTING_ACTION

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the bot."""
    logger.error(f"Error: {context.error} caused by update: {update}")
    
    try:
        if update and update.message:
            await update.message.reply_text(
                "Sorry, something went wrong. Please try again or use /start to restart."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

def format_dict(d: Dict, limit: int = None) -> str:
    """Format dictionary items for display."""
    items = list(d.items())
    if limit:
        items = items[:limit]
    return "\n".join(f"• {k}: {v}" for k, v in items)
