######################載入套件######################
import pygame
import sys
import random
import math


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color, double_score=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False
        self.hit_color = self._get_hit_color()
        self.disappear = False
        self.double_score = double_score  # 是否為雙倍分數磚塊

    def _get_hit_color(self):
        r, g, b = self.color
        return (max(r // 2, 0), max(g // 2, 0), max(b // 2, 0))

    def draw(self, display_area):
        if self.disappear:
            return
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
        else:
            pygame.draw.rect(display_area, self.hit_color, self.rect)
        if self.double_score:
            # 畫上 x2 字樣
            font = pygame.font.Font(font_path, 18)
            text = font.render("x2", True, (0, 0, 0))
            tx = self.rect.x + (self.rect.width - text.get_width()) // 2
            ty = self.rect.y + (self.rect.height - text.get_height()) // 2
            display_area.blit(text, (tx, ty))
        if self.rect.y > 500:
            for i in range(self.rect.height):
                grad_color = (80 + i * 3, 80 + i * 2, 180 + i * 1)
                pygame.draw.line(
                    display_area,
                    grad_color,
                    (self.rect.x, self.rect.y + i),
                    (self.rect.x + self.rect.width, self.rect.y + i),
                    1,
                )
            pygame.draw.rect(display_area, (255, 255, 255), self.rect, 2)
            pygame.draw.polygon(
                display_area,
                (0, 255, 255),
                [
                    (self.rect.x, self.rect.y + self.rect.height // 2),
                    (self.rect.x - 10, self.rect.y + self.rect.height // 2 + 8),
                    (self.rect.x + 5, self.rect.y + self.rect.height),
                    (self.rect.x + 10, self.rect.y + self.rect.height // 2 + 4),
                ],
            )
            pygame.draw.polygon(
                display_area,
                (255, 255, 0),
                [
                    (
                        self.rect.x + self.rect.width,
                        self.rect.y + self.rect.height // 2,
                    ),
                    (
                        self.rect.x + self.rect.width + 10,
                        self.rect.y + self.rect.height // 2 + 8,
                    ),
                    (
                        self.rect.x + self.rect.width - 5,
                        self.rect.y + self.rect.height,
                    ),  # 修正這一行
                    (
                        self.rect.x + self.rect.width - 10,
                        self.rect.y + self.rect.height // 2 + 4,
                    ),
                ],
            )


class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5
        self.speed_y = -5
        self.is_moving = False
        self.angle = 0

    def draw(self, display_area):
        pygame.draw.circle(
            display_area, self.color, (int(self.x), int(self.y)), self.radius
        )
        self.angle = (self.angle + 6) % 360
        center = (int(self.x), int(self.y))
        r = self.radius

        def rotate_point(cx, cy, px, py, angle_deg):
            angle_rad = angle_deg * 3.14159 / 180
            s, c = math.sin(angle_rad), math.cos(angle_rad)
            px, py = px - cx, py - cy
            xnew = px * c - py * s
            ynew = px * s + py * c
            return int(cx + xnew), int(cy + ynew)

        left_eye = rotate_point(
            center[0], center[1], center[0] - r // 3, center[1] - r // 4, self.angle
        )
        right_eye = rotate_point(
            center[0], center[1], center[0] + r // 3, center[1] - r // 4, self.angle
        )
        pygame.draw.circle(display_area, (0, 0, 0), left_eye, max(2, r // 7))
        pygame.draw.circle(display_area, (0, 0, 0), right_eye, max(2, r // 7))

        mouth_points = []
        for deg in range(30, 150, 10):
            rad = deg * 3.14159 / 180
            x = center[0] + (r // 2) * math.cos(rad)
            y = center[1] + (r // 3) * math.sin(rad)
            mouth_points.append(rotate_point(center[0], center[1], x, y, self.angle))
        if len(mouth_points) > 1:
            pygame.draw.lines(display_area, (0, 0, 0), False, mouth_points, 2)

    def move(self):
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad, bombs, lives):
        score_delta = 0
        lose_life = False
        if self.x - self.radius <= 0 or self.x + self.radius > bg_x:
            self.speed_x = -self.speed_x
        if self.y - self.radius <= 0:
            self.speed_y = -self.speed_y
        if self.y + self.radius >= bg_y:
            self.is_moving = False
        if (
            self.y + self.radius >= pad.rect.y
            and self.y + self.radius <= pad.rect.y + pad.rect.height
            and self.x >= pad.rect.x
            and self.x <= pad.rect.x + pad.rect.width
        ):
            self.speed_y = -abs(self.speed_y)

        for brick in bricks:
            if not brick.hit:
                dx = abs(self.x - (brick.rect.x + brick.rect.width / 2))
                dy = abs(self.y - (brick.rect.y + brick.rect.height / 2))
                if dx <= (self.radius + brick.rect.width / 2) and dy <= (
                    self.radius + brick.rect.height / 2
                ):
                    brick.hit = True
                    score_delta += 1
                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y

        for bomb in bombs:
            if bomb.active and not bomb.exploding:
                dist = ((self.x - bomb.x) ** 2 + (self.y - bomb.y) ** 2) ** 0.5
                if dist <= self.radius + bomb.radius:
                    bomb.exploding = True
                    bomb.explode_timer = 0
                    lose_life = True

        return score_delta, lose_life


class Bomb:
    def __init__(self, x, y, radius=12, color=(255, 0, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.active = True
        self.exploding = False
        self.explode_timer = 0

    def draw(self, display_area):
        if self.active and not self.exploding:
            pygame.draw.circle(
                display_area, self.color, (int(self.x), int(self.y)), self.radius
            )
            pygame.draw.line(
                display_area,
                (0, 0, 0),
                (self.x - self.radius // 2, self.y - self.radius // 2),
                (self.x + self.radius // 2, self.y + self.radius // 2),
                2,
            )
            pygame.draw.line(
                display_area,
                (0, 0, 0),
                (self.x + self.radius // 2, self.y - self.radius // 2),
                (self.x - self.radius // 2, self.y + self.radius // 2),
                2,
            )
        elif self.exploding:
            max_radius = int(
                min(display_area.get_width(), display_area.get_height()) * 0.7
            )
            progress = min(self.explode_timer / 400, 1.0)
            cur_radius = int(self.radius + (max_radius - self.radius) * progress)
            alpha = int(255 * (1 - progress))
            explosion_surf = pygame.Surface(
                (max_radius * 2, max_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                explosion_surf,
                (255, 200, 0, int(alpha * 0.7)),
                (max_radius, max_radius),
                int(cur_radius * 0.7),
            )
            pygame.draw.circle(
                explosion_surf,
                (255, 128, 0, alpha),
                (max_radius, max_radius),
                cur_radius,
            )
            pygame.draw.circle(
                explosion_surf,
                (255, 255, 255, int(alpha * 0.4)),
                (max_radius, max_radius),
                int(cur_radius * 0.3),
            )
            display_area.blit(
                explosion_surf, (self.x - max_radius, self.y - max_radius)
            )

    def update(self, dt):
        if self.exploding:
            self.explode_timer += dt
            if self.explode_timer >= 400:
                self.exploding = False
                self.active = False


class Heal:
    def __init__(self, x, y, radius=12, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.active = True
        self.exploding = False
        self.explode_timer = 0

    def draw(self, display_area):
        if self.active and not self.exploding:
            pygame.draw.circle(
                display_area, self.color, (int(self.x), int(self.y)), self.radius
            )
            pygame.draw.rect(
                display_area,
                (255, 255, 255),
                (self.x - 2, self.y - self.radius + 4, 4, self.radius * 2 - 8),
            )
            pygame.draw.rect(
                display_area,
                (255, 255, 255),
                (self.x - self.radius + 4, self.y - 2, self.radius * 2 - 8, 4),
            )
        elif self.exploding:
            max_radius = int(
                min(display_area.get_width(), display_area.get_height()) * 0.7
            )
            progress = min(self.explode_timer / 400, 1.0)
            cur_radius = int(self.radius + (max_radius - self.radius) * progress)
            alpha = int(255 * (1 - progress))
            explosion_surf = pygame.Surface(
                (max_radius * 2, max_radius * 2), pygame.SRCALPHA
            )
            pygame.draw.circle(
                explosion_surf,
                (128, 255, 128, int(alpha * 0.7)),
                (max_radius, max_radius),
                int(cur_radius * 0.7),
            )
            pygame.draw.circle(
                explosion_surf, (0, 255, 0, alpha), (max_radius, max_radius), cur_radius
            )
            pygame.draw.circle(
                explosion_surf,
                (255, 255, 255, int(alpha * 0.3)),
                (max_radius, max_radius),
                int(cur_radius * 0.3),
            )
            display_area.blit(
                explosion_surf, (self.x - max_radius, self.y - max_radius)
            )

    def update(self, dt):
        if self.exploding:
            self.explode_timer += dt
            if self.explode_timer >= 400:
                self.exploding = False
                self.active = False


# 新增粒子效果類別
class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-4, 4)
        angle = random.uniform(math.pi * 1.15, math.pi * 1.85)  # 主要往下
        speed = random.uniform(2, 5)
        self.vx = math.cos(angle) * speed * 0.3  # 水平速度更小
        self.vy = abs(math.sin(angle) * speed) + 1.2  # 保證往下
        self.life = 60  # 60幀 = 1秒
        self.color = color
        self.radius = random.randint(2, 4)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.32  # 重力
        self.life -= 1
        self.radius = max(0.5, self.radius - 0.07)  # 慢慢變小

    def draw(self, surface):
        if self.life > 0 and self.radius > 0.5:
            alpha = max(0, min(255, int(180 * self.life / 60)))
            surf = pygame.Surface(
                (int(self.radius * 2), int(self.radius * 2)), pygame.SRCALPHA
            )
            pygame.draw.circle(
                surf,
                self.color + (alpha,),
                (int(self.radius), int(self.radius)),
                int(self.radius),
            )
            surface.blit(surf, (self.x - self.radius, self.y - self.radius))


######################初始化設定######################
pygame.init()
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("打磚塊遊戲")
screen = pygame.display.set_mode(bg_size)

bricks_row = 9
bricks_col = 11
brick_w = 58
brick_h = 16
bricks_gap = 2
bricks = []


def gen_brick_colors():
    color_list = []
    for col in range(bricks_col):
        for row in range(bricks_row):
            base_r = 40 + random.randint(-20, 60)
            base_g = 80 + random.randint(-30, 80)
            base_b = 180 + random.randint(-40, 75)
            color = (
                max(0, min(base_r, 255)),
                max(0, min(base_g, 255)),
                max(0, min(base_b, 255)),
            )
            color_list.append(color)
    return color_list


brick_colors = gen_brick_colors()
double_score_count = 12  # 例如 12 個
double_score_indices = set(
    random.sample(range(bricks_row * bricks_col), double_score_count)
)
for idx, (col, row) in enumerate(
    [(c, r) for c in range(bricks_col) for r in range(bricks_row)]
):
    x = col * (brick_w + bricks_gap) + 70
    y = row * (brick_h + bricks_gap) + 60
    if idx in double_score_indices:
        color = (255, 255, 80)  # 黃色
        double_score = True
    else:
        color = brick_colors[idx]
        double_score = False
    brick = Brick(x, y, brick_w, brick_h, color, double_score)
    bricks.append(brick)

font_path = "/System/Library/Fonts/PingFang.ttc"
score_font = pygame.font.Font(font_path, 32)
score = 0
lives = 3
game_over = False
waiting_start = True

pad = Brick(0, bg_y - 48, brick_w, brick_h, (168, 56, 38))
ball_radius = 10
ball_color = (255, 255, 0)
ball = Ball(
    pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color
)

FPS = pygame.time.Clock()

bombs = []
bomb_count = 5
bomb_positions = []
min_dist = 80
for _ in range(bomb_count):
    tries = 0
    while True:
        bx = random.randint(70, bg_x - 70)
        by = random.randint(100, bg_y // 2)
        overlap = False
        for brick in bricks:
            if brick.rect.collidepoint(bx, by):
                overlap = True
                break
        too_close = False
        for px, py in bomb_positions:
            if ((bx - px) ** 2 + (by - py) ** 2) ** 0.5 < min_dist:
                too_close = True
                break
        if not overlap and not too_close:
            bombs.append(Bomb(bx, by))
            bomb_positions.append((bx, by))
            break
        tries += 1
        if tries > 100:
            break

heal_count = 5  # 原本是2，改成5，多產生幾個加血
heals = []
for _ in range(heal_count):
    while True:
        hx = random.randint(70, bg_x - 70)
        hy = random.randint(100, bg_y // 2)
        overlap = False
        for brick in bricks:
            if brick.rect.collidepoint(hx, hy):
                overlap = True
                break
        if not overlap:
            heals.append(Heal(hx, hy))
            break

encourage_msgs = [
    "連擊達成！",
    "節奏超棒！",
    "手感爆棚！",
    "快打高手！",
    "超級Combo！",
    "節奏感滿分！",
    "打擊感十足！",
    "帥氣連發！",
    "節奏停不下來！",
    "神操作！",
]
encourage_timer = 0
encourage_text = ""
encourage_count = 0

shake_timer = 0
shake_offset = (0, 0)

balls = ball  # 用 list 管理多顆球

particles = []

while True:
    dt = FPS.tick(60)
    if shake_timer > 0:
        shake_timer -= dt
        if shake_timer > 0:
            shake_offset = (random.randint(-8, 8), random.randint(-8, 8))
        else:
            shake_offset = (0, 0)
    else:
        shake_offset = (0, 0)

    draw_surface = screen
    if shake_offset != (0, 0):
        draw_surface = pygame.Surface((bg_x, bg_y))
        draw_surface.fill((0, 0, 0))
    else:
        screen.fill((0, 0, 0))

    mos_x, mos_y = pygame.mouse.get_pos()
    pad.rect.x = mos_x - pad.rect.width // 2
    if pad.rect.x < 0:
        pad.rect.x = 0
    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if waiting_start or game_over:
                waiting_start = False
                game_over = False
                score = 0
                lives = 3
                # 重新產生雙倍分數磚塊
                double_score_indices = set(
                    random.sample(range(bricks_row * bricks_col), double_score_count)
                )
                bricks.clear()
                for idx, (col, row) in enumerate(
                    [(c, r) for c in range(bricks_col) for r in range(bricks_row)]
                ):
                    x = col * (brick_w + bricks_gap) + 70
                    y = row * (brick_h + bricks_gap) + 60
                    if idx in double_score_indices:
                        color = (255, 255, 80)
                        double_score = True
                    else:
                        color = brick_colors[idx]
                        double_score = False
                    brick = Brick(x, y, brick_w, brick_h, color, double_score)
                    bricks.append(brick)
                bombs.clear()
                bomb_positions = []
                for _ in range(bomb_count):
                    tries = 0
                    while True:
                        bx = random.randint(70, bg_x - 70)
                        by = random.randint(100, bg_y // 2)
                        overlap = False
                        for brick in bricks:
                            if brick.rect.collidepoint(bx, by):
                                overlap = True
                                break
                        too_close = False
                        for px, py in bomb_positions:
                            if ((bx - px) ** 2 + (by - py) ** 2) ** 0.5 < min_dist:
                                too_close = True
                                break
                        if not overlap and not too_close:
                            bombs.append(Bomb(bx, by))
                            bomb_positions.append((bx, by))
                            break
                        tries += 1
                        if tries > 100:
                            break
                heals.clear()
                heal_count = 5  # 重新開始時也要同步
                for _ in range(heal_count):
                    while True:
                        hx = random.randint(70, bg_x - 70)
                        hy = random.randint(100, bg_y // 2)
                        overlap = False
                        for brick in bricks:
                            if brick.rect.collidepoint(hx, hy):
                                overlap = True
                                break
                        if not overlap:
                            heals.append(Heal(hx, hy))
                            break
                pad.rect.x = bg_x // 2 - pad.rect.width // 2
                ball.x = pad.rect.x + pad.rect.width // 2
                ball.y = pad.rect.y - ball_radius
                ball.is_moving = True
                ball.speed_x = 5
                ball.speed_y = -5
                shake_timer = 0
                shake_offset = (0, 0)
                encourage_timer = 0
                encourage_text = ""
                encourage_count = 0
            # 這裡 balls 其實是 ball，不是 list，請改成如下：
            elif not ball.is_moving and not game_over:
                ball.is_moving = True

    if waiting_start:
        encourage_timer = 0
        encourage_text = ""
        encourage_count = 0
    elif not game_over:
        if not ball.is_moving:
            ball.x = pad.rect.x + pad.rect.width // 2
            ball.y = pad.rect.y - ball_radius
        else:
            score_delta, lose_life = ball.check_collision(
                bg_x, bg_y, bricks, pad, bombs, lives
            )
            # 雙倍分數判斷 + 粒子效果
            for brick in bricks:
                if brick.hit and not brick.disappear:
                    # 粒子顏色
                    if brick.double_score:
                        color = (255, 255, 80)
                    else:
                        color = (80, 160, 255)
                    # 產生粒子
                    for _ in range(16):
                        particles.append(
                            Particle(
                                brick.rect.x + brick.rect.width // 2,
                                brick.rect.y + brick.rect.height // 2,
                                color,
                            )
                        )
                    if brick.double_score:
                        score_delta += 1  # 再加 1 分
                    brick.disappear = True
            heal_got = False
            for heal in heals:
                if heal.active and not heal.exploding:
                    dist = ((ball.x - heal.x) ** 2 + (ball.y - heal.y) ** 2) ** 0.5
                    if dist <= ball.radius + heal.radius:
                        heal.active = False
                        heal.exploding = True
                        heal.explode_timer = 0
                        lives += 1
                        heal_got = True
            score += score_delta
            # 新增：達到80分時顯示你贏了
            if score >= 80 and not game_over:
                game_over = True
                win_message = True
            else:
                win_message = False
            if score_delta > 0:
                new_count = score // 10
                if new_count > encourage_count and score > 0:
                    encourage_count = new_count
                    encourage_text = random.choice(encourage_msgs)
                    encourage_timer = 1200
            ball.move()
            if (
                any(bomb.exploding and bomb.explode_timer == 0 for bomb in bombs)
                or heal_got
            ):
                shake_timer = 300
            # 球碰到炸彈時重置
            for bomb in bombs:
                if bomb.exploding and bomb.explode_timer == 0:
                    ball.is_moving = False
                    ball.x = pad.rect.x + pad.rect.width // 2
                    ball.y = pad.rect.y - ball_radius
                    ball.speed_x = 5
                    ball.speed_y = -5
                    break
            if lose_life:
                lives -= 1
                if lives <= 0:
                    game_over = True
            elif not ball.is_moving:
                lives -= 1
                if lives <= 0:
                    game_over = True

    for brick in bricks:
        brick.draw(draw_surface)
    for bomb in bombs:
        bomb.update(dt)
        bomb.draw(draw_surface)
    for heal in heals:
        heal.update(dt)
        heal.draw(draw_surface)
    # 更新粒子
    for p in particles:
        p.update()
    particles = [p for p in particles if p.life > 0 and p.radius > 0.5]
    for p in particles:
        p.draw(draw_surface)
    pad.draw(draw_surface)
    ball.draw(draw_surface)

    score_surface = score_font.render(f"分數: {score}", True, (255, 255, 255))
    draw_surface.blit(score_surface, (10, 10))
    lives_surface = score_font.render(f"剩餘: {lives}", True, (255, 255, 255))
    draw_surface.blit(lives_surface, (10, 50))
    # 右上角顯示目標80分
    target_surface = score_font.render("目標80分", True, (255, 255, 0))
    draw_surface.blit(target_surface, (bg_x - target_surface.get_width() - 16, 10))

    if waiting_start:
        tip_surface = score_font.render("點擊滑鼠左鍵開始遊戲", True, (255, 255, 0))
        draw_surface.blit(
            tip_surface, (bg_x // 2 - tip_surface.get_width() // 2, bg_y // 2)
        )
    elif game_over:
        if score >= 80:
            win_surface = score_font.render("你贏了", True, (0, 255, 0))
            draw_surface.blit(
                win_surface, (bg_x // 2 - win_surface.get_width() // 2, bg_y // 2 - 80)
            )
        over_surface = score_font.render("遊戲結束", True, (255, 0, 0))
        tip_surface = score_font.render("按滑鼠左鍵重新開始", True, (255, 255, 255))
        draw_surface.blit(
            over_surface, (bg_x // 2 - over_surface.get_width() // 2, bg_y // 2 - 40)
        )
        draw_surface.blit(
            tip_surface, (bg_x // 2 - tip_surface.get_width() // 2, bg_y // 2 + 10)
        )

    if encourage_timer > 0 and encourage_text:
        encourage_surface = score_font.render(encourage_text, True, (255, 255, 0))
        draw_surface.blit(
            encourage_surface,
            (bg_x // 2 - encourage_surface.get_width() // 2, bg_y // 2 - 120),
        )
        encourage_timer -= dt
        if encourage_timer <= 0:
            encourage_text = ""

    if shake_offset != (0, 0):
        screen.fill((0, 0, 0))
        screen.blit(draw_surface, shake_offset)
    pygame.display.update()
