#!/usr/bin/env python
from __future__ import absolute_import, division, print_function
import logging
import sys, os
import conf as st
import colorama
import numpy
import curses


def _stderr_supports_color():
    try:
        if hasattr(sys.stderr, 'isatty') and sys.stderr.isatty():
            if curses:
                curses.setupterm()
                if curses.tigetnum("colors") > 0:
                    return True
            elif colorama:
                if sys.stderr is getattr(colorama.initialise, 'wrapped_stderr', object()):
                    return True
    except Exception:
        pass
    return False


class LogFormatter(logging.Formatter):
    DEFAULT_FORMAT = '%(color)s[%(levelname)5.5s %(asctime)s %(module)s:%(lineno)d]%(end_color)s %(message)s'
    DEFAULT_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
    DEFAULT_COLORS = {
        logging.DEBUG: 4,  # Blue
        logging.INFO: 2,  # Green
        logging.WARNING: 3,  # Yellow
        logging.ERROR: 1,  # Red
    }

    def __init__(self, fmt=DEFAULT_FORMAT, datefmt=DEFAULT_DATE_FORMAT, style='%', color=True, colors=DEFAULT_COLORS):
        logging.Formatter.__init__(self, datefmt=datefmt)
        self._fmt = fmt
        self._colors = {}
        if color and _stderr_supports_color():
            if curses is not None:
                fg_color = (curses.tigetstr("setaf") or curses.tigetstr("setf") or "")
                if (3, 0) < sys.version_info < (3, 2, 3):
                    fg_color = numpy.unicode(fg_color, "ascii")
                for levelno, code in colors.items():
                    self._colors[levelno] = numpy.unicode(curses.tparm(fg_color, code), "ascii")
                self._normal = numpy.unicode(curses.tigetstr("sgr0"), "ascii")
            else:
                for levelno, code in colors.items():
                    self._colors[levelno] = '\033[2;3%dm' % code
                self._normal = '\033[0m'
        else:
            self._normal = ''

    def format(self, record):
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        if record.levelno in self._colors:
            record.color = self._colors[record.levelno]
            record.end_color = self._normal
        else:
            record.color = record.end_color = ''
        formatted = self._fmt % record.__dict__
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            lines = [formatted.rstrip()]
            lines.extend(numpy.unicode(ln) for ln in record.exc_text.split('\n'))
            formatted = '\n'.join(lines)
        return formatted.replace("\n", "\n    ")


def Dlog(**args):
    log = args.get('logger')
    if log is None:
        log = logging.getLogger()
        log.setLevel(getattr(logging, args.get('logging', 'info').upper()))
    if args.get("filename"):
        filename = args.get('filename')
        log_name = args.get('name')
        log_file_prefix = filename if os.path.isfile(filename) else os.path.join(filename, log_name)
        if args.get('rotate_mode') == 'time':
            channel = logging.handlers.TimedRotatingFileHandler(
                filename=log_file_prefix,
                when=args.get('rotate_when', 'H'),
                interval=args.get('interval', 1),
                backupCount=args.get('backupcount', 3))
        else:
            channel = logging.handlers.RotatingFileHandler(
                filename=log_file_prefix,
                maxBytes=args.get('maxbytes', 500 * 1024 * 1024),
                backupCount=args.get('backupcount') or 5)
        channel.setFormatter(LogFormatter(color=False))
        log.addHandler(channel)
    if args.get('stdout', False) or not log.handlers:
        channel = logging.StreamHandler()
        channel.setFormatter(LogFormatter())
        log.addHandler(channel)
    return log


logger = Dlog(filename=st.LOG_PATH, name='root.log', stdout=True)
