"""
file    : bot/cmd/setcommands.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module to handle setting bot commands dynamically by scanning the 'cmd' directory
    for available command modules and registering them with the Telegram Bot API.

Copyright:
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

import requests, os, importlib, inspect
from ..config import Config  # Importing bot configuration
from telegram import Update
from telegram.ext import CallbackContext

class setcommands:
    def __init__(self):
        """
        Initializes the Setcmd class.
        - Loads the bot token from the Config class.
        - Sets the API endpoint for setting commands.
        - Defines the directory path where command modules are stored.
        """
        botconfig = Config()
        self.token = botconfig.__dict__()["TOKEN"]  # Retrieve the bot token from Config
        self.api_url = f"https://api.telegram.org/bot{self.token}/setMyCommands"  # API URL for setting commands
        self.command_dir = os.path.join(os.path.dirname(__file__), 'cmd')  # Path to command directory

    def create_commands_payload(self):
        """
        Scans the 'cmd' directory for available command modules, dynamically loads them,
        and extracts command names and descriptions.
        
        Returns:
            dict: A payload containing a list of bot commands in the required API format.
        """
        commands = []  # List to store command information
        
        cmd_folder = "bot/cmd"  # Define the path to the command folder
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py"):  # Only process Python files
                module_name = f"bot.cmd.{filename[:-3]}"  # Remove the ".py" extension from the filename
                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)

                    # Iterate over members of the module to find classes with a 'command' attribute
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'command'):
                            command_class = obj  # Retrieve the class
                            command_name = name.lower()  # Convert class name to lowercase as the command name
                            
                            # Get the documentation string (__doc__) for the command class
                            doc = getattr(command_class, "__doc__", "No documentation available")
                            doc_line = doc.splitlines()[0] if doc else "No description"  # Extract the first line of docstring

                            # Append the command to the list in Telegram API format
                            commands.append({'command': command_name, 'description': doc_line})

                except Exception as e:
                    print(f"Failed to load module {module_name}: {e}")  # Print error if module fails to load

        return {'commands': commands}  # Return the command payload

    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """
        Handles the '/setcommands' command from a Telegram chat.
        - Loads available commands.
        - Sends a request to the Telegram API to update the bot's command list.
        - Responds to the user with the result.

        Args:
            update (Update): The Telegram update object containing user message data.
            context (CallbackContext): The Telegram callback context object.
        """
        setCmd = setcommands()  # Initialize Setcmd instance
        payload = setCmd.create_commands_payload()  # Create payload for setting commands

        # Send a POST request to the Telegram API with the commands
        response = requests.post(setCmd.api_url, json=payload)

        # Process API response
        if response.status_code == 200:
            data = response.json()
            if data.get('ok'):
                res_txt = "Commands set successfully"  # Success message
            else:
                res_txt = f"Failed to set commands: {data.get('description')}"  # API failure message
        else:
            res_txt = f"Error {response.status_code}: {response.text}"  # HTTP error message

        # Reply to the user with the result
        await update.message.reply_text(res_txt)
