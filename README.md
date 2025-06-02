# Carrom Board Game

## Project Overview

This project implements a fully functional Carrom Board game using Pygame. The game features authentic carrom board design, realistic physics, and supports both 2-player and 4-player gameplay modes.

## Game Description

Carrom is a traditional strike-and-pocket board game popular in many parts of Asia. Players use a striker disc to hit and pocket carrom men (coins) into the four corner pockets of a square wooden board. The game combines elements of billiards, shuffleboard, and table hockey.

## Features Implemented

### Game Mechanics
- **Physics-Based Movement**: Realistic friction, velocity, and collision detection
- **Turn-Based Gameplay**: Alternating turns between players
- **Scoring System**: Points for pocketed coins with bonus for queen
- **Foul Detection**: Penalties for pocketing striker or opponent's coins
- **Queen Rules**: Special handling for covering the queen coin

### Visual Design
- **Authentic Carrom Board**: Detailed board with all traditional markings
  - Large red center circle with 8-point star/compass design
  - Four-sided striking zones with curved corners and red circles
  - Directional arrows in quadrants and striking zones
  - Black pockets in corners
- **Realistic Game Pieces**:
  - Detailed coins with decorative patterns
  - Queen with special design
  - White striker with black outline

### User Interface
- **Multiple Game Screens**:
  - Start screen with game options
  - Settings screen for customization
  - Game screen with score display
  - Pause screen with save options
  - Game over screen with results
- **Visual Feedback**:
  - Power meter for striker shots
  - Particle effects for collisions
  - Turn indicators and messages

### Customization
- **Multiple Themes**: Classic, Modern, Dark, and Forest
- **Player Modes**: Support for both 2-player and 4-player gameplay
- **Sound Settings**: Toggle game sounds on/off
- **Save/Load**: Ability to save and resume games

## Technical Implementation

### Code Structure
- **Modular Design**: Separate classes for different game elements
  - `Coin` class: Base class for all game pieces
  - `Striker` class: Extended from Coin with player control functionality
  - `CarromGame` class: Main game class handling state and rendering

### Physics System
- Velocity-based movement with friction
- Elastic collisions between game pieces
- Boundary detection and response
- Pocket detection for scoring

### User Interaction
- Mouse-based controls for positioning and aiming
- Power control system for shots
- Keyboard shortcuts for game functions

## Installation and Setup

1. Requirements:
   - Python 3.6+
   - Pygame library

2. Installation:
   ```
   pip install pygame
   ```

3. Running the Game:
   ```
   python3 carrom_game_fixed.py
   ```

## Game Controls

- **Left Mouse Click**: Position the striker along the baseline
- **Right Mouse Click and Hold**: Aim the striker
- **Left Mouse Click and Hold**: Set power (after aiming)
- **Release Left Mouse Button**: Shoot the striker
- **Press Space**: Start the game (on Start screen)
- **Press S**: Access settings menu / Save game (during gameplay)
- **Press L**: Load a saved game (on Start screen)
- **Press ESC**: Pause the game / Return to previous screen
- **Press R**: Restart the game (on Game Over screen)
- **Press M**: Return to main menu (on Game Over or Pause screen)

## Game Rules

1. Players take turns striking coins into pockets.
2. Each player aims to pocket all their coins (white for Player 1, black for Player 2).
3. The Queen (red coin) is worth 3 bonus points when "covered" (pocketing one of your coins immediately after pocketing the Queen).
4. If a player pockets the striker or opponent's coin, it's a foul.
5. Three consecutive fouls result in losing the turn.
6. The first player to pocket all their coins wins.
7. The player with the highest score at the end wins the game.

## Future Improvements

- AI opponent for single-player mode
- Online multiplayer functionality
- Enhanced sound effects and background music
- Mobile touch controls
- Tournament mode with statistics tracking
- Additional board customization options

## Conclusion

This implementation of the Carrom Board game successfully captures the essence of the traditional game while adding modern features like customizable themes, save/load functionality, and visual effects. The physics system provides realistic gameplay, and the user interface is intuitive and responsive.

The modular code structure allows for easy maintenance and future enhancements, making this a solid foundation for further development.
