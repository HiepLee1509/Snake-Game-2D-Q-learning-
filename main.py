from ui import MainMenu
from agent import run_training, run_demo, clear_q_table
import pygame

if __name__ == "__main__":
    menu = MainMenu()
    
    while True:
        mode = menu.show()
        
        if mode == "TRAIN":
            run_training()
        elif mode == "DEMO":
            run_demo()
        elif mode == "RESET":
            clear_q_table()
            # Sau khi xóa xong, vòng lặp while tiếp tục quay lại hiển thị Menu
        elif mode == "QUIT":
            break
            
    pygame.quit()