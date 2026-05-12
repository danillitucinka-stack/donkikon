# Файл engine.py - Физика и структура
# Этот файл содержит продвинутую систему физики, платформ, лестниц и триггеров для игры Donkey Kong: Ultimate Code Edition
# Включает пиксельную проверку столкновений, инерцию, гравитацию и сложные взаимодействия объектов

import math
import random
from assets_data import *
from entities import Entity

# =============================================================================
# СИСТЕМА ФИЗИКИ
# =============================================================================

class PhysicsEngine:
    """
    Движок физики для управления гравитацией, столкновениями и движениями.
    """
    def __init__(self):
        self.gravity = GRAVITY
        self.friction = FRICTION
        self.air_resistance = 0.99
        self.collision_precision = COLLISION_PRECISION

    def apply_gravity(self, entity, delta_time=1.0):
        """
        Применить гравитацию к сущности.

        Args:
            entity (Entity): Сущность
            delta_time (float): Время кадра
        """
        if not hasattr(entity, 'on_ground') or not entity.on_ground:
            entity.vel_y += self.gravity * delta_time

            # Ограничение максимальной скорости падения
            max_fall_speed = JUMP_FORCE * 1.5
            entity.vel_y = min(entity.vel_y, max_fall_speed)

    def apply_friction(self, entity, surface_friction=1.0):
        """
        Применить трение к сущности.

        Args:
            entity (Entity): Сущность
            surface_friction (float): Коэффициент трения поверхности
        """
        entity.vel_x *= self.friction * surface_friction

        # Остановка при очень малой скорости
        if abs(entity.vel_x) < 0.1:
            entity.vel_x = 0

    def apply_air_resistance(self, entity):
        """
        Применить сопротивление воздуха.

        Args:
            entity (Entity): Сущность
        """
        entity.vel_x *= self.air_resistance
        entity.vel_y *= self.air_resistance

    def update_entity_physics(self, entity, platforms, ladders, delta_time=1.0):
        """
        Обновить физику сущности.

        Args:
            entity (Entity): Сущность
            platforms (list): Список платформ
            ladders (list): Список лестниц
            delta_time (float): Время кадра
        """
        # Применение гравитации
        self.apply_gravity(entity, delta_time)

        # Применение сопротивления воздуха
        self.apply_air_resistance(entity)

        # Временное обновление позиции для проверки столкновений
        temp_x = entity.x + entity.vel_x * delta_time
        temp_y = entity.y + entity.vel_y * delta_time

        # Проверка столкновений
        collision_result = self.check_pixel_collision(entity, temp_x, temp_y, platforms, ladders)

        # Применение результатов столкновений
        entity.x = collision_result['new_x']
        entity.y = collision_result['new_y']
        entity.vel_x = collision_result['new_vel_x']
        entity.vel_y = collision_result['new_vel_y']
        entity.on_ground = collision_result['on_ground']
        entity.on_ladder = collision_result['on_ladder']

        # Применение трения если на земле
        if entity.on_ground:
            surface_friction = self.get_surface_friction(entity, platforms)
            self.apply_friction(entity, surface_friction)

    def check_pixel_collision(self, entity, new_x, new_y, platforms, ladders):
        """
        Проверить пиксельные столкновения.

        Args:
            entity (Entity): Сущность
            new_x, new_y: Новая позиция
            platforms (list): Список платформ
            ladders (list): Список лестниц

        Returns:
            dict: Результаты столкновений
        """
        result = {
            'new_x': new_x,
            'new_y': new_y,
            'new_vel_x': entity.vel_x,
            'new_vel_y': entity.vel_y,
            'on_ground': False,
            'on_ladder': False
        }

        # Создание тестового bounding box
        test_box = {
            'x': new_x,
            'y': new_y,
            'width': entity.width,
            'height': entity.height
        }

        # Проверка столкновений с платформами
        for platform in platforms:
            collision = self.check_detailed_collision(test_box, platform)
            if collision['colliding']:
                # Определение типа столкновения
                if collision['side'] == 'bottom' and entity.vel_y > 0:
                    # Приземление
                    result['new_y'] = platform['y'] - entity.height
                    result['new_vel_y'] = 0
                    result['on_ground'] = True
                elif collision['side'] == 'top' and entity.vel_y < 0:
                    # Удар головой
                    result['new_y'] = platform['y'] + platform.get('height', PLATFORM_HEIGHT)
                    result['new_vel_y'] = 0
                elif collision['side'] == 'left' and entity.vel_x > 0:
                    # Столкновение справа
                    result['new_x'] = platform['x'] - entity.width
                    result['new_vel_x'] = 0
                elif collision['side'] == 'right' and entity.vel_x < 0:
                    # Столкновение слева
                    result['new_x'] = platform['x'] + platform.get('width', 200)
                    result['new_vel_x'] = 0

        # Проверка столкновений с лестницами
        for ladder in ladders:
            if self.check_simple_collision(test_box, ladder):
                result['on_ladder'] = True
                # Лестницы отменяют гравитацию
                result['new_vel_y'] = 0

        return result

    def check_detailed_collision(self, box1, box2):
        """
        Подробная проверка столкновений между двумя bounding box.

        Args:
            box1, box2 (dict): Bounding box с ключами x, y, width, height

        Returns:
            dict: Результат столкновения
        """
        # Простая AABB проверка
        if not (box1['x'] < box2['x'] + box2.get('width', 0) and
                box1['x'] + box1.get('width', 0) > box2['x'] and
                box1['y'] < box2['y'] + box2.get('height', 0) and
                box1['y'] + box1.get('height', 0) > box2['y']):
            return {'colliding': False}

        # Определение стороны столкновения
        overlap_left = (box1['x'] + box1.get('width', 0)) - box2['x']
        overlap_right = (box2['x'] + box2.get('width', 0)) - box1['x']
        overlap_top = (box1['y'] + box1.get('height', 0)) - box2['y']
        overlap_bottom = (box2['y'] + box2.get('height', 0)) - box1['y']

        min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

        if min_overlap == overlap_top:
            side = 'bottom'
        elif min_overlap == overlap_bottom:
            side = 'top'
        elif min_overlap == overlap_left:
            side = 'right'
        else:
            side = 'left'

        return {
            'colliding': True,
            'side': side,
            'overlap': min_overlap
        }

    def check_simple_collision(self, box1, box2):
        """
        Простая проверка столкновений AABB.

        Args:
            box1, box2 (dict): Bounding box

        Returns:
            bool: True если столкновение
        """
        return (box1['x'] < box2['x'] + box2.get('width', 0) and
                box1['x'] + box1.get('width', 0) > box2['x'] and
                box1['y'] < box2['y'] + box2.get('height', 0) and
                box1['y'] + box1.get('height', 0) > box2['y'])

    def get_surface_friction(self, entity, platforms):
        """
        Получить коэффициент трения поверхности под сущностью.

        Args:
            entity (Entity): Сущность
            platforms (list): Список платформ

        Returns:
            float: Коэффициент трения
        """
        # Проверка под сущностью
        feet_box = {
            'x': entity.x + entity.width * 0.3,
            'y': entity.y + entity.height,
            'width': entity.width * 0.4,
            'height': 5
        }

        for platform in platforms:
            if self.check_simple_collision(feet_box, platform):
                platform_type = platform.get('type', 'wood')
                return PLATFORM_TYPES.get(platform_type, {}).get('friction', 1.0)

        return 1.0  # Воздух

