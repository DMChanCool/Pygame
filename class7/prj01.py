###################### 載入套件 ######################
import pygame
import sys


###################### 主角類別 ######################
class Player:
    def __init__(self, x, y, width, height, color):
        """
        初始化主角
        x, y: 主角左上角座標
        width, height: 主角寬高
        color: 主角顏色 (RGB)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area):
        """
        繪製主角
        display_area: 要繪製的畫布
        """
        pygame.draw.rect(display_area, self.color, self.rect)


###################### 初始化設定 ######################
pygame.init()  # 啟動pygame

###################### 遊戲視窗設定 ######################
win_width = 400
win_height = 600
pygame.display.set_caption("Doodle Jump - 基本視窗與主角")
screen = pygame.display.set_mode((win_width, win_height))  # 設定視窗大小

###################### 主角設定 ######################
player_width = 30
player_height = 30
player_color = (0, 255, 0)  # 綠色
# 主角初始位置：底部中間，底部上方50像素
player_x = win_width // 2 - player_width // 2
player_y = win_height - 50 - player_height
player = Player(player_x, player_y, player_width, player_height, player_color)

###################### 遊戲主迴圈 ######################
while True:
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按下關閉視窗
            pygame.quit()
            sys.exit()

    screen.fill((255, 255, 255))  # 清空畫面為白色
    player.draw(screen)  # 繪製主角

    pygame.display.update()  # 更新畫面
