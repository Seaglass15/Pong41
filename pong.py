import pygame
import sys
import random

# Initialize PyGame & Set Up Display
pygame.init()
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600  # screen size
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))  # Set up the display
pygame.display.set_caption("Pong 41 - THEODOROS SYRIOPOULOS")
game_active = False

# Background Color & Fonts
BG_COLOR = pygame.Color('grey12')  # Dark grey background
font_path = 'Quake3d.ttf'
large_font = pygame.font.Font(font_path, 196)
custom_font = pygame.font.Font(font_path, 36)

# Countdown
clock = pygame.time.Clock()  # Create a clock object
countdown_active = False
countdown_time = 3000  # 3 seconds
current_countdown = countdown_time

# Score Count
left_score = 0
right_score = 0

# Load Intro Image
start_image = pygame.image.load('intro.png')
start_image = pygame.transform.scale(start_image, (SCREEN_WIDTH, SCREEN_HEIGHT))


class Paddle:
    def __init__(self, screen, position, is_auto=False):
        self.screen = screen
        self.width, self.height = 10, 100   # Width and height of paddle
        self.x, self.y = position           # Initial position of the paddle
        self.color = pygame.Color('white')  # Color of the paddle
        self.speed = 7                      # Movement speed of the paddle
        self.misalign_chance = 0.33         # 33% chance to not move optimally

    def draw(self):
        """Draws the paddle on the screen."""
        pygame.draw.rect(self.screen, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

    def move_up(self):
        """Moves paddle up"""
        if self.y > 0:  # Ensure the paddle doesn't go off the screen
            self.y -= self.speed

    def move_down(self):
        """Moves paddle down"""
        if self.y + self.height < SCREEN_HEIGHT:  # Ensure the paddle doesn't go off the screen
            self.y += self.speed

    def auto_move(self, ball):
        """Automatically moves the left paddle to follow the ball with a chance of error."""
        if random.random() < self.misalign_chance:
            self.random_move()  # Calls def random_move
        else:
            # move toward the ball's position
            if self.y + self.height / 2 < ball.y:
                self.move_down()
            elif self.y + self.height / 2 > ball.y:
                self.move_up()

    def random_move(self):
        """"Chooses randomly to move down, stay or go up"""
        move_decision = random.choice([-1, 0, 1])
        if move_decision == 1:
            self.move_up()
        elif move_decision == -1:
            self.move_down()


class Ball:
    def __init__(self, screen):
        self.screen = screen
        self.color = pygame.Color('white')
        self.radius = 7                    # Ball radius
        self.speed_increase_factor = 1.042  # Speed increases by 4.2% each reset
        self.reset()

    def draw(self):
        """Draws the ball on the screen."""
        pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius)

    def update(self, left_paddle, right_paddle):
        """Updates the ball's position and handles collisions."""
        self.x += self.speed_x
        self.y += self.speed_y

        # Collision with the edges of the screen
        if self.y - self.radius <= 0 or self.y + self.radius >= SCREEN_HEIGHT:
            self.speed_y *= -1

        # Ball rectangle for collision detection
        ball_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, 2 * self.radius, 2 * self.radius)

        # Paddle rectangles
        left_paddle_rect = pygame.Rect(left_paddle.x, left_paddle.y, left_paddle.width, left_paddle.height)
        right_paddle_rect = pygame.Rect(right_paddle.x, right_paddle.y, right_paddle.width, right_paddle.height)

        # Check for collisions with the paddles
        if ball_rect.colliderect(left_paddle_rect):
            self.speed_x *= -1  # Reverse the horizontal direction of the ball
            # Nudge the ball out of the paddle to avoid sticking
            self.x = left_paddle.x + left_paddle.width + self.radius + 1
        elif ball_rect.colliderect(right_paddle_rect):
            self.speed_x *= -1  # Reverse the horizontal direction of the ball
            # Nudge the ball out of the paddle to avoid sticking
            self.x = right_paddle.x - self.radius - 1

    def reset(self):
        """Resets the ball to the center of the screen with a new random speed and direction."""
        self.x, self.y = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2
        self.base_speed_x = 5 if not hasattr(self, 'base_speed_x') else self.base_speed_x * self.speed_increase_factor
        self.base_speed_y = 5 if not hasattr(self, 'base_speed_y') else self.base_speed_y * self.speed_increase_factor
        self.speed_x = random.choice([-self.base_speed_x, self.base_speed_x])
        self.speed_y = random.choice([-self.base_speed_y, self.base_speed_y])


