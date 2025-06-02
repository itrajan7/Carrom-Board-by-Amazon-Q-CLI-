#!/usr/bin/env python3
"""
Carrom Board Game - A two-player implementation using Pygame
"""
import pygame
import sys
import math
import random
from pygame.locals import *

# Initialize pygame
pygame.init()
pygame.mixer.init()  # Initialize sound mixer

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 800
FPS = 60
BOARD_SIZE = 600
POCKET_RADIUS = 30
STRIKER_RADIUS = 20
COIN_RADIUS = 15
QUEEN_RADIUS = 15

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BROWN = (139, 69, 19)
LIGHT_BROWN = (237, 220, 179)  # Lighter beige for board surface
BOARD_BORDER = (40, 40, 40)    # Dark border
CREAM = (245, 245, 220)        # Cream color for board
GREEN = (0, 128, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (80, 80, 80)

# Game states
START_SCREEN = 0
SETTINGS_SCREEN = 1
PLAYING = 2
GAME_OVER = 3
PAUSED = 4

# Themes
THEMES = {
    "Classic": {
        "board": (237, 220, 179),  # Light wooden color
        "border": (101, 67, 33),   # Dark wooden border
        "lines": (0, 0, 0),        # Black
        "pocket": (180, 0, 0),     # Dark red
        "accent": (180, 0, 0)      # Dark red
    },
    "Modern": {
        "board": (220, 220, 220),  # Light gray
        "border": (50, 50, 50),    # Dark gray
        "lines": (0, 0, 0),        # Black
        "pocket": (0, 100, 200),   # Blue
        "accent": (0, 150, 200)    # Blue
    },
    "Dark": {
        "board": (50, 50, 50),     # Dark gray
        "border": (20, 20, 20),    # Almost black
        "lines": (200, 200, 200),  # Light gray
        "pocket": (150, 0, 0),     # Dark red
        "accent": (200, 0, 0)      # Red
    },
    "Forest": {
        "board": (180, 210, 170),  # Light green
        "border": (60, 80, 50),    # Dark green
        "lines": (40, 60, 30),     # Darker green
        "pocket": (120, 70, 20),   # Brown
        "accent": (150, 100, 50)   # Light brown
    }
}

class Coin:
    """Class representing a carrom coin"""
    def __init__(self, x, y, color, is_queen=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = QUEEN_RADIUS if is_queen else COIN_RADIUS
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_queen = is_queen
        self.is_pocketed = False
        self.friction = 0.98  # Friction coefficient
        self.rotation = random.uniform(0, 360)  # Random initial rotation for visual variety

    def update(self):
        """Update coin position based on velocity"""
        if self.is_pocketed:
            return
            
        # Apply friction
        self.velocity_x *= self.friction
        self.velocity_y *= self.friction
        
        # Stop if velocity is very small
        if abs(self.velocity_x) < 0.1 and abs(self.velocity_y) < 0.1:
            self.velocity_x = 0
            self.velocity_y = 0
        
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y
        
        # Update rotation based on movement
        if self.velocity_x != 0 or self.velocity_y != 0:
            speed = math.sqrt(self.velocity_x**2 + self.velocity_y**2)
            self.rotation += speed * 2  # Rotate based on speed
            self.rotation %= 360  # Keep within 0-360 degrees
        
        # Boundary collision
        board_margin = (SCREEN_WIDTH - BOARD_SIZE) // 2
        
        if self.x - self.radius < board_margin:
            self.x = board_margin + self.radius
            self.velocity_x = -self.velocity_x * 0.8
        elif self.x + self.radius > SCREEN_WIDTH - board_margin:
            self.x = SCREEN_WIDTH - board_margin - self.radius
            self.velocity_x = -self.velocity_x * 0.8
            
        if self.y - self.radius < board_margin:
            self.y = board_margin + self.radius
            self.velocity_y = -self.velocity_y * 0.8
        elif self.y + self.radius > SCREEN_HEIGHT - board_margin:
            self.y = SCREEN_HEIGHT - board_margin - self.radius
            self.velocity_y = -self.velocity_y * 0.8

    def draw(self, screen):
        """Draw the coin on the screen"""
        if not self.is_pocketed:
            # Draw main coin body
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)
            
            if self.is_queen:
                # Queen has a special design
                pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius - 3)
                pygame.draw.circle(screen, RED, (int(self.x), int(self.y)), self.radius - 6)
            else:
                # Regular coins have decorative patterns
                # Draw outer ring
                pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 1)
                
                # Draw inner decorative pattern
                inner_radius = self.radius - 4
                if inner_radius > 0:
                    # Draw decorative lines based on rotation
                    for i in range(4):
                        angle = math.radians(self.rotation + i * 45)
                        end_x = self.x + inner_radius * math.cos(angle)
                        end_y = self.y + inner_radius * math.sin(angle)
                        line_color = (50, 50, 50) if self.color == WHITE else (200, 200, 200)
                        pygame.draw.line(screen, line_color, (self.x, self.y), (end_x, end_y), 1)

    def check_collision(self, other_coin):
        """Check and handle collision with another coin"""
        if self.is_pocketed or other_coin.is_pocketed:
            return False
            
        dx = other_coin.x - self.x
        dy = other_coin.y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance < self.radius + other_coin.radius:
            # Collision detected
            # Calculate collision normal
            nx = dx / distance
            ny = dy / distance
            
            # Relative velocity
            dvx = other_coin.velocity_x - self.velocity_x
            dvy = other_coin.velocity_y - self.velocity_y
            
            # Impact velocity along normal
            impact_speed = dvx * nx + dvy * ny
            
            # No collision if moving away
            if impact_speed < 0:
                return False
                
            # Collision impulse
            impulse = 2 * impact_speed / (self.radius + other_coin.radius)
            
            # Apply impulse
            self.velocity_x += impulse * nx * other_coin.radius
            self.velocity_y += impulse * ny * other_coin.radius
            other_coin.velocity_x -= impulse * nx * self.radius
            other_coin.velocity_y -= impulse * ny * self.radius
            
            # Separate coins to prevent sticking
            overlap = (self.radius + other_coin.radius - distance) / 2
            self.x -= overlap * nx
            self.y -= overlap * ny
            other_coin.x += overlap * nx
            other_coin.y += overlap * ny
            
            # Create collision particles if this is the striker
            if isinstance(self, Striker) and impact_speed > 0.5:
                collision_point_x = self.x + nx * self.radius
                collision_point_y = self.y + ny * self.radius
                
                # Add collision particles
                for _ in range(int(min(10, impact_speed * 2))):
                    angle = math.atan2(ny, nx) + random.uniform(-math.pi/2, math.pi/2)
                    speed = random.uniform(0.5, 2) * min(3, impact_speed)
                    
                    # Vary particle colors based on the coin color
                    if other_coin.color == WHITE:
                        particle_color = (255, 255, 255)
                    elif other_coin.color == BLACK:
                        particle_color = (50, 50, 50)
                    elif other_coin.color == RED:
                        particle_color = (255, 100, 100)
                    else:
                        particle_color = (200, 200, 200)
                    
                    self.strike_particles.append({
                        'x': collision_point_x,
                        'y': collision_point_y,
                        'vx': math.cos(angle) * speed,
                        'vy': math.sin(angle) * speed,
                        'life': random.uniform(5, 15),
                        'color': particle_color
                    })
            
            # Play collision sound if impact is significant
            if impact_speed > 1:
                try:
                    if hasattr(pygame.mixer, 'Sound'):
                        volume = min(1.0, impact_speed / 10)
                        pygame.mixer.Channel(1).set_volume(volume)
                        pygame.mixer.Channel(1).play(pygame.mixer.Sound("collision.wav"))
                except:
                    pass  # Silently fail if sound can't be played
            
            return True
        return False

    def check_pocket(self, pockets):
        """Check if coin falls into a pocket"""
        if self.is_pocketed:
            return False
            
        for pocket in pockets:
            dx = pocket[0] - self.x
            dy = pocket[1] - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance < POCKET_RADIUS - 5:
                self.is_pocketed = True
                return True
        return False

