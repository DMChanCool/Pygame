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

######################循環偵測######################
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # 按x關閉視窗
            sys.exit()  # 離開
