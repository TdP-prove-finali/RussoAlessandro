import flet as ft

from model import constants

FOCUS_COLORS = {
    constants.AERO_FOCUS: ft.colors.BLUE_700,
    constants.CHASSIS_FOCUS: ft.colors.DEEP_ORANGE_700,
}
FOCUS_LIGHT_COLORS = {
    constants.AERO_FOCUS: ft.colors.BLUE_50,
    constants.CHASSIS_FOCUS: ft.colors.DEEP_ORANGE_50,
}


class View(ft.UserControl):
    def __init__(self, page: ft.Page):
        super().__init__()
        self._page = page
        self._page.title = "Applicazione per l'ottimizzazione logistica ed economica degli sviluppi vettura in Formula 1"
        self._page.horizontal_alignment = 'CENTER'
        self._page.theme_mode = ft.ThemeMode.LIGHT
        self._page.bgcolor = ft.colors.GREY_100
        self._page.padding = 16
        self._page.window_maximized = True
        self._controller = None

        self._title = None
        self.switch_mode = None
        self.txt_mode_pre = None
        self.txt_mode_in = None
        self.panel_pre = None
        self.panel_in = None

        self.dd_pre_season = None
        self.btn_pre_start_date = None
        self.date_picker = None
        self.dd_pre_team = None
        self.dd_pre_position = None
        self.txt_pre_other_costs = None
        self.txt_pre_budget = None
        self.slider_pre_tolerance = None
        self.txt_pre_tolerance = None
        self.catalog = None
        self.catalog_rows = {}
        self.catalog_counts = {}
        self.catalog_lead_times = {}
        self.txt_wishlist_count = None
        self.txt_wishlist_cost = None
        self.pb_wishlist_budget = None
        self.txt_wishlist_gain = None
        self.txt_wishlist_hint = None
        self.btn_pre_optimize = None
        self.ring_pre = None
        self.pre_results = None
        self.scroll_pre = None

        self.dd_in_season = None
        self.dd_in_race = None
        self.dd_in_team = None
        self.dd_in_position = None
        self.txt_in_other_costs = None
        self.txt_in_budget = None
        self.dd_in_component = None
        self.slider_in_tolerance = None
        self.txt_in_tolerance = None
        self.btn_in_optimize = None
        self.ring_in = None
        self.in_results = None
        self.scroll_in = None

    def load_interface(self):
        self._title = ft.Row([ft.Icon(ft.icons.SPORTS_MOTORSPORTS, color=ft.colors.RED_700, size=32),
                              ft.Text("F1 Development Planner", size=26, weight=ft.FontWeight.BOLD),
                              ft.Text("Logistic and economic optimisation of car upgrades",
                                      size=14, color=ft.colors.GREY_700)],
                             vertical_alignment=ft.CrossAxisAlignment.CENTER)
        self._page.controls.append(self._title)

        self.date_picker = ft.DatePicker(on_change=self._controller.handle_start_date_change,
                                         help_text="Development start date")
        self._page.overlay.append(self.date_picker)

        self.txt_mode_pre = ft.Text("Pre-Season planning", size=16)
        self.txt_mode_in = ft.Text("In-Season recalculation", size=16)
        self.switch_mode = ft.Switch(value=False, active_color=ft.colors.RED_700,
                                     active_track_color=ft.colors.RED_100,
                                     inactive_thumb_color=ft.colors.RED_700,
                                     inactive_track_color=ft.colors.RED_100,
                                     on_change=self._controller.handle_mode_change)
        self._page.controls.append(ft.Row([self.txt_mode_pre, self.switch_mode, self.txt_mode_in],
                                          alignment=ft.MainAxisAlignment.CENTER,
                                          vertical_alignment=ft.CrossAxisAlignment.CENTER))

        self.panel_pre = self._build_pre_season_panel()
        self.panel_in = self._build_in_season_panel()
        self._page.controls.append(self.panel_pre)
        self._page.controls.append(self.panel_in)
        self.set_mode(False)

        self._controller.fill_catalog()
        self._controller.fill_seasons()
        self._page.update()

    def _build_pre_season_panel(self):
        self.dd_pre_season = ft.Dropdown(label="Season", width=140,
                                         on_change=self._controller.handle_pre_season_change)
        self.btn_pre_start_date = ft.OutlinedButton(text="Development start", icon=ft.icons.CALENDAR_MONTH,
                                                    on_click=self._controller.handle_pick_start_date)
        self.dd_pre_team = ft.Dropdown(label="Team", hint_text="Select a team", width=220)
        self.dd_pre_position = ft.Dropdown(label="Target position", width=150,
                                           on_change=self._controller.handle_pre_input_change)
        self.txt_pre_other_costs = ft.TextField(label="Other costs (M$)", width=170,
                                                on_change=self._controller.handle_pre_other_costs_change)
        self.txt_pre_budget = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.slider_pre_tolerance = ft.Slider(min=0, max=constants.MAX_PERFORMANCE_TOLERANCE_PCT, divisions=20,
                                              width=260, on_change=self._controller.handle_pre_tolerance_change)
        self.txt_pre_tolerance = ft.Text("")

        scenario = self._section("Scenario", ft.Column([
            ft.Row([self.dd_pre_season, self.dd_pre_team, self.dd_pre_position, self.btn_pre_start_date],
                   wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([self.txt_pre_other_costs, self.txt_pre_budget, ft.Container(width=24),
                    self.txt_pre_tolerance, self.slider_pre_tolerance], wrap=True,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER)]))

        self.catalog_rows = {constants.AERO_FOCUS: ft.Row(spacing=10),
                             constants.CHASSIS_FOCUS: ft.Row(spacing=10)}
        self.catalog = ft.Column(list(self.catalog_rows.values()), spacing=10)
        self.txt_wishlist_count = ft.Text("", weight=ft.FontWeight.BOLD)
        self.txt_wishlist_cost = ft.Text("")
        self.pb_wishlist_budget = ft.ProgressBar(value=0, width=260, bar_height=8)
        self.txt_wishlist_gain = ft.Text("")
        self.txt_wishlist_hint = ft.Text("", size=12, color=ft.colors.GREY_700, width=260)
        summary = ft.Container(ft.Column([ft.Text("Wishlist summary", weight=ft.FontWeight.BOLD),
                                          self.txt_wishlist_count, self.txt_wishlist_cost,
                                          self.pb_wishlist_budget, self.txt_wishlist_gain,
                                          self.txt_wishlist_hint], spacing=6),
                               width=290, padding=12, border_radius=8, bgcolor=ft.colors.GREY_100)
        wishlist = self._section("Wishlist", ft.Row([ft.Container(self.catalog, expand=True), summary],
                                                    vertical_alignment=ft.CrossAxisAlignment.START))

        self.btn_pre_optimize = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.PLAY_ARROW, size=26),
                            ft.Text("Optimise plan", size=18, weight=ft.FontWeight.BOLD)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            width=300, height=54, on_click=self._controller.handle_pre_optimize)
        self.ring_pre = ft.ProgressRing(width=24, height=24, stroke_width=3, visible=False)
        self.pre_results = ft.Column(spacing=12, key="pre_results")
        self.scroll_pre = ft.Column([scenario, wishlist, self.pre_results],
                                    scroll=ft.ScrollMode.AUTO, expand=True, spacing=12,
                                    horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        run_row = ft.Row([ft.Container(width=32), self.btn_pre_optimize, ft.Container(self.ring_pre, width=32)],
                         alignment=ft.MainAxisAlignment.CENTER,
                         vertical_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.Column([self.scroll_pre, run_row],
                         expand=True, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def _build_in_season_panel(self):
        self.dd_in_season = ft.Dropdown(label="Season", width=140,
                                        on_change=self._controller.handle_in_season_change)
        self.dd_in_race = ft.Dropdown(label="Current Grand Prix", hint_text="Select the current race", width=360)
        self.dd_in_team = ft.Dropdown(label="Team", hint_text="Select a team", width=220)
        self.dd_in_position = ft.Dropdown(label="Current position", width=150)
        self.txt_in_other_costs = ft.TextField(label="Other costs (M$)", width=170,
                                               on_change=self._controller.handle_in_other_costs_change)
        self.txt_in_budget = ft.Text("", size=16, weight=ft.FontWeight.BOLD)
        self.dd_in_component = ft.Dropdown(label="Urgent package", hint_text="Select a package", width=220)
        self.slider_in_tolerance = ft.Slider(min=0, max=constants.MAX_PERFORMANCE_TOLERANCE_PCT, divisions=20,
                                             width=260, on_change=self._controller.handle_in_tolerance_change)
        self.txt_in_tolerance = ft.Text("")

        scenario = self._section("Scenario", ft.Column([
            ft.Row([self.dd_in_season, self.dd_in_race, self.dd_in_team, self.dd_in_position],
                   wrap=True, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Row([self.dd_in_component, self.txt_in_other_costs, self.txt_in_budget, ft.Container(width=24),
                    self.txt_in_tolerance, self.slider_in_tolerance], wrap=True,
                   vertical_alignment=ft.CrossAxisAlignment.CENTER)]))

        self.btn_in_optimize = ft.ElevatedButton(
            content=ft.Row([ft.Icon(ft.icons.PLAY_ARROW, size=26),
                            ft.Text("Recalculate debut", size=18, weight=ft.FontWeight.BOLD)],
                           alignment=ft.MainAxisAlignment.CENTER, spacing=8),
            width=300, height=54, on_click=self._controller.handle_in_optimize)
        self.ring_in = ft.ProgressRing(width=24, height=24, stroke_width=3, visible=False)
        self.in_results = ft.Column(spacing=12, key="in_results")
        self.scroll_in = ft.Column([scenario, self.in_results],
                                   scroll=ft.ScrollMode.AUTO, expand=True, spacing=12,
                                   horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

        run_row = ft.Row([ft.Container(width=32), self.btn_in_optimize, ft.Container(self.ring_in, width=32)],
                         alignment=ft.MainAxisAlignment.CENTER,
                         vertical_alignment=ft.CrossAxisAlignment.CENTER)
        return ft.Column([self.scroll_in, run_row],
                         expand=True, spacing=10, horizontal_alignment=ft.CrossAxisAlignment.STRETCH)

    def set_mode(self, in_season):
        self.panel_pre.visible = not in_season
        self.panel_in.visible = in_season
        for text, active in ((self.txt_mode_pre, not in_season), (self.txt_mode_in, in_season)):
            text.weight = ft.FontWeight.BOLD if active else ft.FontWeight.NORMAL
            text.color = ft.colors.RED_700 if active else ft.colors.GREY_600

    def _section(self, title, content):
        return ft.Container(ft.Column([ft.Text(title, size=16, weight=ft.FontWeight.BOLD), content], spacing=10),
                            padding=16, border_radius=10, bgcolor=ft.colors.WHITE)

    def add_catalog_card(self, component):
        color = FOCUS_COLORS[component.focus]
        count = ft.Text("0", size=18, weight=ft.FontWeight.BOLD, width=28, text_align=ft.TextAlign.CENTER)
        lead_time = ft.Text("", size=12)
        self.catalog_counts[component] = count
        self.catalog_lead_times[component] = lead_time
        card = ft.Container(
            ft.Column([
                ft.Text(str(component), weight=ft.FontWeight.BOLD, color=color),
                ft.Text(f"Cost {component.cost_mln:.2f} M$", size=12),
                ft.Text(f"Gain {component.base_gain_s:.2f} s/lap", size=12),
                lead_time,
                ft.Row([ft.IconButton(icon=ft.icons.REMOVE_CIRCLE_OUTLINE, icon_color=color, data=component,
                                      tooltip="Remove one", on_click=self._controller.handle_remove_package),
                        count,
                        ft.IconButton(icon=ft.icons.ADD_CIRCLE, icon_color=color, data=component,
                                      tooltip="Add one", on_click=self._controller.handle_add_package)],
                       alignment=ft.MainAxisAlignment.CENTER, spacing=0)],
                spacing=4),
            width=230, height=156, padding=10, border_radius=8, bgcolor=FOCUS_LIGHT_COLORS[component.focus],
            border=ft.border.only(left=ft.border.BorderSide(5, color)))
        self.catalog_rows[component.focus].controls.append(card)

    def set_busy(self, button, ring, busy):
        button.disabled = busy
        ring.visible = busy
        self._page.update()

    def show_result(self, target, races, result, motivations, start_label, current_race=None):
        target.controls.clear()

        debuts = {item.debut_race: item for item in result.included_items}
        cells = [self._timeline_cell(race, debuts.get(race), current_race) for race in races]
        legend = ft.Row([self._legend_dot(FOCUS_COLORS[constants.AERO_FOCUS], "Aero debut"),
                         self._legend_dot(FOCUS_COLORS[constants.CHASSIS_FOCUS], "Chassis debut"),
                         ft.Text(start_label, size=12, color=ft.colors.GREY_700)], spacing=16)
        target.controls.append(self._section("Season timeline", ft.Column([
            legend, ft.Row(cells, wrap=True, spacing=6, run_spacing=6)], spacing=8)))

        if result.included_items:
            cards = [self._item_card(item, motivations[item.item_id]) for item in result.included_items]
            target.controls.append(self._section("Debut plan", ft.Column(cards, spacing=8)))
        if result.excluded_items:
            rows = [ft.Row([ft.Icon(ft.icons.BLOCK, size=16, color=ft.colors.GREY_600),
                            ft.Text(str(item), weight=ft.FontWeight.BOLD,
                                    color=FOCUS_COLORS[item.component.focus]),
                            ft.Text(item.exclusion_label)], spacing=8)
                    for item in result.excluded_items]
            target.controls.append(self._section("Not included", ft.Column(rows, spacing=4)))

        target.controls.append(self._section("Summary", self._summary(result)))
        self._page.update()
        scroll = self.scroll_pre if target is self.pre_results else self.scroll_in
        scroll.scroll_to(key=target.key, duration=400)

    def _timeline_cell(self, race, item, current_race):
        past = current_race is not None and race.date < current_race.date
        is_current = current_race is not None and race == current_race
        text_color = ft.colors.BLACK
        bgcolor = ft.colors.GREY_200
        if past:
            bgcolor = ft.colors.GREY_100
            text_color = ft.colors.GREY_500
        if item is not None:
            bgcolor = FOCUS_COLORS[item.component.focus]
            text_color = ft.colors.WHITE
        lines = [ft.Text(f"R{race.round}", size=10, color=text_color),
                 ft.Text(race.race_name.replace("Grand Prix", "GP"), size=11, weight=ft.FontWeight.BOLD,
                         color=text_color, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
                 ft.Text(race.date.strftime("%d %b"), size=10, color=text_color)]
        if race.is_sprint:
            lines.append(ft.Text("SPRINT", size=9, color=text_color))
        if is_current:
            lines.append(ft.Text("NOW", size=10, weight=ft.FontWeight.BOLD, color=ft.colors.RED_700))
        if item is not None:
            lines.append(ft.Text(str(item), size=11, weight=ft.FontWeight.BOLD, color=text_color))
        tooltip = (f"{race.circuit_name} ({race.locality}, {race.country})\n"
                   f"Aero index {race.aero_index:g} - Chassis index {race.chassis_index:g} - "
                   f"Power index {race.power_index:g}\n"
                   f"Rain probability {race.rain_prob * 100:.0f}% - "
                   f"{'Sprint weekend' if race.is_sprint else 'Standard weekend'}")
        border = ft.border.all(2, ft.colors.RED_700) if is_current else None
        return ft.Container(ft.Column(lines, spacing=2), width=100, height=118, padding=6, border_radius=8,
                            bgcolor=bgcolor, border=border, tooltip=tooltip)

    def _legend_dot(self, color, label):
        return ft.Row([ft.Container(width=12, height=12, border_radius=6, bgcolor=color),
                       ft.Text(label, size=12)], spacing=4)

    def _item_card(self, item, motivation):
        color = FOCUS_COLORS[item.component.focus]
        race = item.debut_race
        chips = [self._chip(f"Margin {item.margin_days} d"),
                 self._chip(f"Gain V {item.value:.3f}"),
                 self._chip(f"Production {item.production_cost:.2f} M$"),
                 self._chip(f"Logistics {item.logistics_cost:.4f} M$ ({item.transport_mode}, "
                            f"{item.transit_days} d)"),
                 self._chip(f"ROI {item.get_roi():.2f}")]
        return ft.Container(
            ft.Column([ft.Row([ft.Text(str(item), weight=ft.FontWeight.BOLD, color=color, size=15),
                               ft.Icon(ft.icons.ARROW_FORWARD, size=16),
                               ft.Text(f"{race.race_name}, {race.date.strftime('%d %b %Y')}",
                                       weight=ft.FontWeight.BOLD)], spacing=8),
                       ft.Row(chips, wrap=True, spacing=6, run_spacing=6),
                       ft.Text(motivation, size=12, italic=True, color=ft.colors.GREY_800)], spacing=6),
            padding=10, border_radius=8, bgcolor=FOCUS_LIGHT_COLORS[item.component.focus],
            border=ft.border.only(left=ft.border.BorderSide(5, color)))

    def _chip(self, text):
        return ft.Container(ft.Text(text, size=12), padding=ft.padding.symmetric(horizontal=8, vertical=3),
                            border_radius=12, bgcolor=ft.colors.WHITE)

    def _summary(self, result):
        if result.performance_price is None:
            return ft.Text("No package can be placed: phase 2 was not run.")
        savings = result.get_savings()
        tiles = [self._stat("Committed budget", f"{result.get_committed_budget():.2f} M$",
                            "production + logistics"),
                 self._stat("Remaining budget", f"{result.get_remaining_budget():.2f} M$",
                            f"of {result.available_budget:.2f} M$ available"),
                 self._stat("Expected gain (V)", f"{result.total_value:.3f}", "s/lap x races"),
                 self._stat("V max (phase 1)", f"{result.max_value:.3f}",
                            f"phase 1 cost {result.phase1_cost:.2f} M$"),
                 self._stat("Performance price", f"{result.performance_price:.3f}", "M$ per unit of V"),
                 self._stat("Savings vs phase 1", f"{-savings:+.2f} M$" if savings > constants.EPSILON
                            else "0.00 M$",
                            f"giving up {result.get_performance_loss_pct():.2f}% of performance"),
                 self._stat("Overall ROI", f"{result.get_roi():.2f}", "V per M$"),
                 self._stat("Computation time", f"{result.total_seconds:.2f} s",
                            f"phase 1 {result.phase1_seconds:.2f} s - phase 2 {result.phase2_seconds:.2f} s")]
        return ft.Row(tiles, wrap=True, spacing=10, run_spacing=10)

    def _stat(self, label, value, note):
        return ft.Container(ft.Column([ft.Text(label, size=12, color=ft.colors.GREY_700),
                                       ft.Text(value, size=20, weight=ft.FontWeight.BOLD),
                                       ft.Text(note, size=11, color=ft.colors.GREY_600)], spacing=2),
                            width=210, padding=10, border_radius=8, bgcolor=ft.colors.GREY_100)

    @property
    def controller(self):
        return self._controller

    @controller.setter
    def controller(self, controller):
        self._controller = controller

    def set_controller(self, controller):
        self._controller = controller

    def create_alert(self, message):
        dlg = ft.AlertDialog(title=ft.Text(message))
        self._page.dialog = dlg
        dlg.open = True
        self._page.update()

    def update_page(self):
        self._page.update()
