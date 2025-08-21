
import pygame
import random
import math
import time

# Initialize Pygame & Mixer
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

# Screen Dimensions
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("DingyAttack_V1")

# Load and Scale assets
    # ...existing code...
try:
    sub_img = pygame.image.load("sub1.png")
    sub_img_flipped = pygame.transform.flip(sub_img, True, False)
    torp_img1 = pygame.image.load("torp.png")
    torp_img2 = pygame.image.load("torp2.png")
    ship_img = pygame.image.load("dingy.png")
    mine_img = pygame.image.load("Mine.png")
    background_img = pygame.image.load("sea.png")
    background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))
    seaweed_imgs = [pygame.image.load(f"seaweed{i}.png") for i in range(1, 5)]
    explode_img = pygame.image.load("ExplodeShip1.png")
    mine_explode_img = pygame.image.load("ExplodeShip.png")
    sub2_img = pygame.image.load("sub.png")
    sub2_img_flipped = pygame.transform.flip(sub2_img, True, False)
    start_screen_img = pygame.image.load("startScreen.png")
    play_again_img = pygame.image.load("PlayAgain.png")
    suicide_img = pygame.image.load("suicideman.png")
except FileNotFoundError as e:
    print(f"Error loading asset: {e}")
    pygame.quit()
    exit()

# Sounds
underwater_sound = pygame.mixer.Sound("underwater.wav")
underwater_explode_sound = pygame.mixer.Sound("underwaterExplode.wav")
ship_explode_sound = pygame.mixer.Sound("ShipExplode.wav")
ahkbar_sound = pygame.mixer.Sound("Ahkbar.wav")
underwater_sound.set_volume(0.3)
underwater_sound.play(loops=-1)
ship_explode_sound.set_volume(1.0)
underwater_explode_sound.set_volume(1.0)

clock = pygame.time.Clock()

# Game state variables
def reset_game_state():
    global level, boats_destroyed, mine2_x, mine2_y_base, mine2_speed, mine2_bob_amplitude, mine2_bob_frequency
    level = 1
    boats_destroyed = 0
    mine2_x = WIDTH
    mine2_y_base = HEIGHT // 2 + 80
    mine2_speed = 2
    mine2_bob_amplitude = 40
    mine2_bob_frequency = 0.04
    global suicide_active, suicide_x, suicide_y, suicide_speed
    suicide_active = False
    suicide_x, suicide_y = 0, 0
    suicide_speed = 5
    global torp_active, torp_x, torp_y, torp_speed, torp_anim_frame, score, font, lives, lives_font, sub_speed, sub_facing_right, sub_x, sub_y, seaweed_anim_frame
    global sub2_x, sub2_y, sub2_speed, sub2_active, sub2_last_spawn, sub2_spawn_interval
    global ship1_x, ship1_y, ship1_speed, ship2_x, ship2_y, ship2_speed, ship2_flipped, ship3_x, ship3_y, ship3_speed
    global mine_x, mine_y_base, mine_speed, mine_bob_amplitude, mine_bob_frequency, ship_explosions, EXPLOSION_DURATION, mine_explosion, seaweed_positions

    torp_active = False
    torp_x, torp_y = 0, 0
    torp_speed = 3
    torp_anim_frame = 0
    score = 0
    font = pygame.font.SysFont(None, 36)
    lives = 3
    lives_font = pygame.font.SysFont(None, 36)
    sub_speed = 5
    sub_facing_right = False
    sub_x, sub_y = 200, 500
    seaweed_anim_frame = 0
    sub2_x = -100
    sub2_y = HEIGHT // 2 + 100
    sub2_speed = 4
    sub2_active = False
    sub2_last_spawn = time.time()
    sub2_spawn_interval = 10
    ship1_x = WIDTH
    ship1_y = 120 - 14 - 30 + 4
    ship1_speed = 2
    ship2_x = -100
    ship2_y = 150
    ship2_speed = 3
    ship2_flipped = True
    ship3_x = WIDTH + 400
    ship3_y = 195
    ship3_speed = 1
    mine_x = WIDTH
    mine_y_base = HEIGHT // 2
    mine_speed = 2
    mine_bob_amplitude = 40
    mine_bob_frequency = 0.03
    ship_explosions = [None, None, None]
    EXPLOSION_DURATION = 20
    mine_explosion = None
    seaweed_positions = [
        (100, HEIGHT - seaweed_imgs[0].get_height() - 37),
        (350, HEIGHT - seaweed_imgs[0].get_height() - 37 - 20),
        (645, HEIGHT - seaweed_imgs[0].get_height() - 37 - 35)
    ]

