"""
VGDL Import Helper Module

This module ensures that all necessary VGDL components are properly imported
and available in the global namespace during environment initialization.
"""

import sys
import os

# Add necessary paths to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
vgdl_env_path = os.path.dirname(current_dir)
thinker_dir = os.path.dirname(vgdl_env_path)

paths_to_add = [
    current_dir,  # /path/to/thinker/thinker/vgdl_env/vgdl
    vgdl_env_path,  # /path/to/thinker/thinker/vgdl_env
    thinker_dir,  # /path/to/thinker/thinker
    os.path.dirname(thinker_dir),  # /path/to/thinker
]

for path in paths_to_add:
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)

# First, directly import the Immovable class from the local ontology module
try:
    # Direct import from the local module
    from ontology import Immovable
    print("Successfully imported Immovable class directly")
except ImportError as e:
    print(f"Error importing Immovable directly: {e}")
    # If direct import fails, try to import from the full path
    try:
        from vgdl.ontology import Immovable
        print("Successfully imported Immovable from vgdl.ontology")
    except ImportError as e2:
        print(f"Error importing Immovable from vgdl.ontology: {e2}")
        try:
            # Try one more approach with the full path
            from thinker.vgdl_env.vgdl.ontology import Immovable
            print("Successfully imported Immovable from thinker.vgdl_env.vgdl.ontology")
        except ImportError as e3:
            print(f"Error importing Immovable from thinker.vgdl_env.vgdl.ontology: {e3}")
            # Define a fallback Immovable class if all imports fail
            from vgdl.core import VGDLSprite
            
            class Immovable(VGDLSprite):
                """ A gray square that does not budge. """
                color = (128, 128, 128)  # GRAY
                is_static = True
                
                def update(self, game):
                    pass
                    
            print("Created fallback Immovable class")

# Import all necessary components from ontology
try:
    # Import basic sprite types
    from vgdl.ontology import (
        # Basic sprite types
        Passive, Flicker, Spreader, SpriteProducer, Portal, SpawnPoint,
        # Moving sprites
        RandomNPC, OrientedSprite, Conveyor, Missile, Switch, OrientedFlicker,
        Walker, WalkJumper, RandomInertial, RandomMissile, ErraticMissile, Bomber,
        Chaser, Fleeing, AStarChaser,
        # Avatars
        MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar, OrientedAvatar,
        RotatingAvatar, RotatingFlippingAvatar, NoisyRotatingFlippingAvatar,
        ShootAvatar, AimedAvatar, AimedFlakAvatar, InertialAvatar, MarioAvatar,
        ClimbingAvatar, FrostBiteAvatar, Floe, FrostbiteIgloo,
        # Physics
        GridPhysics, ContinuousPhysics, NoFrictionPhysics, GravityPhysics,
        # Resources
        Resource, ResourcePack,
        # Colors
        BLACK, WHITE, RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, GRAY, LIGHT_GRAY,
        DARK_GRAY, ORANGE, PURPLE, BROWN, LIGHTGREEN, DARKGRAY, GOLD,
        # Directions
        LEFT, RIGHT, UP, DOWN, BASEDIRS
    )
    
    # Import core components
    from vgdl.core import VGDLParser, VGDLSprite, BasicGame
    from vgdl.interfaces import GameEnvironment
    
    # Define NO_DIR as None since it's not defined in the codebase
    NO_DIR = None
    
    # Import helper functions
    from vgdl.ontology import stochastic_effects
    
    print("Successfully imported all VGDL components in vgdl_imports.py")
    VGDL_IMPORTED = True
    
except ImportError as e:
    print(f"Error importing VGDL components in vgdl_imports.py: {e}")
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    VGDL_IMPORTED = False

# Make all imported components available at the module level
__all__ = [
    'Immovable', 'Passive', 'Flicker', 'Spreader', 'SpriteProducer', 'Portal', 'SpawnPoint',
    'RandomNPC', 'OrientedSprite', 'Conveyor', 'Missile', 'Switch', 'OrientedFlicker',
    'Walker', 'WalkJumper', 'RandomInertial', 'RandomMissile', 'ErraticMissile', 'Bomber',
    'Chaser', 'Fleeing', 'AStarChaser',
    'MovingAvatar', 'HorizontalAvatar', 'VerticalAvatar', 'FlakAvatar', 'OrientedAvatar',
    'RotatingAvatar', 'RotatingFlippingAvatar', 'NoisyRotatingFlippingAvatar',
    'ShootAvatar', 'AimedAvatar', 'AimedFlakAvatar', 'InertialAvatar', 'MarioAvatar',
    'ClimbingAvatar', 'FrostBiteAvatar', 'Floe', 'FrostbiteIgloo',
    'GridPhysics', 'ContinuousPhysics', 'NoFrictionPhysics', 'GravityPhysics',
    'Resource', 'ResourcePack',
    'BLACK', 'WHITE', 'RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'MAGENTA', 'GRAY', 'LIGHT_GRAY',
    'DARK_GRAY', 'ORANGE', 'PURPLE', 'BROWN', 'LIGHTGREEN', 'DARKGRAY', 'GOLD',
    'LEFT', 'RIGHT', 'UP', 'DOWN', 'BASEDIRS',
    'VGDLParser', 'VGDLSprite', 'BasicGame', 'GameEnvironment',
    'NO_DIR', 'stochastic_effects', 'VGDL_IMPORTED'
]
