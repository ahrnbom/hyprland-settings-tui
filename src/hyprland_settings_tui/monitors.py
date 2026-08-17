from typing import List

from hyprland_monitors import MonitorState
from hyprland_state import HyprlandState
from textual.containers import VerticalGroup, VerticalScroll
from textual.widget import Widget
from textual.widgets import Select, Static


class MonitorsManager:
    def __init__(self, state: HyprlandState):
        self.state = state

        monitor_controls: List[Widget] = []
        for mon in self.state.monitors.get_all_cached():
            monitor_controls.append(self.make_monitor_control(mon))

        self.widget = VerticalScroll(*monitor_controls)

    def make_monitor_control(self, mon: MonitorState):
        content: List[Widget] = []
        content.append(Static(f"{mon.name}: {mon.make}"))

        content.append(
            Select.from_values(
                mon.available_modes,
                prompt="Monitor mode",
                allow_blank=False,
                value=mon.available_modes[0], # TODO - this should probably be mon.mode
            )
        )

        return VerticalGroup(*content)
