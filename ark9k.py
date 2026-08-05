import os
import pygame
import sys
import random
import time
import numpy as np
import cv2  # <-- ДОБАВЛЕНО для видео
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

# Инициализация Pygame и OpenGL
pygame.init()

# Константы
WIDTH, HEIGHT = 1260, 800
PADDLE_WIDTH, PADDLE_HEIGHT = 70, 15
BALL_RADIUS = 6.5
BRICK_WIDTH, BRICK_HEIGHT = 57, 20
FPS = 60

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
CYAN = (0, 255, 255)
PINK = (255, 192, 203)
BROWN = (165, 42, 42)
GOLD = (255, 215, 0)
SILVER = (192, 192, 192)
GRAY = (50, 50, 50)
LIGHT_BLUE = (100, 100, 200)
DARK_RED = (139, 0, 0)
COLORS = [RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN, PINK, BROWN]

# Создание окна с OpenGL
pygame.display.gl_set_attribute(GL_ACCELERATED_VISUAL, 1)
pygame.display.set_mode((WIDTH, HEIGHT), HWSURFACE | DOUBLEBUF | OPENGL)
pygame.display.set_caption("Arkanoid - my game")
info = pygame.display.Info()
print(info)
clock = pygame.time.Clock()

# Настройка OpenGL
glViewport(0, 0, WIDTH, HEIGHT)
glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glOrtho(0, WIDTH, HEIGHT, 0, -1, 1)
glMatrixMode(GL_MODELVIEW)
glLoadIdentity()

# Включение смешивания для прозрачности
glEnable(GL_BLEND)
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

# Глобальная переменная для состояния музыки
music_playing = True
current_music = None

# Глобальные переменные для настроек
selected_level = 1
max_level = 20

# Глобальная переменная для игрового фона
game_background_texture = None

# Загрузка звуков
try:
    # Звук отскока от платформы
    paddle_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.1)) for x in range(4410)]))
    paddle_sound.set_volume(0.3)
    # Звук отскока от края экрана (выше по тону, чем от платформы, чтобы отличались на слух)
    wall_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.17)) for x in range(2756)]))
    wall_sound.set_volume(0.25)
    # Звук разрушения кирпича
    brick_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.2)) for x in range(2205)]))
    brick_sound.set_volume(0.4)
    # Звук специального кирпича
    special_brick_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.05)) for x in range(6615)]))
    special_brick_sound.set_volume(0.5)
    # Звук расширения платформы
    expand_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.03)) for x in range(3000)]))
    expand_sound.set_volume(0.6)
    # Звук появления нового мяча
    extra_ball_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.08)) for x in range(3307)]))
    extra_ball_sound.set_volume(0.6)
    # Звук активации пушек
    gun_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.15)) for x in range(2205)]))
    gun_sound.set_volume(0.7)
    # Звук выстрела
    shoot_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.25)) for x in range(1102)]))
    shoot_sound.set_volume(0.4)
    # Звук попадания по боссу
    boss_hit_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.3)) for x in range(4410)]))
    boss_hit_sound.set_volume(0.6)
    # Звук атаки босса
    boss_attack_sound = pygame.mixer.Sound(buffer=bytearray([127 + int(127 * np.sin(x * 0.12)) for x in range(5512)]))
    boss_attack_sound.set_volume(0.5)

    def load_background_music():
        music_files = [
            'music.mp3', 'background.mp3', 'game_music.mp3',
            'soundtrack.mp3', 'arkanoid_music.mp3'
        ]
        for music_file in music_files:
            if os.path.exists(music_file):
                try:
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.set_volume(0.5)
                    print(f"Загружена музыка: {music_file}")
                    return True
                except Exception as e:
                    print(f"Ошибка загрузки {music_file}: {e}")
        print("MP3 файлы не найдены. Музыка недоступна.")
        return False

    music_loaded = load_background_music()

except Exception as e:
    print(f"Ошибка загрузки звуков: {e}")

    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
        def stop(self): pass

    paddle_sound = DummySound()
    wall_sound = DummySound()
    brick_sound = DummySound()
    special_brick_sound = DummySound()
    expand_sound = DummySound()
    extra_ball_sound = DummySound()
    gun_sound = DummySound()
    shoot_sound = DummySound()
    boss_hit_sound = DummySound()
    boss_attack_sound = DummySound()
    music_loaded = False

# Функция для управления музыкой
def toggle_music():
    global music_playing
    music_playing = not music_playing
    if music_playing:
        if music_loaded:
            pygame.mixer.music.play(loops=-1)
    else:
        pygame.mixer.music.stop()

# Функция для загрузки и отрисовки изображения
def load_texture(image_path):
    try:
        surface = pygame.image.load(image_path)
        surface = surface.convert_alpha()
        texture_data = pygame.image.tostring(surface, "RGBA", False)
        width = surface.get_width()
        height = surface.get_height()
        texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)
        return texture_id, width, height
    except Exception as e:
        print(f"Ошибка загрузки изображения {image_path}: {e}")
        return None, 0, 0

def draw_texture(texture_id, x, y, width, height, alpha=1.0):
    if texture_id is None:
        return
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, texture_id)
    glColor4f(1.0, 1.0, 1.0, alpha)
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0); glVertex2f(x, y)
    glTexCoord2f(1.0, 0.0); glVertex2f(x + width, y)
    glTexCoord2f(1.0, 1.0); glVertex2f(x + width, y + height)
    glTexCoord2f(0.0, 1.0); glVertex2f(x, y + height)
    glEnd()
    glDisable(GL_TEXTURE_2D)

# Улучшенные функции для работы с OpenGL
def draw_rect(x, y, width, height, color):
    r, g, b = color[0]/255.0, color[1]/255.0, color[2]/255.0
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_circle(x, y, radius, color, segments=32):
    r, g, b = color[0]/255.0, color[1]/255.0, color[2]/255.0
    glColor3f(r, g, b)
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x, y)
    for i in range(segments + 1):
        angle = 2 * np.pi * i / segments
        glVertex2f(x + radius * np.cos(angle), y + radius * np.sin(angle))
    glEnd()

def draw_gradient_rect(x, y, width, height, color1, color2):
    r1, g1, b1 = color1[0]/255.0, color1[1]/255.0, color1[2]/255.0
    r2, g2, b2 = color2[0]/255.0, color2[1]/255.0, color2[2]/255.0
    glBegin(GL_QUADS)
    glColor3f(r1, g1, b1)
    glVertex2f(x, y)
    glVertex2f(x + width, y)
    glColor3f(r2, g2, b2)
    glVertex2f(x + width, y + height)
    glVertex2f(x, y + height)
    glEnd()

def draw_rounded_rect(x, y, width, height, radius, color):
    r, g, b = color[0]/255.0, color[1]/255.0, color[2]/255.0
    glColor3f(r, g, b)
    glBegin(GL_QUADS)
    glVertex2f(x + radius, y)
    glVertex2f(x + width - radius, y)
    glVertex2f(x + width - radius, y + height)
    glVertex2f(x + radius, y + height)
    glEnd()
    glBegin(GL_QUADS)
    glVertex2f(x, y + radius)
    glVertex2f(x + width, y + radius)
    glVertex2f(x + width, y + height - radius)
    glVertex2f(x, y + height - radius)
    glEnd()
    segments = 12
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + radius, y + radius)
    for i in range(segments + 1):
        angle = np.pi + np.pi/2 * i / segments
        glVertex2f(x + radius + radius * np.cos(angle), y + radius + radius * np.sin(angle))
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + width - radius, y + radius)
    for i in range(segments + 1):
        angle = np.pi/2 * i / segments
        glVertex2f(x + width - radius + radius * np.cos(angle), y + radius + radius * np.sin(angle))
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + width - radius, y + height - radius)
    for i in range(segments + 1):
        angle = -np.pi/2 * i / segments
        glVertex2f(x + width - radius + radius * np.cos(angle), y + height - radius + radius * np.sin(angle))
    glEnd()
    glBegin(GL_TRIANGLE_FAN)
    glVertex2f(x + radius, y + height - radius)
    for i in range(segments + 1):
        angle = np.pi + np.pi/2 * i / segments
        glVertex2f(x + radius + radius * np.cos(angle), y + height - radius + radius * np.sin(angle))
    glEnd()

# === НОВАЯ ФУНКЦИЯ: РИСОВАНИЕ СЕРДЕЧКА ===
def draw_heart_icon(x, y, size=10, filled=True):
    if filled:
        glColor3f(1.0, 0.3, 0.3)  # красный
    else:
        glColor3f(0.3, 0.3, 0.3)  # серый
    if filled:
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(x, y)  # центр для заливки
        for i in range(60):
            t = 2 * np.pi * i / 60
            px = x + size * (16 * np.sin(t)**3) / 16.0
            py = y - size * (13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)) / 16.0
            glVertex2f(px, py)
        glEnd()
    else:
        glBegin(GL_LINE_LOOP)
        for i in range(60):
            t = 2 * np.pi * i / 60
            px = x + size * (16 * np.sin(t)**3) / 16.0
            py = y - size * (13 * np.cos(t) - 5 * np.cos(2*t) - 2 * np.cos(3*t) - np.cos(4*t)) / 16.0
            glVertex2f(px, py)
        glEnd()

_font_cache = {}          # (size) -> pygame.font.Font, so SysFont() is only ever called once per size
_text_texture_cache = {}  # (text, size, color, mirrored) -> (tex_id, width, height), reused while the string doesn't change

def _get_font(size):
    font = _font_cache.get(size)
    if font is None:
        font = pygame.font.SysFont('Arial', size, bold=True)
        _font_cache[size] = font
    return font

def draw_text(text, x, y, color=WHITE, size=24, mirrored=False):
    cache_key = (text, size, color, mirrored)
    cached = _text_texture_cache.get(cache_key)
    if cached is None:
        font = _get_font(size)
        text_surface = font.render(text, True, color)
        if mirrored:
            text_surface = pygame.transform.flip(text_surface, False, False)
        text_data = pygame.image.tostring(text_surface, "RGBA", False)
        tex_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, tex_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, text_surface.get_width(), text_surface.get_height(),
                     0, GL_RGBA, GL_UNSIGNED_BYTE, text_data)
        cached = (tex_id, text_surface.get_width(), text_surface.get_height())
        _text_texture_cache[cache_key] = cached
        # keep the cache from growing forever if score/timers produce endless unique strings
        if len(_text_texture_cache) > 300:
            old_key, (old_tex, _, _) = _text_texture_cache.popitem()
            glDeleteTextures([old_tex])

    tex_id, w, h = cached
    glEnable(GL_TEXTURE_2D)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glColor3f(1.0, 1.0, 1.0)
    glBegin(GL_QUADS)
    glTexCoord2f(0, 0); glVertex2f(x, y)
    glTexCoord2f(1, 0); glVertex2f(x + w, y)
    glTexCoord2f(1, 1); glVertex2f(x + w, y + h)
    glTexCoord2f(0, 1); glVertex2f(x, y + h)
    glEnd()
    glDisable(GL_TEXTURE_2D)

