import asyncio, threading, pygame, time, keyboard
from bot.telegram import TelegramBot

# Setup pygame for playsound
playsound = pygame.mixer
playsound.init()

# Sound Thread Control
should_play = False
keyboard_sensor = False

bot = TelegramBot()

def sound_loop():
    global should_play
    while True:
        if should_play and not playsound.music.get_busy():
            try:
                playsound.music.load("alarm/alarm.wav")
                playsound.music.play(-1)
                print("🔊 Sound started")
            except Exception as e:
                print(f"⚠️ Failed to play sound: {e}")
        elif not should_play and playsound.music.get_busy():
            playsound.music.stop()
            print("🔇 Sound stopped")
        time.sleep(0.1)

def keyboard_simulator():
    global keyboard_sensor
    print("🔧 Tekan [SPACE] untuk aktifkan alarm, tekan [Q] untuk berhenti.")
    while True:
        if keyboard.is_pressed('space'):
            keyboard_sensor = True
        elif keyboard.is_pressed('q'):
            keyboard_sensor = False
        time.sleep(0.1)

async def monitor_pir():
    global should_play
    while True:
        if keyboard_sensor:
            await bot.send_message("Sensor terdeteksi adanya Monyet!", 3)
            should_play = True
        else:
            should_play = False
        await asyncio.sleep(0.5)
        
async def main():
    asyncio.create_task(monitor_pir())

if __name__ == "__main__":
    sound_thread = threading.Thread(target=sound_loop, daemon=True)
    sound_thread.start()

    keyboard_thread = threading.Thread(target=keyboard_simulator, daemon=True)
    keyboard_thread.start()

    asyncio.get_event_loop().run_until_complete(main())
    bot.run()
