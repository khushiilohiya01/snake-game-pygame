import pygame
import random
import sys
import os
import ctypes

pygame.init()

# ---------------- WINDOW ----------------
TOP_BAR = 90
GRID_SIZE = 25

DESIRED_WIDTH = 920
DESIRED_HEIGHT = 680


def get_work_area():
    user32 = ctypes.windll.user32
    SPI_GETWORKAREA = 48

    class RECT(ctypes.Structure):
        _fields_ = [
            ("left", ctypes.c_long),
            ("top", ctypes.c_long),
            ("right", ctypes.c_long),
            ("bottom", ctypes.c_long),
        ]

    rect = RECT()
    user32.SystemParametersInfoW(SPI_GETWORKAREA, 0, ctypes.byref(rect), 0)
    return rect.right - rect.left, rect.bottom - rect.top


usable_w, usable_h = get_work_area()

# Keep safe margins so the full window including title bar stays visible
WIDTH = min(DESIRED_WIDTH, usable_w - 40)
HEIGHT = min(DESIRED_HEIGHT, usable_h - 40)

# Snap width and playable height to grid
WIDTH = max(700, (WIDTH // GRID_SIZE) * GRID_SIZE)
HEIGHT = max(600, HEIGHT)
HEIGHT = TOP_BAR + (((HEIGHT - TOP_BAR) // GRID_SIZE) * GRID_SIZE)

PLAY_WIDTH = WIDTH
PLAY_HEIGHT = HEIGHT - TOP_BAR
GRID_WIDTH = PLAY_WIDTH // GRID_SIZE
GRID_HEIGHT = PLAY_HEIGHT // GRID_SIZE

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game")
clock = pygame.time.Clock()

# ---------------- COLORS ----------------
BG_COLOR = (10, 14, 24)
BG_ACCENT_1 = (18, 28, 44)
BG_ACCENT_2 = (12, 20, 34)

PANEL_COLOR = (22, 28, 44)
PLAYFIELD_BORDER = (40, 60, 92)
GRID_COLOR = (24, 34, 52)

TEXT_COLOR = (240, 245, 255)
SUBTEXT_COLOR = (165, 180, 205)

SNAKE_HEAD = (84, 255, 170)
SNAKE_HEAD_DARK = (30, 160, 100)
SNAKE_BODY = (38, 220, 142)
SNAKE_BODY_DARK = (22, 160, 102)

APPLE_RED = (240, 70, 85)
APPLE_DARK = (180, 35, 55)
APPLE_STEM = (90, 55, 30)
APPLE_LEAF = (55, 180, 90)

GOLD_FRUIT = (255, 215, 70)
GOLD_FRUIT_DARK = (220, 160, 20)
GOLD_GLOW = (255, 240, 140)

OBSTACLE_OUTER = (110, 125, 150)
OBSTACLE_INNER = (78, 92, 118)

GAME_OVER_COLOR = (255, 90, 90)
PAUSE_COLOR = (255, 220, 120)
GLOW_COLOR = (0, 190, 130)

# ---------------- FONTS ----------------
title_font = pygame.font.SysFont("arial", 50, bold=True)
big_font = pygame.font.SysFont("arial", 34, bold=True)
menu_font = pygame.font.SysFont("arial", 28, bold=True)
info_font = pygame.font.SysFont("arial", 22, bold=True)
small_font = pygame.font.SysFont("arial", 18)
tiny_font = pygame.font.SysFont("arial", 16)

# ---------------- FILE ----------------
HIGHSCORE_FILE = "highscore.txt"

# ---------------- HELPERS ----------------
def draw_text(text, font, color, x, y, center=False):
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surface, rect)


def draw_glow_text(text, font, main_color, glow_color, x, y, center=False):
    glow_surface = font.render(text, True, glow_color)
    main_surface = font.render(text, True, main_color)

    glow_rect = glow_surface.get_rect()
    main_rect = main_surface.get_rect()

    if center:
        glow_rect.center = (x, y)
        main_rect.center = (x, y)
    else:
        glow_rect.topleft = (x, y)
        main_rect.topleft = (x, y)

    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1)]:
        temp_rect = glow_rect.copy()
        temp_rect.x += dx
        temp_rect.y += dy
        screen.blit(glow_surface, temp_rect)

    screen.blit(main_surface, main_rect)


def load_highscore():
    if not os.path.exists(HIGHSCORE_FILE):
        with open(HIGHSCORE_FILE, "w") as f:
            f.write("0")
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except:
        return 0


def save_highscore(score):
    with open(HIGHSCORE_FILE, "w") as f:
        f.write(str(score))


def random_position(excluded):
    while True:
        pos = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        if pos not in excluded:
            return pos


def create_obstacles(snake, count):
    obstacles = []
    blocked = set(snake)

    while len(obstacles) < count:
        pos = (random.randint(2, GRID_WIDTH - 3), random.randint(2, GRID_HEIGHT - 3))
        if pos not in blocked:
            obstacles.append(pos)
            blocked.add(pos)

    return obstacles


# ---------------- BACKGROUND ----------------
def draw_background():
    screen.fill(BG_COLOR)

    pygame.draw.circle(screen, BG_ACCENT_1, (int(WIDTH * 0.14), int(HEIGHT * 0.18)), int(min(WIDTH, HEIGHT) * 0.19))
    pygame.draw.circle(screen, BG_ACCENT_2, (int(WIDTH * 0.86), int(HEIGHT * 0.20)), int(min(WIDTH, HEIGHT) * 0.23))
    pygame.draw.circle(screen, BG_ACCENT_1, (int(WIDTH * 0.20), int(HEIGHT * 0.92)), int(min(WIDTH, HEIGHT) * 0.25))
    pygame.draw.circle(screen, BG_ACCENT_2, (int(WIDTH * 0.90), int(HEIGHT * 0.88)), int(min(WIDTH, HEIGHT) * 0.18))


def draw_top_panel(score, highscore, difficulty, paused):
    panel_rect = pygame.Rect(0, 0, WIDTH, TOP_BAR)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect)
    pygame.draw.line(screen, PLAYFIELD_BORDER, (0, TOP_BAR - 1), (WIDTH, TOP_BAR - 1), 2)

    draw_text(f"Score: {score}", info_font, TEXT_COLOR, 20, 30)
    draw_text(f"High Score: {highscore}", info_font, TEXT_COLOR, 180, 30)
    draw_text(f"Difficulty: {difficulty}", info_font, TEXT_COLOR, 420, 30)
    draw_text("P = Pause", info_font, SUBTEXT_COLOR, WIDTH - 190, 30)

    if paused:
        draw_text("PAUSED", info_font, PAUSE_COLOR, WIDTH - 100, 30)


