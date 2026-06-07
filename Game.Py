import pygame 
from pygame.math import Vector2
pygame.init()
screen = pygame.display.set_mode((1000,800))
pygame.display.set_caption("Python game")
clock = pygame.time.Clock()

player_img = pygame.image.load('images/Running_Placeholder.png').convert_alpha()
enemy_img = pygame.image.load('images/Ghost_Enemy.png').convert_alpha()

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
    
    direction = player_pos - enemy_pos
    distance = direction.length()
    if distance > 0:
       direction.normalize_ip()
       enemy_pos += direction * enemy_speed
    
    player_rect = player_img.get_rect(topleft=(player_pos.x,player_pos.y))
    enemy_rect = enemy_img.get_rect(topleft=(enemy_pos.x,enemy_pos.y))

    if player_rect.colliderect(enemy_rect):
        print("gameover")
        running = False

    screen.fill((0,0,0))
    screen.blit(player_img, player_rect)
    screen.blit(enemy_img, enemy_rect)
    pygame.display.flip()
    clock.tick(60)
pygame.quit()
