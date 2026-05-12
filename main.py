# Файл main.py - Ядро и логика игры
# Этот файл содержит главный цикл игры, машину состояний, менеджер уровней и систему коллизий для Donkey Kong: Ultimate Code Edition
# Управляет всем игровым процессом, от меню до финальных титров

import pygame
import sys
from assets_data import *
from renderer import *
from entities import *
from engine import *

# =============================================================================
# МАШИНА СОСТОЯНИЙ ИГРЫ
# =============================================================================

class GameState:
    """
    Перечисление состояний игры.
    """
    MENU = 'menu'
    PLAYING = 'playing'
    PAUSED = 'paused'
    GAME_OVER = 'game_over'
    LEVEL_COMPLETE = 'level_complete'
    SETTINGS = 'settings'
    CREDITS = 'credits'

class GameStateManager:
    """
    Менеджер состояний игры.
    """
    def __init__(self):
        self.current_state = GameState.MENU
        self.previous_state = None
        self.state_timer = 0
        self.transition_duration = 500  # миллисекунды

    def change_state(self, new_state):
        """
        Изменить состояние игры.

        Args:
            new_state (str): Новое состояние
        """
        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            self.state_timer = 0
            print(f"Состояние игры изменено: {self.previous_state} -> {self.current_state}")

    def update(self, delta_time):
        """
        Обновить менеджер состояний.

        Args:
            delta_time (float): Время кадра
        """
        self.state_timer += delta_time * 1000  # в миллисекундах

    def is_transitioning(self):
        """
        Проверить, происходит ли переход между состояниями.

        Returns:
            bool: True если переход
        """
        return self.state_timer < self.transition_duration

    def get_transition_progress(self):
        """
        Получить прогресс перехода.

        Returns:
            float: Прогресс (0.0 - 1.0)
        """
        return min(1.0, self.state_timer / self.transition_duration)

# =============================================================================
# МЕНЮ ИГРЫ
# =============================================================================

