from game_play_functions import *
from player_area_class import Player, Area

areas = generate_areas()
player_names = ['Player1', 'Player2']
players = []
for player_name in player_names:
    players += [Player(player_name)]
start_game(players, areas)
player_turn(players[0], areas, players)
