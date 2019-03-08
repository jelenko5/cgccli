import click

from api_urls import WHOAMI_DETAIL_URL
from utils.helpers import send_api_request, format_dict


@click.command()
@click.pass_context
def whoami(cntx):
    """Display information about the current user."""

    click.echo(click.style('User info:\n', **cntx.obj.get('STYLE')))
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}
    response = send_api_request(url=WHOAMI_DETAIL_URL, verb='GET', headers=headers)
    click.echo(format_dict(response))
