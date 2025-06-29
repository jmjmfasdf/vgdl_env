'''
Created on 2013 2 18

@author: Tom Schaul (schaul@gmail.com)
Modified for Python 3 compatibility and pybrain removal

Wrappers for games to interface them with artificial players.
'''

import numpy as np
import pygame    

from vgdl.ontology import BASEDIRS
from vgdl.core import VGDLSprite
# Import StateObsHandler from the local package
from .stateobs import StateObsHandler 

class GameEnvironment(StateObsHandler):
    """ 
    A simple environment wrapper for VGDL games.
    This is a simplified version that doesn't depend on pybrain.
    """
    
    # If the visualization is enabled, all actions will be reflected on the screen.
    visualize = False
    
    # Required properties for gym-like interface
    action_space = None
    observation_space = None
    reward_range = (-np.inf, np.inf)
    metadata = {'render.modes': ['human', 'rgb_array']}
    
    def step(self, action):
        """
        Run one timestep of the environment's dynamics.
        Returns:
            observation (object): agent's observation of the current environment
            reward (float) : amount of reward returned after previous action
            done (bool): whether the episode has ended
            info (dict): contains auxiliary diagnostic information
        """
        raise NotImplementedError
    
    def reset(self):
        """
        Resets the state of the environment and returns an initial observation.
        Returns:
            observation (object): the initial observation
        """
        raise NotImplementedError
        
    def render(self, mode='human'):
        """
        Renders the environment.
        """
        if not self.visualize:
            return None
            
        if not hasattr(self, 'screen'):
            pygame.init()
            self.screen = pygame.display.set_mode((self.width * 10, self.height * 10))
            
        # Simple rendering - can be customized based on game state
        self.screen.fill((0, 0, 0))
        pygame.display.flip()
        return np.zeros((self.height * 10, self.width * 10, 3), dtype=np.uint8)
    
    def close(self):
        """
        Perform any necessary cleanup.
        """
        if hasattr(self, 'screen'):
            pygame.quit()
            del self.screen
            
    def seed(self, seed=None):
        """
        Sets the seed for this env's random number generator.
        """
        np.random.seed(seed)
        return [seed]
    
    # In that case, optionally wait a few milliseconds between actions?
    actionDelay = 0
    
    # Recording events (in slightly redundant format state-action-nextstate)
    recordingEnabled = False
        
    def __init__(self, game, actionset=BASEDIRS, **kwargs):
        # Initialize the parent class with the game and any additional kwargs
        StateObsHandler.__init__(self, game=game, **kwargs)
        
        # Store the game instance and action set
        self._game = game
        self._actionset = actionset
        
        # Initialize state-related attributes
        self._initstate = self.getState()
        ns = self._stateNeighbors(self._initstate) if self._initstate else []
        self.outdim = (len(ns) + 1) * len(getattr(self, '_obstypes', ['position']))
        
        # Initialize the environment
        self.reset()
    
    def reset(self):
        self._game._initScreen(self._game.screensize, not self.visualize)
        self.setState(self._initstate)
        # if no avatar starting location is specified, the default one will be to place it randomly
        self._game.randomizeAvatar()    
            
        self._game.kill_list = []
        if self.visualize:
            pygame.display.flip()    
        if self.recordingEnabled:
            self._last_state = self.getState()
            self._allEvents = []            
        self._game.keystate = pygame.key.get_pressed()  
            
    def getSensors(self, state=None):
        if state is None:
            state = self.getState()
        if self.orientedAvatar:
            pos = (state[0], state[1])
        else:
            pos = state 
        res = zeros(self.outdim)
        ns = [pos] + self._stateNeighbors(state)
        for i, n in enumerate(ns):
            os = self._rawSensor(n)
            res[i::len(ns)] = os
        return res
    
    def setState(self, state):
        if self.visualize and self._avatar is not None:
            self._avatar._clear(self._game.screen, self._game.background)        
        StateObsHandler.setState(self, state)        
        self._game._clearAll(self.visualize)  
        assert len(self._game.kill_list) ==0          
        
    def performAction(self, action, onlyavatar=False):
        """ Action is an index for the actionset.  """
        if action is None:
            return   
        # if actions are given as a vector, pick the argmax
        import numpy
        # Use numpy.argmax instead of scipy.argmax
        from numpy import argmax
        try:
            from pybrain.utilities import drawIndex
        except ImportError:
            # Fallback implementation if pybrain is not available
            def drawIndex(probs):
                """Draw an index given probabilities."""
                return numpy.argmax(probs)
        if isinstance(action, numpy.ndarray):
            if abs(sum(action) -1) < 1e5:
                # vector represents probabilities
                action = drawIndex(action)
            else:
                action = argmax(action) 
    
        
        # take action and compute consequences
        self._avatar._readMultiActions = lambda *x: [self._actionset[action]]        
        self._game._clearAll(self.visualize)
        
        # update sprites 
        if onlyavatar:
            self._avatar.update(self._game)
        else:
            for s in self._game:
                s.update(self._game)
        
        # handle collision effects                
        self._game._eventHandling()
        self._game._clearAll(self.visualize)
        
        # update screen
        if self.visualize:
            self._game._drawAll()                            
            pygame.display.update(VGDLSprite.dirtyrects)
            VGDLSprite.dirtyrects = []
            pygame.time.wait(self.actionDelay)       
                       

        if self.recordingEnabled:
            self._previous_state = self._last_state
            self._last_state = self.getState()
            self._allEvents.append((self._previous_state, action, self._last_state))
            
    def _isDone(self):
        # remember reward if the final state ends the game
        for t in self._game.terminations[1:]: 
            # Convention: the first criterion is for keyboard-interrupt termination
            ended, win = t.isDone(self._game)
            if ended:
                return ended, win
        return False, False

    def rollOut(self, action_sequence, init_state=None, callback=lambda * _:None):
        """ Take a sequence of actions. """
        if init_state is not None:
            self.setState(init_state)
        for a in action_sequence:
            print(a, self.getState())
            if self._isDone()[0]:
                break
            self.performAction(a)
            callback(self)
        

