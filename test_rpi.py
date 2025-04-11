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

import asyncio, threading, pygame, time
from bot.telegram import TelegramBot
from sensor.pir import SensorPir

# Setup pygame for playsound
playsound = pygame.mixer
playsound.init()

# Sound Thread Control
should_play = False

# Initialize the PIR sensor with the pin numbers
pirsensor = SensorPir(17, 18, 19)
pirsensor.setup()

# Initialize the bot
bot = TelegramBot()

def sound_loop():
    global should_play
    while True:
        if (should_play and not playsound.music.get_busy()):
            try:
                playsound.music.load("alarm/alarm.wav")
                playsound.music.play(-1)
                print("🔊 Sound started")
            except Exception as e:
                print(f"⚠️ Failed to play sound: {e}")
        elif (not should_play and playsound.music.get_busy()):
            playsound.music.stop()
            print("🔇 Sound stopped")
        time.sleep(0.1)

# Function to monitor PIR sensor status
async def monitor_pir():
    global should_play
    while True:
        status = pirsensor.get_action()  # Get sensor statuses
        
        # Count how many sensors are active (detected motion)
        sensor_active_count = sum(1 for sensor_status in status.values() if sensor_status == 1)
        
        # Only send message if there's at least one active sensor
        if sensor_active_count > 0:
            message = f"Sensor detected Monkey! ({sensor_active_count} sensor's detected motion)"
            # Send message with sensor data
            await bot.send_message(message, sensor_active=sensor_active_count)
            should_play = True
        else:
            should_play = False
            
        # Wait for 5 seconds before checking again
        await asyncio.sleep(5)

# Main async function to run the monitor
async def main():
    # Start the monitor_pir coroutine as a task
    asyncio.create_task(monitor_pir())

if __name__ == "__main__":
    sound_thread = threading.Thread(target=sound_loop, daemon=True)
    sound_thread.start()
    
    # Start the bot and run the event loop
    asyncio.get_event_loop().run_until_complete(main())
    bot.run()
