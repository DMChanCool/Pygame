###################### 載入套件 ######################
import pygame
import sys
import random
import os


###################### 全域變數 ######################
score = 0  # 當前分數
highest_score = 0  # 最高分數
game_over = False  # 遊戲結束狀態
initial_player_y = 0  # 玩家初始高度（用於分數計算）


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
        self.velocity_y = 0  # 垂直速度
        self.jump_power = -12  # 跳躍初速度（負值代表向上）
        self.gravity = 0.5  # 重力加速度
        self.on_platform = False  # 是否站在平台上

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

    # === 步驟5: 優化平台碰撞檢查，支援多平台與多點檢查 ===
    def check_platform_collision(self, platforms):
        """
        檢查主角是否落在任一平台上，並處理彈跳
        platforms: 平台列表
        """
        # 僅在主角往下掉時檢查碰撞
        if self.velocity_y > 0:
            # 根據下落速度決定檢查點數量（每5像素一個檢查點）
            steps = max(1, int(self.velocity_y // 5))
            for step in range(1, steps + 1):
                # 計算每個檢查點的y座標
                check_y = self.rect.bottom + (step * self.velocity_y) / steps
                for platform in platforms:
                    # === 步驟10: 處理紅色消失平台 ===
                    if (
                        self.rect.right > platform.rect.left
                        and self.rect.left < platform.rect.right
                        and self.rect.bottom <= platform.rect.top
                        and check_y >= platform.rect.top
                        and check_y <= platform.rect.top + platform.rect.height
                    ):
                        if hasattr(platform, "is_breakable") and platform.is_breakable:
                            # 玩家踩到紅色平台，平台立即消失且不跳躍
                            platforms.remove(platform)
                            self.on_platform = False
                            return False
                        else:
                            # 一般平台正常彈跳
                            self.rect.bottom = platform.rect.top
                            self.velocity_y = self.jump_power
                            self.on_platform = True
                            return True
        self.on_platform = False
        return False

    # === 步驟9: 新增彈簧碰撞檢查方法 ===
    def check_spring_collision(self, springs):
        """
        檢查主角是否落在任一彈簧上，並給予更高跳躍力
        springs: 彈簧列表
        """
        # 僅在主角往下掉時檢查碰撞
        if self.velocity_y > 0:
            for spring in springs:
                # 檢查主角底部與彈簧頂部是否重疊，且左右有交集
                if (
                    self.rect.right > spring.rect.left
                    and self.rect.left < spring.rect.right
                    and self.rect.bottom <= spring.rect.top
                    and self.rect.bottom + self.velocity_y >= spring.rect.top
                ):
                    # 將主角底部對齊彈簧頂部
                    self.rect.bottom = spring.rect.top
                    self.velocity_y = -25  # 彈簧給予更高跳躍力
                    self.on_platform = True
                    return True
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
        self.is_breakable = False  # 是否為只能踩一次的消失平台

    def draw(self, display_area):
        """
        繪製平台
        display_area: 要繪製的平台視窗
        """
        pygame.draw.rect(display_area, self.color, self.rect)


# === 步驟10: 新增BreakablePlatform類別 ===
class BreakablePlatform(Platform):
    def __init__(self, x, y, width, height):
        """
        初始化紅色消失平台
        """
        super().__init__(x, y, width, height, (255, 0, 0))  # 紅色
        self.is_breakable = True


###################### 彈簧類別 ######################
class Spring:
    def __init__(self, x, y, width=20, height=10, color=(255, 255, 0)):
        """
        初始化彈簧道具
        x, y: 彈簧左上角座標
        width, height: 彈簧寬高
        color: 彈簧顏色 (預設黃色)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area):
        """
        繪製彈簧
        display_area: 要繪製的畫布
        """
        pygame.draw.rect(display_area, self.color, self.rect)


###################### 初始化設定 ######################
pygame.init()  # 啟動pygame

###################### 字型設定 ######################
# 載入中文字型，根據作業系統自動選擇
if os.name == "nt":
    # Windows
    font_path = "C:/Windows/Fonts/msjh.ttc"
elif os.name == "posix":
    # macOS 常見中文字型
    font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
else:
    font_path = None

try:
    font = pygame.font.Font(font_path, 28)
except:
    font = pygame.font.SysFont("Arial", 28)

###################### 遊戲視窗設定 ######################
win_width = 400
win_height = 600
pygame.display.set_caption("Doodle Jump - 畫面捲動與平台生成")
screen = pygame.display.set_mode((win_width, win_height))  # 設定視窗大小

###################### 主角設定 ######################
player_width = 30
player_height = 30
player_color = (0, 255, 0)  # 綠色
player_x = win_width // 2 - player_width // 2
player_y = win_height - 50 - player_height
player = Player(player_x, player_y, player_width, player_height, player_color)
initial_player_y = player.rect.y  # 記錄初始高度

###################### 平台設定 ######################
platform_w = 60
platform_h = 10
platform_color = (255, 255, 255)  # 白色
platforms = []  # 平台列表
springs = []  # 彈簧列表
SPRING_PROB = 0.2  # 彈簧生成機率20%

# 產生底部平台，確保玩家不會掉下去
platform_x = (win_width - platform_w) // 2
platform_y = win_height - platform_h - 10
base_platform = Platform(platform_x, platform_y, platform_w, platform_h, platform_color)
platforms.append(base_platform)

# 預設平台數量
PLATFORM_NUM = random.randint(8, 10) + 10  # 增加平台數量，讓畫面有更多平台
for i in range(PLATFORM_NUM - 1):  # 已有一個底部平台
    x = random.randint(0, win_width - platform_w)
    y = (win_height - 100) - (i * 60)
    # 只有分數超過100才產生紅色平台
    if score >= 100 and random.random() < 0.2:
        platform = BreakablePlatform(x, y, platform_w, platform_h)
    else:
        platform = Platform(x, y, platform_w, platform_h, platform_color)
    platforms.append(platform)
    # === 步驟8: 隨機在平台上生成彈簧 ===
    if random.random() < SPRING_PROB:
        spring_x = x + (platform_w - 20) // 2
        spring_y = y - 10
        springs.append(Spring(spring_x, spring_y))


###################### 畫面捲動與平台管理函式 ######################
def update_camera_and_platforms(
    player, platforms, win_height, platform_w, platform_h, platform_color
):
    """
    畫面捲動與平台動態生成/移除
    - 若主角上升到螢幕中間以上，畫面向下捲動，主角固定在中間
    - 移除掉出畫面下方的平台
    - 在最上方自動生成新平台，確保平台數量維持
    - 彈簧跟著平台一起移動，並移除離開畫面的彈簧
    - 分數超過100後有機率產生紅色消失平台
    """
    global score
    screen_middle = win_height // 2
    # 若主角高於畫面中間，畫面捲動
    if player.rect.y < screen_middle:
        camera_move = screen_middle - player.rect.y
        player.rect.y = screen_middle  # 主角固定在中間
        # 所有平台往下移動
        for platform in platforms:
            platform.rect.y += camera_move
        # === 彈簧也要跟著平台一起移動 ===
        for spring in springs:
            spring.rect.y += camera_move
        # 分數計算：每上升10像素加1分
        score += int(camera_move / 10)

    # 移除掉出畫面下方的平台
    platforms[:] = [p for p in platforms if p.rect.top < win_height]
    # === 彈簧離開畫面自動消失 ===
    springs[:] = [s for s in springs if s.rect.top < win_height]

    # 找出目前最高的平台y座標
    y_min = min([p.rect.y for p in platforms])
    # 若平台數量不足，補足到預設數量
    while len(platforms) < PLATFORM_NUM:
        x = random.randint(0, win_width - platform_w)
        y = y_min - 60  # 新平台在最高平台上方60像素
        # 只有分數超過100才產生紅色平台
        if score >= 100 and random.random() < 0.2:
            new_platform = BreakablePlatform(x, y, platform_w, platform_h)
        else:
            new_platform = Platform(x, y, platform_w, platform_h, platform_color)
        platforms.append(new_platform)
        y_min = y  # 更新最高平台座標
        # === 新生成的平台有機率生成彈簧 ===
        if random.random() < SPRING_PROB:
            spring_x = x + (platform_w - 20) // 2
            spring_y = y - 10
            springs.append(Spring(spring_x, spring_y))


###################### 新增fps設定 ######################
FPS = pygame.time.Clock()  # 設定時鐘

###################### 遊戲主迴圈 ######################
while True:
    FPS.tick(60)  # 每秒最多60幀，控制遊戲速度
    screen.fill((0, 0, 0))  # 清空畫面

    if not game_over:
        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 按下關閉視窗
                pygame.quit()
                sys.exit()

        # 取得目前按下的按鍵狀態
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player.move(-1, win_width)
        if keys[pygame.K_RIGHT]:
            player.move(1, win_width)

        # 主角自動下落
        player.apply_gravity()  # 應用重力，主角自動下落

        # === 步驟9: 先檢查彈簧碰撞，再檢查平台碰撞 ===
        spring_hit = player.check_spring_collision(springs)
        if not spring_hit:
            player.check_platform_collision(platforms)  # 檢查所有平台碰撞並彈跳

        # 畫面捲動與平台動態管理
        update_camera_and_platforms(
            player, platforms, win_height, platform_w, platform_h, platform_color
        )

        # 判斷遊戲結束：主角掉出畫面下方
        if player.rect.top > win_height:
            game_over = True
            if score > highest_score:
                highest_score = score

        # 繪製主角與平台
        player.draw(screen)  # 繪製主角
        for platform in platforms:
            platform.draw(screen)  # 繪製所有平台
        # === 繪製所有彈簧道具 ===
        for spring in springs:
            spring.draw(screen)

        # 顯示分數
        score_text = font.render(f"分數: {score}", True, (255, 255, 0))
        screen.blit(score_text, (10, 10))
        high_text = font.render(f"最高分: {highest_score}", True, (255, 255, 255))
        screen.blit(high_text, (10, 40))

    else:
        # 遊戲結束畫面
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # 按下關閉視窗
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                # 重新開始遊戲
                player.rect.x = win_width // 2 - player_width // 2
                player.rect.y = win_height - 50 - player_height
                player.velocity_y = 0
                platforms.clear()
                base_platform = Platform(
                    platform_x, platform_y, platform_w, platform_h, platform_color
                )
                platforms.append(base_platform)
                springs.clear()
                # 分數歸零，紅色平台不會產生
                score = 0
                for i in range(PLATFORM_NUM - 1):
                    x = random.randint(0, win_width - platform_w)
                    y = (win_height - 100) - (i * 60)
                    # 只有分數超過100才產生紅色平台
                    if score >= 100 and random.random() < 0.2:
                        platform = BreakablePlatform(x, y, platform_w, platform_h)
                    else:
                        platform = Platform(
                            x, y, platform_w, platform_h, platform_color
                        )
                    platforms.append(platform)
                    if random.random() < SPRING_PROB:
                        spring_x = x + (platform_w - 20) // 2
                        spring_y = y - 10
                        springs.append(Spring(spring_x, spring_y))
                game_over = False

        # 顯示分數與最高分
        over_text = font.render("遊戲結束", True, (255, 0, 0))
        score_text = font.render(f"分數: {score}", True, (255, 255, 0))
        high_text = font.render(f"最高分: {highest_score}", True, (255, 255, 255))
        restart_text = font.render("按任意鍵重新開始", True, (0, 255, 255))
        screen.blit(
            over_text,
            (win_width // 2 - over_text.get_width() // 2, win_height // 2 - 80),
        )
        screen.blit(
            score_text,
            (win_width // 2 - score_text.get_width() // 2, win_height // 2 - 40),
        )
        screen.blit(
            high_text, (win_width // 2 - high_text.get_width() // 2, win_height // 2)
        )
        screen.blit(
            restart_text,
            (win_width // 2 - restart_text.get_width() // 2, win_height // 2 + 60),
        )

    pygame.display.update()  # 更新畫面
