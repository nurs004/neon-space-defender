"""
Neon Space Defender - Professional Version
Kivy-based space shooter game for Android/Mobile
Beautiful UI, realistic graphics, full game features
"""

import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.properties import NumericProperty, ObjectProperty
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import (
    Line, Ellipse, Triangle, Color, Rectangle, 
    PushMatrix, PopMatrix, Rotate, Scale, Translate
)
import random
import json
import os
from enum import Enum
from math import cos, sin, pi, sqrt

# Настройки экрана
Window.size = (600, 800)

class GameState(Enum):
    MENU = 1
    GAME = 2
    PAUSED = 3
    GAME_OVER = 4
    SETTINGS = 5
    HELP = 6

class Particle:
    """Класс для частиц взрыва и эффектов"""
    def __init__(self, x, y, vx, vy, color, life_time=0.5):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life_time = life_time
        self.max_life = life_time
        self.size = random.randint(2, 6)

    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.life_time -= dt
        return self.life_time > 0

class FireMode(Enum):
    NORMAL = 1
    SPREAD = 2
    LASER = 3
    DOUBLE = 4

class EnemyType(Enum):
    NORMAL = 1
    FAST = 2
    TANK = 3
    MINI = 4
    BOSS = 5

class Player:
    def __init__(self, x=300, y=700):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.speed = 400
        self.lasers = []
        self.health = 3
        self.max_health = 5
        self.invincible_time = 0
        self.fire_rate = 0.15
        self.last_shot = 0
        self.fire_mode = FireMode.NORMAL
        self.has_shield = False
        self.shield_time = 0
        self.angle = 0

    def move(self, touch_x, touch_y):
        """Плавное движение к точке касания"""
        if touch_x is not None:
            if touch_x < self.x - 5:
                self.x = max(0, self.x - 8)
            elif touch_x > self.x + 5:
                self.x = min(600 - self.width, self.x + 8)
            
            if touch_y < self.y - 5:
                self.y = max(700 - 150, self.y - 8)
            elif touch_y > self.y + 5:
                self.y = min(800 - self.height, self.y + 8)

    def shoot(self):
        """Стрельба в зависимости от режима"""
        if self.fire_mode == FireMode.NORMAL:
            self.lasers.append({'x': self.x + 18, 'y': self.y, 'vx': 0, 'vy': -600})
        elif self.fire_mode == FireMode.SPREAD:
            for vx in [-100, -50, 0, 50, 100]:
                self.lasers.append({'x': self.x + 18, 'y': self.y, 'vx': vx, 'vy': -600})
        elif self.fire_mode == FireMode.LASER:
            self.lasers.append({'x': self.x + 15, 'y': self.y, 'vx': 0, 'vy': -800, 'width': 12})
        elif self.fire_mode == FireMode.DOUBLE:
            self.lasers.append({'x': self.x + 8, 'y': self.y, 'vx': 0, 'vy': -600})
            self.lasers.append({'x': self.x + 28, 'y': self.y, 'vx': 0, 'vy': -600})

    def take_damage(self):
        if self.has_shield:
            self.has_shield = False
            return
        self.health -= 1

    def update(self, dt):
        self.invincible_time = max(0, self.invincible_time - dt)
        self.shield_time = max(0, self.shield_time - dt)
        if self.shield_time <= 0:
            self.has_shield = False

