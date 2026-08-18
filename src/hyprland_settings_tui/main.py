import importlib.resources
from pathlib import Path
import shutil
import sys
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
    if "--create-application-shortcut" in sys.argv:
        create_application_shortcut()
    else:
        ui = UI()
        ui.run()


def create_application_shortcut():
    exec_path = shutil.which("hyprland-settings-tui") or sys.executable

    desktop_dir = Path.home() / ".local" / "share" / "applications"
    desktop_dir.mkdir(parents=True, exist_ok=True)

    icons_dir = desktop_dir.parent / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    icon_file = icons_dir / "hyprland-settings-tui.png"

    desktop_content = f"""[Desktop Entry]
Type=Application
Name=Hyprland Settings TUI
Comment=A terminal interface for configuring hyprland
Exec={exec_path}
Terminal=true
Categories=Utility;
Icon={icon_file}
"""

    icon_resource = importlib.resources.files("hyprland_settings_tui") / "icon.png"
    icon_file.write_bytes(icon_resource.read_bytes())

    desktop_file = desktop_dir / "hyprland-settings-tui.desktop"
    desktop_file.write_text(desktop_content)
    print(f"Created desktop shortcut at {desktop_file}")


if __name__ == "__main__":
    main()
