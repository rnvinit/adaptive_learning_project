class QLearningEngine:
    def __init__(self):
        self.q_table = {}  # Format: {(user_state, question_type): q_values}
        
    def get_next_question(self, user_state):
        """Implements ε-greedy policy"""
        # Your Q-learning implementation here
        pass