def draw_playfield_frame():
    rect = pygame.Rect(8, TOP_BAR + 8, WIDTH - 16, PLAY_HEIGHT - 16)
    pygame.draw.rect(screen, (14, 20, 34), rect, border_radius=20)
    pygame.draw.rect(screen, PLAYFIELD_BORDER, rect, width=2, border_radius=20)


def draw_grid():
    for x in range(0, PLAY_WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, TOP_BAR), (x, HEIGHT))
    for y in range(TOP_BAR, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))


# ---------------- DRAW OBSTACLES ----------------
def draw_obstacles(obstacles):
    for ox, oy in obstacles:
        x = ox * GRID_SIZE
        y = oy * GRID_SIZE + TOP_BAR

        outer = pygame.Rect(x + 2, y + 2, GRID_SIZE - 4, GRID_SIZE - 4)
        inner = pygame.Rect(x + 5, y + 5, GRID_SIZE - 10, GRID_SIZE - 10)

        pygame.draw.rect(screen, OBSTACLE_OUTER, outer, border_radius=7)
        pygame.draw.rect(screen, OBSTACLE_INNER, inner, border_radius=5)


# ---------------- DRAW SNAKE ----------------
def get_eye_positions(x, y, direction):
    if direction == (1, 0):
        return [(x + 17, y + 8), (x + 17, y + 17)]
    elif direction == (-1, 0):
        return [(x + 8, y + 8), (x + 8, y + 17)]
    elif direction == (0, -1):
        return [(x + 8, y + 8), (x + 17, y + 8)]
    else:
        return [(x + 8, y + 17), (x + 17, y + 17)]


