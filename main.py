import pygame
import sys

# --- Константы ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Цвета (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Физические константы для игрока
PLAYER_ACC = 0.6  # Ускорение при нажатии клавиш
PLAYER_FRICTION = -0.12 # Трение (замедление)
PLAYER_GRAV = 0.7   # Сила гравитации
PLAYER_JUMP = 15    # Сила прыжка

# --- Инициализация Pygame ---
pygame.init()
pygame.mixer.init()

# --- Создание окна игры ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Мой Платформер")

# --- Объект Clock для контроля FPS ---
clock = pygame.time.Clock()

# --- Класс Игрока ---
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.image = pygame.Surface((30, 40))
        self.image.fill(BLUE)
        # --- Блок для загрузки картинки (если есть) ---
        # try:
        #     self.image = pygame.image.load('player.png').convert_alpha()
        # except pygame.error as e:
        #     print(f"Не удалось загрузить изображение игрока: {e}")
        #     self.image = pygame.Surface((30, 40))
        #     self.image.fill(RED)
        # --- Конец блока ---

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 10 # Начнем чуть выше пола

        # Векторы движения и ускорения
        self.pos = pygame.math.Vector2(self.rect.centerx, self.rect.centery) # Используем векторы для точной позиции
        self.vel = pygame.math.Vector2(0, 0) # Вектор скорости
        self.acc = pygame.math.Vector2(0, 0) # Вектор ускорения

        self.on_ground = False # Флаг для проверки, на земле ли игрок

    def jump(self):
        # Прыгаем, только если стоим на земле (или платформе)
        # Пока проверка только на временный "пол"
        # TODO: Заменить проверку на столкновение с платформами
        self.rect.x += 1 # Сдвигаемся чуть вправо для проверки столкновения ниже
        hits = pygame.sprite.spritecollide(self, platforms, False) # Проверяем столкновение с платформами
        self.rect.x -= 1 # Возвращаем обратно
        if hits or self.on_ground: # Если стоим на платформе или на "полу"
             self.vel.y = -PLAYER_JUMP # Придаем вертикальную скорость вверх
             self.on_ground = False # Мы больше не на земле

    def update(self):
        # Сбрасываем ускорение на каждом кадре (кроме гравитации)
        self.acc = pygame.math.Vector2(0, PLAYER_GRAV) # Гравитация действует всегда

        # Проверяем нажатые клавиши для горизонтального движения
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: # Клавиша A (влево)
            self.acc.x = -PLAYER_ACC
        if keys[pygame.K_d]: # Клавиша D (вправо)
            self.acc.x = PLAYER_ACC

        # Применяем трение к горизонтальному движению
        # Ускорение = текущее_ускорение + скорость * трение
        self.acc.x += self.vel.x * PLAYER_FRICTION

        # Обновляем скорость на основе ускорения (уравнения движения)
        self.vel += self.acc

        # Ограничим максимальную горизонтальную скорость (опционально)
        # if abs(self.vel.x) > 7:
        #     self.vel.x = 7 if self.vel.x > 0 else -7

        # Обновляем позицию на основе скорости
        # Используем векторы для более точных расчетов позиции
        self.pos += self.vel + 0.5 * self.acc # Формула с учетом ускорения

        # --- Предотвращение выхода за пределы экрана по горизонтали ---
        if self.pos.x > SCREEN_WIDTH - self.rect.width / 2:
            self.pos.x = SCREEN_WIDTH - self.rect.width / 2
            self.vel.x = 0 # Останавливаем горизонтальное движение у края
        if self.pos.x < self.rect.width / 2:
            self.pos.x = self.rect.width / 2
            self.vel.x = 0 # Останавливаем горизонтальное движение у края

        # Обновляем rect на основе новой векторной позиции self.pos
        self.rect.midbottom = self.pos # Используем midbottom для позиционирования

        # --- Временная проверка "пола" ---
        # TODO: Это будет заменено на проверку столкновений с платформами
        if self.rect.bottom >= SCREEN_HEIGHT:
            self.pos.y = SCREEN_HEIGHT - self.rect.height / 2 + 1 # Ставим точно на "пол"
            self.vel.y = 0  # Останавливаем вертикальное падение
            self.on_ground = True # Мы на земле
        else:
            self.on_ground = False

# --- /Класс Игрока ---


# --- Создание групп спрайтов ---
all_sprites = pygame.sprite.Group()
platforms = pygame.sprite.Group() # Группа для платформ (пока пустая)
# mobs = pygame.sprite.Group()
# items = pygame.sprite.Group()

# --- Создание игрока ---
player = Player()
all_sprites.add(player)

# --- Основной игровой цикл ---
running = True
while running:
    # Держим цикл на правильной скорости
    clock.tick(FPS)

    # 1. Обработка событий
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # --- Обработка нажатия клавиши ПРОБЕЛ для прыжка ---
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.jump() # Вызываем метод прыжка у игрока
            if event.key == pygame.K_ESCAPE: # Выход по Escape
                running = False

    # 2. Обновление состояния игры
    all_sprites.update() # Вызываем update() у всех спрайтов (включая игрока)

    # 3. Отрисовка (Рендеринг)
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()

# --- Завершение работы Pygame и выход ---
pygame.quit()
sys.exit()