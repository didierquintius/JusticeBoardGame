import numpy as np
import pandas as pd

FIXED_HOUSE_DISTRB = [0.1, 0.6, 0.2, 0.1]
MAX_RESOURCES_AREA = 5
AREA_RESOURCE_DISTRB = [0.4, 0.4, 0.2]
MAX_TRUST = 3
AREA_RESOURCES = ['material', 'coins', 'food']
PLAYER_RESOURCES = ['villages', 'trust', 'troops', 'cities']
SIZE_BOARD_X = 6
SIZE_BOARD_Y = 6
PRICE_MILITIA = 1
PRICE_VILLAGE_MATERIAL = 5
PRICE_VILLAGE_COINS = 5

PRICE_CITY_MATERIAL = 5
PRICE_CITY_COINS = 5

MAX_VILLAGES = 4
MAX_DEFENDER_DICE = 2
MAX_ATTACKER_DICE = 3
SPECIAL_DIE_DISTRB = [3, 3, 3, 4, 5, 6]


class Area:
    def __init__(self, name: str):
        self.name = name
        self.fixed_villages = 0
        self.resources = {}
        for resource in AREA_RESOURCES + PLAYER_RESOURCES:
            self.resources[resource] = 0
        self.location = (0, 0)

    def generate_state(self, location: tuple):
        # load the general information into its correct variables
        self.location = location

        # select a random amount of villages for each area between 0 and 3
        self.fixed_villages = np.random.choice(4, 1, p=FIXED_HOUSE_DISTRB)[0]
        self.resources['villages'] = self.fixed_villages

        # Each area has maximum number of resources
        # there always is at least one food resource per fixed house therefore
        # the amount of other resources (which are randomly selected) is limited by this maximum
        n_other_resources = MAX_RESOURCES_AREA - self.fixed_villages

        # from the fixed resources randomly choose how much will be present in the area
        gen_area_resources = np.random.choice(AREA_RESOURCES, n_other_resources,
                                              p=AREA_RESOURCE_DISTRB)

        # count the amount of resources that were chosen of each fixed resources.
        for resource in AREA_RESOURCES:
            self.resources[resource] = sum(gen_area_resources == resource)
            if resource == 'food':
                self.resources[resource] += self.fixed_villages

    def add_trust(self):
        if self.resources['trust'] < MAX_TRUST:
            self.resources['trust'] += 1

    def reset_area(self):
        # when an area is reset all the resources belonging to the player that owned the area are removed
        for resource in PLAYER_RESOURCES:
            self.resources[resource] = 0
        self.resources['villages'] = self.fixed_villages


class Player:
    def __init__(self, name: str):
        self.name = name
        self.resources_beginning_round = {}
        for resource in AREA_RESOURCES + PLAYER_RESOURCES:
            self.resources_beginning_round[resource] = 0
        self.resources_stored = {}
        for resource in PLAYER_RESOURCES:
            self.resources_stored[resource] = 0
        self.player_areas = []
        self.unplaced_troops = 0
        self.hunger_tokens = 0
        self.bloodshed_tokens = 0

    def add_area(self, area_name: str):
        self.player_areas += [area_name]

    def remove_area(self, area_name: str):
        self.player_areas.remove(area_name)

    def set_beginning_resources(self, areas: dict):
        df_resources = pd.DataFrame()

        # calculate the amount of resources the player has at the beginning by adding the resources from each of the
        # areas that the player owns
        for area in self.player_areas:
            df_resources = df_resources.append(areas[area].resources, ignore_index=True)

        total_resources = df_resources.sum()

        for resource in self.resources_beginning_round:
            self.resources_beginning_round[resource] = total_resources[resource]

    def gather_resources(self):
        for resource in AREA_RESOURCES:
            self.resources_stored[resource] += self.resources_beginning_round[resource]

    def add_troops(self, n_troops: int):

        """"
        Description: a player can only add as much troops as he can either by with the coins he owns or with how many
        villages he owns
        """

        # the subtraction with unplaced troops is for when a player decides he wants to buy more troops
        # in this case the amount of possible villages to extract units from decreases because these villages have
        # already been used
        troops_to_add = min(n_troops, self.resources_beginning_round['villages'] - self.unplaced_troops,
                            int(self.resources_stored['coins'] / PRICE_MILITIA))
        self.resources_stored['coins'] -= troops_to_add * PRICE_MILITIA
        self.unplaced_troops += troops_to_add

    def add_troops_to_area(self, area: Area, n_troops: int):
        if area.name not in self.player_areas:
            print('Not in player area')
            return None

        troops_to_place = min(n_troops, self.unplaced_troops)
        area.resources['troops'] += troops_to_place
        self.unplaced_troops -= troops_to_place

    def add_hunger_tokens(self):
        if self.resources_stored['food'] < self.resources_beginning_round['villages']:
            self.hunger_tokens += 1

    def add_house(self, area, n_villages):
        max_n_villages_resources = min(int(self.resources_stored['material'] / PRICE_VILLAGE_MATERIAL),
                                       int(self.resources_stored['coins'] / PRICE_VILLAGE_COINS))

        max_n_villages_area = MAX_VILLAGES - area.resources['villages']
        villages_to_add = min(max_n_villages_resources, max_n_villages_area, n_villages)
        area.resources['villages'] += villages_to_add

    def add_city(self, area: Area):
        resources_for_1_city = min(int(self.resources_stored['material'] / PRICE_CITY_MATERIAL),
                                   int(self.resources_stored['coins'] / PRICE_CITY_COINS))
        if area.resources['cities'] == 0 and resources_for_1_city > 0:
            area.resources['cities'] = 1

    def conquer_area(self, area: Area, n_troops: int):
        self.add_area(area.name)
        self.add_troops_to_area(area, n_troops)


def calculate_dice_loss(dice_attack, dice_defend):
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
    while attacker_troops > 1 and defender_troops > 0:
        if special_die:
            dice_defender = np.random.choice(5, n_dice_defender - 1)
            extra_die = np.random.choice(SPECIAL_DIE_DISTRB, 1)
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
    if attacker_troops > 0:
        defender_area.reset_area()
        defender.bloodshed_tokens += 1
        defender.remove_area(defender_area.name)


def surrender(defender_area: Area, defender: Player):
    defender_area.resources['troops'] = 0
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


if __name__ == '__main__':
    print(calculate_winner(3, 2, 10, 12, False))
