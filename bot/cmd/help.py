"""
file    : bot/cmd/help.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module handles the /help command for the Telegram bot. It dynamically scans the "bot/cmd" directory for available command modules, imports them, and generates a list of available commands with their descriptions.
    The descriptions are derived from the __doc__ string of the respective command classes.
    
    This file ensures that when a user types /help in the bot, they receive a list of available commands and a brief description of each, with the descriptions being pulled dynamically from the classes defined in the command modules.

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

import os, importlib, inspect
from telegram import Update
from telegram.ext import CallbackContext

class help:
    """Handles the /help command and provides a list of available commands.
    
    This class is responsible for sending the list of available commands to the user when they type /help. 
    It dynamically loads other command modules from the 'bot/cmd' directory, 
    extracts the description from each module's class docstring, 
    and presents the user with a list of available commands and brief descriptions.

    Methods:
        command(update: Update, context: CallbackContext): 
            Handles the /help command, dynamically loads all available commands, 
            and sends a list of commands with their descriptions to the user.
    """
    
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /help command."""
        help_text = "Available commands:\n"

        # Scan files in the bot/cmd folder and try to load them dynamically
        cmd_folder = "bot/cmd"
        for filename in os.listdir(cmd_folder):
            if filename.endswith(".py"):
                module_name = f"bot.cmd.{filename[:-3]}"  # Remove .py extension
                try:
                    # Dynamically import the module
                    module = importlib.import_module(module_name)
                    
                    # Try to find the class within the module
                    for name, obj in inspect.getmembers(module):
                        if inspect.isclass(obj) and hasattr(obj, 'command'):
                            command_class = obj
                            command_name = name.lower()
                            # Get the __doc__ for the command class
                            doc = getattr(command_class, "__doc__", "No documentation available")
                            # Use only the first line of the docstring
                            doc_line = doc.splitlines()[0] if doc else "No description"
                            help_text += f"/{command_name} - {doc_line}\n"
                except Exception as e:
                    print(f"Failed to load module {module_name}: {e}")

        # Send the help message with proper HTML escape
        help_text = help_text.replace("<", "&lt;").replace(">", "&gt;")  # Escape angle brackets to avoid HTML parsing issues
        await update.message.reply_text(help_text, parse_mode='HTML')