def draw_snake(snake, direction):
    for i, (sx, sy) in enumerate(snake):
        x = sx * GRID_SIZE
        y = sy * GRID_SIZE + TOP_BAR

        if i == 0:
            head_rect = pygame.Rect(x + 1, y + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            pygame.draw.ellipse(screen, SNAKE_HEAD, head_rect)
            pygame.draw.ellipse(screen, SNAKE_HEAD_DARK, head_rect, 2)

            for ex, ey in get_eye_positions(x, y, direction):
                pygame.draw.circle(screen, (20, 24, 30), (ex, ey), 3)

            if direction == (1, 0):
                pygame.draw.line(screen, (255, 110, 140), (x + 24, y + 12), (x + 28, y + 12), 2)
            elif direction == (-1, 0):
                pygame.draw.line(screen, (255, 110, 140), (x + 1, y + 12), (x - 3, y + 12), 2)

        else:
            body_rect = pygame.Rect(x + 3, y + 3, GRID_SIZE - 6, GRID_SIZE - 6)
            pygame.draw.ellipse(screen, SNAKE_BODY, body_rect)
            pygame.draw.ellipse(screen, SNAKE_BODY_DARK, body_rect, 1)

            shine_rect = pygame.Rect(x + 7, y + 6, GRID_SIZE - 14, GRID_SIZE - 16)
            pygame.draw.ellipse(screen, (110, 255, 190), shine_rect)


# ---------------- DRAW FRUIT ----------------
def draw_apple(x, y):
    center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2 + 1)

    pygame.draw.circle(screen, APPLE_RED, (center[0] - 4, center[1]), 8)
    pygame.draw.circle(screen, APPLE_RED, (center[0] + 4, center[1]), 8)
    pygame.draw.circle(screen, APPLE_DARK, (center[0] - 4, center[1]), 8, 1)
    pygame.draw.circle(screen, APPLE_DARK, (center[0] + 4, center[1]), 8, 1)

    pygame.draw.circle(screen, (255, 150, 165), (center[0] - 6, center[1] - 4), 3)
    pygame.draw.line(screen, APPLE_STEM, (center[0], center[1] - 10), (center[0] + 1, center[1] - 16), 3)
    pygame.draw.ellipse(screen, APPLE_LEAF, (center[0] + 2, center[1] - 16, 8, 5))


