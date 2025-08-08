import pygame  # 載入 pygame 套件
import sys  # 載入系統相關套件，方便結束程式

###################### 初始化設定 ######################
pygame.init()  # 啟動 pygame

###################### 載入圖片 ######################
bg_img = pygame.image.load("class15/image/space.png")  # 載入背景圖片
bg_rect = bg_img.get_rect()  # 取得圖片的矩形範圍
bg_width, bg_height = bg_rect.size  # 取得圖片寬高

###################### 視窗設定 ######################
screen = pygame.display.set_mode((bg_width, bg_height))  # 設定視窗大小與圖片相同
pygame.display.set_caption("背景循環移動範例")  # 設定視窗標題

###################### 背景移動參數 ######################
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

    # 更新畫面顯示
    pygame.display.update()
