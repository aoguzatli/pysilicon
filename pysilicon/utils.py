from telegram.ext import Updater, MessageHandler, Filters
import sys

class TelegramNotifier():
    def __init__(self, token, chat_id):
        self.token = str(token)
        self.chat_id = str(chat_id)
        self.updater = Updater(token = self.token, use_context = True)
        self.bot = self.updater.dispatcher.bot

    def notify(self, msg:str)->None:
        self.bot.send_message(chat_id = self.chat_id, text = msg)

def telegram_notify(token, chat_id, msg = "Notification"):
    tn = TelegramNotifier(token, chat_id)
    tn.notify(msg)