def draw_gold_fruit(x, y, pulse):
    center = (x + GRID_SIZE // 2, y + GRID_SIZE // 2)

    if pulse:
        pygame.draw.circle(screen, GOLD_GLOW, center, 13, 2)

    pygame.draw.circle(screen, GOLD_FRUIT, center, 10)
    pygame.draw.circle(screen, GOLD_FRUIT_DARK, center, 10, 2)

    pygame.draw.line(screen, APPLE_STEM, (center[0], center[1] - 10), (center[0], center[1] - 15), 3)
    pygame.draw.ellipse(screen, (255, 235, 120), (center[0] - 4, center[1] - 18, 10, 6))
    pygame.draw.circle(screen, (255, 245, 190), (center[0] - 4, center[1] - 4), 3)


def draw_food(food_pos, food_type, frame_count):
    x = food_pos[0] * GRID_SIZE
    y = food_pos[1] * GRID_SIZE + TOP_BAR

    if food_type == "gold":
        pulse = (frame_count // 8) % 2 == 0
        draw_gold_fruit(x, y, pulse)
    else:
        draw_apple(x, y)


# ---------------- ANIMATIONS ----------------
def show_countdown():
    for num in ["3", "2", "1", "GO!"]:
        start_ticks = pygame.time.get_ticks()
        while pygame.time.get_ticks() - start_ticks < 650:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            draw_background()
            draw_glow_text(num, title_font, TEXT_COLOR, GLOW_COLOR, WIDTH // 2, HEIGHT // 2, center=True)
            pygame.display.update()
            clock.tick(60)


def draw_pause_overlay():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 140))
    screen.blit(overlay, (0, 0))

    draw_text("PAUSED", big_font, PAUSE_COLOR, WIDTH // 2, HEIGHT // 2 - 25, center=True)
    draw_text("Press P to Resume", small_font, TEXT_COLOR, WIDTH // 2, HEIGHT // 2 + 20, center=True)


# ---------------- SCREENS ----------------
def show_start_screen():
    selected = 1
    options = [
        ("Easy", 8, 4),
        ("Medium", 12, 7),
        ("Hard", 16, 10)
    ]

    title_y = int(HEIGHT * 0.18)

    card_w = min(520, WIDTH - 100)
    card_h = 250
    card_x = WIDTH // 2 - card_w // 2
    card_y = int(HEIGHT * 0.30)

    controls_y1 = min(HEIGHT - 95, card_y + card_h + 35)
    controls_y2 = controls_y1 + 28
    controls_y3 = controls_y2 + 28

    while True:
        draw_background()

        draw_glow_text("SNAKE GAME", title_font, TEXT_COLOR, GLOW_COLOR, WIDTH // 2, title_y, center=True)

        card = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=22)
        pygame.draw.rect(screen, PLAYFIELD_BORDER, card, 2, border_radius=22)

        draw_text("Choose Difficulty", menu_font, TEXT_COLOR, WIDTH // 2, card_y + 42, center=True)

        for i, (name, speed, obstacle_count) in enumerate(options):
            color = SNAKE_HEAD if i == selected else TEXT_COLOR
            draw_text(
                f"{name}   |   Speed: {speed}   |   Obstacles: {obstacle_count}",
                info_font,
                color,
                WIDTH // 2,
                card_y + 100 + i * 55,
                center=True
            )

        draw_text("UP / DOWN = Select", small_font, SUBTEXT_COLOR, WIDTH // 2, controls_y1, center=True)
        draw_text("ENTER = Start", small_font, SUBTEXT_COLOR, WIDTH // 2, controls_y2, center=True)
        draw_text("ESC = Quit", small_font, SUBTEXT_COLOR, WIDTH // 2, controls_y3, center=True)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected]
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


def show_game_over(score, highscore, is_new_highscore):
    title_y = int(HEIGHT * 0.18)

    card_w = min(460, WIDTH - 100)
    card_h = 190
    card_x = WIDTH // 2 - card_w // 2
    card_y = int(HEIGHT * 0.32)

    controls_y1 = min(HEIGHT - 80, card_y + card_h + 38)
    controls_y2 = controls_y1 + 28

    while True:
        draw_background()

        draw_glow_text("GAME OVER", title_font, GAME_OVER_COLOR, (120, 30, 30), WIDTH // 2, title_y, center=True)

        card = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(screen, PANEL_COLOR, card, border_radius=20)
        pygame.draw.rect(screen, PLAYFIELD_BORDER, card, 2, border_radius=20)

        draw_text(f"Final Score: {score}", big_font, TEXT_COLOR, WIDTH // 2, card_y + 50, center=True)
        draw_text(f"High Score: {highscore}", menu_font, TEXT_COLOR, WIDTH // 2, card_y + 100, center=True)

        if is_new_highscore:
            draw_text("New High Score!", menu_font, GOLD_FRUIT, WIDTH // 2, card_y + 145, center=True)

        draw_text("Press R to Restart", small_font, SUBTEXT_COLOR, WIDTH // 2, controls_y1, center=True)
        draw_text("Press ESC to Quit", small_font, SUBTEXT_COLOR, WIDTH // 2, controls_y2, center=True)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()


# ---------------- GAME LOOP ----------------
def game_loop(difficulty_name, start_speed, obstacle_count):
    snake = [(8, 8), (7, 8), (6, 8)]
    direction = (1, 0)
    next_direction = direction

    highscore = load_highscore()
    score = 0
    is_new_highscore = False

    current_speed = start_speed
    paused = False
    frame_count = 0

    score_popups = []

    obstacles = create_obstacles(snake, obstacle_count)

    blocked_positions = set(snake) | set(obstacles)
    food_pos = random_position(blocked_positions)
    food_type = "normal"
    gold_timer = 0

    show_countdown()

    while True:
        clock.tick(current_speed if not paused else 10)
        frame_count += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != (0, 1):
                    next_direction = (0, -1)
                elif event.key == pygame.K_DOWN and direction != (0, -1):
                    next_direction = (0, 1)
                elif event.key == pygame.K_LEFT and direction != (1, 0):
                    next_direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and direction != (-1, 0):
                    next_direction = (1, 0)
                elif event.key == pygame.K_p:
                    paused = not paused

        if paused:
            draw_background()
            draw_top_panel(score, highscore, difficulty_name, paused)
            draw_playfield_frame()
            draw_grid()
            draw_obstacles(obstacles)
            draw_snake(snake, direction)
            draw_food(food_pos, food_type, frame_count)
            draw_pause_overlay()
            pygame.display.update()
            continue

        direction = next_direction
        head_x, head_y = snake[0]
        dx, dy = direction
        new_head = (head_x + dx, head_y + dy)

        if new_head[0] < 0 or new_head[0] >= GRID_WIDTH or new_head[1] < 0 or new_head[1] >= GRID_HEIGHT:
            if score > highscore:
                highscore = score
                save_highscore(highscore)
                is_new_highscore = True
            return score, highscore, is_new_highscore

        if new_head in snake or new_head in obstacles:
            if score > highscore:
                highscore = score
                save_highscore(highscore)
                is_new_highscore = True
            return score, highscore, is_new_highscore

        snake.insert(0, new_head)

        if new_head == food_pos:
            if food_type == "gold":
                score += 3
                score_popups.append([food_pos[0] * GRID_SIZE + 12, food_pos[1] * GRID_SIZE + TOP_BAR + 10, "+3", GOLD_FRUIT, 35])
            else:
                score += 1
                score_popups.append([food_pos[0] * GRID_SIZE + 12, food_pos[1] * GRID_SIZE + TOP_BAR + 10, "+1", APPLE_RED, 30])

            if score > highscore:
                highscore = score
                save_highscore(highscore)

            current_speed = min(current_speed + 0.25, 24)

            blocked_positions = set(snake) | set(obstacles)
            food_pos = random_position(blocked_positions)

            if random.random() < 0.2:
                food_type = "gold"
                gold_timer = 35
            else:
                food_type = "normal"
                gold_timer = 0
        else:
            snake.pop()

        if food_type == "gold":
            gold_timer -= 1
            if gold_timer <= 0:
                blocked_positions = set(snake) | set(obstacles)
                food_pos = random_position(blocked_positions)
                food_type = "normal"

        draw_background()
        draw_top_panel(score, highscore, difficulty_name, paused)
        draw_playfield_frame()
        draw_grid()
        draw_obstacles(obstacles)
        draw_food(food_pos, food_type, frame_count)
        draw_snake(snake, direction)

        if food_type == "gold":
            draw_text("Golden Fruit = +3", tiny_font, GOLD_FRUIT, WIDTH - 170, 62)

        for popup in score_popups[:]:
            x, y, text, color, life = popup
            draw_text(text, small_font, color, x, y, center=True)
            popup[1] -= 1
            popup[4] -= 1
            if popup[4] <= 0:
                score_popups.remove(popup)

        pygame.display.update()


# ---------------- MAIN ----------------
def main():
    while True:
        difficulty_name, speed, obstacle_count = show_start_screen()
        final_score, highscore, is_new_highscore = game_loop(difficulty_name, speed, obstacle_count)
        show_game_over(final_score, highscore, is_new_highscore)


if __name__ == "__main__":
    main()