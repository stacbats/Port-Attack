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
charge_img = pygame.image.load("charge.png")
excharge_imgs = [pygame.image.load(f"ExChargeSeries{i}.png") for i in range(1, 5)]
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
    explode_img = pygame.image.load("ExplodeShip1.png")
    mine_explode_img = pygame.image.load("ExplodeShip.png")
    sub2_img = pygame.image.load("sub.png")
    sub2_img_flipped = pygame.transform.flip(sub2_img, True, False)
    start_screen_img = pygame.image.load("startScreen.png")
except FileNotFoundError as e:
    print(f"Error loading asset: {e}")
    pygame.quit()
    exit()

# Explosion state for ships
ship_explosions = [None, None, None]  # Each entry: {'x': int, 'y': int, 'timer': int}
EXPLOSION_DURATION = 20  # frames

# Explosion state for mine
mine_explosion = None  # {'x': int, 'y': int, 'timer': int}

# Load sounds
jaws_sound = pygame.mixer.Sound("jaws.wav")
underwater_sound = pygame.mixer.Sound("underwater.wav")
underwater_explode_sound = pygame.mixer.Sound("underwaterExplode.wav")
ship_explode_sound = pygame.mixer.Sound("ShipExplode.wav")
underwater_sound.set_volume(0.3)
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
ship1_y = 120 - 14 - 30 + 4 + 7  # Move top ship down by 7 more pixels
ship1_speed = 2

ship2_x = -100  # Start off-screen left
ship2_y = 150   # Move middle ship
ship2_speed = 3
ship2_flipped = True  # Ship2 moves right, so use flipped image

ship3_x = WIDTH + 400
ship3_y = 195  # Move lowest ship 
ship3_speed = 1

mine_x = WIDTH
mine_y_base = HEIGHT // 2
mine_speed = 2
mine_bob_amplitude = 40
mine_bob_frequency = 0.03

import time
# Second submarine (sub.png) moving left to right, lower by 100 pixels
sub2_x = -100  # Start off-screen left
sub2_y = mine_y_base + 100
sub2_speed = 4  # Move faster
sub2_active = False
sub2_last_spawn = time.time()
sub2_spawn_interval = 10  # seconds

running = True
clock = pygame.time.Clock()

# Start screen
def show_start_screen():
    # Stop all other sounds and play jaws.wav
    pygame.mixer.stop()
    jaws_sound.play(loops=-1)
    screen.blit(pygame.transform.scale(start_screen_img, (WIDTH, HEIGHT)), (0, 0))
    title_font = pygame.font.SysFont(None, 72)
    info_font = pygame.font.SysFont(None, 48)
    title_text = title_font.render("Port Attack", True, (255, 255, 0))
    info_text = info_font.render("Press ENTER to start", True, (255, 255, 255))
    # Move writing to top right, up by 10 more pixels
    screen.blit(title_text, (WIDTH - title_text.get_width() - 40, 20))
    screen.blit(info_text, (WIDTH - info_text.get_width() - 40, 110))
    pygame.display.update()

