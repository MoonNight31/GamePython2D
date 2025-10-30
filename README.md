# GamePython2D - 2D Game with AI

## 🎮 Description
A 2D game featuring an advanced trainable AI system using curriculum learning and PPO. The game includes a player-centered camera system, a 5000x5000 world, enemies, XP progression, and a 3-card draft system for upgrades. The AI evolved from passive behavior to active shooting with sophisticated spatial awareness.

## 📁 Project Structure
```
GamePython2D/
├── src/gamepython2d/        # Game source code
│   ├── game.py              # Main game engine with camera system
│   ├── player.py            # Player logic and projectile system
│   ├── enemy.py             # Enemy system
│   ├── card_system.py       # Card system and drafting
│   ├── xp_system.py         # Experience system
│   ├── ui.py                # User interface
│   ├── effects_system.py    # Visual effects and particles
│   ├── ai_environment.py    # AI Environment (Gymnasium)
│   └── ai_trainer.py        # AI Trainer (PPO)
├── tools/                   # Development tools
│   └── training/            # AI training tools
│       └── curriculum_trainer.py  # 7-stage curriculum trainer
├── ai_models/               # Trained AI models
├── ai_logs/                 # TensorBoard training logs
├── tests/                   # Unit tests
├── main.py                  # Game entry point (human player)
├── train_ai.py              # Basic AI training script
├── demo_ai.py               # AI demonstration
├── test_ai.py               # AI testing script
├── final_comparison.py      # Compare AI models
└── pyproject.toml           # Configuration and dependencies
```

## 🎮 Game Features

### Gameplay
- 🕹️ **Smooth camera system** - Camera centered on player in 5000x5000 world
- 🎯 **Continuous automatic shooting** - Projectiles fire continuously toward mouse/target
- 👹 **Dynamic enemy spawning** - Enemies spawn around player in world coordinates
- ⭐ **XP and leveling system** - Collect XP orbs, level up, gain upgrades
- 🃏 **3-card draft system** - Choose upgrades from randomized card pools
- 💥 **Projectile-based combat** - Fire projectiles to defeat enemies
- 🎆 **Visual effects system** - Particle effects with camera-aware rendering
- 🌐 **Large scrolling world** - 5000x5000 pixel world with grid background

### Camera System
- 📷 **Player-centered view** - Camera follows player smoothly
- 🗺️ **World coordinates** - All gameplay uses world coordinates (0-5000)
- 🖼️ **Screen conversion** - Automatic world-to-screen coordinate conversion
- 🎨 **Grid background** - Scrolling 100px grid for movement sensation
- ⚡ **Optimized culling** - Only renders visible objects

