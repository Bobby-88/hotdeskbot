from telegram.ext import Updater, CommandHandler
import requests
import re
TOKEN = "1082297400:AAE2fpM8ONwmS4NtQj0d6HsDfXNl0lKa3kY"

def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url

def bop(bot, update):
    url = get_url()
    chat_id = update.message.chat_id
    bot.send_photo(chat_id=chat_id, photo=url)


def main():
    #this seems to be deprecated - ignoring for now coz we can
    updater = Updater(TOKEN)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
