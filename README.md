# 🐍 Snake AI - Used Q-Learning algorithm

Dự án này là một hệ thống huấn luyện AI chơi game Rắn săn mồi (Snake Game) sử dụng thuật toán **Reinforcement Learning (Q-Learning)**. Điểm đặc biệt của dự án là khả năng **huấn luyện song song (Vectorized Training)** trên 16 môi trường cùng lúc để tăng tốc độ học, kết hợp với thuật toán **Flood Fill (BFS)** giúp AI phát hiện và tránh các ngõ cụt.

## ✨ Tính năng nổi bật

* **🧠 Q-Learning Agent:** AI tự học thông qua cơ chế Thưởng/Phạt (Reward/Penalty).
* **⚡ Vectorized Environment:** Chạy đồng thời **16 màn chơi** trên một cửa sổ, giúp AI thu thập dữ liệu nhanh gấp 16 lần so với cách huấn luyện đơn lẻ truyền thống.
* **🛡️ Trap Detection (Flood Fill):** Sử dụng thuật toán tìm kiếm theo chiều rộng (BFS) để "nhìn trước" không gian. AI có thể nhận biết được đường đi đó có dẫn vào ngõ cụt hoặc không gian kín hay không trước khi di chuyển.
* **💾 Auto Save/Load:** Tự động lưu bảng Q-Table (`q_table.pkl`) khi dừng huấn luyện và tải lại để học tiếp ở lần sau.
* **🎨 Giao diện trực quan:** Menu điều khiển, hiển thị điểm số (Score/High Score) thời gian thực, chế độ xem Demo tốc độ thường.

## 📂 Cấu trúc dự án

* **`main.py`**: File khởi chạy chính, quản lý Menu và chuyển đổi các chế độ.
* **`agent.py`**: Chứa class `QTableAgent` (thuật toán Q-Learning) và logic huấn luyện.
* **`core.py`**: Logic cốt lõi của game Rắn và thuật toán **Flood Fill (`is_trap`)**.
* **`game.py`**: Quản lý hiển thị đồ họa, xử lý môi trường huấn luyện song song (`VectorizedSnakeGame`) và chế độ Demo.
* **`ui.py`**: Các thành phần giao diện (Vẽ lưới, nút bấm, màu sắc).
* **`settings.py`**: Chứa các tham số cấu hình (Tốc độ, kích thước block, số lượng môi trường, màu sắc...).

## 🛠 Cài đặt & Yêu cầu hệ thống

Để chạy dự án, bạn cần cài đặt Python trên máy tính.

### 1. Cài đặt Python
Tải và cài đặt Python (phiên bản 3.8 trở lên) tại [python.org](https://www.python.org/).

### 2. Cài đặt thư viện phụ thuộc
Mở **Terminal** (trên Mac/Linux) hoặc **Command Prompt / PowerShell** (trên Windows) và chạy lệnh sau:

```bash
pip install -r requirements.txt
```

### 3. Chạy câu lệnh

```bash
python main.py
```

