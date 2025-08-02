from telegram import Update
from telegram.ext import CallbackContext
from utility.sound_control import is_sound_enabled, set_sound_enabled

class on:
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /on command to enable sound playback."""
        chat_id = update.message.chat_id
        
        # Check if sound is enabled
        if is_sound_enabled():
            await context.bot.send_message(chat_id=chat_id, text="🔊 Sound is already enabled.")
            return
        
        # Enable sound
        set_sound_enabled(True)
        await context.bot.send_message(chat_id=chat_id, text="🔊 Sound has been enabled.")