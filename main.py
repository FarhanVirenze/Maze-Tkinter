import tkinter as tk
import random
import time

CELL_SIZE = 40

class Maze:
    def __init__(self, canvas, rows, cols, cell_size):
        self.canvas = canvas
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.map = []
        self.exit_x = self.exit_y = 0
        self.generate_maze()

    def generate_maze(self):
        self.map = [[1 for _ in range(self.cols)] for _ in range(self.rows)]

        def carve(x, y):
            self.map[y][x] = 0
            directions = [(2, 0), (-2, 0), (0, 2), (0, -2)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if 0 < nx < self.cols and 0 < ny < self.rows and self.map[ny][nx] == 1:
                    self.map[y + dy // 2][x + dx // 2] = 0
                    carve(nx, ny)

        carve(1, 1)
        self.start_x, self.start_y = 1, 1
        corners = [(1, 1), (1, self.rows - 2), (self.cols - 2, 1), (self.cols - 2, self.rows - 2)]
        self.exit_x, self.exit_y = random.choice(corners)
        self.map[self.exit_y][self.exit_x] = 2

        self.draw()

    def draw(self):
        self.canvas.delete("all")
        for y in range(self.rows):
            for x in range(self.cols):
                val = self.map[y][x]
                color = "white" if val == 0 else "black"
                if val == 2:
                    color = "red"
                self.canvas.create_rectangle(
                    x * self.cell_size, y * self.cell_size,
                    (x + 1) * self.cell_size, (y + 1) * self.cell_size,
                    fill=color, outline="gray"
                )

    def is_path(self, x, y):
        return 0 <= x < self.cols and 0 <= y < self.rows and self.map[y][x] in [0, 2]

    def is_exit(self, x, y):
        return x == self.exit_x and y == self.exit_y


class Player:
    def __init__(self, canvas, x, y, cell_size):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.cell_size = cell_size
        self.rect = canvas.create_oval(
            x * self.cell_size + 10, y * self.cell_size + 10,
            (x + 1) * self.cell_size - 10, (y + 1) * self.cell_size - 10,
            fill="blue"
        )

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.rect, dx * self.cell_size, dy * self.cell_size)

    def reset_position(self, x, y):
        self.canvas.coords(
            self.rect,
            x * self.cell_size + 10, y * self.cell_size + 10,
            (x + 1) * self.cell_size - 10, (y + 1) * self.cell_size - 10
        )
        self.x = x
        self.y = y


class Game:
    def __init__(self, root):
        self.root = root
        self.level = 1
        self.score = 0
        self.health = 3
        self.start_time = time.time()  # Timer starts when the game begins
        self.canvas = tk.Canvas(root, bg="white")
        self.canvas.pack()
        self.info_label = tk.Label(root, font=("Arial", 14))
        self.info_label.pack()
        self.restart_game()

        self.root.bind("<Up>", lambda e: self.move(0, -1))
        self.root.bind("<Down>", lambda e: self.move(0, 1))
        self.root.bind("<Left>", lambda e: self.move(-1, 0))
        self.root.bind("<Right>", lambda e: self.move(1, 0))

        self.update_timer()

    def restart_game(self):
        # Decrease CELL_SIZE with increasing level, making the maze smaller visually
        self.cell_size = max(30, 40 - self.level * 2)  # Decrease size, but don't go below 30
        rows = 9 + self.level * 2
        cols = 13 + self.level * 2
        rows = rows if rows % 2 == 1 else rows + 1
        cols = cols if cols % 2 == 1 else cols + 1

        width = cols * self.cell_size
        height = rows * self.cell_size
        self.canvas.config(width=width, height=height)

        self.maze = Maze(self.canvas, rows, cols, self.cell_size)
        self.player = Player(self.canvas, self.maze.start_x, self.maze.start_y, self.cell_size)
        self.update_info()

    def update_info(self):
        elapsed = int(time.time() - self.start_time)
        self.info_label.config(
            text=f"Level: {self.level} | Score: {self.score} | Health: {self.health} | Time: {elapsed}s"
        )

    def update_timer(self):
        self.update_info()
        self.root.after(1000, self.update_timer)

    def move(self, dx, dy):
        new_x = self.player.x + dx
        new_y = self.player.y + dy
        if self.maze.is_path(new_x, new_y):
            self.player.move(dx, dy)
            if self.maze.is_exit(new_x, new_y):
                self.score += 100 * self.level
                self.canvas.create_text(
                    self.canvas.winfo_width() // 2,
                    self.canvas.winfo_height() // 2,
                    text=f"Level {self.level} Complete!",
                    font=("Arial", 28), fill="green"
                )
                self.root.after(1500, self.next_level)
        else:
            self.health -= 1
            self.update_info()
            if self.health <= 0:
                self.game_over()

    def game_over(self):
        self.canvas.create_text(
            self.canvas.winfo_width() // 2,
            self.canvas.winfo_height() // 2,
            text="Game Over!",
            font=("Arial", 32), fill="red"
        )
        self.root.unbind("<Up>")
        self.root.unbind("<Down>")
        self.root.unbind("<Left>")
        self.root.unbind("<Right>")

        restart_button = tk.Button(self.root, text="Restart", font=("Arial", 14), command=self.restart_from_game_over)
        restart_button.pack(pady=10)

    def restart_from_game_over(self):
        self.level = 1
        self.score = 0
        self.health = 3
        self.start_time = time.time()  # Reset the timer
        self.canvas.delete("all")
        self.restart_game()
        self.update_info()

        # Remove the restart button and rebind keys
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Button):
                widget.destroy()

        self.root.bind("<Up>", lambda e: self.move(0, -1))
        self.root.bind("<Down>", lambda e: self.move(0, 1))
        self.root.bind("<Left>", lambda e: self.move(-1, 0))
        self.root.bind("<Right>", lambda e: self.move(1, 0))

    def next_level(self):
        self.level += 1
        self.start_time = time.time()  # Reset timer for next level
        self.restart_game()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Maze Runner - Level Challenge")
    game = Game(root)
    root.mainloop()
