import pygame  # 載入 pygame 套件
import sys  # 載入系統相關套件，方便結束程式


###################### 初始化設定 ######################
###################### 玩家物件類別 ######################
class Player:
    def __init__(self, x, y, image_path, bg_width, bg_height):
        self.image = pygame.image.load(image_path)  # 載入玩家圖片
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)  # 設定初始位置
        self.bg_width = bg_width  # 背景寬度
        self.bg_height = bg_height  # 背景高度
        self.speed = 10  # 玩家移動速度
        # 新增：載入左右方向的玩家圖片
        self.image_left = pygame.image.load(
            "class15/image/fighter_L.png"
        )  # 左移時顯示左圖（依原始需求）
        self.image_right = pygame.image.load(
            "class15/image/fighter_R.png"
        )  # 右移時顯示右圖（依原始需求）
        self.image_mid = self.image  # 保留原始圖片（中間）
        # 新增：載入玩家後方的推進器（燈焰）圖片
        # - 位置會以玩家的 rect 作為參考，畫在玩家下方中央
        # - 當玩家按下 S 鍵時，燈焰會暫時隱藏，放開時才顯示
        self.burner_image = pygame.image.load("class15/image/starship_burner.png")
        # 是否顯示燈焰，預設為顯示
        self.burner_visible = True

    def move(self, keys):
        """
        根據按鍵移動玩家，並限制在背景範圍內
        keys: pygame.key.get_pressed() 的結果
        """
        # 先預設為中間圖片，並保持中心位置不變（避免切換圖片時位置跳動）
        prev_center = self.rect.center
        self.image = self.image_mid
        self.rect = self.image.get_rect(center=prev_center)
        # 判斷按鍵並移動
        if keys[pygame.K_w]:  # 上
            self.rect.y -= self.speed
        if keys[pygame.K_s]:  # 下
            self.rect.y += self.speed
        # 當玩家按下 S 時，後方燈焰暫時隱藏；放開時顯示
        # 注意：這裡利用 keys 陣列持續更新燈焰顯示狀態
        if keys[pygame.K_s]:
            self.burner_visible = False
        else:
            self.burner_visible = True
        if keys[pygame.K_a]:  # 左
            self.rect.x -= self.speed
            # 切換為向左圖片，並以原本中心對齊新 rect，避免切換時位置怪異
            prev_center = self.rect.center
            self.image = self.image_left  # 左移時切換圖片（顯示左圖）
            self.rect = self.image.get_rect(center=prev_center)
        if keys[pygame.K_d]:  # 右
            self.rect.x += self.speed
            # 切換為向右圖片，並以原本中心對齊新 rect
            prev_center = self.rect.center
            self.image = self.image_right  # 右移時切換圖片（顯示右圖）
            self.rect = self.image.get_rect(center=prev_center)
        # 邊界判斷，不能超出背景
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.bg_width:
            self.rect.right = self.bg_width
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.bg_height:
            self.rect.bottom = self.bg_height

    def draw(self, display_area):
        """
        繪製玩家
        display_area: pygame 的顯示區域
        """
        # 先繪製後方的燈焰（如果可見），再繪製玩家本體，讓燈焰位於玩家下方
        if self.burner_visible and hasattr(self, "burner_image"):
            # 計算燈焰的位置：置中於玩家下方
            burner_rect = self.burner_image.get_rect()
            # midtop 使燈焰的上中點對齊玩家的下中點
            # 微微上移幾像素，避免燈焰與玩家圖片邊緣重疊；同時使用玩家 rect 的中心
            burner_rect.midtop = (self.rect.centerx, self.rect.bottom - 6)
            display_area.blit(self.burner_image, burner_rect)

        display_area.blit(self.image, self.rect)


pygame.init()  # 啟動 pygame

###################### 載入圖片 ######################
bg_img = pygame.image.load("class15/image/space.png")  # 載入背景圖片
bg_rect = bg_img.get_rect()  # 取得圖片的矩形範圍
bg_width, bg_height = bg_rect.size  # 取得圖片寬高

###################### 視窗設定 ######################
screen = pygame.display.set_mode((bg_width, bg_height))  # 設定視窗大小與圖片相同
pygame.display.set_caption("背景循環移動範例")  # 設定視窗標題

###################### 背景移動參數 ######################
###################### 玩家初始化 ######################
# 玩家初始位置設在畫面中央
player_start_x = bg_width // 2
player_start_y = bg_height // 2
player = Player(
    player_start_x, player_start_y, "class15/image/fighter_M.png", bg_width, bg_height
)
# 設定背景初始 y 座標
bg_y1 = 0  # 第一張背景的 y 座標
bg_y2 = -bg_height  # 第二張背景的 y 座標（在畫面上方）
bg_speed = 10  # 背景向下移動速度（可調整）

###################### 主迴圈 ######################
clock = pygame.time.Clock()  # 建立時鐘物件，用於控制 FPS

while True:
    clock.tick(60)  # 設定每秒 60 FPS

    # 事件處理：關閉視窗時結束程式
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 取得鍵盤按鍵狀態
    keys = pygame.key.get_pressed()
    player.move(keys)  # 玩家移動

    # 更新背景座標，使其向下移動
    bg_y1 += bg_speed
    bg_y2 += bg_speed

    # 當背景完全移出畫面下方時，將其移回畫面上方
    if bg_y1 >= bg_height:
        bg_y1 = bg_y2 - bg_height
    if bg_y2 >= bg_height:
        bg_y2 = bg_y1 - bg_height

    # 繪製背景圖片（兩張，形成循環效果）
    screen.blit(bg_img, (0, bg_y1))
    screen.blit(bg_img, (0, bg_y2))

    # 繪製玩家
    player.draw(screen)

    # 更新畫面顯示
    pygame.display.update()
