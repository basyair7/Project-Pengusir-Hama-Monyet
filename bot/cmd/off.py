from telegram import Update
from telegram.ext import CallbackContext
from utility.sound_control import is_sound_enabled, set_sound_enabled

class off:
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /off command to disable sound playback."""
        chat_id = update.message.chat_id
        
        # Check if sound is already disabled
        if not is_sound_enabled():
            await context.bot.send_message(chat_id=chat_id, text="🔇 Sound is already disabled.")
            return
        
        # Disable sound
        set_sound_enabled(False)
        await context.bot.send_message(chat_id=chat_id, text="🔇 Sound has been disabled.")