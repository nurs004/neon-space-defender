import pygame
import random
import sys
import json
import os
from enum import Enum
from dataclasses import dataclass

# ============= НАСТРОЙКИ =============
WIDTH, HEIGHT = 600, 800
FPS = 60

# Цвета
COLOR_BG = (10, 10, 20)
COLOR_SHIP = (0, 255, 255)
COLOR_LASER = (255, 0, 255)
COLOR_SPREAD = (0, 255, 100)
COLOR_ENEMY = (255, 50, 50)
COLOR_STAR = (200, 200, 200)
COLOR_BONUS = (0, 255, 100)
COLOR_HEALTH = (255, 100, 0)
COLOR_TEXT = (255, 255, 255)
COLOR_UI_BG = (25, 25, 40)

# Режимы стрельбы
class FireMode(Enum):
    NORMAL = 1
    SPREAD = 2
    LASER = 3
    DOUBLE = 4

# Типы врагов
class EnemyType(Enum):
    NORMAL = 1
    FAST = 2
    TANK = 3
    MINI = 4
    BOSS = 5

# --- ИНИЦИАЛИЗАЦИЯ ---
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Neon Space Defender")
clock = pygame.time.Clock()

# Безопасный шрифт
try:
    try:
        game_font = pygame.font.SysFont('arial', 28, bold=True)
        title_font = pygame.font.SysFont('arial', 48, bold=True)
        small_font = pygame.font.SysFont('arial', 18)
    except:
        available = pygame.font.get_fonts()
        if available:
            font_name = available[0]
            game_font = pygame.font.SysFont(font_name, 28, bold=True)
            title_font = pygame.font.SysFont(font_name, 48, bold=True)
            small_font = pygame.font.SysFont(font_name, 18)
        else:
            game_font = pygame.font.Font(None, 28)
            title_font = pygame.font.Font(None, 48)
            small_font = pygame.font.Font(None, 18)
except Exception as e:
    game_font = pygame.font.Font(None, 28)
    title_font = pygame.font.Font(None, 48)
    small_font = pygame.font.Font(None, 18)

# --- КЛАССЫ ОБЪЕКТОВ ---