class GameTask:
    """ A minimal Task wrapper that only considers win/loss information. """
    _ended = False
    
    maxSteps = None
    
    def __init__(self, env):
        self.env = env
        self.reset()
    
    def reset(self):
        """Reset the task and return the initial observation."""
        self.env.reset()
        self._ended = False
        return self.env.getSensors()
    
    def getObservation(self):
        """Get the current observation from the environment."""
        return self.env.getSensors()
    
    def performAction(self, action):
        """Perform an action in the environment."""
        self.env.performAction(action)
        
    def getReward(self):
        """Get the current reward."""
        if self.env._isDone()[0]:
            self._ended = True
            return self.env._isDone()[1]
        return 0
    
    def isFinished(self):
        """Check if the task is finished."""
        if self.maxSteps is not None:
            if self.samples >= self.maxSteps:
                return True
        return self._ended


   
   
   
# ==========================================================
# some small tests
# ==========================================================
   
    

def testRollout(actions=[0, 0, 2, 2, 0, 3] * 20):        
    from examples.gridphysics.mazes import polarmaze_game, maze_level_1
    from core import VGDLParser
    game_str, map_str = polarmaze_game, maze_level_1
    g = VGDLParser().parseGame(game_str)
    g.buildLevel(map_str)    
    env = GameEnvironment(g, visualize=True, actionDelay=100)
    env.rollOut(actions)
        
    
def testRolloutVideo(actions=[0, 0, 2, 2, 0, 3] * 2):        
    from examples.gridphysics.mazes import polarmaze_game, maze_level_1
    from core import VGDLParser
    from vgdl.tools import makeGifVideo
    game_str, map_str = polarmaze_game, maze_level_1
    g = VGDLParser().parseGame(game_str)
    g.buildLevel(map_str)
    makeGifVideo(GameEnvironment(g, visualize=True), actions)
    
    
