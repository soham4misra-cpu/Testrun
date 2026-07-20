import pygame 
from pygame.math import Vector2
from button import Button
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1000,800))
pygame.display.set_caption("Python game")
clock = pygame.time.Clock()
start_ticks = pygame.time.get_ticks()
small_font = pygame.font.Font(None, 40)
font = pygame.font.Font(None, 60)
title_font = pygame.font.Font(None, 100)
menu_font = pygame.font.Font(None, 60)
game_state = "menu"
background_img = pygame.image.load('images/Background.jpg').convert()
background_img = pygame.transform.scale(background_img, (1000,800))
menu_img = pygame.image.load('images/Title_Screen.jpg').convert()
menu_img = pygame.transform.scale(menu_img, (1000,800))

player_img = pygame.image.load('images/Running_Placeholder.png').convert_alpha()
enemy_img = pygame.image.load('images/Ghost_Enemy.png').convert_alpha()
elapsed_seconds = 0

pygame.mixer.music.load('audios/Backgroundmusic.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

player_pos = Vector2(400,300)
player_speed = 5

enemy_pos = Vector2(100,100)
enemy_speed = 2

font = pygame.font.Font(None, 60)
game_over = False

start_button = Button(
    image = None, 
    pos = (500, 280),
    text_input = "START",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)

options_button = Button(
    image = None, 
    pos = (500, 380),
    text_input = "OPTIONS",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)

credits_button = Button(
    image = None, 
    pos = (500, 480),
    text_input = "CREDITS",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)

back_button = Button(
    image = None, 
    pos = (100, 60),
    text_input = "BACK",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)
music_volume = 0.5
volumeUP_button = Button(
    image = None, 
    pos = (600, 480),
    text_input = "+",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)
volumeDOWN_button = Button(
    image = None, 
    pos = (400, 480),
    text_input = "-",
    font = menu_font,
    base_color = "White",
    hovering_color = (0, 0, 139)
)
def reset_game():
    global player_pos, enemy_pos, game_over, start_ticks, elapsed_seconds, game_state
    player_pos = Vector2(400,300)
    enemy_pos = Vector2(100,100)
    game_over = False
    start_ticks = pygame.time.get_ticks()
    elapsed_seconds = 0
    game_state = "playing"

running = True

while running:
    mouse_pos = pygame.mouse.get_pos()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if game_state == "menu":
                if start_button.checkForInput(mouse_pos):
                    reset_game()
                elif options_button.checkForInput(mouse_pos):
                    game_state = "options"
                elif credits_button.checkForInput(mouse_pos):
                    game_state = "credits"
            elif game_state == "options":
                if volumeUP_button.checkForInput(mouse_pos):
                    music_volume = min(1.0, music_volume + 0.1)
                    pygame.mixer.music.set_volume(music_volume)
                elif volumeDOWN_button.checkForInput(mouse_pos):
                    music_volume = min(0.0, music_volume - 0.1)
                    pygame.mixer.music.set_volume(music_volume)
                elif back_button.checkForInput(mouse_pos):
                    game_state = "menu"  
            elif game_state == "credits" or game_state == "game_over":
                if back_button.checkForInput(mouse_pos):
                    game_state = "menu"
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_r: 
                reset_game()
    if game_state == "playing":
        keys = pygame.key.get_pressed()
        if not game_over:
            if keys[pygame.K_LEFT]:
                player_pos.x -= player_speed
            if keys[pygame.K_RIGHT]:
                player_pos.x += player_speed
            if keys[pygame.K_UP]:
                player_pos.y -= player_speed
            if keys[pygame.K_DOWN]:
                player_pos.y += player_speed
            
            if player_pos.x < -player_img.get_width():
                player_pos.x = screen.get_width()
            elif player_pos.x > screen.get_width():
                player_pos.x = -player_img.get_width()

            if player_pos.y < -player_img.get_height():
                player_pos.y = screen.get_height()
            elif player_pos.y > screen.get_height():
                player_pos.y = -player_img.get_height()

            direction = player_pos - enemy_pos
            distance = direction.length()
            if distance > 0:
                direction.normalize_ip()
                enemy_pos += direction * enemy_speed
            elapsed_seconds = (pygame.time.get_ticks() - start_ticks) // 1000
        
        player_rect = player_img.get_rect(topleft=(player_pos.x,player_pos.y))
        enemy_rect = enemy_img.get_rect(topleft=(enemy_pos.x,enemy_pos.y))
        player_rect.inflate_ip(-10,-10)
        enemy_rect.inflate_ip(-10,-10)

        if not game_over and player_rect.colliderect(enemy_rect):
            game_over = True
            game_state = "game_over"
    if game_state == "menu":
        screen.blit(menu_img, (0,0))
        for button in [start_button, options_button, credits_button]:
            button.changeColor(mouse_pos)
            button.update(screen)
    elif game_state == "options":
        screen.blit(background_img, (0,0))
        options_text = title_font.render("OPTIONS", True, (255, 255, 255))
        options_rect = options_text.get_rect(center = (500, 140))
        volume_label = menu_font.render("MUSIC VOLUME", True, (255, 255, 255))
        screen.blit(volume_label, (330, 320))
        volume_percent = menu_font.render(f"{int(music_volume * 100)}%", True, (255, 255, 255))
        volume_rect = volume_percent.get_rect(center = (500, 480))
        screen.blit(volume_percent, volume_rect)
        #screen.blit(options_text, options_rect)
        #info1 = menu_font.render("INFO", True, (255, 255, 255))
        #info2 = menu_font.render("INFO2", True, (255, 255, 255))
        #screen.blit(info1, (220, 320))
       # screen.blit(info2, (190, 390))
        volumeUP_button.changeColor(mouse_pos)
        volumeUP_button.update(screen)
        volumeDOWN_button.changeColor(mouse_pos)
        volumeDOWN_button.update(screen)
        back_button.changeColor(mouse_pos)
        back_button.update(screen)

    elif game_state == "credits":
        screen.blit(background_img, (0,0))
        credits_text = title_font.render("CREDITS", True, (255, 255, 255))
        credits_rect = options_text.get_rect(center = (500, 140))
        screen.blit(credits_text, credits_rect)
        line1 = menu_font.render("MADE BY SOHAM", True, (255, 255, 255))
        line2 = menu_font.render("BUILT WITH PYTHON AND PYGAME.", True, (255, 255, 255))
        screen.blit(line1, (220, 320))
        screen.blit(line2, (190, 390))
        back_button.changeColor(mouse_pos)
        back_button.update(screen)
    elif game_state == "playing":
        screen.blit(background_img, (0,0))
        screen.blit(player_img, player_rect)
        screen.blit(enemy_img, enemy_rect)
        
        timer_text = small_font.render(f"time: {elapsed_seconds} ", True, (255, 255, 255))
        screen.blit(timer_text, (20, 20))
    elif game_state == "game_over":
        screen.blit(background_img, (0,0))
        screen.blit(player_img, player_rect)
        screen.blit(enemy_img, enemy_rect)
  
        timer_text = small_font.render(f"time: {elapsed_seconds} ", True, (255, 255, 255))
        screen.blit(timer_text, (20, 20))
        over_text = font.render("game over", True, (255, 255, 255))
        restart_text = menu_font.render("press R to restart", True, (255, 255, 255))
        screen.blit(over_text, (350, 280))
        screen.blit(restart_text, (270, 360))
        back_button.changeColor(mouse_pos)
        back_button.update(screen)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