### Interface
- 🖥️ **1250x850 screen resolution** - Viewport into 5000x5000 world
- 📊 **Real-time statistics** - Health, XP, level, score display
- � **Mouse targeting** - Click or hold to shoot at mouse position
- 🎨 **Clean UI** - HUD with player stats and enemy count

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
pip install pygame>=2.5.0 gymnasium>=0.29.0 stable-baselines3>=2.0.0 torch>=2.0.0 numpy>=1.21.0
```

### Main Dependencies
- **pygame** ≥2.5.0 - 2D game engine
- **gymnasium** ≥0.29.0 - RL environments
- **stable-baselines3** ≥2.0.0 - PPO algorithms
- **torch** ≥2.0.0 - PyTorch framework
- **numpy** ≥1.21.0 - Numerical computations

## 🚀 Usage

### Play the Game (Human Player)
```bash
python main.py
```
**Controls:**
- **WASD/Arrows** - Move player
- **Mouse** - Aim and shoot (automatic continuous fire)
- **ESC** - Quit game

### Train the AI

**Basic Training** (single stage):
```bash
python train_ai.py
```

**Curriculum Training** (recommended, 7 stages):
```bash
python tools/training/curriculum_trainer.py
```
- 30 parallel environments (optimized for Windows)
- 8.2M total timesteps across 7 progressive stages
- Batch size: 512 (optimized for 30 envs × 2048 steps)
- Stages: 600k → 800k → 1M → 1.2M → 1.4M → 1.2M → 2M

### Test the AI
```bash
python demo_ai.py              # Watch trained AI play
python test_ai.py              # Run AI test episodes
python final_comparison.py     # Compare different models
```

## 🤖 AI System

### AI Evolution
- **Problem Solved**: AI learned to shoot projectiles instead of relying on collision damage
- **Before**: 0 projectiles per episode (passive behavior)
- **After**: Active shooting behavior with strategic positioning

### Reward System (Optimized)
- **+25 points** - Kill enemy with projectile
- **+4 points** - Fire projectile (encourages shooting)
- **+1 point** - Move (encourages exploration)
- **+0.2 points/step** - Survival bonus
- **-10 points** - Hit world boundaries (5000x5000 limits)
- **-5 points** - Die

### Training Features
- **Curriculum Learning**: 7 progressive training stages
- **Multi-Environment**: 30 parallel environments for diversity
- **Normalized Observations**: All values scaled 0-1 for stable training
- **World Coordinates**: Observations normalized with world_size (5000) not screen_size
- **TensorBoard Logging**: Real-time training metrics


## 🧠 AI Technical Details

### Observation Space (12 dimensions, normalized 0-1)
1. **Player X position** (normalized by world_size: 5000)
2. **Player Y position** (normalized by world_size: 5000)
3. **Player health** (0-1, divided by max_health)
4. **Player XP** (0-1, divided by xp_to_next_level)
5. **Player level** (0-1, divided by 20)
6. **Closest enemy X** (normalized by world_size)
7. **Closest enemy Y** (normalized by world_size)
8. **Closest enemy health** (0-1)
9. **Second closest enemy X** (normalized by world_size)
10. **Second closest enemy Y** (normalized by world_size)
11. **Enemy count** (0-1, divided by 20)
12. **Survival time** (0-1, divided by 1000)

### Action Space (5 continuous actions)
- **Movement X**: [-1, 1] - Horizontal movement direction
- **Movement Y**: [-1, 1] - Vertical movement direction
- **Attack X**: [-1, 1] - Horizontal attack direction
- **Attack Y**: [-1, 1] - Vertical attack direction
- **Attack trigger**: [0, 1] - Whether to shoot (>0.5 = shoot)

### Training Algorithm
- **PPO (Proximal Policy Optimization)** via Stable-Baselines3
- **30 Parallel Environments** (DummyVecEnv for Windows compatibility)
- **Batch Size**: 512 samples (optimized for 30 envs × 2048 steps = 61,440 samples)
- **Learning Rate**: 3e-4 with linear annealing
- **Curriculum Learning**: 7 stages with increasing difficulty
- **TensorBoard Integration**: Real-time metric visualization

### Coordinate System
- **World Space**: 5000x5000 pixel game world
- **Screen Space**: 1250x850 pixel viewport
- **Camera**: Centered on player, follows in world coordinates
- **Conversion**: Automatic world↔screen conversion for rendering
- **AI Observations**: All positions normalized with world_size (5000)
- **Projectile Range**: 2000 pixels from player in attack direction

## 🏆 Performance Metrics

### Training Metrics (TensorBoard)
- **ep_rew_mean**: Average episode reward
- **ep_len_mean**: Average episode length (survival)
- **fps**: Training speed (frames per second)
- **total_timesteps**: Cumulative training steps

### Gameplay Metrics
- **Survival Time**: Steps survived before death
- **Kill Count**: Enemies eliminated by projectiles
- **Projectiles Fired**: Measure of AI activity (tracked via `total_projectiles_created`)
- **Score**: Cumulative reward during episode
- **Level Progression**: XP gained and level reached

## 🎯 Key Improvements

### Camera System
✅ **Player-centered camera** - Smooth following in large world  
✅ **World coordinates** - Consistent coordinate system (0-5000)  
✅ **Grid background** - Visual feedback for movement  
✅ **Optimized culling** - Renders only visible entities  

### AI Training
✅ **Curriculum learning** - 7 progressive stages (8.2M timesteps)  
✅ **Normalized observations** - Stable learning with 0-1 values  
✅ **Fixed projectile tracking** - Uses `total_projectiles_created` counter  
✅ **Optimized batch size** - 512 samples for 30 environments  

### Bug Fixes
✅ **Projectile bounds** - Check world_size (5000) not screen bounds  
✅ **Movement limits** - Removed hardcoded screen clamps  
✅ **Mouse targeting** - Proper world coordinate conversion  
✅ **Effects rendering** - Camera-aware particle system  
✅ **Observation space** - Normalized with world_size not screen_size  

## 🔧 Development Notes

### Reinforcement Learning Architecture
- **Environment**: Custom Gymnasium environment (`ai_environment.py`)
- **Algorithm**: PPO with continuous action space
- **Reward Shaping**: Carefully balanced to encourage shooting behavior
- **Parallel Training**: 30 environments for sample diversity
- **Observation Normalization**: Critical for stable learning

### Coordinate System Design
- **World-centric**: All game logic uses world coordinates (0-5000)
- **Camera Transform**: `screen = world - camera + screen_center`
- **Inverse Transform**: `world = screen + camera - screen_center`
- **Player Limits**: Simple bounds checking (center < 0 or > 5000)

### Projectile System
- **Creation**: At player world position with normalized direction
- **Velocity**: Constant speed (500 pixels/sec) in direction vector
- **Bounds**: Removed when outside world_size (5000)
- **Collision**: Standard rect collision in world coordinates
- **Tracking**: `total_projectiles_created` counter for reward calculation

## 📊 Training Progress

Monitor training with TensorBoard:
```bash
tensorboard --logdir=ai_logs
```

Access at: `http://localhost:6006`

### Expected Training Results
- **Stage 1-2** (1.4M steps): AI learns basic movement and shooting
- **Stage 3-4** (2.2M steps): Improves aiming and enemy tracking
- **Stage 5-6** (2.6M steps): Optimizes positioning and survival
- **Stage 7** (2M steps): Fine-tunes strategy for maximum score

## 🚀 Next Steps

1. **Train new model**: `python tools/training/curriculum_trainer.py`
2. **Monitor progress**: TensorBoard at `http://localhost:6006`
3. **Test AI**: `python demo_ai.py` after training completes
4. **Compare models**: `python final_comparison.py` to evaluate

## 📝 Notes

- Old models are **incompatible** due to observation space changes (world_size normalization)
- Training takes ~30-45 minutes depending on hardware (8.2M timesteps)
- CPU training supported (PyTorch CPU version)
- 30 parallel environments optimized for Windows (DummyVecEnv)

---

**Developed with**: Python 3.11, PyGame 2.5, Stable-Baselines3 2.0, PyTorch 2.0