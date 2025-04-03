"""
file    : bot/cmd/status.py
version : 1.0.0
author  : basyair7
date    : 2025
description:
    This module handles the /status command for the Telegram bot. 
    When the user types /status, this module retrieves and displays 
    the system's current status, including system date and time, 
    platform details, CPU information, OS, and kernel version.

    It provides a snapshot of the current system, which can be helpful 
    for monitoring and diagnostics.

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

import os, platform
from datetime import datetime
from telegram import Update
from telegram.ext import CallbackContext

class status:
    """Handles the /status command and provides system information.
    
    This class retrieves and displays various details about the system 
    including the date and time, CPU information, platform model, 
    kernel version, and operating system.

    Methods:
        get_os(): Returns the operating system of the current system.
        stats(): Returns a dictionary containing the current system's 
                date, time, CPU information, platform model, kernel 
                version, and operating system.
        command(update: Update, context: CallbackContext): 
                Handles the /status command, fetches system status, 
                and replies to the user with system information.
    """
    
    def get_os(self):
        """Returns the operating system of the current system."""
        return platform.system()
    
    def stats(self):
        """Fetches system status details.
        
        Returns:
            dict: A dictionary containing system details like date, time, 
                  CPU information, model, kernel version, and OS.
        """
        
        now = datetime.now()
        date = now.strftime("%A, %B, %d, %Y")
        time = now.strftime("%H:%M:%S")
        
        sys_info = platform.uname()
        cpu_info = os.cpu_count()
        model = f"{sys_info.processor} {sys_info.machine}"
        if sys_info.system == "Windows":
            kernel = platform.version()
        else:
            kernel = sys_info.release
        
        return {
            "date": date, 
            "time": time,
            "cpu_info": f"{cpu_info} cores",
            "model": model,
            "kernel": kernel,
            "os": self.get_os()
        }
        
    @staticmethod
    async def command(update: Update, context: CallbackContext):
        """Handles the /status command.
        
        This method fetches the system's status by calling the `stats()` 
        method and formats the result into a human-readable message.
        
        Args:
            update (Update): The update object that contains information 
                             about the incoming message.
            context (CallbackContext): The context object that contains 
                                       data related to the callback.
        """
        # Create an instance of the Status class to access its methods
        status_instance = status()
        stats = status_instance.stats()  # Now we call stats() from the instance
        
        text = f"<b>System Information</b>\n"
        text += f"<pre>Name\t: MicroBox - Pembasmi Hama Monyet\n"
        text += f"Tanggal\t: {stats['date']} ({stats['time']})\n"
        text += f"Platform\t: {stats['model']}\n"
        text += f"CPU\t: {stats['cpu_info']}\n"
        text += f"OS\t: {stats['os']}\n"
        text += f"Kernel\t: {stats['kernel']}\n"
        text += f"Status\t: Online</pre>"
        await update.message.reply_text(parse_mode='html', text=text)