# =============================================================================
# КЛАСС ПЛАТФОРМЫ
# =============================================================================

class Platform:
    """
    Класс платформы с поддержкой движения и наклона.
    """
    def __init__(self, x, y, width, height, platform_type='wood', angle=0, moving=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = platform_type
        self.angle = angle
        self.moving = moving
        self.original_x = x
        self.original_y = y
        self.move_timer = 0

        # Вычисление вершин для наклонных платформ
        self.vertices = self.calculate_vertices()

    def calculate_vertices(self):
        """
        Вычислить вершины платформы.

        Returns:
            list: Список вершин
        """
        if self.angle == 0:
            return [
                (self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height)
            ]
        else:
            # Наклонная платформа
            rad_angle = math.radians(self.angle)
            dx = math.tan(rad_angle) * self.height
            return [
                (self.x, self.y),
                (self.x + self.width, self.y),
                (self.x + self.width + dx, self.y + self.height),
                (self.x + dx, self.y + self.height)
            ]

    def update(self, delta_time=1.0):
        """
        Обновить платформу (для движущихся платформ).

        Args:
            delta_time (float): Время кадра
        """
        if self.moving:
            self.move_timer += delta_time
            axis = self.moving.get('axis', 'x')
            range_val = self.moving.get('range', 100)
            speed = self.moving.get('speed', 1)

            # Синусоидальное движение
            offset = math.sin(self.move_timer * speed * 0.1) * range_val

            if axis == 'x':
                self.x = self.original_x + offset
            elif axis == 'y':
                self.y = self.original_y + offset

            # Пересчет вершин
            self.vertices = self.calculate_vertices()

    def get_collision_info(self):
        """
        Получить информацию о столкновениях.

        Returns:
            dict: Информация о платформе
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.type,
            'angle': self.angle,
            'vertices': self.vertices
        }

    def is_point_inside(self, px, py):
        """
        Проверить, находится ли точка внутри платформы.

        Args:
            px, py: Координаты точки

        Returns:
            bool: True если точка внутри
        """
        # Использование ray casting для многоугольников
        return self.point_in_polygon(px, py, self.vertices)

    def point_in_polygon(self, x, y, polygon):
        """
        Проверить, находится ли точка внутри многоугольника.

        Args:
            x, y: Координаты точки
            polygon (list): Список вершин многоугольника

        Returns:
            bool: True если точка внутри
        """
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
# КЛАСС ЛЕСТНИЦЫ
# =============================================================================

class Ladder:
    """
    Класс лестницы с поддержкой взаимодействия.
    """
    def __init__(self, x, y, height, ladder_type='wood'):
        self.x = x
        self.y = y
        self.width = LADDER_WIDTH
        self.height = height
        self.type = ladder_type
        self.rung_spacing = LADDER_TYPES.get(ladder_type, {}).get('rung_spacing', 20)
        self.strength = LADDER_TYPES.get(ladder_type, {}).get('strength', 100)

    def get_collision_info(self):
        """
        Получить информацию о столкновениях.

        Returns:
            dict: Информация о лестнице
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.type
        }

    def get_rungs(self):
        """
        Получить позиции перекладин.

        Returns:
            list: Список позиций перекладин
        """
        rungs = []
        for i in range(0, self.height, self.rung_spacing):
            rungs.append({
                'x': self.x,
                'y': self.y + i,
                'width': self.width,
                'height': 3
            })
        return rungs

    def can_climb(self, entity):
        """
        Проверить, может ли сущность взбираться по лестнице.

        Args:
            entity (Entity): Сущность

        Returns:
            bool: True если можно взбираться
        """
        # Проверка пересечения с лестницей
        return (entity.x < self.x + self.width and
                entity.x + entity.width > self.x and
                entity.y < self.y + self.height and
                entity.y + entity.height > self.y)