class Enemy:
    def __init__(self, enemy_type=EnemyType.NORMAL, wave=1):
        self.type = enemy_type
        self.wave = wave
        self.x = random.randint(0, 570)
        self.y = -50
        self.angle = 0
        
        if enemy_type == EnemyType.NORMAL:
            self.width, self.height = 35, 30
            self.speed = 100 + wave * 30
            self.health = 1
            self.max_health = 1
            self.score_value = 10 + wave * 3
        elif enemy_type == EnemyType.FAST:
            self.width, self.height = 28, 25
            self.speed = 200 + wave * 50
            self.health = 1
            self.max_health = 1
            self.score_value = 15 + wave * 5
        elif enemy_type == EnemyType.TANK:
            self.width, self.height = 55, 45
            self.speed = 50 + wave * 10
            self.health = 3 + wave // 2
            self.max_health = self.health
            self.score_value = 30 + wave * 10
        elif enemy_type == EnemyType.MINI:
            self.width, self.height = 18, 18
            self.speed = 150 + wave * 40
            self.health = 1
            self.max_health = 1
            self.score_value = 5 + wave * 2
        elif enemy_type == EnemyType.BOSS:
            self.x = 260
            self.y = 100
            self.width, self.height = 90, 70
            self.speed = 30
            self.health = 10 + wave * 5
            self.max_health = self.health
            self.score_value = 500 + wave * 100

    def update(self, dt):
        self.y += self.speed * dt
        self.angle = (self.angle + 30 * dt) % 360

    def take_damage(self):
        self.health -= 1
        return self.health <= 0

class Bonus:
    def __init__(self, x, y, bonus_type):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.bonus_type = bonus_type
        self.speed = 150
        self.rotation = 0

    def update(self, dt):
        self.y += self.speed * dt
        self.rotation = (self.rotation + 180 * dt) % 360

