from telegram.ext import Updater, CommandHandler
import requests
import re
from settings import TG_TOKEN
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler
from gsheet import add_gsheet

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
                 InlineKeyboardButton("Option 2", callback_data='2')],

                [InlineKeyboardButton("Option 3", callback_data='3')]]

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text="Selected option: {}".format(query.data))



def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


# def bop(bot, update):
#     url = get_url()
#     chat_id = update.message.chat_id
#     bsp = bot.send_photo(chat_id=chat_id, photo=url)
#     print(bsp)
#     bsm = bot.send_message(chat_id=chat_id, text="test")
#     print(bsm)

def bop(update, context):
    url = get_url()
    chat_id = update.message.chat_id

    bsp = update.message.reply_photo(
        photo=url
    )
    print(bsp)
    # bsm = update.message.reply_message(
    #     text="test"
    # )
    # print(bsm)





def hello(update, context):
    update.message.reply_text(
        'Hello {}'.format(update.message.from_user.first_name))

def main():
    # this seems to be deprecated - ignoring for now coz we can
    updater = Updater(TG_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('hello', hello))
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    add_gsheet()

    print("bot started")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
