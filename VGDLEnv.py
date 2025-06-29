
# Use gymnasium instead of gym for compatibility with AsyncVectorEnv
import gymnasium as gym
from gymnasium import spaces
# Import colors directly to make them available in the module namespace
from vgdl.colors import *
import vgdl.colors as colors  # Also import as module for direct access
from vgdl import utils  # Use vgdl.utils instead of direct utils import
import pygame
from pygame.locals import K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE
from vgdl.rlenvironmentnonstatic import createRLInputGameFromStrings
import numpy as np
import imageio
from skimage.transform import resize
import pdb
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class VGDLEnv(gym.Env):
    """
    Define a VGDL environment that follows the Gym interface.
    The environment defines which actions can be taken at which point and
    when the agent receives which reward.
    """

    def __init__(self, game_name, game_folder):
        self.__version__ = "0.1.0"
        self.metadata = {'render.modes': ['human', 'rgb_array']}

        self.game_name = game_name
        self.game_folder = game_folder
        
        # Load the game
        self.env_list = utils.load_game(game_name, game_folder)
        self.lvl = 0
        self.set_level(self.lvl)
        
        # Define action space
        self.actions = [0, K_RIGHT, K_LEFT, K_UP, K_DOWN, K_SPACE]
        self.action_space = spaces.Discrete(len(self.actions))
        
        # Get initial observation to determine observation space
        initial_obs = self.render()
        self.observation_space = spaces.Box(
            low=0, high=255, shape=initial_obs.shape, dtype=np.uint8
        )
        
        # For tracking rewards and learning progress
        self.total_reward = 0
        self.episode_count = 0
        self.step_count = 0

    def set_level(self, lvl):
        """Set the current level of the game."""
        self.current_env = self.env_list[lvl]
        self.current_env.softReset()

    def step(self, action):
        """
        The agent takes a step in the environment.
        
        Parameters
        ----------
        action : int
            Index of the action to take
            
        Returns
        -------
        observation, reward, terminated, truncated, info : tuple
            observation (numpy.ndarray) : 
                Current game state as an image
            reward (float) :
                Reward for this step
            terminated (bool) :
                Whether the episode has ended due to termination condition
            truncated (bool) :
                Whether the episode has ended due to truncation (e.g., time limit)
            info (dict) :
                Additional information (win/loss status, etc.)
        """
        self.step_count += 1
        
        # Get the previous score for reward calculation
        prev_score = self.current_env._game.score
        
        # Execute the action in the environment
        results = self.current_env.step(self.actions[action])
        
        # Extract results
        # results contains: {'observation':observation, 'reward':reward, 'pcontinue':pcontinue, 
        #                    'effectList':events, 'ended':ended, 'win':won, 'termination':termination}
        reward = results['reward']
        ended = results['ended']
        win = results['win']
        
        # Alternative reward calculation if needed
        # score = self.current_env._game.score
        # reward = score - prev_score
        
        # Track total reward for debugging
        self.total_reward += reward
        
        # Get the current observation (game state)
        observation = self.render()
        
        # Create info dictionary with additional information
        info = {
            'win': win,
            'game_score': self.current_env._game.score,
            'total_reward': self.total_reward
        }
        
        # Log episode completion
        if ended:
            self.episode_count += 1
        
        # In gymnasium, we need to return 5 values: observation, reward, terminated, truncated, info
        # For VGDL, we don't have a separate concept of truncation, so we set truncated=False
        return observation, reward, ended, False, info

    def reset(self, *, seed=None, options=None):
        """
        Reset the environment to the initial state.
        
        Parameters
        ----------
        seed : int, optional
            Seed for random number generator
        options : dict, optional
            Additional options for reset
            
        Returns
        -------
        observation : numpy.ndarray
            Initial observation of the environment
        info : dict
            Additional information
        """
        
        # Handle seed if provided
        if seed is not None:
            np.random.seed(seed)
        
        # Reset tracking variables
        self.total_reward = 0
        self.step_count = 0
        
        # Reload the game to ensure a clean state
        self.env_list = utils.load_game(self.game_name, self.game_folder)
        self.set_level(self.lvl)
        self.current_env.softReset()
        
        # Return the initial observation and empty info dict (gymnasium API requires this)
        return self.render(), {}

    def render(self, mode='rgb_array'):
        """
        Render the current game state.
        
        Parameters
        ----------
        mode : str
            Rendering mode ('rgb_array' or 'human')
            
        Returns
        -------
        numpy.ndarray
            RGB image of the current game state
        """
        game = self.current_env._game
        
        # Create an image from the game state
        im = np.empty([game.screensize[1], game.screensize[0], 3], dtype=np.uint8)
        bg = np.array(colors.LIGHTGRAY, dtype=np.uint8)  # background
        im[:] = bg
        
        # Draw all sprites
        for className in game.sprite_order:
            if className in game.sprite_groups:
                for sprite in game.sprite_groups[className]:
                    r, c, h, w = sprite.rect.top, sprite.rect.left, sprite.rect.height, sprite.rect.width
                    im[r:r+h, c:c+w, :] = np.array(sprite.color, dtype=np.uint8)
        
        # Resize if needed
        if mode == 'human':
            # You could implement a viewer here if needed
            pass
            
        return im
        
    def close(self):
        """Clean up resources."""
        pass