class Menu:
    """
    Класс главного меню игры.
    """
    def __init__(self):
        self.buttons = []
        self.selected_button = 0
        self.create_menu_buttons()

    def create_menu_buttons(self):
        """
        Создать кнопки меню.
        """
        button_width = UI_BUTTON_WIDTH
        button_height = UI_BUTTON_HEIGHT
        start_y = SCREEN_HEIGHT // 2 - 100

        self.buttons = [
            {
                'text': UI_TEXTS['start_game'],
                'x': SCREEN_WIDTH // 2 - button_width // 2,
                'y': start_y,
                'width': button_width,
                'height': button_height,
                'action': 'start_game'
            },
            {
                'text': UI_TEXTS['settings'],
                'x': SCREEN_WIDTH // 2 - button_width // 2,
                'y': start_y + 80,
                'width': button_width,
                'height': button_height,
                'action': 'settings'
            },
            {
                'text': UI_TEXTS['exit'],
                'x': SCREEN_WIDTH // 2 - button_width // 2,
                'y': start_y + 160,
                'width': button_width,
                'height': button_height,
                'action': 'exit'
            }
        ]

    def update(self, keys_pressed, mouse_pos, mouse_clicked):
        """
        Обновить меню.

        Args:
            keys_pressed (dict): Нажатые клавиши
            mouse_pos (tuple): Позиция мыши
            mouse_clicked (bool): Клик мыши

        Returns:
            str: Действие для выполнения
        """
        # Обработка клавиш
        if keys_pressed.get('up', False):
            self.selected_button = (self.selected_button - 1) % len(self.buttons)
        elif keys_pressed.get('down', False):
            self.selected_button = (self.selected_button + 1) % len(self.buttons)
        elif keys_pressed.get('enter', False) or keys_pressed.get('jump', False):
            return self.buttons[self.selected_button]['action']

        # Обработка мыши
        for i, button in enumerate(self.buttons):
            button_rect = pygame.Rect(button['x'], button['y'], button['width'], button['height'])
            if button_rect.collidepoint(mouse_pos):
                self.selected_button = i
                if mouse_clicked:
                    return button['action']

        return None

    def render(self, screen):
        """
        Отрисовать меню.

        Args:
            screen: Экран для отрисовки
        """
        # Фон
        screen.fill(BLACK)

        # Заголовок
        draw_text(screen, "Donkey Kong: Ultimate Code Edition",
                 SCREEN_WIDTH // 2, 150, WHITE, 36, center=True)

        # Подзаголовок
        draw_text(screen, "Создано с помощью pygame.draw",
                 SCREEN_WIDTH // 2, 200, GRAY_LIGHT, 18, center=True)

        # Кнопки
        for i, button in enumerate(self.buttons):
            color = UI_BUTTON_HOVER if i == self.selected_button else UI_BUTTON_NORMAL
            draw_button(screen, button['x'], button['y'], button['width'],
                       button['height'], button['text'], color)

        # Подсказки
        draw_text(screen, "Используйте стрелки и Enter, или кликните мышкой",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50, GRAY_MEDIUM, 14, center=True)

# =============================================================================
# МЕНЕДЖЕР УРОВНЕЙ
# =============================================================================

class LevelManager:
    """
    Менеджер уровней игры.
    """
    def __init__(self):
        self.current_level = 1
        self.max_unlocked_level = 1
        self.level_scores = {}
        self.level_times = {}
        self.load_progress()

    def load_progress(self):
        """
        Загрузить прогресс игрока.
        """
        # В реальной игре загрузка из файла
        self.max_unlocked_level = 1
        self.level_scores = {}
        self.level_times = {}

    def save_progress(self):
        """
        Сохранить прогресс игрока.
        """
        # В реальной игре сохранение в файл
        pass

    def can_play_level(self, level_number):
        """
        Проверить, можно ли играть на уровне.

        Args:
            level_number (int): Номер уровня

        Returns:
            bool: True если можно
        """
        return level_number <= self.max_unlocked_level

    def start_level(self, level_number):
        """
        Начать уровень.

        Args:
            level_number (int): Номер уровня

        Returns:
            dict: Данные уровня
        """
        if self.can_play_level(level_number):
            self.current_level = level_number
            level_data = get_level_data(level_number)
            if level_data:
                return level_data
        return None

    def complete_level(self, score, time_taken):
        """
        Завершить уровень.

        Args:
            score (int): Набранные очки
            time_taken (float): Время прохождения
        """
        self.level_scores[self.current_level] = max(
            self.level_scores.get(self.current_level, 0), score
        )
        self.level_times[self.current_level] = min(
            self.level_times.get(self.current_level, float('inf')), time_taken
        )

        # Разблокировать следующий уровень
        if self.current_level >= self.max_unlocked_level:
            self.max_unlocked_level = self.current_level + 1

        self.save_progress()

    def get_level_info(self, level_number):
        """
        Получить информацию об уровне.

        Args:
            level_number (int): Номер уровня

        Returns:
            dict: Информация об уровне
        """
        return {
            'unlocked': self.can_play_level(level_number),
            'best_score': self.level_scores.get(level_number, 0),
            'best_time': self.level_times.get(level_number, 0),
            'completed': level_number in self.level_scores
        }

# =============================================================================
# ОСНОВНОЙ КЛАСС ИГРЫ
# =============================================================================

class DonkeyKongGame:
    """
    Основной класс игры Donkey Kong.
    """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Donkey Kong: Ultimate Code Edition")

        self.clock = pygame.time.Clock()
        self.running = True

        # Компоненты игры
        self.state_manager = GameStateManager()
        self.menu = Menu()
        self.level_manager = LevelManager()
        self.engine = GameEngine()
        self.entity_manager = EntityManager()

        # Игровые переменные
        self.game_score = 0
        self.game_time = 0
        self.level_start_time = 0
        self.difficulty = 'normal'
        self.camera_x = 0
        self.camera_y = 0

        # Настройки управления
        self.keys_pressed = {}
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False

    def run(self):
        """
        Главный цикл игры.
        """
        try:
            while self.running:
                delta_time = self.clock.tick(FPS) / 1000.0  # в секундах

                self.handle_events()
                self.update(delta_time)
                self.render()

                pygame.display.flip()
        except Exception as e:
            print(f"Ошибка в главном цикле: {e}")
            import traceback
            traceback.print_exc()
            input("Нажмите Enter для выхода...")

        self.quit()

    def handle_events(self):
        """
        Обработать события Pygame.
        """
        self.mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self.handle_key_up(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Левая кнопка мыши
                    self.mouse_clicked = True
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def handle_key_down(self, key):
        """
        Обработать нажатие клавиши.

        Args:
            key: Код клавиши
        """
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.keys_pressed['left'] = True
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.keys_pressed['right'] = True
        elif key == pygame.K_UP or key == pygame.K_w:
            self.keys_pressed['up'] = True
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.keys_pressed['down'] = True
        elif key == pygame.K_SPACE:
            self.keys_pressed['jump'] = True
        elif key == pygame.K_RETURN:
            self.keys_pressed['enter'] = True
        elif key == pygame.K_ESCAPE:
            self.keys_pressed['pause'] = True
            if self.state_manager.current_state == GameState.PLAYING:
                self.state_manager.change_state(GameState.PAUSED)
            elif self.state_manager.current_state == GameState.PAUSED:
                self.state_manager.change_state(GameState.PLAYING)

    def handle_key_up(self, key):
        """
        Обработать отпускание клавиши.

        Args:
            key: Код клавиши
        """
        if key == pygame.K_LEFT or key == pygame.K_a:
            self.keys_pressed['left'] = False
        elif key == pygame.K_RIGHT or key == pygame.K_d:
            self.keys_pressed['right'] = False
        elif key == pygame.K_UP or key == pygame.K_w:
            self.keys_pressed['up'] = False
        elif key == pygame.K_DOWN or key == pygame.K_s:
            self.keys_pressed['down'] = False
        elif key == pygame.K_SPACE:
            self.keys_pressed['jump'] = False
        elif key == pygame.K_RETURN:
            self.keys_pressed['enter'] = False

    def update(self, delta_time):
        """
        Обновить игру.

        Args:
            delta_time (float): Время кадра
        """
        try:
            self.state_manager.update(delta_time)

            if self.state_manager.current_state == GameState.MENU:
                self.update_menu()
            elif self.state_manager.current_state == GameState.PLAYING:
                self.update_game(delta_time)
            elif self.state_manager.current_state == GameState.PAUSED:
                self.update_pause()
            elif self.state_manager.current_state == GameState.GAME_OVER:
                self.update_game_over()
            elif self.state_manager.current_state == GameState.LEVEL_COMPLETE:
                self.update_level_complete()
        except Exception as e:
            print(f"Ошибка в обновлении: {e}")
            import traceback
            traceback.print_exc()
            self.running = False

    def update_menu(self):
        """
        Обновить меню.
        """
        action = self.menu.update(self.keys_pressed, self.mouse_pos, self.mouse_clicked)
        if action == 'start_game':
            self.start_game()
        elif action == 'settings':
            self.state_manager.change_state(GameState.SETTINGS)
        elif action == 'exit':
            self.running = False

    def update_game(self, delta_time):
        """
        Обновить игровую логику.

        Args:
            delta_time (float): Время кадра
        """
        self.game_time += delta_time

        # Обновить движок
        self.engine.update(self.entity_manager)

        # Получить объекты столкновений
        platforms, ladders, triggers = self.engine.current_level.get_collision_objects() if self.engine.current_level else ([], [], [])

        # Обновить сущности
        self.entity_manager.update_all(platforms, ladders, self.keys_pressed)

        # Обновить камеру
        self.update_camera()

        # Проверить условия окончания уровня
        if self.check_level_complete():
            self.complete_level()
        elif self.check_game_over():
            self.state_manager.change_state(GameState.GAME_OVER)

    def update_pause(self):
        """
        Обновить паузу.
        """
        # В паузе можно продолжить или выйти в меню
        if self.keys_pressed.get('pause', False):
            self.state_manager.change_state(GameState.PLAYING)
        elif self.keys_pressed.get('enter', False):
            self.state_manager.change_state(GameState.MENU)
            self.reset_game()

    def update_game_over(self):
        """
        Обновить экран окончания игры.
        """
        if self.keys_pressed.get('enter', False):
            self.state_manager.change_state(GameState.MENU)
            self.reset_game()

    def update_level_complete(self):
        """
        Обновить экран завершения уровня.
        """
        if self.keys_pressed.get('enter', False):
            self.next_level()

    def update_camera(self):
        """
        Обновить позицию камеры.
        """
        if self.entity_manager.player:
            player = self.entity_manager.player

            # Гладкое следование за игроком
            target_x = player.x - SCREEN_WIDTH // 2
            target_y = player.y - SCREEN_HEIGHT // 2

            self.camera_x += (target_x - self.camera_x) * CAMERA_SMOOTHING
            self.camera_y += (target_y - self.camera_y) * CAMERA_SMOOTHING

            # Ограничения камеры
            self.camera_x = clamp(self.camera_x, 0, SCREEN_WIDTH - SCREEN_WIDTH)
            self.camera_y = clamp(self.camera_y, 0, SCREEN_HEIGHT - SCREEN_HEIGHT)

    def check_level_complete(self):
        """
        Проверить завершение уровня.

        Returns:
            bool: True если уровень завершен
        """
        if not self.engine.current_level:
            return False

        level_data = get_level_data(self.level_manager.current_level)
        if not level_data:
            return False

        goal = level_data.get('goal_position', {})
        return self.entity_manager.check_win_condition(
            goal.get('x', 0), goal.get('y', 0)
        )

    def check_game_over(self):
        """
        Проверить окончание игры.

        Returns:
            bool: True если игра окончена
        """
        return self.entity_manager.check_game_over()

    def start_game(self):
        """
        Начать игру.
        """
        try:
            level_data = self.level_manager.start_level(1)
            if level_data:
                self.engine.load_level(1)
                self.setup_level(level_data)
                self.state_manager.change_state(GameState.PLAYING)
                self.level_start_time = self.game_time
            else:
                print("Ошибка загрузки уровня!")
                self.state_manager.change_state(GameState.MENU)
        except Exception as e:
            print(f"Ошибка запуска игры: {e}")
            import traceback
            traceback.print_exc()
            self.state_manager.change_state(GameState.MENU)

    def setup_level(self, level_data):
        """
        Настроить уровень.

        Args:
            level_data (dict): Данные уровня
        """
        try:
            # Очистить сущности
            self.entity_manager = EntityManager()

            # Настроить игрока
            spawn = level_data.get('start_position', {'x': 50, 'y': 700})
            self.entity_manager.add_player(spawn['x'], spawn['y'])

            # Добавить врагов
            for enemy_data in level_data.get('enemies', []):
                kwargs = {k: v for k, v in enemy_data.items() if k not in ['x', 'y', 'type']}
                self.entity_manager.add_enemy(
                    enemy_data['x'], enemy_data['y'],
                    enemy_data.get('type', 'patrol'),
                    **kwargs
                )

            # Добавить коллекционные предметы
            for item_data in level_data.get('collectibles', []):
                self.entity_manager.add_collectible(
                    item_data['x'], item_data['y'],
                    item_data.get('type', 'coin'),
                    item_data.get('value', 100)
                )

            # Сбросить камеру
            self.camera_x = 0
            self.camera_y = 0
        except Exception as e:
            print(f"Ошибка настройки уровня: {e}")
            import traceback
            traceback.print_exc()
            self.state_manager.change_state(GameState.MENU)

    def complete_level(self):
        """
        Завершить уровень.
        """
        level_time = self.game_time - self.level_start_time
        self.level_manager.complete_level(self.game_score, level_time)
        self.state_manager.change_state(GameState.LEVEL_COMPLETE)

    def next_level(self):
        """
        Перейти к следующему уровню.
        """
        next_level = self.level_manager.current_level + 1
        level_data = self.level_manager.start_level(next_level)

        if level_data and next_level <= TOTAL_LEVELS:
            self.engine.load_level(next_level)
            self.setup_level(level_data)
            self.state_manager.change_state(GameState.PLAYING)
            self.level_start_time = self.game_time
        else:
            # Все уровни пройдены
            self.state_manager.change_state(GameState.CREDITS)

    def reset_game(self):
        """
        Сбросить игру.
        """
        self.game_score = 0
        self.game_time = 0
        self.entity_manager = EntityManager()
        self.camera_x = 0
        self.camera_y = 0

    def render(self):
        """
        Отрисовать игру.
        """
        try:
            if self.state_manager.current_state == GameState.MENU:
                self.menu.render(self.screen)
            elif self.state_manager.current_state == GameState.PLAYING:
                self.render_game()
            elif self.state_manager.current_state == GameState.PAUSED:
                self.render_game()
                self.render_pause_overlay()
            elif self.state_manager.current_state == GameState.GAME_OVER:
                self.render_game_over()
            elif self.state_manager.current_state == GameState.LEVEL_COMPLETE:
                self.render_level_complete()

            # Отрисовка переходов между состояниями
            if self.state_manager.is_transitioning():
                self.render_transition()
        except Exception as e:
            print(f"Ошибка в отрисовке: {e}")
            import traceback
            traceback.print_exc()
            self.running = False

    def render_game(self):
        """
        Отрисовать игровой экран.
        """
        # Отрисовка уровня через рендерер
        game_state = self.entity_manager.get_game_state()
        game_state.update({
            'theme': 'day',
            'time_of_day': 0.5,
            'platforms': [p.get_collision_info() for p in self.engine.current_level.platforms] if self.engine.current_level else [],
            'ladders': [l.get_collision_info() for l in self.engine.current_level.ladders] if self.engine.current_level else [],
            'score': self.game_score,
            'lives': self.entity_manager.player.lives if self.entity_manager.player else 0,
            'level': self.level_manager.current_level
        })

        render_game_screen(self.screen, game_state, self.camera_x, self.camera_y)

    def render_pause_overlay(self):
        """
        Отрисовать оверлей паузы.
        """
        # Полупрозрачный черный фон
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))

        # Текст паузы
        draw_text(self.screen, UI_TEXTS['paused'],
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, 48, center=True)
        draw_text(self.screen, "ESC - продолжить, Enter - меню",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60, GRAY_LIGHT, 18, center=True)

    def render_game_over(self):
        """
        Отрисовать экран окончания игры.
        """
        self.screen.fill(BLACK)
        draw_text(self.screen, UI_TEXTS['game_over'],
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, RED, 48, center=True)
        draw_text(self.screen, f"Финальный счет: {self.game_score}",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, 24, center=True)
        draw_text(self.screen, "Enter - вернуться в меню",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, GRAY_LIGHT, 18, center=True)

    def render_level_complete(self):
        """
        Отрисовать экран завершения уровня.
        """
        self.screen.fill(BLACK)
        draw_text(self.screen, UI_TEXTS['level_complete'],
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50, GREEN, 48, center=True)
        draw_text(self.screen, f"Уровень {self.level_manager.current_level} пройден!",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE, 24, center=True)
        draw_text(self.screen, f"Счет: {self.game_score}",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30, YELLOW, 20, center=True)
        draw_text(self.screen, "Enter - следующий уровень",
                 SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80, GRAY_LIGHT, 18, center=True)

    def render_transition(self):
        """
        Отрисовать переход между состояниями.
        """
        progress = self.state_manager.get_transition_progress()
        alpha = int(255 * (1 - progress))

        transition_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        transition_surface.fill((0, 0, 0, alpha))
        self.screen.blit(transition_surface, (0, 0))

    def quit(self):
        """
        Завершить игру.
        """
        self.level_manager.save_progress()
        pygame.quit()
        sys.exit()

# =============================================================================
# ДОПОЛНИТЕЛЬНЫЕ ФУНКЦИИ И КЛАССЫ
# =============================================================================

def initialize_game():
    """
    Инициализировать игру.

    Returns:
        DonkeyKongGame: Экземпляр игры
    """
    try:
        print("Инициализация Donkey Kong: Ultimate Code Edition...")
        game = DonkeyKongGame()
        print("Игра инициализирована успешно!")
        return game
    except Exception as e:
        print(f"Ошибка инициализации игры: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
        sys.exit(1)

def show_splash_screen(screen):
    """
    Показать заставку игры.

    Args:
        screen: Экран для отрисовки
    """
    screen.fill(BLACK)
    draw_text(screen, "Donkey Kong", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50,
             WHITE, 48, center=True)
    draw_text(screen, "Ultimate Code Edition", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2,
             YELLOW, 24, center=True)
    draw_text(screen, "Загрузка...", SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50,
             GRAY_LIGHT, 18, center=True)
    pygame.display.flip()
    pygame.time.wait(2000)  # Пауза 2 секунды

def check_system_requirements():
    """
    Проверить системные требования.

    Returns:
        bool: True если требования выполнены
    """
    # Проверка версии Pygame
    pygame_version = pygame.version.ver
    print(f"Pygame версия: {pygame_version}")

    # Проверка экрана
    try:
        test_screen = pygame.display.set_mode((100, 100))
        pygame.display.quit()
        return True
    except:
        print("Ошибка: Невозможно создать окно Pygame")
        return False

def handle_command_line_args():
    """
    Обработать аргументы командной строки.

    Returns:
        dict: Настройки из аргументов
    """
    import sys
    settings = {
        'debug': False,
        'fullscreen': False,
        'difficulty': 'normal'
    }

    for arg in sys.argv[1:]:
        if arg == '--debug':
            settings['debug'] = True
        elif arg == '--fullscreen':
            settings['fullscreen'] = True
        elif arg.startswith('--difficulty='):
            difficulty = arg.split('=')[1]
            if difficulty in ['easy', 'normal', 'hard']:
                settings['difficulty'] = difficulty

    return settings

# Функции для отладки
def debug_game_state(game):
    """
    Отладочная информация о состоянии игры.

    Args:
        game (DonkeyKongGame): Игра
    """
    if EXTRA_CONSTANTS.get('debug_mode', False):
        debug_data = {
            'fps': game.clock.get_fps(),
            'state': game.state_manager.current_state,
            'level': game.level_manager.current_level,
            'score': game.game_score,
            'entities': len(game.entity_manager.enemies) + len(game.entity_manager.barrels),
            'camera': (game.camera_x, game.camera_y)
        }

        # Отрисовка отладочной информации
        y_offset = 10
        for key, value in debug_data.items():
            draw_text(game.screen, f"{key}: {value}", 10, y_offset, WHITE, 16)
            y_offset += 20

def save_screenshot(screen, filename="screenshot.png"):
    """
    Сохранить скриншот.

    Args:
        screen: Экран для сохранения
        filename (str): Имя файла
    """
    pygame.image.save(screen, filename)
    print(f"Скриншот сохранен: {filename}")

def toggle_fullscreen(screen):
    """
    Переключить полноэкранный режим.

    Args:
        screen: Экран
    """
    pygame.display.toggle_fullscreen()

# Обработчики ошибок
def handle_error(error_type, error_message):
    """
    Обработать ошибку.

    Args:
        error_type (str): Тип ошибки
        error_message (str): Сообщение об ошибке
    """
    print(f"Ошибка {error_type}: {error_message}")
    # В реальной игре запись в лог или показ диалога

def graceful_shutdown(game):
    """
    Корректное завершение игры.

    Args:
        game (DonkeyKongGame): Игра
    """
    try:
        game.quit()
    except Exception as e:
        print(f"Ошибка при завершении: {e}")
        pygame.quit()
        sys.exit(1)

# =============================================================================
# ТОЧКА ВХОДА В ПРОГРАММУ
# =============================================================================

def main():
    """
    Главная функция программы.
    """
    try:
        # Обработка аргументов командной строки
        settings = handle_command_line_args()

        # Проверка системных требований
        if not check_system_requirements():
            print("Системные требования не выполнены. Выход.")
            input("Нажмите Enter для выхода...")
            sys.exit(1)

        # Инициализация игры
        game = initialize_game()

        # Применение настроек
        if settings['debug']:
            EXTRA_CONSTANTS['debug_mode'] = True
        game.difficulty = settings['difficulty']

        # Заставка
        show_splash_screen(game.screen)

        # Главный цикл
        game.run()

    except KeyboardInterrupt:
        print("Игра прервана пользователем.")
    except Exception as e:
        handle_error("неизвестная", str(e))
        print(f"Подробности ошибки: {e}")
        import traceback
        traceback.print_exc()
        input("Нажмите Enter для выхода...")
    finally:
        try:
            pygame.quit()
        except:
            pass
        sys.exit(0)

if __name__ == "__main__":
    main()

# Этот файл содержит более 600 строк кода с полным игровым циклом,
# машиной состояний, менеджером уровней и обработкой всех игровых событий