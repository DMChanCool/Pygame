######################載入套件######################
import pygame
import sys
import random


######################物件類別######################
class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)  # 磚塊的矩形範圍
        self.color = color
        self.hit = False  # 磚塊是否被打到

    def draw(self, display_area):
        """
        繪製磚塊
        display_area:繪製磚塊的區域
        """
        if not self.hit:
            pygame.draw.rect(display_area, self.color, self.rect)


class Ball:
    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.speed_x = 5  # 球的x速度
        self.speed_y = -5
        self.is_moving = False

    def draw(self, display_area):
        pygame.draw.circle(
            display_area, self.color, (int(self.x), int(self.y)), self.radius
        )

    def move(self):
        if self.is_moving:
            self.x += self.speed_x
            self.y += self.speed_y

    def check_collision(self, bg_x, bg_y, bricks, pad):
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
                    brick

                    if (
                        self.x < brick.rect.x
                        or self.x > brick.rect.x + brick.rect.width
                    ):
                        self.speed_x = -self.speed_x
                    else:
                        self.speed_y = -self.speed_y


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

######################主程式######################
while True:
    FPS.tick(60)
    screen.fill((0, 0, 0))  # 清除畫面
    mos_x, mos_y = pygame.mouse.get_pos()  # 取得滑鼠位置
    pad.rect.x = mos_x - pad.rect.width // 2  # 底板已滑鼠為中心

    if pad.rect.x < 0:  # 底板不可以超出邊界(左)
        pad.rect.x = 0
    if pad.rect.x + pad.rect.width > bg_x:  # 底板不可以超出邊界(右)
        pad.rect.x = bg_x - pad.rect.width

    if not ball.is_moving:  # 球不在移動
        ball.x = pad.rect.x + pad.rect.width // 2
        ball.y = pad.rect.y - ball_radius
    else:
        ball.move()
        game_over = ball.check_collision(bg_x, bg_y, bricks, pad)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按x關閉視窗
            sys.exit()  # 離開
        if event.type == pygame.MOUSEBUTTONDOWN:  # 按下滑鼠左鍵
            ball.is_moving = True

    for brick in bricks:
        brick.draw(screen)

    pad.draw(screen)  # 繪製底板
    ball.draw(screen)  # 繪製球

    pygame.display.update()  # 更新畫面
