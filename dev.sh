#!/bin/bash

set -e

uv sync
uv check --preview-features check-command
uv format --preview-features format-command
uv run hyprland-settings-tui