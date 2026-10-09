import datetime

import flet as ft

from model import constants


class Controller:
    def __init__(self, view, model):
        # the view, with the graphical elements of the UI
        self._view = view
        # the model, which implements the logic of the program and holds the data
        self._model = model

        self._quantities = {}
        self._components = {}
        self._pre_teams = {}
        self._pre_start_date = None
        self._in_teams = {}
        self._in_races = {}
        self._pre_other_costs_edited = False
        self._in_other_costs_edited = False

    def fill_catalog(self):
        for component in self._model.get_components():
            self._quantities[component] = 0
            self._components[str(component.component_id)] = component
            self._view.add_catalog_card(component)
            self._view.dd_in_component.options.append(
                ft.dropdown.Option(key=str(component.component_id), text=str(component)))

    def fill_seasons(self):
        seasons = self._model.get_seasons()
        for dd in (self._view.dd_pre_season, self._view.dd_in_season):
            dd.options = [ft.dropdown.Option(str(season)) for season in seasons]
            dd.value = str(seasons[-1])
        for slider in (self._view.slider_pre_tolerance, self._view.slider_in_tolerance):
            slider.value = constants.DEFAULT_PERFORMANCE_TOLERANCE_PCT
        self._load_pre_season()
        self._load_in_season()
        self._refresh_tolerance_labels()

    def handle_mode_change(self, e):
        self._view.set_mode(self._view.switch_mode.value)
        self._view.update_page()

    def handle_pre_season_change(self, e):
        self._load_pre_season()
        self._view.update_page()

    def handle_pre_input_change(self, e):
        self._refresh_pre_season()
        self._view.update_page()

    def handle_pre_other_costs_change(self, e):
        self._pre_other_costs_edited = True
        self._refresh_pre_season()
        self._view.update_page()

    def handle_pre_tolerance_change(self, e):
        self._refresh_tolerance_labels()
        self._view.update_page()

    def handle_pick_start_date(self, e):
        self._view.date_picker.pick_date()

    def handle_start_date_change(self, e):
        if self._view.date_picker.value is not None:
            self._pre_start_date = self._view.date_picker.value.date()
            self._refresh_start_date()
            self._view.update_page()

    def handle_add_package(self, e):
        if sum(self._quantities.values()) >= constants.MAX_WISHLIST_SIZE:
            self._view.create_alert(f"The wishlist can hold at most {constants.MAX_WISHLIST_SIZE} packages.")
            return
        self._quantities[e.control.data] += 1
        self._refresh_pre_season()
        self._view.update_page()

    def handle_remove_package(self, e):
        if self._quantities[e.control.data] > 0:
            self._quantities[e.control.data] -= 1
            self._refresh_pre_season()
            self._view.update_page()

    def handle_pre_optimize(self, e):
        season = int(self._view.dd_pre_season.value)
        first_date, last_date = self._model.get_development_window(season)
        if self._pre_start_date is None or not first_date <= self._pre_start_date <= last_date:
            self._view.create_alert(f"The development start must be between {first_date.strftime('%d %b %Y')} "
                                    f"and {last_date.strftime('%d %b %Y')}.")
            return
        if not self._view.dd_pre_team.value:
            self._view.create_alert("Select a team.")
            return
        other_costs = self._read_other_costs(self._view.txt_pre_other_costs, season)
        if other_costs is None:
            return
        package_count = sum(self._quantities.values())
        if package_count == 0:
            self._view.create_alert("Add at least one package to the wishlist.")
            return
        if package_count > constants.MAX_WISHLIST_SIZE:
            self._view.create_alert(f"The wishlist can hold at most {constants.MAX_WISHLIST_SIZE} packages.")
            return

        team = self._pre_teams[self._view.dd_pre_team.value]
        position = int(self._view.dd_pre_position.value)
        tolerance = self._view.slider_pre_tolerance.value
        wishlist = self._model.build_wishlist(self._quantities)

        self._view.set_busy(self._view.btn_pre_optimize, self._view.ring_pre, True)
        try:
            result = self._model.optimize_pre_season(season, self._pre_start_date, team, position, other_costs,
                                                     wishlist, tolerance)
            start_label = f"Development start: {self._pre_start_date.strftime('%d %b %Y')}"
            self._view.show_result(self._view.pre_results, self._model.get_races(), result,
                                   self._build_motivations(result), start_label)
        except Exception as ex:
            self._view.create_alert(f"Optimisation failed: {ex}")
        finally:
            self._view.set_busy(self._view.btn_pre_optimize, self._view.ring_pre, False)

    def handle_in_season_change(self, e):
        self._load_in_season()
        self._view.update_page()

    def handle_in_other_costs_change(self, e):
        self._in_other_costs_edited = True
        self._refresh_in_season()
        self._view.update_page()

    def handle_in_tolerance_change(self, e):
        self._refresh_tolerance_labels()
        self._view.update_page()

    def handle_in_optimize(self, e):
        season = int(self._view.dd_in_season.value)
        if not self._view.dd_in_race.value:
            self._view.create_alert("Select the current Grand Prix.")
            return
        if not self._view.dd_in_team.value:
            self._view.create_alert("Select a team.")
            return
        if not self._view.dd_in_component.value:
            self._view.create_alert("Select the urgent package.")
            return
        other_costs = self._read_other_costs(self._view.txt_in_other_costs, season)
        if other_costs is None:
            return

        current_race = self._in_races[self._view.dd_in_race.value]
        team = self._in_teams[self._view.dd_in_team.value]
        position = int(self._view.dd_in_position.value)
        component = self._components[self._view.dd_in_component.value]
        tolerance = self._view.slider_in_tolerance.value

        self._view.set_busy(self._view.btn_in_optimize, self._view.ring_in, True)
        try:
            result = self._model.optimize_in_season(current_race, team, position, other_costs, component, tolerance)
            start_label = f"Current Grand Prix: {current_race.race_name}, {current_race.date.strftime('%d %b %Y')}"
            self._view.show_result(self._view.in_results, self._model.get_races(), result,
                                   self._build_motivations(result), start_label, current_race)
        except Exception as ex:
            self._view.create_alert(f"Optimisation failed: {ex}")
        finally:
            self._view.set_busy(self._view.btn_in_optimize, self._view.ring_in, False)

    def _load_pre_season(self):
        season = int(self._view.dd_pre_season.value)
        self._pre_teams = {t.constructor_id: t for t in self._model.get_constructors(season)}
        self._view.dd_pre_team.options = [ft.dropdown.Option(key=t.constructor_id, text=t.name)
                                          for t in self._pre_teams.values()]
        self._view.dd_pre_team.value = None
        self._fill_positions(self._view.dd_pre_position, season)
        if not self._pre_other_costs_edited:
            self._view.txt_pre_other_costs.value = f"{self._model.get_default_other_costs(season):g}"

        first_date, last_date = self._model.get_development_window(season)
        self._pre_start_date = self._model.get_default_development_start(season)
        self._view.date_picker.first_date = datetime.datetime.combine(first_date, datetime.time())
        self._view.date_picker.last_date = datetime.datetime.combine(last_date, datetime.time())
        self._view.date_picker.value = datetime.datetime.combine(self._pre_start_date, datetime.time())
        self._refresh_start_date()
        self._refresh_pre_season()

    def _load_in_season(self):
        season = int(self._view.dd_in_season.value)
        self._in_teams = {t.constructor_id: t for t in self._model.get_constructors(season)}
        self._view.dd_in_team.options = [ft.dropdown.Option(key=t.constructor_id, text=t.name)
                                         for t in self._in_teams.values()]
        self._view.dd_in_team.value = None
        self._in_races = {str(r.race_id): r for r in self._model.get_season_races(season)}
        self._view.dd_in_race.options = [
            ft.dropdown.Option(key=key, text=f"R{r.round} - {r.race_name} ({r.date.strftime('%d %b')})")
            for key, r in self._in_races.items()]
        self._view.dd_in_race.value = None
        self._fill_positions(self._view.dd_in_position, season)
        if not self._in_other_costs_edited:
            self._view.txt_in_other_costs.value = f"{self._model.get_default_other_costs(season):g}"
        self._refresh_in_season()

    def _fill_positions(self, dropdown, season):
        positions = self._model.get_positions(season)
        dropdown.options = [ft.dropdown.Option(str(p)) for p in positions]
        dropdown.value = str(constants.DEFAULT_POSITION)

    def _refresh_start_date(self):
        self._view.btn_pre_start_date.text = f"Development start: {self._pre_start_date.strftime('%d %b %Y')}"

    def _refresh_tolerance_labels(self):
        self._view.txt_pre_tolerance.value = f"Performance tolerance: {self._view.slider_pre_tolerance.value:.1f}%"
        self._view.txt_in_tolerance.value = f"Performance tolerance: {self._view.slider_in_tolerance.value:.1f}%"

    def _refresh_pre_season(self):
        season = int(self._view.dd_pre_season.value)
        position = int(self._view.dd_pre_position.value)
        budget = self._refresh_budget(self._view.txt_pre_other_costs, self._view.txt_pre_budget, season)

        for component, quantity in self._quantities.items():
            self._view.catalog_counts[component].value = str(quantity)
            lead_time = self._model.get_effective_lead_time(component, position)
            text = f"Lead time {lead_time} d"
            if lead_time != component.base_lead_time_days:
                text += f" (base {component.base_lead_time_days})"
            self._view.catalog_lead_times[component].value = text

        package_count = sum(self._quantities.values())
        total_cost = sum(c.cost_mln * q for c, q in self._quantities.items())
        total_gain = sum(c.base_gain_s * q for c, q in self._quantities.items())
        self._view.txt_wishlist_count.value = f"Packages: {package_count} / {constants.MAX_WISHLIST_SIZE}"
        self._view.txt_wishlist_gain.value = f"Nominal gain: {total_gain:.2f} s/lap"
        if budget is None or budget <= 0:
            self._view.txt_wishlist_cost.value = f"Production cost: {total_cost:.2f} M$"
            self._view.pb_wishlist_budget.value = 0
            self._view.txt_wishlist_hint.value = ""
            return
        self._view.txt_wishlist_cost.value = f"Production cost: {total_cost:.2f} M$ of {budget:.2f} M$"
        self._view.pb_wishlist_budget.value = min(1, total_cost / budget)
        over_budget = total_cost > budget + constants.EPSILON
        self._view.pb_wishlist_budget.color = ft.colors.RED_600 if over_budget else ft.colors.GREEN_600
        self._view.txt_wishlist_hint.value = ("Over budget: the optimiser will choose the best subset."
                                              if over_budget else "")

    def _refresh_in_season(self):
        season = int(self._view.dd_in_season.value)
        self._refresh_budget(self._view.txt_in_other_costs, self._view.txt_in_budget, season)

    def _refresh_budget(self, text_field, label, season):
        other_costs = self._parse_number(text_field.value)
        cost_cap = self._model.get_cost_cap(season)
        if other_costs is None or other_costs < 0:
            label.value = f"Cost cap {cost_cap:.1f} M$ - enter a valid amount"
            label.color = ft.colors.RED_700
            return None
        budget = self._model.get_available_budget(season, other_costs)
        label.value = f"Available budget B = {cost_cap:.1f} - {other_costs:g} = {budget:.2f} M$"
        label.color = ft.colors.RED_700 if budget <= 0 else ft.colors.GREEN_800
        return budget

    def _read_other_costs(self, text_field, season):
        other_costs = self._parse_number(text_field.value)
        if other_costs is None or other_costs < 0:
            self._view.create_alert("Other costs must be a number greater than or equal to 0.")
            return None
        if self._model.get_available_budget(season, other_costs) <= 0:
            self._view.create_alert("The available budget must be greater than 0: reduce the other costs.")
            return None
        return other_costs

    def _parse_number(self, text):
        try:
            return float(str(text).replace(",", "."))
        except (ValueError, TypeError):
            return None

    def _build_motivations(self, result):
        motivations = {}
        for item in result.included_items:
            race = item.debut_race
            affinity = self._model.get_affinity(item.component, race) * 10
            weekend = "sprint weekend" if race.is_sprint else "standard weekend"
            motivations[item.item_id] = (
                f"{item.component.focus} affinity {affinity:g}/10 at {race.circuit_name}; {weekend}, "
                f"rain probability {race.rain_prob * 100:.0f}% (debut quality "
                f"{self._model.get_debut_quality(race):.2f}); margin {item.margin_days} days; "
                f"benefit on {self._model.get_benefit_race_count(race)} races.")
        return motivations
