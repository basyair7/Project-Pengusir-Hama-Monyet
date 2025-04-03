"""_summary_
file    : sensor/__init__.py
version : 1.0.0
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

import RPi.GPIO as GPIO

class Sensor:
    def __init__(self, *sensor_pins: int):
        """
        Initialize the sensor with the given pins, ensuring no duplicates.
        
        Parameters:
        sensor_pins: Pin GPIO numbers for the sensors.
        """
        # Remove duplicates by converting to a set and back to a list
        unique_pins = list(set(sensor_pins))
        
        # Check for duplicates
        if len(unique_pins) < len(sensor_pins):
            print("Warning: Duplicate pins detected, duplicates have been removed.")
        
        self.sensors = unique_pins

    def setup(self):
        """Set up the GPIO pins as input."""
        GPIO.setmode(GPIO.BCM)
        for pin in self.sensors:
            GPIO.setup(pin, GPIO.IN)

    def get_action(self):
        """
        Returns: Dictionary with sensor statuses.
        """
        return {f"sensor_{i+1}": GPIO.input(pin) for i, pin in enumerate(self.sensors)}

    def cleanup(self):
        """Cleans up the GPIO resources."""
        GPIO.cleanup()
