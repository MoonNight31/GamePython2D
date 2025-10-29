# GamePython2D - 2D Game with AI

## 🎮 Description
A 2D game featuring a trainable AI system that evolved from passive to active behavior. The game includes a controllable character, enemies, an XP system, and a 3-card draft system for player upgrades.

## 📁 Project Structure
```
GamePython2D/
├── src/gamepython2d/        # Game source code
│   ├── game.py              # Main game engine
│   ├── player.py            # Player logic
│   ├── enemy.py             # Enemy system
│   ├── card_system.py       # Card system and drafting
│   ├── xp_system.py         # Experience system
│   ├── ui.py                # User interface
│   ├── effects_system.py    # Visual effects and particles
│   ├── audio_system.py      # Procedural audio generation
│   ├── ai_environment.py    # AI Environment (Gymnasium)
│   └── ai_trainer.py        # AI Trainer (PPO)
├── tools/                   # Development tools
│   ├── debug/               # Debug utilities
│   ├── training/            # AI training tools
│   ├── testing/             # Testing and analysis tools
│   └── README.md            # Tools documentation
├── ai_models/               # Trained AI models
│   ├── demo_ai_final.zip    # Passive AI (demonstration)
│   ├── curriculum_stage_*.zip # Curriculum learning models
│   └── game_ai_model_final.zip # Active AI (final)
├── ai_logs/                 # TensorBoard training logs
├── archive/                 # Archived old files
├── tests/                   # Unit tests
├── main.py                  # Game entry point
├── train_ai.py              # AI training script
├── demo_ai.py               # AI demonstration
├── clean_project.py         # Project cleanup utility
└── pyproject.toml           # Configuration and dependencies
```

## 🎮 Game Features

### Gameplay
- 🕹️ Controllable character with projectile shooting
- 👹 Enemy system with automatic spawning
- ⭐ Experience and leveling system
- 🃏 3-card draft system for player upgrades
- 💥 Collision and combat mechanics
- 🎆 **Visual effects system** with particle effects
- 🔊 **Procedural audio system** with dynamic sound generation

### Interface
- 🖥️ 1200x800 resolution
- 📊 Real-time statistics display
- 🎨 Clean and intuitive graphical interface

## 📦 Installation

### Prerequisites
- Python ≥3.11
- pip

### Install Dependencies
```bash
pip install -e .
```

Or manually:
```bash
pip install pygame>=2.5.0 gymnasium>=0.29.0 stable-baselines3>=2.0.0 torch>=2.0.0 numpy>=1.21.0 matplotlib>=3.5.0
```

### Main Dependencies
- **pygame** ≥2.5.0 - 2D game engine
- **gymnasium** ≥0.29.0 - RL environments
- **stable-baselines3** ≥2.0.0 - PPO algorithms
- **torch** ≥2.0.0 - PyTorch framework
- **numpy** ≥1.21.0 - Numerical computations
- **matplotlib** ≥3.5.0 - Graphics and visualizations

## 🚀 Usage

### Play the Game
```bash
python main.py
```

### Train a New AI
```bash
python train_ai.py                           # Basic training
python tools/training/curriculum_trainer.py  # Advanced curriculum training
```

### Test the AI
```bash
python tools/testing/test_ai_effectiveness.py  # Effectiveness analysis
python tools/testing/test_ai_shooting.py       # Shooting system test
python tools/testing/test_effects_demo.py      # Visual effects demo
```

### Debug and Analysis
```bash
python tools/debug/debug_projectile_creation.py  # Debug projectiles
python tools/testing/analyze_ai_behavior.py      # Analyze behavior
```

### Clean Project
```bash
python clean_project.py  # Clean old logs and temporary files
```

## 🤖 AI Evolution

### Problem Solved
- **Before**: Passive AI (0 projectiles, collision kills only)
- **After**: Active AI (shoots projectiles, intentional kills)

### Improved Reward System
- +15 points for projectile kills
- 0 points for collision kills
- +0.5 points per projectile fired
- -0.1 points for inactivity
- Position-based rewards (center vs edges)

### Reward System Details
- **Edge Penalties**: -1.0 to -0.2 points when too close to screen edges
- **Center Bonus**: +0.3 points for staying away from edges
- **Progressive Center Bonus**: Up to +0.2 additional points for optimal positioning

## 🎯 Results
- ✅ AI transformed from passive to active behavior
- ✅ 0.3 projectiles average (vs 0 before)
- ✅ 38% improvement confirmed
- ✅ Enhanced spatial awareness with position-based rewards

## 🧠 AI Technical Details

### Observation Space (12 dimensions)
- Player position (x, y)
- Player health and XP
- Player level
- Closest enemy positions and health
- Second closest enemy position
- Enemy count and survival time

### Action Space (5 continuous actions)
- Movement direction (x, y): [-1, 1]
- Attack direction (x, y): [-1, 1]
- Attack decision: [0, 1]

### Training Algorithm
- **PPO (Proximal Policy Optimization)** via Stable-Baselines3
- **Multi-environment training** for better generalization
- **TensorBoard logging** for performance monitoring

## 🏆 Performance Metrics
- **Survival Time**: Steps survived before death
- **Active Kills**: Enemies killed with projectiles (+15 pts each)
- **Passive Kills**: Enemies killed by collision (0 pts)
- **Projectiles Fired**: Measure of AI activity
- **Spatial Positioning**: Distance from edges and center
- **Total Reward**: Cumulative score during episode

## 🔧 Development Notes
- **Reinforcement Learning**: PPO algorithm with custom reward shaping
- **Reward Engineering**: Carefully balanced to encourage active play
- **Position Awareness**: New system to prevent edge-hugging behavior
- **Gymnasium Integration**: Standard RL environment interface
- **Real-time Visualization**: Both training metrics and gameplay demo
- **Effects System**: Particle-based visual effects with procedural audio
- **Performance Optimized**: Minimal FPS impact with smart particle management

## 🎆 Effects System

The game features a comprehensive visual and audio effects system. See [EFFECTS_SYSTEM.md](EFFECTS_SYSTEM.md) for full documentation.

### Visual Effects
- **Particle System**: Dynamic particles with gravity, velocity, and life
- **Card Selection Effects**: Unique effects for each rarity (Common → Legendary)
- **Upgrade Effects**: Visual feedback for each stat boost
- **Combat Effects**: Projectile firing, impacts, and enemy deaths
- **Level Up**: Spectacular multi-layered effect with screen shake

### Audio System
- **Procedural Generation**: All sounds generated algorithmically
- **Frequency-based Design**: Each card rarity has a unique frequency
- **Dynamic Mixing**: Automatic volume balancing
- **Combat Sounds**: Laser shots, impacts, and explosions
- **No External Files**: Fully self-contained audio system

Test the effects interactively:
```bash
python tools/testing/test_effects_demo.py
```
