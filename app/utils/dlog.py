#!/usr/bin/env python
import logging
import sys, os
import conf
import colorama
import numpy
import curses


class LogFormatter(logging.Formatter):

    def __init__(self, color=True):
        logging.Formatter.__init__(self, fmt='%(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    def format(self, record):
        fmt = '%(color)s[%(asctime)s %(module)s.%(funcName)s:%(lineno)d]%(end_color)s %(message)s'
        color_config = {
            logging.DEBUG: colorama.Fore.BLUE,
            logging.INFO: colorama.Fore.GREEN,
            logging.WARNING: colorama.Fore.YELLOW,
            logging.ERROR: colorama.Fore.RED
        }
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        record.color = color_config.get(record.levelno, colorama.Fore.GREEN)
        record.end_color = colorama.Fore.LIGHTGREEN_EX
        formatted = fmt % record.__dict__
        if record.exc_info and not record.exc_text:
            record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            formatted += record.exc_text
        return formatted


def Dlog(filename: str, max_bytes=500*1024*1024, stdout=False, backup_count=5):
    log = logging.getLogger()
    log.setLevel(logging.INFO)
    fmt = LogFormatter()
    channel = logging.handlers.RotatingFileHandler(filename=filename, maxBytes=max_bytes, backupCount=backup_count)
    channel.setFormatter(fmt)
    log.addHandler(channel)
    if stdout:
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        log.addHandler(console)
    return log


logger = Dlog(filename=conf.LOG_PATH, stdout=conf.settings['debug'])
# logger.info('sd')
