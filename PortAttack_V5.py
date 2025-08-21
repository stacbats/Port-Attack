import pygame
import random
import math

# Initialize Pygame & Mixer
pygame.init()
import os
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

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
    ship_img_big = pygame.transform.scale(ship_img, (ship_img.get_width() * 2, ship_img.get_height() * 2))
    ship_img_small = pygame.transform.scale(ship_img, (int(ship_img.get_width() * 0.75), int(ship_img.get_height() * 0.75)))
    mine_img = pygame.image.load("Mine.png")
    background_img = pygame.image.load("sea.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    seaweed_imgs = [pygame.image.load(f"seaweed{i}.png") for i in range(1, 5)]
except FileNotFoundError as e:
    print(f"error loading asset: {e}")
    pygame.quit()
    seaweed_imgs = [
        pygame.image.load(f"seaweed{i}.png") for i in range(1, 5)
    ]
    exit()

# Load sounds
underwater_sound = pygame.mixer.Sound("underwater.wav")
underwater_explode_sound = pygame.mixer.Sound("underwaterExplode.wav")
ship_explode_sound = pygame.mixer.Sound("ShipExplode.wav")
underwater_sound.set_volume(0.3)
underwater_sound.play(loops=-1)
ship_explode_sound.set_volume(1.0)
underwater_explode_sound.set_volume(1.0)
print("underwaterExplode.wav length:", underwater_explode_sound.get_length())
print("ShipExplode.wav length:", ship_explode_sound.get_length())

# Submarine starting position
sub_x, sub_y = 200, 500
sub_speed = 5
sub_facing_right = False  # Initially facing left

seaweed_positions = [
    (100, HEIGHT - seaweed_imgs[0].get_height() - 37),
    (350, HEIGHT - seaweed_imgs[0].get_height() - 37 - 20),
    (645, HEIGHT - seaweed_imgs[0].get_height() - 37 - 35)
]
seaweed_anim_frame = 0

# Ship starting positions and speeds
ship1_x = WIDTH
ship1_y = 120 - 14 - 30 + 4  # Move top ship down 
ship1_speed = 2

ship2_x = WIDTH + 200
ship2_y = 150   # Move middle ship
ship2_speed = 3

ship3_x = WIDTH + 400
ship3_y = 195  # Move lowest ship 
ship3_speed = 1

# Mine starting position and bobbing parameters
mine_x = WIDTH
mine_y_base = HEIGHT // 2
mine_speed = 2
mine_bob_amplitude = 40
mine_bob_frequency = 0.03

running = True
clock = pygame.time.Clock()

# Torpedo state
torp_active = False
torp_x, torp_y = 0, 0
torp_speed = 3
torp_anim_frame = 0

# Scoring
score = 0
font = pygame.font.SysFont(None, 36)

# Lives
lives = 3
lives_font = pygame.font.SysFont(None, 36)

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

    seaweed_anim_frame += 1
    current_img_index = (seaweed_anim_frame // 10) % 4

    # Check collision with seaweed
    sub_rect = pygame.Rect(sub_x, sub_y, sub_img.get_width(), sub_img.get_height())
    seaweed_rects = [
        pygame.Rect(pos[0], pos[1], seaweed_imgs[current_img_index].get_width(), seaweed_imgs[current_img_index].get_height())
        for pos in seaweed_positions
    ]
    collided_with_seaweed = any(sub_rect.colliderect(rect) for rect in seaweed_rects)
    if collided_with_seaweed:
        effective_sub_speed = max(2, sub_speed - 2)  # Slow down, but not below 2
    else:
        effective_sub_speed = sub_speed

    # Get Keys states
    keys = pygame.key.get_pressed()
    moved = False
    if keys[pygame.K_LEFT]:
        sub_x -= effective_sub_speed
        sub_facing_right = False
        moved = True
    if keys[pygame.K_RIGHT]:
        sub_x += effective_sub_speed
        sub_facing_right = True
        moved = True
    if keys[pygame.K_UP]:
        sub_y -= effective_sub_speed
        moved = True
    if keys[pygame.K_DOWN]:
        sub_y += effective_sub_speed
        moved = True
    # if moved:
    #     submarine_sound.play()

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
                ship_explode_sound.stop()
                ship_explode_sound.play()
                # Scoring: smaller ship = more points
                if i == 0:
                    ship1_x = WIDTH
                    score += 10  # Big ship
                elif i == 1:
                    ship2_x = WIDTH
                    score += 20  # Medium ship
                elif i == 2:
                    ship3_x = WIDTH
                    score += 30  # Small ship

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

    # Move mine left and bob up/down
    mine_x -= mine_speed
    mine_y = mine_y_base + int(mine_bob_amplitude * math.sin(mine_x * mine_bob_frequency))
    if mine_x < -mine_img.get_width():
        mine_x = WIDTH

    # Check collision with mine
    sub_rect = pygame.Rect(sub_x, sub_y, sub_img.get_width(), sub_img.get_height())
    mine_rect = pygame.Rect(mine_x, mine_y, mine_img.get_width(), mine_img.get_height())
    if sub_rect.colliderect(mine_rect):
        lives -= 1
        print(f"Submarine hit a mine! Lives left: {lives}")
        underwater_explode_sound.stop()
        underwater_explode_sound.play()
        # Move mine away after hit
        mine_x = WIDTH
        # Optional: reset submarine position or add invincibility frames
        if lives <= 0:
            print("Game Over!")
            running = False

    # Draw background and images
    screen.blit(background_img, (0, 0))
    screen.blit(ship_img_big, (ship1_x, ship1_y))
    screen.blit(ship_img, (ship2_x, ship2_y))
    screen.blit(ship_img_small, (ship3_x, ship3_y))
    screen.blit(mine_img, (mine_x, mine_y))
    # Animate and draw seaweed
    seaweed_anim_frame += 1
    current_img_index = (seaweed_anim_frame // 10) % 4
    for pos in seaweed_positions:
        screen.blit(seaweed_imgs[current_img_index], pos)
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
    # Draw score
    score_text = font.render(f"Score: {score}", True, (255, 255, 0))
    screen.blit(score_text, (20, 20))
    # Draw lives
    lives_text = lives_font.render(f"Lives: {lives}", True, (255, 0, 0))
    screen.blit(lives_text, (20, 60))

    pygame.display.update()

pygame.quit()