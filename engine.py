import random

import pygame
from pygame.math import Vector2

import quiz
import settings
from button import Button
from entities import Player, Enemy, SpeedBoostPickup, AmmoPickup, Bullet

QUIZ_BUTTON_POSITIONS = [(500, 380), (500, 460), (500, 540), (500, 620)]


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Python game")
        self.clock = pygame.time.Clock()

        self.small_font = pygame.font.Font(None, 40)
        self.font = pygame.font.Font(None, 60)
        self.title_font = pygame.font.Font(None, 100)
        self.menu_font = pygame.font.Font(None, 60)

        self._load_assets()
        self._create_buttons()
        self._create_entities()

        self.game_state = "menu"
        self.mode = None
        self.game_over = False
        self.elapsed_seconds = 0
        self.start_ticks = pygame.time.get_ticks()
        self.music_volume = settings.DEFAULT_MUSIC_VOLUME
        self.bullets = []
        self.kill_count = 0
        self.wave_number = 1
        self.quiz_question = None
        self.quiz_answer = None
        self.quiz_buttons = []
        self.quiz_entered_ticks = 0
        self.quiz_feedback = None
        self.quiz_feedback_until_ticks = 0
        self.quiz_last_correct = None

        pygame.mixer.music.load(settings.MUSIC_PATH)
        pygame.mixer.music.set_volume(self.music_volume)
        pygame.mixer.music.play(-1)

    def _load_assets(self):
        self.background_img = pygame.image.load(settings.BACKGROUND_IMG_PATH).convert()
        self.background_img = pygame.transform.scale(
            self.background_img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self.menu_img = pygame.image.load(settings.MENU_IMG_PATH).convert()
        self.menu_img = pygame.transform.scale(
            self.menu_img, (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        self.player_img = pygame.image.load(settings.PLAYER_IMG_PATH).convert_alpha()
        self.enemy_img = pygame.image.load(settings.ENEMY_IMG_PATH).convert_alpha()
        self.speedup_img = pygame.image.load(settings.SPEEDUP_IMG_PATH).convert()
        self.speedup_img = pygame.transform.scale(self.speedup_img, settings.SPEEDUP_ICON_SIZE)

        self.ammo_img = pygame.Surface(settings.AMMO_ICON_SIZE, pygame.SRCALPHA)
        pygame.draw.rect(
            self.ammo_img, settings.AMMO_ICON_COLOR,
            self.ammo_img.get_rect(), border_radius=4,
        )
        pygame.draw.rect(
            self.ammo_img, settings.AMMO_ICON_BORDER_COLOR,
            self.ammo_img.get_rect(), width=2, border_radius=4,
        )

    def _create_buttons(self):
        self.normal_button = Button(
            image=None, pos=(500, 220), text_input="NORMAL",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.endless_button = Button(
            image=None, pos=(500, 320), text_input="ENDLESS",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.options_button = Button(
            image=None, pos=(500, 420), text_input="OPTIONS",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.credits_button = Button(
            image=None, pos=(500, 520), text_input="CREDITS",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.back_button = Button(
            image=None, pos=(100, 60), text_input="BACK",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.volume_up_button = Button(
            image=None, pos=(600, 480), text_input="+",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )
        self.volume_down_button = Button(
            image=None, pos=(400, 480), text_input="-",
            font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
        )

    def _create_entities(self):
        self.player = Player(
            self.player_img, settings.PLAYER_START_POS, settings.PLAYER_SPEED,
            max_hp=settings.PLAYER_MAX_HP,
            starting_ammo=settings.PLAYER_STARTING_AMMO, max_ammo=settings.PLAYER_MAX_AMMO,
        )
        self.enemy = Enemy(
            self.enemy_img, settings.ENEMY_START_POS, settings.ENEMY_SPEED,
            max_health=settings.ENEMY_MAX_HEALTH,
        )
        self.speedup = SpeedBoostPickup(self.speedup_img, settings.SPEEDUP_SPAWN_INTERVAL_MS)
        self.ammo_pickups = [
            AmmoPickup(self.ammo_img, settings.AMMO_SPAWN_INTERVAL_MS, settings.AMMO_PICKUP_AMOUNT)
            for _ in range(settings.AMMO_PICKUP_COUNT)
        ]

    def _random_pos(self, image):
        x = random.randint(0, self.screen.get_width() - image.get_width())
        y = random.randint(0, self.screen.get_height() - image.get_height())
        return Vector2(x, y)

    def _reset_ammo_pickups(self, now_ticks):
        stagger_ms = settings.AMMO_SPAWN_INTERVAL_MS // len(self.ammo_pickups)
        for i, pickup in enumerate(self.ammo_pickups):
            pickup.pos = None
            pickup.next_spawn_ticks = now_ticks + i * stagger_ms

    def reset_game(self, mode=None):
        if mode is not None:
            self.mode = mode
        now = pygame.time.get_ticks()
        self.player.reset(settings.PLAYER_START_POS)
        self.enemy.reset(settings.ENEMY_START_POS)
        self.speedup.reset(now)
        self._reset_ammo_pickups(now)
        self.bullets = []
        self.kill_count = 0
        self.wave_number = 1
        self.quiz_question = None
        self.quiz_answer = None
        self.quiz_buttons = []
        self.quiz_feedback = None
        self.quiz_last_correct = None
        self.game_over = False
        self.start_ticks = now
        self.elapsed_seconds = 0
        self.game_state = self.mode

    def run(self):
        running = True
        while running:
            running = self.handle_events()
            if self.game_state == "endless":
                self.update_endless()
            elif self.game_state == "normal":
                self.update_normal()
            elif self.game_state == "quiz":
                self.update_quiz()
            self.draw()
            pygame.display.flip()
            self.clock.tick(settings.FPS)
        pygame.quit()

    def handle_events(self):
        mouse_pos = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_click(mouse_pos)
            elif event.type == pygame.KEYDOWN:
                if self.game_over and event.key == pygame.K_r:
                    self.reset_game()
        return True

    def _handle_click(self, mouse_pos):
        if self.game_state == "menu":
            if self.normal_button.checkForInput(mouse_pos):
                self.reset_game(mode="normal")
            elif self.endless_button.checkForInput(mouse_pos):
                self.reset_game(mode="endless")
            elif self.options_button.checkForInput(mouse_pos):
                self.game_state = "options"
            elif self.credits_button.checkForInput(mouse_pos):
                self.game_state = "credits"
        elif self.game_state == "options":
            if self.volume_up_button.checkForInput(mouse_pos):
                self.music_volume = min(1.0, self.music_volume + 0.1)
                pygame.mixer.music.set_volume(self.music_volume)
            elif self.volume_down_button.checkForInput(mouse_pos):
                self.music_volume = max(0.0, self.music_volume - 0.1)
                pygame.mixer.music.set_volume(self.music_volume)
            elif self.back_button.checkForInput(mouse_pos):
                self.game_state = "menu"
        elif self.game_state in ("credits", "game_over"):
            if self.back_button.checkForInput(mouse_pos):
                self.game_state = "menu"
        elif self.game_state == "normal":
            if self.player.has_ammo():
                direction = Vector2(mouse_pos) - self.player.center
                self.bullets.append(Bullet(
                    self.player.center, direction,
                    settings.BULLET_SPEED, settings.BULLET_RADIUS, settings.BULLET_COLOR,
                ))
                self.player.consume_ammo()
        elif self.game_state == "quiz":
            if self.quiz_feedback is None:
                for button in self.quiz_buttons:
                    if button.checkForInput(mouse_pos):
                        self._resolve_quiz(int(button.text_input) == self.quiz_answer)
                        break

    def update_endless(self):
        now = pygame.time.get_ticks()
        if not self.game_over:
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys)
            self.player.wrap_around(self.screen.get_width(), self.screen.get_height())
            self.enemy.chase(self.player.pos)
            self.elapsed_seconds = (now - self.start_ticks) // 1000
            self.player.update_speed_boost(now)
            self.speedup.update(now, self.screen.get_width(), self.screen.get_height())

        if not self.game_over and self.speedup.rect and self.player.rect.colliderect(self.speedup.rect):
            self.player.start_speed_boost(
                settings.SPEED_BOOST_MULTIPLIER, settings.SPEED_BOOST_DURATION_MS, now
            )
            self.speedup.collect(now)

        if not self.game_over and self.player.rect.colliderect(self.enemy.rect):
            self.game_over = True
            self.game_state = "game_over"

    def update_normal(self):
        now = pygame.time.get_ticks()
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        self.player.wrap_around(self.screen.get_width(), self.screen.get_height())
        self.elapsed_seconds = (now - self.start_ticks) // 1000
        self._update_wave()
        if self.game_state != "normal":
            return

        if self.enemy.active:
            self.enemy.chase(self.player.pos)
        elif now >= self.enemy.respawn_at_ticks:
            self.enemy.respawn(self._random_pos(self.enemy.image))

        for pickup in self.ammo_pickups:
            pickup.update(now, self.screen.get_width(), self.screen.get_height())
            if pickup.rect and self.player.rect.colliderect(pickup.rect):
                self.player.add_ammo(pickup.amount)
                pickup.collect(now)

        for bullet in self.bullets:
            bullet.update()
        self.bullets = [
            b for b in self.bullets
            if not b.is_off_screen(self.screen.get_width(), self.screen.get_height())
        ]

        if self.enemy.active:
            for bullet in list(self.bullets):
                if bullet.rect.colliderect(self.enemy.rect):
                    self.bullets.remove(bullet)
                    if self.enemy.take_hit():
                        self.kill_count += 1
                        self.enemy.schedule_respawn(now, settings.ENEMY_RESPAWN_DELAY_MS)

        if (
            self.enemy.active
            and not self.player.is_invulnerable(now)
            and self.player.rect.colliderect(self.enemy.rect)
        ):
            if self.player.take_damage(now, settings.PLAYER_INVULNERABILITY_MS):
                self.game_over = True
                self.game_state = "game_over"

    def _update_wave(self):
        wave = self.elapsed_seconds // settings.WAVE_INTERVAL_SECONDS + 1
        if wave == self.wave_number:
            return
        self.wave_number = wave
        self.enemy.speed = self.enemy.base_speed + (wave - 1) * settings.WAVE_SPEED_INCREMENT
        self.enemy.max_health = self.enemy.base_max_health + (wave - 1) * settings.WAVE_HEALTH_INCREMENT
        self._start_quiz()

    def _start_quiz(self):
        question, answer, choices = quiz.generate_question()
        self.quiz_question = question
        self.quiz_answer = answer
        self.quiz_buttons = [
            Button(
                image=None, pos=pos, text_input=str(choice),
                font=self.menu_font, base_color="White", hovering_color=settings.NAVY,
            )
            for pos, choice in zip(QUIZ_BUTTON_POSITIONS, choices)
        ]
        self.quiz_entered_ticks = pygame.time.get_ticks()
        self.game_state = "quiz"

    def _resolve_quiz(self, correct):
        now = pygame.time.get_ticks()

        if correct:
            self.player.add_ammo(self.player.max_ammo)
            self.player.invulnerable_until_ticks = now + settings.QUIZ_CORRECT_INVULNERABILITY_MS
            self.quiz_feedback = "CORRECT! Ammo refilled."
        else:
            self.enemy.pos = self.enemy.pos.lerp(self.player.pos, settings.QUIZ_WRONG_ENEMY_ADVANCE)
            self.quiz_feedback = f"INCORRECT. The answer was {self.quiz_answer}."

        self.quiz_last_correct = correct
        self.quiz_buttons = []
        self.quiz_feedback_until_ticks = now + settings.QUIZ_FEEDBACK_DURATION_MS

    def update_quiz(self):
        if self.quiz_feedback is None:
            return
        if pygame.time.get_ticks() >= self.quiz_feedback_until_ticks:
            self._finish_quiz()

    def _finish_quiz(self):
        now = pygame.time.get_ticks()
        self.start_ticks += now - self.quiz_entered_ticks
        self.quiz_question = None
        self.quiz_answer = None
        self.quiz_feedback = None
        self.quiz_last_correct = None
        self.game_state = "normal"

    def draw(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.game_state == "menu":
            self._draw_menu(mouse_pos)
        elif self.game_state == "options":
            self._draw_options(mouse_pos)
        elif self.game_state == "credits":
            self._draw_credits(mouse_pos)
        elif self.game_state == "endless":
            self._draw_endless()
        elif self.game_state == "normal":
            self._draw_normal()
        elif self.game_state == "quiz":
            self._draw_quiz(mouse_pos)
        elif self.game_state == "game_over":
            self._draw_game_over(mouse_pos)

    def _draw_menu(self, mouse_pos):
        self.screen.blit(self.menu_img, (0, 0))
        buttons = (self.normal_button, self.endless_button, self.options_button, self.credits_button)
        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

    def _draw_options(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))
        volume_label = self.menu_font.render("MUSIC VOLUME", True, settings.WHITE)
        self.screen.blit(volume_label, (330, 320))
        volume_percent = self.menu_font.render(f"{int(self.music_volume * 100)}%", True, settings.WHITE)
        volume_rect = volume_percent.get_rect(center=(500, 480))
        self.screen.blit(volume_percent, volume_rect)
        self.volume_up_button.changeColor(mouse_pos)
        self.volume_up_button.update(self.screen)
        self.volume_down_button.changeColor(mouse_pos)
        self.volume_down_button.update(self.screen)
        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)

    def _draw_credits(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))
        credits_text = self.title_font.render("CREDITS", True, settings.WHITE)
        credits_rect = credits_text.get_rect(center=(500, 140))
        self.screen.blit(credits_text, credits_rect)
        line1 = self.menu_font.render("MADE BY SOHAM", True, settings.WHITE)
        line2 = self.menu_font.render("BUILT WITH PYTHON AND PYGAME.", True, settings.WHITE)
        self.screen.blit(line1, (220, 320))
        self.screen.blit(line2, (190, 390))
        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)

    def _draw_endless(self):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        self.speedup.draw(self.screen)

        timer_text = self.small_font.render(f"time: {self.elapsed_seconds} ", True, settings.WHITE)
        self.screen.blit(timer_text, (20, 20))

        if self.player.speed_boost_active:
            seconds_left = max(0, (self.player.speed_boost_end_ticks - pygame.time.get_ticks()) // 1000 + 1)
            boost_text = self.small_font.render(f"speed boost: {seconds_left}s", True, settings.YELLOW)
            self.screen.blit(boost_text, (20, 60))

    def _draw_normal(self):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        if self.enemy.active:
            self.enemy.draw(self.screen)
        for pickup in self.ammo_pickups:
            pickup.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)

        timer_text = self.small_font.render(f"time: {self.elapsed_seconds} ", True, settings.WHITE)
        self.screen.blit(timer_text, (20, 20))

        kills_text = self.small_font.render(f"kills: {self.kill_count}", True, settings.WHITE)
        self.screen.blit(kills_text, (20, 60))

        wave_text = self.small_font.render(f"wave: {self.wave_number}", True, settings.WHITE)
        self.screen.blit(wave_text, (20, 100))

        hp_text = self.small_font.render(f"hp: {self.player.hp}/{self.player.max_hp}", True, settings.YELLOW)
        self.screen.blit(hp_text, (20, 140))

        ammo_text = self.small_font.render(f"ammo: {self.player.ammo}/{self.player.max_ammo}", True, settings.YELLOW)
        self.screen.blit(ammo_text, (20, 180))

    def _draw_quiz(self, mouse_pos):
        self._draw_normal()

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        header_text = self.font.render(f"WAVE {self.wave_number} CHALLENGE", True, settings.WHITE)
        header_rect = header_text.get_rect(center=(500, 220))
        self.screen.blit(header_text, header_rect)

        if self.quiz_feedback is not None:
            color = settings.GREEN if self.quiz_last_correct else settings.RED
            feedback_text = self.menu_font.render(self.quiz_feedback, True, color)
            feedback_rect = feedback_text.get_rect(center=(500, 400))
            self.screen.blit(feedback_text, feedback_rect)
            return

        question_text = self.menu_font.render(self.quiz_question, True, settings.WHITE)
        question_rect = question_text.get_rect(center=(500, 300))
        self.screen.blit(question_text, question_rect)

        for button in self.quiz_buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

    def _draw_game_over(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        if self.enemy.active:
            self.enemy.draw(self.screen)

        timer_text = self.small_font.render(f"time: {self.elapsed_seconds} ", True, settings.WHITE)
        self.screen.blit(timer_text, (20, 20))
        if self.mode == "normal":
            kills_text = self.small_font.render(f"kills: {self.kill_count}", True, settings.WHITE)
            self.screen.blit(kills_text, (20, 60))
            wave_text = self.small_font.render(f"wave: {self.wave_number}", True, settings.WHITE)
            self.screen.blit(wave_text, (20, 100))
        over_text = self.font.render("game over", True, settings.WHITE)
        restart_text = self.menu_font.render("press R to restart", True, settings.WHITE)
        self.screen.blit(over_text, (350, 280))
        self.screen.blit(restart_text, (270, 360))
        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)
