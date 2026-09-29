import math

import networkx as nx

from database.DAO import DAO
from model import constants
from model.development_start import DevelopmentStart
from model.shipment import Shipment
from model.wishlist_item import WishlistItem


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._races = []
        self._source = None
        self._components = []
        self._routes = {}
        self._routes_constructor_id = None

    def get_positions(self, season):
        team_count = len(DAO.get_constructors(season))
        return list(range(1, team_count + 1))

    def get_cost_cap(self, season):
        race_count = len(DAO.get_races(season))
        return constants.cost_cap(season, race_count)

    def get_available_budget(self, season, other_costs):
        return self.get_cost_cap(season) - other_costs

    def get_components(self):
        if not self._components:
            self._components = DAO.get_components()
        return self._components

    def build_wishlist(self, quantities):
        wishlist = []
        for component in self.get_components():
            for _ in range(quantities.get(component, 0)):
                wishlist.append(WishlistItem(len(wishlist) + 1, component))
        return wishlist

    def build_graph(self, season, development_start_date=None):
        self._graph.clear()
        self._races = DAO.get_races(season)
        self._source = None

        nodes = list(self._races)
        if development_start_date is not None:
            self._source = DevelopmentStart(development_start_date)
            nodes.insert(0, self._source)

        self._graph.add_nodes_from(nodes)
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1 = nodes[i]
                n2 = nodes[j]
                if n2.date > n1.date:
                    self._graph.add_edge(n1, n2, weight=(n2.date - n1.date).days)

    def get_races(self):
        return self._races

    def get_source(self):
        return self._source

    def get_num_nodes(self):
        return len(self._graph.nodes)

    def get_num_edges(self):
        return len(self._graph.edges)

    def get_effective_lead_time(self, component, position):
        if component.focus != constants.ATR_FOCUS:
            return component.base_lead_time_days
        return math.ceil(component.base_lead_time_days * 100 / constants.ATR_ALLOCATION_PCT[position])

    def get_affinity(self, component, race):
        if component.focus == constants.AERO_FOCUS:
            return race.aero_index / 10
        return race.chassis_index / 10

    def get_debut_quality(self, race, alpha=constants.DEFAULT_ALPHA, beta=constants.DEFAULT_BETA):
        return (1 - alpha * race.rain_prob) * (1 - beta * race.is_sprint)

    def get_assignment_value(self, component, race, alpha=constants.DEFAULT_ALPHA, beta=constants.DEFAULT_BETA):
        index = self._races.index(race)
        setup_races = self._races[index:index + 2]
        following_races = self._races[index + 2:]
        setup_benefit = self.get_debut_quality(race, alpha, beta) * sum(self.get_affinity(component, r)
                                                                         for r in setup_races)
        following_benefit = sum(self.get_affinity(component, r) for r in following_races)
        return component.base_gain_s * (setup_benefit + following_benefit)

    def load_routes(self, constructor):
        if constructor.constructor_id != self._routes_constructor_id:
            self._routes = DAO.get_routes(constructor.constructor_id)
            self._routes_constructor_id = constructor.constructor_id

    def get_shipment(self, constructor, race):
        self.load_routes(constructor)
        route = self._routes.get(race.circuit_id)
        if route is None:
            return self._estimate_shipment(constructor, race)

        mode, distance_km, travel_hours = route
        if mode == constants.ROAD_MODE:
            transit_days = constants.road_transit_days(travel_hours)
        else:
            transit_days = constants.AIR_TRANSIT_DAYS
        return Shipment(race, mode, distance_km, travel_hours, transit_days,
                        self._logistics_cost(mode, distance_km))

    def get_shipments(self, constructor):
        return {race: self.get_shipment(constructor, race) for race in self._races}

    def _estimate_shipment(self, constructor, race):
        print(f"Missing route {constructor.constructor_id} -> {race.circuit_id}: using the fallback estimate")
        air_distance_km = constants.air_distance_km(constructor.base_lat, constructor.base_lng, race.lat, race.lng)
        if air_distance_km > constants.ROAD_THRESHOLD_KM:
            return Shipment(race, constants.AIR_MODE, air_distance_km, None, constants.AIR_TRANSIT_DAYS,
                            self._logistics_cost(constants.AIR_MODE, air_distance_km), True)

        road_distance_km = constants.FALLBACK_ROAD_DETOUR_FACTOR * air_distance_km
        if road_distance_km <= constants.FALLBACK_ROAD_ONE_DAY_MAX_KM:
            transit_days = constants.FALLBACK_ROAD_TRANSIT_DAYS_SHORT
        else:
            transit_days = constants.FALLBACK_ROAD_TRANSIT_DAYS_LONG
        return Shipment(race, constants.ROAD_MODE, road_distance_km, None, transit_days,
                        self._logistics_cost(constants.ROAD_MODE, road_distance_km), True)

    def _logistics_cost(self, mode, distance_km):
        if mode == constants.ROAD_MODE:
            cost_usd = constants.ROAD_RATE_USD_PER_KM * distance_km
        else:
            cost_usd = constants.SHIPMENT_WEIGHT_KG * constants.AIR_RATE_USD_PER_KG + constants.AIR_FIXED_FEE_USD
        return cost_usd / constants.USD_PER_MLN

    def get_assignment_cost(self, component, shipment):
        return component.cost_mln + shipment.logistics_cost

    def get_roi(self, value, cost):
        return value / cost
