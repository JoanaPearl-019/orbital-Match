import pygame
import random
import math

# --- Game Constants ---
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
FPS = 60

# --- Colors ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
LIGHT_GRAY = (150, 150, 150)
GREEN = (34, 197, 94)
RED = (248, 113, 113)
BLUE = (59, 130, 246)
YELLOW = (253, 224, 71)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
COLORS = [GREEN, RED, BLUE, YELLOW, CYAN, ORANGE]

# --- Game Parameters (will be set by difficulty) ---
ORB_SPEED_MODIFIER = 1.0
ORB_COUNT = 20
AVAILABLE_COLORS = 3
LIVES_COUNT = 3

# --- Initialization ---
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Orbital Match")
clock = pygame.time.Clock()

# --- Fonts ---
font_lg = pygame.font.Font(None, 80)
font_md = pygame.font.Font(None, 50)
font_sm = pygame.font.Font(None, 36)
font_tiny = pygame.font.Font(None, 24)

# --- Global Variables for Settings ---
volume = 0.5 # Initial volume level (0.0 to 1.0)

# --- Classes ---
class Launcher(pygame.sprite.Sprite):
    """
    The player's launcher, now a much more sophisticated cannon.
    """
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface([100, 100], pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.angle = 0
    
    def update(self):
        # Aim at the mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        dx = mouse_x - self.rect.centerx
        dy = mouse_y - self.rect.centery
        self.angle = math.atan2(dy, dx)
        
    def draw(self, surface):
        # A more sophisticated cannon design with faceted shapes and a central core
        
        # Calculate the rotation angle in degrees
        angle_deg = -math.degrees(self.angle)
        
        # Create a new surface to draw the cannon on, so it can be rotated as one unit
        cannon_surface = pygame.Surface((150, 60), pygame.SRCALPHA)
        cannon_surface.fill((0, 0, 0, 0)) # Fill with transparent color
        
        # Draw the main cannon body as a rounded rectangle
        body_rect = pygame.Rect(0, 5, 100, 50)
        pygame.draw.rect(cannon_surface, (70, 70, 100), body_rect, border_radius=15)
        
        # Draw the cannon barrel
        barrel_rect = pygame.Rect(90, 15, 60, 30)
        pygame.draw.rect(cannon_surface, (100, 100, 150), barrel_rect, border_radius=5)
        
        # Draw the glowing central core
        core_pos = (50, 30)
        core_radius = 15
        # Outer glow
        for i in range(3):
            alpha = int(255 * (i/3))
            glow_color = (150, 150, 200, alpha)
            pygame.draw.circle(cannon_surface, glow_color, core_pos, core_radius + i, 1)
        # Inner core
        pygame.draw.circle(cannon_surface, (200, 200, 255), core_pos, core_radius)

        # Rotate the entire cannon surface
        rotated_cannon = pygame.transform.rotate(cannon_surface, angle_deg)
        rotated_rect = rotated_cannon.get_rect(center=self.rect.center)
        surface.blit(rotated_cannon, rotated_rect)
        
        # Draw the loading base
        base_width = 80
        base_height = 40
        base_rect = pygame.Rect(self.rect.centerx - base_width/2, self.rect.centery + 10, base_width, base_height)
        pygame.draw.ellipse(surface, (100, 100, 100), base_rect)
        
class Orb(pygame.sprite.Sprite):
    """
    The colored orbs that orbit the center.
    """
    def __init__(self, color, radius, angle, speed):
        super().__init__()
        self.color = color
        self.radius = radius
        self.angle = angle
        self.speed = speed
        self.image = pygame.Surface([30, 30], pygame.SRCALPHA)
        # Using the previous function to draw a 3D-looking orb
        self.image = create_orb_3d_surface(self.color)
        self.rect = self.image.get_rect()
    
    def update(self):
        self.angle += self.speed * ORB_SPEED_MODIFIER
        self.rect.centerx = SCREEN_WIDTH // 2 + self.radius * math.cos(self.angle)
        self.rect.centery = SCREEN_HEIGHT // 2 + self.radius * math.sin(self.angle)

class Projectile(pygame.sprite.Sprite):
    """
    Projectiles fired from the launcher.
    """
    def __init__(self, x, y, color, angle):
        super().__init__()
        self.color = color
        self.image = pygame.Surface([20, 20], pygame.SRCALPHA)
        # Using the previous function to draw a 3D-looking projectile
        self.image = create_projectile_3d_surface(self.color)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 15
        self.velocity_x = self.speed * math.cos(angle)
        self.velocity_y = self.speed * math.sin(angle)
    
    def update(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        
# --- Drawing functions for 3D-like visuals ---
def create_orb_3d_surface(color):
    surface = pygame.Surface([30, 30], pygame.SRCALPHA)
    base_color = color
    light_color = [min(255, c + 70) for c in color]
    dark_color = [max(0, c - 70) for c in color]
    
    # Radial gradient from dark to light
    for i in range(15):
        alpha = int(255 * (i / 15))
        gradient_color = [dark_color[j] + int((base_color[j] - dark_color[j]) * (i / 15)) for j in range(3)]
        pygame.draw.circle(surface, gradient_color, (15, 15), 15-i)

    # Highlight from a light source
    light_pos = (10, 10)
    pygame.draw.circle(surface, light_color, light_pos, 7)
    
    # Specular highlight
    pygame.draw.circle(surface, WHITE, (7, 7), 3)
    
    return surface

def create_projectile_3d_surface(color):
    surface = pygame.Surface([20, 20], pygame.SRCALPHA)
    base_color = color
    light_color = [min(255, c + 100) for c in color]
    
    # Radial gradient
    for i in range(10):
        gradient_color = [base_color[j] + int((light_color[j] - base_color[j]) * (i / 10)) for j in range(3)]
        pygame.draw.circle(surface, gradient_color, (10, 10), 10-i)
    
    # Specular highlight
    pygame.draw.circle(surface, WHITE, (7, 7), 3)

    return surface

def show_settings_screen():
    global volume
    running_settings = True
    
    # Volume slider
    slider_rect = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2, 300, 20)
    slider_knob_rect = pygame.Rect(slider_rect.x + (slider_rect.width * volume) - 10, slider_rect.y - 5, 20, 30)
    
    # Instructions button
    instructions_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 80, 250, 60)
    
    # Back button
    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50)
    
    dragging_knob = False
    
    while running_settings:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if slider_knob_rect.collidepoint(event.pos):
                    dragging_knob = True
                if back_button.collidepoint(event.pos):
                    return
                if instructions_button.collidepoint(event.pos):
                    show_instructions()
            if event.type == pygame.MOUSEBUTTONUP:
                dragging_knob = False
            if event.type == pygame.MOUSEMOTION and dragging_knob:
                mouse_x, _ = event.pos
                if slider_rect.left <= mouse_x <= slider_rect.right:
                    knob_pos = mouse_x - slider_rect.left
                    volume = knob_pos / slider_rect.width
                    slider_knob_rect.centerx = mouse_x
                    pygame.mixer.music.set_volume(volume)
        
        screen.fill(BLACK)
        
        # Draw settings title
        title_text = font_md.render("Settings", True, WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen.blit(title_text, title_rect)

        # Draw volume slider
        volume_text = font_sm.render(f"Volume: {int(volume * 100)}%", True, WHITE)
        volume_rect = volume_text.get_rect(center=(SCREEN_WIDTH // 2, slider_rect.y - 30))
        screen.blit(volume_text, volume_rect)
        pygame.draw.rect(screen, GRAY, slider_rect, border_radius=10)
        pygame.draw.rect(screen, CYAN, slider_knob_rect, border_radius=5)
        
        # Draw instructions button
        pygame.draw.rect(screen, LIGHT_GRAY, instructions_button, border_radius=20)
        instructions_text = font_sm.render("How to Play", True, BLACK)
        screen.blit(instructions_text, instructions_text.get_rect(center=instructions_button.center))
        
        # Draw back button
        pygame.draw.rect(screen, GRAY, back_button, border_radius=15)
        back_text = font_sm.render("Back", True, WHITE)
        screen.blit(back_text, back_text.get_rect(center=back_button.center))
        
        pygame.display.flip()
        clock.tick(FPS)

def show_title_screen():
    screen.fill(BLACK)
    
    # Draw a bigger starfield background
    for _ in range(150):
        star_x = random.randint(0, SCREEN_WIDTH)
        star_y = random.randint(0, SCREEN_HEIGHT)
        star_size = random.randint(2, 4)
        pygame.draw.circle(screen, WHITE, (star_x, star_y), star_size)

    # Draw title
    title_text = font_lg.render("Orbital Match", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    screen.blit(title_text, title_rect)
    
    # Draw difficulty buttons
    earth_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2, 250, 60)
    mars_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 80, 250, 60)
    neptune_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 160, 250, 60)
    instructions_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 240, 250, 60)
    settings_button = pygame.Rect(SCREEN_WIDTH // 2 - 125, SCREEN_HEIGHT // 2 + 320, 250, 60)

    # Draw the buttons
    pygame.draw.rect(screen, GREEN, earth_button, border_radius=20)
    pygame.draw.rect(screen, RED, mars_button, border_radius=20)
    pygame.draw.rect(screen, BLUE, neptune_button, border_radius=20)
    pygame.draw.rect(screen, LIGHT_GRAY, instructions_button, border_radius=20)
    pygame.draw.rect(screen, GRAY, settings_button, border_radius=20)
    
    # Add text to buttons
    earth_text = font_sm.render("Earth (Easy)", True, BLACK)
    mars_text = font_sm.render("Mars (Medium)", True, BLACK)
    neptune_text = font_sm.render("Neptune (Hard)", True, BLACK)
    instructions_text = font_sm.render("Instructions", True, BLACK)
    settings_text = font_sm.render("Settings", True, BLACK)

    screen.blit(earth_text, earth_text.get_rect(center=earth_button.center))
    screen.blit(mars_text, mars_text.get_rect(center=mars_button.center))
    screen.blit(neptune_text, neptune_text.get_rect(center=neptune_button.center))
    screen.blit(instructions_text, instructions_text.get_rect(center=instructions_button.center))
    screen.blit(settings_text, settings_text.get_rect(center=settings_button.center))

    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if earth_button.collidepoint(event.pos): return "easy"
                if mars_button.collidepoint(event.pos): return "medium"
                if neptune_button.collidepoint(event.pos): return "hard"
                if settings_button.collidepoint(event.pos):
                    show_settings_screen()
                    return
                if instructions_button.collidepoint(event.pos):
                    show_instructions()
                    return

def show_instructions():
    screen.fill(BLACK)
    
    title_text = font_md.render("How to Play", True, WHITE)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
    
    instructions_text = [
        "Objective: Clear the screen by launching projectiles at orbiting orbs.",
        "",
        "Controls:",
        "- Use the mouse to aim the central launcher.",
        "- Click the LEFT mouse button to fire a projectile.",
        "",
        "Rules:",
        "- The projectile must have the SAME color as the orb it hits.",
        "- A successful match removes both the projectile and the orb.",
        "- Hitting an incorrect color or missing an orb will cost you a life!",
        "",
        "Difficulty Levels:",
        "- Earth (Easy): Slower orbits and fewer colors.",
        "- Mars (Medium): Increased speeds and orb count.",
        "- Neptune (Hard): Fast, dense orbits and more colors to match."
    ]
    
    y_offset = SCREEN_HEIGHT // 3 - 20
    for line in instructions_text:
        line_text = font_tiny.render(line, True, WHITE)
        line_rect = line_text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(line_text, line_rect)
        y_offset += 25
    
    back_button = pygame.Rect(SCREEN_WIDTH // 2 - 75, SCREEN_HEIGHT - 100, 150, 50)
    pygame.draw.rect(screen, LIGHT_GRAY, back_button, border_radius=15)
    back_text = font_sm.render("Back", True, BLACK)
    screen.blit(back_text, back_text.get_rect(center=back_button.center))
    
    pygame.display.flip()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos): return

def show_end_screen(message, score):
    screen.fill(BLACK)
    
    # Draw a starfield background on the end screen as well
    for _ in range(150):
        star_x = random.randint(0, SCREEN_WIDTH)
        star_y = random.randint(0, SCREEN_HEIGHT)
        star_size = random.randint(2, 4)
        pygame.draw.circle(screen, WHITE, (star_x, star_y), star_size)

    end_text = font_lg.render(message, True, WHITE)
    final_score_text = font_md.render(f"Final Score: {score}", True, WHITE)
    restart_text = font_sm.render("Click to play again", True, WHITE)
    
    text_rect = end_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 70))
    score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
    
    screen.blit(end_text, text_rect)
    screen.blit(final_score_text, score_rect)
    screen.blit(restart_text, restart_rect)
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False