def show_start_screen():
    """Displays the intro screen until the player presses SPACE."""
    screen.blit(start_image, (0, 0))  # Map image to the screen
    pygame.display.flip()
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                # Start the game by pressing SPACE
                if event.key == pygame.K_SPACE:
                    waiting = False
                    return True  # Game Start


def update_scores(ball):
    """Updates the score and manages the countdown after a point is scored."""
    global right_score, left_score, countdown_active, current_countdown
    if ball.x < 0 - ball.radius:  # Ball has passed the left boundary
        right_score += 1
        countdown_active = True
        current_countdown = countdown_time     # Reset countdown
        ball.reset()                           # Reset Ball
    elif ball.x > SCREEN_WIDTH + ball.radius:  # Ball has passed the right boundary
        left_score += 1
        countdown_active = True
        current_countdown = countdown_time  # Reset countdown
        ball.reset()                        # Reset ball


def draw_score(screen, score, position):
    """Draws the current score on the screen."""
    score_surface = custom_font.render(str(score), True, pygame.Color('white'))
    score_rect = score_surface.get_rect(center=position)
    screen.blit(score_surface, score_rect)


# Show the start screen & activate game
show_start_screen()
game_active = True
countdown_active = True
current_countdown = countdown_time

# Create two paddles and a ball
left_paddle = Paddle(screen, (30, SCREEN_HEIGHT // 2 - 50), is_auto=True)
right_paddle = Paddle(screen, (SCREEN_WIDTH - 40, SCREEN_HEIGHT // 2 - 50))
ball = Ball(screen)


# Start the main game loop
running = True
while running:
    dt = clock.tick(60)  # Control the frame rate
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    game_active = True
                    ball.reset()
            if event.key == pygame.K_r:  # Reset scores and game state
                left_score = 0
                right_score = 0
                game_active = False
                countdown_active = False
                current_countdown = countdown_time
                ball.reset()
                show_start_screen()  # Show the intro screen again

    if game_active and not countdown_active:
        # Let the left paddle move by itself
        left_paddle.auto_move(ball)

        # Keyboard input for right side paddle
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            right_paddle.move_up()
        if keys[pygame.K_DOWN]:
            right_paddle.move_down()

        # Update game elements
        ball.update(left_paddle, right_paddle)
        update_scores(ball)

    elif countdown_active:
        # Countdown logic
        current_countdown -= dt
        if current_countdown <= 0:
            countdown_active = False
            game_active = True
        countdown_number = str(current_countdown // 1000 + 1)  # Get the current countdown number

    # Fill the screen with background color
    screen.fill(BG_COLOR)

    if game_active:
        # Draw game elements
        left_paddle.draw()
        right_paddle.draw()
        ball.draw()

    if countdown_active:
        # Render countdown number in the center of the screen in big
        countdown_text = large_font.render(countdown_number, True, pygame.Color('white'))
        countdown_rect = countdown_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT / 2 // 2))
        screen.blit(countdown_text, countdown_rect)

    # Draw scores
    draw_score(screen, left_score, (SCREEN_WIDTH / 4, 50))  # Position for the left score
    draw_score(screen, right_score, (3 * SCREEN_WIDTH / 4, 50))  # Position for the right score

    # Update display
    pygame.display.flip()

# Quit PyGame and sys when the game loop ends
pygame.quit()
sys.exit()
