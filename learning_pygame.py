import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("First Pygame")

box = pygame.Rect(100, 100, 50, 50)

speed = 2

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        box.x -= speed
    if keys[pygame.K_RIGHT]:
        box.x += speed
    if keys[pygame.K_UP]:
        box.y -= speed
    if keys[pygame.K_DOWN]:
        box.y += speed

    screen.fill((0, 0, 0))

    pygame.draw.rect(screen, (255, 0, 0), box)

    pygame.display.flip()

pygame.quit()