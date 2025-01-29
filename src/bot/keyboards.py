from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from .states import EMOTION_OPTIONS, MENU_OPTIONS, MOOD_RATINGS

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Create the main menu keyboard."""
    keyboard = [[KeyboardButton(option)] for option in MENU_OPTIONS]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_emotions_keyboard() -> InlineKeyboardMarkup:
    """Create the emotions selection keyboard."""
    # Split emotions into rows of 2
    keyboard = []
    for i in range(0, len(EMOTION_OPTIONS), 2):
        row = []
        for emotion in EMOTION_OPTIONS[i:i+2]:
            row.append(InlineKeyboardButton(
                emotion,
                callback_data=f"emotion_{emotion.split()[0].lower()}"
            ))
        keyboard.append(row)
    
    # Add Done button at the bottom
    keyboard.append([InlineKeyboardButton("Done ✅", callback_data="emotions_done")])
    return InlineKeyboardMarkup(keyboard)

def get_mood_rating_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard for mood rating."""
    keyboard = []
    # Create rows of 2 buttons each
    for i in range(1, 11, 2):
        row = []
        for rating in range(i, min(i + 2, 11)):
            row.append(InlineKeyboardButton(
                f"{rating} - {MOOD_RATINGS[rating]}", 
                callback_data=f"mood_{rating}"
            ))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Create a confirmation keyboard with Yes/No options."""
    keyboard = [[
        InlineKeyboardButton("Yes ✅", callback_data="confirm_yes"),
        InlineKeyboardButton("No ❌", callback_data="confirm_no")
    ]]
    return InlineKeyboardMarkup(keyboard)

def get_rating_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard for rating AI advice."""
    keyboard = [[
        InlineKeyboardButton("Helpful 👍", callback_data="rate_helpful"),
        InlineKeyboardButton("Not Helpful 👎", callback_data="rate_not_helpful")
    ]]
    return InlineKeyboardMarkup(keyboard)

def get_journal_tags_keyboard() -> InlineKeyboardMarkup:
    """Create a keyboard for selecting journal entry tags."""
    tags = [
        "Personal Growth 🌱", "Reflection 🤔", "Achievement 🏆",
        "Challenge 💪", "Learning 📚", "Gratitude 🙏",
        "Goal Setting 🎯", "Self-Care 💝", "Breakthrough 💡"
    ]
    
    keyboard = []
    # Create rows of 3 buttons each
    for i in range(0, len(tags), 3):
        row = []
        for tag in tags[i:i+3]:
            row.append(InlineKeyboardButton(
                tag,
                callback_data=f"tag_{tag.split()[0].lower()}"
            ))
        keyboard.append(row)
    
    # Add Done button at the bottom
    keyboard.append([InlineKeyboardButton("Done ✅", callback_data="tags_done")])
    return InlineKeyboardMarkup(keyboard)
