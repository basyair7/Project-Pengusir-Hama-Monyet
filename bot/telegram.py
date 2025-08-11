"""_summary_
file    : bot/telegram.py
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

import os, importlib, asyncio
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from db import DBConnect
from .config import Config
from .cmd.changesound import changesound

class TelegramBot:
    def __init__(self):
        """
        Initialize the bot with the API token from .env file.
        """
        botconfig = Config()
        self.token = botconfig.__dict__()["TOKEN"]
        self.db_name = botconfig.__dict__()["DATABASE_NAME"]
        self.table_name = botconfig.__dict__()["TABLE_NAME"]
        self.table_name_chatID = botconfig.__dict__()["TABLE_NAME_CHATID"]
        
        # Create Application (replacing Updater)
        self.app = Application.builder().token(self.token).build()
        
        # Initialize the database connection
        self.db = DBConnect(self.db_name)
        
        # Register command handlers dynamically
        self.load_commands()

        # Register message handler for text messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Handler file audio/document audio
        self.app.add_handler(
            MessageHandler(filters.AUDIO | filters.Document.AUDIO, changesound.handle_audio)
        )


    def load_commands(self):
        """
        Dynamically loads command handlers from Python files located in the 'cmd' directory.
        
        This function scans the 'cmd' directory for Python files and attempts to dynamically 
        import each module. It then checks whether the module contains a class with the same 
        name as the filename (without the `.py` extension). If the class exists and contains 
        a `command` method, it registers the method as a Telegram bot command handler.

        This approach allows the bot to automatically detect and register new commands 
        without requiring manual updates to the codebase.

        Raises:
            ImportError: If a module fails to be imported.
            AttributeError: If the expected class does not exist in the module.
        """
        # Define the path to the command directory
        cmd_dir = os.path.join(os.path.dirname(__file__), 'cmd')
        print("\nInitializing Commands: ")

        # Iterate through all files in the 'cmd' directory
        for filename in os.listdir(cmd_dir):
            if filename.endswith(".py"):  # Only process Python files
                module_name = filename[:-3]  # Extract module name by removing '.py' extension
                class_name = module_name  # Expect class name to match filename

                try:
                    # Dynamically import the module
                    module = importlib.import_module(f'bot.cmd.{module_name}')
                    print(f"Checking module: {module_name}, expected class: {class_name}")  # Debug log

                    # Check if the module contains a class with the expected name
                    if hasattr(module, class_name):
                        command_class = getattr(module, class_name)

                        # Ensure the class contains a 'command' method
                        if hasattr(command_class, 'command'):
                            command_method = getattr(command_class, 'command')

                            # Register the command handler
                            self.app.add_handler(CommandHandler(module_name, command_method))
                            print(f"Registered command: /{module_name}")
                        else:
                            print(f"Warning: {class_name} does not contain a 'command' method.")
                    else:
                        print(f"Warning: {module_name}.py has no class named {class_name}")

                except ImportError as e:
                    print(f"Error: Failed to import module '{module_name}': {e}")
                except AttributeError as e:
                    print(f"Error: Module '{module_name}' is missing expected attributes: {e}")

        print()  # Print an empty line for better output readability
        
    async def handle_message(self, update: Update, context: CallbackContext) -> None:
        """Handles text messages sent by the user."""
        text = update.message.text
        await update.message.reply_text(f"You said: {text}, please send command /help")
        
    async def send_message(self, text: str, sensor_active: int):
        """Sends a message to all registered users concurrently and logs the status in the database."""
        # Create List for chat_ids
        self.chat_ids = self.db.load_chat_ids(self.table_name_chatID)
        max_retries = 5
        retry_delay = 3
        
        # Check if chat_ids is None (i.e., no chat IDs found in the database)
        if not self.chat_ids:
            print("No chat IDs found. Skipping message send.")
            self.db.insert_data(
                table_name=self.table_name,
                date=datetime.now().strftime("%m/%d/%Y"),
                time=datetime.now().strftime("%H:%M:%S"),
                chat_id="None",
                sensor_active=sensor_active,
                status="no_chat_ids"
            )
            return  # Exit if no chat IDs exist
        
        async def send_to_user(chat_id: int):
            """ Helper function to send message with retries """
            attempt = 0
            status = "failed"  # Default status in case of failure
            
            while attempt < max_retries:
                try:
                    # Check if chat_id is valid
                    if chat_id is not None and chat_id != "":  # Only attempt if the chat_id is not empty or None
                        await self.app.bot.send_message(chat_id=chat_id, text=text)
                        status = "success"
                        break
                
                except Exception as e:
                    attempt += 1
                    print(f"[{attempt}/{max_retries}] Failed to send message to {chat_id}: {e}")
                    
                    if attempt < max_retries:
                        print(f"Retrying in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                    else:
                        print(f"Message to {chat_id} failed after {max_retries} attempts")
                        
            # Save to database    
            self.db.insert_data(
                table_name=self.table_name,
                date=datetime.now().strftime("%m/%d/%Y"),
                time=datetime.now().strftime("%H:%M:%S"),
                chat_id=str(chat_id),
                sensor_active=sensor_active,
                status=status
            )

        # Send messages to all chat_ids in parallel
        await asyncio.gather(*(send_to_user(chat_id) for chat_id in self.chat_ids))
        
    def check_internet(host="8.8.8.8", port=53, timeout=3):
        """Check if the internet connection is available by pinging a reliable host."""
        import socket
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception as e:
            return False
        
    def run(self):
        """Start the bot and listen for incoming updates."""
        print("Bot is running...")
        
        # Loop until internet is available
        while True:
            if self.check_internet():
                print("Internet connection is available. Starting bot...")
                try:
                    self.app.run_polling()
                except Exception as e:
                    print(f"Error while running the bot: {e}")
                    print("Restarting bot in 5 seconds...")
                    asyncio.sleep(5)
            else:
                print("No internet connection. Retrying in 5 seconds...")
                asyncio.sleep(5)
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # loop.run_until_complete(self.app.run_polling())
        # loop.run_forever()
