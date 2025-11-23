import pygame
import sys
import random

# --- basic config ---
WIDTH, HEIGHT = 800, 400
FPS = 60

# lanes (top, middle, bottom)
LANE_Y = [
    HEIGHT // 4,      # top
    HEIGHT // 2,      # middle
    3 * HEIGHT // 4,  # bottom
]

PLAYER_X = 150
PLAYER_COLOR = (255, 215, 0)  # gold/yellow
PLAYER_SIZE = 25

SHAPES = ["circle", "square", "triangle"]


def draw_player(screen, lane_index, shape):
    y = LANE_Y[lane_index]
    size = PLAYER_SIZE

    if shape == "circle":
        pygame.draw.circle(screen, PLAYER_COLOR, (PLAYER_X, y), size)

    elif shape == "square":
        rect = pygame.Rect(PLAYER_X - size, y - size, size * 2, size * 2)
        pygame.draw.rect(screen, PLAYER_COLOR, rect)

    elif shape == "triangle":
        points = [
            (PLAYER_X, y - size),
            (PLAYER_X - size, y + size),
            (PLAYER_X + size, y + size),
        ]
        pygame.draw.polygon(screen, PLAYER_COLOR, points)


def draw_lanes(screen):
    lane_color = (60, 60, 60)
    for y in LANE_Y:
        pygame.draw.line(screen, lane_color, (0, y), (WIDTH, y), 1)


def make_new_obstacle():
    # choose which lane will have the shape-hole
    lane_with_hole = random.randint(0, 2)
    shape = random.choice(SHAPES)

    obstacle = {
        "x": WIDTH,
        "width": 120,
        "lane_index": lane_with_hole,
        "shape": shape,
        "counted": False,
    }
    return obstacle


def draw_obstacle(screen, obs):
    x = obs["x"]
    w = obs["width"]
    lane_index = obs["lane_index"]
    shape = obs["shape"]

    # draw full wall
    wall_rect = pygame.Rect(x, 0, w, HEIGHT)
    pygame.draw.rect(screen, (80, 80, 80), wall_rect)

    # cut out one hole at the chosen lane
    hole_color = (30, 30, 30)
    size = 30
    center_x = x + w // 2
    y = LANE_Y[lane_index]

    if shape == "circle":
        pygame.draw.circle(screen, hole_color, (center_x, y), size)
    elif shape == "square":
        rect = pygame.Rect(center_x - size, y - size, size * 2, size * 2)
        pygame.draw.rect(screen, hole_color, rect)
    elif shape == "triangle":
        points = [
            (center_x, y - size),
            (center_x - size, y + size),
            (center_x + size, y + size),
        ]
        pygame.draw.polygon(screen, hole_color, points)


def obstacle_hits_player(obs, player_lane, player_shape):
    x = obs["x"]
    w = obs["width"]
    center_x = x + w // 2

    # only check when obstacle overlaps the player's x
    if x <= PLAYER_X <= x + w:
        # must be in correct lane AND shape
        if obs["lane_index"] != player_lane:
            return True
        if obs["shape"] != player_shape:
            return True
    return False


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Shape-Shifter Lane Runner")

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 22)

    running = True

    # player state
    player_lane = 1          # start in middle lane (0=top,1=mid,2=bottom)
    player_shape = "circle"  # start as circle

    # obstacle
    obstacle = make_new_obstacle()
    OBSTACLE_SPEED = 5

    score = 0
    game_over = False

    while running:
        clock.tick(FPS)

        # ---------- EVENTS ----------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if not game_over:
                    # shape switching
                    if event.key == pygame.K_1:
                        player_shape = "circle"
                    elif event.key == pygame.K_2:
                        player_shape = "square"
                    elif event.key == pygame.K_3:
                        player_shape = "triangle"

                    # lane movement: up/down
                    if event.key in (pygame.K_w, pygame.K_UP):
                        player_lane = max(0, player_lane - 1)
                    elif event.key in (pygame.K_s, pygame.K_DOWN):
                        player_lane = min(2, player_lane + 1)

                # restart
                if game_over and event.key == pygame.K_r:
                    player_lane = 1
                    player_shape = "circle"
                    obstacle = make_new_obstacle()
                    score = 0
                    game_over = False

        # ---------- UPDATE ----------
        if not game_over:
            obstacle["x"] -= OBSTACLE_SPEED

            # collision check
            if obstacle_hits_player(obstacle, player_lane, player_shape):
                game_over = True

            # scoring: when obstacle center passes player and we matched lane+shape
            center_x = obstacle["x"] + obstacle["width"] // 2
            if not obstacle["counted"] and center_x < PLAYER_X:
                obstacle["counted"] = True
                if obstacle["lane_index"] == player_lane and obstacle["shape"] == player_shape:
                    score += 1

            # spawn new obstacle when off-screen
            if obstacle["x"] + obstacle["width"] < 0:
                obstacle = make_new_obstacle()

        # ---------- DRAW ----------
        screen.fill((30, 30, 30))

        draw_lanes(screen)
        draw_player(screen, player_lane, player_shape)
        draw_obstacle(screen, obstacle)

        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        instr1 = font.render("1=CIRCLE  2=SQUARE  3=TRIANGLE", True, (200, 200, 200))
        instr2 = font.render("W/UP=lane up  S/DOWN=lane down", True, (200, 200, 200))
        screen.blit(score_text, (20, 20))
        screen.blit(instr1, (20, 50))
        screen.blit(instr2, (20, 80))

        if game_over:
            go_text = font.render("GAME OVER - Press R to Restart", True, (255, 80, 80))
            rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
            screen.blit(go_text, rect)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