class GameWidget(Widget):
    def __init__(self, app_ref=None, **kwargs):
        super().__init__(**kwargs)
        self.app = app_ref  # Ссылка на приложение для навигации
        self.reset_game()
        Clock.schedule_interval(self.update, 1/60.0)
        self.bind(size=self.on_size)

    def reset_game(self):
        """Инициализация/перезагрузка игры"""
        self.player = Player()
        self.enemies = []
        self.bonuses = []
        self.particles = []
        self.stars = [[random.randint(0, 600), random.randint(0, 800)] for _ in range(100)]
        
        self.score = 0
        self.wave = 1
        self.level = 1
        self.enemies_killed = 0
        self.spawn_timer = 0
        self.spawn_delay = 0.8
        
        self.game_over = False
        self.paused = False
        self.touch_x = None
        self.touch_y = None
        
        self.high_score = self.load_high_score()
        self.combo = 0
        self.combo_timer = 0

    def on_size(self, instance, value):
        pass

    def on_touch_down(self, touch):
        self.touch_x = touch.x
        self.touch_y = touch.y
        
        # Если Game Over — проверяем нажатие на кнопки
        if self.game_over:
            # Кнопка "Заново" (левая, снизу)
            if 50 < touch.x < 280 and 150 < touch.y < 220:
                self.reset_game()
                self.app.start_game()
                return True
            
            # Кнопка "Выйти" (правая, снизу)
            if 320 < touch.x < 550 and 150 < touch.y < 220:
                self.app.show_menu()
                return True
        
        # Если пауза — проверяем нажатие на кнопку паузы
        if self.paused and touch.x > 550 - 40 and touch.y > 750:
            self.paused = False
            return True
        
        # Обычная игра
        if not self.game_over and not self.paused:
            self.player.shoot()
        return True

    def on_touch_move(self, touch):
        self.touch_x = touch.x
        self.touch_y = touch.y
        return True

    def on_touch_up(self, touch):
        self.touch_x = None
        self.touch_y = None
        return True

    def update(self, dt):
        if self.game_over or self.paused:
            self.canvas.clear()
            self.draw_game()
            if self.game_over:
                self.draw_game_over()
            if self.paused:
                self.draw_pause_menu()
            return

        # Движение игрока
        self.player.move(self.touch_x, self.touch_y)
        self.player.update(dt)

        # Спавн врагов
        self.spawn_timer += dt
        if self.spawn_timer > self.spawn_delay:
            weights = [50, 20, 15, 12] if self.wave < 5 else [30, 30, 20, 20]
            enemy_type = random.choices(
                [EnemyType.NORMAL, EnemyType.FAST, EnemyType.TANK, EnemyType.MINI],
                weights=weights
            )[0]
            self.enemies.append(Enemy(enemy_type, self.wave))
            self.spawn_timer = 0
            
            if self.wave % 10 == 0:
                boss_count = len([e for e in self.enemies if e.type == EnemyType.BOSS])
                if boss_count == 0:
                    self.enemies.append(Enemy(EnemyType.BOSS, self.wave))

        # Обновление лазеров
        for laser in self.player.lasers[:]:
            laser['y'] += laser.get('vy', -600) * dt
            if laser['y'] < 0:
                self.player.lasers.remove(laser)

        # Обновление врагов
        for enemy in self.enemies[:]:
            enemy.update(dt)
            
            if enemy.y > 800:
                self.enemies.remove(enemy)
                self.score = max(0, self.score - 5)
                self.combo = 0
                continue

            # Столкновение с игроком
            if self.check_collision(
                self.player.x, self.player.y, self.player.width, self.player.height,
                enemy.x, enemy.y, enemy.width, enemy.height
            ):
                self.create_explosion(enemy.x + enemy.width/2, enemy.y + enemy.height/2)
                self.player.take_damage()
                if self.player.health <= 0:
                    self.game_over = True
                    self.save_high_score()
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                continue

            # Проверка попаданий
            for laser in self.player.lasers[:]:
                if self.check_collision(
                    laser['x'], laser['y'], 4, 15,
                    enemy.x, enemy.y, enemy.width, enemy.height
                ):
                    hit_score = enemy.score_value + (self.combo * 2)
                    if enemy.take_damage():
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                        self.score += hit_score
                        self.enemies_killed += 1
                        self.combo += 1
                        self.combo_timer = 2
                        
                        self.create_explosion(enemy.x + enemy.width/2, enemy.y + enemy.height/2)
                        
                        if random.random() < 0.2:
                            bonus_type = random.choice(['health', 'shield', 'fire_mode'])
                            self.bonuses.append(Bonus(enemy.x, enemy.y, bonus_type))
                    
                    if laser in self.player.lasers:
                        self.player.lasers.remove(laser)
                    break

        # Обновление бонусов
        for bonus in self.bonuses[:]:
            bonus.update(dt)
            
            if bonus.y > 800:
                self.bonuses.remove(bonus)
                continue

            if self.check_collision(
                self.player.x, self.player.y, self.player.width, self.player.height,
                bonus.x, bonus.y, bonus.width, bonus.height
            ):
                if bonus.bonus_type == 'health':
                    self.player.health = min(self.player.health + 1, self.player.max_health)
                elif bonus.bonus_type == 'shield':
                    self.player.has_shield = True
                    self.player.shield_time = 5
                elif bonus.bonus_type == 'fire_mode':
                    modes = [FireMode.NORMAL, FireMode.SPREAD, FireMode.LASER, FireMode.DOUBLE]
                    self.player.fire_mode = random.choice(modes)
                
                self.bonuses.remove(bonus)

        # Обновление частиц
        for particle in self.particles[:]:
            if not particle.update(dt):
                self.particles.remove(particle)

        # Обновление комбо
        if self.combo_timer > 0:
            self.combo_timer -= dt
        else:
            self.combo = 0

        # Волны
        if self.enemies_killed >= 5 + self.wave * 2:
            self.wave += 1
            self.enemies_killed = 0
            self.spawn_delay = max(0.2, self.spawn_delay - 0.05)

        if self.wave >= 10:
            self.level = 3
        elif self.wave >= 5:
            self.level = 2

        self.canvas.clear()
        self.draw_game()

    def create_explosion(self, x, y):
        """Создание взрыва (частицы)"""
        colors = [(1, 0.4, 0), (1, 0.6, 0), (1, 0.8, 0), (1, 1, 0)]
        for _ in range(8):
            angle = random.random() * 2 * pi
            speed = random.uniform(200, 400)
            vx = cos(angle) * speed
            vy = sin(angle) * speed
            color = random.choice(colors)
            self.particles.append(Particle(x, y, vx, vy, color))

    def check_collision(self, x1, y1, w1, h1, x2, y2, w2, h2):
        return (x1 < x2 + w2 and x1 + w1 > x2 and
                y1 < y2 + h2 and y1 + h1 > y2)

    def draw_game(self):
        """Отрисовка игрового поля"""
        with self.canvas:
            # Красивый фон (глубокий космос)
            Color(0.02, 0.02, 0.05)
            Rectangle(size=self.size)
            
            # Линия горизонта (полосканов)
            Color(0.1, 0.15, 0.3, 0.3)
            Line(points=[0, 100, 600, 100], width=2)

            # Движущиеся звёзды (параллакс)
            Color(0.8, 0.8, 0.9)
            for star in self.stars:
                star[1] += 0.5
                if star[1] > 800:
                    star[1] = -10
                Ellipse(pos=(star[0], star[1]), size=(1, 1))
            
            # Дальние звёзды
            Color(0.5, 0.5, 0.6, 0.5)
            for i in range(0, 600, 60):
                for j in range(0, 800, 80):
                    Ellipse(pos=(i, j), size=(0.5, 0.5))

            # Лазеры (яркие с подсветкой)
            for laser in self.player.lasers:
                width = laser.get('width', 4)
                Color(0, 1, 1)
                Ellipse(pos=(laser['x'] - width/2, laser['y']), size=(width, 15))
                Color(0.5, 1, 1, 0.5)
                Ellipse(pos=(laser['x'] - width - 2, laser['y']), size=(width + 4, 15))

            # Враги с улучшенной графикой
            for enemy in self.enemies:
                if enemy.type == EnemyType.NORMAL:
                    Color(1, 0.2, 0.2)
                    self.draw_enemy_ship(enemy.x, enemy.y, enemy.width, enemy.height, enemy.angle)
                elif enemy.type == EnemyType.FAST:
                    Color(1, 0.4, 0.4)
                    self.draw_fast_enemy(enemy.x, enemy.y, enemy.width, enemy.height, enemy.angle)
                elif enemy.type == EnemyType.TANK:
                    Color(0.6, 0, 0)
                    self.draw_tank_enemy(enemy.x, enemy.y, enemy.width, enemy.height)
                elif enemy.type == EnemyType.MINI:
                    Color(1, 0.6, 0)
                    self.draw_mini_enemy(enemy.x, enemy.y, enemy.width, enemy.height, enemy.angle)
                elif enemy.type == EnemyType.BOSS:
                    Color(0.9, 0, 0)
                    self.draw_boss_enemy(enemy.x, enemy.y, enemy.width, enemy.height, enemy.angle)

                # Красивая полоса здоровья
                if enemy.health < enemy.max_health:
                    max_bar_w = enemy.width
                    bar_w = max_bar_w * (enemy.health / enemy.max_health)
                    Color(0, 1, 0)
                    Rectangle(pos=(enemy.x + (enemy.width - bar_w) / 2, enemy.y - 8), size=(bar_w, 3))
                    Color(1, 0, 0, 0.3)
                    Rectangle(pos=(enemy.x, enemy.y - 8), size=(enemy.width, 3))

            # Бонусы (вращающиеся звёзды)
            for bonus in self.bonuses:
                if bonus.bonus_type == 'health':
                    Color(1, 0, 0)
                elif bonus.bonus_type == 'shield':
                    Color(0, 1, 1)
                else:
                    Color(1, 1, 0)
                
                self.draw_star(bonus.x + 10, bonus.y + 10, 8, bonus.rotation)

            # Частицы взрыва
            for particle in self.particles:
                alpha = particle.life_time / particle.max_life
                Color(particle.color[0], particle.color[1], particle.color[2], alpha)
                Ellipse(pos=(particle.x - particle.size/2, particle.y - particle.size/2), 
                       size=(particle.size, particle.size))

            # Игрок (реалистичный самолет)
            Color(0, 1, 1)
            self.draw_realistic_airplane(self.player.x, self.player.y)
            
            # Щит (двойное свечение)
            if self.player.has_shield:
                Color(0, 1, 1, 0.2)
                Ellipse(pos=(self.player.x - 25, self.player.y - 25), size=(90, 90))
                Color(0, 1, 1, 0.15)
                Ellipse(pos=(self.player.x - 30, self.player.y - 30), size=(100, 100))

            # Верхняя панель информации
            Color(0, 0, 0, 0.6)
            Rectangle(pos=(0, 750), size=(600, 50))
            
            Color(0.2, 1, 0.8)
            Line(points=[0, 750, 600, 750], width=2)
        
        # Рисование текстовой информации
        self.draw_top_ui()

    def draw_top_ui(self):
        """Отрисовка текстовой информации сверху"""
        from kivy.core.text import Label as CoreLabel
        
        with self.canvas:
            # Здоровье (сердечки)
            Color(1, 0, 0)
            for i in range(self.player.health):
                x_pos = 15 + i * 20
                Ellipse(pos=(x_pos, 762), size=(12, 12))
            
            # Текстовая информация
            ui_info = f"Score: {self.score}  High: {self.high_score}  Wave: {self.wave}  Combo: {self.combo}x"
            try:
                label = CoreLabel(text=ui_info, font_size=11, color=(0.2, 1, 0.8, 1), bold=True)
                label.refresh()
                if label.texture:
                    Rectangle(texture=label.texture, size=label.texture.size, pos=(120, 762))
            except:
                pass

    def draw_pause_menu(self):
        """Отрисовка меню паузы"""
        with self.canvas:
            Color(0, 0, 0, 0.7)
            Rectangle(size=self.size)
            
            Color(0, 1, 1)
            try:
                from kivy.core.text import Label as CoreLabel
                pause_label = CoreLabel(text='⏸ PAUSED', font_size=32, bold=True)
                pause_label.refresh()
                if pause_label.texture:
                    Rectangle(texture=pause_label.texture, size=pause_label.texture.size, 
                             pos=(150, 380))
            except:
                pass

    def draw_game_over(self):
        """Отрисовка экрана Game Over с кнопками"""
        with self.canvas:
            # Тёмный фон (полупрозрачный)
            Color(0, 0, 0, 0.85)
            Rectangle(size=self.size)
            
            # Заголовок "GAME OVER"
            Color(1, 0.1, 0.1)
            try:
                from kivy.core.text import Label as CoreLabel
                gameover_label = CoreLabel(text='GAME OVER', font_size=48, bold=True)
                gameover_label.refresh()
                if gameover_label.texture:
                    Rectangle(texture=gameover_label.texture, size=gameover_label.texture.size, 
                             pos=(100, 550))
            except:
                pass
            
            # Информация: Score
            Color(1, 1, 0)
            try:
                from kivy.core.text import Label as CoreLabel
                score_label = CoreLabel(text=f'📊 Score: {self.score}', font_size=28, bold=True)
                score_label.refresh()
                if score_label.texture:
                    Rectangle(texture=score_label.texture, size=score_label.texture.size, 
                             pos=(120, 480))
            except:
                pass
            
            # Информация: Wave
            Color(0.2, 1, 0.8)
            try:
                from kivy.core.text import Label as CoreLabel
                wave_label = CoreLabel(text=f'🌊 Wave Reached: {self.wave}', font_size=26, bold=True)
                wave_label.refresh()
                if wave_label.texture:
                    Rectangle(texture=wave_label.texture, size=wave_label.texture.size, 
                             pos=(110, 420))
            except:
                pass
            
            # Информация: High Score
            Color(1, 0.6, 0)
            try:
                from kivy.core.text import Label as CoreLabel
                high_label = CoreLabel(text=f'🏆 High Score: {self.high_score}', font_size=22)
                high_label.refresh()
                if high_label.texture:
                    Rectangle(texture=high_label.texture, size=high_label.texture.size, 
                             pos=(130, 360))
            except:
                pass
            
            # КНОПКА "Заново" (левая)
            Color(0, 0.6, 0.6)  # Цвет кнопки
            Rectangle(pos=(50, 150), size=(220, 70))  # Кнопка
            Color(0, 1, 1)  # Контур
            Line(points=[50, 150, 270, 150, 270, 220, 50, 220, 50, 150], width=3)
            
            # Текст на кнопке "Заново" (по центру)
            Color(0, 1, 1)
            try:
                from kivy.core.text import Label as CoreLabel
                btn_restart = CoreLabel(text='▶ Заново', font_size=20, bold=True, color=(0, 1, 1, 1))
                btn_restart.refresh()
                if btn_restart.texture:
                    Rectangle(texture=btn_restart.texture, size=btn_restart.texture.size, 
                             pos=(80, 175))
            except:
                pass
            
            # КНОПКА "Выйти" (правая)
            Color(0.6, 0.2, 0.2)  # Цвет кнопки
            Rectangle(pos=(320, 150), size=(220, 70))  # Кнопка
            Color(1, 0.3, 0.3)  # Контур
            Line(points=[320, 150, 540, 150, 540, 220, 320, 220, 320, 150], width=3)
            
            # Текст на кнопке "Выйти" (по центру)
            Color(1, 0.3, 0.3)
            try:
                from kivy.core.text import Label as CoreLabel
                btn_exit = CoreLabel(text='✕ Меню', font_size=20, bold=True, color=(1, 0.3, 0.3, 1))
                btn_exit.refresh()
                if btn_exit.texture:
                    Rectangle(texture=btn_exit.texture, size=btn_exit.texture.size, 
                             pos=(350, 175))
            except:
                pass

    def draw_realistic_airplane(self, x, y):
        """Отрисовка реалистичного самолета"""
        cx, cy = x + 20, y + 20
        
        # Носовая часть
        points_nose = [(cx, cy - 18), (cx - 5, cy - 15), (cx + 5, cy - 15)]
        Triangle(points=(points_nose[0][0], points_nose[0][1], 
                        points_nose[1][0], points_nose[1][1], 
                        points_nose[2][0], points_nose[2][1]))

        # Основной корпус
        Triangle(points=(cx - 5, cy - 15, cx - 8, cy, cx - 6, cy + 8))
        Triangle(points=(cx + 5, cy - 15, cx + 8, cy, cx + 6, cy + 8))
        Triangle(points=(cx - 6, cy + 8, cx + 6, cy + 8, cx, cy + 12))

        # Контур самолета
        Color(0, 1.5, 1.5)
        Line(points=[cx, cy - 18, cx - 8, cy, cx - 6, cy + 8, cx, cy + 12, cx + 6, cy + 8, cx + 8, cy, cx, cy - 18], width=1.5)

        # Огни кабины
        Color(0, 1, 1, 0.8)
        Ellipse(pos=(cx - 3, cy - 10), size=(6, 6))
        
        # Выхлопы (пламя двигателя)
        Color(1, 0.6, 0, 0.6)
        Triangle(points=(cx - 4, cy + 12, cx - 2, cy + 16, cx - 6, cy + 14))
        Triangle(points=(cx + 4, cy + 12, cx + 2, cy + 16, cx + 6, cy + 14))

    def draw_enemy_ship(self, x, y, w, h, angle):
        """Отрисовка вражеского корабля"""
        cx, cy = x + w/2, y + h/2
        
        # Основной корпус
        points = [
            (cx, cy - h/2 + 2),
            (cx - w/2 + 2, cy + h/3),
            (cx + w/2 - 2, cy + h/3),
            (cx, cy + h/2 - 2),
        ]
        
        Triangle(points=(points[0][0], points[0][1], 
                        points[1][0], points[1][1], 
                        points[2][0], points[2][1]))
        Triangle(points=(points[1][0], points[1][1], 
                        points[2][0], points[2][1], 
                        points[3][0], points[3][1]))
        
        # Контур
        Color(1, 0.4, 0.4)
        Line(points=[p[0] for p in points] + [points[0][0]] + 
                   [p[1] for p in points] + [points[0][1]], width=1)

    def draw_fast_enemy(self, x, y, w, h, angle):
        """Быстрый враг"""
        cx, cy = x + w/2, y + h/2
        Triangle(points=(cx, cy - h/2, cx - w/2, cy + h/2, cx + w/2, cy + h/2))

    def draw_tank_enemy(self, x, y, w, h):
        """Танк"""
        Rectangle(pos=(x, y), size=(w, h))
        cx, cy = x + w/2, y + h/2
        Color(0.8, 0, 0)
        Ellipse(pos=(cx - 8, cy - 8), size=(16, 16))

    def draw_mini_enemy(self, x, y, w, h, angle):
        """Мини враг"""
        Ellipse(pos=(x, y), size=(w, h))

    def draw_boss_enemy(self, x, y, w, h, angle):
        """Босс"""
        cx, cy = x + w/2, y + h/2
        
        # Основная форма
        Triangle(points=(cx, cy - h/2, cx - w/2, cy + h/2, cx + w/2, cy + h/2))
        
        # Контур боса
        Color(0.9, 0, 0)
        Line(points=[cx, cy - h/2, cx - w/2, cy + h/2, cx + w/2, cy + h/2, cx, cy - h/2], width=2)
        
        # Глаз
        Ellipse(pos=(cx - 4, cy - 10), size=(8, 8))

    def draw_star(self, x, y, size, rotation):
        """Рисование вращающейся звезды"""
        points = []
        for i in range(10):
            angle = (rotation + i * 36) * pi / 180
            if i % 2 == 0:
                r = size
            else:
                r = size / 2
            px = x + r * sin(angle)
            py = y + r * cos(angle)
            points.extend([px, py])
        
        points.extend([points[0], points[1]])
        Line(points=points, width=1.5)

    def load_high_score(self):
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r", encoding="utf-8") as f:
                    return json.load(f).get("score", 0)
        except:
            pass
        return 0

    def save_high_score(self):
        try:
            if self.score > self.high_score:
                with open("highscore.json", "w", encoding="utf-8") as f:
                    json.dump({"score": self.score}, f)
        except:
            pass


