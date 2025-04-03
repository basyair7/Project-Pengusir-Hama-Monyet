"""_summary_
file    : main.py
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

import asyncio
from bot.telegram import TelegramBot
from sensor.pir import Sensor

# Initialize the PIR sensor with the pin numbers
pirsensor = Sensor(17, 18, 19)
pirsensor.setup()

# Initialize the bot
bot = TelegramBot()

# Function to monitor PIR sensor status
async def monitor_pir():
    while True:
        status = pirsensor.get_action()  # Get sensor statuses
        
        # Count how many sensors are active (detected motion)
        sensor_active_count = sum(1 for sensor_status in status.values() if sensor_status == 1)
        
        # Only send message if there's at least one active sensor
        if sensor_active_count > 0:
            message = f"Sensor detected Monkey! ({sensor_active_count} sensor's detected motion)"
            # Send message with sensor data
            await bot.send_message(message, sensor_active=sensor_active_count)
            
        # Wait for 5 seconds before checking again
        await asyncio.sleep(5)

# Main async function to run the monitor
async def main():
    # Start the monitor_pir coroutine as a task
    asyncio.create_task(monitor_pir())

if __name__ == "__main__":
    # Start the bot and run the event loop
    asyncio.get_event_loop().run_until_complete(main())
    bot.run()
