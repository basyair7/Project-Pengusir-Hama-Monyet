import os
from dotenv import load_dotenv

class Config:
    def __init__(self):
        load_dotenv()
        
        self.TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.DATABASE_NAME = os.getenv("DATABASE_NAME")
        self.TABLE_NAME = os.getenv("TABLE_NAME")
        self.TABLE_NAME_CHATID = os.getenv("TABLE_NAME_CHATID")

        if not all([self.TOKEN, self.DATABASE_NAME, self.TABLE_NAME, self.TABLE_NAME_CHATID]):
            raise ValueError("Required environment variables are not set.")

    def __dict__(self):
        return ({
            "TOKEN": self.TOKEN,
            "DATABASE_NAME": self.DATABASE_NAME,
            "TABLE_NAME": self.TABLE_NAME,
            "TABLE_NAME_CHATID": self.TABLE_NAME_CHATID
        })