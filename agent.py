import random
import numpy as np
import pickle
import os
from game import VectorizedSnakeGame, DemoGame, Direction, Point, BLOCK_SIZE, NUM_ENVS

# Hyperparameters
LR = 0.1
GAMMA = 0.9
EPSILON_START = 80
DECAY_RATE = 0.05

class QTableAgent:
    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 
        self.q_table = {} 
        self.load_table()

    def get_state(self, game):
        # (Giữ nguyên code get_state như cũ của bạn)
        head = game.snake[0]
        point_l = Point(head.x - BLOCK_SIZE, head.y)
        point_r = Point(head.x + BLOCK_SIZE, head.y)
        point_u = Point(head.x, head.y - BLOCK_SIZE)
        point_d = Point(head.x, head.y + BLOCK_SIZE)
        
        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            dir_l, dir_r, dir_u, dir_d,
            
            game.food.x < game.head.x, 
            game.food.x > game.head.x, 
            game.food.y < game.head.y, 
            game.food.y > game.head.y
        ]
        return tuple(map(int, state))

    def get_q_values(self, state):
        if state not in self.q_table:
            self.q_table[state] = [0.0, 0.0, 0.0]
        return self.q_table[state]

    def get_action(self, state, train_mode=True):
        """Nếu train_mode=False, Epsilon = 0 (luôn chọn tốt nhất)"""
        final_move = [0, 0, 0]
        
        if train_mode:
            self.epsilon = max(1, EPSILON_START - self.n_games * DECAY_RATE)
        else:
            self.epsilon = 0 # Demo mode: No random
        
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
        else:
            q_values = self.get_q_values(state)
            move = np.argmax(q_values)
            
        final_move[move] = 1
        return final_move

    def train_step(self, state, action, reward, next_state, done):
        action_idx = np.argmax(action)
        current_q = self.get_q_values(state)
        current_val = current_q[action_idx]
        
        if done:
            target = reward
        else:
            next_q = self.get_q_values(next_state)
            max_next_q = np.max(next_q)
            target = current_val + LR * (reward + GAMMA * max_next_q - current_val)

        self.q_table[state][action_idx] = target

    def save_table(self):
        print(f"Saving Q-Table with {len(self.q_table)} states...")
        with open("q_table.pkl", "wb") as f:
            pickle.dump(self.q_table, f)

    def load_table(self):
        if os.path.exists("q_table.pkl"):
            with open("q_table.pkl", "rb") as f:
                self.q_table = pickle.load(f)
            print("Loaded Q-Table.")

# --- LOGIC ĐIỀU KHIỂN ---

def run_training():
    """Chạy vòng lặp training 16 envs"""
    agent = QTableAgent()
    env = VectorizedSnakeGame()
    record = 0
    
    running = True
    while running:
        states_old = [agent.get_state(game) for game in env.games]
        
        # Lấy actions (Batch)
        final_moves = []
        for state in states_old:
            final_moves.append(agent.get_action(state, train_mode=True))

        # Step
        rewards, dones, scores, stop_req = env.step_all(final_moves)
        
        # Nếu người dùng bấm STOP
        if stop_req:
            agent.save_table()
            running = False
            continue

        states_new = [agent.get_state(game) for game in env.games]

        # Train
        for i in range(NUM_ENVS):
            agent.train_step(states_old[i], final_moves[i], rewards[i], states_new[i], dones[i])
            if dones[i]:
                agent.n_games += 1
                if scores[i] > record:
                    record = scores[i]
                    # Auto save kỉ lục mới
                    if record % 5 == 0: agent.save_table()

def run_demo():
    """Chạy demo 1 env"""
    agent = QTableAgent() # Sẽ tự load table
    env = DemoGame()
    
    print("Starting Demo Mode...")
    while True:
        state = agent.get_state(env.game)
        action = agent.get_action(state, train_mode=False) # Pure exploitation
        
        stop_req = env.step(action)
        
        if stop_req:
            break

def clear_q_table():
    if os.path.exists("q_table.pkl"):
        os.remove("q_table.pkl")
        print("Data cleared! Training will start from scratch.")
    else:
        print("No data found to delete.")