class Particle:
    def __init__(self, x, y, color, velocity=None, size=3, lifetime=60):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.velocity = velocity if velocity else [random.uniform(-2, 2), random.uniform(-2, 2)]

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.lifetime -= 1
        self.size *= 0.95
        return self.lifetime > 0

    def draw(self):
        alpha = self.lifetime / self.max_lifetime
        r, g, b = self.color[0]/255.0, self.color[1]/255.0, self.color[2]/255.0
        glColor4f(r, g, b, alpha)
        glPointSize(self.size)
        glBegin(GL_POINTS)
        glVertex2f(self.x, self.y)
        glEnd()

class BrickShard:
    """Один осколок кирпича — прямоугольный фрагмент, разлетающийся с вращением и затуханием."""
    def __init__(self, x, y, w, h, color):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        # Разлёт в стороны от центра кирпича + лёгкий подброс вверх
        self.vx = random.uniform(-3.5, 3.5)
        self.vy = random.uniform(-4.5, -1.0)
        self.gravity = 0.28
        self.rotation = random.uniform(0, 360)
        self.angular_velocity = random.uniform(-12, 12)
        self.lifetime = random.randint(28, 42)
        self.max_lifetime = self.lifetime

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.rotation += self.angular_velocity
        self.lifetime -= 1
        return self.lifetime > 0

    def draw(self):
        alpha = max(0.0, self.lifetime / self.max_lifetime)
        r, g, b = self.color[0] / 255.0, self.color[1] / 255.0, self.color[2] / 255.0
        glPushMatrix()
        glTranslatef(self.x, self.y, 0)
        glRotatef(self.rotation, 0, 0, 1)
        glColor4f(r, g, b, alpha)
        hw, hh = self.w / 2.0, self.h / 2.0
        glBegin(GL_QUADS)
        glVertex2f(-hw, -hh)
        glVertex2f(hw, -hh)
        glVertex2f(hw, hh)
        glVertex2f(-hw, hh)
        glEnd()
        glPopMatrix()


def shatter_brick(brick, shard_list):
    """Разбивает кирпич на несколько осколков вместо мгновенного исчезновения."""
    special_colors = {
        'life': (255, 235, 80),
        'expand': (210, 210, 235),
        'ball': (80, 255, 220),
        'gun': (255, 130, 130),
    }
    shard_color = special_colors.get(brick.special_type, brick.color)
    cols, rows = 3, 2
    piece_w = brick.width / cols
    piece_h = brick.height / rows
    for row in range(rows):
        for col in range(cols):
            piece_x = brick.x + col * piece_w + piece_w / 2
            piece_y = brick.y + row * piece_h + piece_h / 2
            shard_list.append(BrickShard(piece_x, piece_y, piece_w, piece_h, shard_color))


# Очки за разные типы кирпичей (раньше были магическими числами, продублированными в двух местах)
SCORE_NORMAL_BRICK = 10
SCORE_LIFE_BRICK = 50
SCORE_EXPAND_BRICK = 30
SCORE_BALL_BRICK = 40
SCORE_GUN_BRICK = 60


def resolve_brick_destruction(brick, paddle, balls, score, lives, brick_shards):
    """
    Общая логика уничтожения кирпича: анимация осколков, начисление очков,
    применение эффекта спецкирпича и звук.

    Раньше этот блок был продублирован дословно в двух местах (столкновение с мячом
    и столкновение с пулей) и мог рассинхронизироваться при правках. Теперь он один.

    Возвращает обновлённые (score, lives), т.к. они простые int в вызывающем коде.
    """
    brick.visible = False
    shatter_brick(brick, brick_shards)

    if brick.special_type == 'life':
        lives += 1
        score += SCORE_LIFE_BRICK
        special_brick_sound.play()
    elif brick.special_type == 'expand':
        paddle.expand()
        score += SCORE_EXPAND_BRICK
        special_brick_sound.play()
    elif brick.special_type == 'ball':
        new_ball = Ball(paddle.x + paddle.width // 2, paddle.y - 20)
        balls.append(new_ball)
        score += SCORE_BALL_BRICK
        extra_ball_sound.play()
    elif brick.special_type == 'gun':
        paddle.activate_guns()
        score += SCORE_GUN_BRICK
        gun_sound.play()
    else:
        score += SCORE_NORMAL_BRICK
        brick_sound.play()

    return score, lives


class Bullet:
    def __init__(self, x, y, speed=10):
        self.x = x
        self.y = y
        self.speed = speed
        self.width = 3
        self.height = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.active = True
        self.trail_particles = []

    def update(self):
        self.y -= self.speed
        self.rect.y = self.y
        if random.random() < 0.7:
            self.trail_particles.append(Particle(
                self.x + self.width/2,
                self.y + self.height,
                (255, 255, 100),
                [random.uniform(-0.5, 0.5), random.uniform(0.5, 1.5)],
                1, 15
            ))
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        if self.y < 0:
            self.active = False

    def draw(self):
        for particle in self.trail_particles:
            particle.draw()
        draw_gradient_rect(self.x, self.y, self.width, self.height,
                           (255, 255, 100), (255, 200, 50))
        glow_size = 5
        glColor4f(1.0, 1.0, 0.3, 0.4)
        glBegin(GL_QUADS)
        glVertex2f(self.x - glow_size/2, self.y - glow_size/2)
        glVertex2f(self.x + self.width + glow_size/2, self.y - glow_size/2)
        glVertex2f(self.x + self.width + glow_size/2, self.y + self.height + glow_size/2)
        glVertex2f(self.x - glow_size/2, self.y + self.height + glow_size/2)
        glEnd()

class BossProjectile:
    def __init__(self, x, y, target_x, target_y, speed=5, damage_type='normal'):
        self.x = x
        self.y = y
        self.target_x = target_x
        self.target_y = target_y
        self.speed = speed
        self.damage_type = damage_type  # 'normal', 'slow', 'explosive'
        self.width = 10
        self.height = 10
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2, self.width, self.height)
        self.active = True
        
        # Вычисление направления
        dx = target_x - x
        dy = target_y - y
        dist = np.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.vx = dx / dist * speed
            self.vy = dy / dist * speed
        else:
            self.vx = 0
            self.vy = speed
        
        self.trail_particles = []
        self.explosion_particles = []
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.x = self.x - self.width//2
        self.rect.y = self.y - self.height//2
        
        # Создание следа
        if random.random() < 0.5:
            color = (255, 100, 100) if self.damage_type == 'explosive' else (200, 100, 255)
            self.trail_particles.append(Particle(
                self.x, self.y, color,
                [random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)],
                2, 20
            ))
        
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        
        # Проверка выхода за границы
        if self.y > HEIGHT + 50 or self.y < -50 or self.x < -50 or self.x > WIDTH + 50:
            self.active = False
            
    def draw(self):
        for particle in self.trail_particles:
            particle.draw()
            
        # Рисование снаряда
        if self.damage_type == 'explosive':
            color1 = (255, 80, 80)
            color2 = (200, 0, 0)
            radius = 8
        elif self.damage_type == 'slow':
            color1 = (100, 100, 255)
            color2 = (0, 0, 200)
            radius = 6
        else:
            color1 = (255, 100, 255)
            color2 = (150, 0, 150)
            radius = 5
            
        # Ядро снаряда
        draw_circle(self.x, self.y, radius, color1)
        draw_circle(self.x-1, self.y-1, radius-2, color2)
        
        # Свечение
        glow_alpha = 0.3 + 0.2 * np.sin(pygame.time.get_ticks() * 0.02)
        glColor4f(1.0, 0.2, 0.2, glow_alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.x, self.y)
        for i in range(16 + 1):
            angle = 2 * np.pi * i / 16
            glVertex2f(self.x + (radius+3) * np.cos(angle), self.y + (radius+3) * np.sin(angle))
        glEnd()
        
