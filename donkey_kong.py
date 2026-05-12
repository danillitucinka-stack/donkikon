import pygame
import sys
import math

# Инициализация Pygame
pygame.init()

# Константы
WIDTH, HEIGHT = 800, 600
FPS = 60
GRAVITY = 0.5
JUMP_STRENGTH = -10
PLAYER_SPEED = 5
BARREL_SPEED = 3

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BROWN = (139, 69, 19)
WOOD = (160, 82, 45)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Настройка окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Donkey Kong: Pavlograd Edition")
clock = pygame.time.Clock()

# Класс игрока
class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.on_ladder = False
        self.facing_right = True

    def update(self, platforms, ladders):
        # Гравитация
        if not self.on_ground and not self.on_ladder:
            self.vel_y += GRAVITY
        else:
            self.vel_y = 0

        # Движение по горизонтали
        self.x += self.vel_x

        # Проверка столкновений с платформами по горизонтали
        for platform in platforms:
            if self.collide_platform(platform):
                if self.vel_x > 0:  # Движение вправо
                    self.x = platform.x - self.width
                elif self.vel_x < 0:  # Движение влево
                    self.x = platform.x + platform.width

        # Движение по вертикали
        self.y += self.vel_y

        # Проверка столкновений с платформами по вертикали
        self.on_ground = False
        for platform in platforms:
            if self.collide_platform(platform):
                if self.vel_y > 0:  # Падение
                    self.y = platform.y - self.height
                    self.on_ground = True
                elif self.vel_y < 0:  # Прыжок вверх
                    self.y = platform.y + platform.height
                    self.vel_y = 0

        # Проверка лестниц
        self.on_ladder = False
        for ladder in ladders:
            if self.collide_ladder(ladder):
                self.on_ladder = True
                if pygame.key.get_pressed()[pygame.K_UP]:
                    self.vel_y = -PLAYER_SPEED
                elif pygame.key.get_pressed()[pygame.K_DOWN]:
                    self.vel_y = PLAYER_SPEED
                else:
                    self.vel_y = 0

    def collide_platform(self, platform):
        return (self.x < platform.x + platform.width and
                self.x + self.width > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.height > platform.y)

    def collide_ladder(self, ladder):
        return (self.x < ladder.x + ladder.width and
                self.x + self.width > ladder.x and
                self.y < ladder.y + ladder.height and
                self.y + self.height > ladder.y)

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH

    def draw(self, screen):
        draw_player(screen, self.x, self.y, self.facing_right)

# Класс платформы
class Platform:
    def __init__(self, x, y, width, height, angle=0):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.angle = angle  # Угол наклона в градусах

    def draw(self, screen):
        draw_platform(screen, self.x, self.y, self.width, self.height, self.angle)

# Класс лестницы
class Ladder:
    def __init__(self, x, y, height):
        self.x = x
        self.y = y
        self.width = 20
        self.height = height

    def draw(self, screen):
        draw_ladder(screen, self.x, self.y, self.width, self.height)

# Класс врага
class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40

    def draw(self, screen):
        draw_enemy(screen, self.x, self.y)

    def throw_barrel(self):
        # Создать бочку и добавить в список
        pass  # Реализуем позже

# Класс бочки
class Barrel:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 15
        self.vel_x = BARREL_SPEED
        self.vel_y = 0

    def update(self, platforms):
        # Катиться вниз по платформам
        self.x += self.vel_x
        self.y += self.vel_y

        # Простая гравитация для бочки
        self.vel_y += GRAVITY

        # Столкновения с платформами
        for platform in platforms:
            if (self.x < platform.x + platform.width and
                self.x + self.radius * 2 > platform.x and
                self.y < platform.y + platform.height and
                self.y + self.radius * 2 > platform.y):
                # Если бочка касается платформы снизу
                if self.vel_y > 0:
                    self.y = platform.y - self.radius * 2
                    self.vel_y = 0
                    # Катиться вдоль платформы
                    self.vel_x = BARREL_SPEED if self.vel_x > 0 else -BARREL_SPEED

    def draw(self, screen):
        draw_barrel(screen, self.x, self.y, self.radius)

# Функции рисования
def draw_player(screen, x, y, facing_right):
    # Тело птицы - эллипс
    pygame.draw.ellipse(screen, BLUE, (x, y + 10, 20, 15))
    # Голова - круг
    pygame.draw.circle(screen, WHITE, (x + 15, y + 5), 10)
    # Глаза - маленькие круги
    pygame.draw.circle(screen, BLACK, (x + 18, y + 3), 2)
    # Клюв - треугольник
    if facing_right:
        pygame.draw.polygon(screen, RED, [(x + 25, y + 5), (x + 30, y + 3), (x + 30, y + 7)])
    else:
        pygame.draw.polygon(screen, RED, [(x - 5, y + 5), (x, y + 3), (x, y + 7)])
    # Крылья - маленькие эллипсы
    pygame.draw.ellipse(screen, BLUE, (x + 5, y + 12, 10, 8))

