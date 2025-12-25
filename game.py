# game.py
import pygame
from settings import *
from core import SingleGame
from ui import UIRenderer

class VectorizedSnakeGame:
    def __init__(self):
        self.display = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Snake AI Training Cluster')
        self.canvas = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
        self.clock = pygame.time.Clock()
        self.games = [SingleGame(BASE_GAME_W, BASE_GAME_H) for _ in range(NUM_ENVS)]
        self.scores = [0] * NUM_ENVS
        self.high_scores = [0] * NUM_ENVS
        
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
        
        for idx, game in enumerate(self.games):
            ox = (idx % COLS) * BASE_GAME_W
            oy = (idx // COLS) * BASE_GAME_H
            
            UIRenderer.draw_grid(self.canvas, BASE_GAME_W, BASE_GAME_H, BLOCK_SIZE, ox, oy)
            UIRenderer.draw_game_elements(self.canvas, game, ox, oy)
            
            score_txt = font_main.render(f"{game.score}", True, Theme.TEXT_MAIN)
            hi_txt = font_main.render(f"H:{self.high_scores[idx]}", True, Theme.ACCENT)
            self.canvas.blit(score_txt, (ox + 4, oy + 2))
            self.canvas.blit(hi_txt, (ox + 35, oy + 2))

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
        
        UIRenderer.draw_grid(self.canvas, self.base_w, self.base_h, BLOCK_SIZE)
        UIRenderer.draw_game_elements(self.canvas, self.game)
        
        score_surf = font_main.render(f"SCORE: {self.game.score}", True, Theme.TEXT_MAIN)
        bg_score_rect = score_surf.get_rect(topleft=(5, 5))
        bg_score_rect.inflate_ip(10, 6)
        pygame.draw.rect(self.canvas, (0, 0, 0, 150), bg_score_rect, border_radius=5)
        self.canvas.blit(score_surf, (10, 8))
        
        scaled_surf = pygame.transform.scale(self.canvas, self.display.get_size())
        self.display.blit(scaled_surf, (0, 0))
        pygame.display.flip()