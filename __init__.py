"""
VGDL (Video Game Definition Language) Environment

This package provides a Python implementation of the Video Game Definition Language (VGDL)
for reinforcement learning research. It includes the core VGDL engine, game definitions,
and Gym environment wrappers.
"""

import os
import sys
import warnings
from typing import Optional, List, Any, Dict, Union

# Make sure the current directory is in the path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Define version information at the top level
__version__ = '0.1.0'

# Import core modules with error handling
try:
    # Import utils module first
    from . import utils
    
    # Import the vgdl package and its components
    try:
        from .vgdl.core import VGDLParser, BasicGame, VGDLSprite
        # Note: VGDLGame is not found in core.py, using BasicGame instead
        # Resource and Avatar are imported from ontology
        from .vgdl.ontology import Resource, Avatar
        from .vgdl.ontology import *
        from .VGDLEnv import VGDLEnv
        _has_vgdl = True
    except ImportError as e:
        warnings.warn(f"Could not import VGDL core components: {str(e)}. Some features will be disabled.")
        _has_vgdl = False
    
    # Define VGDLGame as an alias for BasicGame for backward compatibility
    try:
        VGDLGame = BasicGame
    except NameError:
        # If BasicGame is not defined, create a dummy class
        class VGDLGame:
            def __init__(self, *args, **kwargs):
                raise ImportError("VGDLGame (BasicGame) could not be imported")
    
    __all__ = ['VGDLParser', 'BasicGame', 'VGDLSprite', 'Resource', 'Avatar', 'VGDLEnv', 'VGDLGame']
    
    # Also expose all ontology classes
    from .vgdl.ontology import (
        Immovable, Passive, ResourcePack, Flicker, Spreader, SpriteProducer,
        Portal, SpawnPoint, RandomNPC, OrientedSprite, Conveyor, Missile,
        Switch, OrientedFlicker, Walker, WalkJumper, RandomInertial,
        RandomMissile, ErraticMissile, Bomber, Chaser, Fleeing, AStarChaser,
        MovingAvatar, HorizontalAvatar, VerticalAvatar, FlakAvatar,
        OrientedAvatar, RotatingAvatar, RotatingFlippingAvatar,
        NoisyRotatingFlippingAvatar, ShootAvatar, AimedAvatar,
        AimedFlakAvatar, InertialAvatar, MarioAvatar, ClimbingAvatar,
        FrostBiteAvatar, Floe, FrostbiteIgloo
    )
    
    # Add ontology classes to __all__
    __all__.extend([
        'Immovable', 'Passive', 'ResourcePack', 'Flicker', 'Spreader', 'SpriteProducer',
        'Portal', 'SpawnPoint', 'RandomNPC', 'OrientedSprite', 'Conveyor', 'Missile',
        'Switch', 'OrientedFlicker', 'Walker', 'WalkJumper', 'RandomInertial',
        'RandomMissile', 'ErraticMissile', 'Bomber', 'Chaser', 'Fleeing', 'AStarChaser',
        'MovingAvatar', 'HorizontalAvatar', 'VerticalAvatar', 'FlakAvatar',
        'OrientedAvatar', 'RotatingAvatar', 'RotatingFlippingAvatar',
        'NoisyRotatingFlippingAvatar', 'ShootAvatar', 'AimedAvatar',
        'AimedFlakAvatar', 'InertialAvatar', 'MarioAvatar', 'ClimbingAvatar',
        'FrostBiteAvatar', 'Floe', 'FrostbiteIgloo'
    ])
    
    # Import successful, clear any previous warnings
    import warnings
    warnings.filterwarnings('ignore', message='Could not import VGDL components')
    
except ImportError as e:
    warnings.warn(f"Could not import VGDL components: {str(e)}")
    _has_vgdl = False
    
    # Import main components
    from .vgdl.core import VGDLParser, VGDLGame, VGDLSprite
    from .vgdl.ontology import BASEDIRS
    from .vgdl.stateobs import StateObsHandler
    from .vgdl.interfaces import GameEnvironment
    
    # Set default paths for game files
    DEFAULT_GAME_DIRS = [
        os.path.join(os.path.dirname(__file__), 'vgdl', 'games'),
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'games'),
        'games',
        os.path.join(os.path.dirname(__file__), 'games')
    ]
    
    # Add default game directories to BASEDIRS if they exist
    for game_dir in DEFAULT_GAME_DIRS:
        game_dir = os.path.abspath(game_dir)
        if os.path.exists(game_dir) and game_dir not in BASEDIRS:
            BASEDIRS.insert(0, game_dir)  # Insert at beginning to prioritize user directories
    
    # Make sure the current working directory is in the path
    cwd = os.getcwd()
    if cwd not in sys.path:
        sys.path.insert(0, cwd)
    
    # Make sure the vgdl directory is in the path
    vgdl_dir = os.path.dirname(os.path.abspath(__file__))
    if vgdl_dir not in sys.path:
        sys.path.insert(0, vgdl_dir)
    
    # Define the make function for creating game environments
    def make(game_name: str, game_folder: Optional[str] = None, **kwargs) -> GameEnvironment:
        """
        Create a VGDL game environment.
        
        Args:
            game_name: Name of the game (without .txt extension)
            game_folder: Path to the folder containing game files
            **kwargs: Additional arguments to pass to GameEnvironment
            
        Returns:
            GameEnvironment: Initialized game environment
        """
        if game_folder is None:
            # Try to find the game in default directories
            for base_dir in BASEDIRS:
                game_path = os.path.join(base_dir, f"{game_name}.txt")
                if os.path.exists(game_path):
                    game_folder = base_dir
                    break
            else:
                raise FileNotFoundError(
                    f"Could not find game {game_name} in any of {BASEDIRS}. "
                    f"Please provide the correct game_folder parameter."
                )
        
        env = GameEnvironment()
        try:
            env.load_games([game_name], game_folder=game_folder, **kwargs)
            return env
        except Exception as e:
            raise RuntimeError(f"Failed to load game {game_name} from {game_folder}: {str(e)}")
    
    # Define __all__ to expose public API
    __all__ = [
        'GameEnvironment',
        'VGDLParser',
        'VGDLGame',
        'VGDLSprite',
        'StateObsHandler',
        'BASEDIRS',
        'make',
        'vgdl'  # Expose the vgdl module
    ]
    
except ImportError as e:
    # Create dummy classes if imports fail
    class DummyClass:
        def __init__(self, *args, **kwargs):
            raise ImportError("VGDL components could not be imported. "
                           "Please check your installation and dependencies.")
    
    # Create dummy instances
    GameEnvironment = DummyClass
    VGDLParser = DummyClass
    VGDLGame = DummyClass
    VGDLSprite = DummyClass
    StateObsHandler = DummyClass
    BASEDIRS = []
    
    def make(*args, **kwargs):
        raise ImportError("VGDL components could not be imported. "
                        "Please check your installation and dependencies.")
    
    __all__ = [
        'GameEnvironment',
        'VGDLParser',
        'VGDLGame',
        'VGDLSprite',
        'StateObsHandler',
        'BASEDIRS',
        'make',
    ]

# Define a function to check if VGDL is fully functional
def is_vgdl_available():
    """Check if VGDL components are available."""
    return _has_vgdl
