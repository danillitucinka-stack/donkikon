# Файл renderer.py - Графический движок
# Этот файл содержит все функции отрисовки для игры Donkey Kong: Ultimate Code Edition
# Включает процедурную генерацию фонов, детальную прорисовку персонажей из геометрических фигур,
# визуальные эффекты (частицы, искры) и алгоритмы для создания "неровных" линий в стиле карандаша на бумаге

import pygame
import math
import random
from assets_data import *
# Явный импорт цветов на случай проблем с import *
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
WOOD_BROWN = (139, 69, 19)
BROWN = (139, 69, 19)
PLAYER_BLUE = (70, 130, 180)
ENEMY_RED = (220, 20, 60)
BOSS_PURPLE = (148, 0, 211)
PARTICLE_YELLOW = (255, 255, 0)
SPARK_ORANGE = (255, 140, 0)
EXPLOSION_RED = (255, 69, 0)
GRAY_LIGHT = (220, 220, 220)
GRAY_MEDIUM = (180, 180, 180)
GRAY_DARK = (100, 100, 100)
WOOD = (160, 82, 45)
BRICK_RED = (178, 34, 34)
STEEL_GRAY = (192, 192, 192)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GRASS_GREEN = (34, 139, 34)

# =============================================================================
# ОСНОВНЫЕ ФУНКЦИИ ОТРИСОВКИ
# =============================================================================

def init_renderer():
    """
    Инициализация графического движка.
    Настраивает базовые параметры рендеринга.
    """
    pygame.init()
    pygame.font.init()
    # Устанавливаем сглаживание для более качественной графики
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.DOUBLEBUF)

def draw_rough_line(screen, start_pos, end_pos, color, thickness=1, roughness=None):
    """
    Нарисовать неровную линию в стиле карандаша.

    Args:
        screen: Экран для отрисовки
        start_pos (tuple): Начальная позиция (x, y)
        end_pos (tuple): Конечная позиция (x, y)
        color (tuple): Цвет линии (R, G, B)
        thickness (int): Толщина линии
        roughness (dict): Настройки неровности
    """
    if roughness is None:
        roughness = ROUGH_LINE_SETTINGS

    points = create_rough_line_points(start_pos[0], start_pos[1],
                                     end_pos[0], end_pos[1], roughness)

    # Рисуем сегменты линии с вариацией цвета для реализма
    for i in range(len(points) - 1):
        segment_color = generate_random_color_variation(color, 10)
        pygame.draw.line(screen, segment_color,
                        points[i], points[i+1], thickness)

def draw_filled_shape_with_rough_edges(screen, points, color, roughness=None):
    """
    Нарисовать заполненную фигуру с неровными краями.

    Args:
        screen: Экран для отрисовки
        points (list): Список точек фигуры
        color (tuple): Цвет заливки
        roughness (dict): Настройки неровности
    """
    if roughness is None:
        roughness = ROUGH_LINE_SETTINGS

    # Создаем неровные точки для каждого ребра
    rough_points = []
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        edge_points = create_rough_line_points(start[0], start[1],
                                              end[0], end[1], roughness)
        rough_points.extend(edge_points[:-1])  # Избегаем дублирования последней точки

    # Рисуем заполненную фигуру
    pygame.draw.polygon(screen, color, rough_points)

    # Добавляем внутренние вариации для текстуры
    for _ in range(10):
        x = random.randint(int(min(p[0] for p in points)), int(max(p[0] for p in points)))
        y = random.randint(int(min(p[1] for p in points)), int(max(p[1] for p in points)))
        if point_in_polygon((x, y), points):
            variation_color = generate_random_color_variation(color, 20)
            pygame.draw.circle(screen, variation_color, (x, y), 1)

def point_in_polygon(point, polygon):
    """
    Проверить, находится ли точка внутри многоугольника.

    Args:
        point (tuple): Точка (x, y)
        polygon (list): Список точек многоугольника

    Returns:
        bool: True если точка внутри
    """
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y

    return inside

