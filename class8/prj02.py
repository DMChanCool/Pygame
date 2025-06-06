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
        self.speed = 5  # 主角移動速度（每次移動5像素）

    def draw(self, display_area):
        """
        繪製主角
        display_area: 要繪製的畫布
        """
        pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        """
        控制主角左右移動，並實現穿牆效果
        direction: -1為左移，1為右移
        bg_x: 視窗寬度（右邊界）
        """
        self.rect.x += direction * self.speed  # 根據方向與速度移動主角

        # 穿牆效果：主角完全移出左邊界，從右側出現
        if self.rect.right < 0:
            self.rect.left = bg_x
        # 穿牆效果：主角完全移出右邊界，從左側出現
        elif self.rect.left > bg_x:
            self.rect.right = 0


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

###################### 新增fps設定 ######################
FPS = pygame.time.Clock()  # 設定時鐘

###################### 遊戲主迴圈 ######################
while True:
    FPS.tick(60)  # 每秒最多60幀，控制遊戲速度
    # 處理事件
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按下關閉視窗
            pygame.quit()
            sys.exit()

    # 取得目前按下的按鍵狀態
    keys = pygame.key.get_pressed()
    # 如果按下左方向鍵，主角向左移動
    if keys[pygame.K_LEFT]:
        player.move(-1, win_width)
    # 如果按下右方向鍵，主角向右移動
    if keys[pygame.K_RIGHT]:
        player.move(1, win_width)

    screen.fill((0, 0, 0))  # 清空畫面為黑色
    player.draw(screen)  # 繪製主角

    pygame.display.update()  # 更新畫面
