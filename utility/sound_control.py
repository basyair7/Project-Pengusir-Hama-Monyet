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

class sound_control:
    """Sound control utility for enabling/disabling sound playback."""
    def __init__(self):
        self.sound_file = "utility/sound.txt"

    def is_sound_enabled(self):
        """Check if sound is enabled by reading from a file."""
        try:
            with open(self.sound_file, 'r') as file:
                return file.read().strip().lower() == "on"
        
        except FileNotFoundError:
            print(f"Warning: {self.sound_file} not found. Defaulting to sound enabled.")
            return True  # Default to sound enabled if file does not exist
        
        except Exception as e:
            print(f"Error reading {self.sound_file}: {e}")
            return True  # Default to sound enabled on error
    
    def set_sound_enabled(self, enabled: bool):
        """Set sound enabled/disabled by writing to a file."""
        with open(self.sound_file, 'w') as file:
            file.write("on" if enabled else "off")