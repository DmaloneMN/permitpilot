#!/usr/bin/env python3
"""
American Football GUI Game - Roblox Prototype
A complete football game with Pygame
"""

import pygame
import random
import math
import sys

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
LIGHT_GREEN = (50, 205, 50)
BROWN = (139, 69, 19)
BLUE = (0, 0, 255)
LIGHT_BLUE = (135, 206, 250)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
SKY_BLUE = (135, 206, 235)

# Team colors
EAGLES_PRIMARY = (0, 76, 84)
EAGLES_SECONDARY = (165, 172, 175)
CHIEFS_PRIMARY = (227, 24, 55)
CHIEFS_SECONDARY = (255, 184, 28)

# Game setup
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("American Football - Roblox Prototype")

# Try to load system fonts with fallback
try:
    FONT_LARGE = pygame.font.SysFont("Segoe UI,Arial,Helvetica", 48, bold=True)
    FONT_MEDIUM = pygame.font.SysFont("Segoe UI,Arial,Helvetica", 32, bold=True)
    FONT_SMALL = pygame.font.SysFont("Segoe UI,Arial,Helvetica", 24)
    FONT_TINY = pygame.font.SysFont("Segoe UI,Arial,Helvetica", 16)
    FONT_MICRO = pygame.font.SysFont("Segoe UI,Arial,Helvetica", 12)
except:
    FONT_LARGE = pygame.font.Font(None, 48)
    FONT_MEDIUM = pygame.font.Font(None, 32)
    FONT_SMALL = pygame.font.Font(None, 24)
    FONT_TINY = pygame.font.Font(None, 16)
    FONT_MICRO = pygame.font.Font(None, 12)

# Sound generation functions
def generate_sound(frequency, duration, volume=0.3):
    """Generate a simple sine wave sound"""
    sample_rate = 22050
    n_samples = int(round(duration * sample_rate))
    
    # Generate sine wave
    buf = []
    for i in range(n_samples):
        value = int(volume * 32767 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
        buf.append([value, value])
    
    sound = pygame.sndarray.make_sound(buf)
    return sound

def generate_noise(duration, volume=0.2):
    """Generate white noise"""
    sample_rate = 22050
    n_samples = int(round(duration * sample_rate))
    
    buf = []
    for i in range(n_samples):
        value = int(volume * 32767 * (random.random() * 2 - 1))
        buf.append([value, value])
    
    sound = pygame.sndarray.make_sound(buf)
    return sound

# Create sounds
SOUNDS = {
    'whistle': generate_sound(2000, 0.3, 0.3),
    'crowd': generate_noise(0.5, 0.15),
    'hit': generate_noise(0.1, 0.25),
    'kick': generate_sound(150, 0.15, 0.25),
    'snap': generate_sound(100, 0.05, 0.2),
    'click': generate_sound(800, 0.05, 0.15),
}

def play_sound(sound_name):
    """Play a sound if it exists"""
    if sound_name in SOUNDS:
        SOUNDS[sound_name].play()

def play_touchdown_fanfare():
    """Play ascending notes for touchdown"""
    frequencies = [262, 330, 392, 523]  # C, E, G, C
    for freq in frequencies:
        sound = generate_sound(freq, 0.15, 0.2)
        sound.play()
        pygame.time.wait(100)

def play_throw_sound():
    """Ascending whoosh"""
    sound = generate_sound(200, 0.2, 0.15)
    sound.play()

def play_catch_sound():
    """Two-tone pop"""
    sound1 = generate_sound(400, 0.1, 0.15)
    sound2 = generate_sound(300, 0.1, 0.15)
    sound1.play()
    pygame.time.wait(50)
    sound2.play()

# Particle system
class Particle:
    def __init__(self, x, y, vx, vy, color, lifetime):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.lifetime = lifetime
        self.age = 0
    
    def update(self, dt):
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += 500 * dt  # Gravity
        self.age += dt
    
    def draw(self, surface):
        if self.age < self.lifetime:
            alpha = int(255 * (1 - self.age / self.lifetime))
            color = (*self.color[:3], alpha)
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), 3)
    
    def is_alive(self):
        return self.age < self.lifetime

class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def emit(self, x, y, count, color_list):
        for _ in range(count):
            vx = random.uniform(-200, 200)
            vy = random.uniform(-300, -100)
            color = random.choice(color_list)
            self.particles.append(Particle(x, y, vx, vy, color, random.uniform(1.0, 2.0)))
    
    def update(self, dt):
        self.particles = [p for p in self.particles if p.is_alive()]
        for p in self.particles:
            p.update(dt)
    
    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)

