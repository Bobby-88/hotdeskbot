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
from bot import responses

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove, ParseMode)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

START_DATE, END_DATE, SEAT_RELEASE, BUSINESS_TRIP = range(4)


def start(update, context):
    reply_keyboard = [[responses.BUTTON_FLIGHT]]
    update.message.reply_text(
        responses.GREETING, parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return BUSINESS_TRIP

def business_trip(update, context):
    reply_keyboard = [['ОК']]
    update.message.reply_text(
        responses.FLIGHT_WELCOME, parse_mode=ParseMode.MARKDOWN_V2,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return START_DATE


def start_date(update, context):
    user = update.message.from_user
    reply_keyboard = [['start date']]
    logger.info("start date")
    update.message.reply_text(text=responses.FLIGHT_START_DATE, parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return END_DATE


def end_date(update, context):
    user = update.message.from_user
    reply_keyboard = [['end date']]
    logger.info("end date")
    update.message.reply_text(text=responses.FLIGHT_END_DATE, parse_mode=ParseMode.MARKDOWN_V2,
                              reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return SEAT_RELEASE


def seat_release(update, context):
    update.message.reply_text(responses.FLIGHT_SEAT_RELEASE)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Bye! I hope we can talk again some day.', parse_mode=ParseMode.MARKDOWN_V2,
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

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            BUSINESS_TRIP: [MessageHandler(Filters.text, business_trip)],

            START_DATE: [MessageHandler(Filters.text, start_date)],

            END_DATE: [MessageHandler(Filters.text, end_date)],

            SEAT_RELEASE: [MessageHandler(Filters.text, seat_release)]
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
