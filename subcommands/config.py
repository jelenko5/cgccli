import click

from utils import logger
from utils.configuration import get_profiles, add_profile, set_env, has_env, get_env
# from utils.const import DEFAULT_USER


@click.command()
@click.option('--username', default=None)
@click.option('-f', '--force', help='Overwrite profile.', is_flag=True, default=False)
@click.pass_context
def config(cntx, username, force):
    """This command allows you to create users and set their `tokens`.
    If you omit `username` argument, token will be extracted from `last_logged_user` user.
    """

    token = cntx.parent.params.get('token')
    if username:
        if username not in get_profiles():
            logger.debug('Adding profile: {}'.format(username))
            add_profile(username)

        set_env('global', 'last_logged_user', username)
        if not has_env(username, 'token') and token or force:
            set_env(username, 'token', token)

    elif has_env('global', 'last_logged_user'):
        # command was started without `username`. We should try to get `last_logged_user`
        username = get_env('global', 'last_logged_user')
    else:
        click.BadOptionUsage('--username', 'No user provided! Please run `config` command.')

    cntx.obj['USER'] = username


