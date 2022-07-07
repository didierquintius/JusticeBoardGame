from game_play_functions import *
from player_area_class import Player, Area
if __name__ == '__main__':
    areas = generate_areas()
    player1 = Player('Player1')
    player2 = Player('Player2')
    players = [player1, player2]
    start_game(players, areas)
    print(player1.player_areas)
    print(areas['A00'].resources['troops'])
