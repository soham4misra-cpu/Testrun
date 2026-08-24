import asyncio
import math
import random

import pygame
from pygame import Vector2

import trivia
import settings
from button import Button
from entities import Player, Enemy, SpeedBoostPickup, AmmoPickup, Bullet

QUIZ_BUTTON_POSITIONS = [(500, 400), (500, 470), (500, 540), (500, 610)]


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT))
        pygame.display.set_caption("Python game")
        self.clock = pygame.time.Clock()

        self.small_font = self._load_font(26)
        self.font = self._load_font(52)
        self.title_font = self._load_font(84)
        self.menu_font = self._load_font(42)
        self.label_font = self._load_font(20)

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

    def _load_font(self, size):
        return pygame.font.Font(settings.FONT_PATH, size)

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
            image=None, pos=(500, 240), text_input="NORMAL",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
        )
        self.endless_button = Button(
            image=None, pos=(500, 330), text_input="ENDLESS",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
        )
        self.options_button = Button(
            image=None, pos=(500, 420), text_input="OPTIONS",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
        )
        self.credits_button = Button(
            image=None, pos=(500, 510), text_input="CREDITS",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
        )
        self.back_button = Button(
            image=None, pos=(110, 60), text_input="< BACK",
            font=self.label_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
            padding_x=18, padding_y=10,
        )
        self.volume_up_button = Button(
            image=None, pos=(610, 480), text_input="+",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
        )
        self.volume_down_button = Button(
            image=None, pos=(390, 480), text_input="-",
            font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
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

    async def run(self):
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
            await asyncio.sleep(0)
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
        self.player.update_speed_boost(now)
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

        self.speedup.update(now, self.screen.get_width(), self.screen.get_height())
        if self.speedup.rect and self.player.rect.colliderect(self.speedup.rect):
            self.player.start_speed_boost(
                settings.SPEED_BOOST_MULTIPLIER, settings.SPEED_BOOST_DURATION_MS, now
            )
            self.speedup.collect(now)

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
        question, answer, choices = trivia.generate_question()
        self.quiz_question = question
        self.quiz_answer = answer
        self.quiz_buttons = [
            Button(
                image=None, pos=pos, text_input=str(choice),
                font=self.menu_font, base_color=settings.TEXT_PRIMARY, hovering_color=settings.ACCENT,
                padding_x=60, padding_y=10,
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

    def _draw_panel(self, rect, fill=None, border=None, radius=None, border_width=2):
        fill = settings.PANEL_BG if fill is None else fill
        border = settings.PANEL_BORDER if border is None else border
        radius = settings.PANEL_RADIUS if radius is None else radius

        shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=radius)
        self.screen.blit(shadow, (rect.x + 3, rect.y + 5))

        panel = pygame.Surface(rect.size, pygame.SRCALPHA)
        local_rect = panel.get_rect()
        pygame.draw.rect(panel, fill, local_rect, border_radius=radius)
        if border is not None:
            pygame.draw.rect(panel, border, local_rect, width=border_width, border_radius=radius)
        self.screen.blit(panel, rect)

    def _draw_bar(self, pos, size, ratio, fg_color, radius=7):
        rect = pygame.Rect(pos, size)
        pygame.draw.rect(self.screen, settings.BG_DARK, rect, border_radius=radius)
        ratio = max(0.0, min(1.0, ratio))
        if ratio > 0:
            fill_width = max(radius * 2, round(size[0] * ratio))
            fill_rect = pygame.Rect(pos, (min(fill_width, size[0]), size[1]))
            pygame.draw.rect(self.screen, fg_color, fill_rect, border_radius=radius)
        pygame.draw.rect(self.screen, settings.PANEL_BORDER, rect, width=2, border_radius=radius)

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

        panel_rect = pygame.Rect(0, 0, 420, 350)
        panel_rect.center = (500, 375)
        self._draw_panel(panel_rect)

        buttons = (self.normal_button, self.endless_button, self.options_button, self.credits_button)
        for button in buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

    def _draw_options(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))

        panel_rect = pygame.Rect(0, 0, 560, 340)
        panel_rect.center = (500, 400)
        self._draw_panel(panel_rect)

        title_text = self.font.render("OPTIONS", True, settings.ACCENT)
        title_rect = title_text.get_rect(center=(500, 280))
        self.screen.blit(title_text, title_rect)

        volume_label = self.menu_font.render("MUSIC VOLUME", True, settings.TEXT_PRIMARY)
        volume_label_rect = volume_label.get_rect(center=(500, 350))
        self.screen.blit(volume_label, volume_label_rect)

        self._draw_bar((330, 400), (340, 22), self.music_volume, settings.ACCENT)

        volume_percent = self.small_font.render(f"{int(self.music_volume * 100)}%", True, settings.TEXT_MUTED)
        volume_rect = volume_percent.get_rect(center=(500, 450))
        self.screen.blit(volume_percent, volume_rect)

        self.volume_up_button.changeColor(mouse_pos)
        self.volume_up_button.update(self.screen)
        self.volume_down_button.changeColor(mouse_pos)
        self.volume_down_button.update(self.screen)
        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)

    def _draw_credits(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))

        panel_rect = pygame.Rect(0, 0, 560, 320)
        panel_rect.center = (500, 340)
        self._draw_panel(panel_rect)

        credits_text = self.title_font.render("CREDITS", True, settings.ACCENT)
        credits_rect = credits_text.get_rect(center=(500, 250))
        self.screen.blit(credits_text, credits_rect)

        line1 = self.menu_font.render("MADE BY SOHAM", True, settings.TEXT_PRIMARY)
        line1_rect = line1.get_rect(center=(500, 340))
        self.screen.blit(line1, line1_rect)

        line2 = self.small_font.render("BUILT WITH PYTHON AND PYGAME", True, settings.TEXT_MUTED)
        line2_rect = line2.get_rect(center=(500, 400))
        self.screen.blit(line2, line2_rect)

        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)

    def _draw_boost_badge(self, text, pos):
        label = self.label_font.render(text, True, settings.BG_DARK)
        badge_rect = label.get_rect()
        badge_rect.size = (badge_rect.width + 28, badge_rect.height + 14)
        badge_rect.topleft = pos
        pygame.draw.rect(self.screen, settings.WARNING, badge_rect, border_radius=badge_rect.height // 2)
        label_rect = label.get_rect(center=badge_rect.center)
        self.screen.blit(label, label_rect)

    def _draw_endless(self):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        self.enemy.draw(self.screen)
        self.speedup.draw(self.screen)

        panel_rect = pygame.Rect(20, 20, 220, 88)
        self._draw_panel(panel_rect, radius=settings.HUD_RADIUS)
        pad = panel_rect.x + 16

        mode_label = self.label_font.render("ENDLESS", True, settings.ACCENT)
        self.screen.blit(mode_label, (pad, panel_rect.y + 14))

        timer_text = self.small_font.render(f"TIME  {self.elapsed_seconds}s", True, settings.TEXT_PRIMARY)
        self.screen.blit(timer_text, (pad, panel_rect.y + 44))

        if self.player.speed_boost_active:
            seconds_left = max(0, (self.player.speed_boost_end_ticks - pygame.time.get_ticks()) // 1000 + 1)
            self._draw_boost_badge(f"SPEED BOOST {seconds_left}s", (panel_rect.x, panel_rect.bottom + 12))

    def _draw_normal(self):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        if self.enemy.active:
            self.enemy.draw(self.screen)
        for pickup in self.ammo_pickups:
            pickup.draw(self.screen)
        self.speedup.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)

        panel_rect = pygame.Rect(20, 20, 250, 210)
        self._draw_panel(panel_rect, radius=settings.HUD_RADIUS)
        pad = panel_rect.x + 16
        bar_width = panel_rect.width - 32

        mode_label = self.label_font.render("NORMAL", True, settings.ACCENT)
        self.screen.blit(mode_label, (pad, panel_rect.y + 14))

        timer_text = self.small_font.render(f"TIME  {self.elapsed_seconds}s", True, settings.TEXT_PRIMARY)
        self.screen.blit(timer_text, (pad, panel_rect.y + 42))

        stats_text = self.small_font.render(
            f"KILLS {self.kill_count}   WAVE {self.wave_number}", True, settings.TEXT_PRIMARY
        )
        self.screen.blit(stats_text, (pad, panel_rect.y + 74))

        hp_label = self.label_font.render(f"HP  {self.player.hp}/{self.player.max_hp}", True, settings.TEXT_MUTED)
        self.screen.blit(hp_label, (pad, panel_rect.y + 110))
        self._draw_bar((pad, panel_rect.y + 134), (bar_width, 14), self.player.hp / self.player.max_hp, settings.DANGER)

        ammo_label = self.label_font.render(
            f"AMMO  {self.player.ammo}/{self.player.max_ammo}", True, settings.TEXT_MUTED
        )
        self.screen.blit(ammo_label, (pad, panel_rect.y + 156))
        self._draw_bar(
            (pad, panel_rect.y + 180), (bar_width, 14), self.player.ammo / self.player.max_ammo, settings.WARNING
        )

        if self.player.speed_boost_active:
            seconds_left = max(0, (self.player.speed_boost_end_ticks - pygame.time.get_ticks()) // 1000 + 1)
            self._draw_boost_badge(f"SPEED BOOST {seconds_left}s", (panel_rect.x, panel_rect.bottom + 12))

    def _draw_quiz(self, mouse_pos):
        self._draw_normal()

        overlay = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((6, 8, 14, 195))
        self.screen.blit(overlay, (0, 0))

        card_rect = pygame.Rect(0, 0, 620, 520)
        card_rect.center = (500, 420)
        self._draw_panel(card_rect, border=settings.ACCENT)

        header_text = self.font.render(f"WAVE {self.wave_number} CHALLENGE", True, settings.ACCENT)
        header_rect = header_text.get_rect(center=(500, card_rect.y + 60))
        self.screen.blit(header_text, header_rect)

        if self.quiz_feedback is not None:
            color = settings.SUCCESS if self.quiz_last_correct else settings.DANGER
            feedback_text = self.menu_font.render(self.quiz_feedback, True, color)
            feedback_rect = feedback_text.get_rect(center=(500, card_rect.centery))
            self.screen.blit(feedback_text, feedback_rect)
            return

        question_text = self.menu_font.render(self.quiz_question, True, settings.TEXT_PRIMARY)
        question_rect = question_text.get_rect(center=(500, card_rect.y + 150))
        self.screen.blit(question_text, question_rect)

        for button in self.quiz_buttons:
            button.changeColor(mouse_pos)
            button.update(self.screen)

    def _draw_game_over(self, mouse_pos):
        self.screen.blit(self.background_img, (0, 0))
        self.player.draw(self.screen)
        if self.enemy.active:
            self.enemy.draw(self.screen)

        panel_rect = pygame.Rect(0, 0, 480, 300)
        panel_rect.center = (500, 400)
        self._draw_panel(panel_rect, border=settings.DANGER)

        over_text = self.font.render("GAME OVER", True, settings.DANGER)
        over_rect = over_text.get_rect(center=(500, panel_rect.y + 70))
        self.screen.blit(over_text, over_rect)

        stats_y = panel_rect.y + 140
        time_text = self.small_font.render(f"TIME SURVIVED  {self.elapsed_seconds}s", True, settings.TEXT_PRIMARY)
        time_rect = time_text.get_rect(center=(500, stats_y))
        self.screen.blit(time_text, time_rect)

        if self.mode == "normal":
            stats_text = self.small_font.render(
                f"KILLS {self.kill_count}   WAVE {self.wave_number}", True, settings.TEXT_MUTED
            )
            stats_rect = stats_text.get_rect(center=(500, stats_y + 38))
            self.screen.blit(stats_text, stats_rect)

        pulse = (math.sin(pygame.time.get_ticks() / 300) + 1) / 2
        restart_text = self.menu_font.render("PRESS R TO RESTART", True, settings.ACCENT)
        restart_text.set_alpha(int(140 + pulse * 115))
        restart_rect = restart_text.get_rect(center=(500, panel_rect.bottom - 40))
        self.screen.blit(restart_text, restart_rect)

        self.back_button.changeColor(mouse_pos)
        self.back_button.update(self.screen)
