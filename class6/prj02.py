######################載入套件######################
import pygame
import sys
import random
import math


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.hit = False
        self.hit_color = self._get_hit_color()
        self.disappear = False  # 新增：打完後消失

    def _get_hit_color(self):
        r, g, b = self.color
        return (max(r // 2, 0), max(g // 2, 0), max(b // 2, 0))

    def draw(self, display_area):
        if self.disappear:
            return  # 不畫已消失的磚塊
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)
        else:
            pygame.draw.rect(display_area, self.hit_color, self.rect)
        # 酷炫裝飾：底板才畫
        if self.rect.y > 500:  # 只裝飾底板
            # 板子漸層
            for i in range(self.rect.height):
                grad_color = (
                    80 + i * 3,
                    80 + i * 2,
                    180 + i * 1,
                )
                pygame.draw.line(
                    display_area,
                    grad_color,
                    (self.rect.x, self.rect.y + i),
                    (self.rect.x + self.rect.width, self.rect.y + i),
                    1,
                )
            # 板子外框
            pygame.draw.rect(display_area, (255, 255, 255), self.rect, 2)
            # 板子兩側閃電
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
                    (self.rect.x + self.rect.width - 5, self.rect.y + self.rect.height),
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
        self.angle = 0  # 旋轉角度

    def draw(self, display_area):
        # 畫球本體
        pygame.draw.circle(
            display_area, self.color, (int(self.x), int(self.y)), self.radius
        )
        # 畫旋轉笑臉
        self.angle = (self.angle + 6) % 360  # 每次呼叫旋轉
        center = (int(self.x), int(self.y))
        r = self.radius

        # 計算旋轉後的眼睛和嘴巴座標
        def rotate_point(cx, cy, px, py, angle_deg):
            angle_rad = angle_deg * 3.14159 / 180
            s, c = math.sin(angle_rad), math.cos(angle_rad)
            px, py = px - cx, py - cy
            xnew = px * c - py * s
            ynew = px * s + py * c
            return int(cx + xnew), int(cy + ynew)

        # 眼睛
        left_eye = rotate_point(
            center[0], center[1], center[0] - r // 3, center[1] - r // 4, self.angle
        )
        right_eye = rotate_point(
            center[0], center[1], center[0] + r // 3, center[1] - r // 4, self.angle
        )
        pygame.draw.circle(display_area, (0, 0, 0), left_eye, max(2, r // 7))
        pygame.draw.circle(display_area, (0, 0, 0), right_eye, max(2, r // 7))

        # 嘴巴（弧線）
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
                    # 球擊中磚塊
                    brick.hit = True
                    score_delta += 1
                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y

        # 檢查炸彈碰撞
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
        self.explode_timer = 0  # 單位: 毫秒

    def draw(self, display_area):
        if self.active and not self.exploding:
            pygame.draw.circle(
                display_area, self.color, (int(self.x), int(self.y)), self.radius
            )
            # 畫個簡單的黑色X
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
            # 超大爆炸動畫：紅橙色擴散圓，覆蓋大半個畫面
            max_radius = int(
                min(display_area.get_width(), display_area.get_height()) * 0.7
            )
            progress = min(self.explode_timer / 400, 1.0)  # 0~1, 0.4秒
            cur_radius = int(self.radius + (max_radius - self.radius) * progress)
            alpha = int(255 * (1 - progress))
            explosion_surf = pygame.Surface(
                (max_radius * 2, max_radius * 2), pygame.SRCALPHA
            )
            # 多層次爆炸色彩
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


# 新增回血物件
class Heal:
    def __init__(self, x, y, radius=12, color=(0, 255, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.active = True
        self.exploding = False
        self.explode_timer = 0  # 單位: 毫秒

    def draw(self, display_area):
        if self.active and not self.exploding:
            pygame.draw.circle(
                display_area, self.color, (int(self.x), int(self.y)), self.radius
            )
            # 畫白色十字
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
            # 綠色大爆炸動畫
            max_radius = int(
                min(display_area.get_width(), display_area.get_height()) * 0.7
            )
            progress = min(self.explode_timer / 400, 1.0)
            cur_radius = int(self.radius + (max_radius - self.radius) * progress)
            alpha = int(255 * (1 - progress))
            explosion_surf = pygame.Surface(
                (max_radius * 2, max_radius * 2), pygame.SRCALPHA
            )
            # 多層次綠色爆炸
            pygame.draw.circle(
                explosion_surf,
                (128, 255, 128, int(alpha * 0.7)),
                (max_radius, max_radius),
                int(cur_radius * 0.7),
            )
            pygame.draw.circle(
                explosion_surf,
                (0, 255, 0, alpha),
                (max_radius, max_radius),
                cur_radius,
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


######################定義函式區######################

######################初始化設定######################
pygame.init()  # 啟動pygame
######################載入圖片######################

######################遊戲視窗設定######################
bg_x = 800
bg_y = 600
bg_size = (bg_x, bg_y)
pygame.display.set_caption("打磚塊遊戲")  # 設定視窗大小
screen = pygame.display.set_mode(bg_size)  # 設定視窗大小
######################磚塊######################
bricks_row = 9
bricks_col = 11
brick_w = 58
brick_h = 16
bricks_gap = 2
bricks = []  # 裝磚塊列表
for col in range(bricks_col):
    for row in range(bricks_row):
        x = col * (brick_w + bricks_gap) + 70
        y = row * (brick_h + bricks_gap) + 60
        color = (
            random.randint(10, 255),
            random.randint(10, 255),
            random.randint(10, 255),
        )
        brick = Brick(x, y, brick_w, brick_h, color)
        bricks.append(brick)
######################顯示文字設定######################
font_path = "/System/Library/Fonts/PingFang.ttc"
score_font = pygame.font.Font(font_path, 32)
score = 0
lives = 3
game_over = False  # 一開始為等待開始狀態
waiting_start = True  # 新增：一開始等待玩家點擊

######################底板設定######################
pad = Brick(0, bg_y - 48, brick_w, brick_h, (168, 56, 38))
######################球設定######################
ball_radius = 10
ball_color = (255, 255, 0)
ball = Ball(
    pad.rect.x + pad.rect.width // 2, pad.rect.y - ball_radius, ball_radius, ball_color
)
######################遊戲結束設定######################

# ######################新增fps######################
FPS = pygame.time.Clock()  # 設定時鐘

######################炸彈設定######################
bombs = []
bomb_count = 5
for _ in range(bomb_count):
    while True:
        bx = random.randint(70, bg_x - 70)
        by = random.randint(100, bg_y // 2)
        # 避免與磚塊重疊
        overlap = False
        for brick in bricks:
            if brick.rect.collidepoint(bx, by):
                overlap = True
                break
        if not overlap:
            bombs.append(Bomb(bx, by))
            break

######################回血設定######################
heals = []
heal_count = 2
for _ in range(heal_count):
    while True:
        hx = random.randint(70, bg_x - 70)
        hy = random.randint(100, bg_y // 2)
        # 避免與磚塊重疊
        overlap = False
        for brick in bricks:
            if brick.rect.collidepoint(hx, hy):
                overlap = True
                break
        if not overlap:
            heals.append(Heal(hx, hy))
            break

######################主程式######################
shake_timer = 0
shake_offset = (0, 0)
while True:
    dt = FPS.tick(60)
    # 處理震動
    if shake_timer > 0:
        shake_timer -= dt
        if shake_timer > 0:
            shake_offset = (random.randint(-8, 8), random.randint(-8, 8))
        else:
            shake_offset = (0, 0)
    else:
        shake_offset = (0, 0)

    # 畫面繪製到一個暫存 surface
    draw_surface = screen
    if shake_offset != (0, 0):
        draw_surface = pygame.Surface((bg_x, bg_y))
        draw_surface.fill((0, 0, 0))
    else:
        screen.fill((0, 0, 0))  # 清除畫面

    mos_x, mos_y = pygame.mouse.get_pos()
    pad.rect.x = mos_x - pad.rect.width // 2

    if pad.rect.x < 0:
        pad.rect.x = 0
    if pad.rect.x + pad.rect.width > bg_x:
        pad.rect.x = bg_x - pad.rect.width

    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if waiting_start:
                waiting_start = False
                game_over = False
                score = 0
                lives = 3
                # 重新產生磚塊
                bricks.clear()
                for col in range(bricks_col):
                    for row in range(bricks_row):
                        x = col * (brick_w + bricks_gap) + 70
                        y = row * (brick_h + bricks_gap) + 60
                        color = (
                            random.randint(10, 255),
                            random.randint(10, 255),
                            random.randint(10, 255),
                        )
                        brick = Brick(x, y, brick_w, brick_h, color)
                        bricks.append(brick)
                bombs.clear()
                for _ in range(bomb_count):
                    while True:
                        bx = random.randint(70, bg_x - 70)
                        by = random.randint(100, bg_y // 2)
                        overlap = False
                        for brick in bricks:
                            if brick.rect.collidepoint(bx, by):
                                overlap = True
                                break
                        if not overlap:
                            bombs.append(Bomb(bx, by))
                            break
                heals.clear()
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
            elif game_over:
                # 重新開始遊戲
                score = 0
                lives = 3
                game_over = False
                waiting_start = False
                # 重新產生磚塊
                bricks.clear()
                for col in range(bricks_col):
                    for row in range(bricks_row):
                        x = col * (brick_w + bricks_gap) + 70
                        y = row * (brick_h + bricks_gap) + 60
                        color = (
                            random.randint(10, 255),
                            random.randint(10, 255),
                            random.randint(10, 255),
                        )
                        brick = Brick(x, y, brick_w, brick_h, color)
                        bricks.append(brick)
                bombs.clear()
                for _ in range(bomb_count):
                    while True:
                        bx = random.randint(70, bg_x - 70)
                        by = random.randint(100, bg_y // 2)
                        overlap = False
                        for brick in bricks:
                            if brick.rect.collidepoint(bx, by):
                                overlap = True
                                break
                        if not overlap:
                            bombs.append(Bomb(bx, by))
                            break
                heals.clear()
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
            elif not ball.is_moving and not game_over:
                ball.is_moving = True

    if waiting_start:
        # 等待開始狀態不進行遊戲邏輯
        pass
    elif not game_over:
        if not ball.is_moving:
            ball.x = pad.rect.x + pad.rect.width // 2
            ball.y = pad.rect.y - ball_radius
        else:
            score_delta, lose_life = ball.check_collision(
                bg_x, bg_y, bricks, pad, bombs, lives
            )
            # 處理磚塊消失
            for brick in bricks:
                if brick.hit and not brick.disappear:
                    brick.disappear = True
            # 處理回血碰撞
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
            ball.move()
            # 爆炸震動
            if (
                any(bomb.exploding and bomb.explode_timer == 0 for bomb in bombs)
                or heal_got
            ):
                shake_timer = 300  # 0.3秒
            if lose_life:
                lives -= 1
                if lives <= 0:
                    game_over = True
                ball.is_moving = False
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

    pad.draw(draw_surface)
    ball.draw(draw_surface)

    # 顯示分數
    score_surface = score_font.render(f"分數: {score}", True, (255, 255, 255))
    draw_surface.blit(score_surface, (10, 10))
    # 顯示剩餘次數
    lives_surface = score_font.render(f"剩餘: {lives}", True, (255, 255, 255))
    draw_surface.blit(lives_surface, (10, 50))

    # 顯示等待開始或遊戲結束
    if waiting_start:
        tip_surface = score_font.render("點擊滑鼠左鍵開始遊戲", True, (255, 255, 0))
        draw_surface.blit(
            tip_surface, (bg_x // 2 - tip_surface.get_width() // 2, bg_y // 2)
        )
    elif game_over:
        over_surface = score_font.render("遊戲結束", True, (255, 0, 0))
        tip_surface = score_font.render("按滑鼠左鍵重新開始", True, (255, 255, 255))
        draw_surface.blit(
            over_surface, (bg_x // 2 - over_surface.get_width() // 2, bg_y // 2 - 40)
        )
        draw_surface.blit(
            tip_surface, (bg_x // 2 - tip_surface.get_width() // 2, bg_y // 2 + 10)
        )

    # 若有震動，將暫存 surface 貼到主畫面
    if shake_offset != (0, 0):
        screen.fill((0, 0, 0))
        screen.blit(draw_surface, shake_offset)
    pygame.display.update()  # 更新畫面
