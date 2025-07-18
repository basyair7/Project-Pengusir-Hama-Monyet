"""
file    : bot/cmd/disablesendmsg.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module handles the disabling of automatic message sending. 
    When the user triggers the /disablesendmsg command, this module removes 
    the chat ID from the database, effectively stopping the bot from 
    sending messages to that chat.

    It relies on environment variables to fetch database credentials 
    and interact with the database to store or remove chat IDs.

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

from telegram import Update
from telegram.ext import CallbackContext
from db import DBConnect
from ..config import Config

class disablesendmsg:
    """Handles the /disablesendmsg command to stop the bot from sending automatic messages.
    
    This class removes the given chat ID from the database, effectively disabling 
    automatic messages for that chat. It requires certain environment variables 
    to function correctly:
    
    - DATABASE_NAME: The name of the database to connect to.
    - TABLE_NAME_CHATID: The name of the table in which chat IDs are stored.

    Attributes:
        db_name (str): The name of the database to connect to.
        table_name_chatID (str): The name of the table for storing chat IDs.
        db (DBConnect): The database connection object used to interact with the database.

    Methods:
        remove_chatID(chat_id: str): Removes the given chat ID from the specified table.
        command(update: Update, context: CallbackContext): Handles the /disablesendmsg command 
            and removes the chat ID from the database.
    """

    def __init__(self):
        """Initializes the Disable class and loads environment variables."""
        botconfig = Config()
        self.table_name_chatID = botconfig.__dict__()["TABLE_NAME_CHATID"]
        self.db_name = botconfig.__dict__()["DATABASE_NAME"]
        
        self.db = DBConnect(self.db_name)

    def remove_chatID(self, chat_id: str):
        """Removes the specified chat ID from the database.
        
        Args:
            chat_id (str): The chat ID to be removed from the database.
        """
        self.db.remove_chatID(table_name=self.table_name_chatID, chat_id=chat_id)

    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /disablesendmsg command to disable automatic message sending.
        
        This method removes the chat ID of the user from the database, 
        effectively disabling the auto-send message functionality for that user.
        
        Args:
            update (Update): The update object that contains information 
                             about the incoming message.
            context (CallbackContext): The context object that contains 
                                       data related to the callback.
        """
        remove_id = disablesendmsg()
        chat_id = update.message.chat_id
        remove_id.remove_chatID(chat_id=chat_id)
        await update.message.reply_text("Auto send message is disabled now")
