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
bricks = []  # 裝磚塊列表w
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

######################球設定######################

######################遊戲結束設定######################

######################主程式######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按x關閉視窗
            sys.exit()  # 離開
    for brick in bricks:
        brick.draw(screen)

    pygame.display.update()  # 更新畫面
