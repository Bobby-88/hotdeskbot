#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
First, a few callback functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Example of a bot-user conversation using ConversationHandler.
Send /start to initiate the conversation.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import telegramcalendar
from settings import TG_TOKEN
from bot import responds

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler, CallbackQueryHandler)
import telegramcalendar

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

HOT_DESK, START_DATE, END_DATE, SEAT_RESERVATION = range(4)


def start(update, context):
    reply_keyboard = [['Забронировать рабочее место👨‍💻']]

    update.message.reply_text(
        responds.GREETING,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return HOT_DESK

def hotdesk(update, context):
    reply_keyboard = [['Хочу поработать!']]
    update.message.reply_text(
        responds.UC1_WELCOME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START_DATE


def calendar_handler(update, context):
    update.message.reply_text(text="Please select a date: ",
                              reply_markup=telegramcalendar.create_calendar())

def inline_handler(update, context):
    selected, date = telegramcalendar.process_calendar_selection(update, context)
    if selected:
        context.bot.send_message(chat_id=update.callback_query.from_user.id,
                                 text="You selected %s" % (date.strftime("%d/%m/%Y")),
                                 reply_markup=ReplyKeyboardRemove())

def start_date(update, context):
    user = update.message.from_user
    reply_keyboard = [['start date']]
    logger.info("start date")
    update.message.reply_text(text=responds.UC1_START_DATE,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return END_DATE


def end_date(update, context):
    user = update.message.from_user
    reply_keyboard = [['end date']]
    logger.info("end date")
    update.message.reply_text(text=responds.UC1_END_DATE,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SEAT_RESERVATION


def seat_reservation(update, context):
    update.message.reply_text(responds.UC1_SEAT_RESERVATION)
    return ConversationHandler.END


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
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TG_TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher
    dp.add_handler(CallbackQueryHandler(inline_handler))


    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            HOT_DESK: [MessageHandler(Filters.text, hotdesk)],

            START_DATE: [MessageHandler(Filters.text, calendar_handler)],

            END_DATE: [MessageHandler(Filters.text, end_date)],

            SEAT_RESERVATION: [MessageHandler(Filters.text, seat_reservation)]
        },

        fallbacks=[CommandHandler('cancel', cancel)]
    )

    dp.add_handler(conv_handler)


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