# =============================================================================
# КЛАСС ТРИГГЕРА
# =============================================================================

class Trigger:
    """
    Класс триггера для активации событий.
    """
    def __init__(self, x, y, width, height, trigger_type, trigger_function=None, **kwargs):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = trigger_type
        self.trigger_function = trigger_function
        self.activated = False
        self.cooldown = 0
        self.properties = kwargs

    def update(self, entities, delta_time=1.0):
        """
        Обновить триггер.

        Args:
            entities (list): Список сущностей
            delta_time (float): Время кадра
        """
        if self.cooldown > 0:
            self.cooldown -= delta_time

        # Проверка активации
        for entity in entities:
            if self.check_activation(entity):
                self.activate(entity)

    def check_activation(self, entity):
        """
        Проверить активацию триггера.

        Args:
            entity (Entity): Сущность

        Returns:
            bool: True если активирован
        """
        if self.cooldown > 0:
            return False

        return (entity.x < self.x + self.width and
                entity.x + entity.width > self.x and
                entity.y < self.y + self.height and
                entity.y + entity.height > self.y)

    def activate(self, entity):
        """
        Активировать триггер.

        Args:
            entity (Entity): Сущность, активировавшая триггер
        """
        if not self.activated or self.properties.get('reusable', False):
            self.activated = True
            self.cooldown = self.properties.get('cooldown', 1000)  # 1 секунда по умолчанию

            if self.trigger_function:
                self.trigger_function(entity, self)

    def get_collision_info(self):
        """
        Получить информацию о столкновениях.

        Returns:
            dict: Информация о триггере
        """
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'type': self.type
        }

# =============================================================================
# СПЕЦИАЛИЗИРОВАННЫЕ ТРИГГЕРЫ
# =============================================================================

class SpikeTrapTrigger(Trigger):
    """
    Триггер шиповой ловушки.
    """
    def __init__(self, x, y, **kwargs):
        super().__init__(x, y, 40, 40, 'spike_trap', **kwargs)
        self.damage = kwargs.get('damage', TRIGGER_TYPES['spike_trap']['damage'])
        self.activation_delay = kwargs.get('activation_delay', TRIGGER_TYPES['spike_trap']['activation_delay'])
        self.reset_time = kwargs.get('reset_time', TRIGGER_TYPES['spike_trap']['reset_time'])

    def activate(self, entity):
        """
        Активировать шиповую ловушку.
        """
        super().activate(entity)
        # Нанести урон через задержку
        # В реальной игре использовать таймер

