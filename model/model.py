import networkx as nx

from database.DAO import DAO
from model import constants
from model.development_start import DevelopmentStart
from model.wishlist_item import WishlistItem


class Model:
    def __init__(self):
        self._graph = nx.DiGraph()
        self._races = []
        self._source = None
        self._components = []

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
