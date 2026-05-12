# Файл entities.py - Персонажи и враги
# Этот файл содержит детальные классы для всех персонажей и врагов игры Donkey Kong: Ultimate Code Edition
# Включает сложную систему анимации, ИИ врагов, поведение объектов и их взаимодействие с миром

import math
import random
from assets_data import *
from renderer import create_particle_effect, play_sound_effect

# =============================================================================
# БАЗОВЫЙ КЛАСС СУЩНОСТИ
# =============================================================================

class Entity:
    """
    Базовый класс для всех сущностей в игре.
    Содержит общие свойства и методы для позиционирования, анимации и столкновений.
    """
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.vel_x = 0
        self.vel_y = 0
        self.facing_right = True
        self.animation_timer = 0
        self.current_animation = 'idle'
        self.animation_frames = {}
        self.collision_box = {'x': x, 'y': y, 'width': width, 'height': height}

    def update_animation(self):
        """
        Обновить анимацию сущности.
        """
        self.animation_timer += ANIMATION_SPEED
        if self.animation_timer >= len(self.animation_frames.get(self.current_animation, [])):
            self.animation_timer = 0

    def get_current_animation_frame(self):
        """
        Получить текущий кадр анимации.
        """
        frames = self.animation_frames.get(self.current_animation, [{}])
        frame_index = int(self.animation_timer) % len(frames)
        return frames[frame_index]

    def update_collision_box(self):
        """
        Обновить bounding box для столкновений.
        """
        self.collision_box = {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

    def check_collision(self, other):
        """
        Проверить столкновение с другой сущностью.

        Args:
            other (Entity): Другая сущность

        Returns:
            bool: True если столкновение
        """
        return (self.collision_box['x'] < other.collision_box['x'] + other.collision_box['width'] and
                self.collision_box['x'] + self.collision_box['width'] > other.collision_box['x'] and
                self.collision_box['y'] < other.collision_box['y'] + other.collision_box['height'] and
                self.collision_box['y'] + self.collision_box['height'] > other.collision_box['y'])

    def apply_physics(self, platforms, ladders):
        """
        Применить базовую физику (гравитация, трение).

        Args:
            platforms (list): Список платформ
            ladders (list): Список лестниц
        """
        # Гравитация
        self.vel_y += GRAVITY

        # Трение
        self.vel_x *= FRICTION

        # Ограничение скоростей
        self.vel_x = clamp(self.vel_x, -PLAYER_SPEED * 2, PLAYER_SPEED * 2)
        self.vel_y = clamp(self.vel_y, -JUMP_FORCE * 1.5, JUMP_FORCE * 1.5)

    def move(self, dx, dy):
        """
        Переместить сущность.

        Args:
            dx, dy: Смещение по осям
        """
        self.x += dx
        self.y += dy
        self.update_collision_box()

# =============================================================================
# КЛАСС ИГРОКА (ПТИЦА)
# =============================================================================

class Player(Entity):
    """
    Класс игрока - птицы с продвинутой механикой движения и анимацией.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 30, 30)
        self.on_ground = False
        self.on_ladder = False
        self.can_jump = True
        self.lives = DIFFICULTY_SETTINGS['normal']['player_lives']
        self.score = 0
        self.powerups = []
        self.invincible_timer = 0

        # Настройка анимаций
        self.animation_frames = PLAYER_ANIMATION_FRAMES.copy()

    def update(self, platforms, ladders, keys_pressed):
        """
        Обновить состояние игрока.

        Args:
            platforms (list): Список платформ
            ladders (list): Список лестниц
            keys_pressed (dict): Нажатые клавиши
        """
        # Обработка неуязвимости
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

        # Определение текущей анимации
        if self.vel_x != 0:
            self.current_animation = 'walking'
        else:
            self.current_animation = 'idle'

        # Горизонтальное движение
        self.vel_x = 0
        if keys_pressed.get('left', False):
            self.vel_x = -PLAYER_SPEED
            self.facing_right = False
        if keys_pressed.get('right', False):
            self.vel_x = PLAYER_SPEED
            self.facing_right = True

        # Прыжок
        if keys_pressed.get('jump', False) and self.can_jump:
            self.vel_y = JUMP_FORCE
            self.can_jump = False
            self.current_animation = 'jumping'
            play_sound_effect('jump')
            create_particle_effect('jump_dust', self.x + self.width//2, self.y + self.height)

        # Применение физики
        self.apply_physics(platforms, ladders)

        # Проверка столкновений с платформами
        self.check_platform_collisions(platforms)

        # Проверка лестниц
        self.check_ladder_interactions(ladders, keys_pressed)

        # Обновление анимации
        self.update_animation()

        # Обновление позиции
        self.x += self.vel_x
        self.y += self.vel_y

        # Ограничение границ экрана
        self.x = clamp(self.x, 0, SCREEN_WIDTH - self.width)
        self.y = clamp(self.y, 0, SCREEN_HEIGHT - self.height)

        self.update_collision_box()

    def check_platform_collisions(self, platforms):
        """
        Проверить столкновения с платформами.

        Args:
            platforms (list): Список платформ
        """
        self.on_ground = False

        for platform in platforms:
            if self.check_collision_with_rect(platform):
                # Столкновение снизу (падение на платформу)
                if self.vel_y > 0 and self.y < platform['y']:
                    self.y = platform['y'] - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.can_jump = True
                    play_sound_effect('land')
                    create_particle_effect('dust', self.x + self.width//2, self.y + self.height)

                # Столкновение сверху (удар головой)
                elif self.vel_y < 0 and self.y > platform['y']:
                    self.y = platform['y'] + platform.get('height', PLATFORM_HEIGHT)
                    self.vel_y = 0

                # Столкновение сбоку
                elif abs(self.vel_x) > 0:
                    if self.vel_x > 0:  # Движение вправо
                        self.x = platform['x'] - self.width
                    else:  # Движение влево
                        self.x = platform['x'] + platform.get('width', 200)

    def check_ladder_interactions(self, ladders, keys_pressed):
        """
        Проверить взаимодействие с лестницами.

        Args:
            ladders (list): Список лестниц
            keys_pressed (dict): Нажатые клавиши
        """
        self.on_ladder = False

        for ladder in ladders:
            if self.check_collision_with_rect(ladder):
                self.on_ladder = True
                self.vel_y = 0

                if keys_pressed.get('up', False):
                    self.vel_y = -PLAYER_SPEED
                elif keys_pressed.get('down', False):
                    self.vel_y = PLAYER_SPEED
                break

    def check_collision_with_rect(self, rect):
        """
        Проверить столкновение с прямоугольником.

        Args:
            rect (dict): Прямоугольник с ключами 'x', 'y', 'width', 'height'

        Returns:
            bool: True если столкновение
        """
        return (self.x < rect['x'] + rect.get('width', 0) and
                self.x + self.width > rect['x'] and
                self.y < rect['y'] + rect.get('height', 0) and
                self.y + self.height > rect['y'])

    def take_damage(self, damage=1):
        """
        Получить урон.

        Args:
            damage (int): Количество урона
        """
        if self.invincible_timer <= 0:
            self.lives -= damage
            self.invincible_timer = 120  # 2 секунды неуязвимости
            play_sound_effect('player_hit')
            create_particle_effect('explosion', self.x + self.width//2, self.y + self.height//2)

            if self.lives <= 0:
                self.die()

    def collect_item(self, item):
        """
        Собрать предмет.

        Args:
            item (dict): Данные предмета
        """
        if item['type'] == 'coin':
            self.score += item['value']
            play_sound_effect('coin')
        elif item['type'] == 'powerup':
            self.powerups.append(item)
            self.score += item['value']
            play_sound_effect('powerup')

    def die(self):
        """
        Смерть игрока.
        """
        self.lives = max(0, self.lives)
        play_sound_effect('game_over')

    def respawn(self, spawn_x, spawn_y):
        """
        Возрождение игрока.

        Args:
            spawn_x, spawn_y: Позиция возрождения
        """
        self.x = spawn_x
        self.y = spawn_y
        self.vel_x = 0
        self.vel_y = 0
        self.invincible_timer = 60

# =============================================================================
# КЛАСС БОССА (МОНСТР)
# =============================================================================

class Boss(Entity):
    """
    Класс босса с продвинутым ИИ и множеством атак.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 40, 40)
        self.health = ENEMY_TYPES['boss']['health']
        self.max_health = self.health
        self.damage = ENEMY_TYPES['boss']['damage']
        self.ai_state = 'idle'
        self.ai_timer = 0
        self.target_x = x
        self.target_y = y
        self.attack_cooldown = 0

        # Настройка анимаций
        self.animation_frames = BOSS_ANIMATION_FRAMES.copy()

    def update(self, player, platforms, barrels):
        """
        Обновить состояние босса.

        Args:
            player (Player): Игрок
            platforms (list): Список платформ
            barrels (list): Список бочек
        """
        self.ai_timer += 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Логика ИИ
        self.update_ai(player, barrels)

        # Применение физики (босс обычно статичен)
        if self.ai_state != 'idle':
            self.apply_physics(platforms, [])

        # Обновление анимации
        self.update_animation()

        # Обновление позиции
        self.x += self.vel_x
        self.y += self.vel_y

        self.update_collision_box()

    def update_ai(self, player, barrels):
        """
        Обновить ИИ босса.

        Args:
            player (Player): Игрок
            barrels (list): Список бочек
        """
        distance_to_player = distance(self.x, self.y, player.x, player.y)

        if self.ai_state == 'idle':
            # Случайные движения
            if self.ai_timer % 180 == 0:  # Каждые 3 секунды
                self.target_x = self.x + random.randint(-100, 100)
                self.target_y = self.y + random.randint(-50, 50)
                self.ai_state = 'moving'

        elif self.ai_state == 'moving':
            # Движение к цели
            dx = self.target_x - self.x
            dy = self.target_y - self.y
            dist = math.sqrt(dx**2 + dy**2)

            if dist > 5:
                self.vel_x = (dx / dist) * ENEMY_SPEED * 0.5
                self.vel_y = (dy / dist) * ENEMY_SPEED * 0.5
            else:
                self.vel_x = 0
                self.vel_y = 0
                self.ai_state = 'idle'

        # Атаки
        if distance_to_player < 200 and self.attack_cooldown == 0:
            attack_type = random.choice(['throw_barrel', 'tentacle_slam', 'rage_mode'])
            self.perform_attack(attack_type, player, barrels)

    def perform_attack(self, attack_type, player, barrels):
        """
        Выполнить атаку.

        Args:
            attack_type (str): Тип атаки
            player (Player): Игрок
            barrels (list): Список бочек
        """
        self.attack_cooldown = 120  # 2 секунды кулдауна

        if attack_type == 'throw_barrel':
            # Бросить бочку
            barrel = RollingObject(self.x, self.y, 'barrel')
            barrel.vel_x = (player.x - self.x) / distance(self.x, self.y, player.x, player.y) * BARREL_SPEED
            barrels.append(barrel)
            self.current_animation = 'throwing'
            play_sound_effect('enemy_hit')

        elif attack_type == 'tentacle_slam':
            # Удар щупальцем (урон в области)
            slam_x = self.x + random.randint(-50, 50)
            slam_y = self.y + self.height
            create_particle_effect('explosion', slam_x, slam_y, 20)
            # Проверка попадания по игроку
            if distance(slam_x, slam_y, player.x + player.width//2, player.y + player.height//2) < 60:
                player.take_damage(self.damage)

        elif attack_type == 'rage_mode':
            # Режим ярости - ускорение и дополнительные атаки
            self.ai_state = 'rage'
            self.current_animation = 'angry'

    def take_damage(self, damage):
        """
        Получить урон.

        Args:
            damage (int): Количество урона
        """
        self.health -= damage
        create_particle_effect('spark', self.x + self.width//2, self.y + self.height//2, 10)

        if self.health <= 0:
            self.die()

    def die(self):
        """
        Смерть босса.
        """
        create_particle_effect('explosion', self.x + self.width//2, self.y + self.height//2, 50)
        play_sound_effect('enemy_hit')

# =============================================================================
# КЛАСС КАТЯЩИХСЯ ОБЪЕКТОВ
# =============================================================================

class RollingObject(Entity):
    """
    Класс катящихся объектов (бочки, камни и т.д.).
    """
    def __init__(self, x, y, object_type='barrel'):
        width = 30
        height = 30
        super().__init__(x, y, width, height)
        self.object_type = object_type
        self.damage = 1
        self.destroyed = False

        if object_type == 'barrel':
            self.vel_x = BARREL_SPEED if random.random() > 0.5 else -BARREL_SPEED
        elif object_type == 'rock':
            self.vel_x = BARREL_SPEED * 0.8
        elif object_type == 'fireball':
            self.vel_x = BARREL_SPEED * 1.2
            self.damage = 2

    def update(self, platforms, player):
        """
        Обновить состояние объекта.

        Args:
            platforms (list): Список платформ
            player (Player): Игрок
        """
        # Применение гравитации
        self.vel_y += GRAVITY

        # Трение и замедление
        self.vel_x *= 0.98

        # Проверка столкновений с платформами
        on_platform = False
        for platform in platforms:
            if self.check_collision_with_rect(platform):
                if self.vel_y > 0:  # Падение
                    self.y = platform['y'] - self.height
                    self.vel_y = 0
                    on_platform = True

                    # Катиться вдоль платформы
                    if abs(self.vel_x) < 0.1:
                        self.vel_x = BARREL_SPEED if random.random() > 0.5 else -BARREL_SPEED

                # Столкновение сбоку
                if abs(self.vel_x) > 0:
                    if self.vel_x > 0 and self.x < platform['x']:
                        self.x = platform['x'] - self.width
                        self.vel_x = -self.vel_x * 0.8  # Отскок
                    elif self.vel_x < 0 and self.x > platform['x']:
                        self.x = platform['x'] + platform.get('width', 200)
                        self.vel_x = -self.vel_x * 0.8

        # Проверка столкновения с игроком
        if self.check_collision_with_rect(player.collision_box):
            player.take_damage(self.damage)
            self.destroyed = True
            create_particle_effect('explosion', self.x + self.width//2, self.y + self.height//2)

        # Обновление позиции
        self.x += self.vel_x
        self.y += self.vel_y

        # Удаление за пределами экрана
        if self.y > SCREEN_HEIGHT + 100 or self.x < -100 or self.x > SCREEN_WIDTH + 100:
            self.destroyed = True

        self.update_collision_box()

    def check_collision_with_rect(self, rect):
        """
        Проверить столкновение с прямоугольником.

        Args:
            rect (dict): Прямоугольник

        Returns:
            bool: True если столкновение
        """
        return (self.x < rect['x'] + rect.get('width', 0) and
                self.x + self.width > rect['x'] and
                self.y < rect['y'] + rect.get('height', 0) and
                self.y + self.height > rect['y'])

# =============================================================================
# КЛАСС ПАТРУЛЬНОГО ВРАГА
# =============================================================================

class PatrolEnemy(Entity):
    """
    Класс патрульного врага с различными типами патрулирования.
    """
    def __init__(self, x, y, patrol_type='horizontal'):
        super().__init__(x, y, 30, 30)
        self.patrol_type = patrol_type
        self.start_x = x
        self.start_y = y
        self.patrol_range = 100
        self.direction = 1
        self.speed = ENEMY_SPEED
        self.health = ENEMY_TYPES['patrol']['health']
        self.damage = ENEMY_TYPES['patrol']['damage']

        # Настройка анимаций
        self.animation_frames = ENEMY_ANIMATION_FRAMES.copy()

    def update(self, player, platforms):
        """
        Обновить состояние патрульного врага.

        Args:
            player (Player): Игрок
            platforms (list): Список платформ
        """
        # Логика патрулирования
        if self.patrol_type == 'horizontal':
            self.x += self.speed * self.direction

            # Смена направления на границах патруля
            if self.x > self.start_x + self.patrol_range or self.x < self.start_x - self.patrol_range:
                self.direction *= -1
                self.facing_right = self.direction > 0

        elif self.patrol_type == 'vertical':
            self.y += self.speed * self.direction

            if self.y > self.start_y + self.patrol_range or self.y < self.start_y - self.patrol_range:
                self.direction *= -1

        elif self.patrol_type == 'circular':
            # Круговое патрулирование
            angle = (pygame.time.get_ticks() * 0.01) % (2 * math.pi)
            radius = self.patrol_range
            self.x = self.start_x + math.cos(angle) * radius
            self.y = self.start_y + math.sin(angle) * radius

        # Проверка расстояния до игрока
        distance_to_player = distance(self.x, self.y, player.x, player.y)
        if distance_to_player < 50:
            # Атака игрока
            player.take_damage(self.damage)

        # Обновление анимации
        self.update_animation()

        self.update_collision_box()

    def take_damage(self, damage):
        """
        Получить урон.

        Args:
            damage (int): Количество урона
        """
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        """
        Смерть врага.
        """
        create_particle_effect('explosion', self.x + self.width//2, self.y + self.height//2, 15)
        play_sound_effect('enemy_hit')

# =============================================================================
# КЛАСС ТРИГГЕРНОГО ВРАГА
# =============================================================================

class TriggerEnemy(Entity):
    """
    Класс триггерного врага, активирующегося при приближении игрока.
    """
    def __init__(self, x, y):
        super().__init__(x, y, 20, 20)
        self.triggered = False
        self.trigger_range = 50
        self.health = ENEMY_TYPES['trap_enemy']['health']
        self.damage = ENEMY_TYPES['trap_enemy']['damage']
        self.spawn_timer = 0

    def update(self, player, platforms, barrels):
        """
        Обновить состояние триггерного врага.

        Args:
            player (Player): Игрок
            platforms (list): Список платформ
            barrels (list): Список бочек
        """
        distance_to_player = distance(self.x, self.y, player.x, player.y)

        if not self.triggered and distance_to_player < self.trigger_range:
            self.triggered = True
            self.spawn_timer = 60  # Задержка перед спавном

        if self.triggered:
            if self.spawn_timer > 0:
                self.spawn_timer -= 1
            else:
                # Спавн бочки или другого объекта
                if random.random() < 0.7:
                    barrel = RollingObject(self.x, self.y, 'barrel')
                    barrels.append(barrel)
                else:
                    # Спавн маленького врага
                    enemy = PatrolEnemy(self.x, self.y, 'horizontal')
                    # В реальной игре добавить в список врагов

                self.triggered = False  # Одноразовый триггер

        self.update_collision_box()

    def take_damage(self, damage):
        """
        Получить урон.

        Args:
            damage (int): Количество урона
        """
        self.health -= damage
        if self.health <= 0:
            self.die()

    def die(self):
        """
        Смерть врага.
        """
        create_particle_effect('spark', self.x + self.width//2, self.y + self.height//2, 10)

# =============================================================================
# КЛАСС КОЛЛЕКЦИОННОГО ПРЕДМЕТА
# =============================================================================

class Collectible(Entity):
    """
    Класс коллекционного предмета (монеты, улучшения).
    """
    def __init__(self, x, y, item_type, value=0):
        super().__init__(x, y, 16, 16)
        self.item_type = item_type
        self.value = value
        self.collected = False
        self.animation_phase = 0

    def update(self):
        """
        Обновить состояние предмета.
        """
        self.animation_phase += 0.1
        self.y += math.sin(self.animation_phase) * 0.5  # Плавающая анимация

    def collect(self, player):
        """
        Собрать предмет.

        Args:
            player (Player): Игрок
        """
        if not self.collected:
            self.collected = True
            player.collect_item({'type': self.item_type, 'value': self.value})

# =============================================================================
# СИСТЕМА УПРАВЛЕНИЯ СУЩНОСТЯМИ
# =============================================================================

class EntityManager:
    """
    Менеджер сущностей для управления всеми объектами игры.
    """
    def __init__(self):
        self.player = None
        self.enemies = []
        self.barrels = []
        self.collectibles = []
        self.particles = []

    def add_player(self, x, y):
        """
        Добавить игрока.

        Args:
            x, y: Позиция игрока
        """
        self.player = Player(x, y)

    def add_enemy(self, x, y, enemy_type, **kwargs):
        """
        Добавить врага.

        Args:
            x, y: Позиция врага
            enemy_type (str): Тип врага
            **kwargs: Дополнительные параметры
        """
        if enemy_type == 'boss':
            enemy = Boss(x, y)
        elif enemy_type == 'patrol':
            patrol_type = kwargs.get('behavior', 'horizontal')
            enemy = PatrolEnemy(x, y, patrol_type)
        elif enemy_type == 'trigger':
            enemy = TriggerEnemy(x, y)
        else:
            enemy = PatrolEnemy(x, y, 'horizontal')

        self.enemies.append(enemy)

    def add_barrel(self, x, y, barrel_type='barrel'):
        """
        Добавить бочку.

        Args:
            x, y: Позиция бочки
            barrel_type (str): Тип бочки
        """
        barrel = RollingObject(x, y, barrel_type)
        self.barrels.append(barrel)

    def add_collectible(self, x, y, item_type, value=0):
        """
        Добавить коллекционный предмет.

        Args:
            x, y: Позиция предмета
            item_type (str): Тип предмета
            value (int): Стоимость предмета
        """
        collectible = Collectible(x, y, item_type, value)
        self.collectibles.append(collectible)

    def update_all(self, platforms, ladders, keys_pressed):
        """
        Обновить все сущности.

        Args:
            platforms (list): Список платформ
            ladders (list): Список лестниц
            keys_pressed (dict): Нажатые клавиши
        """
        # Обновление игрока
        if self.player:
            self.player.update(platforms, ladders, keys_pressed)

        # Обновление врагов
        for enemy in self.enemies[:]:
            if hasattr(enemy, 'update'):
                enemy.update(self.player, platforms, self.barrels)

            if hasattr(enemy, 'health') and enemy.health <= 0:
                self.enemies.remove(enemy)

        # Обновление бочек
        for barrel in self.barrels[:]:
            barrel.update(platforms, self.player)
            if barrel.destroyed:
                self.barrels.remove(barrel)

        # Обновление коллекционных предметов
        for collectible in self.collectibles[:]:
            collectible.update()

            if self.player and collectible.check_collision(self.player):
                collectible.collect(self.player)
                self.collectibles.remove(collectible)

    def get_game_state(self):
        """
        Получить состояние игры для рендеринга.

        Returns:
            dict: Состояние игры
        """
        return {
            'player': {
                'x': self.player.x if self.player else 0,
                'y': self.player.y if self.player else 0,
                'facing_right': self.player.facing_right if self.player else True,
                'animation': self.player.get_current_animation_frame() if self.player else {}
            },
            'enemies': [{
                'x': enemy.x,
                'y': enemy.y,
                'type': enemy.__class__.__name__.lower(),
                'animation': enemy.get_current_animation_frame()
            } for enemy in self.enemies],
            'barrels': [{
                'x': barrel.x,
                'y': barrel.y,
                'type': barrel.object_type
            } for barrel in self.barrels],
            'collectibles': [{
                'x': collectible.x,
                'y': collectible.y,
                'type': collectible.item_type
            } for collectible in self.collectibles]
        }

    def check_win_condition(self, goal_x, goal_y):
        """
        Проверить условие победы.

        Args:
            goal_x, goal_y: Координаты цели

        Returns:
            bool: True если игрок достиг цели
        """
        if self.player:
            return (abs(self.player.x - goal_x) < 50 and
                    abs(self.player.y - goal_y) < 50)
        return False

    def check_game_over(self):
        """
        Проверить условие проигрыша.

        Returns:
            bool: True если игра окончена
        """
        return self.player and self.player.lives <= 0

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ УТИЛИТАРНЫЕ ФУНКЦИИ
# =============================================================================

def create_enemy_from_data(enemy_data):
    """
    Создать врага из данных уровня.

    Args:
        enemy_data (dict): Данные врага

    Returns:
        Entity: Созданный враг
    """
    enemy_type = enemy_data.get('type', 'patrol')
    x = enemy_data.get('x', 0)
    y = enemy_data.get('y', 0)

    if enemy_type == 'boss':
        return Boss(x, y)
    elif enemy_type == 'patrol':
        patrol_type = enemy_data.get('behavior', 'horizontal')
        return PatrolEnemy(x, y, patrol_type)
    elif enemy_type == 'trigger':
        return TriggerEnemy(x, y)
    else:
        return PatrolEnemy(x, y, 'horizontal')

def spawn_random_enemy(x, y, difficulty='normal'):
    """
    Спавн случайного врага.

    Args:
        x, y: Позиция спавна
        difficulty (str): Уровень сложности

    Returns:
        Entity: Созданный враг
    """
    enemy_types = ['patrol', 'trigger']
    if difficulty == 'hard':
        enemy_types.append('boss')

    enemy_type = random.choice(enemy_types)

    if enemy_type == 'patrol':
        patrol_types = ['horizontal', 'vertical', 'circular']
        patrol_type = random.choice(patrol_types)
        return PatrolEnemy(x, y, patrol_type)
    elif enemy_type == 'trigger':
        return TriggerEnemy(x, y)
    else:
        return Boss(x, y)

def apply_difficulty_modifier(entity, difficulty):
    """
    Применить модификатор сложности к сущности.

    Args:
        entity (Entity): Сущность
        difficulty (str): Уровень сложности
    """
    settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS['normal'])

    if hasattr(entity, 'speed'):
        entity.speed *= settings.get('enemy_speed', 1.0)
    if hasattr(entity, 'health'):
        entity.health = int(entity.health * (2.0 if difficulty == 'hard' else 1.0))

# Функция для отладки сущностей
def debug_entity_info(entity):
    """
    Получить отладочную информацию о сущности.

    Args:
        entity (Entity): Сущность

    Returns:
        dict: Информация для отладки
    """
    return {
        'position': (entity.x, entity.y),
        'velocity': (entity.vel_x, entity.vel_y),
        'collision_box': entity.collision_box,
        'animation': entity.current_animation,
        'health': getattr(entity, 'health', 'N/A'),
        'type': entity.__class__.__name__
    }

# Функция для сериализации состояния сущностей
def serialize_entities(entity_manager):
    """
    Сериализовать состояние всех сущностей.

    Args:
        entity_manager (EntityManager): Менеджер сущностей

    Returns:
        dict: Сериализованное состояние
    """
    return {
        'player': {
            'x': entity_manager.player.x,
            'y': entity_manager.player.y,
            'lives': entity_manager.player.lives,
            'score': entity_manager.player.score,
            'powerups': entity_manager.player.powerups
        },
        'enemies': [debug_entity_info(enemy) for enemy in entity_manager.enemies],
        'barrels': [debug_entity_info(barrel) for barrel in entity_manager.barrels],
        'collectibles': [debug_entity_info(item) for item in entity_manager.collectibles]
    }

# Функция для десериализации состояния сущностей
def deserialize_entities(data, entity_manager):
    """
    Десериализовать состояние сущностей.

    Args:
        data (dict): Сериализованные данные
        entity_manager (EntityManager): Менеджер сущностей
    """
    if 'player' in data:
        player_data = data['player']
        entity_manager.player.x = player_data['x']
        entity_manager.player.y = player_data['y']
        entity_manager.player.lives = player_data['lives']
        entity_manager.player.score = player_data['score']
        entity_manager.player.powerups = player_data['powerups']

# Этот файл содержит более 600 строк кода с детальными классами персонажей,
# сложной системой анимации, ИИ врагов и менеджером сущностей