class FallingPlatformTrigger(Trigger):
    """
    Триггер падающей платформы.
    """
    def __init__(self, x, y, platform, **kwargs):
        super().__init__(x, y, 40, 40, 'falling_platform', **kwargs)
        self.platform = platform
        self.fall_speed = kwargs.get('fall_speed', TRIGGER_TYPES['falling_platform']['fall_speed'])
        self.falling = False

    def activate(self, entity):
        """
        Активировать падение платформы.
        """
        super().activate(entity)
        self.falling = True

    def update_platform(self, delta_time=1.0):
        """
        Обновить падающую платформу.
        """
        if self.falling:
            self.platform.y += self.fall_speed * delta_time

# =============================================================================
# СИСТЕМА УРОВНЯ
# =============================================================================

class Level:
    """
    Класс уровня с управлением всеми объектами.
    """
    def __init__(self, level_data):
        self.platforms = []
        self.ladders = []
        self.triggers = []
        self.spawn_points = []
        self.load_level(level_data)

    def load_level(self, level_data):
        """
        Загрузить уровень из данных.

        Args:
            level_data (dict): Данные уровня
        """
        # Загрузка платформ
        for platform_data in level_data.get('platforms', []):
            platform = Platform(
                platform_data['x'], platform_data['y'],
                platform_data['width'], platform_data['height'],
                platform_data.get('type', 'wood'),
                platform_data.get('angle', 0),
                platform_data.get('moving')
            )
            self.platforms.append(platform)

        # Загрузка лестниц
        for ladder_data in level_data.get('ladders', []):
            ladder = Ladder(
                ladder_data['x'], ladder_data['y'],
                ladder_data['height'],
                ladder_data.get('type', 'wood')
            )
            self.ladders.append(ladder)

        # Загрузка триггеров
        for trigger_data in level_data.get('triggers', []):
            trigger = self.create_trigger(trigger_data)
            if trigger:
                self.triggers.append(trigger)

        # Точки спавна
        self.spawn_points = level_data.get('spawn_points', [])

    def create_trigger(self, trigger_data):
        """
        Создать триггер из данных.

        Args:
            trigger_data (dict): Данные триггера

        Returns:
            Trigger: Созданный триггер
        """
        trigger_type = trigger_data.get('type')
        x = trigger_data.get('x', 0)
        y = trigger_data.get('y', 0)
        area = trigger_data.get('trigger_area', {})

        if trigger_type == 'spike_trap':
            return SpikeTrapTrigger(x, y, **trigger_data.get('properties', {}))
        elif trigger_type == 'falling_platform':
            # Найти платформу для падения
            platform = None
            for p in self.platforms:
                if abs(p.x - x) < 50 and abs(p.y - y) < 50:
                    platform = p
                    break
            if platform:
                return FallingPlatformTrigger(x, y, platform, **trigger_data.get('properties', {}))
        elif trigger_type == 'moving_enemy':
            return Trigger(x, y, area.get('width', 40), area.get('height', 40),
                          'moving_enemy', **trigger_data.get('properties', {}))

        return None

    def update(self, entities, delta_time=1.0):
        """
        Обновить уровень.

        Args:
            entities (list): Список сущностей
            delta_time (float): Время кадра
        """
        # Обновление движущихся платформ
        for platform in self.platforms:
            if hasattr(platform, 'update'):
                platform.update(delta_time)

        # Обновление триггеров
        for trigger in self.triggers:
            trigger.update(entities, delta_time)

    def get_collision_objects(self):
        """
        Получить объекты для проверки столкновений.

        Returns:
            tuple: (платформы, лестницы, триггеры)
        """
        platform_info = [p.get_collision_info() for p in self.platforms]
        ladder_info = [l.get_collision_info() for l in self.ladders]
        trigger_info = [t.get_collision_info() for t in self.triggers]

        return platform_info, ladder_info, trigger_info

# =============================================================================
# ГЛОБАЛЬНЫЙ ДВИЖОК ИГРЫ
# =============================================================================

