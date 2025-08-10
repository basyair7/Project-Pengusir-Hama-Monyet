"""
file    : bot/cmd/on.py
version : 2.0.0
author  : basyair7
date    : 2025
description:
    Handles the /on command to enable sound playback.
    When the user triggers the /on command, this module enables sound
    playback for the bot and notifies the user.

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
from utility.sound_control import is_sound_enabled, set_sound_enabled

class on:
    """Handles the /on command to enable sound playback."""
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        chat_id = update.message.chat_id
        
        # Check if sound is enabled
        if is_sound_enabled():
            await context.bot.send_message(chat_id=chat_id, text="🔊 Sound is already enabled.")
            return
        
        # Enable sound
        set_sound_enabled(True)
        await context.bot.send_message(chat_id=chat_id, text="🔊 Sound has been enabled.")