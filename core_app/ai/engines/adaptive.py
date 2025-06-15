import numpy as np
from collections import defaultdict

class AdaptiveEngine:
    def __init__(self):
        self.user_states = {}  # Stores user_id: {'skill_level': 0.5, 'progress': [...]}
        
    def calculate_difficulty(self, user_id):
        """Returns difficulty level between 0-1 based on user performance"""
        default_level = 0.5
        return self.user_states.get(user_id, {}).get('skill_level', default_level)
    
    def update_user_state(self, user_id, correct, response_time):
        """Updates user profile after each question"""
        if user_id not in self.user_states:
            self.user_states[user_id] = {'skill_level': 0.5, 'progress': []}
        
        # Simple adaptive logic - can replace with your Q-learning
        adjustment = 0.1 if correct else -0.05
        self.user_states[user_id]['skill_level'] = np.clip(
            self.user_states[user_id]['skill_level'] + adjustment,
            0.1,  # Minimum difficulty
            1.0    # Maximum difficulty
        )