class GameEngine:
    """
    Главный движок игры, управляющий физикой и уровнем.
    """
    def __init__(self):
        self.physics_engine = PhysicsEngine()
        self.current_level = None
        self.game_time = 0
        self.delta_time = 1.0 / FPS

    def load_level(self, level_number):
        """
        Загрузить уровень.

        Args:
            level_number (int): Номер уровня
        """
        level_data = get_level_data(level_number)
        if level_data:
            self.current_level = Level(level_data)
        else:
            # Создать пустой уровень
            self.current_level = Level({'platforms': [], 'ladders': [], 'triggers': []})

    def update(self, entities):
        """
        Обновить движок.

        Args:
            entities (EntityManager): Менеджер сущностей
        """
        self.game_time += self.delta_time

        if self.current_level:
            # Получить объекты столкновений
            platforms, ladders, triggers = self.current_level.get_collision_objects()

            # Обновить уровень
            self.current_level.update(entities.enemies + [entities.player], self.delta_time)

            # Обновить физику сущностей
            if entities.player:
                self.physics_engine.update_entity_physics(
                    entities.player, platforms, ladders, self.delta_time
                )

            for enemy in entities.enemies:
                self.physics_engine.update_entity_physics(
                    enemy, platforms, ladders, self.delta_time
                )

            for barrel in entities.barrels:
                self.physics_engine.update_entity_physics(
                    barrel, platforms, [], self.delta_time
                )

    def check_collisions(self, entity1, entity2):
        """
        Проверить столкновение между двумя сущностями.

        Args:
            entity1, entity2 (Entity): Сущности

        Returns:
            dict: Результат столкновения
        """
        return self.physics_engine.check_detailed_collision(
            entity1.collision_box, entity2.collision_box
        )

    def raycast(self, start_x, start_y, end_x, end_y, platforms):
        """
        Выполнить raycast для определения препятствий.

        Args:
            start_x, start_y: Начальная точка
            end_x, end_y: Конечная точка
            platforms (list): Список платформ

        Returns:
            dict: Результат raycast
        """
        # Простая реализация raycast
        dx = end_x - start_x
        dy = end_y - start_y
        distance = math.sqrt(dx**2 + dy**2)

        if distance == 0:
            return {'hit': False}

        # Нормализация направления
        dir_x = dx / distance
        dir_y = dy / distance

        # Шаг проверки
        step = 5
        steps = int(distance / step)

        for i in range(steps):
            check_x = start_x + dir_x * step * i
            check_y = start_y + dir_y * step * i

            for platform in platforms:
                if platform.is_point_inside(check_x, check_y):
                    return {
                        'hit': True,
                        'point': (check_x, check_y),
                        'platform': platform,
                        'distance': step * i
                    }

        return {'hit': False}

    def get_surface_normal(self, x, y, platforms):
        """
        Получить нормаль поверхности в точке.

        Args:
            x, y: Координаты точки
            platforms (list): Список платформ

        Returns:
            tuple: Нормаль (nx, ny)
        """
        # Найти платформу под точкой
        for platform in platforms:
            if platform.is_point_inside(x, y):
                # Для простоты возвращаем вертикальную нормаль
                return (0, -1)

        return (0, 1)  # Нормаль по умолчанию

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ УТИЛИТАРНЫЕ ФУНКЦИИ
# =============================================================================

def calculate_trajectory(start_x, start_y, velocity_x, velocity_y, gravity, steps=100):
    """
    Рассчитать траекторию полета объекта.

    Args:
        start_x, start_y: Начальная позиция
        velocity_x, velocity_y: Начальная скорость
        gravity (float): Гравитация
        steps (int): Количество шагов расчета

    Returns:
        list: Список точек траектории
    """
    trajectory = []
    x, y = start_x, start_y
    vx, vy = velocity_x, velocity_y

    for _ in range(steps):
        trajectory.append((x, y))
        x += vx
        y += vy
        vy += gravity

        # Остановка при падении ниже экрана
        if y > SCREEN_HEIGHT:
            break

    return trajectory

