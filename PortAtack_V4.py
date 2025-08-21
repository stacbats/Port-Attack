import pygame
import random

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()

# Screen Dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PortAttack_V4")

# Load and Scale assets
try:
    sub_img = pygame.image.load("sub1.png")
    sub_img_flipped = pygame.transform.flip(sub_img, True, False)
    torp_img1 = pygame.image.load("torp.png")
    torp_img2 = pygame.image.load("torp2.png")
    ship_img = pygame.image.load("ship.png")
    background_img = pygame.image.load("sea.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
except FileNotFoundError as e:
    print(f"error loading asset: {e}")
    pygame.quit()
    exit()

# Submarine starting position
sub_x, sub_y = 200, 500
sub_speed = 5
sub_facing_right = False  # Initially facing left

# Ship starting positions and speeds
ship1_x = WIDTH
ship1_y = 120
ship1_speed = 2

ship2_x = WIDTH + 200
ship2_y = 180
ship2_speed = 3

ship3_x = WIDTH + 400
ship3_y = 240
ship3_speed = 1

running = True
clock = pygame.time.Clock()

# Torpedo state
torp_active = False
torp_x, torp_y = 0, 0
torp_speed = 3
torp_anim_frame = 0

# Main game loop
while running:
    clock.tick(60)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # Fire torpedo on space bar
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if not torp_active:
                torp_active = True
                # Launch from middle-top of sub
                torp_x = sub_x + sub_img.get_width() // 2
                torp_y = sub_y

    # Get Keys states
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        sub_x -= sub_speed
        sub_facing_right = False
    if keys[pygame.K_RIGHT]:
        sub_x += sub_speed
        sub_facing_right = True
    if keys[pygame.K_UP]:
        sub_y -= sub_speed
    if keys[pygame.K_DOWN]:
        sub_y += sub_speed

    # Keep submarine within screen bounds
    sub_x = max(0, min(sub_x, WIDTH - sub_img.get_width()))
    sub_y = max(0, min(sub_y, HEIGHT - sub_img.get_height()))

    # Move torpedo if active
    if torp_active:
        torp_y -= torp_speed  # Move up
        torp_anim_frame += 1
        # Deactivate if off screen or near top
        if torp_y < 100:
            torp_active = False
            torp_anim_frame = 0

        # --- HIT DETECTION ---
        torp_rect = pygame.Rect(
            torp_x - torp_img1.get_width() // 2,
            torp_y - torp_img1.get_height() // 2,
            torp_img1.get_width(),
            torp_img1.get_height()
        )
        ship_rects = [
            pygame.Rect(ship1_x, ship1_y, ship_img.get_width(), ship_img.get_height()),
            pygame.Rect(ship2_x, ship2_y, ship_img.get_width(), ship_img.get_height()),
            pygame.Rect(ship3_x, ship3_y, ship_img.get_width(), ship_img.get_height())
        ]
        for i, ship_rect in enumerate(ship_rects):
            if torp_rect.colliderect(ship_rect):
                print(f"Hit ship {i+1}!")
                torp_active = False
                torp_anim_frame = 0
                # Optionally, reset ship position
                if i == 0:
                    ship1_x = WIDTH
                elif i == 1:
                    ship2_x = WIDTH
                elif i == 2:
                    ship3_x = WIDTH

    # Move ships left
    ship1_x -= ship1_speed
    if ship1_x < -ship_img.get_width():
        ship1_x = WIDTH

    ship2_x -= ship2_speed
    if ship2_x < -ship_img.get_width():
        ship2_x = WIDTH

    ship3_x -= ship3_speed
    if ship3_x < -ship_img.get_width():
        ship3_x = WIDTH

    # Draw background and images
    screen.blit(background_img, (0, 0))
    screen.blit(ship_img, (ship1_x, ship1_y))
    screen.blit(ship_img, (ship2_x, ship2_y))
    screen.blit(ship_img, (ship3_x, ship3_y))
    # Draw torpedo if active
    if torp_active:
        if (torp_anim_frame // 5) % 2 == 0:
            torp_img = torp_img1
        else:
            torp_img = torp_img2
        screen.blit(torp_img, (torp_x - torp_img.get_width() // 2, torp_y - torp_img.get_height() // 2))
    # Draw submarine facing correct direction
    if sub_facing_right:
        screen.blit(sub_img_flipped, (sub_x, sub_y))
    else:
        screen.blit(sub_img, (sub_x, sub_y))

    pygame.display.update()

pygame.quit()