import openai
from django.conf import settings

class AIContentGenerator:
    @staticmethod
    def generate_question(topic, difficulty):
        prompt = f"""Generate a {difficulty}-difficulty multiple choice question about {topic} with:
        - 1 correct answer
        - 3 incorrect but plausible options
        - Brief explanation (50 words)"""
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            api_key=settings.OPENAI_KEY
        )
        return response.choices[0].message.content