def draw_platform(screen, x, y, width, height, angle):
    # Деревянная балка - прямоугольник с текстурой
    pygame.draw.rect(screen, WOOD, (x, y, width, height))
    # Добавим линии для текстуры дерева
    for i in range(0, width, 20):
        pygame.draw.line(screen, BROWN, (x + i, y), (x + i, y + height), 2)
    # Если угол, то наклонная платформа (упрощенная версия)
    if angle != 0:
        # Для наклона используем многоугольник
        rad_angle = math.radians(angle)
        dx = math.tan(rad_angle) * height
        points = [(x, y), (x + width, y), (x + width + dx, y + height), (x + dx, y + height)]
        pygame.draw.polygon(screen, WOOD, points)
        # Линии текстуры
        for i in range(0, width, 20):
            start_x = x + i
            end_x = start_x + dx
            pygame.draw.line(screen, BROWN, (start_x, y), (end_x, y + height), 2)

def draw_ladder(screen, x, y, width, height):
    # Лестница - вертикальные линии и перекладины
    pygame.draw.line(screen, WOOD, (x + 5, y), (x + 5, y + height), 3)
    pygame.draw.line(screen, WOOD, (x + width - 5, y), (x + width - 5, y + height), 3)
    for i in range(0, height, 20):
        pygame.draw.line(screen, WOOD, (x, y + i), (x + width, y + i), 3)

def draw_enemy(screen, x, y):
    # Обезьяна - тело, голова, руки
    pygame.draw.circle(screen, BROWN, (x + 20, y + 10), 15)  # Голова
    pygame.draw.ellipse(screen, BROWN, (x + 5, y + 20, 30, 20))  # Тело
    pygame.draw.line(screen, BROWN, (x + 10, y + 30), (x + 5, y + 40), 3)  # Рука левая
    pygame.draw.line(screen, BROWN, (x + 30, y + 30), (x + 35, y + 40), 3)  # Рука правая
    pygame.draw.circle(screen, BLACK, (x + 18, y + 8), 2)  # Глаз левый
    pygame.draw.circle(screen, BLACK, (x + 22, y + 8), 2)  # Глаз правый

def draw_barrel(screen, x, y, radius):
    # Бочка - круг с линиями
    pygame.draw.circle(screen, WOOD, (x + radius, y + radius), radius)
    pygame.draw.line(screen, BROWN, (x + radius, y), (x + radius, y + radius * 2), 2)
    pygame.draw.line(screen, BROWN, (x, y + radius), (x + radius * 2, y + radius), 2)

# Создание уровня
def create_level():
    platforms = []
    ladders = []
    # Наклонные платформы
    platforms.append(Platform(100, 500, 200, 20, 15))  # Наклон 15 градусов
    platforms.append(Platform(400, 400, 200, 20, -10))  # Наклон -10 градусов
    platforms.append(Platform(200, 300, 200, 20, 20))
    platforms.append(Platform(500, 200, 200, 20, -15))
    # Лестницы соединяют платформы
    ladders.append(Ladder(300, 480, 100))  # Между первой и второй
    ladders.append(Ladder(600, 380, 100))  # Между второй и третьей
    ladders.append(Ladder(400, 280, 100))  # Между третьей и четвертой
    enemy = Enemy(650, 150)  # Враг наверху
    return platforms, ladders, enemy

# Основная функция игры
def main():
    player = Player(50, 550)
    platforms, ladders, enemy = create_level()
    barrels = []

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(BLACK)

        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.jump()

        # Управление игроком
        keys = pygame.key.get_pressed()
        player.vel_x = 0
        if keys[pygame.K_LEFT]:
            player.vel_x = -PLAYER_SPEED
            player.facing_right = False
        if keys[pygame.K_RIGHT]:
            player.vel_x = PLAYER_SPEED
            player.facing_right = True

        # Обновление игрока
        player.update(platforms, ladders)

        # Обновление бочек
        for barrel in barrels[:]:
            barrel.update(platforms)
            # Проверка столкновения с игроком
            if (barrel.x < player.x + player.width and
                barrel.x + barrel.radius * 2 > player.x and
                barrel.y < player.y + player.height and
                barrel.y + barrel.radius * 2 > player.y):
                print("Игра окончена! Вы столкнулись с бочкой.")
                running = False
            # Удалить бочки, вышедшие за экран
            if barrel.y > HEIGHT:
                barrels.remove(barrel)

        # Периодически враг бросает бочку
        if pygame.time.get_ticks() % 3000 < 50:  # Каждые 3 секунды
            barrels.append(Barrel(enemy.x, enemy.y + enemy.height))

        # Рисование
        for platform in platforms:
            platform.draw(screen)
        for ladder in ladders:
            ladder.draw(screen)
        enemy.draw(screen)
        for barrel in barrels:
            barrel.draw(screen)
        player.draw(screen)

        # Проверка победы (достижение верха)
        if player.y < 100:
            print("Поздравляем! Вы выиграли!")
            running = False

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()