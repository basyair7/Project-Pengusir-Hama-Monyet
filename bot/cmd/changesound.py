"""
file    : bot/cmd/changesound.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module handles the /changesound command that allows users to
    update the alarm sound played by the system. Once triggered, the bot
    prompts the user to send a new audio file (.wav or .mp3) and replaces
    the existing alarm file.

    The new audio file will replace alarm/alarm.wav and will be used on
    the next sound trigger.

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

import os, time
from pydub import AudioSegment
from telegram import Update
from telegram.ext import CallbackContext
from ..config import Config

class changesound:
    """Handles the /changesound command for replacing alarm sound file."""
    """
    Attributes:
        accepted_formats (tuple): Allowed file extensions for the sound file. waiting_chat (set): Chat IDs awaiting audio file input.
        
        Methods:
            command(update: Update, context: CallbackContext): Triggers the sound change prompt.
            handle_audio(update: Update, context: CallbackContext): Handles incoming audio/doc file.
    """
    
    waiting_chats = set()
    accepted_formats = ('.wav', '.mp3')
    
    def __init__(self):
        botconfig = Config()
        self.table_name_chatID = botconfig.__dict__()["TABLE_NAME_CHATID"]
    
    
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Starts the sound change process by prompting user for file."""
        chat_id = update.message.chat_id
        changesound.waiting_chats.add(chat_id)
        await update.message.reply_text("Please send a sound file (.wav or .mp3) to replace the alarm.")
        
    @staticmethod    
    def safe_delete(file_path):
        for i in range(3):
            try:
                os.remove(file_path)
                return True
            except PermissionError:
                print(f"[Retry {i+1}] File sedang digunakan. Menunggu...")
                time.sleep(1)
        print("Failed: Permission denied")
        return False
        
    @staticmethod
    async def handle_audio(update: Update, context: CallbackContext):
        """Receives and replaces the alarm sound file if valid format is sent."""
        chat_id = update.message.chat_id
        if chat_id not in changesound.waiting_chats:
            return # Ignore if not in waiting state
        
        audio = update.message.audio or update.message.document
        if not audio:
            return
        
        file_name = audio.file_name
        if not file_name.lower().endswith(changesound.accepted_formats):
            await update.message.reply_text("Formats not supported. Please send .wav or .mp3 files")
            return
        
        file = await context.bot.get_file(audio.file_id)
        temp_path = f"alarm/temp{os.path.splitext(file_name)[1]}"
        final_path = "alarm/alarm.wav"

        # Ensure alarm directory exists
        os.makedirs("alarm", exist_ok=True)

        # Download file
        await file.download_to_drive(temp_path)

        try:
            sound = AudioSegment.from_file(temp_path)
            sound.export(final_path, format="wav")
            # os.remove(temp_path)
            changesound.safe_delete(temp_path)
        except Exception as e:
            await update.message.reply_text(f"Failed to convert sound: {e}")
            return
            
        changesound.waiting_chats.remove(chat_id)
        await update.message.reply_text("🎵 Alarm sound changed successfully!")