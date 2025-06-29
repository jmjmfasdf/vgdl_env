
# Import the centralized vgdl_imports module to ensure all VGDL components are available
import sys
import os

# Add necessary paths to sys.path
vgdl_env_path = os.path.dirname(os.path.abspath(__file__))
thinker_dir = os.path.dirname(vgdl_env_path)
paths_to_add = [
    vgdl_env_path,  # /path/to/thinker/thinker/vgdl_env
    thinker_dir,  # /path/to/thinker/thinker
    os.path.dirname(thinker_dir),  # /path/to/thinker
    os.path.join(vgdl_env_path, 'vgdl')  # Direct vgdl module path
]

for path in paths_to_add:
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)

# Set flag to indicate VGDL components are imported
VGDL_IMPORTED = True
print("Successfully imported VGDL components in utils.py")

from vgdl.rlenvironmentnonstatic import createRLInputGameFromStrings
import os
os.environ['SDL_AUDIODRIVER'] = 'dsp'
import pygame
import numpy as np
import pdb


def load_game(game_name, games_folder):
	def _load_level(gameString, levelString):

		headless = True

		rleCreateFunc = lambda: createRLInputGameFromStrings(gameString, levelString)

		# (self, gameDef, levelDef, observationType=OBSERVATION_GLOBAL, visualize=False, actionset=BASEDIRS, positions=None, **kwargs)

		rle = rleCreateFunc()
		# import pdb; pdb.set_trace()
		rle.visualize = True
		if headless:
			os.environ["SDL_VIDEODRIVER"] = "dummy"
		#pdb.set_trace()
		pygame.init()

		return rle

	def _gen_color():
		from vgdl.colors import colorDict
		color_list = colorDict.values()
		color_list = [c for c in color_list if c not in ['UUWSWF']]
		for color in color_list:
			yield color
	
	# Extract the base game name from formats like "vgdl-bait-lvl0-v0"
	base_game_name = game_name
	if 'vgdl-' in game_name:
		# Extract the game name (e.g., "bait" from "vgdl-bait-lvl0-v0")
		parts = game_name.split('-')
		if len(parts) >= 2:
			base_game_name = parts[1]
			# If there's a level specified in the name, extract it
			if len(parts) >= 3 and 'lvl' in parts[2]:
				try:
					level_num = int(parts[2].replace('lvl', ''))
				except ValueError:
					pass

	file_list = {}
	# First check if there's a subdirectory for this game
	game_subdir = None
	for item in os.listdir(games_folder):
		if os.path.isdir(os.path.join(games_folder, item)) and base_game_name in item:
			game_subdir = os.path.join(games_folder, item)
			break
	
	# If we found a subdirectory, look for game files there
	if game_subdir:
		for file in os.listdir(game_subdir):
			if 'DS' not in file:
				if base_game_name == file.split('.txt')[0] or base_game_name == file.split('_lvl')[0]:
					if 'lvl' not in file: 
						file_list['game'] = os.path.join(os.path.basename(game_subdir), file)
					else: 
						try:
							level = int(file.split('_lvl')[1][0])
							file_list[level] = os.path.join(os.path.basename(game_subdir), file)
						except (IndexError, ValueError):
							pass
	
	# If we didn't find files in a subdirectory, look in the main directory
	if 'game' not in file_list:
		for file in os.listdir(games_folder):
			if 'DS' not in file:
				if 'expt_ee' in game_name:
					if game_name in file:
						if 'lvl' not in file:
							level = file.split('desc_')[1][0]
							file_list['game_{}'.format(level)] = file
						else:
							level = file.split('_lvl')[1][0]
							file_list[int(level)] = file
				else:
					if base_game_name == file.split('.txt')[0] or base_game_name == file.split('_lvl')[0]:
						if 'lvl' not in file: 
							file_list['game'] = file
						else: 
							try:
								level = int(file.split('_lvl')[1][0])
								file_list[level] = file
							except (IndexError, ValueError):
								pass
	
	# If we still don't have a game file, raise a more helpful error
	if 'game' not in file_list and 'expt_ee' not in game_name:
		raise KeyError(f"Could not find game file for '{game_name}' (base name: '{base_game_name}') in folder '{games_folder}'. Available files: {os.listdir(games_folder)}")


	# new_doc = ''
	# with open('{}/{}'.format(games_folder, file_list['game']), 'r') as f:
	# 	new_doc = []
	# 	g = _gen_color()
	# 	for line in f.readlines():
	# 		new_line = (" ".join([string if string[:4]!="img="
	# 			else "color={}".format(next(g))
	# 			for string in line.split(" ")]))
	# 		new_doc.append(new_line)
	# 	new_doc = "\n".join(new_doc)

	# import pdb; pdb.set_trace()

	if 'expt_ee' not in game_name:
		with open('{}/{}'.format(games_folder, file_list['game']), 'r') as game:
			gameString = game.read()

	env_list = {}

	num_levels = len(file_list.keys())-1
	if 'expt_ee' in game_name:
		num_levels = int(len(file_list.keys())/2)

	for lvl_idx in range(num_levels):

		if 'expt_ee' in game_name:

			with open('{}/{}'.format(games_folder, file_list['game_{}'.format(lvl_idx)]), 'r') as game:
				gameString = game.read()

		with open('{}/{}'.format(games_folder, file_list[lvl_idx]), 'r') as level:
			levelString = level.read()

		# import pdb; pdb.set_trace()

		env_list[lvl_idx] = _load_level(gameString, levelString)

	return env_list




























