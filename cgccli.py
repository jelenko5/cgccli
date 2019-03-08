import click

from utils.helpers import set_color, set_debug, check_auth_token

from subcommands.projects import projects
from subcommands.files import files
from subcommands.whoami import whoami
from subcommands.config import config


@click.group()
@click.option('--token', help='CGC auth token')
@click.option('--debug', '-d', help="Flag which enables you to run the command with debug information in the output.",
              is_flag=True)
@click.option('--no-color', help="Flag which turns on/off the color of the output.", is_flag=True)
@click.option('--username', help='Can be used instead of `token`, but only if you have set token for this user in '
                                 '`config` command. If this argument is omitted, `default` user will be used so be '
                                 'careful when setting `token` for `default` user.')
@click.pass_context
def cli(cntx, token=None, debug=False, no_color=False, username=None):
    """CLI tool for CGC Public API \n
The Cancer Genomics Cloud (CGC), powered by Seven Bridges, is one of three pilot
systems funded by the National Cancer Institute to explore the paradigm of colocalizing
massive genomics datasets, like The Cancer Genomics Atlas (TCGA), alongside secure
and scalable computational resources to analyze them. \n

It is recommended that you start with `config` sub-command. Once you run it with :arg:`--username`, CLI will remember
you as `last_logged_user` so you dont have to include `--token` argument to commands anymore.
If you wish to switch to another profile, just include it's username in `--username` argument next time you run `cgccli`

For more info run: cgccli [SUBCOMMAND] --help"""

    set_color(cntx, no_color)
    set_debug(debug)
    check_auth_token(cntx, token, username)


# Register subcommands:
cli.add_command(files)
cli.add_command(projects)
cli.add_command(whoami)
cli.add_command(config)


# Runner:
def entry_point():
    try:
        cli()
    except Exception as e:
        click.echo('ERROR:')
        click.echo(e)


if __name__ == '__main__':
    entry_point()