# Play again screen
def show_play_again_screen(score, level):
    pygame.mixer.stop()
    # Load and scale PlayAgain.png to cover the whole background
    play_again_img = pygame.image.load("PlayAgain.png")
    play_again_img = pygame.transform.smoothscale(play_again_img, (WIDTH, HEIGHT))
    screen.blit(play_again_img, (0, 0))
    # Shift all text up by 80 pixels
    font_big = pygame.font.SysFont(None, 80)
    font_small = pygame.font.SysFont(None, 48)
    game_over_text = font_big.render("GAME OVER", True, (255, 0, 0))
    score_text = font_small.render(f"Score: {score}", True, (255, 255, 0))
    level_text = font_small.render(f"Level reached: {level}", True, (0, 255, 255))
    play_again_text = font_small.render("Press ENTER to play again", True, (255, 255, 255))
    y_offset = -80
    screen.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, 200 + y_offset))
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 300 + y_offset))
    screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, 360 + y_offset))
    screen.blit(play_again_text, (WIDTH // 2 - play_again_text.get_width() // 2, 440 + y_offset))
    pygame.display.update()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                waiting = False

# Wait for ENTER
show_start_screen()
waiting = True
while waiting:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            # Stop jaws.wav and start underwater sound for gameplay
            jaws_sound.stop()
            underwater_sound.play(loops=-1)
            waiting = False

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
# Charge drop state
charge_active = False
charge_x, charge_y = 0, 0
charge_speed = 5
charge_exploding = False
charge_explosion_frame = 0
charge_explosion_x, charge_explosion_y = 0, 0
charge_boat_index = None
level_flash_timer = 0
level_flash_duration = 60  # frames (1 second at 60 FPS)
# ...existing code...
level = 1
boats_destroyed = 0
mine2_x = WIDTH
mine2_y_base = HEIGHT // 2 + 80
mine2_speed = 2
mine2_bob_amplitude = 40
mine2_bob_frequency = 0.04
level_last = level
level = 1
boats_destroyed = 0
mine2_x = WIDTH
mine2_y_base = HEIGHT // 2 + 80
mine2_speed = 2
mine2_bob_amplitude = 40
mine2_bob_frequency = 0.04
while running:
    # Randomly drop a charge from one boat if none active
    if not charge_active and not charge_exploding and random.random() < 0.005:
        charge_boat_index = random.randint(0, 2)
        charge_x = ship_positions[charge_boat_index][0] + ship_imgs[charge_boat_index].get_width() // 2 - charge_img.get_width() // 2
        charge_y = ship_positions[charge_boat_index][1] + ship_imgs[charge_boat_index].get_height()
        charge_active = True

    # Move charge down if active
    if charge_active:
        charge_y += charge_speed
        # If charge reaches sub's y-level, start explosion
        if charge_y >= sub_y:
            charge_active = False
            charge_exploding = True
            charge_explosion_frame = 0
            charge_explosion_x = charge_x
            charge_explosion_y = charge_y
            # Check collision with sub at explosion start
            excharge_rect = pygame.Rect(charge_explosion_x, charge_explosion_y, excharge_imgs[0].get_width(), excharge_imgs[0].get_height())
            sub_rect = pygame.Rect(sub_x, sub_y, sub_img.get_width(), sub_img.get_height())
            if excharge_rect.colliderect(sub_rect):
                lives -= 1
                underwater_explode_sound.stop()
                underwater_explode_sound.play()
                mine_explosion = {
                    'x': sub_x,
                    'y': sub_y - 60,
                    'timer': EXPLOSION_DURATION
                }
                if lives <= 0:
                    running = False

    # Animate charge explosion
    if charge_exploding:
        charge_explosion_frame += 1
        if charge_explosion_frame > 4 * 10:  # 4 frames, 10 ticks each
            charge_exploding = False
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

    # Detect level change and start flash
    if level != level_last:
        level_flash_timer = level_flash_duration
        level_last = level

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

    # Prevent sub from going above the bottom ship and hiding at the top
    sub_x = max(0, min(sub_x, WIDTH - sub_img.get_width()))
    bottom_ship_y = ship3_y + ship_img.get_height()
    ceiling_y = 275  # Sub cannot go above this y value (adjusted to 275)
    sub_y = max(ceiling_y, min(sub_y, HEIGHT - sub_img.get_height()))

    # Move torpedo if active
    if torp_active:
        torp_y -= torp_speed  # Move up
        torp_anim_frame += 1
        # Stop torpedo 40 pixels below the top ship
        top_ship_limit = ship1_y + 40
        if torp_y < top_ship_limit:
            torp_active = False
            torp_anim_frame = 0

        # --- HIT DETECTION ---
        torp_margin = 4
        ship_margin = 10
        torp_rect = pygame.Rect(
            torp_x - torp_img1.get_width() // 2 + torp_margin,
            torp_y - torp_img1.get_height() // 2 + torp_margin,
            torp_img1.get_width() - 2 * torp_margin,
            torp_img1.get_height() - 2 * torp_margin
        )
        ship_rects = [
            pygame.Rect(ship1_x + ship_margin, ship1_y + ship_margin, ship_img_big.get_width() - 2 * ship_margin, ship_img_big.get_height() - 2 * ship_margin),
            pygame.Rect(ship2_x + ship_margin, ship2_y + ship_margin, ship_img.get_width() - 2 * ship_margin, ship_img.get_height() - 2 * ship_margin),
            pygame.Rect(ship3_x + ship_margin, ship3_y + ship_margin, ship_img_small.get_width() - 2 * ship_margin, ship_img_small.get_height() - 2 * ship_margin)
        ]
        for i, ship_rect in enumerate(ship_rects):
            if torp_rect.colliderect(ship_rect):
                print(f"Hit ship {i+1}!")
                torp_active = False
                torp_anim_frame = 0
                ship_explode_sound.stop()
                ship_explode_sound.play()
                # Center explosion for each ship size
                if i == 0:
                    explosion_x = ship_positions[i][0] + (ship_img_big.get_width() // 2) - (explode_img.get_width() // 2)
                    explosion_y = ship_positions[i][1] + (ship_img_big.get_height() // 2) - (explode_img.get_height() // 2)
                elif i == 1:
                    explosion_x = ship_positions[i][0] + (ship_img.get_width() // 2) - (explode_img.get_width() // 2)
                    explosion_y = ship_positions[i][1] + (ship_img.get_height() // 2) - (explode_img.get_height() // 2)
                else:
                    explosion_x = ship_positions[i][0] + (ship_img_small.get_width() // 2) - (explode_img.get_width() // 2)
                    explosion_y = ship_positions[i][1] + (ship_img_small.get_height() // 2) - (explode_img.get_height() // 2)
                ship_explosions[i] = {
                    'x': explosion_x,
                    'y': explosion_y,
                    'timer': EXPLOSION_DURATION
                }
                boats_destroyed += 1
                # Level up every 10 boats
                if boats_destroyed % 10 == 0:
                    level = min(5, level + 1)
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

    # Level-based ship speed
    speed_boost = 0
    if level >= 4:
        speed_boost = 2
    ship1_x -= ship1_speed + speed_boost
    if ship1_x < -ship_img.get_width():
        ship1_x = WIDTH

    # Middle ship moves right
    ship2_x += ship2_speed + speed_boost
    if ship2_x > WIDTH:
        ship2_x = -ship_img.get_width()

    ship3_x -= ship3_speed + speed_boost
    if ship3_x < -ship_img.get_width():
        ship3_x = WIDTH

    # Level 2+: spawn sub
    current_time = time.time()
    if level >= 2:
        sub2_interval = 10
        if level >= 4:
            sub2_interval = 5
        if not sub2_active and current_time - sub2_last_spawn >= sub2_interval:
            sub2_x = -100
            sub2_active = True
        if sub2_active:
            sub2_x += sub2_speed + (2 if level >= 4 else 0)
            if sub2_x > WIDTH:
                sub2_active = False
                sub2_last_spawn = current_time

    # Always define mine_y to avoid NameError
    mine_y = mine_y_base
    if level >= 3:
        mine_x -= mine_speed + (1 if level >= 4 else 0)
        mine_y = mine_y_base + int(mine_bob_amplitude * math.sin(mine_x * mine_bob_frequency))
        if mine_x < -mine_img.get_width():
            mine_x = WIDTH
    # Level 5: spawn second mine
    mine2_y = mine2_y_base
    if level >= 5:
        mine2_x -= mine2_speed + 1
        mine2_y = mine2_y_base + int(mine2_bob_amplitude * math.sin(mine2_x * mine2_bob_frequency))
        if mine2_x < -mine_img.get_width():
            mine2_x = WIDTH

    # Tighten hit box for mine(s)
    mine_margin = 8
    sub_margin = 10
    sub_rect = pygame.Rect(
        sub_x + sub_margin,
        sub_y + sub_margin,
        sub_img.get_width() - 2 * sub_margin,
        sub_img.get_height() - 2 * sub_margin
    )
    mine_rect = pygame.Rect(
        mine_x + mine_margin,
        mine_y + mine_margin,
        mine_img.get_width() - 2 * mine_margin,
        mine_img.get_height() - 2 * mine_margin
    ) if level >= 3 else None
    mine2_rect = pygame.Rect(
        mine2_x + mine_margin,
        mine2_y + mine_margin,
        mine_img.get_width() - 2 * mine_margin,
        mine_img.get_height() - 2 * mine_margin
    ) if level >= 5 else None
    sub2_margin = 10
    sub2_rect = pygame.Rect(
        sub2_x + sub2_margin,
        sub2_y + sub2_margin,
        sub2_img.get_width() - 2 * sub2_margin,
        sub2_img.get_height() - 2 * sub2_margin
    ) if sub2_active else None

    # Sub1 hits mine
    if level >= 3 and mine_rect and sub_rect.colliderect(mine_rect):
        lives -= 1
        print(f"Submarine hit a mine! Lives left: {lives}")
        underwater_explode_sound.stop()
        underwater_explode_sound.play()
        # Add mine explosion state
        mine_explosion = {
            'x': mine_x,
            'y': mine_y - 60,  # Shift explosion up more
            'timer': EXPLOSION_DURATION
        }
        # Move mine away after hit
        mine_x = WIDTH
        if lives <= 0:
            print("Game Over!")
            running = False
    # Sub1 hits second mine
    if level >= 5 and mine2_rect and sub_rect.colliderect(mine2_rect):
        lives -= 1
        print(f"Submarine hit second mine! Lives left: {lives}")
        underwater_explode_sound.stop()
        underwater_explode_sound.play()
        mine_explosion = {
            'x': mine2_x,
            'y': mine2_y - 60,
            'timer': EXPLOSION_DURATION
        }
        mine2_x = WIDTH
        if lives <= 0:
            print("Game Over!")
            running = False
    # Sub1 hits sub2
    if sub2_active and sub_rect.colliderect(sub2_rect):
        lives -= 1
        print(f"Submarine hit sub.png! Lives left: {lives}")
        underwater_explode_sound.stop()
        underwater_explode_sound.play()
        # Add explosion at collision point
        mine_explosion = {
            'x': sub_x,
            'y': sub_y - 60,
            'timer': EXPLOSION_DURATION
        }
        # Move sub2 away after hit
        sub2_active = False
        sub2_last_spawn = time.time()
        if lives <= 0:
            print("Game Over!")
            running = False

    # Draw background and images
    screen.blit(background_img, (0, 0))
    # Draw ships and explosions
    ship_positions = [(ship1_x, ship1_y), (ship2_x, ship2_y), (ship3_x, ship3_y)]
    ship_imgs = [ship_img_big, ship_img, ship_img_small]
    for i in range(3):
        if ship_explosions[i]:
            # Draw explosion if timer > 0
            if ship_explosions[i]['timer'] > 0:
                screen.blit(explode_img, (ship_explosions[i]['x'], ship_explosions[i]['y']))
                ship_explosions[i]['timer'] -= 1
            else:
                ship_explosions[i] = None
        else:
            # Flip ship2 image when moving right
            if i == 1:
                screen.blit(pygame.transform.flip(ship_img, True, False), ship_positions[i])
            else:
                screen.blit(ship_imgs[i], ship_positions[i])

    # Draw falling charge
    if charge_active:
        screen.blit(charge_img, (charge_x, charge_y))
    # Draw charge explosion animation
    if charge_exploding:
        frame = min(charge_explosion_frame // 10, 3)
        screen.blit(excharge_imgs[frame], (charge_explosion_x, charge_explosion_y))

    # Draw second submarine (sub.png) at mine's level if active
    if sub2_active:
        screen.blit(sub2_img_flipped, (sub2_x, sub2_y))
    # Draw mine and explosion
    if level >= 3:
        if mine_explosion:
            if mine_explosion['timer'] > 0:
                screen.blit(mine_explode_img, (mine_explosion['x'], mine_explosion['y']))
                mine_explosion['timer'] -= 1
            else:
                mine_explosion = None
        else:
            screen.blit(mine_img, (mine_x, mine_y))
    if level >= 5:
        screen.blit(mine_img, (mine2_x, mine2_y))
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
    # Draw score, lives, and level
    score_text = font.render(f"Score: {score}", True, (255, 255, 0))
    lives_text = lives_font.render(f"Lives: {lives}", True, (255, 0, 0))
    level_text = font.render(f"Level: {level}", True, (0, 255, 255))
    total_width = score_text.get_width() + 40 + lives_text.get_width() + 40 + level_text.get_width()
    start_x = WIDTH // 2 - total_width // 2
    screen.blit(score_text, (start_x, 20))
    screen.blit(lives_text, (start_x + score_text.get_width() + 40, 20))
    screen.blit(level_text, (start_x + score_text.get_width() + 40 + lives_text.get_width() + 40, 20))

    # Flash level change message
    if level_flash_timer > 0:
        flash_font = pygame.font.SysFont(None, 120)
        flash_text = flash_font.render(f"LEVEL {level}", True, (255, 255, 0))
        flash_bg = pygame.Surface((flash_text.get_width() + 40, flash_text.get_height() + 40))
        flash_bg.set_alpha(180)
        flash_bg.fill((0, 0, 0))
        center_x = WIDTH // 2 - flash_text.get_width() // 2
        center_y = HEIGHT // 2 - flash_text.get_height() // 2
        screen.blit(flash_bg, (center_x - 20, center_y - 20))
        screen.blit(flash_text, (center_x, center_y))
        level_flash_timer -= 1

    pygame.display.update()

show_play_again_screen(score, level)
pygame.quit()