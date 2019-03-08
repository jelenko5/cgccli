import json

import click

from api_urls import PAGINATED_PROJECTS_LIST_URL, PROJECTS_DETAIL_URL
from utils.helpers import send_paginated_api_request, send_api_request, parse_query_params
from utils.const import ITEMS_PER_SCREEN, PROJECT_DETAIL_SUCCESS_MESSAGE, PROJECT_DETAIL_FAILURE_MESSAGE, \
    PROJECT_PROMPT_MESSAGE


@click.group()
def projects():
    """Manage your projects on CGC. \n
    For more info run: cgccli projects [SUBCOMMAND] --help"""
    pass


@projects.command()
@click.option('--project', help="ID ({owner}/{id}) of project which details should be writen in the output.")
@click.option('--fields', help='Subset of fields to include in output. Separate them with coma(no blanks between).',
              default=None)
@click.pass_context
def stat(cntx, project, fields):
    """Outputs details about requested project."""

    base_url = PROJECTS_DETAIL_URL.format(project_id=project) + ('?' if fields else '')
    url = parse_query_params({'fields': fields}, base_url)
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}
    response = send_api_request(url=url, verb='GET', headers=headers)

    if response.get('id'):
        output = PROJECT_DETAIL_SUCCESS_MESSAGE.format(project_id=response.get('id'))
        click.echo(click.style(output,  **cntx.obj.get('STYLE')))
        click.echo(json.dumps(response, indent=4))
    else:
        output = PROJECT_DETAIL_FAILURE_MESSAGE.format(project_id=project)
        click.echo(click.style(output, **cntx.obj.get('STYLE')))


@projects.command()
@click.option('--fields', help='Subset of fields to include in output. Separate them with coma(no blanks between).',
              default=None)
@click.pass_context
def list(cntx, fields):
    """List projects filtered by command options."""

    click.echo(click.style('Project list:\n',  **cntx.obj.get('STYLE')))
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}

    base_url = PAGINATED_PROJECTS_LIST_URL.format(limit=ITEMS_PER_SCREEN)
    url = parse_query_params(query_params={'fields': fields}, base_url=base_url)

    for response, next_page in send_paginated_api_request(url=url, headers=headers):
        for item in response['items']:
            click.echo(json.dumps(item, indent=4))
        if not next_page or \
                not click.confirm(click.style('Load next page of projects?', **cntx.obj.get('STYLE')), abort=False):
            break

    project_id = click.prompt(click.style(PROJECT_PROMPT_MESSAGE, **cntx.obj.get('STYLE')))
    if project_id.lower() == 'exit':
        return

    cntx.params['project'] = project_id
    cntx.params['fields'] = fields
    stat.invoke(cntx)
