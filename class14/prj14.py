###################### 載入套件 ######################
import pygame
import sys
import random
import os


# 載入 Doodle Jump 圖片精靈的函式
def load_doodle_sprites():
    """
    載入 Doodle Jump 遊戲所需的圖片，並裁切出各種遊戲物件的精靈圖。
    回傳一個 sprites 字典，key 為物件名稱，value 為 pygame.Surface 物件。
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, "image")
    src_path = os.path.join(image_dir, "src.png")
    sprites = {}
    try:
        source_image = pygame.image.load(src_path).convert_alpha()
        sprite_data = {
            "std_platform": (0, 0, 116, 30),
            "break_platform": (0, 145, 124, 33),
            "spring_normal": (376, 188, 71, 35),
        }
        for key in ["std_platform", "break_platform", "spring_normal"]:
            x, y, w, h = sprite_data[key]
            sprites[key] = source_image.subsurface(pygame.Rect(x, y, w, h)).copy()
    except Exception as e:
        pass  # 若 src.png 不存在則 sprites 不含平台/彈簧圖片
    # 載入角色圖片
    for key, fname in [
        ("player_left_jumping", "l.png"),
        ("player_left_falling", "ls.png"),
        ("player_right_jumping", "r.png"),
        ("player_right_falling", "rs.png"),
    ]:
        img_path = os.path.join(image_dir, fname)
        if os.path.exists(img_path):
            try:
                sprites[key] = pygame.image.load(img_path).convert_alpha()
            except Exception:
                pass
    return sprites


###################### 全域變數 ######################
score = 0  # 當前分數
highest_score = 0  # 最高分數
game_over = False  # 遊戲結束狀態
initial_player_y = 0  # 玩家初始高度（用於分數計算）


# === 步驟11: 載入圖片與裁切精靈 ===
def load_doodle_sprites():
    """
    載入Doodle Jump遊戲所需的圖片，並裁切出各種遊戲物件的精靈圖。
    回傳一個sprites字典，key為物件名稱，value為pygame.Surface物件。
    """
    # 設定圖片資料夾路徑為目前python檔案所在目錄
    base_dir = os.path.dirname(os.path.abspath(__file__))
    image_dir = os.path.join(base_dir, "image")
    src_path = os.path.join(image_dir, "src.png")

    # 載入主圖片（包含多個物件）
    source_image = pygame.image.load(src_path).convert_alpha()

    # 定義各物件在src.png中的裁切座標與寬高
    sprite_data = {
        "std_platform": (0, 0, 116, 30),  # 標準平台
        "break_platform": (0, 145, 124, 33),  # 可破壞平台
        "spring_normal": (376, 188, 71, 35),  # 普通彈簧
        # 玩家角色圖片路徑
        "player_left_jumping": os.path.join(image_dir, "l.png"),  # 左跳躍
        "player_left_falling": os.path.join(image_dir, "ls.png"),  # 左下落
        "player_right_jumping": os.path.join(image_dir, "r.png"),  # 右跳躍
        "player_right_falling": os.path.join(image_dir, "rs.png"),  # 右下落
    }

    sprites = {}

    # 處理需要裁切的圖片（平台、彈簧等）
    for key in ["std_platform", "break_platform", "spring_normal"]:
        x, y, w, h = sprite_data[key]
        # 使用subsurface裁切出對應區域
        sprites[key] = source_image.subsurface(pygame.Rect(x, y, w, h)).copy()

    # 處理玩家角色圖片（直接載入單張png）
    for key in [
        "player_left_jumping",
        "player_left_falling",
        "player_right_jumping",
        "player_right_falling",
    ]:
        img_path = sprite_data[key]
        sprites[key] = pygame.image.load(img_path).convert_alpha()

    return sprites


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
        self.velocity_y = 0  # 垂直速度
        self.jump_power = -12  # 跳躍初速度（負值代表向上）
        self.gravity = 0.5  # 重力加速度
        self.on_platform = False  # 是否站在平台上

    def draw(
        self, display_area, sprites=None, facing_right=True, jumping=False, velocity_y=0
    ):
        """
        繪製主角，優先使用 sprites 圖片，若無則用方塊
        display_area: 要繪製的畫布
        sprites: 圖片字典
        facing_right: 是否面向右
        jumping: 是否跳躍中
        velocity_y: 垂直速度（判斷上升/下降）
        """
        use_image = False
        if sprites:
            if facing_right:
                if velocity_y < 0:
                    key = "player_right_jumping"
                else:
                    key = "player_right_falling"
            else:
                if velocity_y < 0:
                    key = "player_left_jumping"
                else:
                    key = "player_left_falling"
            if key in sprites:
                img = sprites[key]
                img = pygame.transform.smoothscale(
                    img, (self.rect.width, self.rect.height)
                )
                display_area.blit(img, self.rect)
                use_image = True
        if not use_image:
            pygame.draw.rect(display_area, self.color, self.rect)

    def move(self, direction, bg_x):
        self.rect.x += direction * self.speed
        if self.rect.right < 0:
            self.rect.left = bg_x
        elif self.rect.left > bg_x:
            self.rect.right = 0

    def apply_gravity(self):
        self.velocity_y += self.gravity
        self.rect.y += int(self.velocity_y)

    def check_platform_collision(self, platforms):
        if self.velocity_y > 0:
            steps = max(1, int(self.velocity_y // 5))
            for step in range(1, steps + 1):
                check_y = self.rect.bottom + (step * self.velocity_y) / steps
                for platform in platforms:
                    if (
                        self.rect.right > platform.rect.left
                        and self.rect.left < platform.rect.right
                        and self.rect.bottom <= platform.rect.top
                        and check_y >= platform.rect.top
                        and check_y <= platform.rect.top + platform.rect.height
                    ):
                        if hasattr(platform, "is_breakable") and platform.is_breakable:
                            self.rect.bottom = platform.rect.top
                            self.velocity_y = self.jump_power
                            self.on_platform = True
                            platforms.remove(platform)
                            if "jump_sound" in globals() and jump_sound:
                                jump_sound.play()
                            return True
                        else:
                            self.rect.bottom = platform.rect.top
                            self.velocity_y = self.jump_power
                            self.on_platform = True
                            if "jump_sound" in globals() and jump_sound:
                                jump_sound.play()
                            return True
        self.on_platform = False
        return False

    def check_spring_collision(self, springs):
        if self.velocity_y > 0:
            for spring in springs:
                if (
                    self.rect.right > spring.rect.left
                    and self.rect.left < spring.rect.right
                    and self.rect.bottom <= spring.rect.top
                    and self.rect.bottom + self.velocity_y >= spring.rect.top
                ):
                    self.rect.bottom = spring.rect.top
                    self.velocity_y = -25
                    self.on_platform = True
                    if "spring_sound" in globals() and spring_sound:
                        spring_sound.play()
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

    def draw(self, display_area, sprites=None):
        """
        繪製平台，優先使用 sprites 圖片，若無則用方塊
        display_area: 要繪製的平台視窗
        sprites: 圖片字典
        """
        use_image = False
        if sprites:
            key = "std_platform"
            if hasattr(self, "is_breakable") and self.is_breakable:
                key = "break_platform"
            if key in sprites:
                img = sprites[key]
                img = pygame.transform.smoothscale(
                    img, (self.rect.width, self.rect.height)
                )
                display_area.blit(img, self.rect)
                use_image = True
        if not use_image:
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
    def __init__(self, x, y, width=40, height=20, color=(255, 255, 0)):
        """
        初始化彈簧道具
        x, y: 彈簧左上角座標
        width, height: 彈簧寬高
        color: 彈簧顏色 (預設黃色)
        """
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, display_area, sprites=None):
        """
        繪製彈簧，優先使用 sprites 圖片，若無則用方塊
        display_area: 要繪製的畫布
        sprites: 圖片字典
        """
        use_image = False
        if sprites and "spring_normal" in sprites:
            img = sprites["spring_normal"]
            img = pygame.transform.smoothscale(img, (self.rect.width, self.rect.height))
            display_area.blit(img, self.rect)
            use_image = True
        if not use_image:
            pygame.draw.rect(display_area, self.color, self.rect)


###################### 初始化設定 ######################
pygame.init()  # 啟動pygame


# === 載入音效檔案 ===
# 取得音效資料夾路徑
base_dir = os.path.dirname(os.path.abspath(__file__))
sound_dir = os.path.join(base_dir, "sound")
# 跳躍音效檔案路徑
jump_sound_path = os.path.join(sound_dir, "jump.mp3")
# 彈簧音效檔案路徑
spring_sound_path = os.path.join(sound_dir, "spring.mp3")
# 載入跳躍音效
try:
    jump_sound = pygame.mixer.Sound(jump_sound_path)
except Exception as e:
    jump_sound = None
    print(f"[警告] 跳躍音效載入失敗: {e}")
# 載入彈簧音效
try:
    spring_sound = pygame.mixer.Sound(spring_sound_path)
except Exception as e:
    spring_sound = None
    print(f"[警告] 彈簧音效載入失敗: {e}")
# 註：若音效檔案不存在或格式不支援，將不會播放音效，並於終端顯示警告

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
# 載入所有遊戲精靈圖片（必須在設定視窗之後）
sprites = load_doodle_sprites()

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
    screen.fill((255, 255, 255))  # 清空畫面，背景改為白色

    # === 新增角色面向與跳躍狀態變數 ===
    if "facing_right" not in globals():
        facing_right = True  # 預設面向右
    if "jumping" not in globals():
        jumping = False
    direction = 0  # -1:左, 1:右, 0:無

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
            direction = -1
        if keys[pygame.K_RIGHT]:
            player.move(1, win_width)
            direction = 1
        # 根據 direction 決定面向
        if direction > 0:
            facing_right = True
        elif direction < 0:
            facing_right = False

        # 主角自動下落
        player.apply_gravity()  # 應用重力，主角自動下落

        # === 判斷是否跳躍中 ===
        if player.velocity_y < 0:
            jumping = True
        elif player.velocity_y > 0:
            jumping = False

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
        player.draw(
            screen,
            sprites=sprites,
            facing_right=facing_right,
            jumping=jumping,
            velocity_y=player.velocity_y,
        )  # 傳遞狀態給 draw
        for platform in platforms:
            platform.draw(screen, sprites=sprites)
        # === 繪製所有彈簧道具 ===
        for spring in springs:
            spring.draw(screen, sprites=sprites)

        # 顯示分數
        score_text = font.render(f"分數: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))
        high_text = font.render(f"最高分: {highest_score}", True, (0, 0, 0))
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
        over_text = font.render("遊戲結束", True, (0, 0, 0))
        score_text = font.render(f"分數: {score}", True, (0, 0, 0))
        high_text = font.render(f"最高分: {highest_score}", True, (0, 0, 0))
        restart_text = font.render("按任意鍵重新開始", True, (0, 0, 0))
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
