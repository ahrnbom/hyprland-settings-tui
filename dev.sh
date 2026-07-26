#!/bin/bash

set -e

uv sync
uv format --preview-features format-command
uv run hyprland-settings-tui