# Floating text
class FloatingText:
    def __init__(self, text, x, y, color, font, duration=2.0):
        self.text = text
        self.x = x
        self.y = y
        self.start_y = y
        self.color = color
        self.font = font
        self.duration = duration
        self.age = 0
    
    def update(self, dt):
        self.age += dt
        self.y = self.start_y - (self.age / self.duration) * 50
    
    def draw(self, surface):
        if self.age < self.duration:
            alpha = int(255 * (1 - self.age / self.duration))
            text_surf = self.font.render(self.text, True, self.color)
            text_surf.set_alpha(alpha)
            surface.blit(text_surf, (self.x - text_surf.get_width() // 2, int(self.y)))
    
    def is_alive(self):
        return self.age < self.duration

# Global game state
class GameState:
    def __init__(self):
        # Teams
        self.home_name = "EAGLES"
        self.away_name = "CHIEFS"
        self.home_score = 0
        self.away_score = 0
        self.home_timeouts = 3
        self.away_timeouts = 3
        
        # Game clock
        self.quarter = 1
        self.game_clock = 15 * 60  # 15 minutes in seconds
        
        # Possession
        self.possession = "home"  # "home" or "away"
        self.ball_on = 25  # Yard line (0-100)
        self.down = 1
        self.yards_to_go = 10
        self.yards_to_first = 35  # Line to gain
        
        # Game status
        self.total_plays = 0
        self.game_over = False
        
        # Current play
        self.offensive_play = None
        self.defensive_play = None
        
    def flip_possession(self):
        self.possession = "away" if self.possession == "home" else "home"
        self.down = 1
        self.yards_to_go = 10
    
    def new_set_of_downs(self, yard_line):
        self.down = 1
        self.ball_on = yard_line
        self.yards_to_go = 10
        self.yards_to_first = min(100, yard_line + 10)
    
    def next_down(self):
        self.down += 1
    
    def is_user_team(self):
        return self.possession == "home"
    
    def get_team_color(self, team):
        if team == "home":
            return EAGLES_PRIMARY
        else:
            return CHIEFS_PRIMARY
    
    def advance_quarter(self):
        self.quarter += 1
        self.game_clock = 15 * 60
        if self.quarter == 3:
            # Halftime - receiving team switches
            self.home_timeouts = 3
            self.away_timeouts = 3

# Field rendering
class Field:
    def __init__(self):
        self.field_rect = pygame.Rect(100, 150, 1000, 500)
        self.cached_crowd = None
    
    def draw_stadium(self, surface):
        """Draw stadium background with stands, lights, etc."""
        # Sky gradient
        for y in range(150):
            color_value = int(135 + (235 - 135) * (y / 150))
            pygame.draw.line(surface, (color_value, 206, 235), (0, y), (WINDOW_WIDTH, y))
        
        # Upper stands
        pygame.draw.rect(surface, DARK_GRAY, (0, 150, 100, 350))
        pygame.draw.rect(surface, DARK_GRAY, (1100, 150, 100, 350))
        
        # Lower stands
        pygame.draw.rect(surface, GRAY, (0, 500, 100, 150))
        pygame.draw.rect(surface, GRAY, (1100, 500, 100, 150))
        
        # Bottom stands behind endzone
        pygame.draw.rect(surface, DARK_GRAY, (100, 650, 1000, 150))
        
        # Press box
        pygame.draw.rect(surface, (50, 50, 50), (450, 100, 300, 50))
        # Windows
        for i in range(6):
            pygame.draw.rect(surface, SKY_BLUE, (465 + i * 45, 110, 35, 30))
        
        # Stadium lights - left
        pygame.draw.line(surface, DARK_GRAY, (50, 150), (50, 50), 5)
        for i in range(3):
            pygame.draw.circle(surface, YELLOW, (50, 60 + i * 30), 8)
            # Glow effect
            pygame.draw.circle(surface, (255, 255, 200, 100), (50, 60 + i * 30), 15, 2)
        
        # Stadium lights - right
        pygame.draw.line(surface, DARK_GRAY, (1150, 150), (1150, 50), 5)
        for i in range(3):
            pygame.draw.circle(surface, YELLOW, (1150, 60 + i * 30), 8)
            pygame.draw.circle(surface, (255, 255, 200, 100), (1150, 60 + i * 30), 15, 2)
        
        # Crowd (use cached version if available)
        if self.cached_crowd is None:
            self.cached_crowd = pygame.Surface((100, 500))
            self.cached_crowd.fill(DARK_GRAY)
            # Left stands crowd
            for _ in range(800):
                x = random.randint(5, 95)
                y = random.randint(0, 490)
                color = random.choice([RED, BLUE, YELLOW, WHITE, GREEN, (255, 165, 0)])
                pygame.draw.circle(self.cached_crowd, color, (x, y), 2)
        
        surface.blit(self.cached_crowd, (0, 150))
        # Mirror for right stands
        right_crowd = pygame.transform.flip(self.cached_crowd, True, False)
        surface.blit(right_crowd, (1100, 150))
        
        # Safety barriers
        pygame.draw.rect(surface, YELLOW, (95, 145, 10, 510), 0)
        pygame.draw.rect(surface, YELLOW, (1095, 145, 10, 510), 0)
    
    def draw_field(self, surface, game_state):
        """Draw the football field"""
        # Field border
        pygame.draw.rect(surface, WHITE, self.field_rect, 3)
        
        # Grass stripes
        stripe_width = self.field_rect.width // 10
        for i in range(10):
            if i % 2 == 0:
                color = GREEN
            else:
                color = DARK_GREEN
            stripe_rect = pygame.Rect(
                self.field_rect.x + i * stripe_width,
                self.field_rect.y,
                stripe_width,
                self.field_rect.height
            )
            pygame.draw.rect(surface, color, stripe_rect)
        
        # Endzones
        # Home endzone (left)
        endzone_width = self.field_rect.width // 12
        home_endzone = pygame.Rect(self.field_rect.x, self.field_rect.y, endzone_width, self.field_rect.height)
        pygame.draw.rect(surface, EAGLES_PRIMARY, home_endzone)
        # Diagonal stripes
        for i in range(-10, 15):
            start_x = home_endzone.x + i * 20
            pygame.draw.line(surface, EAGLES_SECONDARY, 
                           (start_x, home_endzone.y), 
                           (start_x + home_endzone.height, home_endzone.y + home_endzone.height), 3)
        # Text
        text = FONT_SMALL.render("EAGLES", True, WHITE)
        surface.blit(text, (home_endzone.centerx - text.get_width() // 2, home_endzone.centery - text.get_height() // 2))
        
        # Away endzone (right)
        away_endzone = pygame.Rect(self.field_rect.x + self.field_rect.width - endzone_width, 
                                   self.field_rect.y, endzone_width, self.field_rect.height)
        pygame.draw.rect(surface, CHIEFS_PRIMARY, away_endzone)
        # Diagonal stripes
        for i in range(-10, 15):
            start_x = away_endzone.x + i * 20
            pygame.draw.line(surface, CHIEFS_SECONDARY, 
                           (start_x, away_endzone.y), 
                           (start_x + away_endzone.height, away_endzone.y + away_endzone.height), 3)
        # Text
        text = FONT_SMALL.render("CHIEFS", True, WHITE)
        surface.blit(text, (away_endzone.centerx - text.get_width() // 2, away_endzone.centery - text.get_height() // 2))
        
        # Yard lines
        play_area_width = self.field_rect.width - 2 * endzone_width
        play_area_start = self.field_rect.x + endzone_width
        
        for yard in range(0, 101, 5):
            x = play_area_start + (yard / 100) * play_area_width
            if yard % 10 == 0:
                # Bold line every 10 yards
                pygame.draw.line(surface, WHITE, (x, self.field_rect.y), 
                               (x, self.field_rect.bottom), 2)
                # Yard number
                if yard > 0 and yard < 100:
                    number = min(yard, 100 - yard)
                    text = FONT_TINY.render(str(number), True, WHITE)
                    surface.blit(text, (x - text.get_width() // 2, self.field_rect.y + 10))
                    surface.blit(text, (x - text.get_width() // 2, self.field_rect.bottom - 30))
            else:
                # Thin line every 5 yards
                pygame.draw.line(surface, WHITE, (x, self.field_rect.y), 
                               (x, self.field_rect.bottom), 1)
        
        # Hash marks between yard lines
        for yard in range(1, 100):
            x = play_area_start + (yard / 100) * play_area_width
            # Top hash marks
            pygame.draw.line(surface, WHITE, 
                           (x, self.field_rect.y + 100), 
                           (x, self.field_rect.y + 110), 2)
            # Bottom hash marks
            pygame.draw.line(surface, WHITE, 
                           (x, self.field_rect.bottom - 110), 
                           (x, self.field_rect.bottom - 100), 2)
        
        # Line of scrimmage (blue)
        if hasattr(game_state, 'ball_on'):
            los_x = play_area_start + (game_state.ball_on / 100) * play_area_width
            pygame.draw.line(surface, BLUE, (los_x, self.field_rect.y + 5), 
                           (los_x, self.field_rect.bottom - 5), 3)
        
        # First down line (yellow)
        if hasattr(game_state, 'yards_to_first'):
            first_x = play_area_start + (game_state.yards_to_first / 100) * play_area_width
            pygame.draw.line(surface, YELLOW, (first_x, self.field_rect.y + 5), 
                           (first_x, self.field_rect.bottom - 5), 3)
    
    def yard_to_screen_x(self, yard):
        """Convert yard line to screen x coordinate"""
        endzone_width = self.field_rect.width // 12
        play_area_width = self.field_rect.width - 2 * endzone_width
        play_area_start = self.field_rect.x + endzone_width
        return play_area_start + (yard / 100) * play_area_width
    
    def screen_to_yard(self, x):
        """Convert screen x coordinate to yard line"""
        endzone_width = self.field_rect.width // 12
        play_area_width = self.field_rect.width - 2 * endzone_width
        play_area_start = self.field_rect.x + endzone_width
        yard = ((x - play_area_start) / play_area_width) * 100
        return max(0, min(100, yard))

# Player rendering
class Player:
    def __init__(self, x, y, number, position, team, is_user=False):
        self.x = x
        self.y = y
        self.number = number
        self.position = position
        self.team = team
        self.is_user = is_user
        self.target_x = x
        self.target_y = y
        self.has_ball = False
        self.anim_time = random.uniform(0, math.pi * 2)
        
    def update(self, dt):
        # Move towards target
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 2:
            speed = 150
            self.x += (dx / dist) * speed * dt
            self.y += (dy / dist) * speed * dt
        
        self.anim_time += dt * 10
    
    def draw(self, surface, pulse_time=0, is_target=False):
        # Shadow
        pygame.draw.ellipse(surface, (0, 0, 0, 100), 
                          (int(self.x) - 8, int(self.y) + 10, 16, 8))
        
        # Legs (animated)
        leg_offset = int(5 * math.sin(self.anim_time))
        leg_color = BLACK
        pygame.draw.circle(surface, leg_color, (int(self.x) - 3, int(self.y) + 5 + leg_offset), 3)
        pygame.draw.circle(surface, leg_color, (int(self.x) + 3, int(self.y) + 5 - leg_offset), 3)
        
        # Shoes
        pygame.draw.rect(surface, BLACK, (int(self.x) - 5, int(self.y) + 7, 4, 2))
        pygame.draw.rect(surface, BLACK, (int(self.x) + 1, int(self.y) + 7, 4, 2))
        
        # Jersey color
        if self.team == "home":
            jersey_color = EAGLES_PRIMARY
            stripe_color = EAGLES_SECONDARY
        else:
            jersey_color = CHIEFS_PRIMARY
            stripe_color = CHIEFS_SECONDARY
        
        # Body
        pygame.draw.circle(surface, jersey_color, (int(self.x), int(self.y)), 10)
        pygame.draw.rect(surface, stripe_color, (int(self.x) - 10, int(self.y) - 2, 20, 4))
        
        # Arms (animated swing)
        arm_offset = int(5 * math.sin(self.anim_time + math.pi))
        pygame.draw.circle(surface, jersey_color, (int(self.x) - 10, int(self.y) + arm_offset), 4)
        pygame.draw.circle(surface, jersey_color, (int(self.x) + 10, int(self.y) - arm_offset), 4)
        
        # Helmet
        helmet_color = jersey_color
        pygame.draw.circle(surface, helmet_color, (int(self.x), int(self.y) - 10), 8)
        # Facemask
        pygame.draw.arc(surface, GRAY, (int(self.x) - 6, int(self.y) - 14, 12, 10), 3.14, 6.28, 2)
        # Center stripe
        pygame.draw.line(surface, stripe_color, (int(self.x), int(self.y) - 16), (int(self.x), int(self.y) - 4), 2)
        
        # Number on jersey
        num_text = FONT_MICRO.render(str(self.number), True, WHITE)
        surface.blit(num_text, (int(self.x) - num_text.get_width() // 2, int(self.y) - 3))
        
        # Position label
        pos_text = FONT_MICRO.render(self.position, True, WHITE)
        surface.blit(pos_text, (int(self.x) - pos_text.get_width() // 2, int(self.y) + 12))
        
        # User indicator (pulsing yellow ring)
        if self.is_user:
            pulse = int(50 + 50 * math.sin(pulse_time * 5))
            pygame.draw.circle(surface, (255, 255, pulse), (int(self.x), int(self.y)), 15, 2)
            you_text = FONT_TINY.render("YOU", True, YELLOW)
            surface.blit(you_text, (int(self.x) - you_text.get_width() // 2, int(self.y) - 30))
        
        # Target indicator (pulsing green ring)
        if is_target:
            pulse = int(100 + 100 * math.sin(pulse_time * 5))
            pygame.draw.circle(surface, (0, pulse, 0), (int(self.x), int(self.y)), 17, 2)
            target_text = FONT_TINY.render("TARGET", True, GREEN)
            surface.blit(target_text, (int(self.x) - target_text.get_width() // 2, int(self.y) - 35))
        
        # Ball carrier indicator
        if self.has_ball:
            # Football on shoulder
            pygame.draw.ellipse(surface, BROWN, (int(self.x) + 8, int(self.y) - 5, 8, 5))
            pygame.draw.line(surface, WHITE, (int(self.x) + 10, int(self.y) - 3), 
                           (int(self.x) + 14, int(self.y) - 3), 1)

# Formation setup
def create_offensive_formation(game_state, field):
    """Create 11 offensive players"""
    los_x = field.yard_to_screen_x(game_state.ball_on)
    center_y = field.field_rect.centery
    
    players = []
    
    # Offensive line (5 players)
    players.append(Player(los_x, center_y, 50, "C", game_state.possession))  # Center
    players.append(Player(los_x, center_y - 30, 67, "LG", game_state.possession))  # Left Guard
    players.append(Player(los_x, center_y + 30, 72, "RG", game_state.possession))  # Right Guard
    players.append(Player(los_x, center_y - 60, 74, "LT", game_state.possession))  # Left Tackle
    players.append(Player(los_x, center_y + 60, 79, "RT", game_state.possession))  # Right Tackle
    
    # QB (user controlled)
    qb = Player(los_x - 40, center_y, 12, "QB", game_state.possession, is_user=True)
    players.append(qb)
    
    # Running back
    players.append(Player(los_x - 60, center_y, 22, "RB", game_state.possession))
    
    # Fullback
    players.append(Player(los_x - 50, center_y + 15, 33, "FB", game_state.possession))
    
    # Wide receivers
    players.append(Player(los_x, center_y - 120, 80, "WR", game_state.possession))
    players.append(Player(los_x, center_y + 120, 88, "WR", game_state.possession))
    
    # Tight end
    players.append(Player(los_x, center_y + 75, 84, "TE", game_state.possession))
    
    return players, qb

def create_defensive_formation(game_state, field):
    """Create 11 defensive players"""
    los_x = field.yard_to_screen_x(game_state.ball_on)
    center_y = field.field_rect.centery
    
    defense_team = "away" if game_state.possession == "home" else "home"
    players = []
    
    # Defensive line (4 players)
    players.append(Player(los_x + 20, center_y - 35, 90, "DL", defense_team))
    players.append(Player(los_x + 20, center_y - 10, 95, "DL", defense_team))
    players.append(Player(los_x + 20, center_y + 10, 97, "DL", defense_team))
    players.append(Player(los_x + 20, center_y + 35, 99, "DL", defense_team))
    
    # Linebackers (3 players)
    players.append(Player(los_x + 50, center_y - 50, 51, "LB", defense_team))
    players.append(Player(los_x + 50, center_y, 54, "MLB", defense_team))
    players.append(Player(los_x + 50, center_y + 50, 58, "LB", defense_team))
    
    # Cornerbacks (2 players)
    players.append(Player(los_x + 30, center_y - 120, 21, "CB", defense_team))
    players.append(Player(los_x + 30, center_y + 120, 24, "CB", defense_team))
    
    # Safeties (2 players)
    players.append(Player(los_x + 100, center_y - 40, 41, "FS", defense_team))
    players.append(Player(los_x + 100, center_y + 40, 43, "SS", defense_team))
    
    return players

# HUD
def draw_hud(surface, game_state):
    """Draw scoreboard and game info"""
    # Home team box
    home_rect = pygame.Rect(50, 10, 250, 80)
    pygame.draw.rect(surface, EAGLES_PRIMARY, home_rect)
    pygame.draw.rect(surface, WHITE, home_rect, 2)
    
    home_name = FONT_MEDIUM.render(game_state.home_name, True, WHITE)
    surface.blit(home_name, (home_rect.x + 10, home_rect.y + 10))
    
    home_score = FONT_LARGE.render(str(game_state.home_score), True, WHITE)
    surface.blit(home_score, (home_rect.x + 10, home_rect.y + 40))
    
    # Home timeouts
    for i in range(game_state.home_timeouts):
        pygame.draw.circle(surface, GOLD, (home_rect.right - 30 - i * 25, home_rect.centery), 8)
    
    # Away team box
    away_rect = pygame.Rect(900, 10, 250, 80)
    pygame.draw.rect(surface, CHIEFS_PRIMARY, away_rect)
    pygame.draw.rect(surface, WHITE, away_rect, 2)
    
    away_name = FONT_MEDIUM.render(game_state.away_name, True, WHITE)
    surface.blit(away_name, (away_rect.right - away_name.get_width() - 10, away_rect.y + 10))
    
    away_score = FONT_LARGE.render(str(game_state.away_score), True, WHITE)
    surface.blit(away_score, (away_rect.right - away_score.get_width() - 10, away_rect.y + 40))
    
    # Away timeouts
    for i in range(game_state.away_timeouts):
        pygame.draw.circle(surface, GOLD, (away_rect.x + 30 + i * 25, away_rect.centery), 8)
    
    # Quarter and clock
    center_rect = pygame.Rect(350, 10, 500, 80)
    pygame.draw.rect(surface, (50, 50, 50), center_rect)
    pygame.draw.rect(surface, WHITE, center_rect, 2)
    
    quarter_text = FONT_MEDIUM.render(f"Q{game_state.quarter}", True, WHITE)
    surface.blit(quarter_text, (center_rect.x + 20, center_rect.y + 10))
    
    minutes = int(game_state.game_clock // 60)
    seconds = int(game_state.game_clock % 60)
    clock_text = FONT_LARGE.render(f"{minutes:02d}:{seconds:02d}", True, WHITE)
    surface.blit(clock_text, (center_rect.centerx - clock_text.get_width() // 2, center_rect.y + 10))
    
    # Down and distance
    down_text = FONT_MEDIUM.render(f"{game_state.down}{['st', 'nd', 'rd', 'th'][min(game_state.down - 1, 3)]} & {game_state.yards_to_go}", True, WHITE)
    surface.blit(down_text, (center_rect.x + 20, center_rect.y + 50))
    
    # Possession indicator
    poss_team = game_state.home_name if game_state.possession == "home" else game_state.away_name
    poss_color = game_state.get_team_color(game_state.possession)
    pygame.draw.circle(surface, poss_color, (center_rect.right - 100, center_rect.centery), 12)
    poss_text = FONT_SMALL.render(poss_team, True, WHITE)
    surface.blit(poss_text, (center_rect.right - 90, center_rect.centery - poss_text.get_height() // 2))

# Playbook data
OFFENSIVE_PLAYS = {
    "run": [
        {"name": "HB Dive", "desc": "RB up the middle", "type": "run", "min_gain": 1, "max_gain": 7, "risk": "low"},
        {"name": "HB Toss", "desc": "RB sweeps outside", "type": "run", "min_gain": -2, "max_gain": 15, "risk": "medium"},
        {"name": "QB Sneak", "desc": "QB pushes forward", "type": "run", "min_gain": 0, "max_gain": 3, "risk": "very low"},
        {"name": "Draw Play", "desc": "Fake pass then run", "type": "run", "min_gain": 2, "max_gain": 12, "risk": "medium"},
        {"name": "Power Run", "desc": "FB lead block", "type": "run", "min_gain": 2, "max_gain": 9, "risk": "low"},
    ],
    "pass": [
        {"name": "Slant Pass", "desc": "Quick slant route", "type": "pass", "min_gain": 4, "max_gain": 10, "risk": "low"},
        {"name": "Out Route", "desc": "WR cuts to sideline", "type": "pass", "min_gain": 3, "max_gain": 9, "risk": "medium"},
        {"name": "Screen Pass", "desc": "Dump off to RB", "type": "pass", "min_gain": 0, "max_gain": 16, "risk": "low"},
        {"name": "Deep Post", "desc": "Long bomb downfield", "type": "pass", "min_gain": 15, "max_gain": 45, "risk": "high"},
        {"name": "Play Action", "desc": "Fake run then pass", "type": "pass", "min_gain": 8, "max_gain": 25, "risk": "medium"},
        {"name": "Hail Mary", "desc": "Desperation throw", "type": "pass", "min_gain": 30, "max_gain": 60, "risk": "very high"},
        {"name": "TE Drag", "desc": "Tight end across middle", "type": "pass", "min_gain": 5, "max_gain": 12, "risk": "low"},
    ],
    "kick": [
        {"name": "Punt", "desc": "Kick it away on 4th down", "type": "punt", "min_gain": 30, "max_gain": 50, "risk": "none"},
        {"name": "Field Goal", "desc": "Kick for 3 points", "type": "fg", "min_gain": 0, "max_gain": 0, "risk": "varies"},
    ]
}

DEFENSIVE_PLAYS = [
    {"name": "Cover 1 Man", "pass_mod": 0, "run_mod": 0, "sack_mod": 5, "int_mod": 5},
    {"name": "Cover 2 Zone", "pass_mod": -5, "run_mod": 5, "sack_mod": 0, "int_mod": 8},
    {"name": "Cover 3", "pass_mod": -10, "run_mod": 10, "sack_mod": -5, "int_mod": 3},
    {"name": "All-Out Blitz", "pass_mod": 15, "run_mod": -10, "sack_mod": 25, "int_mod": -5},
    {"name": "Safety Blitz", "pass_mod": 10, "run_mod": 0, "sack_mod": 15, "int_mod": 0},
    {"name": "Run Stuff", "pass_mod": 10, "run_mod": -15, "sack_mod": 5, "int_mod": -5},
    {"name": "Prevent", "pass_mod": -15, "run_mod": 15, "sack_mod": -10, "int_mod": 5},
    {"name": "Nickel", "pass_mod": -5, "run_mod": 5, "sack_mod": 5, "int_mod": 5},
]

# CPU AI
def cpu_select_play(game_state, is_offense):
    """AI play selection"""
    if is_offense:
        # Offense AI
        if game_state.down == 4:
            # 4th down logic
            if game_state.yards_to_go <= 2:
                # Go for it
                return random.choice(OFFENSIVE_PLAYS["run"][:3])
            elif game_state.ball_on >= 60:
                # Field goal range
                return OFFENSIVE_PLAYS["kick"][1]
            else:
                # Punt
                return OFFENSIVE_PLAYS["kick"][0]
        elif game_state.yards_to_go > 10:
            # Long yardage
            return random.choice([OFFENSIVE_PLAYS["pass"][3], OFFENSIVE_PLAYS["pass"][2]])
        elif game_state.yards_to_go > 5:
            # Medium yardage
            return random.choice(OFFENSIVE_PLAYS["pass"][:3] + OFFENSIVE_PLAYS["run"][1:3])
        else:
            # Short yardage
            return random.choice(OFFENSIVE_PLAYS["run"][:3])
    else:
        # Defense AI - random for now
        return random.choice(DEFENSIVE_PLAYS)

# Scenes
class CoinTossScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.coin_choice = None
        self.coin_result = None
        self.winner = None
        self.spinning = False
        self.spin_time = 0
        self.done = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and not self.spinning:
            x, y = event.pos
            # Heads button
            if 400 <= x <= 550 and 400 <= y <= 450:
                self.coin_choice = "heads"
                self.start_spin()
                play_sound('click')
            # Tails button
            elif 650 <= x <= 800 and 400 <= y <= 450:
                self.coin_choice = "tails"
                self.start_spin()
                play_sound('click')
        
        if event.type == pygame.MOUSEBUTTONDOWN and self.winner:
            # Continue button
            if 500 <= x <= 700 and 600 <= y <= 660:
                self.done = True
                play_sound('click')
    
    def start_spin(self):
        self.spinning = True
        self.coin_result = random.choice(["heads", "tails"])
        self.winner = self.game_state.home_name if self.coin_result == self.coin_choice else self.game_state.away_name
        if self.winner == self.game_state.home_name:
            self.game_state.possession = "home"
        else:
            self.game_state.possession = "away"
    
    def update(self, dt):
        if self.spinning:
            self.spin_time += dt
            if self.spin_time >= 2.0:
                self.spinning = False
                play_sound('whistle')
    
    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Title
        title = FONT_LARGE.render("COIN TOSS", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        if not self.coin_choice:
            # Choice buttons
            inst = FONT_MEDIUM.render("Choose:", True, BLACK)
            screen.blit(inst, (WINDOW_WIDTH // 2 - inst.get_width() // 2, 300))
            
            # Heads button
            pygame.draw.rect(screen, GOLD, (400, 400, 150, 50))
            pygame.draw.rect(screen, BLACK, (400, 400, 150, 50), 2)
            heads_text = FONT_MEDIUM.render("Heads", True, BLACK)
            screen.blit(heads_text, (475 - heads_text.get_width() // 2, 415))
            
            # Tails button
            pygame.draw.rect(screen, GOLD, (650, 400, 150, 50))
            pygame.draw.rect(screen, BLACK, (650, 400, 150, 50), 2)
            tails_text = FONT_MEDIUM.render("Tails", True, BLACK)
            screen.blit(tails_text, (725 - tails_text.get_width() // 2, 415))
        
        elif self.spinning:
            # Spinning coin animation
            spin_frame = int(self.spin_time * 10) % 2
            pygame.draw.circle(screen, GOLD, (WINDOW_WIDTH // 2, 400), 50)
            if spin_frame == 0:
                pygame.draw.ellipse(screen, BROWN, (WINDOW_WIDTH // 2 - 50, 370, 100, 60))
        
        elif self.winner:
            # Result
            result_text = FONT_LARGE.render(f"Result: {self.coin_result.upper()}!", True, BLACK)
            screen.blit(result_text, (WINDOW_WIDTH // 2 - result_text.get_width() // 2, 300))
            
            winner_text = FONT_MEDIUM.render(f"{self.winner} wins toss!", True, BLACK)
            screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, 400))
            
            receive_text = FONT_MEDIUM.render(f"{self.winner} will receive", True, BLACK)
            screen.blit(receive_text, (WINDOW_WIDTH // 2 - receive_text.get_width() // 2, 450))
            
            # Continue button
            pygame.draw.rect(screen, GREEN, (500, 600, 200, 60))
            pygame.draw.rect(screen, BLACK, (500, 600, 200, 60), 3)
            cont_text = FONT_MEDIUM.render("Continue", True, WHITE)
            screen.blit(cont_text, (600 - cont_text.get_width() // 2, 620))
    
    def is_done(self):
        return self.done

class PlayCallScene:
    def __init__(self, game_state, is_kickoff=False):
        self.game_state = game_state
        self.is_kickoff = is_kickoff
        self.field = Field()
        self.selected_play = None
        self.current_tab = "run"
        self.done = False
        
        # If CPU's turn, auto-select
        if not game_state.is_user_team() and not is_kickoff:
            self.selected_play = cpu_select_play(game_state, is_offense=True)
            self.done = True
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if self.is_kickoff:
                # Kickoff - auto-proceed
                self.selected_play = {"type": "kickoff"}
                self.done = True
                return
            
            # Tab selection
            if 150 <= y <= 200:
                if 120 <= x <= 250:
                    self.current_tab = "run"
                    play_sound('click')
                elif 270 <= x <= 400:
                    self.current_tab = "pass"
                    play_sound('click')
                elif 420 <= x <= 550:
                    self.current_tab = "kick"
                    play_sound('click')
            
            # Play selection
            elif 220 <= y <= 680:
                plays = OFFENSIVE_PLAYS[self.current_tab]
                for i, play in enumerate(plays):
                    play_y = 220 + i * 70
                    if 120 <= x <= 1080 and play_y <= y <= play_y + 60:
                        self.selected_play = play
                        self.game_state.offensive_play = play
                        play_sound('click')
                        
                        # Now select defensive play
                        if not self.game_state.is_user_team():
                            self.game_state.defensive_play = cpu_select_play(self.game_state, is_offense=False)
                        else:
                            # CPU selects defense
                            self.game_state.defensive_play = cpu_select_play(self.game_state, is_offense=False)
                        
                        self.done = True
                        break
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        # Draw field background
        self.field.draw_stadium(screen)
        self.field.draw_field(screen, self.game_state)
        draw_hud(screen, self.game_state)
        
        if self.is_kickoff:
            # Kickoff message
            panel = pygame.Rect(300, 300, 600, 200)
            pygame.draw.rect(screen, (50, 50, 50, 200), panel)
            pygame.draw.rect(screen, WHITE, panel, 3)
            
            text = FONT_LARGE.render("KICKOFF!", True, WHITE)
            screen.blit(text, (panel.centerx - text.get_width() // 2, panel.centery - 20))
            return
        
        # Playbook panel
        panel = pygame.Rect(100, 130, 1000, 570)
        pygame.draw.rect(screen, (50, 50, 50, 230), panel)
        pygame.draw.rect(screen, WHITE, panel, 3)
        
        # Title
        title = FONT_LARGE.render("SELECT PLAY", True, WHITE)
        screen.blit(title, (panel.centerx - title.get_width() // 2, panel.y + 10))
        
        # Tabs
        tabs = [("run", "RUN"), ("pass", "PASS"), ("kick", "KICK")]
        for i, (tab_id, tab_name) in enumerate(tabs):
            tab_x = 120 + i * 150
            tab_rect = pygame.Rect(tab_x, 150, 130, 50)
            if self.current_tab == tab_id:
                pygame.draw.rect(screen, GREEN, tab_rect)
            else:
                pygame.draw.rect(screen, GRAY, tab_rect)
            pygame.draw.rect(screen, WHITE, tab_rect, 2)
            
            tab_text = FONT_SMALL.render(tab_name, True, WHITE)
            screen.blit(tab_text, (tab_rect.centerx - tab_text.get_width() // 2, 
                                  tab_rect.centery - tab_text.get_height() // 2))
        
        # Play list
        plays = OFFENSIVE_PLAYS[self.current_tab]
        for i, play in enumerate(plays):
            play_y = 220 + i * 70
            play_rect = pygame.Rect(120, play_y, 960, 60)
            pygame.draw.rect(screen, (70, 70, 70), play_rect)
            pygame.draw.rect(screen, WHITE, play_rect, 2)
            
            # Play name
            name_text = FONT_MEDIUM.render(play["name"], True, WHITE)
            screen.blit(name_text, (play_rect.x + 10, play_rect.y + 5))
            
            # Description
            desc_text = FONT_SMALL.render(play["desc"], True, LIGHT_BLUE)
            screen.blit(desc_text, (play_rect.x + 10, play_rect.y + 35))
            
            # Gain range
            if play["type"] in ["run", "pass"]:
                gain_text = FONT_SMALL.render(f"{play['min_gain']}-{play['max_gain']} yds", True, YELLOW)
                screen.blit(gain_text, (play_rect.right - 150, play_rect.y + 10))
            
            # Risk
            risk_colors = {"very low": GREEN, "low": LIGHT_GREEN, "medium": YELLOW, 
                         "high": (255, 165, 0), "very high": RED, "none": WHITE, "varies": LIGHT_BLUE}
            risk_color = risk_colors.get(play.get("risk", "medium"), YELLOW)
            risk_text = FONT_TINY.render(f"Risk: {play.get('risk', 'medium')}", True, risk_color)
            screen.blit(risk_text, (play_rect.right - 150, play_rect.y + 35))
        
        # Show FG distance if on kick tab
        if self.current_tab == "kick" and self.game_state.down == 4:
            dist_to_goal = 100 - self.game_state.ball_on + 17  # Add 17 for endzone depth and snap
            fg_text = FONT_MEDIUM.render(f"FG Distance: {dist_to_goal} yards", True, WHITE)
            screen.blit(fg_text, (panel.centerx - fg_text.get_width() // 2, panel.bottom - 40))
    
    def is_done(self):
        return self.done
    
    def get_selected_play(self):
        return self.selected_play


class LivePlayScene:
    def __init__(self, game_state, offensive_play, field):
        self.game_state = game_state
        self.offensive_play = offensive_play
        self.field = field
        self.time = 0
        self.done = False
        self.result = None
        
        # Player setup
        self.offense, self.user_player = create_offensive_formation(game_state, field)
        self.defense = create_defensive_formation(game_state, field)
        
        # Sprint/stamina
        self.stamina = 100
        self.sprinting = False
        
        # Ball state
        self.ball_in_air = False
        self.ball_x = 0
        self.ball_y = 0
        self.ball_vx = 0
        self.ball_vy = 0
        self.ball_start_x = 0
        self.ball_start_y = 0
        self.ball_target = None
        self.ball_arc_time = 0
        
        # Route assignments
        self.setup_routes()
        
        # Play timer
        self.play_duration = 5.0
        
        # Snap the ball
        play_sound('snap')
        self.user_player.has_ball = True if offensive_play.get("type") in ["run", "pass"] else False
        
        # Target receiver for passes
        self.target_receiver = None
        if offensive_play.get("type") == "pass":
            # Find WR/TE players
            receivers = [p for p in self.offense if p.position in ["WR", "TE", "RB"]]
            if receivers:
                self.target_receiver = random.choice(receivers)
    
    def setup_routes(self):
        """Set up target positions for players"""
        play_type = self.offensive_play.get("type")
        
        for player in self.offense:
            if player.is_user:
                continue
            
            if play_type in ["run", "pass"]:
                # OL pushes forward
                if player.position in ["C", "LG", "RG", "LT", "RT"]:
                    player.target_x = player.x + 30
                    player.target_y = player.y
                # Receivers run routes
                elif player.position in ["WR", "TE"]:
                    player.target_x = player.x + random.randint(100, 250)
                    player.target_y = player.y + random.randint(-80, 80)
                # RB/FB
                elif player.position in ["RB", "FB"]:
                    if play_type == "run":
                        player.target_x = player.x + random.randint(50, 150)
                        player.target_y = player.y + random.randint(-40, 40)
                    else:
                        player.target_x = player.x + 80
                        player.target_y = player.y + random.randint(-60, 60)
        
        # Defense chases
        for player in self.defense:
            player.target_x = self.user_player.x + random.randint(-30, 30)
            player.target_y = self.user_player.y + random.randint(-30, 30)
    
    def handle_event(self, event):
        keys = pygame.key.get_pressed()
        
        # Arrow keys for movement
        if not self.ball_in_air and self.offensive_play.get("type") in ["run", "pass"]:
            speed = 200
            if keys[pygame.K_LEFT]:
                self.user_player.target_x = max(self.field.field_rect.left + 20, self.user_player.x - 10)
            if keys[pygame.K_RIGHT]:
                self.user_player.target_x = min(self.field.field_rect.right - 20, self.user_player.x + 10)
            if keys[pygame.K_UP]:
                self.user_player.target_y = max(self.field.field_rect.top + 20, self.user_player.y - 10)
            if keys[pygame.K_DOWN]:
                self.user_player.target_y = min(self.field.field_rect.bottom - 20, self.user_player.y + 10)
        
        # Sprint key
        if keys[pygame.K_s]:
            self.sprinting = True
        else:
            self.sprinting = False
        
        # Pass key
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.offensive_play.get("type") == "pass" and not self.ball_in_air and self.target_receiver:
                self.throw_pass()
    
    def throw_pass(self):
        """Initiate a pass to the target receiver"""
        self.ball_in_air = True
        self.ball_start_x = self.user_player.x
        self.ball_start_y = self.user_player.y
        self.ball_x = self.user_player.x
        self.ball_y = self.user_player.y
        self.ball_target = self.target_receiver
        self.ball_arc_time = 0
        self.user_player.has_ball = False
        play_throw_sound()
    
    def update(self, dt):
        self.time += dt
        
        # Update stamina
        if self.sprinting and self.stamina > 0:
            self.stamina = max(0, self.stamina - 50 * dt)
        else:
            self.stamina = min(100, self.stamina + 30 * dt)
        
        # Apply sprint speed
        if self.sprinting and self.stamina > 0:
            speed_mult = 1.5
        else:
            speed_mult = 1.0
        
        # Update user player
        if not self.ball_in_air:
            dx = self.user_player.target_x - self.user_player.x
            dy = self.user_player.target_y - self.user_player.y
            dist = math.sqrt(dx * dx + dy * dy)
            if dist > 1:
                speed = 200 * speed_mult
                self.user_player.x += (dx / dist) * speed * dt
                self.user_player.y += (dy / dist) * speed * dt
        
        self.user_player.anim_time += dt * 10
        
        # Update other players
        for player in self.offense + self.defense:
            if not player.is_user:
                player.update(dt)
        
        # Ball flight
        if self.ball_in_air:
            self.ball_arc_time += dt
            progress = min(1.0, self.ball_arc_time / 1.5)
            
            # Arc trajectory
            self.ball_x = self.ball_start_x + (self.ball_target.x - self.ball_start_x) * progress
            self.ball_y = self.ball_start_y + (self.ball_target.y - self.ball_start_y) * progress
            # Add arc height
            arc_height = 100 * math.sin(progress * math.pi)
            self.ball_y -= arc_height
            
            # Check if reached target
            if progress >= 1.0:
                self.ball_in_air = False
                # Check for catch/incompletion
                if random.random() < 0.7:  # 70% catch rate
                    self.ball_target.has_ball = True
                    play_catch_sound()
                else:
                    play_sound('hit')
                    self.result = "incomplete"
                    self.done = True
        
        # Check for play end
        if self.time >= self.play_duration:
            self.resolve_play()
    
    def resolve_play(self):
        """Determine play outcome"""
        play = self.offensive_play
        defense = self.game_state.defensive_play or {"pass_mod": 0, "run_mod": 0, "sack_mod": 0, "int_mod": 0}
        
        if play["type"] == "kickoff":
            # Kickoff return
            kick_dist = random.randint(55, 70)
            return_dist = random.randint(15, 30)
            self.result = {"type": "kickoff", "gain": kick_dist - return_dist}
        elif play["type"] == "punt":
            # Punt
            punt_dist = random.randint(30, 50)
            self.result = {"type": "punt", "gain": punt_dist}
        elif play["type"] == "fg":
            # Field goal
            dist_to_goal = 100 - self.game_state.ball_on + 17
            accuracy = max(0.3, 1.0 - (dist_to_goal - 20) / 80)
            if random.random() < accuracy:
                self.result = {"type": "fg_good"}
            else:
                self.result = {"type": "fg_miss"}
        elif play["type"] == "run":
            # Running play
            base_gain = random.randint(play["min_gain"], play["max_gain"])
            defense_mod = defense["run_mod"]
            gain = max(-5, base_gain - defense_mod // 5)
            
            # Fumble chance
            if random.random() < 0.02:
                self.result = {"type": "fumble", "gain": gain}
            else:
                self.result = {"type": "run", "gain": gain}
        elif play["type"] == "pass":
            # Passing play
            # Check for sack
            sack_chance = 0.1 + defense["sack_mod"] / 100
            if random.random() < sack_chance:
                sack_loss = random.randint(3, 10)
                self.result = {"type": "sack", "gain": -sack_loss}
            # Check for interception
            elif random.random() < (0.05 + defense["int_mod"] / 100):
                int_return = random.randint(0, 25)
                self.result = {"type": "interception", "gain": -int_return}
            # Completion/incompletion handled by ball flight
            elif self.result and self.result == "incomplete":
                self.result = {"type": "incomplete", "gain": 0}
            else:
                # Completion
                base_gain = random.randint(play["min_gain"], play["max_gain"])
                defense_mod = defense["pass_mod"]
                gain = max(0, base_gain - defense_mod // 5)
                self.result = {"type": "pass", "gain": gain}
        
        self.done = True
        play_sound('whistle')
    
    def draw(self, screen):
        # Draw field
        self.field.draw_stadium(screen)
        self.field.draw_field(screen, self.game_state)
        draw_hud(screen, self.game_state)
        
        # Draw route lines for receivers
        if self.offensive_play.get("type") == "pass":
            for player in self.offense:
                if player.position in ["WR", "TE", "RB"] and not player.is_user:
                    # Dashed line to target
                    start_x, start_y = player.x, player.y
                    end_x, end_y = player.target_x, player.target_y
                    segments = 10
                    for i in range(0, segments, 2):
                        sx = start_x + (end_x - start_x) * i / segments
                        sy = start_y + (end_y - start_y) * i / segments
                        ex = start_x + (end_x - start_x) * (i + 1) / segments
                        ey = start_y + (end_y - start_y) * (i + 1) / segments
                        color = (0, 255, 0) if player == self.target_receiver else (255, 255, 0)
                        pygame.draw.line(screen, color, (sx, sy), (ex, ey), 2)
        
        # Draw players
        pulse_time = self.time
        for player in self.defense:
            player.draw(screen, pulse_time)
        for player in self.offense:
            is_target = (player == self.target_receiver)
            player.draw(screen, pulse_time, is_target)
        
        # Draw ball if in air
        if self.ball_in_air:
            pygame.draw.ellipse(screen, BROWN, (int(self.ball_x) - 6, int(self.ball_y) - 4, 12, 8))
            pygame.draw.line(screen, WHITE, (int(self.ball_x) - 3, int(self.ball_y)), 
                           (int(self.ball_x) + 3, int(self.ball_y)), 2)
        
        # Stamina bar
        if self.offensive_play.get("type") in ["run", "pass"]:
            bar_x = 50
            bar_y = WINDOW_HEIGHT - 50
            bar_w = 200
            bar_h = 20
            pygame.draw.rect(screen, GRAY, (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, GREEN, (bar_x, bar_y, int(bar_w * self.stamina / 100), bar_h))
            pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_w, bar_h), 2)
            stam_text = FONT_TINY.render("STAMINA", True, WHITE)
            screen.blit(stam_text, (bar_x, bar_y - 20))
        
        # Progress timer
        timer_x = WINDOW_WIDTH - 250
        timer_y = WINDOW_HEIGHT - 50
        timer_w = 200
        timer_h = 20
        progress = min(1.0, self.time / self.play_duration)
        pygame.draw.rect(screen, GRAY, (timer_x, timer_y, timer_w, timer_h))
        pygame.draw.rect(screen, YELLOW, (timer_x, timer_y, int(timer_w * progress), timer_h))
        pygame.draw.rect(screen, WHITE, (timer_x, timer_y, timer_w, timer_h), 2)
        timer_text = FONT_TINY.render("PLAY TIMER", True, WHITE)
        screen.blit(timer_text, (timer_x, timer_y - 20))
        
        # Control hints
        hints = [
            "Arrow Keys: Move",
            "SPACE: Pass (if pass play)",
            "S: Sprint"
        ]
        for i, hint in enumerate(hints):
            hint_text = FONT_MICRO.render(hint, True, WHITE)
            screen.blit(hint_text, (50, 100 + i * 15))
    
    def is_done(self):
        return self.done
    
    def get_result(self):
        return self.result

class ResultScene:
    def __init__(self, game_state, play_result):
        self.game_state = game_state
        self.play_result = play_result
        self.done = False
        self.particles = ParticleSystem()
        self.floating_texts = []
        
        # Apply result to game state
        self.apply_result()
    
    def apply_result(self):
        """Update game state based on play result"""
        result = self.play_result
        
        if result["type"] == "kickoff":
            # Kickoff return
            new_pos = result["gain"]
            self.game_state.ball_on = max(0, min(100, new_pos))
            self.game_state.new_set_of_downs(self.game_state.ball_on)
        elif result["type"] == "punt":
            # Punt - flip possession
            new_pos = min(100, self.game_state.ball_on + result["gain"])
            self.game_state.flip_possession()
            self.game_state.ball_on = 100 - new_pos
            self.game_state.new_set_of_downs(self.game_state.ball_on)
        elif result["type"] == "fg_good":
            # Field goal made
            if self.game_state.possession == "home":
                self.game_state.home_score += 3
            else:
                self.game_state.away_score += 3
            self.floating_texts.append(FloatingText("+3", WINDOW_WIDTH // 2, 300, YELLOW, FONT_LARGE))
            self.particles.emit(WINDOW_WIDTH // 2, 300, 30, [YELLOW, GOLD, (255, 165, 0)])
            # Kickoff after score
            self.game_state.flip_possession()
            self.game_state.ball_on = 25
            self.game_state.new_set_of_downs(25)
        elif result["type"] == "fg_miss":
            # Field goal missed - turnover on downs
            self.game_state.flip_possession()
            self.game_state.ball_on = 100 - self.game_state.ball_on
            self.game_state.new_set_of_downs(self.game_state.ball_on)
        elif result["type"] in ["run", "pass"]:
            gain = result["gain"]
            new_pos = self.game_state.ball_on + gain
            
            # Check for touchdown
            if new_pos >= 100:
                if self.game_state.possession == "home":
                    self.game_state.home_score += 6
                else:
                    self.game_state.away_score += 6
                self.floating_texts.append(FloatingText("TOUCHDOWN! +6", WINDOW_WIDTH // 2, 300, GREEN, FONT_LARGE))
                self.particles.emit(WINDOW_WIDTH // 2, 300, 100, [RED, BLUE, GREEN, YELLOW, (255, 165, 0)])
                play_touchdown_fanfare()
                play_sound('crowd')
                # Extra point coming
            elif new_pos <= 0:
                # Safety
                if self.game_state.possession == "home":
                    self.game_state.away_score += 2
                else:
                    self.game_state.home_score += 2
                self.floating_texts.append(FloatingText("SAFETY! +2", WINDOW_WIDTH // 2, 300, RED, FONT_LARGE))
                self.game_state.flip_possession()
                self.game_state.ball_on = 20
                self.game_state.new_set_of_downs(20)
            else:
                # Normal gain
                self.game_state.ball_on = int(new_pos)
                self.game_state.yards_to_go = max(0, self.game_state.yards_to_go - gain)
                
                # Check for first down
                if self.game_state.ball_on >= self.game_state.yards_to_first:
                    self.game_state.new_set_of_downs(self.game_state.ball_on)
                    self.floating_texts.append(FloatingText("FIRST DOWN!", WINDOW_WIDTH // 2, 350, YELLOW, FONT_MEDIUM))
                    play_sound('crowd')
                else:
                    # Next down
                    self.game_state.next_down()
                    if self.game_state.down > 4:
                        # Turnover on downs
                        self.game_state.flip_possession()
                        self.game_state.ball_on = 100 - self.game_state.ball_on
                        self.game_state.new_set_of_downs(self.game_state.ball_on)
        elif result["type"] == "sack":
            loss = -result["gain"]
            self.game_state.ball_on = max(0, self.game_state.ball_on - loss)
            self.game_state.yards_to_go += loss
            self.game_state.next_down()
            play_sound('hit')
        elif result["type"] == "incomplete":
            # No gain
            self.game_state.next_down()
        elif result["type"] in ["interception", "fumble"]:
            # Turnover
            self.floating_texts.append(FloatingText("TURNOVER!", WINDOW_WIDTH // 2, 300, RED, FONT_LARGE))
            self.game_state.flip_possession()
            return_yards = result.get("gain", 0)
            self.game_state.ball_on = max(0, min(100, 100 - self.game_state.ball_on + return_yards))
            self.game_state.new_set_of_downs(self.game_state.ball_on)
            play_sound('crowd')
        
        # Decrement clock
        time_used = random.randint(18, 40)
        self.game_state.game_clock = max(0, self.game_state.game_clock - time_used)
        self.game_state.total_plays += 1
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Continue button
            if 500 <= x <= 700 and 600 <= y <= 660:
                self.done = True
                play_sound('click')
    
    def update(self, dt):
        self.particles.update(dt)
        self.floating_texts = [ft for ft in self.floating_texts if ft.is_alive()]
        for ft in self.floating_texts:
            ft.update(dt)
    
    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Result panel
        panel = pygame.Rect(200, 200, 800, 400)
        pygame.draw.rect(screen, (50, 50, 50, 230), panel)
        pygame.draw.rect(screen, WHITE, panel, 3)
        
        # Result text
        result = self.play_result
        if result["type"] == "run":
            text = f"RUN: {result['gain']} yards"
            color = GREEN if result["gain"] > 0 else RED
        elif result["type"] == "pass":
            text = f"PASS COMPLETE: {result['gain']} yards"
            color = GREEN
        elif result["type"] == "incomplete":
            text = "INCOMPLETE PASS"
            color = RED
        elif result["type"] == "sack":
            text = f"SACK: {-result['gain']} yards"
            color = RED
        elif result["type"] == "interception":
            text = "INTERCEPTION!"
            color = RED
        elif result["type"] == "fumble":
            text = "FUMBLE!"
            color = RED
        elif result["type"] == "punt":
            text = f"PUNT: {result['gain']} yards"
            color = YELLOW
        elif result["type"] == "fg_good":
            text = "FIELD GOAL GOOD!"
            color = GREEN
        elif result["type"] == "fg_miss":
            text = "FIELD GOAL MISSED"
            color = RED
        elif result["type"] == "kickoff":
            text = f"KICKOFF RETURN: {result['gain']} yards"
            color = YELLOW
        else:
            text = "PLAY COMPLETE"
            color = WHITE
        
        result_text = FONT_LARGE.render(text, True, color)
        screen.blit(result_text, (panel.centerx - result_text.get_width() // 2, panel.y + 100))
        
        # Current situation
        sit_text = FONT_MEDIUM.render(
            f"{self.game_state.down}{['st', 'nd', 'rd', 'th'][min(self.game_state.down - 1, 3)]} & {self.game_state.yards_to_go} at {int(self.game_state.ball_on)} yard line",
            True, WHITE
        )
        screen.blit(sit_text, (panel.centerx - sit_text.get_width() // 2, panel.y + 200))
        
        # Continue button
        pygame.draw.rect(screen, GREEN, (500, 600, 200, 60))
        pygame.draw.rect(screen, BLACK, (500, 600, 200, 60), 3)
        cont_text = FONT_MEDIUM.render("Continue", True, WHITE)
        screen.blit(cont_text, (600 - cont_text.get_width() // 2, 620))
        
        # Particles and floating text
        self.particles.draw(screen)
        for ft in self.floating_texts:
            ft.draw(screen)
    
    def is_done(self):
        return self.done
    
    def needs_extra_point(self):
        """Check if we just scored a touchdown"""
        result = self.play_result
        if result["type"] in ["run", "pass"]:
            gain = result["gain"]
            old_pos = self.game_state.ball_on - gain
            if old_pos + gain >= 100:
                return True
        return False

class ExtraPointScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.choice = None
        self.result = None
        self.done = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            
            if not self.result:
                # Kick button
                if 300 <= x <= 500 and 400 <= y <= 460:
                    self.choice = "kick"
                    if random.random() < 0.94:
                        self.result = "good"
                        if self.game_state.possession == "home":
                            self.game_state.home_score += 1
                        else:
                            self.game_state.away_score += 1
                    else:
                        self.result = "miss"
                    play_sound('kick')
                
                # 2-pt button
                elif 700 <= x <= 900 and 400 <= y <= 460:
                    self.choice = "2pt"
                    if random.random() < 0.45:
                        self.result = "good"
                        if self.game_state.possession == "home":
                            self.game_state.home_score += 2
                        else:
                            self.game_state.away_score += 2
                    else:
                        self.result = "fail"
                    play_sound('snap')
            else:
                # Continue button
                if 500 <= x <= 700 and 550 <= y <= 610:
                    # After score, kickoff
                    self.game_state.flip_possession()
                    self.game_state.ball_on = 25
                    self.game_state.new_set_of_downs(25)
                    self.done = True
                    play_sound('click')
    
    def update(self, dt):
        pass
    
    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Title
        title = FONT_LARGE.render("EXTRA POINT", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 100))
        
        if not self.result:
            # Choices
            inst = FONT_MEDIUM.render("Choose:", True, BLACK)
            screen.blit(inst, (WINDOW_WIDTH // 2 - inst.get_width() // 2, 250))
            
            # Kick button
            pygame.draw.rect(screen, GREEN, (300, 400, 200, 60))
            pygame.draw.rect(screen, BLACK, (300, 400, 200, 60), 3)
            kick_text = FONT_MEDIUM.render("Kick (1 pt)", True, WHITE)
            screen.blit(kick_text, (400 - kick_text.get_width() // 2, 420))
            
            kick_pct = FONT_SMALL.render("94% success", True, BLACK)
            screen.blit(kick_pct, (400 - kick_pct.get_width() // 2, 470))
            
            # 2-pt button
            pygame.draw.rect(screen, YELLOW, (700, 400, 200, 60))
            pygame.draw.rect(screen, BLACK, (700, 400, 200, 60), 3)
            two_text = FONT_MEDIUM.render("2-Point", True, BLACK)
            screen.blit(two_text, (800 - two_text.get_width() // 2, 420))
            
            two_pct = FONT_SMALL.render("45% success", True, BLACK)
            screen.blit(two_pct, (800 - two_pct.get_width() // 2, 470))
        else:
            # Result
            if self.result in ["good"]:
                pts = 1 if self.choice == "kick" else 2
                result_text = FONT_LARGE.render(f"GOOD! +{pts}", True, GREEN)
            else:
                result_text = FONT_LARGE.render("NO GOOD", True, RED)
            
            screen.blit(result_text, (WINDOW_WIDTH // 2 - result_text.get_width() // 2, 300))
            
            # Continue button
            pygame.draw.rect(screen, GREEN, (500, 550, 200, 60))
            pygame.draw.rect(screen, BLACK, (500, 550, 200, 60), 3)
            cont_text = FONT_MEDIUM.render("Continue", True, WHITE)
            screen.blit(cont_text, (600 - cont_text.get_width() // 2, 570))
    
    def is_done(self):
        return self.done

class GameOverScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.particles = ParticleSystem()
        self.time = 0
        self.done = False
        
        # Confetti
        for _ in range(200):
            x = random.randint(0, WINDOW_WIDTH)
            y = random.randint(-200, 0)
            vx = random.uniform(-100, 100)
            vy = random.uniform(100, 300)
            color = random.choice([RED, BLUE, GREEN, YELLOW, (255, 165, 0), (128, 0, 128)])
            self.particles.particles.append(Particle(x, y, vx, vy, color, random.uniform(5.0, 8.0)))
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # New game button
            if 450 <= x <= 750 and 650 <= y <= 710:
                self.done = True
                play_sound('click')
    
    def update(self, dt):
        self.time += dt
        self.particles.update(dt)
    
    def draw(self, screen):
        screen.fill(SKY_BLUE)
        
        # Confetti
        self.particles.draw(screen)
        
        # Title
        title = FONT_LARGE.render("GAME OVER", True, BLACK)
        screen.blit(title, (WINDOW_WIDTH // 2 - title.get_width() // 2, 50))
        
        # Winner
        if self.game_state.home_score > self.game_state.away_score:
            winner_text = FONT_LARGE.render(f"{self.game_state.home_name} WIN!", True, EAGLES_PRIMARY)
        elif self.game_state.away_score > self.game_state.home_score:
            winner_text = FONT_LARGE.render(f"{self.game_state.away_name} WIN!", True, CHIEFS_PRIMARY)
        else:
            winner_text = FONT_LARGE.render("TIE GAME!", True, GRAY)
        screen.blit(winner_text, (WINDOW_WIDTH // 2 - winner_text.get_width() // 2, 150))
        
        # Score panels
        home_panel = pygame.Rect(200, 300, 350, 250)
        pygame.draw.rect(screen, EAGLES_PRIMARY, home_panel)
        pygame.draw.rect(screen, WHITE, home_panel, 3)
        
        home_name = FONT_LARGE.render(self.game_state.home_name, True, WHITE)
        screen.blit(home_name, (home_panel.centerx - home_name.get_width() // 2, home_panel.y + 20))
        
        home_score = FONT_LARGE.render(str(self.game_state.home_score), True, WHITE)
        screen.blit(home_score, (home_panel.centerx - home_score.get_width() // 2, home_panel.y + 100))
        
        away_panel = pygame.Rect(650, 300, 350, 250)
        pygame.draw.rect(screen, CHIEFS_PRIMARY, away_panel)
        pygame.draw.rect(screen, WHITE, away_panel, 3)
        
        away_name = FONT_LARGE.render(self.game_state.away_name, True, WHITE)
        screen.blit(away_name, (away_panel.centerx - away_name.get_width() // 2, away_panel.y + 20))
        
        away_score = FONT_LARGE.render(str(self.game_state.away_score), True, WHITE)
        screen.blit(away_score, (away_panel.centerx - away_score.get_width() // 2, away_panel.y + 100))
        
        # Total plays
        plays_text = FONT_MEDIUM.render(f"Total Plays: {self.game_state.total_plays}", True, BLACK)
        screen.blit(plays_text, (WINDOW_WIDTH // 2 - plays_text.get_width() // 2, 570))
        
        # New game button
        pygame.draw.rect(screen, GREEN, (450, 650, 300, 60))
        pygame.draw.rect(screen, BLACK, (450, 650, 300, 60), 3)
        new_text = FONT_LARGE.render("NEW GAME", True, WHITE)
        screen.blit(new_text, (600 - new_text.get_width() // 2, 670))
    
    def is_done(self):
        return self.done

# Main game loop
def main():
    game_state = GameState()
    field = Field()
    current_scene = CoinTossScene(game_state)
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                current_scene.handle_event(event)
        
        # Update
        current_scene.update(dt)
        
        # Check for scene transitions
        if current_scene.is_done():
            if isinstance(current_scene, CoinTossScene):
                # Start with kickoff
                current_scene = PlayCallScene(game_state, is_kickoff=True)
            elif isinstance(current_scene, PlayCallScene):
                selected_play = current_scene.get_selected_play()
                if selected_play:
                    game_state.offensive_play = selected_play
                    current_scene = LivePlayScene(game_state, selected_play, field)
                else:
                    current_scene = PlayCallScene(game_state, is_kickoff=False)
            elif isinstance(current_scene, LivePlayScene):
                result = current_scene.get_result()
                current_scene = ResultScene(game_state, result)
            elif isinstance(current_scene, ResultScene):
                # Check for extra point
                if current_scene.needs_extra_point():
                    current_scene = ExtraPointScene(game_state)
                # Check for game over
                elif game_state.game_clock <= 0:
                    if game_state.quarter >= 4:
                        current_scene = GameOverScene(game_state)
                    else:
                        game_state.advance_quarter()
                        current_scene = PlayCallScene(game_state, is_kickoff=game_state.quarter == 3)
                else:
                    current_scene = PlayCallScene(game_state)
            elif isinstance(current_scene, ExtraPointScene):
                # After extra point, check for game over or continue
                if game_state.game_clock <= 0 and game_state.quarter >= 4:
                    current_scene = GameOverScene(game_state)
                else:
                    current_scene = PlayCallScene(game_state, is_kickoff=True)
            elif isinstance(current_scene, GameOverScene):
                # Restart game
                game_state = GameState()
                field = Field()
                current_scene = CoinTossScene(game_state)
        
        # Draw
        screen.fill(BLACK)
        current_scene.draw(screen)
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