class MenuWidget(BoxLayout):
    """Главное меню"""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation='vertical', spacing=15, padding=30, **kwargs)
        self.app = app_ref
        
        # Заголовок
        title = Label(
            text='🌟 NEON SPACE\nDEFENDER 🌟',
            font_size=36,
            size_hint=(1, 0.25),
            bold=True,
            color=(0, 1, 1, 1)
        )
        self.add_widget(title)

        # Кнопки
        btn_start = Button(text='▶ START GAME', size_hint=(1, 0.12), background_color=(0, 0.5, 0.5, 1))
        btn_settings = Button(text='⚙ SETTINGS', size_hint=(1, 0.12), background_color=(0.3, 0.3, 0.5, 1))
        btn_help = Button(text='❓ HELP', size_hint=(1, 0.12), background_color=(0.3, 0.3, 0.5, 1))
        btn_exit = Button(text='✕ EXIT', size_hint=(1, 0.12), background_color=(0.5, 0.2, 0.2, 1))

        btn_start.bind(on_release=lambda *a: app_ref.start_game())
        btn_settings.bind(on_release=lambda *a: app_ref.show_settings())
        btn_help.bind(on_release=lambda *a: app_ref.show_help())
        btn_exit.bind(on_release=lambda *a: App.get_running_app().stop())

        self.add_widget(btn_start)
        self.add_widget(btn_settings)
        self.add_widget(btn_help)
        self.add_widget(btn_exit)
        
        # Информация о рекорде
        try:
            with open("highscore.json", "r", encoding="utf-8") as f:
                high_score = json.load(f).get("score", 0)
                info_label = Label(text=f'🏆 High Score: {high_score}', font_size=14, size_hint=(1, 0.1), bold=True)
                self.add_widget(info_label)
        except:
            pass