def run_game_loop():
    running = True
    game_state = "title"
    next_projectile_color = None
    combo_count = 0

    while running:
        if game_state == "title":
            difficulty = show_title_screen()
            
            global ORB_SPEED_MODIFIER, ORB_COUNT, AVAILABLE_COLORS
            if difficulty == "easy":
                ORB_SPEED_MODIFIER = 1.2
                ORB_COUNT = 15
                AVAILABLE_COLORS = 3
            elif difficulty == "medium":
                ORB_SPEED_MODIFIER = 1.7
                ORB_COUNT = 25
                AVAILABLE_COLORS = 4
            elif difficulty == "hard":
                ORB_SPEED_MODIFIER = 3.0
                ORB_COUNT = 40
                AVAILABLE_COLORS = 5
            elif difficulty == None:
                continue
            
            # Set up level layout
            launcher = Launcher()
            all_sprites = pygame.sprite.Group(launcher)
            orbs = pygame.sprite.Group()
            projectiles = pygame.sprite.Group()

            for i in range(ORB_COUNT):
                color = random.choice(COLORS[:AVAILABLE_COLORS])
                radius = 200 + (i % 3) * 50
                angle = (i / ORB_COUNT) * 2 * math.pi
                speed = 0.005 + random.uniform(-0.001, 0.001)
                new_orb = Orb(color, radius, angle, speed)
                orbs.add(new_orb)
                all_sprites.add(new_orb)
            
            game_state = "playing"
            score = 0
            lives = LIVES_COUNT
            
            if orbs:
                initial_orb_colors = [orb.color for orb in orbs]
                next_projectile_color = random.choice(initial_orb_colors)
            else:
                next_projectile_color = random.choice(COLORS[:AVAILABLE_COLORS])

            combo_count = 0
            
        elif game_state == "playing":
            # --- Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if orbs:
                            new_projectile = Projectile(launcher.rect.centerx, launcher.rect.centery, next_projectile_color, launcher.angle)
                            projectiles.add(new_projectile)
                            all_sprites.add(new_projectile)

                            available_orb_colors = list(set([orb.color for orb in orbs]))
                            if available_orb_colors:
                                next_projectile_color = random.choice(available_orb_colors)
                            else:
                                next_projectile_color = None
            
            # --- Game Logic ---
            all_sprites.update()
            launcher.update()

            for projectile in projectiles.copy():
                if projectile.rect.left > SCREEN_WIDTH or projectile.rect.right < 0 or \
                   projectile.rect.top > SCREEN_HEIGHT or projectile.rect.bottom < 0:
                    lives -= 1
                    combo_count = 0
                    projectile.kill()
            
            collided_dict = pygame.sprite.groupcollide(projectiles, orbs, False, False)
            for projectile, collided_orbs in collided_dict.items():
                for orb in collided_orbs:
                    if projectile.color == orb.color:
                        combo_count += 1
                        score_multiplier = 1 + (combo_count // 5)
                        score += 100 * score_multiplier
                        projectile.kill()
                        orb.kill()
                        available_orb_colors = list(set([orb.color for orb in orbs]))
                        if available_orb_colors:
                            next_projectile_color = random.choice(available_orb_colors)
                        else:
                            next_projectile_color = None
                    else:
                        lives -= 1
                        combo_count = 0
                        projectile.kill()
            
            if not orbs:
                game_state = "win"
            
            if lives <= 0:
                game_state = "game_over"
            
            # --- Rendering ---
            screen.fill(BLACK)
            
            launcher.draw(screen)
            all_sprites.draw(screen)

            score_text = font_sm.render(f"Score: {score}", True, WHITE)
            screen.blit(score_text, (10, 10))

            for i in range(lives):
                heart_img = pygame.Surface([30, 30], pygame.SRCALPHA)
                pygame.draw.polygon(heart_img, RED, [
                    (15, 0), (10, 5), (0, 15), (0, 25), (5, 30),
                    (15, 25), (25, 30), (30, 25), (30, 15), (20, 5)
                ])
                screen.blit(heart_img, (10 + i * 40, 50))
            
            if combo_count > 0:
                combo_text = font_sm.render(f"Combo: {combo_count}x", True, YELLOW)
                screen.blit(combo_text, (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, 10))

            next_color_text = font_tiny.render("Next:", True, WHITE)
            screen.blit(next_color_text, (SCREEN_WIDTH - 120, 10))
            if next_projectile_color:
                pygame.draw.circle(screen, next_projectile_color, (SCREEN_WIDTH - 50, 25), 10)
            
            pygame.display.flip()
        
        elif game_state == "win":
            show_end_screen("Level Complete!", score)
            game_state = "title"

        elif game_state == "game_over":
            show_end_screen("Game Over", score)
            game_state = "title"

        # --- Frame Rate Control ---
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    run_game_loop()