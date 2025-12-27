import random
import numpy as np
import pickle
import os
from settings import Direction, Point, BLOCK_SIZE, NUM_ENVS
from game import VectorizedSnakeGame, DemoGame

# Hyperparameters
LR = 0.001 
GAMMA = 0.95
EPSILON_START = 80
DECAY_RATE = 0.05

class QTableAgent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 
        self.q_table = {} 
        self.load_table()
    #state = (danger, move
    def get_state(self, game):
        head = game.snake[0]
        
        # Calculate danger in all 4 directions
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        # is_trap function will return True if moving to that point leads to a trap
        is_danger_l = game.is_trap(point_l)
        is_danger_r = game.is_trap(point_r)
        is_danger_u = game.is_trap(point_u)
        is_danger_d = game.is_trap(point_d)

        state = [
            # Danger Straight
            (dir_r and is_danger_r) or 
            (dir_l and is_danger_l) or 
            (dir_u and is_danger_u) or 
            (dir_d and is_danger_d),

            # Danger Right
            (dir_u and is_danger_r) or 
            (dir_d and is_danger_l) or 
            (dir_l and is_danger_u) or 
            (dir_r and is_danger_d),

            # Danger Left
            (dir_d and is_danger_r) or 
            (dir_u and is_danger_l) or 
            (dir_r and is_danger_u) or 
            (dir_l and is_danger_d),
            
            # Move Direction
            dir_l, dir_r, dir_u, dir_d,
            
            # Food Location
            game.food.x < game.head.x, # Food Left
            game.food.x > game.head.x, # Food Right
            game.food.y < game.head.y, # Food Up
            game.food.y > game.head.y  # Food Down
        ]
        
        return tuple(map(int, state))

    # Get Q-values for a state, initialize if not present
    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0]
        return self.q_table[state]

    # Choose action based on epsilon-greedy policy
    def get_action(self, state, train_mode=True):
        final_move = [0, 0, 0]
        
        if train_mode:
            self.epsilon = max(1, EPSILON_START - self.n_games * DECAY_RATE)
        else:
            self.epsilon = 0
        
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            q_values = self.get_q_values(state)
            move = np.argmax(q_values)
            
        final_move[move] = 1
        return final_move

    # Train Q-value for a state-action pair
    def train_step(self, state, action, reward, next_state, done):
        action_idx = np.argmax(action)
        current_q = self.get_q_values(state)
        current_val = current_q[action_idx]
        
        if done:    #dead
            target = reward
        else:       #live
            next_q = self.get_q_values(next_state)
            max_next_q = np.max(next_q)
            # Q learning formula
            target = current_val + LR * (reward + GAMMA * max_next_q - current_val)

        self.q_table[state][action_idx] = target

    def save_table(self):
        print(f"Saving Q-Table with {len(self.q_table)} states...")
        with open("q_table.pkl", "wb") as f:
            data = {
                "q_table": self.q_table,
                "n_games": self.n_games
            }
            pickle.dump(data, f)

    def load_table(self):
        if os.path.exists("q_table.pkl"):
            with open("q_table.pkl", "rb") as f:
                try:
                    data = pickle.load(f)
                    if isinstance(data, dict) and "q_table" in data:
                        self.q_table = data["q_table"]
                        self.n_games = data["n_games"] # Khôi phục số ván
                        print(f"Loaded Q-Table and continued from game {self.n_games}.")
                    else:
                        # Hỗ trợ đọc file cũ (chỉ có q_table)
                        self.q_table = data
                        self.n_games = 0
                        print("Loaded old version Q-Table.")
                except:
                    print("Error loading Q-Table")

# --- Main Content ---
def run_training():
    """Chạy vòng lặp training 16 envs"""
    agent = QTableAgent()
    env = VectorizedSnakeGame()
    record = 0
    running = True
    while running:
        states_old = [agent.get_state(game) for game in env.games]
        final_moves = []
        for state in states_old:
            final_moves.append(agent.get_action(state, train_mode=True))
        rewards, dones, scores, stop_req = env.step_all(final_moves)
        if stop_req:
            agent.save_table()
            running = False
            continue
        states_new = [agent.get_state(game) for game in env.games]
        #
        for i in range(NUM_ENVS):
            agent.train_step(states_old[i], final_moves[i], rewards[i], states_new[i], dones[i])
            if dones[i]:
                agent.n_games += 1
                if scores[i] > record:
                    record = scores[i]
                    if record % 5 == 0: agent.save_table()

def run_demo():
    agent = QTableAgent()
    env = DemoGame()
    print("Starting Demo Mode...")
    while True:
        state = agent.get_state(env.game)
        action = agent.get_action(state, train_mode=False)
        stop_req = env.step(action)
        if stop_req:
            break

def clear_q_table():
    if os.path.exists("q_table.pkl"):
        os.remove("q_table.pkl")
        print("Data cleared! Training will start from scratch.")
    else:
        print("No data found to delete.")