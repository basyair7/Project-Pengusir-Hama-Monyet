"""_summary_
file    : utils/sound_control.py
version : 2.0.0
author  : basyair7
date    : 2025
copyright:
    Copyright (C) 2025, basyair7
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>
"""

SOUND_FILE = "utility/sound.txt"

def is_sound_enabled():
    """Check if sound is enabled by reading from a file."""
    try:
        with open(SOUND_FILE, 'r') as file:
            return file.read().strip().lower() == "on"
    
    except FileNotFoundError:
        print(f"Warning: {SOUND_FILE} not found. Defaulting to sound enabled.")
        return True  # Default to sound enabled if file does not exist
    
    except Exception as e:
        print(f"Error reading {SOUND_FILE}: {e}")
        return True  # Default to sound enabled on error
    
def set_sound_enabled(enabled: bool):
    with open(SOUND_FILE, 'w') as file:
        file.write("on" if enabled else "off")