from typing import List

from textual.containers import VerticalGroup
from textual.widget import Widget
from textual.widgets import Label
from hyprland_config import Keyword, load_lua, default_lua_entrypoint


class KeybindsEditor:
    def __init__(self):
        path = default_lua_entrypoint()
        self.config = load_lua(path)

        widgets: List[Widget] = []
        for bind in self.config.get_all("bind"):
            widgets.append(Label(bind))
        self.widget = VerticalGroup(*widgets)
