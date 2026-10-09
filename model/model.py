import datetime
import math
import time

import networkx as nx

from database.DAO import DAO
from model import constants
from model.development_start import DevelopmentStart
from model.optimization_result import OptimizationResult
from model.shipment import Shipment
from model.wishlist_item import WishlistItem


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._races = []
        self._source = None
        self._components = []
        self._seasons = []
        self._season_races = {}
        self._season_constructors = {}
        self._routes = {}
        self._routes_constructor_id = None

        self._types = []
        self._lead_times = []
        self._shipments = {}
        self._values = []
        self._costs = []
        self._reachable = {}
        self._max_reachable_value = {}
        self._min_reachable_cost = {}
        self._moves = {}
        self._phase = 1
        self._threshold = 0.0
        self._price = 0.0
        self._best_path = []
        self._best_value = 0.0
        self._best_cost = 0.0
        self._best_net = -math.inf

    def get_seasons(self):
        if not self._seasons:
            self._seasons = DAO.get_seasons()
        return self._seasons

    def get_season_races(self, season):
        if season not in self._season_races:
            self._season_races[season] = DAO.get_races(season)
        return self._season_races[season]

    def get_constructors(self, season):
        if season not in self._season_constructors:
            self._season_constructors[season] = DAO.get_constructors(season)
        return self._season_constructors[season]

    def get_positions(self, season):
        team_count = len(self.get_constructors(season))
        return list(range(1, team_count + 1))

    def get_development_window(self, season):
        first_date = datetime.date(season - 1, constants.DEVELOPMENT_WINDOW_START_MONTH,
                                   constants.DEVELOPMENT_WINDOW_START_DAY)
        last_date = self.get_season_races(season)[-1].date
        return first_date, last_date

    def get_default_development_start(self, season):
        return datetime.date(season, constants.DEFAULT_DEVELOPMENT_START_MONTH,
                             constants.DEFAULT_DEVELOPMENT_START_DAY)

    def get_cost_cap(self, season):
        race_count = len(self.get_season_races(season))
        return constants.cost_cap(season, race_count)

    def get_available_budget(self, season, other_costs):
        return self.get_cost_cap(season) - other_costs

    def get_default_other_costs(self, season):
        return round(self.get_cost_cap(season) - constants.DEFAULT_BUDGET_MLN, 2)

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
        self._races = self.get_season_races(season)
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

    def get_benefit_race_count(self, race):
        return len(self._races) - self._races.index(race)

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

    def optimize_pre_season(self, season, development_start_date, constructor, position, other_costs, wishlist,
                            tolerance_pct=constants.DEFAULT_PERFORMANCE_TOLERANCE_PCT,
                            alpha=constants.DEFAULT_ALPHA, beta=constants.DEFAULT_BETA):
        self.build_graph(season, development_start_date)
        available_budget = self.get_available_budget(season, other_costs)
        return self._optimize(self._source, constructor, position, available_budget, wishlist,
                              tolerance_pct, alpha, beta)

    def optimize_in_season(self, current_race, constructor, position, other_costs, component,
                           tolerance_pct=constants.DEFAULT_PERFORMANCE_TOLERANCE_PCT,
                           alpha=constants.DEFAULT_ALPHA, beta=constants.DEFAULT_BETA):
        self.build_graph(current_race.season)
        start_node = self._races[self._races.index(current_race)]
        available_budget = self.get_available_budget(current_race.season, other_costs)
        wishlist = self.build_wishlist({component: 1})
        return self._optimize(start_node, constructor, position, available_budget, wishlist,
                              tolerance_pct, alpha, beta)

    def _optimize(self, start_node, constructor, position, available_budget, wishlist, tolerance_pct, alpha, beta):
        start_time = time.perf_counter()
        for item in wishlist:
            item.reset_results()
        self._prepare_tables(constructor, position, wishlist, alpha, beta)

        counts = [0] * len(self._types)
        for item in wishlist:
            counts[self._types.index(item.component)] += 1
        min_costs = self._min_reachable_cost[start_node]
        search_counts = [counts[t] if min_costs[t] is not None and min_costs[t] <= available_budget + constants.EPSILON
                         else 0 for t in range(len(self._types))]

        phase1_start = time.perf_counter()
        self._phase = 1
        self._best_path, self._best_value, self._best_cost = [], 0.0, 0.0
        self._recursion(start_node, search_counts, available_budget, 0.0, 0.0, [])
        phase1_seconds = time.perf_counter() - phase1_start
        max_value, phase1_cost = self._best_value, self._best_cost

        phase2_seconds = 0.0
        performance_price = None
        if max_value > constants.EPSILON:
            phase2_start = time.perf_counter()
            performance_price = phase1_cost / max_value
            self._phase = 2
            self._price = performance_price
            self._threshold = (1 - tolerance_pct / 100) * max_value
            self._best_path, self._best_value, self._best_cost, self._best_net = [], 0.0, 0.0, -math.inf
            self._recursion(start_node, search_counts, available_budget, 0.0, 0.0, [])
            phase2_seconds = time.perf_counter() - phase2_start

        result = OptimizationResult(max_value=max_value, phase1_cost=phase1_cost,
                                    performance_price=performance_price, available_budget=available_budget,
                                    phase1_seconds=phase1_seconds, phase2_seconds=phase2_seconds)
        self._fill_results(start_node, wishlist, self._best_path, min_costs, available_budget, result)
        result.total_seconds = time.perf_counter() - start_time
        return result

    def _prepare_tables(self, constructor, position, wishlist, alpha, beta):
        self._types = []
        for item in wishlist:
            if item.component not in self._types:
                self._types.append(item.component)
        self._lead_times = [self.get_effective_lead_time(c, position) for c in self._types]
        self._shipments = self.get_shipments(constructor)
        self._values = [{r: self.get_assignment_value(c, r, alpha, beta) for r in self._races} for c in self._types]
        self._costs = [{r: self.get_assignment_cost(c, self._shipments[r]) for r in self._races} for c in self._types]

        self._reachable = {}
        self._max_reachable_value = {}
        self._min_reachable_cost = {}
        self._moves = {}
        for node in self._graph.nodes:
            reachable = [[r for r in self._graph.successors(node)
                          if self._graph[node][r]["weight"] >= self._lead_times[t] + self._shipments[r].transit_days]
                         for t in range(len(self._types))]
            self._reachable[node] = reachable
            self._max_reachable_value[node] = [max((self._values[t][r] for r in reachable[t]), default=None)
                                               for t in range(len(self._types))]
            self._min_reachable_cost[node] = [min((self._costs[t][r] for r in reachable[t]), default=None)
                                              for t in range(len(self._types))]
            moves = [(t, r) for t in range(len(self._types)) for r in reachable[t]]
            self._moves[node] = sorted(moves, key=lambda move: -self._values[move[0]][move[1]])

    def _recursion(self, node, counts, remaining_budget, value, cost, path):
        self._update_best(path, value, cost)

        remaining_types = [t for t in range(len(counts)) if counts[t] > 0]
        if not remaining_types:
            return

        if all(not self._reachable[node][t] for t in remaining_types):
            return

        costs = [self._min_reachable_cost[node][t] for t in remaining_types
                 if self._min_reachable_cost[node][t] is not None]
        if min(costs) > remaining_budget + constants.EPSILON:
            return

        bound = sum(counts[t] * self._max_reachable_value[node][t] for t in remaining_types
                    if self._max_reachable_value[node][t] is not None)
        if self._phase == 1:
            if value + bound < self._best_value - constants.EPSILON:
                return
        else:
            if value + bound < self._threshold - constants.EPSILON:
                return
            if self._price * (value + bound) - cost < self._best_net - constants.EPSILON:
                return

        for t, race in self._moves[node]:
            race_cost = self._costs[t][race]
            if counts[t] > 0 and race_cost <= remaining_budget + constants.EPSILON:
                counts[t] -= 1
                path.append((t, race))
                self._recursion(race, counts, remaining_budget - race_cost, value + self._values[t][race],
                                cost + race_cost, path)
                path.pop()
                counts[t] += 1

    def _update_best(self, path, value, cost):
        if self._phase == 1:
            better = value > self._best_value + constants.EPSILON
            tie = abs(value - self._best_value) <= constants.EPSILON and cost < self._best_cost - constants.EPSILON
            if better or tie:
                self._best_path, self._best_value, self._best_cost = list(path), value, cost
        else:
            if value < self._threshold - constants.EPSILON:
                return
            net = self._price * value - cost
            better = net > self._best_net + constants.EPSILON
            tie = abs(net - self._best_net) <= constants.EPSILON and value > self._best_value + constants.EPSILON
            if better or tie:
                self._best_path, self._best_value, self._best_cost, self._best_net = list(path), value, cost, net

    def _fill_results(self, start_node, wishlist, path, min_costs, available_budget, result):
        free_items = list(wishlist)
        previous = start_node
        for t, race in path:
            item = next(i for i in free_items if i.component == self._types[t])
            free_items.remove(item)
            shipment = self._shipments[race]
            item.debut_race = race
            item.margin_days = self._graph[previous][race]["weight"] - self._lead_times[t] - shipment.transit_days
            item.value = self._values[t][race]
            item.production_cost = item.component.cost_mln
            item.logistics_cost = shipment.logistics_cost
            item.transport_mode = shipment.mode
            item.transit_days = shipment.transit_days
            result.included_items.append(item)
            result.total_value += item.value
            result.total_cost += item.get_cost()
            previous = race

        free_budget = available_budget - result.total_cost
        for item in free_items:
            min_cost = min_costs[self._types.index(item.component)]
            if min_cost is None:
                item.exclusion_label = constants.NOT_PLACEABLE_LABEL
            elif min_cost > available_budget + constants.EPSILON:
                item.exclusion_label = constants.OVER_BUDGET_LABEL
            elif min_cost > free_budget + constants.EPSILON:
                item.exclusion_label = constants.EXCLUDED_FOR_BUDGET_LABEL
            else:
                item.exclusion_label = constants.EXCLUDED_FOR_OTHERS_LABEL
            result.excluded_items.append(item)
