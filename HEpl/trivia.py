import aiohttp
import random

class TriviaGame:
    def __init__(self, api_url):
        self.api_url = api_url
        self.questions = []
        self.current_question = None

    async def fetch_questions(self, category=None, difficulty=None, amount=1):
        params = {
            'amount': amount,
            'type': 'multiple'
        }
        if category:
            params['category'] = category
        if difficulty:
            params['difficulty'] = difficulty

        async with aiohttp.ClientSession() as session:
            async with session.get(self.api_url, params=params) as response:
                data = await response.json()
                self.questions = data['results']

    def get_next_question(self):
        if not self.questions:
            return None
        self.current_question = self.questions.pop(0)
        return self.current_question

    def check_answer(self, answer):
        if not self.current_question:
            return False
        return self.current_question['correct_answer'].lower() == answer.lower()
