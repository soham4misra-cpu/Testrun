import pygame 
from pygame.math import Vector2
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((1000,800))
pygame.display.set_caption("Python game")
clock = pygame.time.Clock()
background_img = pygame.image.load('images/Background.jpg').convert()
background_img = pygame.transform.scale(background_img, (1000,800))

player_img = pygame.image.load('images/Running_Placeholder.png').convert_alpha()
enemy_img = pygame.image.load('images/Ghost_Enemy.png').convert_alpha()

pygame.mixer.music.load('audios/Backgroundmusic.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)

player_pos = Vector2(400,300)
player_speed = 5

enemy_pos = Vector2(100,100)
enemy_speed = 2

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    keys = pygame.key.get_pressed()
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
    
    player_rect = player_img.get_rect(topleft=(player_pos.x,player_pos.y))
    enemy_rect = enemy_img.get_rect(topleft=(enemy_pos.x,enemy_pos.y))
    player_rect.inflate_ip(-10,-10)
    enemy_rect.inflate_ip(-10,-10)

    if player_rect.colliderect(enemy_rect):
        print("gameover")
        running = False

    screen.fill((0,0,0))
    screen.blit(player_img, player_rect)
    screen.blit(enemy_img, enemy_rect)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