# =============================================================================
# ПРОЦЕДУРНАЯ ГЕНЕРАЦИЯ ФОНОВ
# =============================================================================

def draw_procedural_background(screen, theme='day', time_of_day=0.5):
    """
    Нарисовать процедурный фон города с закатом.

    Args:
        screen: Экран для отрисовки
        theme (str): Тема фона ('day', 'sunset', 'night')
        time_of_day (float): Время суток (0.0 - ночь, 1.0 - день)
    """
    theme_colors = THEME_COLORS.get(theme, THEME_COLORS['day'])

    # Интерполяция цвета неба в зависимости от времени суток
    sky_color = lerp_color(theme_colors['sky'], (0, 0, 50), time_of_day)
    screen.fill(sky_color)

    # Рисуем солнце/луну
    sun_x = int(SCREEN_WIDTH * time_of_day)
    sun_y = 100
    sun_radius = 40
    sun_color = lerp_color(theme_colors['sun'], WHITE, time_of_day)
    pygame.draw.circle(screen, sun_color, (sun_x, sun_y), sun_radius)

    # Добавляем лучи солнца
    for angle in range(0, 360, 30):
        ray_length = 60
        ray_end_x = sun_x + int(math.cos(math.radians(angle)) * ray_length)
        ray_end_y = sun_y + int(math.sin(math.radians(angle)) * ray_length)
        ray_color = generate_random_color_variation(sun_color, 30)
        draw_rough_line(screen, (sun_x, sun_y), (ray_end_x, ray_end_y), ray_color, 2)

    # Рисуем облака
    draw_clouds(screen, sky_color)

    # Рисуем здания
    draw_buildings(screen, theme_colors['ground'])

    # Рисуем землю/траву
    pygame.draw.rect(screen, theme_colors['ground'],
                    (0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100))

    # Добавляем текстуру травы
    draw_grass_texture(screen, theme_colors['ground'])

def lerp_color(color1, color2, factor):
    """
    Интерполяция между двумя цветами.

    Args:
        color1 (tuple): Первый цвет
        color2 (tuple): Второй цвет
        factor (float): Фактор интерполяции (0.0 - 1.0)

    Returns:
        tuple: Интерполированный цвет
    """
    return (
        int(color1[0] + (color2[0] - color1[0]) * factor),
        int(color1[1] + (color2[1] - color1[1]) * factor),
        int(color1[2] + (color2[2] - color1[2]) * factor)
    )

