
from hyprland_version import determine_hyprland_version
import hyprland_schema

def get_default_version():
    return hyprland_schema.available_versions()[0]

def get_schema():
    version = determine_hyprland_version()
    if not version:
        version = get_default_version()
        print(f"Warning: could not determine hyprland version, defaulting to {version}")

    try:
        schema = hyprland_schema.load(version)
    except hyprland_schema.MigrationError:
        new_ver = get_default_version()
        print(f"Your hyprland version {version} is not supported, defaulting to {new_ver}")
        schema = hyprland_schema.load(new_ver)

    return schema
    