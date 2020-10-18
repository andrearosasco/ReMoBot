#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import multiprocessing as mp
import re
import subprocess
import time

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
from Allocator import Allocator
from Monitor import Monitor

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def nvidia_smi():
    out = subprocess.Popen(['nvidia-smi'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    sout, serr = out.communicate()
    res = re.findall("([0-9]*)MiB / 16130MiB", str(sout))
    res = [int(x) for x in res]
    return (f'GPU 0 | {res[0]:05d}MiB / 16130MiB | {int(res[0]/16130 * 100):02d}%\n'
            f'GPU 1 | {res[1]:05d}MiB / 16130MiB | {int(res[1]/16130 * 100):02d}%\n'
            f'GPU 2 | {res[2]:05d}MiB / 16130MiB | {int(res[2]/16130 * 100):02d}%\n'
            f'GPU 3 | {res[3]:05d}MiB / 16130MiB | {int(res[3]/16130 * 100):02d}%\n')

# Define a few command handlers. These usually take the two arguments update and
# context. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help(update, context):
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')


def echo(update, context):
    """Echo the user message."""
    # update.message.reply_text(threading.active_count())

def check(update, context):
    update.message.reply_text(nvidia_smi())

def error(update, context):
    """Log Errors caused by Updates."""
    raise context.error
    # logger.warning('Update "%s" caused error "%s"', update, context.error)



def notify(update, context):
    user = update.effective_user

    if len(context.args) != 1 or \
            int(context.args[0]) not in range(0, 16100):
        update.message.reply_text('You must provide an integer between 0 and 16100')
        return

    threshold = int(context.args[0])

    if 'monitor' not in context.bot_data or not context.bot_data['monitor'].is_alive():
        monitor = context.bot_data['monitor'] = Monitor()
        monitor.add(user, threshold)
        monitor.start()

    monitor = context.bot_data['monitor']
    monitor.add(user, threshold)


    update.message.reply_text(f'Monitoring started! You\'ll be notified when one of the GPUs has more than {threshold}MiB'
                              ' memory available.')

memory = dict()
def reserve(update, context):
    user = update.effective_user

    if len(context.args) != 2 or \
            int(context.args[0]) not in range(305, 7000) or \
            int(context.args[1]) not in range(4):
        update.message.reply_text('You must provide an integer between 305 and 7000')
        return

    if 'reserved' in context.user_data:
        update.message.reply_text('Before allocating other memory free the one you previously reserved')
        return

    # subtract 300 because numba already allocates 300 when initialized
    size = str(int(context.args[0]) - 305)
    gpu = context.args[1]

    if 'allocator' not in context.bot_data:
        context.bot_data[f'allocator'] = Allocator()

    allocator = context.bot_data['allocator']
    allocator.add(user, size, gpu)
    context.user_data['reserved'] = True

    update.message.reply_text('Memory reserved.')
    time.sleep(1)
    update.message.reply_text(nvidia_smi())

def free(update, context):
    user = update.effective_user
    if 'reserved' not in context.user_data:
        update.message.reply_text('You have to reserve some memory before deallocating it')
        return

    context.bot_data[f'allocator'].remove(user)
    context.user_data.pop('reserved')


    update.message.reply_text('Memory freed.')
    time.sleep(1)
    update.message.reply_text(nvidia_smi())

def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("YOUR-TOKEN-GOES-HERE", use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    monitor = Monitor()
    # on different commands - answer in Telegram
    filter = Filters.user()
    filter.add_usernames(['allowed', 'user', 'names'])
    dp.add_handler(CommandHandler("start", start, filters=filter))
    dp.add_handler(CommandHandler("help", help, filters=filter))
    dp.add_handler(CommandHandler("check", check, filters=filter))
    dp.add_handler(CommandHandler("notify", notify, filters=filter))
    dp.add_handler(CommandHandler("reserve", reserve, filters=filter, pass_user_data=True))
    dp.add_handler(CommandHandler("free", free, filters=filter, pass_user_data=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    mp.set_start_method('fork')
    main()