class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH//2, HEIGHT - 70, 40, 40)
        self.speed = 7
        self.lasers = []
        self.last_shot = 0
        self.health = 3  # Жизни
        self.max_health = 5
        self.invincible_time = 0
        self.fire_rate = 250  # Можно улучшать
        self.fire_mode = FireMode.NORMAL
        self.has_shield = False
        self.shield_time = 0
        self.dual_gun = False
        self.dual_gun_time = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            if self.rect.left > 0: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            if self.rect.right < WIDTH: self.rect.x += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.fire_rate:
            if self.fire_mode == FireMode.NORMAL:
                self.lasers.append(pygame.Rect(self.rect.centerx - 2, self.rect.top, 4, 15))
            elif self.fire_mode == FireMode.SPREAD:
                # Спрей из 3 лазеров
                for dx in [-5, 0, 5]:
                    self.lasers.append(pygame.Rect(self.rect.centerx + dx - 2, self.rect.top, 4, 15))
            elif self.fire_mode == FireMode.LASER:
                # Мощный лазер
                self.lasers.append(pygame.Rect(self.rect.centerx - 4, self.rect.top, 8, 20))
            elif self.fire_mode == FireMode.DOUBLE:
                # Двойная стрельба по сторонам
                self.lasers.append(pygame.Rect(self.rect.centerx - 10, self.rect.top, 4, 15))
                self.lasers.append(pygame.Rect(self.rect.centerx + 8, self.rect.top, 4, 15))
            self.last_shot = now

    def take_damage(self):
        if self.invincible_time <= 0:
            self.health -= 1
            self.invincible_time = 120  # 2 секунды неуязвимости

    def update(self):
        if self.invincible_time > 0:
            self.invincible_time -= 1

    def draw(self, surf):
        # Мигание при неуязвимости
        if self.invincible_time > 0 and (self.invincible_time // 10) % 2 == 0:
            return
        
        # Рисуем самолёт
        cx, cy = self.rect.centerx, self.rect.centery
        w, h = 20, 30
        
        # Корпус самолёта
        pygame.draw.polygon(surf, COLOR_SHIP, [
            (cx, cy - h//2),      # Нос
            (cx - w//2, cy),      # Левое крыло
            (cx + w//2, cy),      # Правое крыло
            (cx, cy + h//2)       # Хвост
        ])
        
        # Обводка
        pygame.draw.polygon(surf, (255, 255, 255), [
            (cx, cy - h//2),
            (cx - w//2, cy),
            (cx + w//2, cy),
            (cx, cy + h//2)
        ], 2)
        
        # Кабина пилота
        pygame.draw.circle(surf, (100, 255, 255), (cx, cy - 5), 3)
        
        # Крылья (детали)
        pygame.draw.line(surf, (255, 255, 255), (cx - 12, cy - 2), (cx - 10, cy + 2), 1)
        pygame.draw.line(surf, (255, 255, 255), (cx + 12, cy - 2), (cx + 10, cy + 2), 1)

class Enemy:
    def __init__(self, wave=1):
        self.rect = pygame.Rect(random.randint(0, WIDTH-40), -50, 40, 30)
        self.speed = random.uniform(2 + wave*0.5, 5 + wave*0.5)
        self.health = 1 + (wave // 3)

    def update(self):
        self.rect.y += self.speed

    def take_damage(self):
        self.health -= 1

    def draw(self, surf):
        # Рисуем звездолёт врага
        cx, cy = self.rect.centerx, self.rect.centery
        w, h = self.rect.width // 2, self.rect.height // 2
        
        # Основной корпус (звёзда)
        points = [
            (cx, cy - h),           # Верх
            (cx + w//2, cy - h//3),  # Верх-право
            (cx + w, cy),            # Право
            (cx + w//2, cy + h//3),  # Низ-право
            (cx, cy + h),            # Низ
            (cx - w//2, cy + h//3),  # Низ-лево
            (cx - w, cy),            # Лево
            (cx - w//2, cy - h//3)   # Верх-лево
        ]
        
        pygame.draw.polygon(surf, COLOR_ENEMY, points)
        pygame.draw.polygon(surf, (255, 100, 100), points, 2)
        
        # Окно кабины
        pygame.draw.circle(surf, (255, 255, 255), (cx, cy - 3), 2)
        
        # Здоровье врага
        if self.health > 1:
            health_bar_w = self.rect.width * (self.health / (1 + (self.health)))
            pygame.draw.rect(surf, COLOR_HEALTH, (self.rect.x, self.rect.y - 7, health_bar_w, 3))
            pygame.draw.rect(surf, (255, 255, 255), (self.rect.x, self.rect.y - 7, self.rect.width, 3), 1)

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.bonus_type = bonus_type  # 'health', 'firerate', 'shield'
        self.speed = 3

    def update(self):
        self.rect.y += self.speed

    def draw(self, surf):
        pygame.draw.rect(surf, COLOR_BONUS, self.rect)
        if self.bonus_type == 'health':
            pygame.draw.line(surf, (255, 255, 255), (self.rect.centerx - 5, self.rect.centerx), (self.rect.centerx + 5, self.rect.centerx), 2)
            pygame.draw.line(surf, (255, 255, 255), (self.rect.centerx, self.rect.centery - 5), (self.rect.centerx, self.rect.centery + 5), 2)
        elif self.bonus_type == 'firerate':
            pygame.draw.polygon(surf, (255, 255, 255), [(self.rect.centerx, self.rect.centery - 8), (self.rect.centerx + 8, self.rect.centery + 4), (self.rect.centerx - 8, self.rect.centery + 4)])


# --- СЛУЖЕБНЫЕ ФУНКЦИИ ---

def load_high_score():
    if os.path.exists("highscore.json"):
        try:
            with open("highscore.json", "r") as f:
                data = json.load(f)
                return data.get("score", 0)
        except:
            return 0
    return 0

def save_high_score(score):
    try:
        with open("highscore.json", "w") as f:
            json.dump({"score": score}, f)
    except:
        pass

def show_menu(high_score):
    """Главное меню"""
    waiting = True
    menu_timer = 0
    
    while waiting:
        clock.tick(FPS)
        screen.fill(COLOR_BG)
        
        # Звёезды в фоне
        for _ in range(50):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            pygame.draw.circle(screen, COLOR_STAR, (x, y), 1)
        
        # Заголовок
        menu_timer += 1
        y_offset = int(10 * (0.5 + 0.5 * (1 + pygame.math.Vector2(1, 0).normalize().length())))
        title = title_font.render("NEON SPACE", True, COLOR_SHIP)
        title_rect = title.get_rect(center=(WIDTH//2, 100 + y_offset))
        screen.blit(title, title_rect)
        
        defender = title_font.render("DEFENDER", True, COLOR_LASER)
        defender_rect = defender.get_rect(center=(WIDTH//2, 180))
        screen.blit(defender, defender_rect)
        
        # Инструкции
        inst1 = game_font.render("СТРЕЛКИ или A/D - движение", True, COLOR_TEXT)
        inst2 = game_font.render("ПРОБЕЛ - стрелять", True, COLOR_TEXT)
        inst3 = small_font.render("R - смена режима стрельбы", True, COLOR_BONUS)
        screen.blit(inst1, (WIDTH//2 - inst1.get_width()//2, 300))
        screen.blit(inst2, (WIDTH//2 - inst2.get_width()//2, 350))
        screen.blit(inst3, (WIDTH//2 - inst3.get_width()//2, 380))
        
        # Рекорд
        hs_text = game_font.render(f"РЕКОРД: {high_score}", True, COLOR_BONUS)
        screen.blit(hs_text, (WIDTH//2 - hs_text.get_width()//2, 420))
        
        # Кнопка старта
        start_text = game_font.render("Нажмите ПРОБЕЛ для начала", True, 
                                      COLOR_HEALTH if (menu_timer // 15) % 2 == 0 else COLOR_TEXT)
        screen.blit(start_text, (WIDTH//2 - start_text.get_width()//2, 550))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    return True

def show_game_over(score, high_score):
    """Экран конца игры"""
    if score > high_score:
        high_score = score
        save_high_score(high_score)
        new_record = True
    else:
        new_record = False
    
    waiting = True
    while waiting:
        clock.tick(FPS)
        screen.fill(COLOR_BG)
        
        # Заголовок
        game_over = title_font.render("GAME OVER", True, COLOR_ENEMY)
        screen.blit(game_over, (WIDTH//2 - game_over.get_width()//2, 150))
        
        # Счёт
        score_text = game_font.render(f"Счежт: {score}", True, COLOR_TEXT)
        screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 280))
        
        # Рекорд
        record_text = game_font.render(f"РЕКОРД: {high_score}", True, COLOR_BONUS)
        screen.blit(record_text, (WIDTH//2 - record_text.get_width()//2, 330))
        
        if new_record:
            record_tag = game_font.render("⭐ НОВЫЙ РЕКОРД! ⭐", True, COLOR_HEALTH)
            screen.blit(record_tag, (WIDTH//2 - record_tag.get_width()//2, 380))
        
        # Кнопка рестарта
        restart_text = game_font.render("ПРОБЕЛ для рестарта", True, COLOR_SHIP)
        screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, 480))
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, high_score
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False
    
    return True, high_score

# --- ГЛАВНЫЙ ЦИКЛ ---

def main():
    high_score = load_high_score()
    
    while True:
        # Показываем меню
        if not show_menu(high_score):
            break
        
        # Игровой цикл
        player = Player()
        enemies = []
        bonuses = []
        stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(50)]
        
        score = 0
        wave = 1
        enemies_killed_in_wave = 0
        spawn_timer = 0
        bonus_chance = 0.3
        running = True

        while running:
            dt = clock.tick(FPS)
            screen.fill(COLOR_BG)

            # 1. Звёездное небо (фон)
            for star in stars:
                star[1] += 2
                if star[1] > HEIGHT: 
                    star[1] = 0
                    star[0] = random.randint(0, WIDTH)
                pygame.draw.circle(screen, COLOR_STAR, star, 1)

            # 2. События
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    fire_modes = [FireMode.NORMAL, FireMode.SPREAD, FireMode.LASER, FireMode.DOUBLE]
                    current_idx = fire_modes.index(player.fire_mode)
                    player.fire_mode = fire_modes[(current_idx + 1) % len(fire_modes)]

            # 3. Управление
            keys = pygame.key.get_pressed()
            player.move(keys)
            if keys[pygame.K_SPACE]:
                player.shoot()
            player.update()

            # 4. Спавн врагов (волны становятся сложнее)
            spawn_timer += dt
            spawn_delay = max(300, 800 - wave * 50)  # Чем выше волна, тем быстрее
            if spawn_timer > spawn_delay:
                enemies.append(Enemy(wave))
                spawn_timer = 0

            # 5. Обновление лазеров
            for l in player.lasers[:]:
                l.y -= 12
                if l.bottom < 0:
                    player.lasers.remove(l)

            # 6. Обновление врагов и коллизии
            for e in enemies[:]:
                e.update()
                if e.rect.top > HEIGHT:
                    enemies.remove(e)
                    score = max(0, score - 5)
                    continue

                # Проверка столкновения с игроком
                if e.rect.colliderect(player.rect):
                    player.take_damage()
                    if player.health <= 0:
                        running = False
                    if e in enemies:
                        enemies.remove(e)
                        enemies_killed_in_wave += 1
                    continue

                # Проверка попадания лазером
                for l in player.lasers[:]:
                    if e.rect.colliderect(l):
                        e.take_damage()
                        if l in player.lasers:
                            player.lasers.remove(l)
                        
                        if e.health <= 0:
                            if e in enemies:
                                enemies.remove(e)
                            score += 10 + wave * 5  # Больше очков на высоких волнах
                            enemies_killed_in_wave += 1
                            
                            # Спавн бонуса
                            if random.random() < bonus_chance:
                                bonus_type = random.choice(['health', 'firerate'])
                                bonuses.append(Bonus(e.rect.centerx, e.rect.centery, bonus_type))
                        break

            # 7. Обновление бонусов
            for b in bonuses[:]:
                b.update()
                if b.rect.top > HEIGHT:
                    bonuses.remove(b)
                    continue
                
                if b.rect.colliderect(player.rect):
                    if b.bonus_type == 'health' and player.health < 5:
                        player.health += 1
                    elif b.bonus_type == 'firerate':
                        player.fire_rate = max(100, player.fire_rate - 30)
                    bonuses.remove(b)

            # 8. Проверка волны
            if enemies_killed_in_wave >= 5 + wave * 2:
                wave += 1
                enemies_killed_in_wave = 0
                bonus_chance += 0.05

            # 9. Отрисовка
            for l in player.lasers:
                pygame.draw.rect(screen, COLOR_LASER, l)
            
            for e in enemies:
                e.draw(screen)
            
            for b in bonuses:
                b.draw(screen)
            
            player.draw(screen)

            # UI (Счет, жизни, волна)
            score_text = game_font.render(f"SCORE: {score}", True, COLOR_TEXT)
            wave_text = game_font.render(f"WAVE: {wave}", True, COLOR_BONUS)
            health_text = game_font.render(f"HP: {player.health}", True, COLOR_HEALTH if player.health > 1 else COLOR_ENEMY)
            
            # Текущий режим стрельбы
            fire_mode_names = {FireMode.NORMAL: "NORMAL", FireMode.SPREAD: "SPREAD", 
                              FireMode.LASER: "LASER", FireMode.DOUBLE: "DOUBLE"}
            fire_text = small_font.render(f"Mode: {fire_mode_names[player.fire_mode]}", True, COLOR_LASER)
            
            screen.blit(score_text, (20, 20))
            screen.blit(wave_text, (WIDTH - 200, 20))
            screen.blit(health_text, (WIDTH - 200, 60))
            screen.blit(fire_text, (20, 60))

            pygame.display.flip()

        # Показываем экран конца игры
        continue_game, high_score = show_game_over(score, high_score)
        if not continue_game:
            break

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