class Boss:
    def __init__(self, level):
        self.level = level
        self.boss_type = level // 5  # 1, 2, 3, 4 для уровней 5, 10, 15, 20
        
        # Характеристики босса в зависимости от типа
        boss_stats = {
            1: {'name': 'Sentinel', 'health': 30, 'color': DARK_RED, 'attack_speed': 60, 'projectile_speed': 4},
            2: {'name': 'Guardian', 'health': 50, 'color': PURPLE, 'attack_speed': 45, 'projectile_speed': 5},
            3: {'name': 'Titan', 'health': 80, 'color': GOLD, 'attack_speed': 30, 'projectile_speed': 6},
            4: {'name': 'Overlord', 'health': 120, 'color': (255, 0, 255), 'attack_speed': 20, 'projectile_speed': 7}
        }
        
        stats = boss_stats[self.boss_type]
        self.name = stats['name']
        self.max_health = stats['health']
        self.health = self.max_health
        self.color = stats['color']
        self.attack_speed = stats['attack_speed']
        self.projectile_speed = stats['projectile_speed']
        
        # Позиция и размер
        self.width = 200
        self.height = 150
        self.x = WIDTH // 2 - self.width // 2
        self.y = 80
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Движение
        self.direction = 1
        self.move_speed = 2
        self.move_range = 150
        
        # Атака
        self.attack_timer = 0
        self.projectiles = []
        self.attack_pattern = 0  # 0, 1, 2 для разных паттернов атаки
        self.pattern_timer = 0
        
        # Визуальные эффекты
        self.pulse_offset = random.uniform(0, 2 * np.pi)
        self.glow_intensity = 0
        self.hit_flash = 0
        self.particles = []
        
        # Уязвимые места - тепер вони впливають на загальне здоров'я боса
        self.weak_points = []
        self.create_weak_points()
        
        # Фазы босса
        self.phase = 1
        self.max_phases = 3
        self.phase_thresholds = [0.66, 0.33, 0]  # Процент здоровья для смены фазы
        
    def create_weak_points(self):
        """Создание уязвимых точек босса"""
        if self.boss_type == 1:
            # Простой босс - одна уязвимая точка
            self.weak_points.append({'x': self.x + self.width//2, 'y': self.y + self.height//2, 
                                     'radius': 30, 'active': True, 'health': 5, 'max_health': 8})
        elif self.boss_type == 2:
            # Средний босс - две точки
            self.weak_points.append({'x': self.x + self.width//3, 'y': self.y + self.height//2, 
                                     'radius': 25, 'active': True, 'health': 15, 'max_health': 15})
            self.weak_points.append({'x': self.x + 2*self.width//3, 'y': self.y + self.height//2, 
                                     'radius': 25, 'active': True, 'health': 15, 'max_health': 15})
        elif self.boss_type == 3:
            # Сложный босс - три точки
            for i in range(3):
                self.weak_points.append({'x': self.x + (i+1)*self.width//4, 'y': self.y + self.height//2, 
                                         'radius': 20, 'active': True, 'health': 20, 'max_health': 20})
        else:
            # Финальный босс - четыре точки
            for i in range(2):
                for j in range(2):
                    self.weak_points.append({'x': self.x + (i+1)*self.width//3, 
                                             'y': self.y + (j+1)*self.height//3,
                                             'radius': 18, 'active': True, 'health': 25, 'max_health': 25})
    
    def update(self, paddle_x, paddle_y):
        # Движение босса
        self.x += self.direction * self.move_speed
        if self.x < self.move_range or self.x > WIDTH - self.width - self.move_range:
            self.direction *= -1
        self.rect.x = self.x
        
        # Оновлення позицій уразливих точок (вони рухаються разом з босом)
        self.update_weak_points_position()
        
        # Обновление таймеров
        self.attack_timer += 1
        self.pattern_timer += 1
        if self.hit_flash > 0:
            self.hit_flash -= 1
            
        # Смена фазы
        health_percent = self.health / self.max_health
        new_phase = 1
        if health_percent <= 0.66:
            new_phase = 2
        if health_percent <= 0.33:
            new_phase = 3
            
        if new_phase != self.phase:
            self.phase = new_phase
            self.create_phase_effect()
        
        # Атака
        if self.attack_timer >= self.attack_speed:
            self.attack(paddle_x, paddle_y)
            self.attack_timer = 0
            self.attack_pattern = (self.attack_pattern + 1) % 3
            
        # Обновление снарядов
        for projectile in self.projectiles[:]:
            projectile.update()
            if not projectile.active:
                self.projectiles.remove(projectile)
                
        # Обновление частиц
        self.particles = [p for p in self.particles if p.update()]
        
        # Создание эффектов свечения
        self.glow_intensity = max(0, self.glow_intensity - 0.1)
    
    def update_weak_points_position(self):
        """Оновлює позиції уразливих точок відповідно до позиції боса"""
        if self.boss_type == 1:
            if len(self.weak_points) > 0:
                self.weak_points[0]['x'] = self.x + self.width//2
                self.weak_points[0]['y'] = self.y + self.height//2
        elif self.boss_type == 2:
            if len(self.weak_points) >= 2:
                self.weak_points[0]['x'] = self.x + self.width//3
                self.weak_points[0]['y'] = self.y + self.height//2
                self.weak_points[1]['x'] = self.x + 2*self.width//3
                self.weak_points[1]['y'] = self.y + self.height//2
        elif self.boss_type == 3:
            for i in range(min(3, len(self.weak_points))):
                self.weak_points[i]['x'] = self.x + (i+1)*self.width//4
                self.weak_points[i]['y'] = self.y + self.height//2
        else:
            positions = [(self.x + self.width//3, self.y + self.height//3),
                        (self.x + 2*self.width//3, self.y + self.height//3),
                        (self.x + self.width//3, self.y + 2*self.height//3),
                        (self.x + 2*self.width//3, self.y + 2*self.height//3)]
            for i in range(min(4, len(self.weak_points), len(positions))):
                self.weak_points[i]['x'] = positions[i][0]
                self.weak_points[i]['y'] = positions[i][1]
    
    def attack(self, target_x, target_y):
        """Различные паттерны атаки"""
        boss_attack_sound.play()
        
        if self.attack_pattern == 0:
            # Одиночный выстрел по игроку
            self.projectiles.append(BossProjectile(
                self.x + self.width//2, self.y + self.height,
                target_x, target_y,
                self.projectile_speed, 'normal'
            ))
            
        elif self.attack_pattern == 1:
            # Тройной выстрел веером
            for offset in [-30, 0, 30]:
                self.projectiles.append(BossProjectile(
                    self.x + self.width//2, self.y + self.height,
                    target_x + offset, target_y,
                    self.projectile_speed, 'slow' if self.phase > 1 else 'normal'
                ))
                
        elif self.attack_pattern == 2 and self.phase >= 2:
            # Взрывная атака (только на высоких фазах)
            for i in range(5):
                angle = random.uniform(-30, 30)
                dx = np.sin(np.radians(angle)) * 100
                self.projectiles.append(BossProjectile(
                    self.x + self.width//2, self.y + self.height,
                    target_x + dx, target_y,
                    self.projectile_speed * 1.5, 'explosive'
                ))
    
    def check_hit(self, ball_x, ball_y, ball_radius):
        """Проверка попадания по уязвимым точкам"""
        hit = False
        for weak_point in self.weak_points:
            if weak_point['active']:
                dist = np.sqrt((ball_x - weak_point['x'])**2 + (ball_y - weak_point['y'])**2)
                if dist < ball_radius + weak_point['radius']:
                    weak_point['health'] -= 1
                    hit = True
                    
                    # Створюємо ефект попадання
                    for _ in range(5):
                        self.particles.append(Particle(
                            weak_point['x'], weak_point['y'],
                            YELLOW, [random.uniform(-2, 2), random.uniform(-2, 2)], 3, 20
                        ))
                    
                    # Якщо точка знищена
                    if weak_point['health'] <= 0:
                        weak_point['active'] = False
                        # Зменшуємо здоров'я боса на значення здоров'я точки
                        health_loss = weak_point['max_health'] * 3  # Збільшуємо втрату здоров'я
                        self.health -= health_loss
                        self.glow_intensity = 20
                        boss_hit_sound.play()
                        
                        # Створюємо ефект вибуху точки
                        for _ in range(15):
                            self.particles.append(Particle(
                                weak_point['x'], weak_point['y'],
                                GOLD, [random.uniform(-4, 4), random.uniform(-4, 4)], 5, 40
                            ))
                        
                        print(f"Точку знищено! Здоров'я боса: {self.health}/{self.max_health}")  # Для відладки
                    else:
                        # Невелике зменшення здоров'я за кожне попадання
                        self.health -= 2
                        boss_hit_sound.play()
                        print(f"Попадання! Здоров'я боса: {self.health}/{self.max_health}")  # Для відладки
                    
        return hit
    
    def check_bullet_hit(self, bullet):
        """Проверка попадания пули платформы по боссу"""
        for weak_point in self.weak_points:
            if weak_point['active']:
                bullet_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                point_rect = pygame.Rect(weak_point['x'] - weak_point['radius'],
                                        weak_point['y'] - weak_point['radius'],
                                        weak_point['radius']*2, weak_point['radius']*2)
                if bullet_rect.colliderect(point_rect):
                    weak_point['health'] -= 2  # Пулі завдають більше шкоди
                    
                    # Створюємо ефект попадання
                    for _ in range(3):
                        self.particles.append(Particle(
                            weak_point['x'], weak_point['y'],
                            (255, 255, 0), [random.uniform(-1, 1), random.uniform(-1, 1)], 2, 15
                        ))
                    
                    # Якщо точка знищена
                    if weak_point['health'] <= 0:
                        weak_point['active'] = False
                        health_loss = weak_point['max_health'] * 2
                        self.health -= health_loss
                        self.glow_intensity = 20
                        boss_hit_sound.play()
                        
                        # Ефект вибуху точки
                        for _ in range(15):
                            self.particles.append(Particle(
                                weak_point['x'], weak_point['y'],
                                GOLD, [random.uniform(-4, 4), random.uniform(-4, 4)], 5, 40
                            ))
                        print(f"Точку знищено кулею! Здоров'я боса: {self.health}/{self.max_health}")
                    else:
                        self.health -= 2  # Пуля завдає 2 шкоди
                        print(f"Попадання кулею! Здоров'я боса: {self.health}/{self.max_health}")
                    return True
        return False
    
    def create_phase_effect(self):
        """Эффект при смене фазы"""
        for _ in range(30):
            self.particles.append(Particle(
                self.x + random.uniform(0, self.width),
                self.y + random.uniform(0, self.height),
                (255, 255, 0),
                [random.uniform(-4, 4), random.uniform(-4, 4)],
                5, 60
            ))
    
    def draw(self):
        # Рисование частиц
        for particle in self.particles:
            particle.draw()
        
        # Основной корпус босса с эффектом свечения
        pulse = np.sin(pygame.time.get_ticks() * 0.003 + self.pulse_offset) * 0.1 + 0.9
        
        # Тень
        shadow_alpha = 0.3
        glColor4f(0, 0, 0, shadow_alpha)
        glBegin(GL_QUADS)
        glVertex2f(self.x + 10, self.y + 10)
        glVertex2f(self.x + self.width + 10, self.y + 10)
        glVertex2f(self.x + self.width + 10, self.y + self.height + 10)
        glVertex2f(self.x + 10, self.y + self.height + 10)
        glEnd()
        
        # Корпус с градиентом
        color1 = tuple(int(c * pulse) for c in self.color)
        color2 = tuple(int(c * 0.7) for c in self.color)
        
        if self.hit_flash > 0:
            color1 = (255, 255, 255)
            color2 = (200, 200, 200)
            
        # Основной прямоугольник с закругленными углами
        draw_rounded_rect(self.x, self.y, self.width, self.height, 20, color1)
        
        # Детали корпуса
        draw_rounded_rect(self.x + 10, self.y + 10, self.width - 20, self.height - 20, 15, color2)
        
        # Глаза босса
        eye_color = (255, 0, 0) if self.phase > 1 else (255, 255, 0)
        draw_circle(self.x + self.width//3, self.y + self.height//3, 15, eye_color)
        draw_circle(self.x + 2*self.width//3, self.y + self.height//3, 15, eye_color)
        draw_circle(self.x + self.width//3, self.y + self.height//3, 7, (0, 0, 0))
        draw_circle(self.x + 2*self.width//3, self.y + self.height//3, 7, (0, 0, 0))
        
        # Рисование уязвимых точек
        active_points = 0
        for weak_point in self.weak_points:
            if weak_point['active']:
                active_points += 1
                # Пульсирующий эффект
                pulse_size = weak_point['radius'] + np.sin(pygame.time.get_ticks() * 0.01) * 3
                
                # Свечение
                glColor4f(1.0, 0.0, 0.0, 0.3)
                glBegin(GL_TRIANGLE_FAN)
                glVertex2f(weak_point['x'], weak_point['y'])
                for i in range(20 + 1):
                    angle = 2 * np.pi * i / 20
                    glVertex2f(weak_point['x'] + (pulse_size+5) * np.cos(angle),
                              weak_point['y'] + (pulse_size+5) * np.sin(angle))
                glEnd()
                
                # Сама точка
                draw_circle(weak_point['x'], weak_point['y'], weak_point['radius'], (255, 50, 50))
                draw_circle(weak_point['x'], weak_point['y'], weak_point['radius']-3, (255, 200, 200))
                
                # Индикатор здоровья точки
                health_percent = weak_point['health'] / weak_point['max_health']
                bar_width = weak_point['radius'] * 2
                bar_height = 4
                bar_x = weak_point['x'] - weak_point['radius']
                bar_y = weak_point['y'] + weak_point['radius'] + 5
                draw_rect(bar_x, bar_y, bar_width, bar_height, (50, 50, 50))
                draw_rect(bar_x, bar_y, bar_width * health_percent, bar_height, (0, 255, 0))
        
        # Индикатор здоровья босса
        health_percent = max(0, self.health) / self.max_health
        bar_width = 300
        bar_height = 20
        bar_x = WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        # Фон полоски здоровья
        draw_rounded_rect(bar_x, bar_y, bar_width, bar_height, 5, (50, 50, 50))
        
        # Заполнение
        health_color = (0, 255, 0) if health_percent > 0.66 else (255, 255, 0) if health_percent > 0.33 else (255, 0, 0)
        draw_rounded_rect(bar_x, bar_y, bar_width * health_percent, bar_height, 5, health_color)
        
        # Текст здоровья
        health_text = f"{self.name} [{self.phase}/{self.max_phases}] {max(0, self.health)}/{self.max_health}"
        draw_text(health_text, bar_x + bar_width//2 - 80, bar_y + 2, WHITE, 16)
        
        # Підказка про активні точки
        if active_points > 0:
            hint_text = f"Points remaining: {active_points}"
            draw_text(hint_text, bar_x + bar_width//2 - 50, bar_y - 20, RED, 14)
        
        # Рисование снарядов
        for projectile in self.projectiles:
            projectile.draw()
            
        # Эффект свечения при получении урона
        if self.glow_intensity > 0:
            glow_alpha = min(0.8, self.glow_intensity / 25.0)
            glColor4f(1.0, 1.0, 0.0, glow_alpha)
            glBegin(GL_TRIANGLE_FAN)
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            glVertex2f(center_x, center_y)
            for i in range(32 + 1):
                angle = 2 * np.pi * i / 32
                glVertex2f(center_x + (self.width//2 + self.glow_intensity) * np.cos(angle),
                          center_y + (self.height//2 + self.glow_intensity) * np.sin(angle))
            glEnd()


class Paddle:
    def __init__(self):
        self.original_width = PADDLE_WIDTH
        self.width = self.original_width
        self.height = PADDLE_HEIGHT
        self.x = WIDTH // 2 - self.width // 2
        self.y = HEIGHT - 50
        self.speed = 8
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.expand_timer = 0
        self.expanded = False
        self.bevel_size = 5
        self.glow_intensity = 0
        self.guns_active = False
        self.guns_timer = 0
        self.bullets = []
        self.shoot_cooldown = 0
        self.movement_particles = []

    def expand(self):
        if not self.expanded:
            self.width = self.original_width * 1.5
            self.expanded = True
            self.expand_timer = 700
            self.glow_intensity = 15
            self.rect.width = self.width
            expand_sound.play()

    def activate_guns(self):
        if not self.guns_active:
            self.guns_active = True
            self.guns_timer = 1000
            self.glow_intensity = 15
            gun_sound.play()

    def shoot(self):
        if self.guns_active and self.shoot_cooldown <= 0:
            self.bullets.append(Bullet(self.x + 8, self.y))
            self.bullets.append(Bullet(self.x + self.width - 11, self.y))
            self.shoot_cooldown = 20
            shoot_sound.play()

    def update(self):
        if self.expand_timer > 0:
            self.expand_timer -= 1
            if self.expand_timer == 0:
                self.width = self.original_width
                self.expanded = False
        # Keep the collision rect in sync with the current position/size,
        # otherwise the ball can pass through the paddle when it expands
        # (the rect's width was never updated to match self.width).
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        if self.guns_active:
            self.guns_timer -= 1
            if self.guns_timer <= 0:
                self.guns_active = False
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.guns_active and self.shoot_cooldown <= 0:
            self.shoot()
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
        if self.glow_intensity > 0:
            self.glow_intensity -= 0.3

    def move(self, direction):
        old_x = self.x
        if direction == "left" and self.x > 0:
            self.x -= self.speed
            if random.random() < 0.3:
                self.movement_particles.append(Particle(
                    self.x + self.width, self.y + self.height,
                    (100, 200, 255),
                    [random.uniform(0.5, 2.0), random.uniform(-0.5, 0.5)],
                    2, 30
                ))
        if direction == "right" and self.x < WIDTH - self.width:
            self.x += self.speed
            if random.random() < 0.3:
                self.movement_particles.append(Particle(
                    self.x, self.y + self.height,
                    (100, 200, 255),
                    [random.uniform(-2.0, -0.5), random.uniform(-0.5, 0.5)],
                    2, 30
                ))
        self.rect.x = self.x
        self.movement_particles = [p for p in self.movement_particles if p.update()]

    def draw(self):
        for particle in self.movement_particles:
            particle.draw()
        base_color1 = (0, 220, 255) if self.expanded else (80, 160, 255)
        base_color2 = (0, 120, 220) if self.expanded else (20, 100, 200)
        shadow_color = (0, 80, 160) if self.expanded else (0, 60, 140)
        highlight_color = (150, 250, 255) if self.expanded else (150, 200, 255)
        if self.guns_active:
            base_color1 = (255, 120, 120)
            base_color2 = (200, 60, 60)
            shadow_color = (160, 40, 40)
            highlight_color = (255, 180, 180)
        draw_rounded_rect(self.x, self.y + self.height - self.bevel_size,
                          self.width, self.bevel_size, 2, shadow_color)
        draw_rounded_rect(self.x + self.width - self.bevel_size, self.y,
                          self.bevel_size, self.height, 2, shadow_color)
        draw_gradient_rect(self.x, self.y, self.width, self.height, base_color1, base_color2)
        draw_rounded_rect(self.x, self.y, self.width, self.bevel_size, 2, highlight_color)
        draw_rounded_rect(self.x, self.y, self.bevel_size, self.height, 2, highlight_color)
        strip_color = (0, 255, 255) if self.expanded else (100, 200, 255)
        if self.guns_active:
            strip_color = (255, 100, 100)
        strip_width = self.width * 0.6
        strip_height = self.height * 0.4
        strip_x = self.x + (self.width - strip_width) / 2
        strip_y = self.y + (self.height - strip_height) / 2
        glColor4f(strip_color[0]/255.0, strip_color[1]/255.0, strip_color[2]/255.0, 0.3)
        glBegin(GL_QUADS)
        glVertex2f(strip_x - 3, strip_y - 3)
        glVertex2f(strip_x + strip_width + 3, strip_y - 3)
        glVertex2f(strip_x + strip_width + 3, strip_y + strip_height + 3)
        glVertex2f(strip_x - 3, strip_y + strip_height + 3)
        glEnd()
        draw_rounded_rect(strip_x, strip_y, strip_width, strip_height, 3, strip_color)
        pulse = np.sin(pygame.time.get_ticks() * 0.01) * 0.5 + 0.5
        glColor4f(1.0, 1.0, 1.0, pulse * 0.8)
        glLineWidth(2.0)
        glBegin(GL_LINES)
        glVertex2f(strip_x + 5, strip_y + strip_height/2)
        glVertex2f(strip_x + strip_width - 5, strip_y + strip_height/2)
        glEnd()
        if self.guns_active:
            gun_color = (255, 60, 60)
            gun_highlight = (255, 150, 150)
            draw_rounded_rect(self.x + 6, self.y - 8, 8, 6, 2, gun_color)
            draw_rounded_rect(self.x + 7, self.y - 7, 6, 2, 1, gun_highlight)
            draw_rounded_rect(self.x + self.width - 14, self.y - 8, 8, 6, 2, gun_color)
            draw_rounded_rect(self.x + self.width - 13, self.y - 7, 6, 2, 1, gun_highlight)
            glow_alpha = 0.4 + 0.3 * np.sin(pygame.time.get_ticks() * 0.02)
            glColor4f(1.0, 0.2, 0.2, glow_alpha)
            glBegin(GL_TRIANGLE_FAN)
            center_x = self.x + 10
            center_y = self.y - 5
            glVertex2f(center_x, center_y)
            for i in range(16 + 1):
                angle = 2 * np.pi * i / 16
                glVertex2f(center_x + 8 * np.cos(angle), center_y + 8 * np.sin(angle))
            center_x = self.x + self.width - 10
            center_y = self.y - 5
            glVertex2f(center_x, center_y)
            for i in range(16 + 1):
                angle = 2 * np.pi * i / 16
                glVertex2f(center_x + 8 * np.cos(angle), center_y + 8 * np.sin(angle))
            glEnd()
        if self.glow_intensity > 0:
            glow_alpha = min(0.6, self.glow_intensity / 25.0)
            glow_color = (1.0, 0.0, 0.0) if self.guns_active else (0.0, 1.0, 1.0)
            glColor4f(glow_color[0], glow_color[1], glow_color[2], glow_alpha)
            glBegin(GL_TRIANGLE_FAN)
            center_x = self.x + self.width // 2
            center_y = self.y + self.height // 2
            glVertex2f(center_x, center_y)
            for i in range(32 + 1):
                angle = 2 * np.pi * i / 32
                glVertex2f(center_x + (self.width//2 + self.glow_intensity) * np.cos(angle),
                           center_y + (self.height//2 + self.glow_intensity) * np.sin(angle))
            glEnd()
        if self.expanded:
            bar_width = (self.expand_timer / 700.0) * (self.width - 10)
            draw_rounded_rect(self.x + 5, self.y - 12, bar_width, 4, 2, (0, 255, 255))
        if self.guns_active:
            bar_width = (self.guns_timer / 1000.0) * (self.width - 10)
            draw_rounded_rect(self.x + 5, self.y - 18, bar_width, 4, 2, (255, 50, 50))
        for bullet in self.bullets:
            bullet.draw()

class Ball:
    def __init__(self, x=None, y=None):
        self.radius = BALL_RADIUS
        self.x = x if x is not None else WIDTH // 2
        self.y = y if y is not None else HEIGHT // 2
        self.dx = random.choice([-4, -3, 3, 4])
        self.dy = -4
        self.rect = pygame.Rect(self.x - self.radius, self.y - self.radius,
                                self.radius * 2, self.radius * 2)
        self.glow_timer = 0
        self.rotation = 0
        self.light_angle = 0
        self.trail_particles = []

    def move(self):
        old_x, old_y = self.x, self.y
        self.x += self.dx
        self.y += self.dy
        self.rotation += np.sqrt(self.dx**2 + self.dy**2) * 0.1
        self.light_angle += 0.05
        if self.x <= self.radius or self.x >= WIDTH - self.radius:
            self.dx *= -1
            self.glow_timer = 10
            self.create_impact_particles()
            wall_sound.play()
        if self.y <= self.radius:
            self.dy *= -1
            self.glow_timer = 10
            self.create_impact_particles()
            wall_sound.play()
        self.rect.x = self.x - self.radius
        self.rect.y = self.y - self.radius
        if random.random() < 0.6:
            self.trail_particles.append(Particle(
                self.x, self.y,
                (255, 255, 255),
                [random.uniform(-0.3, 0.3), random.uniform(-0.3, 0.3)],
                2, 15
            ))
        self.trail_particles = [p for p in self.trail_particles if p.update()]
        if self.glow_timer > 0:
            self.glow_timer -= 1

    def create_impact_particles(self):
        for _ in range(8):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(1, 3)
            self.trail_particles.append(Particle(
                self.x, self.y,
                (255, 255, 200),
                [speed * np.cos(angle), speed * np.sin(angle)],
                3, 30
            ))

    def draw(self):
        for particle in self.trail_particles:
            particle.draw()
        if self.glow_timer > 0:
            glow_alpha = min(0.8, self.glow_timer / 25.0)
            glow_size = self.radius + self.glow_timer
            glColor4f(1.0, 1.0, 1.0, glow_alpha)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(self.x, self.y)
            for i in range(32 + 1):
                angle = 2 * np.pi * i / 32
                glVertex2f(self.x + glow_size * np.cos(angle),
                           self.y + glow_size * np.sin(angle))
            glEnd()
        segments = 36
        light_x = self.x + np.cos(self.light_angle) * self.radius * 0.7
        light_y = self.y + np.sin(self.light_angle) * self.radius * 0.7
        glBegin(GL_TRIANGLE_FAN)
        glColor3f(1.0, 1.0, 1.0)
        glVertex2f(self.x, self.y)
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            px = self.x + self.radius * np.cos(angle)
            py = self.y + self.radius * np.sin(angle)
            to_light = np.sqrt((px - light_x)**2 + (py - light_y)**2)
            light_factor = 1.0 - min(1.0, to_light / (self.radius * 2))
            base_color = 0.3 + 0.7 * light_factor
            glColor3f(base_color, base_color, base_color)
            glVertex2f(px, py)
        glEnd()
        glColor4f(0.8, 0.8, 1.0, 0.3)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(self.x, self.y)
        for i in range(segments + 1):
            angle = 2 * np.pi * i / segments
            glVertex2f(self.x + self.radius * 0.8 * np.cos(angle),
                       self.y + self.radius * 0.8 * np.sin(angle))
        glEnd()
        highlight_size = self.radius * 0.3
        highlight_x = light_x - highlight_size * 0.5
        highlight_y = light_y - highlight_size * 0.5
        glColor4f(1.0, 1.0, 1.0, 0.9)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(highlight_x, highlight_y)
        for i in range(16 + 1):
            angle = 2 * np.pi * i / 16
            glVertex2f(highlight_x + highlight_size * np.cos(angle),
                       highlight_y + highlight_size * np.sin(angle))
        glEnd()
        glColor3f(0.9, 0.9, 1.0)
        glLineWidth(2.0)
        glBegin(GL_LINE_LOOP)
        for i in range(segments):
            angle = 2 * np.pi * i / segments
            glVertex2f(self.x + self.radius * np.cos(angle),
                       self.y + self.radius * np.sin(angle))
        glEnd()
        if self.y > self.radius + 20:
            shadow_alpha = 0.2 * (1.0 - np.minimum(1.0, (self.y - HEIGHT/2) / (HEIGHT/2)))
            shadow_y = self.y + self.radius * 0.8
            shadow_size = self.radius * 0.9
            glColor4f(0.0, 0.0, 0.0, shadow_alpha)
            glBegin(GL_TRIANGLE_FAN)
            glVertex2f(self.x, shadow_y)
            for i in range(16 + 1):
                angle = 2 * np.pi * i / 16
                glVertex2f(self.x + shadow_size * np.cos(angle),
                           shadow_y + shadow_size * np.sin(angle) * 0.4)
            glEnd()

class Brick:
    def __init__(self, x, y, color, special_type=None):
        self.width = BRICK_WIDTH
        self.height = BRICK_HEIGHT
        self.x = x
        self.y = y
        self.color = color
        self.special_type = special_type
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.visible = True
        self.bevel_size = 4
        self.pulse_offset = random.uniform(0, 2 * np.pi)

    def draw(self):
        if not self.visible:
            return
        pulse = np.sin(pygame.time.get_ticks() * 0.005 + self.pulse_offset) * 0.1 + 0.9
        if self.special_type == 'life':
            flash = (pygame.time.get_ticks() // 150) % 2
            main_color1 = (255, 220, 50) if flash else (255, 255, 100)
            main_color2 = (220, 180, 0) if flash else (230, 200, 0)
            self.draw_enhanced_brick(main_color1, main_color2, pulse)
            self.draw_heart_symbol()
        elif self.special_type == 'expand':
            main_color1 = (220, 220, 240)
            main_color2 = (180, 180, 220)
            self.draw_enhanced_brick(main_color1, main_color2, pulse)
            self.draw_arrows_symbol()
        elif self.special_type == 'ball':
            main_color1 = (80, 255, 220)
            main_color2 = (0, 200, 180)
            self.draw_enhanced_brick(main_color1, main_color2, pulse)
            self.draw_ball_symbol()
        elif self.special_type == 'gun':
            flash = (pygame.time.get_ticks() // 100) % 2
            main_color1 = (255, 100, 100) if flash else (255, 150, 150)
            main_color2 = (220, 60, 60) if flash else (230, 100, 100)
            self.draw_enhanced_brick(main_color1, main_color2, pulse)
            self.draw_gun_symbol()
        else:
            darker_color = tuple(max(0, c - 40) for c in self.color)
            self.draw_enhanced_brick(self.color, darker_color, pulse)

    def draw_enhanced_brick(self, color1, color2, pulse=1.0):
        enhanced_color1 = tuple(min(255, int(c * pulse)) for c in color1)
        enhanced_color2 = tuple(min(255, int(c * pulse)) for c in color2)
        glDisable(GL_BLEND)
        draw_gradient_rect(self.x, self.y, self.width, self.height,
                           enhanced_color1, enhanced_color2)
        glEnable(GL_BLEND)
        shadow_color = tuple(max(0, c - 60) for c in color2)
        highlight_color = tuple(min(255, c + 40) for c in color1)
        glColor3f(highlight_color[0]/255.0, highlight_color[1]/255.0, highlight_color[2]/255.0)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width - self.bevel_size, self.y + self.bevel_size)
        glVertex2f(self.x + self.bevel_size, self.y + self.bevel_size)
        glVertex2f(self.x, self.y)
        glVertex2f(self.x + self.bevel_size, self.y + self.bevel_size)
        glVertex2f(self.x + self.bevel_size, self.y + self.height - self.bevel_size)
        glVertex2f(self.x, self.y + self.height)
        glEnd()
        glColor3f(shadow_color[0]/255.0, shadow_color[1]/255.0, shadow_color[2]/255.0)
        glBegin(GL_QUADS)
        glVertex2f(self.x, self.y + self.height)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x + self.width - self.bevel_size, self.y + self.height - self.bevel_size)
        glVertex2f(self.x + self.bevel_size, self.y + self.height - self.bevel_size)
        glVertex2f(self.x + self.width, self.y)
        glVertex2f(self.x + self.width, self.y + self.height)
        glVertex2f(self.x + self.width - self.bevel_size, self.y + self.height - self.bevel_size)
        glVertex2f(self.x + self.width - self.bevel_size, self.y + self.bevel_size)
        glEnd()
        glColor4f(0, 0, 0, 0.3)
        glLineWidth(1.5)
        glBegin(GL_LINES)
        for i in range(1, 3):
            x_pos = self.x + i * self.width // 3
            glVertex2f(x_pos, self.y + self.bevel_size)
            glVertex2f(x_pos, self.y + self.height - self.bevel_size)
        y_pos = self.y + self.height // 2
        glVertex2f(self.x + self.bevel_size, y_pos)
        glVertex2f(self.x + self.width - self.bevel_size, y_pos)
        glEnd()

    def draw_heart_symbol(self):
        heart_x = self.x + self.width // 2
        heart_y = self.y + self.height // 2
        size = min(self.width, self.height) // 4
        glColor3f(0.5, 0.2, 0.2)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(heart_x, heart_y)
        for i in range(16 + 1):
            angle = 2 * np.pi * i / 16
            glVertex2f(heart_x + size * 1.1 * np.cos(angle),
                       heart_y + size * 1.1 * np.sin(angle))
        glEnd()
        glColor3f(1.0, 0.3, 0.3)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(heart_x, heart_y)
        for i in range(16 + 1):
            angle = 2 * np.pi * i / 16
            glVertex2f(heart_x + size * np.cos(angle),
                       heart_y + size * np.sin(angle))
        glEnd()
        glColor3f(1.0, 0.6, 0.6)
        glBegin(GL_TRIANGLES)
        glVertex2f(heart_x - size*0.3, heart_y - size*0.3)
        glVertex2f(heart_x - size*0.1, heart_y - size*0.5)
        glVertex2f(heart_x + size*0.1, heart_y - size*0.3)
        glEnd()

    def draw_arrows_symbol(self):
        arrow_x = self.x + self.width // 2
        arrow_y = self.y + self.height // 2
        glColor3f(0.1, 0.1, 0.3)
        glLineWidth(3.0)
        glBegin(GL_LINES)
        glVertex2f(arrow_x - 8, arrow_y)
        glVertex2f(arrow_x - 2, arrow_y)
        glVertex2f(arrow_x - 6, arrow_y - 3)
        glVertex2f(arrow_x - 2, arrow_y)
        glVertex2f(arrow_x - 6, arrow_y + 3)
        glVertex2f(arrow_x - 2, arrow_y)
        glVertex2f(arrow_x + 8, arrow_y)
        glVertex2f(arrow_x + 2, arrow_y)
        glVertex2f(arrow_x + 6, arrow_y - 3)
        glVertex2f(arrow_x + 2, arrow_y)
        glVertex2f(arrow_x + 6, arrow_y + 3)
        glVertex2f(arrow_x + 2, arrow_y)
        glEnd()

    def draw_ball_symbol(self):
        ball_x = self.x + self.width // 2
        ball_y = self.y + self.height // 2
        radius = min(self.width, self.height) // 5
        draw_circle(ball_x + 1, ball_y + 1, radius, (0, 100, 100))
        draw_circle(ball_x, ball_y, radius, (200, 255, 255))
        draw_circle(ball_x - radius//2, ball_y - radius//2, radius//3, (255, 255, 255))

    def draw_gun_symbol(self):
        gun_x = self.x + self.width // 2
        gun_y = self.y + self.height // 2
        draw_rect(gun_x - 6, gun_y - 2, 12, 6, (60, 60, 70))
        draw_rect(gun_x - 1, gun_y - 8, 2, 8, (80, 80, 90))
        glow_alpha = 0.4 + 0.3 * np.sin(pygame.time.get_ticks() * 0.01)
        glColor4f(1.0, 0.2, 0.2, glow_alpha)
        glBegin(GL_TRIANGLE_FAN)
        glVertex2f(gun_x, gun_y - 8)
        for i in range(8 + 1):
            angle = 2 * np.pi * i / 8
            glVertex2f(gun_x + 6 * np.cos(angle), gun_y - 8 + 6 * np.sin(angle))
        glEnd()

# === ОТРИСОВКА ФОНА ===
def draw_background():
    global game_background_texture
    if game_background_texture is not None:
        draw_texture(game_background_texture, 0, 0, WIDTH, HEIGHT)
    else:
        glClearColor(0.05, 0.05, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        glBegin(GL_QUADS)
        glColor3f(0.05, 0.05, 0.15)
        glVertex2f(0, 0)
        glVertex2f(WIDTH, 0)
        glColor3f(0.1, 0.1, 0.2)
        glVertex2f(WIDTH, HEIGHT)
        glVertex2f(0, HEIGHT)
        glEnd()
        glPointSize(1.5)
        glBegin(GL_POINTS)
        for i in range(100):
            x = (i * 137) % WIDTH
            y = (i * 97) % HEIGHT
            intensity = 0.3 + 0.7 * (i % 3) / 2
            flicker = np.sin(pygame.time.get_ticks() * 0.001 + i) * 0.2 + 0.8
            glColor3f(intensity * flicker, intensity * flicker, intensity * flicker + 0.1)
            glVertex2f(x, y)
        glEnd()
        glPointSize(2.0)
        glBegin(GL_POINTS)
        for i in range(50):
            x = (i * 73) % WIDTH
            y = (pygame.time.get_ticks() * 0.05 + i * 20) % HEIGHT
            color_val = (i % 3) / 2
            alpha = 0.3 + 0.4 * np.sin(pygame.time.get_ticks() * 0.002 + i)
            glColor4f(color_val, color_val * 0.7, 1.0, alpha)
            glVertex2f(x, y)
        glEnd()

# === ФУНКЦИИ УРОВНЕЙ ===
def distribute_4_bonuses(bricks, level):
    """Розподіляє 4 бонуси по цеглинках на рівні"""
    if len(bricks) < 4:
        return bricks
    
    bonus_types = ['life', 'expand', 'ball', 'gun']
    bonus_colors = {
        'life': YELLOW,
        'expand': SILVER,
        'ball': (0, 200, 200),
        'gun': (255, 100, 100)
    }
    
    # Визначаємо 4 позиції для бонусів (розподілені по рівню)
    total_bricks = len(bricks)
    positions = [
        total_bricks // 4,           # Перша чверть
        total_bricks // 2,           # Середина
        (3 * total_bricks) // 4,     # Третя чверть
        total_bricks - 1             # Кінець
    ]
    
    # Перемішуємо типи бонусів залежно від рівня для різноманітності
    shuffled_types = bonus_types.copy()
    shuffle_offset = level % 4
    shuffled_types = shuffled_types[shuffle_offset:] + shuffled_types[:shuffle_offset]
    
    for i, pos in enumerate(positions):
        if pos < len(bricks):
            bricks[pos].special_type = shuffled_types[i]
            bricks[pos].color = bonus_colors[shuffled_types[i]]
    
    return bricks


def create_pyramid(level):
    bricks = []
    start_y = 100
    max_rows = 8
    bricks_per_row = min(15, 5 + level)
    for row in range(max_rows):
        row_bricks = bricks_per_row - row
        if row_bricks <= 0:
            break
        row_width = row_bricks * BRICK_WIDTH
        start_x = (WIDTH - row_width) // 2
        for i in range(row_bricks):
            x = start_x + i * BRICK_WIDTH
            y = start_y + row * BRICK_HEIGHT
            color = random.choice(COLORS)
            bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks


def create_diamond(level):
    bricks = []
    center_x = WIDTH // 2
    center_y = 200
    size = min(7, 3 + level // 2)
    for i in range(-size, size + 1):
        row_width = size - abs(i) + 1
        start_x = center_x - (row_width * BRICK_WIDTH) // 2
        for j in range(row_width):
            x = start_x + j * BRICK_WIDTH
            y = center_y + i * BRICK_HEIGHT
            color = random.choice(COLORS)
            bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks


def create_heart(level):
    bricks = []
    center_x = WIDTH // 2
    center_y = 200
    size = min(5, 2 + level // 3)
    heart_pattern = [
        "  XX XX   ",
        " XXXXXXX  ",
        "XXXXXXXXX ",
        "XXXXXXXXX ",
        " XXXXXXX  ",
        "  XXXXX   ",
        "   XXX    ",
        "    X     "
    ]
    for i, row in enumerate(heart_pattern):
        for j, cell in enumerate(row):
            if cell == 'X':
                x = center_x + (j - len(row) // 2) * BRICK_WIDTH
                y = center_y + i * BRICK_HEIGHT
                color = random.choice(COLORS)
                bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks


def create_rectangle(level):
    bricks = []
    width = min(12, 6 + level)
    height = min(6, 3 + level // 2)
    start_x = (WIDTH - width * BRICK_WIDTH) // 2
    start_y = 150
    for i in range(height):
        for j in range(width):
            x = start_x + j * BRICK_WIDTH
            y = start_y + i * BRICK_HEIGHT
            color = random.choice(COLORS)
            bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks


def create_circle(level):
    bricks = []
    center_x = WIDTH // 2
    center_y = 200
    radius = min(5, 2 + level // 2)
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            if i*i + j*j <= radius*radius:
                x = center_x + j * BRICK_WIDTH
                y = center_y + i * BRICK_HEIGHT
                color = random.choice(COLORS)
                bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks


def create_arrow(level):
    bricks = []
    start_x = WIDTH // 2 - 3 * BRICK_WIDTH
    start_y = 150
    arrow_pattern = [
        "    X     ",
        "   XXX    ",
        "  XXXXX   ",
        " XXXXXXX  ",
        "XXXX XXXX ",
        "XX     XX ",
        "X       X "
    ]
    for i, row in enumerate(arrow_pattern):
        for j, cell in enumerate(row):
            if cell == 'X':
                x = start_x + j * BRICK_WIDTH
                y = start_y + i * BRICK_HEIGHT
                color = random.choice(COLORS)
                bricks.append(Brick(x, y, color, special_type=None))
    
    # Розподіляємо 4 бонуси по рівню
    bricks = distribute_4_bonuses(bricks, level)
    return bricks

def create_level(level):
    if level in [5, 10, 15, 20]:
        return []  # Для босс-уровней кирпичей нет
    pattern_type = level % 6
    if pattern_type == 0:
        bricks = create_pyramid(level)
    elif pattern_type == 1:
        bricks = create_diamond(level)
    elif pattern_type == 2:
        bricks = create_heart(level)
    elif pattern_type == 3:
        bricks = create_rectangle(level)
    elif pattern_type == 4:
        bricks = create_circle(level)
    else:
        bricks = create_arrow(level)
    return bricks

# === НОВАЯ ФУНКЦИЯ МЕНЮ С РАЗНЫМИ ВИДЕО ===
def show_menu():
    global music_playing, selected_level
    
    menu_items = ["Play", "Settings", "Exit"]
    settings_items = ["Level: {} / 20".format(selected_level), "Music: On" if music_playing else "Music: Off", "Back"]
    current_menu = "main"  # "main" или "settings"
    selected_item = 0
    FPS=30
    # Пути к видеофайлам
    main_video_path = 'intro.mp4'
    settings_video_path = 'settings.mp4'  # Специальное видео для настроек
    
    # Переменные для видео
    main_cap = None
    settings_cap = None
    
    # Загружаем видео для главного меню
    if os.path.exists(main_video_path):
        main_cap = cv2.VideoCapture(main_video_path)
        if not main_cap.isOpened():
            main_cap = None
            print("Не удалось открыть видеофайл intro.mp4")
    else:
        print("Видео intro.mp4 не найдено. Используется стандартный фон.")
    
    # Загружаем видео для настроек
    if os.path.exists(settings_video_path):
        settings_cap = cv2.VideoCapture(settings_video_path)
        if not settings_cap.isOpened():
            settings_cap = None
            print("Не удалось открыть видеофайл settings.mp4")
    else:
        print("Видео settings.mp4 не найдено. Будет использоваться intro.mp4 для настроек")
        # Если специального видео нет, используем то же что и для главного меню
        if main_cap is not None:
            settings_cap = cv2.VideoCapture(main_video_path)

    # Запуск музыки
    if music_loaded and music_playing:
        pygame.mixer.music.play(loops=-1)

    # Одна постоянная текстура для видео-фона меню — переиспользуется каждый кадр,
    # вместо glGenTextures/glDeleteTextures на каждой итерации цикла (это было дорого на Windows)
    menu_video_texture_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, menu_video_texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

    menu_running = True
    while menu_running:
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        # Выбираем текущее видео в зависимости от меню
        current_cap = main_cap if current_menu == "main" else settings_cap

        # Отображение видео, если оно загружено
        if current_cap is not None:
            ret, frame = current_cap.read()
            if ret:
                # Конвертация BGR -> RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # Изменение размера под окно
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                # Преобразование в текстуру OpenGL (обновляем существующую текстуру, а не создаём новую)
                texture_data = frame.tobytes()
                glBindTexture(GL_TEXTURE_2D, menu_video_texture_id)
                glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)

                glEnable(GL_TEXTURE_2D)
                glColor3f(1.0, 1.0, 1.0)
                glBegin(GL_QUADS)
                glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
                glTexCoord2f(1.0, 0.0); glVertex2f(WIDTH, 0)
                glTexCoord2f(1.0, 1.0); glVertex2f(WIDTH, HEIGHT)
                glTexCoord2f(0.0, 1.0); glVertex2f(0, HEIGHT)
                glEnd()
                glDisable(GL_TEXTURE_2D)
            else:
                # Видео закончилось — перезапустить
                current_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
        else:
            # Резервный вариант
            if current_menu == "main":
                draw_text("File intro.mp4 not found", WIDTH//2 - 150, HEIGHT//2 - 20, WHITE, 24)
            else:
                draw_text("File settings.mp4 not found", WIDTH//2 - 150, HEIGHT//2 - 20, WHITE, 24)

               # Отображение меню
        if current_menu == "main":
            items = menu_items
            start_y = 350
        else:  # settings
            items = settings_items
            start_y = 300
            # Дополнительная информация для настроек уровня
            if selected_item == 0:  # Если выбран пункт уровня
                hint_y = start_y + len(items) * 60 + 40
                hint_text = "< / > to change level"
                draw_text(hint_text, WIDTH//2 - 150, hint_y, CYAN, 18)

        for i, item in enumerate(items):
            y = start_y + i * 60
            color = YELLOW if i == selected_item else WHITE
            size = 32 if i == selected_item else 24
            # Подсветка выбранного пункта
            if i == selected_item:
                # Пульсирующая рамка
                pulse = np.sin(pygame.time.get_ticks() * 0.005) * 0.1 + 0.2
                glColor4f(1.0, 1.0, 0.0, pulse)
                glBegin(GL_QUADS)
                glVertex2f(WIDTH//2 - 150, y - 10)
                glVertex2f(WIDTH//2 + 150, y - 10)
                glVertex2f(WIDTH//2 + 150, y + 40)
                glVertex2f(WIDTH//2 - 150, y + 40)
                glEnd()
            draw_text(item, WIDTH//2 - len(item) * 8, y, color, size)

        # Подсказки
        hint_y = HEIGHT - 100
        draw_text("UP DOWN - navigate", WIDTH//2 - 80, hint_y, GRAY, 16)
        draw_text("ENTER - select", WIDTH//2 - 70, hint_y + 25, GRAY, 16)
        
        # Статус музыки (если не в настройках)
        if not music_loaded:
            draw_text("Add music.mp3 to the game folder", WIDTH//2 - 160, HEIGHT - 50, YELLOW, 14)

        pygame.display.flip()
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if main_cap:
                    main_cap.release()
                if settings_cap:
                    settings_cap.release()
                return "exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_item = (selected_item - 1) % len(items)
                elif event.key == pygame.K_DOWN:
                    selected_item = (selected_item + 1) % len(items)
                elif event.key == pygame.K_LEFT:
                    if current_menu == "settings" and selected_item == 0:
                        # Изменение уровня влево
                        selected_level = max(1, selected_level - 1)
                        settings_items[0] = "Level: {} / 20".format(selected_level)
                elif event.key == pygame.K_RIGHT:
                    if current_menu == "settings" and selected_item == 0:
                        # Изменение уровня вправо
                        selected_level = min(20, selected_level + 1)
                        settings_items[0] = "Level: {} / 20".format(selected_level)
                elif event.key == pygame.K_RETURN:
                    if current_menu == "main":
                        if selected_item == 0:  # Играть
                            if main_cap:
                                main_cap.release()
                            if settings_cap:
                                settings_cap.release()
                            return "play"
                        elif selected_item == 1:  # Настройки
                            current_menu = "settings"
                            selected_item = 0
                        elif selected_item == 2:  # Выход
                            if main_cap:
                                main_cap.release()
                            if settings_cap:
                                settings_cap.release()
                            return "exit"
                    else:  # settings
                        if selected_item == 1:  # Музыка
                            toggle_music()
                            settings_items[1] = "Music: On" if music_playing else "Music: Off"
                        elif selected_item == 2:  # Назад
                            current_menu = "main"
                            selected_item = 0
                elif event.key == pygame.K_ESCAPE:
                    if current_menu == "settings":
                        current_menu = "main"
                        selected_item = 0
                    else:
                        if main_cap:
                            main_cap.release()
                        if settings_cap:
                            settings_cap.release()
                        return "exit"
                elif event.key == pygame.K_m and music_loaded:
                    toggle_music()
                    if current_menu == "settings":
                        settings_items[1] = "Music: On" if music_playing else "Music: Off"

    if main_cap:
        main_cap.release()
    if settings_cap:
        settings_cap.release()
    return "exit"

# === НОВАЯ ФУНКЦИЯ ЭКРАНА ВЫХОДА С ВИДЕО ===
def show_exit_screen():
    """Показывает видео при выходе из игры"""
    global music_playing
    
    # Останавливаем игровую музыку
    if music_loaded:
        pygame.mixer.music.stop()
    
    # Путь к видеофайлу
    video_path = 'intro.mp4'  # Можно использовать то же видео или создать отдельное outro.mp4
    outro_path = 'outro.mp4'  # Проверяем наличие специального видео для выхода
    
    # Сначала проверяем наличие отдельного видео для выхода
    if os.path.exists(outro_path):
        video_path = outro_path
        print("Найдено видео для выхода: outro.mp4")
    elif os.path.exists(video_path):
        print("Используется intro.mp4 для выхода")
    else:
        print("Видео для выхода не найдено")
        return
    
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Не удалось открыть видеофайл {video_path}")
        return
    
    # Запускаем музыку для выхода (если есть)
    if music_loaded and music_playing:
        # Пробуем загрузить специальную музыку для выхода
        exit_music_files = ['exit.mp3', 'goodbye.mp3', 'music.mp3']
        music_loaded_exit = False
        for music_file in exit_music_files:
            if os.path.exists(music_file):
                try:
                    pygame.mixer.music.load(music_file)
                    pygame.mixer.music.play(loops=-1)
                    music_loaded_exit = True
                    print(f"Загружена музыка для выхода: {music_file}")
                    break
                except Exception as e:
                    print(f"Ошибка загрузки музыки для выхода {music_file}: {e}")
        
        if not music_loaded_exit and music_loaded:
            # Если нет специальной музыки, перезапускаем обычную
            pygame.mixer.music.play(loops=-1)
    
    start_time = time.time()
    duration = 5  # Длительность показа видео в секундах
    fade_start = duration - 1  # Начинаем затемнение за 1 секунду до конца
    
    while True:
        current_time = time.time()
        elapsed = current_time - start_time
        
        if elapsed >= duration:
            break
        
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Отображение видео
        ret, frame = cap.read()
        if ret:
            # Конвертация BGR -> RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Изменение размера под окно
            frame = cv2.resize(frame, (WIDTH, HEIGHT))
            # Преобразование в текстуру OpenGL
            texture_data = frame.tobytes()
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, WIDTH, HEIGHT, 0, GL_RGB, GL_UNSIGNED_BYTE, texture_data)
            
            # Определяем альфа-канал для затемнения
            alpha = 1.0
            if elapsed > fade_start:
                alpha = 1.0 - (elapsed - fade_start)
            
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glColor4f(1.0, 1.0, 1.0, alpha)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(0, 0)
            glTexCoord2f(1.0, 0.0); glVertex2f(WIDTH, 0)
            glTexCoord2f(1.0, 1.0); glVertex2f(WIDTH, HEIGHT)
            glTexCoord2f(0.0, 1.0); glVertex2f(0, HEIGHT)
            glEnd()
            glDisable(GL_TEXTURE_2D)
            
            glDeleteTextures([texture_id])
        else:
            # Если видео закончилось, зацикливаем
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        # Текст "До свидания!"
        if elapsed < duration - 1:
            # Мигающий текст
            if int(elapsed * 2) % 2 == 0:
                draw_text("GOODBYE!", WIDTH//2 - 150, HEIGHT//2 - 50, WHITE, 36)
                draw_text("Thanks for playing!", WIDTH//2 - 120, HEIGHT//2 + 20, YELLOW, 24)
        FPS=30
        pygame.display.flip()
        clock.tick(FPS)
        
        # Проверяем события, чтобы можно было прервать выход
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                cap.release()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    cap.release()
                    return
    
    cap.release()

def show_boss_intro(boss):
    """Показывает вступление перед битвой с боссом"""
    intro_duration = 180  # 3 секунды при 60 FPS
    for frame in range(intro_duration):
        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Эффект появления
        alpha = min(1.0, frame / 60)
        
        # Текст
        if frame < 60:
            draw_text("BOSS!", WIDTH//2 - 150, HEIGHT//2 - 100, RED, 36)
        elif frame < 120:
            draw_text(boss.name, WIDTH//2 - 100, HEIGHT//2 - 100, boss.color, 48)
        else:
            draw_text("GET Ready!", WIDTH//2 - 120, HEIGHT//2 - 100, YELLOW, 40)
            
        # Изображение босса (упрощенное)
        draw_rounded_rect(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 100, 20, boss.color)
        draw_circle(WIDTH//2 - 50, HEIGHT//2 - 20, 20, (255, 255, 255))
        draw_circle(WIDTH//2 + 50, HEIGHT//2 - 20, 20, (255, 255, 255))
        draw_circle(WIDTH//2 - 50, HEIGHT//2 - 20, 10, (0, 0, 0))
        draw_circle(WIDTH//2 + 50, HEIGHT//2 - 20, 10, (0, 0, 0))
        
        pygame.display.flip()
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return False
    return True

# === ОСНОВНАЯ ФУНКЦИЯ ===
def main():
    global game_background_texture, selected_level, max_level
    
    while True:
        # Показываем меню
        menu_result = show_menu()
        
        if menu_result == "exit":
            show_exit_screen()
            break
        elif menu_result == "play":
            # Загружаем игровой фон
            game_background_texture, _, _ = load_texture('background_game.png')
            
            # Инициализация игры
            paddle = Paddle()
            ball = Ball()
            balls = [ball]
            current_level = selected_level
            inverted_level = 20 - current_level
            bricks = create_level(inverted_level)
            brick_shards = []
            boss = None
            boss_active = False
            score = 0
            lives = 3
            game_over = False
            level_complete = False
            running = True
            
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r and (game_over or level_complete):
                            paddle = Paddle()
                            ball = Ball()
                            balls = [ball]
                            current_level = selected_level
                            bricks = create_level(current_level)
                            brick_shards = []
                            boss = None
                            boss_active = False
                            score = 0
                            lives = 3
                            game_over = False
                            level_complete = False
                        elif event.key == pygame.K_n and level_complete and current_level < max_level:
                            current_level += 1
                            inverted_level = 20 - current_level
                            
                            # Проверка на босс-уровень
                            if current_level in [5, 10, 15, 20]:
                                boss = Boss(current_level)
                                boss_active = True
                                bricks = []
                                show_boss_intro(boss)
                                # Создаем новый мяч для босс-уровня
                                balls = [Ball()]
                            else:
                                bricks = create_level(inverted_level)
                                boss = None
                                boss_active = False
                                balls = [Ball()]
                            
                            level_complete = False
                        elif event.key == pygame.K_m and music_loaded:
                            toggle_music()
                        elif event.key == pygame.K_ESCAPE:
                            running = False
                            
                if not game_over and not level_complete:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_LEFT]:
                        paddle.move("left")
                    if keys[pygame.K_RIGHT]:
                        paddle.move("right")
                    paddle.update()
                    
                    # === ВАЖЛИВО: рух м'ячів на всіх рівнях (включаючи боссів) ===
                    for ball in balls[:]:
                        ball.move()
                        
                        # Перевірка зіткнення з платформою
                        if ball.rect.colliderect(paddle.rect) and ball.dy > 0:
                            relative_x = (ball.x - paddle.x) / paddle.width
                            ball.dx = 8 * (relative_x - 0.5)
                            ball.dy *= -1
                            ball.glow_timer = 8
                            paddle_sound.play()
                        
                        # Перевірка виходу за нижню межу
                        if ball.y > HEIGHT:
                            balls.remove(ball)
                            continue
                    
                    # Якщо всі м'ячі втрачені
                    if not balls:
                        lives -= 1
                        if lives > 0:
                            # Створюємо новий м'яч на платформі
                            new_ball = Ball(paddle.x + paddle.width // 2, paddle.y - 20)
                            balls.append(new_ball)
                        else:
                            game_over = True
                    
                    # Обробка босса (якщо активний)
                    if boss_active and boss:
                        boss.update(paddle.x + paddle.width//2, paddle.y)
                        
                        # Перевірка зіткнення м'ячів з босом
                        for ball in balls[:]:
                            if boss.check_hit(ball.x, ball.y, ball.radius):
                                # Відскок м'яча
                                ball.dy *= -1
                                ball.glow_timer = 10
                        
                        # Перевірка зіткнення снарядів босса з платформою
                        for projectile in boss.projectiles[:]:
                            if projectile.rect.colliderect(paddle.rect):
                                if projectile.damage_type == 'normal':
                                    lives -= 1
                                    if lives <= 0:
                                        game_over = True
                                elif projectile.damage_type == 'slow':
                                    paddle.speed = max(4, paddle.speed - 2)
                                elif projectile.damage_type == 'explosive':
                                    lives -= 2
                                    if lives <= 0:
                                        game_over = True
                                projectile.active = False
                                boss.projectiles.remove(projectile)
                                
                                # Створення ефекту вибуху
                                for _ in range(10):
                                    paddle.movement_particles.append(Particle(
                                        paddle.x + paddle.width//2, paddle.y + paddle.height//2,
                                        RED, [random.uniform(-3, 3), random.uniform(-3, 3)], 4, 30
                                    ))
                        
                        # Перевірка попадання куль платформи по боссу
                        for bullet in paddle.bullets[:]:
                            if boss.check_bullet_hit(bullet):
                                bullet.active = False
                                paddle.bullets.remove(bullet)
                        
                        # Перевірка смерті босса
                        if boss.health <= 0:
                            boss_active = False
                            level_complete = True
                            score += 500  # Бонус за перемогу над босом
                            # Даємо додаткове життя за перемогу над босом
                            lives += 1
                            if current_level == max_level:
                                game_over = True
                    
                    # Звичайна ігрова логіка (кирпичі)
                    if not boss_active:
                        for ball in balls[:]:
                            for brick in bricks:
                                if brick.visible and ball.rect.colliderect(brick.rect):
                                    score, lives = resolve_brick_destruction(
                                        brick, paddle, balls, score, lives, brick_shards)
                                    ball.dy *= -1
                                    ball.glow_timer = 8
                                    break

                        for bullet in paddle.bullets[:]:
                            for brick in bricks:
                                if brick.visible and bullet.rect.colliderect(brick.rect):
                                    score, lives = resolve_brick_destruction(
                                        brick, paddle, balls, score, lives, brick_shards)
                                    bullet.active = False
                                    break
                                    
                        paddle.bullets = [bullet for bullet in paddle.bullets if bullet.active]
                        
                        # Перевірка завершення рівня
                        if bricks and all(not brick.visible for brick in bricks):
                            level_complete = True
                            if current_level == max_level:
                                game_over = True

                # Обновление осколков разбитых кирпичей (в т.ч. когда игра на паузе/окончена, чтобы анимация доигралась)
                brick_shards = [s for s in brick_shards if s.update()]

                # Отрисовка
                draw_background()
                paddle.draw()
                
                if boss_active and boss:
                    boss.draw()
                    
                for ball in balls:
                    ball.draw()
                    
                for brick in bricks:
                    brick.draw()

                for shard in brick_shards:
                    shard.draw()
                    
                # Відображення життів сердечками
                max_lives_display = 5
                heart_size = 10
                heart_spacing = heart_size + 4
                start_x = WIDTH - (max_lives_display * heart_spacing) - 10
                start_y = 10 + heart_size
                for i in range(max_lives_display):
                    filled = i < lives
                    draw_heart_icon(start_x + i * heart_spacing, start_y, heart_size, filled)
                    
                draw_text(f"Score: {score}", 20, 10, WHITE, 12)
                
                if boss_active:
                    draw_text(f"BOSS: LEVEL {current_level}", WIDTH // 2 - 70, 10, RED, 16)
                else:
                    draw_text(f"Level: {current_level}/{max_level}", WIDTH // 2 - 60, 10, CYAN, 12)
                    
                draw_text(f"Balls: {len(balls)}", WIDTH - 250, 10, YELLOW, 12)
                
                if game_over:
                    if lives <= 0:
                        draw_text("Game over! Press R to restart",
                                  WIDTH // 2 - 220, HEIGHT // 2 - 20, RED, 16)
                    else:
                        draw_text("VICTORY! PRESS R FOR A NEW GAME",
                                  WIDTH // 2 - 200, HEIGHT // 2 - 20, GREEN, 16)
                elif level_complete:
                    if current_level < max_level:
                        if boss_active and boss and boss.health <= 0:
                            draw_text(f"BOSS {current_level} DEFEATED! N - Next level",
                                      WIDTH // 2 - 280, HEIGHT // 2 - 20, GOLD, 16)
                        else:
                            draw_text(f"LEVEL {current_level} COMPLETE! N - Next level",
                                      WIDTH // 2 - 240, HEIGHT // 2 - 20, CYAN, 16)
                    else:
                        draw_text("FINAL LEVEL COMPLETE! PRESS R",
                                  WIDTH // 2 - 260, HEIGHT // 2 - 20, GOLD, 16)
                    
                    # Підказки по бонусах (тільки якщо не босс)
                    if not boss_active:
                        draw_text("* GOLD: +1 LIFE", WIDTH//2 - 100, HEIGHT - 30, GOLD, 10)
                        draw_text("<> SILVER: EXPAND", WIDTH//2 - 320, HEIGHT - 30, SILVER, 10)
                        draw_text("o CYAN: +1 BALL", WIDTH//2 + 120, HEIGHT - 30, (0, 200, 200), 10)
                        draw_text("X RED: WEAPON", WIDTH//2 + 350, HEIGHT - 30, (255, 100, 100), 10)
                
                # Статус музики
                if music_loaded:
                    music_status = "M: MUSIC ON" if music_playing else "M: MUSIC OFF"
                    music_color = GREEN if music_playing else RED
                    draw_text(music_status, 16, HEIGHT - 30, music_color, 14)
                
                # Підказка для босс-рівнів
                if current_level in [5, 10, 15, 20] and boss_active and not level_complete and not game_over:
                    draw_text("! BOSS FIGHT! AIM FOR THE RED DOTS !", 
                             WIDTH//2 - 250, HEIGHT - 60, RED, 18)
                
                pygame.display.flip()
                clock.tick(FPS)
            
            # Освобождаем текстуру фона
            if game_background_texture is not None:
                glDeleteTextures([game_background_texture])
                game_background_texture = None
    
    # Завершення роботи
    if music_loaded:
        pygame.mixer.music.stop()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
