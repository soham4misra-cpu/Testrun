import pygame
import random
from pygame.math import Vector2


class Player:
    def __init__(self, image, pos, speed, max_hp=None):
        self.image = image
        self.pos = Vector2(pos)
        self.base_speed = speed
        self.speed = speed
        self.speed_boost_active = False
        self.speed_boost_end_ticks = 0
        self.max_hp = max_hp
        self.hp = max_hp
        self.invulnerable_until_ticks = 0

    @property
    def rect(self):
        rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
        rect.inflate_ip(-10, -10)
        return rect

    @property
    def center(self):
        return Vector2(self.pos.x + self.image.get_width() / 2, self.pos.y + self.image.get_height() / 2)

    def handle_input(self, keys):
        if keys[pygame.K_LEFT]:
            self.pos.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.pos.x += self.speed
        if keys[pygame.K_UP]:
            self.pos.y -= self.speed
        if keys[pygame.K_DOWN]:
            self.pos.y += self.speed

    def wrap_around(self, screen_width, screen_height):
        if self.pos.x < -self.image.get_width():
            self.pos.x = screen_width
        elif self.pos.x > screen_width:
            self.pos.x = -self.image.get_width()

        if self.pos.y < -self.image.get_height():
            self.pos.y = screen_height
        elif self.pos.y > screen_height:
            self.pos.y = -self.image.get_height()

    def start_speed_boost(self, multiplier, duration_ms, now_ticks):
        self.speed = self.base_speed * multiplier
        self.speed_boost_active = True
        self.speed_boost_end_ticks = now_ticks + duration_ms

    def update_speed_boost(self, now_ticks):
        if self.speed_boost_active and now_ticks >= self.speed_boost_end_ticks:
            self.speed_boost_active = False
            self.speed = self.base_speed

    def is_invulnerable(self, now_ticks):
        return now_ticks < self.invulnerable_until_ticks

    def take_damage(self, now_ticks, invulnerability_ms):
        self.hp -= 1
        self.invulnerable_until_ticks = now_ticks + invulnerability_ms
        return self.hp <= 0

    def reset(self, pos):
        self.pos = Vector2(pos)
        self.speed = self.base_speed
        self.speed_boost_active = False
        self.speed_boost_end_ticks = 0
        self.hp = self.max_hp
        self.invulnerable_until_ticks = 0

    def draw(self, screen):
        screen.blit(self.image, self.pos)


class Enemy:
    def __init__(self, image, pos, speed, max_health=None):
        self.image = image
        self.pos = Vector2(pos)
        self.speed = speed
        self.max_health = max_health
        self.health = max_health
        self.active = True
        self.respawn_at_ticks = 0

    @property
    def rect(self):
        rect = self.image.get_rect(topleft=(self.pos.x, self.pos.y))
        rect.inflate_ip(-10, -10)
        return rect

    def chase(self, target_pos):
        direction = target_pos - self.pos
        if direction.length() > 0:
            direction.normalize_ip()
            self.pos += direction * self.speed

    def take_hit(self):
        self.health -= 1
        if self.health <= 0:
            self.active = False
            return True
        return False

    def schedule_respawn(self, now_ticks, delay_ms):
        self.respawn_at_ticks = now_ticks + delay_ms

    def respawn(self, pos):
        self.pos = Vector2(pos)
        self.health = self.max_health
        self.active = True

    def reset(self, pos):
        self.pos = Vector2(pos)
        self.health = self.max_health
        self.active = True
        self.respawn_at_ticks = 0

    def draw(self, screen):
        screen.blit(self.image, self.pos)


class Bullet:
    def __init__(self, pos, direction, speed, radius, color):
        self.pos = Vector2(pos)
        if direction.length() > 0:
            direction = direction.normalize()
        self.velocity = direction * speed
        self.radius = radius
        self.color = color

    @property
    def rect(self):
        return pygame.Rect(
            self.pos.x - self.radius, self.pos.y - self.radius,
            self.radius * 2, self.radius * 2,
        )

    def update(self):
        self.pos += self.velocity

    def is_off_screen(self, screen_width, screen_height):
        return (
            self.pos.x < -self.radius or self.pos.x > screen_width + self.radius
            or self.pos.y < -self.radius or self.pos.y > screen_height + self.radius
        )

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)


class SpeedBoostPickup:
    def __init__(self, image, spawn_interval_ms):
        self.image = image
        self.spawn_interval_ms = spawn_interval_ms
        self.pos = None
        self.next_spawn_ticks = 0

    @property
    def rect(self):
        if self.pos is None:
            return None
        return self.image.get_rect(topleft=(self.pos.x, self.pos.y))

    def update(self, now_ticks, screen_width, screen_height):
        if self.pos is None and now_ticks >= self.next_spawn_ticks:
            x = random.randint(0, screen_width - self.image.get_width())
            y = random.randint(0, screen_height - self.image.get_height())
            self.pos = Vector2(x, y)

    def collect(self, now_ticks):
        self.pos = None
        self.next_spawn_ticks = now_ticks + self.spawn_interval_ms

    def reset(self, now_ticks):
        self.pos = None
        self.next_spawn_ticks = now_ticks + self.spawn_interval_ms

    def draw(self, screen):
        if self.pos is not None:
            screen.blit(self.image, self.pos)