class Striker(Coin):
    """Class representing the striker"""
    def __init__(self, x, y):
        super().__init__(x, y, WHITE)  # Changed from BLUE to WHITE with black outline
        self.radius = STRIKER_RADIUS
        self.reset_position(1)  # Player 1 starts
        self.is_positioned = False
        self.is_aiming = False
        self.aim_angle = 0
        self.power = 0
        self.max_power = 20
        self.is_shooting = False
        self.strike_particles = []
        self.strike_sound_played = False
        self.small_font = pygame.font.SysFont(None, 24)

    def reset_position(self, player):
        """Reset striker position based on current player"""
        board_margin = (SCREEN_WIDTH - BOARD_SIZE) // 2
        self.velocity_x = 0
        self.velocity_y = 0
        
        if player == 1:
            # Bottom
            self.y = SCREEN_HEIGHT - board_margin - 50
            self.x = SCREEN_WIDTH // 2
        else:
            # Top
            self.y = board_margin + 50
            self.x = SCREEN_WIDTH // 2
            
        self.is_positioned = False
        self.is_aiming = False
        self.is_shooting = False
        self.power = 0
        self.is_pocketed = False

    def position(self, x):
        """Position the striker horizontally along the baseline"""
        board_margin = (SCREEN_WIDTH - BOARD_SIZE) // 2
        min_x = board_margin + self.radius + 50
        max_x = SCREEN_WIDTH - board_margin - self.radius - 50
        
        self.x = max(min_x, min(x, max_x))

    def aim(self, mouse_x, mouse_y):
        """Set aiming direction based on mouse position"""
        dx = mouse_x - self.x
        dy = mouse_y - self.y
        self.aim_angle = math.atan2(dy, dx)

    def set_power(self, power_percentage):
        """Set shooting power"""
        self.power = min(power_percentage * self.max_power / 100, self.max_power)

    def shoot(self):
        """Shoot the striker with current angle and power"""
        self.velocity_x = math.cos(self.aim_angle) * self.power
        self.velocity_y = math.sin(self.aim_angle) * self.power
        self.is_shooting = True
        self.is_positioned = False
        self.is_aiming = False
        
        # Create strike effect particles
        self.strike_particles = []
        num_particles = int(20 * (self.power / self.max_power))  # More particles for higher power
        
        for _ in range(num_particles):
            # Particles shoot in the opposite direction of striker movement
            angle = self.aim_angle + math.pi + random.uniform(-0.3, 0.3)
            speed = random.uniform(1, 4) * (self.power / self.max_power)
            
            # Vary the particle colors
            r = random.randint(200, 255)
            g = random.randint(200, 255)
            b = random.randint(100, 200)
            
            self.strike_particles.append({
                'x': self.x - math.cos(self.aim_angle) * self.radius * 0.8,  # Start behind striker
                'y': self.y - math.sin(self.aim_angle) * self.radius * 0.8,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.uniform(10, 25),
                'color': (r, g, b)
            })

    def update(self):
        """Update striker position and particles"""
        super().update()
        
        # Update strike particles
        if hasattr(self, 'strike_particles'):
            particles_to_keep = []
            for particle in self.strike_particles:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
                
                if particle['life'] > 0:
                    particles_to_keep.append(particle)
            
            self.strike_particles = particles_to_keep
            
        # Reset strike sound flag when striker stops
        if self.velocity_x == 0 and self.velocity_y == 0:
            self.strike_sound_played = False

    def draw(self, screen):
        """Draw the striker and aiming line if applicable"""
        # Draw strike particles first (behind the striker)
        if hasattr(self, 'strike_particles'):
            for particle in self.strike_particles:
                alpha = min(255, int(particle['life'] * 12))
                color = list(particle['color'])
                if len(color) < 4:
                    color.append(alpha)
                pygame.draw.circle(screen, color, (int(particle['x']), int(particle['y'])), 
                                  int(particle['life'] / 5) + 1)
        
        # Draw the striker
        if not self.is_pocketed:
            pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.radius)
            pygame.draw.circle(screen, BLACK, (int(self.x), int(self.y)), self.radius, 2)
        
        if self.is_aiming:
            # Draw aiming line
            end_x = self.x + math.cos(self.aim_angle) * 150
            end_y = self.y + math.sin(self.aim_angle) * 150
            pygame.draw.line(screen, RED, (self.x, self.y), (end_x, end_y), 2)
            
            # Draw power meter
            if self.power > 0:
                # Draw power bar background
                bar_width = 200
                bar_height = 20
                bar_x = SCREEN_WIDTH // 2 - bar_width // 2
                bar_y = SCREEN_HEIGHT - 50
                
                # Draw background bar
                pygame.draw.rect(screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                
                # Draw power level
                power_width = int(bar_width * (self.power / self.max_power))
                
                # Gradient color based on power
                if self.power < self.max_power * 0.33:
                    power_color = (0, 255, 0)  # Green for low power
                elif self.power < self.max_power * 0.66:
                    power_color = (255, 255, 0)  # Yellow for medium power
                else:
                    power_color = (255, 0, 0)  # Red for high power
                
                pygame.draw.rect(screen, power_color, (bar_x, bar_y, power_width, bar_height))
                
                # Draw border
                pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
                
                # Draw power text
                power_text = f"Power: {int(self.power / self.max_power * 100)}%"
                text_surf = self.small_font.render(power_text, True, WHITE)
                screen.blit(text_surf, (bar_x + bar_width // 2 - text_surf.get_width() // 2, 
                                       bar_y - 25))
                
                # Draw power line on aiming line
                power_length = 150 * (self.power / self.max_power)
                power_end_x = self.x + math.cos(self.aim_angle) * power_length
                power_end_y = self.y + math.sin(self.aim_angle) * power_length
                pygame.draw.line(screen, power_color, (self.x, self.y), (power_end_x, power_end_y), 4)

class CarromGame:
    """Main game class"""
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Carrom Board Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        self.title_font = pygame.font.SysFont(None, 48)
        
        # Game settings
        self.current_theme = "Classic"
        self.player_mode = 2  # Default to 2 players
        self.sound_enabled = True
        self.selected_option = 0  # For menu navigation
        
        # Load sounds
        try:
            self.strike_sound = pygame.mixer.Sound("strike.wav")
            self.pocket_sound = pygame.mixer.Sound("pocket.wav")
            self.collision_sound = pygame.mixer.Sound("collision.wav")
            self.menu_sound = pygame.mixer.Sound("menu.wav")
            self.sounds_loaded = True
        except:
            print("Warning: Sound files not found. Game will run without sound.")
            self.sounds_loaded = False
        
        self.game_state = START_SCREEN
        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state"""
        self.striker = Striker(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.coins = []
        self.pockets = self.create_pockets()
        self.setup_coins()
        
        self.current_player = 1
        self.player1_score = 0
        self.player2_score = 0
        self.player3_score = 0
        self.player4_score = 0
        self.queen_pocketed = False
        self.queen_covered = False
        self.last_pocketed_queen = False
        self.foul_count = 0
        self.winner = None
        self.all_coins_still = True
        self.turn_message = ""
        self.game_saved = False

    def create_pockets(self):
        """Create the four corner pockets"""
        board_margin = (SCREEN_WIDTH - BOARD_SIZE) // 2
        return [
            (board_margin, board_margin),  # Top-left
            (SCREEN_WIDTH - board_margin, board_margin),  # Top-right
            (board_margin, SCREEN_HEIGHT - board_margin),  # Bottom-left
            (SCREEN_WIDTH - board_margin, SCREEN_HEIGHT - board_margin)  # Bottom-right
        ]

    def setup_coins(self):
        """Set up the initial coin positions"""
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Create the queen (red coin) at the center
        self.coins.append(Coin(center_x, center_y, RED, True))
        
        # Create white and black coins in a circular arrangement
        # Traditional carrom setup has coins arranged in concentric circles
        
        # Inner circle - 6 coins (alternating black and white)
        radius = COIN_RADIUS * 2.5
        for i in range(6):
            angle = i * (2 * math.pi / 6)
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if i % 2 == 0:
                self.coins.append(Coin(x, y, BLACK))
            else:
                self.coins.append(Coin(x, y, WHITE))
        
        # Middle circle - 8 coins
        radius = COIN_RADIUS * 4.5
        for i in range(8):
            angle = (i * (2 * math.pi / 8)) + (math.pi / 8)  # Offset to stagger
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if i % 2 == 0:
                self.coins.append(Coin(x, y, WHITE))
            else:
                self.coins.append(Coin(x, y, BLACK))
        
        # Outer circle - 9 coins
        radius = COIN_RADIUS * 6.5
        for i in range(9):
            angle = (i * (2 * math.pi / 9)) + (math.pi / 9)  # Offset to stagger
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            if i % 2 == 0:
                self.coins.append(Coin(x, y, BLACK))
            else:
                self.coins.append(Coin(x, y, WHITE))

    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
                
            if self.game_state == START_SCREEN:
                if event.type == KEYDOWN:
                    if event.key == K_SPACE:
                        self.game_state = PLAYING
                    elif event.key == K_s:
                        self.game_state = SETTINGS_SCREEN
                        self.selected_option = 0
                    elif event.key == K_l:
                        self.load_game()
                        
            elif self.game_state == SETTINGS_SCREEN:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = START_SCREEN
                    elif event.key == K_RETURN:
                        # Apply selected setting
                        if self.selected_option == 0:  # Theme
                            theme_list = list(THEMES.keys())
                            current_idx = theme_list.index(self.current_theme)
                            self.current_theme = theme_list[(current_idx + 1) % len(theme_list)]
                        elif self.selected_option == 1:  # Player mode
                            self.player_mode = 4 if self.player_mode == 2 else 2
                        elif self.selected_option == 2:  # Sound
                            self.sound_enabled = not self.sound_enabled
                        elif self.selected_option == 3:  # Back
                            self.game_state = START_SCREEN
                    elif event.key == K_UP:
                        self.selected_option = (self.selected_option - 1) % 4
                    elif event.key == K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 4
                    
            elif self.game_state == GAME_OVER:
                if event.type == KEYDOWN:
                    if event.key == K_r:
                        self.reset_game()
                        self.game_state = PLAYING
                    elif event.key == K_m:
                        self.game_state = START_SCREEN
                    
            elif self.game_state == PLAYING:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE:
                        self.game_state = PAUSED
                    elif event.key == K_s:
                        self.save_game()
                
                if self.all_coins_still and not self.striker.is_shooting:
                    if event.type == MOUSEBUTTONDOWN:
                        if event.button == 1:  # Left click
                            if not self.striker.is_positioned:
                                self.striker.is_positioned = True
                                self.striker.position(event.pos[0])
                            elif self.striker.is_aiming:
                                # Start setting power
                                pass
                        elif event.button == 3 and self.striker.is_positioned:  # Right click
                            self.striker.is_aiming = True
                            
                    if event.type == MOUSEMOTION:
                        if self.striker.is_positioned and not self.striker.is_aiming:
                            self.striker.position(event.pos[0])
                        elif self.striker.is_aiming:
                            self.striker.aim(event.pos[0], event.pos[1])
                            if pygame.mouse.get_pressed()[0]:  # Left button held
                                # Calculate power based on distance
                                dx = event.pos[0] - self.striker.x
                                dy = event.pos[1] - self.striker.y
                                distance = min(math.sqrt(dx*dx + dy*dy), 100)
                                self.striker.set_power(distance)
                                
                    if event.type == MOUSEBUTTONUP:
                        if event.button == 1 and self.striker.is_aiming:  # Left button released
                            if self.striker.power > 0:
                                self.striker.shoot()
                                self.foul_count += 1  # Increment foul count, will be reset if valid shot
                                
            elif self.game_state == PAUSED:
                if event.type == KEYDOWN:
                    if event.key == K_ESCAPE or event.key == K_p:
                        self.game_state = PLAYING
                    elif event.key == K_s:
                        self.save_game()
                    elif event.key == K_m:
                        self.game_state = START_SCREEN

    def update(self):
        """Update game state"""
        if self.game_state != PLAYING:
            return
            
        # Update striker
        self.striker.update()
        
        # Check if striker is pocketed
        if self.striker.check_pocket(self.pockets):
            self.handle_foul("Striker pocketed!")
            self.striker.is_shooting = False
            return
            
        # Update coins
        for coin in self.coins:
            coin.update()
            
        # Check coin-coin collisions
        for i in range(len(self.coins)):
            # Check collision with striker
            if not self.coins[i].is_pocketed:
                self.striker.check_collision(self.coins[i])
                
            # Check collision with other coins
            for j in range(i + 1, len(self.coins)):
                if not self.coins[i].is_pocketed and not self.coins[j].is_pocketed:
                    self.coins[i].check_collision(self.coins[j])
                    
        # Check if coins are pocketed
        for coin in self.coins:
            if coin.check_pocket(self.pockets):
                self.handle_pocketed_coin(coin)
                
        # Check if all pieces have stopped moving
        self.all_coins_still = (self.striker.velocity_x == 0 and self.striker.velocity_y == 0)
        for coin in self.coins:
            if not coin.is_pocketed and (coin.velocity_x != 0 or coin.velocity_y != 0):
                self.all_coins_still = False
                break
                
        # If all pieces have stopped, prepare for next turn
        if self.all_coins_still and self.striker.is_shooting:
            self.striker.is_shooting = False
            self.check_turn_end()
            
        # Check for game over
        self.check_game_over()

    def handle_pocketed_coin(self, coin):
        """Handle scoring when a coin is pocketed"""
        if coin.is_queen:
            self.queen_pocketed = True
            self.last_pocketed_queen = True
            self.turn_message = f"Player {self.current_player} pocketed the Queen! Must cover it."
            self.foul_count = 0  # Reset foul count on successful pocket
            return
            
        # Regular coin pocketed
        if coin.color == WHITE and self.current_player == 1:
            # Player 1 pocketed their coin
            self.player1_score += 1
            self.turn_message = "Player 1 pocketed a white coin!"
            self.foul_count = 0  # Reset foul count
            
            # Check if queen is covered
            if self.last_pocketed_queen:
                self.queen_covered = True
                self.player1_score += 3  # Bonus for covering queen
                self.turn_message = "Player 1 covered the Queen! +3 points"
                self.last_pocketed_queen = False
                
        elif coin.color == BLACK and self.current_player == 2:
            # Player 2 pocketed their coin
            self.player2_score += 1
            self.turn_message = "Player 2 pocketed a black coin!"
            self.foul_count = 0  # Reset foul count
            
            # Check if queen is covered
            if self.last_pocketed_queen:
                self.queen_covered = True
                self.player2_score += 3  # Bonus for covering queen
                self.turn_message = "Player 2 covered the Queen! +3 points"
                self.last_pocketed_queen = False
                
        else:
            # Player pocketed opponent's coin
            self.handle_foul(f"Player {self.current_player} pocketed opponent's coin!")

    def handle_foul(self, message):
        """Handle foul situations"""
        self.turn_message = message
        
        # If queen was pocketed but not covered, return it to the board
        if self.last_pocketed_queen and not self.queen_covered:
            for coin in self.coins:
                if coin.is_queen:
                    coin.is_pocketed = False
                    # Place queen at center if possible, or find empty spot
                    coin.x = SCREEN_WIDTH // 2
                    coin.y = SCREEN_HEIGHT // 2
                    self.last_pocketed_queen = False
                    break
                    
        # Switch player's turn
        self.current_player = 3 - self.current_player  # Toggle between 1 and 2
        self.striker.reset_position(self.current_player)

    def check_turn_end(self):
        """Check if the current turn should end"""
        # If no coins were pocketed or a foul occurred, switch turns
        if self.foul_count >= 3:
            self.handle_foul(f"Player {self.current_player} committed 3 consecutive fouls!")
            self.foul_count = 0
        elif self.foul_count > 0:
            # No coins were pocketed, switch turns
            self.current_player = 3 - self.current_player
            self.striker.reset_position(self.current_player)
            self.turn_message = f"Player {self.current_player}'s turn"
            
        # Reset foul count if a coin was pocketed (handled in handle_pocketed_coin)

    def check_game_over(self):
        """Check if the game is over"""
        # Count remaining coins for each player
        white_coins = 0
        black_coins = 0
        
        for coin in self.coins:
            if not coin.is_pocketed:
                if coin.color == WHITE:
                    white_coins += 1
                elif coin.color == BLACK:
                    black_coins += 1
                    
        # Game is over if one player has no coins left
        if white_coins == 0:
            self.winner = 1
            self.game_state = GAME_OVER
        elif black_coins == 0:
            self.winner = 2
            self.game_state = GAME_OVER

    def draw(self):
        """Draw the game"""
        self.screen.fill(BROWN)
        
        if self.game_state == START_SCREEN:
            self.draw_start_screen()
        elif self.game_state == SETTINGS_SCREEN:
            self.draw_settings_screen()
        elif self.game_state == GAME_OVER:
            self.draw_game_over_screen()
        elif self.game_state == PAUSED:
            self.draw_paused_screen()
        else:
            self.draw_board()
            self.draw_coins()
            self.draw_striker()
            self.draw_ui()
            
        pygame.display.flip()

    def draw_start_screen(self):
        """Draw the start screen"""
        # Background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BOARD_BORDER)
        
        # Draw a simplified board in the background
        board_size = 400
        board_margin = (SCREEN_WIDTH - board_size) // 2
        pygame.draw.rect(overlay, LIGHT_BROWN, (board_margin, board_margin, board_size, board_size))
        
        # Title
        title = self.title_font.render("CARROM BOARD GAME", True, WHITE)
        self.screen.blit(overlay, (0, 0))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
        
        # Menu options
        start_text = self.font.render("Press SPACE to Start", True, WHITE)
        settings_text = self.font.render("Press S for Settings", True, WHITE)
        load_text = self.font.render("Press L to Load Game", True, WHITE)
        
        self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
        self.screen.blit(settings_text, (SCREEN_WIDTH // 2 - settings_text.get_width() // 2, 350))
        self.screen.blit(load_text, (SCREEN_WIDTH // 2 - load_text.get_width() // 2, 400))
        
        # Game mode info
        mode_text = self.small_font.render(f"Current Mode: {self.player_mode}-Player", True, WHITE)
        theme_text = self.small_font.render(f"Theme: {self.current_theme}", True, WHITE)
        
        self.screen.blit(mode_text, (SCREEN_WIDTH // 2 - mode_text.get_width() // 2, 500))
        self.screen.blit(theme_text, (SCREEN_WIDTH // 2 - theme_text.get_width() // 2, 530))

    def draw_settings_screen(self):
        """Draw the settings screen"""
        # Background
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(DARK_GRAY)
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.title_font.render("SETTINGS", True, WHITE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 100))
        
        # Settings options
        options = [
            f"Theme: {self.current_theme}",
            f"Player Mode: {self.player_mode}-Player",
            f"Sound: {'On' if self.sound_enabled else 'Off'}",
            "Back to Main Menu"
        ]
        
        y_pos = 250
        for i, option in enumerate(options):
            color = YELLOW if i == self.selected_option else WHITE
            option_text = self.font.render(option, True, color)
            self.screen.blit(option_text, (SCREEN_WIDTH // 2 - option_text.get_width() // 2, y_pos))
            y_pos += 60
            
        # Instructions
        instructions = self.small_font.render("Use UP/DOWN to navigate, ENTER to select, ESC to go back", True, LIGHT_GRAY)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 600))
        
    def draw_paused_screen(self):
        """Draw the paused screen overlay"""
        # Draw the game in the background
        self.draw_board()
        self.draw_coins()
        self.draw_striker()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        paused = self.title_font.render("GAME PAUSED", True, WHITE)
        continue_text = self.font.render("Press ESC or P to Continue", True, WHITE)
        save_text = self.font.render("Press S to Save Game", True, WHITE)
        menu_text = self.font.render("Press M for Main Menu", True, WHITE)
        
        self.screen.blit(paused, (SCREEN_WIDTH // 2 - paused.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(continue_text, (SCREEN_WIDTH // 2 - continue_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(save_text, (SCREEN_WIDTH // 2 - save_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 + 100))

    def draw_game_over_screen(self):
        """Draw the game over screen"""
        self.draw_board()
        self.draw_coins()
        
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over = self.title_font.render("GAME OVER", True, WHITE)
        
        if self.player_mode == 2:
            winner_text = self.font.render(f"Player {self.winner} Wins!", True, WHITE)
            score_text = self.font.render(f"Score: Player 1: {self.player1_score} - Player 2: {self.player2_score}", True, WHITE)
        else:  # 4-player mode
            if self.winner <= 2:
                winner_text = self.font.render(f"Team 1 Wins!", True, WHITE)
            else:
                winner_text = self.font.render(f"Team 2 Wins!", True, WHITE)
            score_text = self.font.render(f"Score: Team 1: {self.player1_score + self.player3_score} - Team 2: {self.player2_score + self.player4_score}", True, WHITE)
        
        restart = self.font.render("Press R to Restart", True, WHITE)
        menu = self.font.render("Press M for Main Menu", True, WHITE)
        
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        self.screen.blit(winner_text, (SCREEN_WIDTH // 2 - winner_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(menu, (SCREEN_WIDTH // 2 - menu.get_width() // 2, SCREEN_HEIGHT // 2 + 120))

    def draw_board(self):
        """Draw the carrom board"""
        theme = THEMES[self.current_theme]
        board_margin = (SCREEN_WIDTH - BOARD_SIZE) // 2
        center_x = SCREEN_WIDTH // 2
        center_y = SCREEN_HEIGHT // 2
        
        # Draw board background (outer border)
        pygame.draw.rect(self.screen, theme["border"], (board_margin - 20, board_margin - 20, 
                                                    BOARD_SIZE + 40, BOARD_SIZE + 40))
        
        # Draw board main surface
        pygame.draw.rect(self.screen, theme["board"], (board_margin, board_margin, BOARD_SIZE, BOARD_SIZE))
        
        # Draw inner border
        inner_margin = 20
        pygame.draw.rect(self.screen, theme["lines"], (board_margin + inner_margin, board_margin + inner_margin, 
                                             BOARD_SIZE - 2*inner_margin, BOARD_SIZE - 2*inner_margin), 2)
        
        # Draw diagonal lines connecting corners
        pygame.draw.line(self.screen, theme["lines"], 
                        (board_margin + inner_margin, board_margin + inner_margin), 
                        (board_margin + BOARD_SIZE - inner_margin, board_margin + BOARD_SIZE - inner_margin), 2)
        pygame.draw.line(self.screen, theme["lines"], 
                        (board_margin + BOARD_SIZE - inner_margin, board_margin + inner_margin), 
                        (board_margin + inner_margin, board_margin + BOARD_SIZE - inner_margin), 2)
        
        # 1. Draw large red circle at center (approx 3 inches diameter)
        # Assuming 1 inch = 25 pixels, so 3 inches = 75 pixels
        pygame.draw.circle(self.screen, RED, (center_x, center_y), 75, 0)
        
        # Draw center circle outline
        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 75, 2)
        
        # 2. Draw star/compass design with 8 equal sections
        for i in range(8):
            angle = i * math.pi / 4
            # Draw lines from center to edge of red circle
            x2 = center_x + 75 * math.cos(angle)
            y2 = center_y + 75 * math.sin(angle)
            pygame.draw.line(self.screen, BLACK, (center_x, center_y), (x2, y2), 2)
        
        # 3. Draw small red dot at exact center
        pygame.draw.circle(self.screen, RED, (center_x, center_y), 5, 0)
        pygame.draw.circle(self.screen, BLACK, (center_x, center_y), 5, 1)
        
        # 4. Draw Player's Playing Areas (Rectangular Striking Zones with curved corners) on all four sides
        # Common dimensions
        rect_length = 460  # Width of rectangle (slightly shorter to fit inside border)
        rect_width = 30    # Height of rectangle (approx 1-2 inches)
        inset = 60         # Distance from edge (well inside outer and inner border)
        
        # Define rectangles for all four sides
        # Bottom (Player 1)
        p1_x = center_x - rect_length // 2
        p1_y = SCREEN_HEIGHT - board_margin - inset
        
        # Top (Player 2)
        p2_x = p1_x
        p2_y = board_margin + inset - rect_width
        
        # Left (Player 3)
        p3_x = board_margin + inset - rect_width
        p3_y = center_y - rect_length // 2
        
        # Right (Player 4)
        p4_x = SCREEN_WIDTH - board_margin - inset
        p4_y = p3_y
        
        # Draw the rectangles with rounded corners for all four sides
        # Horizontal rectangles (Players 1 & 2)
        for x, y in [(p1_x, p1_y), (p2_x, p2_y)]:
            # Draw the outlines with curved corners
            # Top and bottom straight lines
            pygame.draw.line(self.screen, BLACK, (x + rect_width//2, y), (x + rect_length - rect_width//2, y), 2)
            pygame.draw.line(self.screen, BLACK, (x + rect_width//2, y + rect_width), (x + rect_length - rect_width//2, y + rect_width), 2)
            
            # Left and right curved corners
            # Left top arc
            pygame.draw.arc(self.screen, BLACK, (x, y, rect_width, rect_width), math.pi/2, math.pi, 2)
            # Left bottom arc
            pygame.draw.arc(self.screen, BLACK, (x, y, rect_width, rect_width), math.pi, 3*math.pi/2, 2)
            # Right top arc
            pygame.draw.arc(self.screen, BLACK, (x + rect_length - rect_width, y, rect_width, rect_width), 0, math.pi/2, 2)
            # Right bottom arc
            pygame.draw.arc(self.screen, BLACK, (x + rect_length - rect_width, y, rect_width, rect_width), 3*math.pi/2, 2*math.pi, 2)
            
            # Red circles at both ends
            circle_radius = 15  # approx 1 inch diameter
            pygame.draw.circle(self.screen, RED, (x + rect_width//2, y + rect_width//2), circle_radius, 0)
            pygame.draw.circle(self.screen, BLACK, (x + rect_width//2, y + rect_width//2), circle_radius, 1)
            
            pygame.draw.circle(self.screen, RED, (x + rect_length - rect_width//2, y + rect_width//2), circle_radius, 0)
            pygame.draw.circle(self.screen, BLACK, (x + rect_length - rect_width//2, y + rect_width//2), circle_radius, 1)
            
            # Arrows extending inward from the red circles
            arrow_length = 20
            
            # Left circle arrow
            left_arrow_start = (x + rect_width//2, y + rect_width//2)
            left_arrow_end = (left_arrow_start[0] + arrow_length, left_arrow_start[1])
            pygame.draw.line(self.screen, BLACK, left_arrow_start, left_arrow_end, 2)
            # Arrow head
            pygame.draw.line(self.screen, BLACK, left_arrow_end, 
                            (left_arrow_end[0] - 5, left_arrow_end[1] - 5), 2)
            pygame.draw.line(self.screen, BLACK, left_arrow_end, 
                            (left_arrow_end[0] - 5, left_arrow_end[1] + 5), 2)
            
            # Right circle arrow
            right_arrow_start = (x + rect_length - rect_width//2, y + rect_width//2)
            right_arrow_end = (right_arrow_start[0] - arrow_length, right_arrow_start[1])
            pygame.draw.line(self.screen, BLACK, right_arrow_start, right_arrow_end, 2)
            # Arrow head
            pygame.draw.line(self.screen, BLACK, right_arrow_end, 
                            (right_arrow_end[0] + 5, right_arrow_end[1] - 5), 2)
            pygame.draw.line(self.screen, BLACK, right_arrow_end, 
                            (right_arrow_end[0] + 5, right_arrow_end[1] + 5), 2)
        
        # Vertical rectangles (Players 3 & 4)
        for x, y in [(p3_x, p3_y), (p4_x, p4_y)]:
            # Draw the outlines with curved corners
            # Left and right straight lines
            pygame.draw.line(self.screen, BLACK, (x, y + rect_width//2), (x, y + rect_length - rect_width//2), 2)
            pygame.draw.line(self.screen, BLACK, (x + rect_width, y + rect_width//2), (x + rect_width, y + rect_length - rect_width//2), 2)
            
            # Top and bottom curved corners
            # Top left arc
            pygame.draw.arc(self.screen, BLACK, (x, y, rect_width, rect_width), math.pi, 3*math.pi/2, 2)
            # Top right arc
            pygame.draw.arc(self.screen, BLACK, (x, y, rect_width, rect_width), 3*math.pi/2, 2*math.pi, 2)
            # Bottom left arc
            pygame.draw.arc(self.screen, BLACK, (x, y + rect_length - rect_width, rect_width, rect_width), math.pi/2, math.pi, 2)
            # Bottom right arc
            pygame.draw.arc(self.screen, BLACK, (x, y + rect_length - rect_width, rect_width, rect_width), 0, math.pi/2, 2)
            
            # Red circles at both ends
            circle_radius = 15  # approx 1 inch diameter
            pygame.draw.circle(self.screen, RED, (x + rect_width//2, y + rect_width//2), circle_radius, 0)
            pygame.draw.circle(self.screen, BLACK, (x + rect_width//2, y + rect_width//2), circle_radius, 1)
            
            pygame.draw.circle(self.screen, RED, (x + rect_width//2, y + rect_length - rect_width//2), circle_radius, 0)
            pygame.draw.circle(self.screen, BLACK, (x + rect_width//2, y + rect_length - rect_width//2), circle_radius, 1)
            
            # Arrows extending inward from the red circles
            arrow_length = 20
            
            # Top circle arrow
            top_arrow_start = (x + rect_width//2, y + rect_width//2)
            top_arrow_end = (top_arrow_start[0], top_arrow_start[1] + arrow_length)
            pygame.draw.line(self.screen, BLACK, top_arrow_start, top_arrow_end, 2)
            # Arrow head
            pygame.draw.line(self.screen, BLACK, top_arrow_end, 
                            (top_arrow_end[0] - 5, top_arrow_end[1] - 5), 2)
            pygame.draw.line(self.screen, BLACK, top_arrow_end, 
                            (top_arrow_end[0] + 5, top_arrow_end[1] - 5), 2)
            
            # Bottom circle arrow
            bottom_arrow_start = (x + rect_width//2, y + rect_length - rect_width//2)
            bottom_arrow_end = (bottom_arrow_start[0], bottom_arrow_start[1] - arrow_length)
            pygame.draw.line(self.screen, BLACK, bottom_arrow_start, bottom_arrow_end, 2)
            # Arrow head
            pygame.draw.line(self.screen, BLACK, bottom_arrow_end, 
                            (bottom_arrow_end[0] - 5, bottom_arrow_end[1] + 5), 2)
            pygame.draw.line(self.screen, BLACK, bottom_arrow_end, 
                            (bottom_arrow_end[0] + 5, bottom_arrow_end[1] + 5), 2)
        
        # Draw arrow circles in each quadrant with directional arrows
        quadrant_centers = [
            (center_x - BOARD_SIZE//4, center_y - BOARD_SIZE//4),
            (center_x + BOARD_SIZE//4, center_y - BOARD_SIZE//4),
            (center_x - BOARD_SIZE//4, center_y + BOARD_SIZE//4),
            (center_x + BOARD_SIZE//4, center_y + BOARD_SIZE//4)
        ]
        
        arrow_directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]  # Direction for each quadrant
        
        for i, qc in enumerate(quadrant_centers):
            # Draw circle
            pygame.draw.circle(self.screen, theme["lines"], qc, 30, 1)
            
            # Draw arrow inside circle
            dx, dy = arrow_directions[i]
            arrow_start = (qc[0] - dx * 15, qc[1] - dy * 15)
            arrow_end = (qc[0] + dx * 15, qc[1] + dy * 15)
            pygame.draw.line(self.screen, theme["accent"], arrow_start, arrow_end, 2)
            
            # Arrow head
            head_size = 5
            angle = math.atan2(dy, dx)
            head1 = (arrow_end[0] - head_size * math.cos(angle - math.pi/4),
                     arrow_end[1] - head_size * math.sin(angle - math.pi/4))
            head2 = (arrow_end[0] - head_size * math.cos(angle + math.pi/4),
                     arrow_end[1] - head_size * math.sin(angle + math.pi/4))
            pygame.draw.line(self.screen, theme["accent"], arrow_end, head1, 2)
            pygame.draw.line(self.screen, theme["accent"], arrow_end, head2, 2)
        
        # Draw pockets (black circles in corners)
        for pocket in self.pockets:
            # Outer pocket circle
            pygame.draw.circle(self.screen, BLACK, pocket, POCKET_RADIUS, 0)
            # Inner pocket detail
            pygame.draw.circle(self.screen, (20, 20, 20), pocket, POCKET_RADIUS - 8, 0)

    def draw_coins(self):
        """Draw all coins"""
        for coin in self.coins:
            coin.draw(self.screen)

    def draw_striker(self):
        """Draw the striker"""
        self.striker.draw(self.screen)

    def draw_ui(self):
        """Draw UI elements"""
        theme = THEMES[self.current_theme]
        
        # Draw scores
        if self.player_mode == 2:
            # Two-player mode
            p1_score = self.font.render(f"Player 1: {self.player1_score}", True, WHITE)
            p2_score = self.font.render(f"Player 2: {self.player2_score}", True, BLACK)
            
            self.screen.blit(p1_score, (20, 20))
            self.screen.blit(p2_score, (SCREEN_WIDTH - p2_score.get_width() - 20, 20))
        else:
            # Four-player mode (teams)
            team1_score = self.font.render(f"Team 1: {self.player1_score + self.player3_score}", True, WHITE)
            team2_score = self.font.render(f"Team 2: {self.player2_score + self.player4_score}", True, BLACK)
            
            self.screen.blit(team1_score, (20, 20))
            self.screen.blit(team2_score, (SCREEN_WIDTH - team2_score.get_width() - 20, 20))
        
        # Draw current player indicator
        current = self.font.render(f"Current Player: {self.current_player}", True, theme["accent"])
        self.screen.blit(current, (SCREEN_WIDTH // 2 - current.get_width() // 2, 20))
        
        # Draw turn message
        if self.turn_message:
            message = self.small_font.render(self.turn_message, True, theme["accent"])
            self.screen.blit(message, (SCREEN_WIDTH // 2 - message.get_width() // 2, SCREEN_HEIGHT - 30))
            
        # Draw game controls help
        controls = self.small_font.render("ESC: Pause | S: Save Game", True, WHITE)
        self.screen.blit(controls, (SCREEN_WIDTH - controls.get_width() - 20, SCREEN_HEIGHT - 30))

    def save_game(self):
        """Save the current game state to a file"""
        try:
            import pickle
            
            game_state = {
                'player_mode': self.player_mode,
                'current_theme': self.current_theme,
                'current_player': self.current_player,
                'player1_score': self.player1_score,
                'player2_score': self.player2_score,
                'player3_score': self.player3_score,
                'player4_score': self.player4_score,
                'queen_pocketed': self.queen_pocketed,
                'queen_covered': self.queen_covered,
                'last_pocketed_queen': self.last_pocketed_queen,
                'coins': [(c.x, c.y, c.color, c.is_queen, c.is_pocketed) for c in self.coins],
                'striker_pos': (self.striker.x, self.striker.y)
            }
            
            with open('carrom_save.dat', 'wb') as f:
                pickle.dump(game_state, f)
                
            self.game_saved = True
            self.turn_message = "Game saved successfully!"
            
        except Exception as e:
            self.turn_message = f"Error saving game: {str(e)}"
            
    def load_game(self):
        """Load a saved game state from a file"""
        try:
            import pickle
            import os
            
            if not os.path.exists('carrom_save.dat'):
                self.turn_message = "No saved game found!"
                return
                
            with open('carrom_save.dat', 'rb') as f:
                game_state = pickle.load(f)
                
            # Reset and apply saved state
            self.reset_game()
            
            self.player_mode = game_state['player_mode']
            self.current_theme = game_state['current_theme']
            self.current_player = game_state['current_player']
            self.player1_score = game_state['player1_score']
            self.player2_score = game_state['player2_score']
            self.player3_score = game_state['player3_score']
            self.player4_score = game_state['player4_score']
            self.queen_pocketed = game_state['queen_pocketed']
            self.queen_covered = game_state['queen_covered']
            self.last_pocketed_queen = game_state['last_pocketed_queen']
            
            # Recreate coins
            self.coins = []
            for c_data in game_state['coins']:
                x, y, color, is_queen, is_pocketed = c_data
                coin = Coin(x, y, color, is_queen)
                coin.is_pocketed = is_pocketed
                self.coins.append(coin)
                
            # Set striker position
            self.striker.x, self.striker.y = game_state['striker_pos']
            
            self.game_state = PLAYING
            self.turn_message = "Game loaded successfully!"
            
        except Exception as e:
            self.turn_message = f"Error loading game: {str(e)}"
            self.game_state = START_SCREEN

    def run(self):
        """Main game loop"""
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = CarromGame()
    game.run()
