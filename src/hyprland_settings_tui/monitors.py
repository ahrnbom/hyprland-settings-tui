from hyprland_monitors import MonitorState
from hyprland_state import HyprlandState
from textual.containers import Grid, HorizontalGroup, VerticalScroll
from textual.widgets import Input, Rule, Select, Static


class MonitorsManager(VerticalScroll):
    DEFAULT_CSS = """
        Grid {
            layout: grid;
            grid-size: 2 3;
            max-height: 10;
        }

        .wide {
            column-span: 2;
        }

        Static {
            margin: 0 0 0 0;
            text-align: center;
        }
    """

    def __init__(self, state: HyprlandState):
        self.state = state
        super().__init__()

        self.monitors = self.state.monitors.get_all_cached()
        self.widget = self

        self.curr_modes = {
            m.name: m.mode or m.available_modes[0] for m in self.monitors
        }
        self.curr_scales = {m.name: m.scale for m in self.monitors}

    def compose(self):
        for mon in self.monitors:
            yield self._make_monitor_control(mon)
            yield Rule()

    def _make_monitor_control(self, mon: MonitorState):
        return Grid(
            Static(f"{mon.name}: {mon.make}", classes="wide"),
            Static("resolution @ frame rate"),
            Static("scaling factor"),
            Select.from_values(
                mon.available_modes,
                prompt="Monitor mode",
                allow_blank=False,
                value=mon.mode or mon.available_modes[0],
                id=f"MODE___{mon.name}",
                classes="halfwidth",
            ),
            Input(
                f"{mon.scale:.4f}",
                type="number",
                classes="halfwidth",
                id=f"SCALE___{mon.name}",
            ),
        )

    def on_select_changed(self, event: Select.Changed):
        event.stop()
        _, _, mon_name = event.select.id.partition("___")
        curr_mode = self.curr_modes.get(mon_name)
        if curr_mode == event.select.value:
            return

        self.notify(f"Handled: {mon_name} {event.select.value}")

    def on_input_submitted(self, event: Input.Changed):
        event.stop()
        _, _, mon_name = event.input.id.partition("___")

        curr_scale = self.curr_scales.get(mon_name, 1.0)
        try:
            new_scale = float(event.input.value)
        except ValueError:
            return

        if abs(curr_scale - new_scale) < 1 / 12:
            return
        self.notify(mon_name + f" {event.input.value}")
