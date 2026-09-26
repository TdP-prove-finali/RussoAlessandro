from database.DAO import DAO
from model import constants


class Model:
    def __init__(self):
        pass

    def get_positions(self, season):
        team_count = len(DAO.get_constructors(season))
        return list(range(1, team_count + 1))

    def get_cost_cap(self, season):
        race_count = len(DAO.get_races(season))
        return constants.cost_cap(season, race_count)

    def get_available_budget(self, season, other_costs):
        return self.get_cost_cap(season) - other_costs
