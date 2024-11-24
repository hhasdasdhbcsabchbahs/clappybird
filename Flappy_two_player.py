import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Clappy Bird - Tap to Play")

# Colors
WHITE = (255, 255, 255)
BLUE = (135, 206, 250)
DARK_BLUE = (70, 130, 180)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
DARK_GREEN = (0, 150, 0)
GRAY = (200, 200, 200)

# Fonts
font = pygame.font.Font(None, 48)
small_font = pygame.font.Font(None, 36)

# Game variables
gravity = 0.5
pipe_width = 60
pipe_gap = 150
pipe_velocity = 3

# Load the bird sprite
bird_sprite = pygame.image.load("bird.png").convert_alpha()
bird_sprite = pygame.transform.scale(bird_sprite, (50, 50))  # Resize as needed

# Create a background gradient
background_gradient = pygame.Surface((WIDTH, HEIGHT))
for y in range(HEIGHT):
    shade = DARK_BLUE[1] + (BLUE[1] - DARK_BLUE[1]) * (y / HEIGHT)
    pygame.draw.line(background_gradient, (shade, shade, 255), (0, y), (WIDTH, y))

def create_pipe():
    pipe_height = random.randint(150, 450)
    return {"top": pygame.Rect(WIDTH, 0, pipe_width, pipe_height - pipe_gap),
            "bottom": pygame.Rect(WIDTH, pipe_height, pipe_width, HEIGHT - pipe_height)}

def move_pipes(pipes):
    for pipe in pipes:
        pipe["top"].x -= pipe_velocity
        pipe["bottom"].x -= pipe_velocity
    return [pipe for pipe in pipes if pipe["top"].x > -pipe_width]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, DARK_GREEN, pipe["top"])
        pygame.draw.rect(screen, GREEN, pipe["bottom"])

def check_collision(pipes, bird_pos):
    for pipe in pipes:
        if pygame.Rect(pipe["top"]).collidepoint(bird_pos) or pygame.Rect(pipe["bottom"]).collidepoint(bird_pos):
            return True
    if bird_pos[1] <= 0 or bird_pos[1] >= HEIGHT:
        return True
    return False

def draw_text(text, font, color, x, y):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=(x, y))
    screen.blit(text_surface, text_rect)

def draw_bird(bird_pos):
    screen.blit(bird_sprite, (bird_pos[0] - bird_sprite.get_width() // 2, bird_pos[1] - bird_sprite.get_height() // 2))

def game_loop():
    # Reset bird position
    bird_pos = [100, HEIGHT // 2]
    bird_movement = 0
    pipes = []
    score = 0
    clock = pygame.time.Clock()

    # Initialize game state
    game_started = False
    collision_occurred = False  # To track if a collision has occurred
    collision_timer = 0  # Timer for how long to freeze the game on collision
    flash_timer = 0
    flash_visible = True

    while True:
        screen.blit(background_gradient, (0, 0))  # Draw gradient background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if not collision_occurred and game_started and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                bird_movement = -8  # Jump during gameplay
            elif not game_started and (event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN):
                game_started = True
                bird_movement = -8  # Initial jump to start

        if not game_started:
            # Show "Tap to Play" message
            flash_timer += clock.get_time()
            if flash_timer > 500:  # Toggle visibility every 500ms
                flash_visible = not flash_visible
                flash_timer = 0

            if flash_visible:
                draw_text("Tap to Play", font, WHITE, WIDTH // 2, HEIGHT // 3)

            # Hold bird in place
            draw_bird(bird_pos)
        elif not collision_occurred:
            # Bird movement
            bird_movement += gravity
            bird_pos[1] += bird_movement

            # Create bird's bounding rectangle
            bird_rect = pygame.Rect(
                bird_pos[0] - bird_sprite.get_width() // 1.4,
                bird_pos[1] - bird_sprite.get_height() // 1.4,
                bird_sprite.get_width(),
                bird_sprite.get_height(),
            )

            # Pipe handling
            if not pipes or pipes[-1]["top"].x < WIDTH - 200:
                pipes.append(create_pipe())
            pipes = move_pipes(pipes)
            draw_pipes(pipes)

            # Collision detection
            for pipe in pipes:
                if bird_rect.colliderect(pipe["top"]) or bird_rect.colliderect(pipe["bottom"]):
                    collision_occurred = True  # Trigger collision state
                    break

            # Check collision with screen borders
            if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
                collision_occurred = True  # Trigger collision state

            # Draw bird
            draw_bird(bird_pos)

            # Score
            score += sum(1 for pipe in pipes if pipe["top"].x == bird_pos[0])
            draw_text(f"Score: {score}", small_font, WHITE, WIDTH // 2, 50)

        else:
            # Collision occurred - freeze game state
            collision_timer += clock.get_time()  # Track time since collision
            draw_pipes(pipes)  # Keep pipes static
            draw_bird(bird_pos)  # Keep bird static
            draw_text(f"Score: {score}", small_font, WHITE, WIDTH // 2, 50)

            if collision_timer > 1000:  # Wait 1 second before ending the game
                return score  # End the game and return the score

        pygame.display.flip()
        clock.tick(60)

def menu_screen():
    while True:
        screen.blit(background_gradient, (0, 0))
        draw_text("Clappy Bird", font, WHITE, WIDTH // 2, HEIGHT // 3)
        play_button = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 50)
        pygame.draw.rect(screen, GRAY, play_button)
        draw_text("Play", small_font, BLACK, play_button.centerx, play_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button.collidepoint(event.pos):
                    return  # Start the game

        pygame.display.flip()

def game_over_screen(score):
    while True:
        screen.blit(background_gradient, (0, 0))
        draw_text("Game Over", font, WHITE, WIDTH // 2, HEIGHT // 3)
        draw_text(f"Score: {score}", small_font, WHITE, WIDTH // 2, HEIGHT // 2 - 20)
        play_again_button = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 50)
        pygame.draw.rect(screen, GRAY, play_again_button)
        draw_text("Play Again", small_font, BLACK, play_again_button.centerx, play_again_button.centery)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_button.collidepoint(event.pos):
                    return  # Restart the game

        pygame.display.flip()

# Main game flow
while True:
    menu_screen()
    final_score = game_loop()
    game_over_screen(final_score)