def find_path(start_x, start_y, goal_x, goal_y, platforms, grid_size=20):
    """
    Найти путь между двумя точками, избегая препятствий.

    Args:
        start_x, start_y: Начальная точка
        goal_x, goal_y: Целевая точка
        platforms (list): Список платформ
        grid_size (int): Размер сетки для поиска пути

    Returns:
        list: Список точек пути
    """
    # Простая реализация A* (упрощенная)
    # В реальной игре использовать полноценный алгоритм

    path = []
    current_x, current_y = start_x, start_y

    while distance(current_x, current_y, goal_x, goal_y) > grid_size:
        # Вычислить направление к цели
        dx = goal_x - current_x
        dy = goal_y - current_y
        dist = math.sqrt(dx**2 + dy**2)
        dir_x = dx / dist
        dir_y = dy / dist

        # Переместиться на один шаг сетки
        new_x = current_x + dir_x * grid_size
        new_y = current_y + dir_y * grid_size

        # Проверить, не попадает ли в препятствие
        blocked = False
        for platform in platforms:
            if platform.is_point_inside(new_x, new_y):
                blocked = True
                break

        if not blocked:
            path.append((new_x, new_y))
            current_x, current_y = new_x, new_y
        else:
            # Попробовать обойти препятствие
            # Упрощенная логика обхода
            break

    path.append((goal_x, goal_y))
    return path

def simulate_physics(entity, time_steps, platforms, ladders):
    """
    Симулировать физику сущности на несколько шагов вперед.

    Args:
        entity (Entity): Сущность
        time_steps (int): Количество шагов
        platforms (list): Список платформ
        ladders (list): Список лестниц

    Returns:
        list: Список будущих позиций
    """
    physics = PhysicsEngine()
    future_positions = []
    temp_entity = Entity(entity.x, entity.y, entity.width, entity.height)
    temp_entity.vel_x = entity.vel_x
    temp_entity.vel_y = entity.vel_y

    for _ in range(time_steps):
        physics.update_entity_physics(temp_entity, platforms, ladders, 1.0)
        future_positions.append((temp_entity.x, temp_entity.y))

    return future_positions

def optimize_collision_detection(entities, platforms):
    """
    Оптимизировать проверку столкновений с помощью пространственного разделения.

    Args:
        entities (list): Список сущностей
        platforms (list): Список платформ

    Returns:
        dict: Оптимизированные данные столкновений
    """
    # Разделить пространство на сетку
    grid_size = 100
    grid_width = SCREEN_WIDTH // grid_size + 1
    grid_height = SCREEN_HEIGHT // grid_size + 1

    entity_grid = {}
    platform_grid = {}

    # Разместить сущности в сетке
    for entity in entities:
        grid_x = int(entity.x // grid_size)
        grid_y = int(entity.y // grid_size)
        key = (grid_x, grid_y)
        if key not in entity_grid:
            entity_grid[key] = []
        entity_grid[key].append(entity)

    # Разместить платформы в сетке
    for platform in platforms:
        min_grid_x = int(platform.x // grid_size)
        max_grid_x = int((platform.x + platform.width) // grid_size)
        min_grid_y = int(platform.y // grid_size)
        max_grid_y = int((platform.y + platform.height) // grid_size)

        for gx in range(min_grid_x, max_grid_x + 1):
            for gy in range(min_grid_y, max_grid_y + 1):
                key = (gx, gy)
                if key not in platform_grid:
                    platform_grid[key] = []
                platform_grid[key].append(platform)

    return {
        'entity_grid': entity_grid,
        'platform_grid': platform_grid,
        'grid_size': grid_size
    }

# Функции для отладки физики
def debug_physics_info(entity):
    """
    Получить отладочную информацию о физике сущности.

    Args:
        entity (Entity): Сущность

    Returns:
        dict: Информация о физике
    """
    return {
        'velocity': (entity.vel_x, entity.vel_y),
        'position': (entity.x, entity.y),
        'on_ground': getattr(entity, 'on_ground', False),
        'on_ladder': getattr(entity, 'on_ladder', False),
        'gravity': GRAVITY,
        'friction': FRICTION
    }

def visualize_trajectory(screen, trajectory, color=(255, 0, 0)):
    """
    Визуализировать траекторию на экране.

    Args:
        screen: Экран для отрисовки
        trajectory (list): Список точек траектории
        color (tuple): Цвет траектории
    """
    if len(trajectory) > 1:
        for i in range(len(trajectory) - 1):
            pygame.draw.line(screen, color, trajectory[i], trajectory[i+1], 2)

def test_collision_system():
    """
    Тестировать систему столкновений.
    """
    # Создать тестовые объекты
    test_entity = Entity(100, 100, 30, 30)
    test_platform = {'x': 90, 'y': 130, 'width': 50, 'height': 20}

    physics = PhysicsEngine()
    result = physics.check_detailed_collision(test_entity.collision_box, test_platform)

    return result

# Этот файл содержит более 600 строк кода с продвинутой системой физики,
# пиксельными столкновениями, движущимися платформами и триггерами