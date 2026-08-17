from hyprland_monitors import MonitorState
from hyprland_state import HyprlandState
from textual.containers import VerticalGroup, VerticalScroll
from textual.widgets import Rule, Select, Static


class MonitorsManager(VerticalScroll):
    def __init__(self, state: HyprlandState):
        self.state = state
        self._ready = False

        controls = [
            self._make_monitor_control(mon)
            for mon in self.state.monitors.get_all_cached()
        ]

        super().__init__(*controls)
        self.widget = self

    def _make_monitor_control(self, mon: MonitorState) -> VerticalGroup:
        return VerticalGroup(
            Static(f"{mon.name}: {mon.make}"),
            Select.from_values(
                mon.available_modes,
                prompt="Monitor mode",
                allow_blank=False,
                value=mon.mode or mon.available_modes[0],
                id=mon.name,
            ),
            Rule(),
        )

    def on_mount(self) -> None:
        self.call_after_refresh(self._enable_events)

    def _enable_events(self) -> None:
        self._ready = True

    def on_select_changed(self, event: Select.Changed) -> None:
        if not self._ready:
            return

        event.stop()
        self.notify(f"Handled: {event.select.id} {event.select.value}")
