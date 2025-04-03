from bot.telegram import TelegramBot
import asyncio

bot = TelegramBot()

async def monitor_pir():
    while True:
        await bot.send_message("Sensor terdeteksi adanya Monyet!", 3)
        await asyncio.sleep(5)  # Use asyncio's sleep to prevent blocking

async def main():
    # Start the monitor_pir coroutine as a task
    asyncio.create_task(monitor_pir())

if __name__ == "__main__":
    # Since the bot already runs an event loop, just start the main coroutine
    asyncio.get_event_loop().run_until_complete(main())
    bot.run()