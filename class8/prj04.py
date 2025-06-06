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

        # === 步驟4: 新增跳躍與重力屬性 ===
        self.velocity_y = 0      # 垂直速度
        self.jump_power = -12    # 跳躍初速度（負值代表向上）
        self.gravity = 0.5       # 重力加速度
        self.on_platform = False # 是否站在平台上

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

    # === 步驟4: 新增apply_gravity方法 ===
    def apply_gravity(self):
        """
        應用重力，讓主角自動下落
        """
        self.velocity_y += self.gravity  # 垂直速度隨重力增加
        self.rect.y += int(self.velocity_y)  # 更新主角y座標

    # === 步驟4: 新增平台碰撞檢查 ===
    def check_platform_collision(self, platform):
        """
        檢查主角是否落在平台上，並處理彈跳
        platform: Platform物件
        """
        # 僅在主角往下掉時檢查碰撞
        if self.velocity_y > 0:
            # 主角底部與平台頂部重疊，且左右有交集
            if (
                self.rect.bottom <= platform.rect.top + self.velocity_y
                and self.rect.bottom + self.velocity_y >= platform.rect.top
                and self.rect.right > platform.rect.left
                and self.rect.left < platform.rect.right
            ):
                self.rect.bottom = platform.rect.top  # 主角底部對齊平台頂部
                self.velocity_y = self.jump_power     # 彈跳
                self.on_platform = True
                return True
        self.on_platform = False
        return False


###################### 平台類別 ######################
class Platform:
    def __init__(self, x, y, width, height, color):
        """
        初始化平台
        x, y: 平台左上角座標
        width, height: 平台寬高
        color: 平台顏色 (RGB)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area):
        """
        繪製平台
        display_area: 要繪製的平台視窗
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

###################### 平台設定 ######################
# 平台尺寸
platform_w = 60
platform_h = 10
platform_color = (255, 255, 255)  # 白色
# 平台位置：底部上方10像素，水平置中
platform_x = (win_width - platform_w) // 2
platform_y = win_height - platform_h - 10
# 建立平台物件
platform = Platform(platform_x, platform_y, platform_w, platform_h, platform_color)

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

    # === 步驟4: 主角自動下落與平台碰撞 ===
    player.apply_gravity()  # 應用重力，主角自動下落
    player.check_platform_collision(platform)  # 檢查是否落在平台並彈跳

    screen.fill((0, 0, 0))  # 清空畫面為黑色
    player.draw(screen)  # 繪製主角
    platform.draw(screen)  # 繪製平台

    pygame.display.update()  # 更新畫面
