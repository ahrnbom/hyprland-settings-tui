# Determine the hyprland version

import subprocess

NUMBERS_AND_DOT = "0123456789."


def determine_hyprland_version():
    """
    Returns None if the version cannot be determined
    """

    out = subprocess.run(["hyprland", "--version"], shell=False, stdout=subprocess.PIPE)
    output = out.stdout.decode()
    if not output.startswith("Hyprland "):
        return None

    words = output.split(" ")
    if len(words) < 2:
        return None

    version = words[1]
    if not version:
        return None

    for letter in version:
        if letter not in NUMBERS_AND_DOT:
            return None

    return "v" + version


if __name__ == "__main__":
    print(determine_hyprland_version())
