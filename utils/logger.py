import click

debug_logging = False
debug_style = dict()


def is_debug_mode():
    return debug_logging


def debug(output):
    if debug_logging:
        click.echo(click.style(output, **debug_style))


def enable_debug():
    global debug_logging
    debug_logging = True
    debug('Running in DEBUG mode!')


def set_debug_style(style):
    if style:
        global debug_style
        debug_style = style

