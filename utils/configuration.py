import os
import click

import configparser

import utils.logger as logger
from utils.const import CONFIG_FILE_PATH

config = configparser.ConfigParser()


def get_config_path():
    homedir = os.environ.get('HOME', None)
    if not homedir:
        click.echo('Home Directory Not found!! Set Environment `HOME` ')
        exit()
    logger.debug('Home Directory: {}'.format(homedir))
    config_file = os.path.join(homedir + CONFIG_FILE_PATH)
    logger.debug('Config File Location: {}'.format(config_file))
    if not os.path.exists(config_file):
        click.echo('ERROR: No Config file present')
        try:
            os.makedirs(os.path.dirname(config_file))
        except OSError as exc:  # Guard against race condition
            click.echo('Directory found! but not config file')

        logger.debug('Creating config file')
        file = open(config_file, 'w')
        file.write('[{}]'.format('global'))
        file.close()

    logger.debug(config.read(config_file))
    return config_file


config_file = get_config_path()


def set_env(profile, key, value):
    if not config.has_section(profile):
        config.add_section(profile)
    config.set(profile, key, value)
    write_config()


def add_profile(profile):
    if config.has_section(profile):
        click.echo('Section [{}] already exists!!'.format(profile))
        return

    config.add_section(profile)
    write_config()


def write_config():
    with open(config_file, 'w') as configfile:
        config.write(configfile)


def get_env(profile, key):
    if has_env(profile, key):
        return config.get(profile, key)
    logger.debug('Not found in current profile')

    click.echo('Value not found in {profile} use `cgccli config` command'.format(profile=profile))
    exit()


def has_env(profile, key):
    if profile:
        logger.debug('Searching in profile : {}'.format(profile))
        logger.debug('Searching key {}'.format(key))
        return config.has_option(profile, key)
    return False


def get_profiles():
    return config.sections()
