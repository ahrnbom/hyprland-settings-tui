from textual.app import App

from main_screen import MainScreen
from schema import get_schema


class UI(App):
    CSS = """
    TabPane { overflow: hidden; }
    DataTable { height: 1fr; }
    """

    def on_mount(self) -> None:
        self.push_screen(MainScreen(get_schema()))


def main():
    ui = UI()
    ui.run()


if __name__ == "__main__":
    main()
