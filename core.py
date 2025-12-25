# core.py
import random
import numpy as np
from collections import deque
from settings import Direction, Point, BLOCK_SIZE

class SingleGame:
    def __init__(self, w, h):
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
        
        # 1. Tính khoảng cách cũ
        old_dist = abs(self.food.x - self.head.x) + abs(self.food.y - self.head.y)

        # 2. Di chuyển
        self._move(action)
        self.snake.insert(0, self.head)
        
        reward = 0
        game_over = False
        
        # 3. Check va chạm hoặc đói chết
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -20 # Phạt nặng khi chết
            return reward, game_over, self.score

        # 4. Logic Thưởng/Phạt
        if self.head == self.food:
            self.score += 1
            reward = 20 # Thưởng lớn khi ăn
            self._place_food()
        else:
            new_dist = abs(self.food.x - self.head.x) + abs(self.food.y - self.head.y)
            
            # Thêm logic phạt ngõ cụt: Nếu đi vào ngõ cụt (kể cả chưa chết ngay) -> Phạt
            # Nhưng để tiết kiệm hiệu năng, ta để logic tránh ngõ cụt cho Agent xử lý qua State
            
            if new_dist < old_dist:
                reward = 1 
            else:
                reward = -2 
            
            self.snake.pop()
        
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None: pt = self.head
        # Hit wall
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Hit self
        if pt in self.snake[1:]:
            return True
        return False

    # --- TÍNH NĂNG MỚI: PHÁT HIỆN NGÕ CỤT (Flood Fill) ---
    # Use BFS to determine if moving to point pt will lead to a trap
    def is_trap(self, pt):
        """
        Kiểm tra xem đi vào điểm pt có bị kẹt không.
        Trả về True nếu vùng không gian tại pt nhỏ hơn chiều dài rắn (hoặc một ngưỡng an toàn).
        """
        # Nếu điểm đó là tường hoặc thân rắn thì coi như là trap luôn
        if self.is_collision(pt):
            return True

        # Bắt đầu Flood Fill (Loang)
        # Giới hạn tìm kiếm: Không cần loang hết bản đồ, chỉ cần loang đủ số bước = chiều dài rắn
        # Nếu tìm được số ô trống > chiều dài rắn thì an toàn.
        
        search_limit = len(self.snake) + 5 # Ngưỡng an toàn
        if search_limit > 100: search_limit = 100 # Cap lại để không bị lag game khi rắn quá dài
        
        queue = deque([pt])
        visited = {pt}
        count = 0
        
        # Chuyển thân rắn thành set để tra cứu O(1)
        snake_set = set(self.snake)

        while queue:
            curr = queue.popleft()
            count += 1
            if count > search_limit:
                return False # An toàn, không gian đủ rộng

            # Kiểm tra 4 hướng xung quanh
            neighbors = [
                Point(curr.x + BLOCK_SIZE, curr.y),
                Point(curr.x - BLOCK_SIZE, curr.y),
                Point(curr.x, curr.y + BLOCK_SIZE),
                Point(curr.x, curr.y - BLOCK_SIZE)
            ]

            for n in neighbors:
                if n not in visited:
                    # Kiểm tra biên map
                    if 0 <= n.x <= self.w - BLOCK_SIZE and 0 <= n.y <= self.h - BLOCK_SIZE:
                        # Kiểm tra va chạm thân rắn
                        if n not in snake_set:
                            visited.add(n)
                            queue.append(n)
        
        # Nếu chạy hết vòng lặp mà count vẫn <= search_limit -> Bị kẹt
        return True

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