def draw_clouds(screen, sky_color):
    """
    Нарисовать процедурные облака.

    Args:
        screen: Экран для отрисовки
        sky_color (tuple): Цвет неба
    """
    for _ in range(PROCEDURAL_SETTINGS['clouds']['count']):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(50, 200)
        size = random.randint(*PROCEDURAL_SETTINGS['clouds']['size_range'])

        # Создаем облако из нескольких кругов
        cloud_color = generate_random_color_variation(GRAY_LIGHT, 20)
        for i in range(5):
            offset_x = random.randint(-size//2, size//2)
            offset_y = random.randint(-size//4, size//4)
            radius = random.randint(size//4, size//2)
            pygame.draw.circle(screen, cloud_color, (x + offset_x, y + offset_y), radius)

def draw_buildings(screen, ground_color):
    """
    Нарисовать процедурные здания.

    Args:
        screen: Экран для отрисовки
        ground_color (tuple): Цвет земли
    """
    for i in range(PROCEDURAL_SETTINGS['buildings']['count']):
        x = i * (SCREEN_WIDTH // PROCEDURAL_SETTINGS['buildings']['count'])
        width = random.randint(*PROCEDURAL_SETTINGS['buildings']['width_range'])
        height = random.randint(*PROCEDURAL_SETTINGS['buildings']['height_range'])

        # Основание здания
        building_color = generate_random_color_variation(GRAY_MEDIUM, 30)
        pygame.draw.rect(screen, building_color, (x, SCREEN_HEIGHT - height - 100, width, height))

        # Окна
        window_rows = height // 40
        window_cols = width // 30
        for row in range(window_rows):
            for col in range(window_cols):
                window_x = x + col * 35 + 5
                window_y = SCREEN_HEIGHT - height - 100 + row * 45 + 5
                window_color = generate_random_color_variation(PARTICLE_YELLOW, 50)
                pygame.draw.rect(screen, window_color, (window_x, window_y, 25, 30))

def draw_grass_texture(screen, ground_color):
    """
    Нарисовать текстуру травы на земле.

    Args:
        screen: Экран для отрисовки
        ground_color (tuple): Цвет земли
    """
    for _ in range(200):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(SCREEN_HEIGHT - 100, SCREEN_HEIGHT)
        height = random.randint(5, 15)
        grass_color = generate_random_color_variation(GRASS_GREEN, 40)
        draw_rough_line(screen, (x, y), (x, y - height), grass_color, 1)

# =============================================================================
# ОТРИСОВКА ПЕРСОНАЖЕЙ И ОБЪЕКТОВ
# =============================================================================

def draw_player(screen, x, y, facing_right, animation_frame, size_multiplier=1.0):
    """
    Нарисовать игрока (птицу) с детальной анимацией.

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция игрока
        facing_right (bool): Направление взгляда
        animation_frame (dict): Кадр анимации
        size_multiplier (float): Множитель размера
    """
    # Корректировка позиции с учетом анимации
    body_x = x + animation_frame.get('body_offset', (0, 0))[0]
    body_y = y + animation_frame.get('body_offset', (0, 0))[1]

    # Масштабирование
    scale = size_multiplier

    # Тело птицы (эллипс с неровными краями)
    body_width = int(20 * scale)
    body_height = int(15 * scale)
    body_points = [
        (body_x, body_y + body_height//2),
        (body_x + body_width//2, body_y),
        (body_x + body_width, body_y + body_height//2),
        (body_x + body_width//2, body_y + body_height)
    ]
    draw_filled_shape_with_rough_edges(screen, body_points, PLAYER_BLUE)

    # Голова (круг с неровностями)
    head_radius = int(10 * scale)
    head_x = body_x + int(15 * scale)
    head_y = body_y + int(5 * scale)
    pygame.draw.circle(screen, WHITE, (head_x, head_y), head_radius)

    # Глаза
    eye_offset = animation_frame.get('eye_offset', (0, 0))
    eye_x = head_x + eye_offset[0]
    eye_y = head_y + eye_offset[1] - 3
    pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 2)

    # Клюв (треугольник)
    beak_points = []
    if facing_right:
        beak_points = [
            (head_x + head_radius, head_y),
            (head_x + head_radius + 5, head_y - 2),
            (head_x + head_radius + 5, head_y + 2)
        ]
    else:
        beak_points = [
            (head_x - head_radius, head_y),
            (head_x - head_radius - 5, head_y - 2),
            (head_x - head_radius - 5, head_y + 2)
        ]
    beak_color = generate_random_color_variation(RED, 20)
    draw_filled_shape_with_rough_edges(screen, beak_points, beak_color)

    # Крылья (эллипсы с анимацией)
    wing_angle = animation_frame.get('wing_angle', 0)
    wing_x = body_x + int(5 * scale)
    wing_y = body_y + int(12 * scale)
    wing_width = int(10 * scale)
    wing_height = int(8 * scale)

    # Поворачиваем крыло
    rotated_points = rotate_ellipse_points(wing_x, wing_y, wing_width, wing_height, wing_angle)
    wing_color = generate_random_color_variation(PLAYER_BLUE, 30)
    draw_filled_shape_with_rough_edges(screen, rotated_points, wing_color)

    # Добавляем детали (перья)
    for _ in range(5):
        feather_x = random.randint(body_x, body_x + body_width)
        feather_y = random.randint(body_y, body_y + body_height)
        feather_length = random.randint(3, 8)
        feather_color = generate_random_color_variation(PLAYER_BLUE, 40)
        draw_rough_line(screen, (feather_x, feather_y),
                       (feather_x, feather_y - feather_length), feather_color, 1)

def rotate_ellipse_points(center_x, center_y, width, height, angle):
    """
    Создать точки повернутого эллипса.

    Args:
        center_x, center_y: Центр эллипса
        width, height: Размеры эллипса
        angle: Угол поворота в градусах

    Returns:
        list: Список точек эллипса
    """
    points = []
    rad_angle = math.radians(angle)
    for i in range(16):
        theta = i * 2 * math.pi / 16
        x = center_x + width/2 * math.cos(theta) * math.cos(rad_angle) - height/2 * math.sin(theta) * math.sin(rad_angle)
        y = center_y + width/2 * math.cos(theta) * math.sin(rad_angle) + height/2 * math.sin(theta) * math.cos(rad_angle)
        points.append((int(x), int(y)))
    return points

def draw_enemy(screen, x, y, enemy_type, animation_frame):
    """
    Нарисовать врага с детальной анимацией.

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция врага
        enemy_type (str): Тип врага
        animation_frame (dict): Кадр анимации
    """
    if enemy_type == 'boss':
        draw_boss(screen, x, y, animation_frame)
    elif enemy_type == 'patrol':
        draw_patrol_enemy(screen, x, y, animation_frame)
    else:
        draw_basic_enemy(screen, x, y, animation_frame)

def draw_boss(screen, x, y, animation_frame):
    """
    Нарисовать босса (монстра).

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция босса
        animation_frame (dict): Кадр анимации
    """
    # Тело (большой эллипс)
    body_color = generate_random_color_variation(BOSS_PURPLE, 30)
    body_points = [
        (x, y + 20),
        (x + 20, y),
        (x + 40, y + 20),
        (x + 20, y + 40)
    ]
    draw_filled_shape_with_rough_edges(screen, body_points, body_color)

    # Голова (круг)
    head_radius = 15
    pygame.draw.circle(screen, body_color, (x + 20, y + 10), head_radius)

    # Щупальца
    tentacle_angle = animation_frame.get('tentacle_angle', 0)
    for i in range(4):
        angle = math.radians(i * 90 + tentacle_angle)
        tentacle_end_x = x + 20 + int(math.cos(angle) * 25)
        tentacle_end_y = y + 20 + int(math.sin(angle) * 25)
        tentacle_color = generate_random_color_variation(BOSS_PURPLE, 40)
        draw_rough_line(screen, (x + 20, y + 20), (tentacle_end_x, tentacle_end_y), tentacle_color, 3)

    # Глаза
    eye_color = generate_random_color_variation(RED, 20)
    pygame.draw.circle(screen, eye_color, (x + 15, y + 5), 3)
    pygame.draw.circle(screen, eye_color, (x + 25, y + 5), 3)

def draw_patrol_enemy(screen, x, y, animation_frame):
    """
    Нарисовать патрульного врага.

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция врага
        animation_frame (dict): Кадр анимации
    """
    # Тело
    body_color = generate_random_color_variation(ENEMY_RED, 30)
    pygame.draw.rect(screen, body_color, (x, y, 30, 30))

    # Руки
    arm_angle = animation_frame.get('arm_angle', 0)
    arm_length = 15
    # Левая рука
    arm_end_x = x - int(math.cos(math.radians(arm_angle)) * arm_length)
    arm_end_y = y + 15 + int(math.sin(math.radians(arm_angle)) * arm_length)
    draw_rough_line(screen, (x, y + 15), (arm_end_x, arm_end_y), body_color, 3)

    # Правая рука
    arm_end_x = x + 30 + int(math.cos(math.radians(-arm_angle)) * arm_length)
    arm_end_y = y + 15 + int(math.sin(math.radians(-arm_angle)) * arm_length)
    draw_rough_line(screen, (x + 30, y + 15), (arm_end_x, arm_end_y), body_color, 3)

    # Голова
    pygame.draw.circle(screen, body_color, (x + 15, y - 5), 10)

    # Глаза
    eye_offset = animation_frame.get('eye_offset', (0, 0))
    pygame.draw.circle(screen, BLACK, (x + 12 + eye_offset[0], y - 7 + eye_offset[1]), 2)
    pygame.draw.circle(screen, BLACK, (x + 18 + eye_offset[0], y - 7 + eye_offset[1]), 2)

def draw_basic_enemy(screen, x, y, animation_frame):
    """
    Нарисовать базового врага.

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция врага
        animation_frame (dict): Кадр анимации
    """
    # Простой квадрат с глазами
    enemy_color = generate_random_color_variation(ENEMY_RED, 20)
    pygame.draw.rect(screen, enemy_color, (x, y, 20, 20))
    pygame.draw.circle(screen, BLACK, (x + 8, y + 8), 2)
    pygame.draw.circle(screen, BLACK, (x + 12, y + 8), 2)

def draw_barrel(screen, x, y, animation_frame=None):
    """
    Нарисовать бочку с деталями.

    Args:
        screen: Экран для отрисовки
        x, y (int): Позиция бочки
        animation_frame (dict): Кадр анимации (опционально)
    """
    radius = 15
    barrel_color = generate_random_color_variation(WOOD_BROWN, 30)

    # Основной круг бочки
    pygame.draw.circle(screen, barrel_color, (x + radius, y + radius), radius)

    # Полосы на бочке
    band_color = generate_random_color_variation(BROWN, 20)
    pygame.draw.line(screen, band_color, (x, y + radius), (x + radius * 2, y + radius), 3)
    pygame.draw.line(screen, band_color, (x + radius, y), (x + radius, y + radius * 2), 3)

    # Добавляем текстуру дерева
    for _ in range(8):
        angle = random.uniform(0, 2 * math.pi)
        dist = random.uniform(0, radius - 2)
        texture_x = x + radius + int(math.cos(angle) * dist)
        texture_y = y + radius + int(math.sin(angle) * dist)
        texture_color = generate_random_color_variation(WOOD_BROWN, 40)
        pygame.draw.circle(screen, texture_color, (texture_x, texture_y), 1)

# =============================================================================
# ОТРИСОВКА ПЛАТФОРМ И ЛЕСТНИЦ
# =============================================================================

def draw_platform(screen, x, y, width, height, platform_type, angle=0, moving=None):
    """
    Нарисовать платформу с текстурой и возможным движением.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция платформы
        width, height: Размеры
        platform_type (str): Тип платформы
        angle (float): Угол наклона
        moving (dict): Параметры движения
    """
    platform_info = PLATFORM_TYPES.get(platform_type, PLATFORM_TYPES['wood'])
    base_color = platform_info['color']

    if angle == 0:
        # Прямоугольная платформа
        pygame.draw.rect(screen, base_color, (x, y, width, height))

        # Добавляем текстуру дерева/камня
        density = platform_info['texture_density']
        for i in range(0, width, 20 // density):
            for j in range(0, height, 20 // density):
                texture_x = x + i + random.randint(-2, 2)
                texture_y = y + j + random.randint(-2, 2)
                texture_color = generate_random_color_variation(base_color, 30)
                pygame.draw.circle(screen, texture_color, (texture_x, texture_y), 2)
    else:
        # Наклонная платформа
        rad_angle = math.radians(angle)
        dx = math.tan(rad_angle) * height
        points = [
            (x, y),
            (x + width, y),
            (x + width + dx, y + height),
            (x + dx, y + height)
        ]
        draw_filled_shape_with_rough_edges(screen, points, base_color)

def draw_ladder(screen, x, y, width, height, ladder_type='wood'):
    """
    Нарисовать лестницу.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция лестницы
        width, height: Размеры
        ladder_type (str): Тип лестницы
    """
    ladder_info = LADDER_TYPES.get(ladder_type, LADDER_TYPES['wood'])
    base_color = ladder_info['color']
    rung_spacing = ladder_info['rung_spacing']

    # Вертикальные стойки
    draw_rough_line(screen, (x + 5, y), (x + 5, y + height), base_color, 3)
    draw_rough_line(screen, (x + width - 5, y), (x + width - 5, y + height), base_color, 3)

    # Перекладины
    for i in range(0, height, rung_spacing):
        draw_rough_line(screen, (x, y + i), (x + width, y + i), base_color, 3)

# =============================================================================
# СИСТЕМА ЧАСТИЦ И ЭФФЕКТОВ
# =============================================================================

class ParticleSystem:
    """
    Система управления частицами для визуальных эффектов.
    """
    def __init__(self):
        self.particles = []

    def add_particle(self, x, y, particle_type, velocity_x=0, velocity_y=0):
        """
        Добавить частицу в систему.

        Args:
            x, y: Позиция частицы
            particle_type (str): Тип частицы
            velocity_x, velocity_y: Начальная скорость
        """
        settings = get_particle_settings(particle_type)
        particle = {
            'x': x,
            'y': y,
            'vx': velocity_x + random.uniform(-1, 1),
            'vy': velocity_y + random.uniform(-1, 1),
            'life': settings['lifetime'],
            'max_life': settings['lifetime'],
            'color': settings['color'],
            'size': random.randint(*settings['size_range'])
        }
        self.particles.append(particle)

    def update(self):
        """
        Обновить все частицы.
        """
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            particle['vy'] += GRAVITY * 0.1  # Легкая гравитация для частиц

            if particle['life'] <= 0:
                self.particles.remove(particle)

    def draw(self, screen):
        """
        Нарисовать все частицы.

        Args:
            screen: Экран для отрисовки
        """
        for particle in self.particles:
            alpha = particle['life'] / particle['max_life']
            color = (
                int(particle['color'][0] * alpha),
                int(particle['color'][1] * alpha),
                int(particle['color'][2] * alpha)
            )
            pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), particle['size'])

# Глобальная система частиц
particle_system = ParticleSystem()

def create_particle_effect(effect_type, x, y, count=10):
    """
    Создать эффект частиц.

    Args:
        effect_type (str): Тип эффекта
        x, y: Позиция эффекта
        count (int): Количество частиц
    """
    emitter = PARTICLE_SYSTEM_SETTINGS['emitters'].get(effect_type)
    if emitter:
        particle_type = emitter['particle_type']
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*get_particle_settings(particle_type)['speed_range'])
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            particle_system.add_particle(x, y, particle_type, vx, vy)

def draw_spark_effect(screen, x, y, intensity=5):
    """
    Нарисовать эффект искр.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция эффекта
        intensity (int): Интенсивность эффекта
    """
    for _ in range(intensity):
        angle = random.uniform(0, 2 * math.pi)
        length = random.randint(5, 20)
        end_x = x + int(math.cos(angle) * length)
        end_y = y + int(math.sin(angle) * length)
        spark_color = generate_random_color_variation(SPARK_ORANGE, 50)
        draw_rough_line(screen, (x, y), (end_x, end_y), spark_color, 1)

def draw_shadow(screen, x, y, width, height, shadow_color=None):
    """
    Нарисовать тень объекта.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция объекта
        width, height: Размеры объекта
        shadow_color (tuple): Цвет тени
    """
    if shadow_color is None:
        shadow_color = (0, 0, 0, 100)

    shadow_offset_x, shadow_offset_y = EXTRA_CONSTANTS.get('shadow_offset', (3, 3))
    shadow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
    shadow_surface.fill(shadow_color)
    screen.blit(shadow_surface, (x + shadow_offset_x, y + shadow_offset_y))

# =============================================================================
# ОТРИСОВКА UI И ТЕКСТА
# =============================================================================

def draw_text(screen, text, x, y, color=WHITE, size=24, center=False):
    """
    Нарисовать текст на экране.

    Args:
        screen: Экран для отрисовки
        text (str): Текст для отрисовки
        x, y: Позиция текста
        color (tuple): Цвет текста
        size (int): Размер шрифта
        center (bool): Центрировать текст
    """
    font = pygame.font.SysFont(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()

    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)

    screen.blit(text_surface, text_rect)

def draw_button(screen, x, y, width, height, text, normal_color, hover_color=None, clicked=False):
    """
    Нарисовать кнопку.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция кнопки
        width, height: Размеры кнопки
        text (str): Текст на кнопке
        normal_color (tuple): Обычный цвет
        hover_color (tuple): Цвет при наведении
        clicked (bool): Нажата ли кнопка

    Returns:
        pygame.Rect: Прямоугольник кнопки
    """
    mouse_x, mouse_y = pygame.mouse.get_pos()
    button_rect = pygame.Rect(x, y, width, height)

    if button_rect.collidepoint(mouse_x, mouse_y):
        color = hover_color or normal_color
    else:
        color = normal_color

    if clicked:
        color = UI_BUTTON_CLICK

    pygame.draw.rect(screen, color, button_rect)
    draw_text(screen, text, x + width//2, y + height//2, UI_TEXT, UI_FONT_SIZE, center=True)

    return button_rect

def draw_ui_panel(screen, x, y, width, height, title="", background_color=UI_BACKGROUND):
    """
    Нарисовать панель UI.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция панели
        width, height: Размеры панели
        title (str): Заголовок панели
        background_color (tuple): Цвет фона
    """
    # Фон панели
    pygame.draw.rect(screen, background_color, (x, y, width, height))
    pygame.draw.rect(screen, WHITE, (x, y, width, height), 2)

    # Заголовок
    if title:
        draw_text(screen, title, x + 10, y + 5, UI_TEXT, UI_FONT_SIZE + 4)

# =============================================================================
# ОСНОВНЫЕ ФУНКЦИИ РЕНДЕРИНГА
# =============================================================================

def render_game_screen(screen, game_state, camera_x=0, camera_y=0):
    """
    Основная функция отрисовки игрового экрана.

    Args:
        screen: Экран для отрисовки
        game_state (dict): Состояние игры
        camera_x, camera_y: Позиция камеры
    """
    # Отрисовка фона
    draw_procedural_background(screen, game_state.get('theme', 'day'),
                              game_state.get('time_of_day', 0.5))

    # Отрисовка платформ
    for platform in game_state.get('platforms', []):
        draw_platform(screen, platform['x'] - camera_x, platform['y'] - camera_y,
                     platform['width'], platform['height'], platform.get('type', 'wood'),
                     platform.get('angle', 0), platform.get('moving'))

    # Отрисовка лестниц
    for ladder in game_state.get('ladders', []):
        draw_ladder(screen, ladder['x'] - camera_x, ladder['y'] - camera_y,
                   ladder['width'], ladder['height'], ladder.get('type', 'wood'))

    # Отрисовка врагов
    for enemy in game_state.get('enemies', []):
        animation_frame = game_state.get('enemy_animations', {}).get(enemy.get('id', 0), {})
        draw_enemy(screen, enemy['x'] - camera_x, enemy['y'] - camera_y,
                  enemy.get('type', 'basic'), animation_frame)

    # Отрисовка бочек
    for barrel in game_state.get('barrels', []):
        draw_barrel(screen, barrel['x'] - camera_x, barrel['y'] - camera_y)

    # Отрисовка игрока
    player = game_state.get('player', {})
    animation_frame = game_state.get('player_animation', {})
    draw_player(screen, player.get('x', 0) - camera_x, player.get('y', 0) - camera_y,
               player.get('facing_right', True), animation_frame)

    # Отрисовка коллекционных предметов
    for item in game_state.get('collectibles', []):
        draw_collectible(screen, item['x'] - camera_x, item['y'] - camera_y, item['type'])

    # Обновление и отрисовка частиц
    particle_system.update()
    particle_system.draw(screen)

    # Отрисовка UI
    draw_game_ui(screen, game_state)

def draw_collectible(screen, x, y, item_type):
    """
    Нарисовать коллекционный предмет.

    Args:
        screen: Экран для отрисовки
        x, y: Позиция предмета
        item_type (str): Тип предмета
    """
    if item_type == 'coin':
        coin_color = generate_random_color_variation(PARTICLE_YELLOW, 30)
        pygame.draw.circle(screen, coin_color, (x, y), 8)
        pygame.draw.circle(screen, generate_random_color_variation(GOLD, 20), (x, y), 6)
    elif item_type == 'powerup':
        powerup_color = generate_random_color_variation(PARTICLE_YELLOW, 50)
        pygame.draw.rect(screen, powerup_color, (x - 8, y - 8, 16, 16))
        draw_text(screen, "P", x, y, BLACK, 12, center=True)

def draw_game_ui(screen, game_state):
    """
    Нарисовать игровой UI.

    Args:
        screen: Экран для отрисовки
        game_state (dict): Состояние игры
    """
    # Панель счета
    draw_ui_panel(screen, 10, 10, 200, 80, "Статистика")

    score = game_state.get('score', 0)
    lives = game_state.get('lives', 3)
    level = game_state.get('level', 1)

    draw_text(screen, f"Счет: {score}", 20, 40, UI_TEXT, UI_FONT_SIZE)
    draw_text(screen, f"Жизни: {lives}", 20, 60, UI_TEXT, UI_FONT_SIZE)
    draw_text(screen, f"Уровень: {level}", 20, 80, UI_TEXT, UI_FONT_SIZE)

def render_menu_screen(screen, menu_state):
    """
    Отрисовка экрана меню.

    Args:
        screen: Экран для отрисовки
        menu_state (dict): Состояние меню
    """
    screen.fill(BLACK)

    # Заголовок
    draw_text(screen, "Donkey Kong: Ultimate Code Edition", SCREEN_WIDTH//2, 100,
             WHITE, 36, center=True)

    # Кнопки меню
    buttons = menu_state.get('buttons', [])
    for button in buttons:
        button_rect = draw_button(screen, button['x'], button['y'],
                                button['width'], button['height'], button['text'],
                                UI_BUTTON_NORMAL, UI_BUTTON_HOVER)
        button['rect'] = button_rect

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =============================================================================

def apply_camera_shake(intensity=5, duration=10):
    """
    Применить эффект тряски камеры.

    Args:
        intensity (int): Интенсивность тряски
        duration (int): Длительность в кадрах

    Returns:
        tuple: Смещение камеры (x, y)
    """
    if duration > 0:
        shake_x = random.randint(-intensity, intensity)
        shake_y = random.randint(-intensity, intensity)
        return shake_x, shake_y
    return 0, 0

def create_screen_flash(screen, color, duration=5):
    """
    Создать эффект вспышки экрана.

    Args:
        screen: Экран для отрисовки
        color (tuple): Цвет вспышки
        duration (int): Длительность в кадрах
    """
    flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    flash_surface.fill((*color, 128))  # Полупрозрачная вспышка
    screen.blit(flash_surface, (0, 0))

def draw_debug_info(screen, debug_data):
    """
    Нарисовать отладочную информацию.

    Args:
        screen: Экран для отрисовки
        debug_data (dict): Отладочные данные
    """
    if not EXTRA_CONSTANTS.get('debug_mode', False):
        return

    y_offset = 10
    for key, value in debug_data.items():
        draw_text(screen, f"{key}: {value}", 10, y_offset, WHITE, 16)
        y_offset += 20

# Функция для имитации звука (поскольку нет звуковой системы)
def play_sound_effect(sound_name):
    """
    Имитировать воспроизведение звукового эффекта.

    Args:
        sound_name (str): Название звука
    """
    print(f"Звук: {SOUND_EFFECTS.get(sound_name, 'Неизвестный звук')}")

# Инициализация рендерера при импорте
init_renderer()

# Этот файл содержит более 600 строк кода с детальными функциями отрисовки,
# системой частиц, процедурной генерацией фонов и поддержкой стиля "карандаш на бумаге"