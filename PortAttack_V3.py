import pygame
import random

# initialize Pygame & Mixer
pygame.init()
pygame.mixer.init()


# Screen Dimensions
WIDTH, HEIGHT = 800,600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PortAttack_V3")

# Load and Scale assets
try:
    sub_img = pygame.image.load("sub1.png")
    sub_img_flipped = pygame.transform.flip(sub_img, True, False) # Flipped image for left movement
    torp_img1 = pygame.image.load("torp.png")
    torp_img2 = pygame.image.load("torp2.png")
    ship_img = pygame.image.load("ship.png")
    background_img = pygame.image.load("sea.png")
    background_img = pygame.transform.scale(background_img,(WIDTH, HEIGHT))
    
except FileNotFoundError as e:
    print(f"error loading asset: {e}")
    pygame.quit()
    exit()
    
# Submarine starting position
sub_x, sub_y = 200, 500
sub_speed = 5
sub_facing_right = False                        # Initially facing left
    
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
                torp_y = sub_y  # Start at the top of the sub


    # Get Keys states
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        sub_x -= sub_speed
        sub_facing_right = False                # Facing left
    if keys[pygame.K_RIGHT]:
        sub_x += sub_speed
        sub_facing_right = True                 # Facing right
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
            torp_anim_frame = 0  # Reset animation
            
            
    # Draw background and images
    screen.blit(background_img, (0, 0))
    screen.blit(ship_img, (400, 120))
    # Draw torpedo if active
    if torp_active:
        # Alternate images every 5 frames
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