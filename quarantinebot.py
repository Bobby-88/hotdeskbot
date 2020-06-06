import logging

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters,
                          ConversationHandler)
from settings import TG_TOKEN
from bot import responds

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

RESERVAION_RESULT, QUARANTINE_EXIT, LOCATION = range(3)


def start(update, context):
    reply_keyboard = [['Выйти в офис🏢']]
    update.message.reply_text(
        responds.GREETING,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return QUARANTINE_EXIT

def quarantine_exit(update, context):
    reply_keyboard = [['Конечно хочу! 🏢']]
    update.message.reply_text(
        responds.UC2_WELCOME,
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True))

    return RESERVAION_RESULT


def reservation_result(update, context):
    update.message.reply_text(responds.UC2_YES)
    return ConversationHandler.END


def cancel(update, context):
    user = update.message.from_user
    logger.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text('Пока До встречи',
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

    # Add conversation handler with the state RESERVAION_RESULT
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            RESERVAION_RESULT: [MessageHandler(Filters.text, reservation_result)],
            QUARANTINE_EXIT: [MessageHandler(Filters.text, quarantine_exit)]
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