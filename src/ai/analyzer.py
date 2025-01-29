import logging
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
from typing import List, Dict, Optional
from database.models import PersonalSituation, AIAdvice, JournalEntry

logger = logging.getLogger(__name__)

class ConflictAnalyzer:
    """Handles AI analysis of conflicts and generation of advice."""

    def __init__(self):
        """Initialize the OpenAI client."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        self.client = OpenAI(api_key=api_key)

    def analyze_situation(self, situation: PersonalSituation) -> str:
        """Analyze a personal situation and generate advice."""
        try:
            # Get user's journal entries for context
            journal_entries = JournalEntry.objects(
                user=situation.user,
                created_at__gte=situation.created_at - timedelta(days=7)
            ).order_by('-created_at')
            
            # Prepare the context for the AI
            prompt = self._prepare_analysis_prompt(situation, journal_entries)
            
            # Generate response using GPT
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """You are a compassionate AI life coach 
                    specializing in personal growth and problem-solving. Provide empathetic, 
                    constructive, and actionable advice for individuals facing life challenges. 
                    Focus on self-improvement, emotional intelligence, and practical solutions."""},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            # Extract and save the advice
            advice = response.choices[0].message.content.strip()
            self._save_advice(situation, advice)
            
            return advice
        
        except Exception as e:
            logger.error(f"Error analyzing conflict: {e}")
            return "I apologize, but I'm having trouble analyzing this conflict right now. Please try again later."

    def analyze_patterns(self, user_id: int) -> Dict:
        """Analyze patterns and progress for a user."""
        try:
            # Get user's situations and journal entries
            situations = PersonalSituation.objects(user=user_id).order_by('-created_at')
            journal_entries = JournalEntry.objects(user=user_id).order_by('-created_at')
            
            # Extract relevant data
            topics = [s.topic for s in situations]
            emotions = [e for s in situations for e in s.emotions]
            mood_ratings = [e.mood_rating for e in journal_entries if e.mood_rating]
            
            # Calculate statistics
            topic_frequency = self._count_frequency(topics)
            emotion_frequency = self._count_frequency(emotions)
            resolution_rate = self._calculate_resolution_rate(situations)
            
            # Calculate mood trends
            mood_trend = self._calculate_mood_trend(mood_ratings)
            
            return {
                "common_topics": topic_frequency,
                "common_emotions": emotion_frequency,
                "resolution_rate": resolution_rate,
                "total_situations": len(situations),
                "mood_trend": mood_trend,
                "journal_consistency": len(journal_entries) / 30 if journal_entries else 0,  # Entries per month
                "growth_areas": self._identify_growth_areas(situations, journal_entries)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing patterns: {e}")
            return {}

    def _prepare_analysis_prompt(self, situation: PersonalSituation, journal_entries: List[JournalEntry]) -> str:
        """Prepare the prompt for AI analysis."""
        journal_context = "\n".join([
            f"Recent Journal Entry ({e.created_at.strftime('%Y-%m-%d')}): {e.content[:200]}..."
            for e in journal_entries[:3]
        ])
        
        return f"""
        Please analyze this personal situation and provide guidance:
        
        Topic: {situation.topic}
        Situation: {situation.situation}
        Desired Outcome: {situation.desired_outcome}
        Current Emotions: {', '.join(situation.emotions)}
        Mood Rating: {situation.mood_rating}/10
        
        Recent Journal Context:
        {journal_context}
        
        Please provide:
        1. Empathetic acknowledgment of the situation and emotions
        2. Personal insights and potential root causes to consider
        3. Specific, actionable steps for personal growth
        4. Coping strategies and self-care suggestions
        5. Reflection questions for deeper understanding
        6. A positive affirmation or motivation for moving forward
        """

    def _save_advice(self, situation: PersonalSituation, advice: str) -> None:
        """Save the generated advice to the database."""
        try:
            AIAdvice(
                situation=situation.id,
                advice=advice
            ).save()
        except Exception as e:
            logger.error(f"Error saving advice: {e}")

    @staticmethod
    def _count_frequency(items: List[str]) -> Dict[str, int]:
        """Count frequency of items in a list."""
        frequency = {}
        for item in items:
            frequency[item] = frequency.get(item, 0) + 1
        return dict(sorted(frequency.items(), key=lambda x: x[1], reverse=True))

    @staticmethod
    def _calculate_mood_trend(mood_ratings: List[int]) -> Dict:
        """Calculate trend in mood ratings."""
        if not mood_ratings:
            return {"trend": "neutral", "average": 0, "change": 0}
        
        avg = sum(mood_ratings) / len(mood_ratings)
        if len(mood_ratings) >= 2:
            recent_avg = sum(mood_ratings[:7]) / min(7, len(mood_ratings))
            older_avg = sum(mood_ratings[-7:]) / min(7, len(mood_ratings))
            change = recent_avg - older_avg
        else:
            change = 0
            
        return {
            "trend": "improving" if change > 0.5 else "declining" if change < -0.5 else "stable",
            "average": round(avg, 2),
            "change": round(change, 2)
        }
    
    @staticmethod
    def _calculate_resolution_rate(situations: List[PersonalSituation]) -> float:
        """Calculate the resolution rate of situations."""
        if not situations:
            return 0.0
        resolved = sum(1 for s in situations if s.resolved_at is not None)
        return (resolved / len(situations)) * 100
    
    @staticmethod
    def _identify_growth_areas(situations: List[PersonalSituation], 
                             journal_entries: List[JournalEntry]) -> List[Dict]:
        """Identify areas for personal growth based on patterns."""
        # Analyze recurring themes and challenges
        topics = [s.topic for s in situations]
        emotions = [e for s in situations for e in s.emotions]
        
        growth_areas = []
        
        # Check for emotional patterns
        emotion_freq = {}
        for emotion in emotions:
            emotion_freq[emotion] = emotion_freq.get(emotion, 0) + 1
        
        for emotion, count in emotion_freq.items():
            if count >= 3 and emotion in ["Anxious 😰", "Overwhelmed 😫", "Frustrated 😤"]:
                growth_areas.append({
                    "area": f"Emotional Management: {emotion}",
                    "frequency": count,
                    "suggestion": "Consider stress management techniques and emotional regulation strategies"
                })
        
        # Check for recurring situations
        topic_freq = {}
        for topic in topics:
            topic_freq[topic] = topic_freq.get(topic, 0) + 1
            
        for topic, count in topic_freq.items():
            if count >= 2:
                growth_areas.append({
                    "area": f"Recurring Challenge: {topic}",
                    "frequency": count,
                    "suggestion": "This might be a core area for focused personal development"
                })
        
        return growth_areas
