"""
file    : bot/cmd/enablesendmsg.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module handles the enabling of automatic message sending. 
    When the user triggers the /enablesendmsg command, this module adds 
    the chat ID to the database, allowing the bot to start sending 
    messages to that chat.

    It relies on environment variables to fetch database credentials 
    and interact with the database to store chat IDs.

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

class enablesendmsg:
    """Handles the /enablesendmsg command to allow automatic message sending.
    
    This class adds the given chat ID to the database, effectively enabling 
    automatic message sending for that chat. It requires certain environment 
    variables to function correctly:
    
    - DATABASE_NAME: The name of the database to connect to.
    - TABLE_NAME_CHATID: The name of the table in which chat IDs are stored.

    Attributes:
        db_name (str): The name of the database to connect to.
        table_name_chatID (str): The name of the table for storing chat IDs.
        db (DBConnect): The database connection object used to interact with the database.

    Methods:
        store_chatID(chat_id: str): Stores the given chat ID in the specified table.
        command(update: Update, context: CallbackContext): Handles the /enablesendmsg command 
            and stores the chat ID in the database.
    """
    
    def __init__(self):
        """Initializes the Enable class and loads environment variables."""
        botconfig = Config()
        self.table_name_chatID = botconfig.__dict__()["TABLE_NAME_CHATID"]
        self.db_name = botconfig.__dict__()["DATABASE_NAME"]
        
        self.db = DBConnect(self.db_name)

    def store_chatID(self, chat_id: str):
        """Stores the specified chat ID in the database.
        
        Args:
            chat_id (str): The chat ID to be stored in the database.
        """
        self.db.store_chatID(table_name=self.table_name_chatID, chat_id=chat_id)

    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /enablesendmsg command to enable automatic message sending.
        
        This method adds the chat ID of the user to the database, 
        enabling the bot to send automatic messages to that user.
        
        Args:
            update (Update): The update object that contains information 
                             about the incoming message.
            context (CallbackContext): The context object that contains 
                                       data related to the callback.
        """
        save_id = enablesendmsg()
        chat_id = update.message.chat_id
        save_id.store_chatID(chat_id=chat_id)
        await update.message.reply_text("Auto send message is enabled now")
