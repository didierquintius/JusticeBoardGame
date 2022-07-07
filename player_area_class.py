import numpy as np
import pandas as pd

FIXED_HOUSE_DISTRIBUTION = [0.1, 0.6, 0.2, 0.1]
MAX_RESOURCES_AREA = 5
AREA_RESOURCE_DISTRIBUTION = [0.4, 0.4, 0.2]
MAX_TRUST = 3
AREA_RESOURCES = ['material', 'coins', 'food']
PLAYER_RESOURCES = ['villages', 'trust', 'troops', 'cities']
PRICE_MILITIA = 1
PRICE_VILLAGE_MATERIAL = 5
PRICE_VILLAGE_COINS = 5
PRICE_CITY_MATERIAL = 5
PRICE_CITY_COINS = 5
MAX_VILLAGES = 4
MIN_TRUST_TO_WIN = 20
START_TROOPS = 5
CITY_POINT_MULTIPLIER = 5

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
        self.fixed_villages = np.random.choice(4, 1, p=FIXED_HOUSE_DISTRIBUTION)[0]
        self.resources['villages'] = self.fixed_villages

        # Each area has maximum number of resources
        # there always is at least one food resource per fixed house therefore
        # the amount of other resources (which are randomly selected) is limited by this maximum
        n_other_resources = MAX_RESOURCES_AREA - self.fixed_villages

        # from the fixed resources randomly choose how much will be present in the area
        gen_area_resources = np.random.choice(AREA_RESOURCES, n_other_resources,
                                              p=AREA_RESOURCE_DISTRIBUTION)

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
        for resource in AREA_RESOURCES:
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
        Description: a player can only add as many troops as he can buy with the coins he owns and how many
        villages he owns
        """

        # the subtraction with unplaced troops is for when a player decides he wants to buy more troops
        # in this case the amount of possible villages to extract units from decreases because these villages have
        # already been used
        unused_villages = self.resources_beginning_round['villages'] - self.unplaced_troops
        n_villages_from_coins = int(self.resources_stored['coins'] / PRICE_MILITIA)
        troops_to_add = min(n_troops, unused_villages, n_villages_from_coins)
        self.resources_stored['coins'] -= troops_to_add * PRICE_MILITIA
        self.unplaced_troops += troops_to_add

    def calc_possible_troops(self):
        unused_villages = self.resources_beginning_round['villages'] - self.unplaced_troops
        n_villages_from_coins = int(self.resources_stored['coins'] / PRICE_MILITIA)
        possible_troops = min(unused_villages, n_villages_from_coins)
        return possible_troops

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

    def can_add_village(self, area: Area):
        enough_coins = self.resources_stored['coins'] >= PRICE_VILLAGE_COINS
        enough_material = self.resources_stored['material'] >= PRICE_VILLAGE_MATERIAL

        possibility = enough_coins and enough_material and area.resources['villages'] < MAX_VILLAGES
        return possibility

    def can_add_city(self, area: Area):
        enough_coins = self.resources_stored['coins'] >= PRICE_CITY_COINS
        enough_material = self.resources_stored['material'] >= PRICE_CITY_MATERIAL

        possibility = enough_coins and enough_material and area.resources['cities'] == 0
        return possibility

    def conquer_area(self, area: Area, n_troops: int):
        self.add_area(area.name)
        self.add_troops_to_area(area, n_troops)

    def surrender_area(self, area: Area):
        area.resources['troops'] = 0
        self.remove_area(area.name)

    def check_win(self):
        win_status = self.resources_beginning_round['trust'] >= MIN_TRUST_TO_WIN
        return win_status

    def calculate_trade_possibilities(self):
        trade_possibilities = {}
        for resource, n_resource in self.resources_stored.keys():
            trade_possibilities[resource] = np.arange(n_resource) + 1
        return trade_possibilities

    def choose_start_area(self, area: Area):
        self.conquer_area(area, START_TROOPS)

    def calc_points(self):
        points = self.resources_beginning_round['trust'] - self.hunger_tokens - self.bloodshed_tokens +\
                 self.resources_beginning_round['villages'] +\
                 CITY_POINT_MULTIPLIER * self.resources_beginning_round['cities']

        return points
