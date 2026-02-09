# American Football GUI Game

A complete, fully-working American Football game built with Pygame in a single Python file.

## Installation & Running

### Requirements
- Python 3.7+
- Pygame (installed via pip)

### Install Dependencies
```bash
pip install pygame
```

### Run the Game
```bash
python football_game.py
```

## Game Controls

### During Live Play
- **Arrow Keys**: Move your QB / ball carrier
- **SPACE**: Throw a pass to the nearest receiver (highlighted with green "TARGET" ring)
- **S Key**: Sprint boost (limited stamina bar that regenerates)

### Menu Navigation
- **Mouse**: Click to select plays from menus and UI buttons

## Features

### Stadium & Visuals
- Full stadium background with multi-tier stands, press box, and stadium lights
- Animated crowd (pre-rendered for performance)
- 100-yard football field with:
  - Alternating grass stripes
  - Team endzones with diagonal stripe patterns
  - Yard lines every 5 yards (bold every 10)
  - Hash marks between yard lines
  - Blue line of scrimmage
  - Yellow first-down line

### Players (22 on field)
Each of the 22 players features:
- Animated legs and arms
- Team jersey with number
- Helmet with facemask
- Position label
- User-controlled player gets pulsing yellow ring + "YOU" label
- Pass target receiver gets pulsing green ring + "TARGET" label
- Ball carrier shows football graphic

**Offense (11):** C, LG, RG, LT, RT (OL), QB (user), RB, FB, 2x WR, TE
**Defense (11):** 4x DL, 3x LB (including MLB), 2x CB, FS, SS

### Offensive Playbook (14 plays)

**Run Tab (5 plays):**
- HB Dive - RB up the middle
- HB Toss - RB sweeps outside
- QB Sneak - QB pushes forward
- Draw Play - Fake pass then run
- Power Run - FB lead block

**Pass Tab (7 plays):**
- Slant Pass - Quick slant route
- Out Route - WR cuts to sideline
- Screen Pass - Dump off to RB
- Deep Post - Long bomb downfield
- Play Action - Fake run then pass
- Hail Mary - Desperation throw
- TE Drag - Tight end across middle

**Kick Tab (2 plays):**
- Punt - Kick it away on 4th down
- Field Goal - Kick for 3 points

### Defensive Plays (8 plays)
- Cover 1 Man - Man coverage, 1 safety deep
- Cover 2 Zone - Two safeties deep
- Cover 3 - Three deep zones
- All-Out Blitz - Send everyone
- Safety Blitz - Extra rusher
- Run Stuff - Stack the box
- Prevent - Deep coverage
- Nickel - 5 DBs

### Game Rules
- **4 downs** to gain 10 yards for first down
- **Touchdown** = 6 points
- **Extra point** choice: Kick (1 pt, 94%) or 2-point conversion (45%)
- **Field Goal** = 3 points
- **Safety** = 2 points
- **4 quarters** of 15 minutes each
- **Coin toss** at start
- **Kickoffs** after scores
- **3 timeouts** per team per half

### Game Scenes
1. **Coin Toss** - Animated spinning coin
2. **Play Call** - Tabbed playbook with play descriptions
3. **Live Animation** - User controls with stamina bar and timer
4. **Result** - Play outcome display
5. **Extra Point** - After TD, choose kick or 2-pt
6. **Game Over** - Final score with confetti

### Sound Effects
All sounds are generated programmatically:
- Whistle (play stops)
- Crowd roar (big plays)
- Hit/tackle sound
- Kick sound
- Touchdown fanfare
- Snap sound
- Click (UI)
- Throw/catch sounds

**Note:** Sounds require numpy. If not installed, game runs silently.

### HUD Display
- Team names and scores
- Quarter indicator
- Game clock (MM:SS)
- Down & distance
- Possession indicator
- Timeout indicators

## Teams
- **Home**: EAGLES (Blue)
- **Away**: CHIEFS (Red)
- User always plays as home team

## Technical Details
- Window size: 1200 x 800
- 60 FPS
- Single file, no external assets
- All graphics drawn with Pygame
- Crowd surface pre-rendered and cached for performance

## Development Notes
This game demonstrates:
- Complete NFL rules implementation
- AI opponent play calling
- User-controlled gameplay with multiple mechanics
- Full game loop from coin toss to game over
- Visual effects (particles, floating text, animations)
- Single-file architecture with no external dependencies

## Troubleshooting

### No Sound
If you don't hear sounds, install numpy:
```bash
pip install numpy
```

### Display Issues
The game requires a graphical environment. If running on a server, you may need to set up a virtual display (Xvfb).

### Performance
The game is optimized with pre-rendered crowd and efficient drawing. If you experience lag, ensure you have adequate GPU support for Pygame.
