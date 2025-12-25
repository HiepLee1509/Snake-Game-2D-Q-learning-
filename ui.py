# ui.py
import pygame
from settings import Theme, BLOCK_SIZE, font_btn, font_main, font_title

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
            pygame.draw.rect(surface, color, rect, border_radius=3)
            
            # Vẽ mắt cho đầu rắn
            if i == 0: 
                eye_radius = 2
                center_x = offset_x + pt.x + BLOCK_SIZE // 2
                center_y = offset_y + pt.y + BLOCK_SIZE // 2
                pygame.draw.circle(surface, (0,0,0), (center_x, center_y), eye_radius)

        # 2. Vẽ Thức ăn
        center_food_x = offset_x + game.food.x + BLOCK_SIZE // 2
        center_food_y = offset_y + game.food.y + BLOCK_SIZE // 2
        pygame.draw.circle(surface, Theme.FOOD_OUTER, (center_food_x, center_food_y), BLOCK_SIZE // 2 - 1)
        pygame.draw.circle(surface, Theme.FOOD_INNER, (center_food_x, center_food_y), BLOCK_SIZE // 4)

    @staticmethod
    def draw_button(surface, rect, text, mouse_pos, is_reset=False):
        base_col = Theme.BTN_RESET if is_reset else Theme.BTN_DEFAULT
        hover_col = Theme.BTN_RESET_H if is_reset else Theme.BTN_HOVER
        
        color = hover_col if rect.collidepoint(mouse_pos) else base_col
        
        # Vẽ bóng (Shadow)
        shadow_rect = pygame.Rect(rect.x, rect.y + 4, rect.width, rect.height)
        pygame.draw.rect(surface, (30,30,40), shadow_rect, border_radius=8)
        
        # Vẽ nút chính
        pygame.draw.rect(surface, color, rect, border_radius=8)
        
        # Vẽ text
        txt_surf = font_btn.render(text, True, Theme.BTN_TEXT)
        txt_rect = txt_surf.get_rect(center=rect.center)
        surface.blit(txt_surf, txt_rect)

class MainMenu:
    def __init__(self):
        self.base_w, self.base_h = 400, 400 
        self.display = pygame.display.set_mode((self.base_w, self.base_h), pygame.RESIZABLE)
        pygame.display.set_caption('Snake Q-Learning Hub')
        self.canvas = pygame.Surface((self.base_w, self.base_h))
        
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
            
            # Title
            title_txt = "SNAKE AI LAB"
            title_shadow = font_title.render(title_txt, True, (0, 100, 50))
            title_main = font_title.render(title_txt, True, Theme.SNAKE_HEAD)
            
            title_rect = title_main.get_rect(center=(self.base_w//2, 60))
            self.canvas.blit(title_shadow, (title_rect.x + 2, title_rect.y + 2))
            self.canvas.blit(title_main, title_rect)
            
            sub_txt = font_main.render("Q-Learning Implementation", True, Theme.TEXT_SUB)
            sub_rect = sub_txt.get_rect(center=(self.base_w//2, 90))
            self.canvas.blit(sub_txt, sub_rect)
            
            mouse_pos = self._get_scaled_mouse_pos()
            
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