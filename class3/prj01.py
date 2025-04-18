######################匯入模組######################
import pygame
import sys

######################初始化######################
pygame.init()  # 啟動pygame
width = 640  # 視窗寬度
height = 320  # 視窗高度

######################建立視窗及物件######################
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("My Game")

#######################建立畫布######################
bg = pygame.Surface((width, height))  # 建立畫布
bg.fill((255, 255, 255))  # 填充背景顏色

#########################繪製圖形######################
# 繪製圓形
pygame.draw.circle(bg, (0, 0, 255), (200, 100), 30, 0)  # 圓心(200,100) 半徑30 顏色藍色
pygame.draw.circle(bg, (0, 0, 255), (400, 100), 30, 0)

# 繪製矩形
pygame.draw.rect(bg, (255, 0, 0), (100, 200, 100, 50), 0)
# 左上角(100,200) 寬100 高50 顏色紅色

# 繪製橢圓形
pygame.draw.ellipse(bg, (0, 255, 0), (300, 200, 100, 50), 0)
# 左上角(300,200) 寬100 高50 顏色綠色

# 畫線
pygame.draw.line(bg, (255, 255, 0), (50, 50), (200, 200), 5)

# 畫多邊形
pygame.draw.polygon(
    bg, (255, 0, 255), [(50, 50), (200, 50), (200, 200), (50, 200)], 0
)  # 顏色紫色
pygame.draw.polygon(
    bg, (0, 255, 255), [(300, 50), (400, 50), (400, 150), (300, 150)], 0
)

# 畫弧
pygame.draw.arc(bg, (0, 0, 0), (50, 50, 100, 100), 0, 3.14, 5)  # 顏色黑色


######################循環偵測######################
paint = False
color = (0, 255, 255)
while True:
    x, y = pygame.mouse.get_pos()  # 取得滑鼠座標
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按x關閉視窗
            sys.exit()  # 離開

        if event.type == pygame.MOUSEBUTTONDOWN:  # 按下滑鼠
            print("click!!!")
            print(f"Mouse pos: {x}, {y}")
            paint = not (paint)

    if paint:
        pygame.draw.circle(bg, color, (x, y), 10, 0)
    screen.blit(bg, (0, 0))  # 畫布放在視窗左上角
    pygame.display.update()  # 更新視窗
