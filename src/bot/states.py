from enum import Enum, auto

class ConversationState(Enum):
    """Enum for conversation states in the bot."""
    
    # Main flow states
    SELECTING_ACTION = auto()
    RECORDING_TOPIC = auto()
    RECORDING_SITUATION = auto()
    RECORDING_DESIRED_OUTCOME = auto()
    SELECTING_EMOTIONS = auto()
    RATING_MOOD = auto()
    CONFIRMING_SITUATION = auto()
    
    # Journal states
    WRITING_JOURNAL = auto()
    TAGGING_ENTRY = auto()
    
    # Resolution and reflection states
    RECORDING_RESOLUTION = auto()
    WRITING_REFLECTION = auto()
    RATING_ADVICE = auto()

# Predefined emotion options
EMOTION_OPTIONS = [
    "Anxious 😰",
    "Overwhelmed 😫",
    "Frustrated 😤",
    "Sad 😢",
    "Angry 😠",
    "Disappointed 😞",
    "Confused 😕",
    "Hopeful 🌟",
    "Motivated 💪",
    "Calm 😌"
]

# Main menu options
MENU_OPTIONS = [
    "Share a Situation 💭",
    "Write in Journal 📝",
    "View Progress 📊",
    "Get AI Advice 🤖",
    "Past Situations 📚",
    "Daily Reflection ✨"
]

# Mood rating descriptions
MOOD_RATINGS = {
    1: "Very Low 😢",
    2: "Low 😞",
    3: "Somewhat Low 😕",
    4: "Below Average 😐",
    5: "Neutral 😶",
    6: "Slightly Good 🙂",
    7: "Good 😊",
    8: "Very Good 😃",
    9: "Excellent 😄",
    10: "Amazing 🌟"
}
