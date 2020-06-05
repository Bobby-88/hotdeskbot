from telegram.ext import Updater, CommandHandler
import requests
import re
from settings import TG_TOKEN
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, \
    ReplyKeyboardRemove
from telegram.ext import (Updater, CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler, Filters)
from gsheet import *

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# OFFICE, \
EMAIL, PASSWORD, SUMMARY, BEGIN_MAIN_JOURNEY = range(4)


# inv_offices = []

# def start(update, context):
#     keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
#                  InlineKeyboardButton("Option 2", callback_data='2')],
#
#                 [InlineKeyboardButton("Option 3", callback_data='3')]]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


# def start(update, context):
#     keyboard = [[InlineKeyboardButton("Option 1", callback_data='1'),
#                  InlineKeyboardButton("Option 2", callback_data='2')],
#
#                 [InlineKeyboardButton("Option 3", callback_data='3')]]
#
#     reply_markup = InlineKeyboardMarkup(keyboard)
#
#     update.message.reply_text('Please choose:', reply_markup=reply_markup)


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


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])
    return menu


def offices(update, context):
    # button_list = [[KeyboardButton(s)] for s in inv_offices]
    # button_list = [[InlineKeyboardButton("Option 1", callback_data='1'),
    #              InlineKeyboardButton("Option 2", callback_data='2')],
    #
    #             [InlineKeyboardButton("Option 3", callback_data='3')]]
    # print(inv_offices)
    # print(button_list)
    # reply_markup = InlineKeyboardMarkup(button_list)
    # reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))

    # dicts = {"Name": "John", "Language": "Python", "API": "pyTelegramBotAPI"}
    # logger.log(1,"message")
    buttons = []

    # for key, value in dicts.items():
    for value in inv_offices:
        buttons.append(
            [InlineKeyboardButton(text=value, callback_data=value)]
        )
    keyboard = InlineKeyboardMarkup(buttons)
    # print(buttons)

    update.message.reply_text('Please choose:', reply_markup=keyboard)


def begin_main_journey(update, context):
    buttons = []

    # for key, value in dicts.items():
    for value in ["Хочу поработать", "Уезжаю в командос", "Корона? Хочу в офис"]:  # inv_offices:
        buttons.append(
            [InlineKeyboardButton(text=value, callback_data=value)]
        )
    keyboard = InlineKeyboardMarkup(buttons)
    # print(buttons)

    update.message.reply_text('Please choose:', reply_markup=keyboard)
    return ConversationHandler.END


def start(update, context):
    reply_keyboard = [inv_offices]

    update.message.reply_text(
        'Hi! My name is Professor Bot. I will hold a conversation with you. '
        'Send /cancel to stop talking to me.\n\n'
        'Are you a boy or a girl?',
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return OFFICE


def start_auth(update, context):
    user = update.message.from_user
    logger.info("Gender of %s: %s", user.first_name, update.message.text)
    update.message.reply_text('I see! What\'s your e-mail address ?',
                              reply_markup=ReplyKeyboardRemove())

    return EMAIL


def get_email(update, context):
    user = update.message.from_user
    # photo_file = update.message.photo[-1].get_file()
    # photo_file.download('user_photo.jpg')
    logger.info("Email of %s: %s", user.first_name, update.message.text)
    global email
    email = update.message.text
    update.message.reply_text('Gorgeous! Now, send me your password please, '
                              'or send /skip if you don\'t want to.')

    return PASSWORD


def skip_password(update, context):
    user = update.message.from_user
    logger.info("User %s did not send a photo.", user.first_name)
    update.message.reply_text('I bet you look great! Now, send me your location please, '
                              'or send /skip.')

    return PASSWORD


def get_password(update, context):
    user = update.message.from_user
    global password
    # user_location = update.message.location
    logger.info("Password of %s: %s", user.first_name, update.message.text)
    password = update.message.text
    update.message.reply_text('Maybe I can visit you sometime! '
                              'At last, tell me something about yourself.')

    return SUMMARY


# def skip_location(update, context):
#     user = update.message.from_user
#     logger.info("User %s did not send a location.", user.first_name)
#     update.message.reply_text('You seem a bit paranoid! '
#                               'At last, tell me something about yourself.')
#
#     return BIO


def complete_auth(update, context):
    authed = false
    tg_user = update.message.from_user
    logger.info("Bio of %s: %s", tg_user.first_name, update.message.text)
    for i, user in enumerate(inv_users):
        print(user, email)
        if user[0] == email and user[1] == password:
            print("match found:", user[2])
            print("match found:", i)
            # i+1 is needed because there counting starts at 1, not at 0
            persist_user_id(sheet, i + 1, tg_user.id)

    buttons = []

    # for key, value in dicts.items():
    for value in ["Хочу поработать", "Уезжаю в командос", "Корона? Хочу в офис"]:  # inv_offices:
        buttons.append(
            [InlineKeyboardButton(text=value, callback_data=value)]
        )
    keyboard = InlineKeyboardMarkup(buttons)

    update.message.reply_text('Чего тебе?:', reply_markup=keyboard)

    return BEGIN_MAIN_JOURNEY


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.',
                              reply_markup=ReplyKeyboardRemove())

    return ConversationHandler.END


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    # retrieving const DB
    global sheet
    sheet = add_gsheet()
    global inv_offices
    inv_offices = get_offices(sheet)
    print(inv_offices)
    global inv_users
    inv_users = get_users(sheet)
    print(inv_users)
    # bootstrapping telegram bot
    updater = Updater(TG_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('bop', bop))
    dp.add_handler(CommandHandler('hello', hello))
    # dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('offices', offices))

    onboarding_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_auth)],
        states={
            # OFFICE: [MessageHandler(Filters.text, get_office)],
            EMAIL: [MessageHandler(Filters.text, get_email)],
            PASSWORD: [MessageHandler(Filters.text, get_password)],
            # BIO: [MessageHandler(Filters.text, bio)],
            SUMMARY: [MessageHandler(Filters.text, complete_auth)],
            BEGIN_MAIN_JOURNEY: [MessageHandler(Filters.text, begin_main_journey)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(onboarding_handler)
    dp.add_error_handler(error)

    print("bot started")
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
