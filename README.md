# Personal Growth Assistant Bot 🌱

A Telegram bot designed to help individuals navigate life's challenges, track personal growth, and receive AI-powered guidance. This bot serves as your personal companion for self-reflection, journaling, and getting actionable advice.

## Features

- 💭 **Situation Sharing**: Share personal situations and get AI-powered guidance
- 📝 **Personal Journal**: Keep track of your thoughts, feelings, and experiences
- 📊 **Progress Tracking**: Monitor your emotional trends and personal growth
- 🤖 **AI Advice**: Receive personalized, actionable suggestions
- 📚 **History Review**: Look back at past situations and their resolutions
- ✨ **Daily Reflections**: Regular prompts for self-reflection and mood tracking

## Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB
- OpenAI API key
- Telegram Bot token

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/personal-growth-assistant.git
cd personal-growth-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create and configure your environment variables:
```bash
cp .env.template .env
```

Edit `.env` with your configuration:
- Add your MongoDB connection URI
- Add your OpenAI API key
- Add your Telegram Bot token
- Adjust other settings as needed

4. Start the bot:
```bash
python src/main.py
```

## Deployment

### Deploying to Render

1. Fork this repository to your GitHub account

2. Create a new Web Service on Render:
   - Go to https://dashboard.render.com
   - Click "New +" and select "Web Service"
   - Connect your GitHub repository
   - Choose the repository you want to deploy

3. Configure the Web Service:
   - Name: Choose a name for your service
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python src/main.py`

4. Add Environment Variables:
   - Click on "Environment" tab
   - Add the following environment variables:
     ```
     MONGODB_URI=your_mongodb_uri
     OPENAI_API_KEY=your_openai_api_key
     TELEGRAM_BOT_TOKEN=your_telegram_bot_token
     RENDER=true
     ```
   Note: For MongoDB, consider using MongoDB Atlas for your database

5. Click "Create Web Service"

Your bot will be deployed and start running on Render. The service will automatically restart if it crashes and redeploy when you push changes to your repository.

## Usage

1. Start a chat with the bot on Telegram using `/start`
2. Choose from the available options:
   - Share a Situation 💭
   - Write in Journal 📝
   - View Progress 📊
   - Get AI Advice 🤖
   - Past Situations 📚
   - Daily Reflection ✨

3. Follow the bot's prompts to:
   - Describe situations you'd like guidance on
   - Record your thoughts and feelings
   - Track your mood and emotional state
   - Get personalized advice and suggestions
   - Review your progress over time

## Features in Detail

### Situation Sharing
- Share personal challenges or situations
- Specify desired outcomes
- Track emotions and mood
- Receive AI-generated advice

### Personal Journal
- Write daily reflections
- Add mood ratings
- Tag entries for better organization
- Track patterns over time

### Progress Tracking
- View emotional trends
- Monitor mood patterns
- Track resolution rates
- Identify growth areas

### AI Advice
- Get personalized guidance
- Receive actionable steps
- Learn coping strategies
- Get reflection prompts

## Configuration

The bot can be configured through environment variables:

```env
# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017/personal_growth_bot_db

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
DAILY_REFLECTION_TIME=21:00

# Application Configuration
MAX_SITUATIONS_HISTORY=50
MAX_JOURNAL_ENTRIES=100
ANALYSIS_WINDOW_DAYS=30
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the GPT API
- python-telegram-bot for the Telegram bot framework
- MongoDB for the database
- All contributors and users of this bot
