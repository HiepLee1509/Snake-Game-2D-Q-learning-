import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
pygame.font.init()

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# --- CONFIGS & THEME ---
BLOCK_SIZE = 10
SPEED_TRAIN = 10000 # Tăng tốc độ train tối đa
SPEED_DEMO = 20
GRID_W = 20
GRID_H = 20
NUM_ENVS = 16
COLS = 4
ROWS = 4

# Base resolution
BASE_GAME_W = GRID_W * BLOCK_SIZE
BASE_GAME_H = GRID_H * BLOCK_SIZE
BASE_WIDTH = BASE_GAME_W * COLS
BASE_HEIGHT = BASE_GAME_H * ROWS + 50 # Tăng footer lên 50px

# --- MODERN COLOR PALETTE ---
class Theme:
    BG_DARK     = (18, 18, 24)       # Nền tối
    GRID_LINE   = (40, 40, 50)       # Đường kẻ lưới mờ
    SNAKE_HEAD  = (0, 255, 150)      # Xanh Neon sáng
    SNAKE_BODY  = (0, 180, 100)      # Xanh dịu hơn
    FOOD_OUTER  = (255, 80, 80)      # Đỏ cam
    FOOD_INNER  = (255, 200, 200)    # Đỏ nhạt tâm
    TEXT_MAIN   = (240, 240, 240)    # Trắng sữa
    TEXT_SUB    = (150, 150, 160)    # Xám
    ACCENT      = (255, 215, 0)      # Vàng Gold (cho High Score)
    
    # Button Colors
    BTN_DEFAULT = (50, 50, 65)
    BTN_HOVER   = (70, 70, 90)
    BTN_TEXT    = (255, 255, 255)
    BTN_RESET   = (180, 60, 60)
    BTN_RESET_H = (200, 80, 80)

# Fonts
try:
    font_main = pygame.font.SysFont('consolas', 14, bold=True)
    font_title = pygame.font.SysFont('consolas', 28, bold=True)
    font_btn = pygame.font.SysFont('arial', 18, bold=True)
except:
    font_main = pygame.font.SysFont('arial', 14)
    font_title = pygame.font.SysFont('arial', 28)
    font_btn = pygame.font.SysFont('arial', 18)

class SingleGame:
    """Logic cốt lõi (Giữ nguyên)"""
    def __init__(self, w=BASE_GAME_W, h=BASE_GAME_H):
        self.w = w
        self.h = h
        self.reset()

    def reset(self):
        self.direction = Direction.RIGHT
        self.head = Point(self.w/2, self.h/2)
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y), 
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0
        return self

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.frame_iteration += 1
        self._move(action)
        self.snake.insert(0, self.head)
        
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            reward = -0.1
            self.snake.pop()
        
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None: pt = self.head
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        if pt in self.snake[1:]:
            return True
        return False

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)
        if np.array_equal(action, [1, 0, 0]): new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]): new_dir = clock_wise[(idx + 1) % 4]
        else: new_dir = clock_wise[(idx - 1) % 4]
        self.direction = new_dir
        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT: x += BLOCK_SIZE
        elif self.direction == Direction.LEFT: x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN: y += BLOCK_SIZE
        elif self.direction == Direction.UP: y -= BLOCK_SIZE
        self.head = Point(x, y)