class SettingsWidget(BoxLayout):
    """Экран настроек"""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=20, **kwargs)
        self.app = app_ref
        
        title = Label(text='⚙ SETTINGS', font_size=28, size_hint=(1, 0.15), bold=True)
        self.add_widget(title)
        
        info = Label(
            text='Game Settings:\n\n'
                 '• Master Volume: ON\n'
                 '• Sound Effects: ON\n'
                 '• Quality: HIGH\n'
                 '• Difficulty: NORMAL\n\n'
                 'More options coming soon!',
            font_size=14,
            size_hint=(1, 0.5)
        )
        self.add_widget(info)
        
        btn_back = Button(text='← BACK', size_hint=(1, 0.1), background_color=(0.3, 0.3, 0.5, 1))
        btn_back.bind(on_release=lambda *a: app_ref.show_menu())
        self.add_widget(btn_back)


class HelpWidget(BoxLayout):
    """Экран справки"""
    def __init__(self, app_ref, **kwargs):
        super().__init__(orientation='vertical', spacing=10, padding=20, **kwargs)
        self.app = app_ref
        
        title = Label(text='❓ HOW TO PLAY', font_size=28, size_hint=(1, 0.15), bold=True)
        self.add_widget(title)
        
        info = Label(
            text='NEON SPACE DEFENDER\n\n'
                 'OBJECTIVE:\n'
                 'Destroy all enemies and survive!\n\n'
                 'CONTROLS:\n'
                 'Tap anywhere to move & shoot\n\n'
                 'ENEMIES:\n'
                 '🔴 Normal - Basic enemies\n'
                 '🔴 Fast - Quick targets\n'
                 '🔴 Tank - Heavy armor\n'
                 '🟠 Mini - Small & quick\n'
                 '🔴 Boss - Mega threat!\n\n'
                 'BONUSES:\n'
                 '❤ Health (+1 life)\n'
                 '💙 Shield (5 sec protection)\n'
                 '⭐ Fire Mode (weapons change)\n\n'
                 'FIRE MODES:\n'
                 '• Normal • Spread • Laser • Double',
            font_size=11,
            size_hint=(1, 0.7)
        )
        self.add_widget(info)
        
        btn_back = Button(text='← BACK', size_hint=(1, 0.1), background_color=(0.3, 0.3, 0.5, 1))
        btn_back.bind(on_release=lambda *a: app_ref.show_menu())
        self.add_widget(btn_back)


class NeonSpaceDefenderApp(App):
    def build(self):
        self.title = "🌟 NEON SPACE DEFENDER 🌟"
        self.root_widget = BoxLayout()
        self.show_menu()
        return self.root_widget

    def show_menu(self):
        self.root_widget.clear_widgets()
        self.menu = MenuWidget(self)
        self.root_widget.add_widget(self.menu)

    def start_game(self):
        self.root_widget.clear_widgets()
        self.game = GameWidget(app_ref=self)  # Передаём ссылку на приложение
        self.root_widget.add_widget(self.game)

    def show_settings(self):
        self.root_widget.clear_widgets()
        settings = SettingsWidget(self)
        self.root_widget.add_widget(settings)

    def show_help(self):
        self.root_widget.clear_widgets()
        help_widget = HelpWidget(self)
        self.root_widget.add_widget(help_widget)


if __name__ == '__main__':
    NeonSpaceDefenderApp().run()
