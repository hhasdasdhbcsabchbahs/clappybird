import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 400, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flappy Bird - Horizontal Pipes")

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
pipe_height = 60
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
    pipe_x = random.randint(100, WIDTH - pipe_gap - 100)
    return {"left": pygame.Rect(0, HEIGHT, pipe_x, pipe_height),  # Left block
            "right": pygame.Rect(pipe_x + pipe_gap, HEIGHT, WIDTH - (pipe_x + pipe_gap), pipe_height)}  # Right block

def move_pipes(pipes):
    for pipe in pipes:
        pipe["left"].y -= pipe_velocity
        pipe["right"].y -= pipe_velocity
    return [pipe for pipe in pipes if pipe["left"].y > -pipe_height]

def draw_pipes(pipes):
    for pipe in pipes:
        pygame.draw.rect(screen, DARK_GREEN, pipe["left"])
        pygame.draw.rect(screen, GREEN, pipe["right"])

def check_collision(pipes, bird_pos):
    for pipe in pipes:
        if pipe["left"].collidepoint(bird_pos) or pipe["right"].collidepoint(bird_pos):
            return True
    if bird_pos[0] <= 0 or bird_pos[0] >= WIDTH:
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
    bird_pos = [WIDTH // 2, HEIGHT // 2]
    bird_movement = 0
    pipes = []
    score = 0
    clock = pygame.time.Clock()

    # Initialize game state
    game_started = False
    collision_occurred = False
    collision_timer = 0
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
            if not pipes or pipes[-1]["left"].y < HEIGHT - 200:
                pipes.append(create_pipe())
            pipes = move_pipes(pipes)
            draw_pipes(pipes)

            # Collision detection
            for pipe in pipes:
                if bird_rect.colliderect(pipe["left"]) or bird_rect.colliderect(pipe["right"]):
                    collision_occurred = True
                    break

            # Check collision with screen borders
            if bird_rect.top <= 0 or bird_rect.bottom >= HEIGHT:
                collision_occurred = True

            # Draw bird
            draw_bird(bird_pos)

            # Score
            score += sum(1 for pipe in pipes if pipe["left"].y == bird_pos[1])
            draw_text(f"Score: {score}", small_font, WHITE, WIDTH // 2, 50)

        else:
            # Collision occurred - freeze game state
            collision_timer += clock.get_time()
            draw_pipes(pipes)
            draw_bird(bird_pos)
            draw_text(f"Score: {score}", small_font, WHITE, WIDTH // 2, 50)

            if collision_timer > 1000:  # Wait 1 second before ending the game
                return score

        pygame.display.flip()
        clock.tick(60)
