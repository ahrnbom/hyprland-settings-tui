import subprocess
from typing import List


def parse_lines_after_keyword(cmd: str, kw: str | None, split: str):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True)
    active = kw is None
    cmds: List[str] = []
    infos: List[str] = []
    for line in result.stdout.decode().split("\n"):
        if kw and kw in line:
            active = True
            continue

        if active and line:
            cmd, _, info = line.lstrip().partition(split)
            cmds.append(cmd.strip())
            infos.append(info.strip())

    return cmds, infos


def find_noctalia_commands():
    return parse_lines_after_keyword("noctalia msg --help", "Commands:", "  ")


def find_flatpak_commands():
    return parse_lines_after_keyword(
        "flatpak list --app --columns=name,application", None, "\t"
    )


if __name__ == "__main__":
    cmds, infos = find_noctalia_commands()
    for cmd, info in zip(cmds, infos):
        print(cmd, " -> ", info)
