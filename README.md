# Arkanoid – My Game

A classic **Arkanoid / Breakout**–style game written in Python, rendered with **OpenGL** through Pygame. Break bricks, collect power-ups, and fight bosses across 20 levels.

🌏 [中文说明 (Chinese README)](README.zh.md)

## Features

- 🎮 Smooth OpenGL-accelerated 2D rendering (1260×800, 60 FPS)
- 🧱 20 playable levels with a variety of brick layouts
- 👾 Boss fights on levels 5, 10, 15, and 20, each boss firing different projectile types (normal, slowing, explosive)
- ⭐ Special power-up bricks:
  - **Gold** – grants an extra life
  - **Silver** – expands the paddle
  - **Cyan** – spawns an extra ball
  - **Red** – activates paddle-mounted guns
- 💥 Particle effects for collisions, explosions, and bullet trails
- ❤️ Heart-based lives display
- 🔊 Procedurally generated sound effects (paddle bounce, brick break, power-ups, boss hits, etc.)
- 🎵 Optional background music — just drop an MP3 file (`music.mp3`, `background.mp3`, `game_music.mp3`, `soundtrack.mp3`, or `arkanoid_music.mp3`) next to the script
- ⏸️ Pause menu and level-select

## Requirements

- Python 3.8+
- [Pygame](https://www.pygame.org/)
- [PyOpenGL](http://pyopengl.sourceforge.net/)
- [NumPy](https://numpy.org/)
- [OpenCV (opencv-python)](https://pypi.org/project/opencv-python/)

Install the dependencies:

```bash
pip install pygame PyOpenGL PyOpenGL_accelerate numpy opencv-python
```

## Running the Game

```bash
python ark9k.py
```

## Controls

| Key | Action |
|-----|--------|
| ← / → | Move paddle (in-game) / navigate menu |
| ↑ / ↓ | Navigate menu |
| Enter | Confirm menu selection |
| Esc | Pause / open menu |
| M | Toggle background music |
| R | Restart after game over or victory |
| N | Advance to the next level after clearing one |

Paddle guns (once activated by a red brick) fire automatically.

## Adding Background Music

The game looks for one of the following files in the working directory and plays it on loop if found:

```
music.mp3
background.mp3
game_music.mp3
soundtrack.mp3
arkanoid_music.mp3
```

If none are present, the game runs silently for music (sound effects still play, as they are generated procedurally).

## Project Structure

```
ark9k.py    # Single-file game: engine, entities, levels, boss logic, UI, main loop
```

## License

No license specified yet — add one (e.g., MIT) if you plan to share or accept contributions.
