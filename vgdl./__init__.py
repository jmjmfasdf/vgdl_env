"""
VGDL (Video Game Definition Language) - A framework for defining 2D video games.
"""

import os
import sys
import warnings

# Add the current directory to the path to allow relative imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import core components with error handling
try:
    # Note: pybrain and structure modules were previously used but are no longer required
    # The package has been refactored to remove these dependencies
    # If you encounter any issues related to missing modules, please report them
    pass
    
    # Import main modules
    from . import core
    from . import ontology
    from . import stateobs
    from . import interfaces
    
    # Import utils from parent directory
    import os
    import sys
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if parent_dir not in sys.path:
        sys.path.insert(0, parent_dir)
    try:
        # Import utils from parent directory and expose as vgdl.utils
        import utils
        sys.modules['vgdl.utils'] = utils  # Make utils available as vgdl.utils
        from utils import *  # Import utils from parent directory
    except ImportError as e:
        warnings.warn(f"Could not import utils from parent directory: {e}")
    
    # Import main classes
    from .core import VGDLParser, BasicGame, VGDLSprite
    from .ontology import BASEDIRS
    from .stateobs import StateObsHandler
    from .interfaces import GameEnvironment
    
    # Export main classes and modules
    __all__ = [
        # Main classes
        'VGDLParser',
        'VGDLGame',
        'VGDLSprite',
        'StateObsHandler',
        'GameEnvironment',
        'BASEDIRS',
        
        # Modules
        'core',
        'ontology',
        'stateobs',
        'interfaces',
        'tools',
    ]
    
    # Make sure BASEDIRS includes the local games directory
    local_games = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'games')
    if local_games not in BASEDIRS and os.path.exists(local_games):
        BASEDIRS.insert(0, local_games)
        
except ImportError as e:
    warnings.warn(f"Could not import VGDL components: {e}")
    
    # Create dummy classes if imports fail
    # This allows the package to be imported even if some components are missing
    class DummyClass:
        def __init__(self, *args, **kwargs):
            raise ImportError("VGDL components could not be imported. "
                           "Please check your installation and dependencies.")
    
    # Create dummy instances
    VGDLParser = DummyClass
    BasicGame = DummyClass
    VGDLSprite = DummyClass
    StateObsHandler = DummyClass
    GameEnvironment = DummyClass
    BASEDIRS = []
    
    # Dummy modules
    core = DummyClass()
    ontology = DummyClass()
    stateobs = DummyClass()
    interfaces = DummyClass()
    tools = DummyClass()
    
    __all__ = [
        'VGDLParser',
        'VGDLGame',
        'VGDLSprite',
        'StateObsHandler',
        'GameEnvironment',
        'BASEDIRS',
        'core',
        'ontology',
        'stateobs',
        'interfaces',
        'tools',
    ]

# Version information
__version__ = '0.1.0'
