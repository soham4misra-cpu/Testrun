import pygame

import settings


class Button:
    """A modern rounded-panel button with a hover glow.

    When no custom image is supplied, the button draws its own translucent
    rounded panel (with a soft drop shadow and border) sized to fit the text,
    instead of rendering bare text on the background.
    """

    def __init__(self, image, pos, text_input, font, base_color, hovering_color,
                 padding_x=30, padding_y=16):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input
        self.padding_x = padding_x
        self.padding_y = padding_y
        self.hovering = False

        self.text = self.font.render(self.text_input, True, self.base_color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

        self.panel_mode = self.image is None
        if self.panel_mode:
            self.rect = self.text_rect.inflate(self.padding_x * 2, self.padding_y * 2)
        else:
            self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.panel_mode:
            self._draw_panel(screen)
        else:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def _draw_panel(self, screen):
        shadow = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            shadow, (0, 0, 0, 90), shadow.get_rect(), border_radius=settings.BUTTON_RADIUS
        )
        screen.blit(shadow, (self.rect.x + 2, self.rect.y + 4))

        panel = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        local_rect = panel.get_rect()
        if self.hovering:
            pygame.draw.rect(
                panel, (*settings.ACCENT_DIM, 150), local_rect, border_radius=settings.BUTTON_RADIUS
            )
            pygame.draw.rect(
                panel, settings.ACCENT, local_rect, width=2, border_radius=settings.BUTTON_RADIUS
            )
        else:
            pygame.draw.rect(
                panel, settings.PANEL_BG_SOFT, local_rect, border_radius=settings.BUTTON_RADIUS
            )
            pygame.draw.rect(
                panel, settings.PANEL_BORDER, local_rect, width=2, border_radius=settings.BUTTON_RADIUS
            )
        screen.blit(panel, self.rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        self.hovering = self.rect.collidepoint(position)
        color = self.hovering_color if self.hovering else self.base_color
        self.text = self.font.render(self.text_input, True, color)
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))