def testInteractions():
    from random import randint
    from pybrain.rl.experiments.episodic import EpisodicExperiment
    from core import VGDLParser
    from examples.gridphysics.mazes import polarmaze_game, maze_level_1    
    from pybrain.rl.agents.agent import Agent
    
    class DummyAgent(Agent):
        total = 4
        def getAction(self):
            res = randint(0, self.total - 1)
            return res    
        
    game_str, map_str = polarmaze_game, maze_level_1
    g = VGDLParser().parseGame(game_str)
    g.buildLevel(map_str)
    
    env = GameEnvironment(g, visualize=True, actionDelay=100)
    task = GameTask(env)
    agent = DummyAgent()
    exper = EpisodicExperiment(task, agent)
    res = exper.doEpisodes(2)
    print(res)

def testPolicyAgent():
    from pybrain.rl.experiments.episodic import EpisodicExperiment
    from core import VGDLParser
    from examples.gridphysics.mazes import polarmaze_game, maze_level_2
    from agents import PolicyDrivenAgent
    game_str, map_str = polarmaze_game, maze_level_2
    g = VGDLParser().parseGame(game_str)
    g.buildLevel(map_str)
    
    env = GameEnvironment(g, visualize=False, actionDelay=100)
    task = GameTask(env)
    agent = PolicyDrivenAgent.buildOptimal(env)
    env.visualize = True
    env.reset()
    exper = EpisodicExperiment(task, agent)
    res = exper.doEpisodes(2)
    print(res)
    
def testRecordingToGif(human=False):
    from pybrain.rl.experiments.episodic import EpisodicExperiment
    from core import VGDLParser
    from examples.gridphysics.mazes import polarmaze_game, maze_level_2
    from agents import PolicyDrivenAgent, InteractiveAgent    
    from vgdl.tools import makeGifVideo
    
    game_str, map_str = polarmaze_game, maze_level_2
    g = VGDLParser().parseGame(game_str)
    g.buildLevel(map_str)
    env = GameEnvironment(g, visualize=human, recordingEnabled=True, actionDelay=200)
    task = GameTask(env)
    if human:
        agent = InteractiveAgent()
    else:
        agent = PolicyDrivenAgent.buildOptimal(env)
    exper = EpisodicExperiment(task, agent)
    res = exper.doEpisodes(1)
    print(res)
    
    actions = [a for _, a, _ in env._allEvents]
    print(actions)
    makeGifVideo(env, actions, initstate=env._initstate)
    
def testAugmented():
    from core import VGDLParser
    from pybrain.rl.experiments.episodic import EpisodicExperiment
    from mdpmap import MDPconverter
    from agents import PolicyDrivenAgent    
    
    
    zelda_level2 = """
wwwwwwwwwwwww
wA wwk1ww   w
ww  ww    1 w
ww     wwww+w
wwwww1ww  www
wwwww  0  Gww
wwwwwwwwwwwww
"""

    
    from examples.gridphysics.mazes.rigidzelda import rigidzelda_game
    g = VGDLParser().parseGame(rigidzelda_game)
    g.buildLevel(zelda_level2)
    env = GameEnvironment(g, visualize=False,
                          recordingEnabled=True, actionDelay=150)
    C = MDPconverter(g, env=env, verbose=True)
    Ts, R, _ = C.convert()
    print(C.states)
    print(Ts[0])
    print(R)
    env.reset()
    agent = PolicyDrivenAgent.buildOptimal(env)
    env.visualize = True
    env.reset()
    task = GameTask(env)    
    exper = EpisodicExperiment(task, agent)
    exper.doEpisodes(1)
    
    
if __name__ == "__main__":
    #testRollout()
    #testInteractions()
    #testRolloutVideo()
    #testPolicyAgent()
    #testRecordingToGif(human=True)
    testRecordingToGif(human=False)
    #testAugmented()
