import hyprland_schema
from hyprland_state import HyprlandState
from textual.app import App

from hyprland_settings_tui.main_screen import MainScreen


class UI(App):
    CSS = """
    TabPane { overflow: hidden; }
    DataTable { height: 1fr; }
    """

    def on_mount(self) -> None:
        state = HyprlandState()
        assert state.version, "hyprland not running"
        schema = hyprland_schema.load(f"v{state.version}")
        self.push_screen(MainScreen(state=state, schema=schema))


def main():
    ui = UI()
    ui.run()


if __name__ == "__main__":
    main()