def show_start_screen():
    screen.blit(pygame.transform.scale(start_screen_img, (WIDTH, HEIGHT)), (0, 0))
    title_font = pygame.font.SysFont(None, 72)
    info_font = pygame.font.SysFont(None, 48)
    name_font = pygame.font.SysFont(None, 48)
    title_text = title_font.render("Dingy Attack", True, (255, 255, 0))
    info_text = info_font.render("Press ENTER to start", True, (255, 255, 255))
    name_text = name_font.render("by Stacy Bates", True, (255, 255, 255))
    # Align horizontally with info_text, but keep near bottom
    name_x = WIDTH - name_text.get_width() - 40
    name_y = HEIGHT - name_text.get_height() - 40
    screen.blit(title_text, (WIDTH - title_text.get_width() - 40, 20))
    screen.blit(info_text, (WIDTH - info_text.get_width() - 40, 110))
    screen.blit(name_text, (name_x, name_y))
    pygame.display.update()

def show_play_again_screen():
    screen.blit(pygame.transform.scale(play_again_img, (WIDTH, HEIGHT)), (0, 0))
    font_big = pygame.font.SysFont(None, 72)
    font_small = pygame.font.SysFont(None, 48)
    text1 = font_big.render("Game Over!", True, (255, 0, 0))
    text2 = font_small.render("Press ENTER to play again", True, (255, 255, 255))
    text3 = font_small.render("Press ESC to quit", True, (255, 255, 255))
    offset = -200
    screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 - 120 + offset + 40))
    screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, HEIGHT // 2 + offset))
    screen.blit(text3, (WIDTH // 2 - text3.get_width() // 2, HEIGHT // 2 + 60 + offset))
    pygame.display.update()

def main():
    global level, boats_destroyed, mine2_x, mine2_y_base, mine2_speed, mine2_bob_amplitude, mine2_bob_frequency

    while True:
        intro_waiting = True
        while intro_waiting:
            show_start_screen()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    intro_waiting = False

        reset_game_state()
        running = True
        while running:
            # Declare all game state variables as global so they can be updated
            global torp_active, torp_x, torp_y, torp_speed, torp_anim_frame, score, font, lives, lives_font, sub_speed, sub_facing_right, sub_x, sub_y, seaweed_anim_frame
            global sub2_x, sub2_y, sub2_speed, sub2_active, sub2_last_spawn, sub2_spawn_interval
            global ship1_x, ship1_y, ship1_speed, ship2_x, ship2_y, ship2_speed, ship2_flipped, ship3_x, ship3_y, ship3_speed
            global mine_x, mine_y_base, mine_speed, mine_bob_amplitude, mine_bob_frequency, ship_explosions, EXPLOSION_DURATION, mine_explosion, seaweed_positions
            global suicide_img, suicide_active, suicide_x, suicide_y, suicide_speed

            clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    if not torp_active:
                        torp_active = True
                        torp_x = sub_x + sub_img.get_width() // 2
                        torp_y = sub_y

            seaweed_anim_frame += 1
            current_img_index = (seaweed_anim_frame // 10) % 4
            # Tighten hit box for sub
            sub_margin = 10
            sub_rect = pygame.Rect(
                sub_x + sub_margin,
                sub_y + sub_margin,
                sub_img.get_width() - 2 * sub_margin,
                sub_img.get_height() - 2 * sub_margin
            )
            seaweed_rects = [
                pygame.Rect(
                    pos[0] + 5,
                    pos[1] + 5,
                    seaweed_imgs[current_img_index].get_width() - 10,
                    seaweed_imgs[current_img_index].get_height() - 10
                )
                for pos in seaweed_positions
            ]
            collided_with_seaweed = any(sub_rect.colliderect(rect) for rect in seaweed_rects)
            if collided_with_seaweed:
                effective_sub_speed = max(2, sub_speed - 2)
            else:
                effective_sub_speed = sub_speed
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
            sub_x = max(0, min(sub_x, WIDTH - sub_img.get_width()))
            # Prevent sub from going above the bottom ship
            bottom_ship_y = ship3_y + ship_img.get_height()
            sub_y = max(bottom_ship_y, min(sub_y, HEIGHT - sub_img.get_height()))

            if torp_active:
                torp_y -= torp_speed
                torp_anim_frame += 1
                # Stop torpedo 40 pixels below the top ship (10 pixels higher than before)
                top_ship_limit = ship1_y + 40
                if torp_y < top_ship_limit:
                    torp_active = False
                    torp_anim_frame = 0
                # Tighten hit box for torpedo
                torp_margin = 4
                ship_margin = 10
                torp_rect = pygame.Rect(
                    torp_x - torp_img1.get_width() // 2 + torp_margin,
                    torp_y - torp_img1.get_height() // 2 + torp_margin,
                    torp_img1.get_width() - 2 * torp_margin,
                    torp_img1.get_height() - 2 * torp_margin
                )
                ship_rects = [
                    pygame.Rect(ship1_x + ship_margin, ship1_y + ship_margin, ship_img.get_width() - 2 * ship_margin, ship_img.get_height() - 2 * ship_margin),
                    pygame.Rect(ship2_x + ship_margin, ship2_y + ship_margin, ship_img.get_width() - 2 * ship_margin, ship_img.get_height() - 2 * ship_margin),
                    pygame.Rect(ship3_x + ship_margin, ship3_y + ship_margin, ship_img.get_width() - 2 * ship_margin, ship_img.get_height() - 2 * ship_margin)
                ]
                for i, ship_rect in enumerate(ship_rects):
                    if torp_rect.colliderect(ship_rect):
                        torp_active = False
                        torp_anim_frame = 0
                        ship_explode_sound.stop()
                        ship_explode_sound.play()
                        ship_explosions[i] = {
                            'x': ship_rect.x,
                            'y': ship_rect.y - 60,
                            'timer': EXPLOSION_DURATION
                        }
                        # Spawn suicide man from the hit boat before resetting its position
                        suicide_active = True
                        suicide_x = ship_rect.x + ship_img.get_width() // 2 - suicide_img.get_width() // 2
                        suicide_y = ship_rect.y + ship_img.get_height()
                        ahkbar_sound.stop()
                        ahkbar_sound.play()
                        boats_destroyed += 1
                        # Level up every 10 boats
                        if boats_destroyed % 10 == 0:
                            level = min(5, level + 1)
                        if i == 0:
                            ship1_x = WIDTH
                            score += 10
                        elif i == 1:
                            ship2_x = WIDTH
                            score += 20
                        elif i == 2:
                            ship3_x = WIDTH
                            score += 30

            # Level-based ship speed
            speed_boost = 0
            if level >= 4:
                speed_boost = 2
            ship1_x -= ship1_speed + speed_boost
            if ship1_x < -ship_img.get_width():
                ship1_x = WIDTH
            ship2_x += ship2_speed + speed_boost
            if ship2_x > WIDTH:
                ship2_x = -ship_img.get_width()
            ship3_x -= ship3_speed + speed_boost
            if ship3_x < -ship_img.get_width():
                ship3_x = WIDTH

            current_time = time.time()
            # Level 2+: spawn sub
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

            # Level 3+: spawn mine
            if level >= 3:
                mine_x -= mine_speed + (1 if level >= 4 else 0)
                mine_y = mine_y_base + int(mine_bob_amplitude * math.sin(mine_x * mine_bob_frequency))
                if mine_x < -mine_img.get_width():
                    mine_x = WIDTH
            # Level 5: spawn second mine
            if level >= 5:
                mine2_x -= mine2_speed + 1
                mine2_y = mine2_y_base + int(mine2_bob_amplitude * math.sin(mine2_x * mine2_bob_frequency))
                if mine2_x < -mine_img.get_width():
                    mine2_x = WIDTH

            # Tighten hit box for mine(s)
            mine_margin = 8
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

            if level >= 3 and mine_rect and sub_rect.colliderect(mine_rect):
                lives -= 1
                underwater_explode_sound.stop()
                underwater_explode_sound.play()
                mine_explosion = {
                    'x': mine_x,
                    'y': mine_y - 60,
                    'timer': EXPLOSION_DURATION
                }
                mine_x = WIDTH
                if lives <= 0:
                    running = False
            if level >= 5 and mine2_rect and sub_rect.colliderect(mine2_rect):
                lives -= 1
                underwater_explode_sound.stop()
                underwater_explode_sound.play()
                mine_explosion = {
                    'x': mine2_x,
                    'y': mine2_y - 60,
                    'timer': EXPLOSION_DURATION
                }
                mine2_x = WIDTH
                if lives <= 0:
                    running = False

            if sub2_active and sub_rect.colliderect(sub2_rect):
                lives -= 1
                underwater_explode_sound.stop()
                underwater_explode_sound.play()
                mine_explosion = {
                    'x': sub_x,
                    'y': sub_y - 60,
                    'timer': EXPLOSION_DURATION
                }
                sub2_active = False
                sub2_last_spawn = time.time()
                if lives <= 0:
                    running = False

            screen.blit(background_img, (0, 0))
            ship_positions = [(ship1_x, ship1_y), (ship2_x, ship2_y), (ship3_x, ship3_y)]
            for i in range(3):
                if ship_explosions[i]:
                    if ship_explosions[i]['timer'] > 0:
                        screen.blit(explode_img, (ship_explosions[i]['x'], ship_explosions[i]['y']))
                        ship_explosions[i]['timer'] -= 1
                    else:
                        ship_explosions[i] = None
                else:
                    if i == 1:
                        screen.blit(pygame.transform.flip(ship_img, True, False), ship_positions[i])
                    else:
                        screen.blit(ship_img, ship_positions[i])
            # Draw mines
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

            # Animate suicide man falling
            if suicide_active:
                suicide_y += suicide_speed
                screen.blit(suicide_img, (suicide_x, suicide_y))
                # Check collision with sub
                sub_rect = pygame.Rect(sub_x, sub_y, sub_img.get_width(), sub_img.get_height())
                # Tighten hit box for suicide man
                suicide_margin = 8
                suicide_rect = pygame.Rect(
                    suicide_x + suicide_margin,
                    suicide_y + suicide_margin,
                    suicide_img.get_width() - 2 * suicide_margin,
                    suicide_img.get_height() - 2 * suicide_margin
                )
                if sub_rect.colliderect(suicide_rect):
                    lives -= 1
                    underwater_explode_sound.stop()
                    underwater_explode_sound.play()
                    mine_explosion = {
                        'x': sub_x,
                        'y': sub_y - 60,
                        'timer': EXPLOSION_DURATION
                    }
                    suicide_active = False
                elif suicide_y > HEIGHT:
                    suicide_active = False
            if sub2_active:
                screen.blit(sub2_img_flipped, (sub2_x, sub2_y))
            seaweed_anim_frame += 1
            current_img_index = (seaweed_anim_frame // 10) % 4
            for pos in seaweed_positions:
                screen.blit(seaweed_imgs[current_img_index], pos)
            if torp_active:
                if (torp_anim_frame // 5) % 2 == 0:
                    torp_img = torp_img1
                else:
                    torp_img = torp_img2
                screen.blit(torp_img, (torp_x - torp_img.get_width() // 2, torp_y - torp_img.get_height() // 2))
            if sub_facing_right:
                screen.blit(sub_img_flipped, (sub_x, sub_y))
            else:
                screen.blit(sub_img, (sub_x, sub_y))
            score_text = font.render(f"Score: {score}", True, (255, 255, 0))
            lives_text = lives_font.render(f"Lives: {lives}", True, (255, 0, 0))
            level_text = font.render(f"Level: {level}", True, (0, 255, 255))
            total_width = score_text.get_width() + 40 + lives_text.get_width() + 40 + level_text.get_width()
            start_x = WIDTH // 2 - total_width // 2
            screen.blit(score_text, (start_x, 20))
            screen.blit(lives_text, (start_x + score_text.get_width() + 40, 20))
            screen.blit(level_text, (start_x + score_text.get_width() + 40 + lives_text.get_width() + 40, 20))
            pygame.display.update()

        # End of main game loop, show play again screen
        show_play_again_screen()
        play_again_waiting = True
        while play_again_waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        play_again_waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        exit()

if __name__ == "__main__":
    main()