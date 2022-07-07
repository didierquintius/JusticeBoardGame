import numpy as np
from player_area_class import Player, Area

SIZE_BOARD_X = 3
SIZE_BOARD_Y = 3
MAX_DEFENDER_DICE = 2
MAX_ATTACKER_DICE = 3
SPECIAL_DIE_DISTRIBUTION = [3, 3, 3, 4, 5, 6]


def trade_resources(player_1: Player, resource_1: str, n_resource_1: int, player_2: Player, resource_2: str,
                    n_resource_2: int):
    player_1.resources_stored[resource_1] -= n_resource_1
    player_2.resources_stored[resource_2] -= n_resource_2
    player_1.resources_stored[resource_2] += n_resource_2
    player_2.resources_stored[resource_1] -= n_resource_1


def calculate_dice_loss(dice_attack: np.array, dice_defend: np.array):
    loss_attack = 0
    loss_defend = 0
    while len(dice_attack) > 0 and len(dice_defend) > 0:
        highest_die_defend = max(dice_defend)
        highest_die_attack = max(dice_attack)
        if highest_die_attack > highest_die_defend:
            loss_defend += 1
        else:
            loss_attack += 1
        dice_attack = np.setdiff1d(dice_attack, highest_die_attack)
        dice_defend = np.setdiff1d(dice_defend, highest_die_defend)

    return loss_attack, loss_defend


def calculate_winner(n_dice_attacker: int, n_dice_defender: int, attacker_troops: int, defender_troops: int,
                     special_die: bool):
    if special_die:
        dice_defender = np.random.choice(5, n_dice_defender - 1)
        extra_die = np.random.choice(SPECIAL_DIE_DISTRIBUTION, 1)
        dice_defender = np.append(dice_defender, extra_die)
    else:
        dice_defender = np.random.choice(5, n_dice_defender)

    dice_attacker = np.random.choice(5, n_dice_attacker)
    loss_attack, loss_defence = calculate_dice_loss(dice_attacker, dice_defender)
    attacker_troops -= loss_attack
    defender_troops -= loss_defence

    return attacker_troops, defender_troops


def perform_battle(attacker_area: Area, defender_area: Area, defender: Player):
    # get troops of both areas
    attacker_troops = attacker_area.resources['troops']
    defender_troops = defender_area.resources['troops']

    # calculate dice defender
    n_dice_defender = min(defender_troops, MAX_DEFENDER_DICE)
    if defender_area.resources['cities'] == 1:
        special_die = True
    else:
        special_die = False

    # calculate dice attacker
    n_dice_attacker = min(attacker_troops, MAX_ATTACKER_DICE)

    # calculate winner
    attacker_troops, defender_troops = calculate_winner(n_dice_attacker, n_dice_defender, attacker_troops,
                                                        defender_troops, special_die)

    # adjust troops area
    attacker_area.resources['troops'] = max(attacker_troops, 0)
    defender_area.resources['troops'] = max(defender_troops, 0)

    # reset villages
    if defender_troops <= 0:
        defender_area.reset_area()
        defender.bloodshed_tokens += 1
        defender.remove_area(defender_area.name)


def possible_attack_areas(current_area: Area, areas: dict):
    deltas = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    possible_locations = []

    for delta_x, delta_y in deltas:
        possible_locations += [(current_area.location[0] - delta_x, current_area.location[1] - delta_y)]

    possible_areas = []

    for area_name, area in areas.items():
        if area.location in possible_locations:
            possible_areas += [area_name]

    return possible_areas


def generate_areas():
    areas = {}
    for i in range(SIZE_BOARD_X):
        for j in range(SIZE_BOARD_Y):
            area_name = f'A{i}{j}'
            area = Area(area_name)
            area.generate_state((i, j))
            areas[area_name] = area

    return areas
def start_game(players: list, areas: dict):
    for player in players:
        print('| ', end = "")
        for area_name, area in areas.items():
            if area.resources['troops'] == 0:
                print(area_name, end=" | ")
        print("")
        chosen_area = input(f'Choose area, {player.name}:')

        player.choose_start_area(areas[chosen_area])

def player_turn(player: Player):
    player.check_win()
    player