# --- HELPER UI CLASS ---
class UIRenderer:
    @staticmethod
    def draw_grid(surface, w, h, block_size, offset_x=0, offset_y=0):
        # Vẽ lưới mờ
        for x in range(0, w, block_size):
            pygame.draw.line(surface, Theme.GRID_LINE, (offset_x + x, offset_y), (offset_x + x, offset_y + h))
        for y in range(0, h, block_size):
            pygame.draw.line(surface, Theme.GRID_LINE, (offset_x, offset_y + y), (offset_x + w, offset_y + y))
        # Vẽ khung viền
        pygame.draw.rect(surface, Theme.GRID_LINE, (offset_x, offset_y, w, h), 1)

    @staticmethod
    def draw_game_elements(surface, game, offset_x=0, offset_y=0):
        # 1. Vẽ Rắn
        for i, pt in enumerate(game.snake):
            color = Theme.SNAKE_HEAD if i == 0 else Theme.SNAKE_BODY
            rect = pygame.Rect(offset_x + pt.x, offset_y + pt.y, BLOCK_SIZE, BLOCK_SIZE)
            
            # Bo góc mềm mại hơn (radius = 3)
            pygame.draw.rect(surface, color, rect, border_radius=3)
            
            # Vẽ mắt cho đầu rắn
            if i == 0: 
                eye_radius = 2
                # Tính vị trí mắt dựa trên hướng (đơn giản hóa là vẽ 2 chấm đen)
                center_x = offset_x + pt.x + BLOCK_SIZE // 2
                center_y = offset_y + pt.y + BLOCK_SIZE // 2
                pygame.draw.circle(surface, (0,0,0), (center_x, center_y), eye_radius)

        # 2. Vẽ Thức ăn (Dạng Orb tròn)
        center_food_x = offset_x + game.food.x + BLOCK_SIZE // 2
        center_food_y = offset_y + game.food.y + BLOCK_SIZE // 2
        pygame.draw.circle(surface, Theme.FOOD_OUTER, (center_food_x, center_food_y), BLOCK_SIZE // 2 - 1)
        pygame.draw.circle(surface, Theme.FOOD_INNER, (center_food_x, center_food_y), BLOCK_SIZE // 4)

    @staticmethod
    def draw_button(surface, rect, text, mouse_pos, is_reset=False):
        base_col = Theme.BTN_RESET if is_reset else Theme.BTN_DEFAULT
        hover_col = Theme.BTN_RESET_H if is_reset else Theme.BTN_HOVER
        
        color = hover_col if rect.collidepoint(mouse_pos) else base_col
        
        # Vẽ bóng (Shadow) nhẹ
        shadow_rect = pygame.Rect(rect.x, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(surface, (30,30,40), shadow_rect, border_radius=8)
        
        # Vẽ nút chính
        pygame.draw.rect(surface, color, rect, border_radius=8)
        
        # Vẽ text
        txt_surf = font_btn.render(text, True, Theme.BTN_TEXT)
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)

class VectorizedSnakeGame:
    def __init__(self):
        self.display = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Snake AI Training Cluster')
        self.canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.clock = pygame.time.Clock()
        self.games = [SingleGame(BASE_GAME_W, BASE_GAME_H) for _ in range(NUM_ENVS)]
        self.scores = [0] * NUM_ENVS
        self.high_scores = [0] * NUM_ENVS
        
        # Nút Stop thiết kế dài và đẹp hơn
        self.stop_btn_rect = pygame.Rect(BASE_WIDTH // 2 - 80, BASE_HEIGHT - 40, 160, 30)

    def _get_scaled_mouse_pos(self, mouse_pos):
        win_w, win_h = self.display.get_size()
        scale_x = win_w / BASE_WIDTH
        scale_y = win_h / BASE_HEIGHT
        return (mouse_pos[0] / scale_x, mouse_pos[1] / scale_y)

    def step_all(self, actions):
        stop_requested = False
        mouse_pos_virtual = (0,0)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); quit()
            if event.type == pygame.MOUSEMOTION:
                mouse_pos_virtual = self._get_scaled_mouse_pos(event.pos)
            if event.type == pygame.MOUSEBUTTONDOWN:
                real_mouse_pos = self._get_scaled_mouse_pos(event.pos)
                if self.stop_btn_rect.collidepoint(real_mouse_pos):
                    stop_requested = True 

        rewards, dones, scores = [], [], []
        for i, game in enumerate(self.games):
            reward, done, score = game.play_step(actions[i])
            if score > self.high_scores[i]: self.high_scores[i] = score
            if done:
                game.reset()
                self.scores[i] = score
            rewards.append(reward)
            dones.append(done)
            scores.append(score)
            
        self._update_ui(mouse_pos_virtual)
        self.clock.tick(SPEED_TRAIN)
        return rewards, dones, scores, stop_requested

    def _update_ui(self, mouse_pos):
        self.canvas.fill(Theme.BG_DARK)
        
        # Vẽ các màn hình con
        for idx, game in enumerate(self.games):
            ox = (idx % COLS) * BASE_GAME_W
            oy = (idx // COLS) * BASE_GAME_H
            
            # Vẽ nền riêng cho từng ô game để tạo độ sâu
            # pygame.draw.rect(self.canvas, (25, 25, 35), (ox + 1, oy + 1, BASE_GAME_W - 2, BASE_GAME_H - 2))
            
            # Vẽ chi tiết game
            UIRenderer.draw_grid(self.canvas, BASE_GAME_W, BASE_GAME_H, BLOCK_SIZE, ox, oy)
            UIRenderer.draw_game_elements(self.canvas, game, ox, oy)
            
            # UI Text (Score)
            score_txt = font_main.render(f"{game.score}", True, Theme.TEXT_MAIN)
            hi_txt = font_main.render(f"H:{self.high_scores[idx]}", True, Theme.ACCENT)
            self.canvas.blit(score_txt, (ox + 4, oy + 2))
            self.canvas.blit(hi_txt, (ox + 35, oy + 2))

        # Footer Area
        pygame.draw.rect(self.canvas, (30,30,35), (0, BASE_HEIGHT - 50, BASE_WIDTH, 50))
        UIRenderer.draw_button(self.canvas, self.stop_btn_rect, "STOP & SAVE", mouse_pos, is_reset=True)

        scaled_surf = pygame.transform.scale(self.canvas, self.display.get_size())
        self.display.blit(scaled_surf, (0, 0))
        pygame.display.flip()

class DemoGame:
    def __init__(self):
        self.base_w = BASE_GAME_W
        self.base_h = BASE_GAME_H
        self.display = pygame.display.set_mode((self.base_w * 2, self.base_h * 2), pygame.RESIZABLE)
        pygame.display.set_caption('AI Demonstration Mode')
        self.canvas = pygame.Surface((self.base_w, self.base_h))
        self.clock = pygame.time.Clock()
        self.game = SingleGame(self.base_w, self.base_h)
        
    def step(self, action):
        stop_demo = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT: stop_demo = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE: stop_demo = True

        reward, done, score = self.game.play_step(action)
        if done: self.game.reset()
            
        self._update_ui()
        self.clock.tick(SPEED_DEMO)
        return stop_demo

    def _update_ui(self):
        self.canvas.fill(Theme.BG_DARK)
        
        # Vẽ grid và game objects
        UIRenderer.draw_grid(self.canvas, self.base_w, self.base_h, BLOCK_SIZE)
        UIRenderer.draw_game_elements(self.canvas, self.game)
        
        # Score HUD đẹp hơn
        score_surf = font_main.render(f"SCORE: {self.game.score}", True, Theme.TEXT_MAIN)
        
        # Vẽ background mờ cho điểm số
        bg_score_rect = score_surf.get_rect(topleft=(5, 5))
        bg_score_rect.inflate_ip(10, 6)
        pygame.draw.rect(self.canvas, (0, 0, 0, 150), bg_score_rect, border_radius=5)
        self.canvas.blit(score_surf, (10, 8))
        
        scaled_surf = pygame.transform.scale(self.canvas, self.display.get_size())
        self.display.blit(scaled_surf, (0, 0))
        pygame.display.flip()

class MainMenu:
    def __init__(self):
        self.base_w, self.base_h = 400, 400 
        self.display = pygame.display.set_mode((self.base_w, self.base_h), pygame.RESIZABLE)
        pygame.display.set_caption('Snake Q-Learning Hub')
        self.canvas = pygame.Surface((self.base_w, self.base_h))
        
        # Layout nút bấm
        center_x = self.base_w // 2
        start_y = 120
        gap = 60
        w_btn, h_btn = 220, 45
        
        self.btn_train = pygame.Rect(center_x - w_btn//2, start_y, w_btn, h_btn)
        self.btn_demo  = pygame.Rect(center_x - w_btn//2, start_y + gap, w_btn, h_btn)
        self.btn_reset = pygame.Rect(center_x - w_btn//2, start_y + gap*2, w_btn, h_btn)
        self.btn_quit  = pygame.Rect(center_x - w_btn//2, start_y + gap*3, w_btn, h_btn)

    def _get_scaled_mouse_pos(self):
        mouse_pos = pygame.mouse.get_pos()
        win_w, win_h = self.display.get_size()
        scale_x = win_w / self.base_w
        scale_y = win_h / self.base_h
        return (mouse_pos[0] / scale_x, mouse_pos[1] / scale_y)

    def show(self):
        run = True
        while run:
            self.canvas.fill(Theme.BG_DARK)
            
            # Vẽ Title có bóng
            title_txt = "SNAKE AI LAB"
            title_shadow = font_title.render(title_txt, True, (0, 100, 50))
            title_main = font_title.render(title_txt, True, Theme.SNAKE_HEAD)
            
            title_rect = title_main.get_rect(center=(self.base_w//2, 60))
            self.canvas.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
            self.canvas.blit(title_main, title_rect)
            
            # Subtitle
            sub_txt = font_main.render("Q-Learning Implementation", True, Theme.TEXT_SUB)
            sub_rect = sub_txt.get_rect(center=(self.base_w//2, 90))
            self.canvas.blit(sub_txt, sub_rect)
            
            mouse_pos = self._get_scaled_mouse_pos()
            
            # Vẽ các nút sử dụng class UIRenderer
            UIRenderer.draw_button(self.canvas, self.btn_train, "START TRAINING (16x)", mouse_pos)
            UIRenderer.draw_button(self.canvas, self.btn_demo, "WATCH DEMO", mouse_pos)
            UIRenderer.draw_button(self.canvas, self.btn_reset, "RESET Q-TABLE", mouse_pos, is_reset=True)
            UIRenderer.draw_button(self.canvas, self.btn_quit, "EXIT", mouse_pos)
            
            scaled_surf = pygame.transform.scale(self.canvas, self.display.get_size())
            self.display.blit(scaled_surf, (0, 0))
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return "QUIT"
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.btn_train.collidepoint(mouse_pos): return "TRAIN"
                    if self.btn_demo.collidepoint(mouse_pos): return "DEMO"
                    if self.btn_reset.collidepoint(mouse_pos): return "RESET"
                    if self.btn_quit.collidepoint(mouse_pos): return "QUIT"