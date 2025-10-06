"""
Flappy Plane – Python + pygame (tanpa aset, bentuk sederhana)

Kontrol:
- Spasi/Klik: terbang
- R: restart

Menjalankan:
  python flappy.py

Catatan: butuh pygame
  pip install pygame
"""

import random
import sys

try:
    import pygame
except Exception as e:  # pragma: no cover
    print("Pygame belum terpasang. Instal dengan: pip install pygame")
    sys.exit(1)


W, H = 480, 640
GROUND_H = 60
SKY_H = H - GROUND_H

GRAVITY = 0.5
FLAP_VY = -8.5
PIPE_GAP = 140
PIPE_SPEED = 2.6
PIPE_INTERVAL_MS = 1500
MIN_PIPE_TOP = 60

BIRD_X = 100
BIRD_R = 16


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def circle_rect_collide(cx, cy, cr, rx, ry, rw, rh):
    nx = clamp(cx, rx, rx + rw)
    ny = clamp(cy, ry, ry + rh)
    dx = cx - nx
    dy = cy - ny
    return dx * dx + dy * dy <= cr * cr


def draw_text(surface, text, size, color, x, y, center=True):
    font = pygame.font.SysFont(None, size, bold=True)
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    surface.blit(surf, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((W, H))
    pygame.display.set_caption("Flappy Bird Clone (pygame)")
    clock = pygame.time.Clock()

    # Colors
    SKY1 = (135, 206, 235)
    SKY2 = (191, 231, 255)
    # Buildings & ground palette
    BUILD = (82, 109, 130)
    BUILD_D = (64, 92, 115)
    WINDOW = (230, 240, 255)
    GROUND = (160, 82, 45)
    GROUND_TICK = (193, 143, 90)

    # Plane palette
    PLANE_BODY = (223, 230, 233)
    PLANE_OUTLINE = (99, 110, 114)
    PLANE_WING = (231, 76, 60)
    PLANE_WING_D = (192, 57, 43)

    # Game state
    state = 'ready'  # ready | running | gameover
    score = 0
    best = 0
    bird_y = SKY_H // 2
    bird_vy = 0.0
    pipes = []  # list of dicts: {x, top, gap, scored}

    SPAWN = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN, PIPE_INTERVAL_MS)

    def reset():
        nonlocal state, score, bird_y, bird_vy, pipes
        state = 'ready'
        score = 0
        bird_y = SKY_H // 2
        bird_vy = 0.0
        pipes = []

    def start():
        nonlocal state, score, bird_y, bird_vy, pipes
        state = 'running'
        score = 0
        bird_y = SKY_H // 2
        bird_vy = 0.0
        pipes = []

    def flap():
        nonlocal state, bird_vy
        if state == 'ready':
            start()
        elif state == 'running':
            bird_vy = FLAP_VY
        elif state == 'gameover':
            reset()

    def spawn_pipe():
        max_top = SKY_H - PIPE_GAP - MIN_PIPE_TOP
        top = random.randint(MIN_PIPE_TOP, max_top)
        pipes.append({"x": W + 40, "top": top, "gap": PIPE_GAP, "scored": False})

    def game_over():
        nonlocal state
        state = 'gameover'

    gradient = pygame.Surface((1, SKY_H))
    for y in range(SKY_H):
        t = y / max(1, SKY_H - 1)
        r = int(SKY1[0] * (1 - t) + SKY2[0] * t)
        g = int(SKY1[1] * (1 - t) + SKY2[1] * t)
        b = int(SKY1[2] * (1 - t) + SKY2[2] * t)
        gradient.set_at((0, y), (r, g, b))
    gradient = pygame.transform.scale(gradient, (W, SKY_H))

    running = True
    while running:
        dt = clock.tick(60)  # ms
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    flap()
                elif event.key == pygame.K_r:
                    reset()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                flap()
            elif event.type == SPAWN and state == 'running':
                spawn_pipe()

        # Update
        if state == 'running':
            bird_vy += GRAVITY
            bird_y += bird_vy

            # ground
            if bird_y + BIRD_R >= SKY_H:
                bird_y = SKY_H - BIRD_R
                game_over()

            # move pipes
            for p in pipes:
                p["x"] -= PIPE_SPEED * (dt / 16.67)
            # remove offscreen
            pipes = [p for p in pipes if p["x"] + 60 > -10]

            # collision & scoring
            for p in pipes:
                top_rect = (p["x"], 0, 60, p["top"])  # x, y, w, h
                bottom_y = p["top"] + p["gap"]
                bottom_rect = (p["x"], bottom_y, 60, SKY_H - bottom_y)

                if circle_rect_collide(BIRD_X, bird_y, BIRD_R, *top_rect) or \
                   circle_rect_collide(BIRD_X, bird_y, BIRD_R, *bottom_rect):
                    game_over()
                    break

                center_x = p["x"] + 30
                if not p["scored"] and center_x < BIRD_X:
                    p["scored"] = True
                    score += 1

            if score > best:
                best = score

        # Draw
        screen.blit(gradient, (0, 0))
        # buildings (rintangan)
        def draw_building(x, y, w, h, roof_at_top=True):
            if h <= 0:
                return
            pygame.draw.rect(screen, BUILD, (x, y, w, h))
            # roof band
            if roof_at_top:
                pygame.draw.rect(screen, BUILD_D, (x - 2, y, w + 4, 10))
            else:
                pygame.draw.rect(screen, BUILD_D, (x - 2, y + h - 10, w + 4, 10))
            # windows grid
            col_count = 2
            row_step = 22
            col_step = (w - 16) // max(1, col_count)
            for ci in range(col_count):
                wx = x + 8 + ci * col_step
                wy = y + 12
                while wy < y + h - 12:
                    pygame.draw.rect(screen, WINDOW, (wx, wy, 10, 12))
                    wy += row_step

        for p in pipes:
            # top building
            draw_building(p["x"], 0, 60, p["top"], roof_at_top=False)
            # bottom building
            by = p["top"] + p["gap"]
            draw_building(p["x"], by, 60, SKY_H - by, roof_at_top=True)

        # ground
        pygame.draw.rect(screen, GROUND, (0, SKY_H, W, GROUND_H))
        for x in range(0, W, 20):
            pygame.draw.rect(screen, GROUND_TICK, (x, SKY_H, 14, 8))

        # plane (mengganti burung)
        # fuselage
        fy = int(bird_y)
        body_w, body_h = 38, 12
        body_rect = pygame.Rect(BIRD_X - body_w // 2, fy - body_h // 2, body_w, body_h)
        pygame.draw.rect(screen, PLANE_BODY, body_rect, border_radius=6)
        pygame.draw.rect(screen, PLANE_OUTLINE, body_rect, width=1, border_radius=6)
        # nose
        nose = [(body_rect.right, fy), (body_rect.right + 10, fy - 3), (body_rect.right + 10, fy + 3)]
        pygame.draw.polygon(screen, PLANE_BODY, nose)
        pygame.draw.polygon(screen, PLANE_OUTLINE, nose, 1)
        # tail fin
        tail = [(body_rect.left, fy), (body_rect.left - 6, fy - 6), (body_rect.left + 2, fy - 2)]
        pygame.draw.polygon(screen, PLANE_BODY, tail)
        pygame.draw.polygon(screen, PLANE_OUTLINE, tail, 1)
        # wing
        wing = [
            (BIRD_X - 6, fy + 2),
            (BIRD_X + 10, fy + 2),
            (BIRD_X + 2, fy + 12),
            (BIRD_X - 14, fy + 12),
        ]
        pygame.draw.polygon(screen, PLANE_WING, wing)
        pygame.draw.polygon(screen, PLANE_WING_D, wing, 1)

        # Score
        draw_text(screen, str(score), 48, (255, 255, 255), W // 2, 72)
        draw_text(screen, f"Best: {best}", 16, (255, 255, 255), W // 2, 96)

        # UI
        if state == 'ready':
            draw_text(screen, 'Klik / Spasi untuk mulai', 24, (255, 255, 255), W // 2, H // 2 - 20)
            draw_text(screen, 'Lewati gedung sebanyak mungkin!', 18, (255, 255, 255), W // 2, H // 2 + 10)
        elif state == 'gameover':
            draw_text(screen, 'Game Over', 28, (255, 255, 255), W // 2, H // 2 - 10)
            draw_text(screen, f'Skor: {score}  ·  Best: {best}', 18, (255, 255, 255), W // 2, H // 2 + 16)
            draw_text(screen, 'Tekan R untuk restart', 18, (255, 255, 255), W // 2, H // 2 + 38)

        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
