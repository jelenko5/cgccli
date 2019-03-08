import json
import requests

import click

from api_urls import PAGINATED_FILES_LIST_URL, FILES_DETAIL_URL, FILES_DOWNLOAD_URL
from utils import logger
from utils.helpers import send_paginated_api_request, parse_query_params, send_api_request, UpdateFileType, \
    normalize_file_size, parse_unknown_params, check_dir
from utils.const import ITEMS_PER_SCREEN, PROJECT_PARENT_ERROR_MESSAGE, PROJECT_LIST_REPLACEMENTS, \
    FILE_PROMPT_MESSAGE, FILE_DETAIL_SUCCESS_MESSAGE, FILE_UPDATE_SUCCESS_MESSAGE, FILE_DOWNLOAD_PROMPT_MESSAGE, \
    DOWNLOAD_CHUNK_SIZE

update_file_data = dict()


@click.group()
@click.pass_context
def files(cntx):
    """Manage your files on CGC. \n
    For more info run: cgccli files [SUBCOMMAND] --help"""
    # Inserting global variable to context object for easier handling of unstructured arguments
    global update_file_data
    cntx.obj['update_file_data'] = update_file_data
    pass


@files.command(context_settings=dict(
    ignore_unknown_options=True,
), short_help='List files filtered by command options.')
@click.option('--project', help='ID ({owner}/{id}) of project which file belongs to.', default=None)
@click.option('--parent', help='ID of the folder whose content you want to list.', default=None)
@click.option('--name', help='File name(multiple allowed).', multiple=True, default=None)
@click.option('--tag', help='File tag(multiple allowed).', multiple=True, default=None)
@click.option('--origin.task', 'origin_task', help='List only files produced by task specified by ID in this field',
              default=None)
@click.option('--origin.dataset', 'origin_dataset',
              help='List only files which are part of the dataset specified in this field.',
              type=click.Choice(['tcga', 'tcga_grch38', 'ccle', 'cptac', 'target']), default=None)
@click.option('--fields', help='Subset of fields to include in output. Separate them with coma(no blanks between).',
              default=None)
@click.argument('unknown_params', nargs=-1, type=click.UNPROCESSED)
@click.pass_context
def list(cntx, unknown_params=None, **kwargs):
    """List files filtered by command options.
    Additional (non-predefined) filters: \n
    - `metadata.{field}`="value as a string" - List only files that have the specified
    value in metadata field.

    Mandatory input format:
    - --metadata.{field}="value with spaces"` in case value has spaces
    - "metadata.{field with spaces}=value as a string" in case field name has spaces

    Tips for filtering:
    When filtering on any resource, including the same field several times with different filtering criteria results in
     an implicit OR operation for that field and the different criteria.

    When filtering by different specified fields, an implicit AND is performed between those criteria. Thus, the call
    in Example 3 above would return files matching the specified project AND sample ID AND library.

    """

    if kwargs['project'] and kwargs['parent']:
        raise click.BadOptionUsage('project', message=PROJECT_PARENT_ERROR_MESSAGE)

    if unknown_params:
        unknown_params = parse_unknown_params(unknown_params)
        kwargs.update(unknown_params)

    base_url = PAGINATED_FILES_LIST_URL.format(limit=ITEMS_PER_SCREEN)
    url = parse_query_params(kwargs, base_url, PROJECT_LIST_REPLACEMENTS)

    click.echo(click.style('Files list:\n', **cntx.obj.get('STYLE')))
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}
    for response, next_page in send_paginated_api_request(url=url, headers=headers):
        for item in response['items']:
            click.echo(json.dumps(item, indent=4))
        if not next_page or \
                not click.confirm(click.style('Load next page of files?', **cntx.obj.get('STYLE')), abort=False):
            break

    file_id = click.prompt(click.style(FILE_PROMPT_MESSAGE, **cntx.obj.get('STYLE')))
    if file_id.lower() == 'exit':
        return

    params = {
        'file': file_id,
        'fields': kwargs.get('fields')
    }
    cntx.params = params
    stat.invoke(cntx)


@files.command()
@click.option('--file', help='File ID.')
@click.option('--fields', help='Subset of fields to include in output. Separate them with coma(no blanks between).',
              default=None)
@click.pass_context
def stat(cntx, file, fields):
    """Outputs details about requested file."""
    # click.echo(f'Getting stats for file: {file}')

    base_url = FILES_DETAIL_URL.format(file_id=file) + ('?' if fields else '')
    url = parse_query_params({'fields': fields}, base_url)
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}
    response = send_api_request(url=url, verb='GET', headers=headers)

    output = FILE_DETAIL_SUCCESS_MESSAGE.format(file_id=file)
    click.echo(click.style(output, **cntx.obj.get('STYLE')))
    click.echo(json.dumps(response, indent=4))


@files.command('update', short_help='Update the name, the full set of metadata, and/or tags for the specified file')
@click.option('--file', help='File ID.')
@click.argument('arguments',
                nargs=-1,
                type=UpdateFileType())
@click.pass_context
def update(cntx, file, arguments):
    """Update the name, the full set of metadata, and/or tags for the specified file.
Arguments are `{key}={value}` pairs(without `--`) of fields to be updated.
Pairs should be separated by whitespace character.
Command accepts multiple `{key}={value} pairs for `metadata` and `tags`.
For nested fields use `.` delimiter in `key` to navigate levels, e.g.: \n
    metadata.some_field="blah blah" or "metadata.some_field=blah blah"  \n
For list values should be inside square brackets, delimited by coma, e.g.: \n
    tags="[new_tag,new-tag2, new tag3]" """

    logger.debug('Updating file: {file}, setting arguments: {arguments}'.format(file=file, arguments=arguments))

    data = cntx.obj.get('update_file_data')

    headers = {
        'X-SBG-Auth-Token': cntx.obj.get('auth_token'),
        'Content-Type': 'application/json'
    }
    response = \
        send_api_request(url=FILES_DETAIL_URL.format(file_id=file), verb='PATCH', headers=headers,
                         data=json.dumps(data))

    output = FILE_UPDATE_SUCCESS_MESSAGE.format(file_id=file)
    click.echo(click.style(output, **cntx.obj.get('STYLE')))
    click.echo(json.dumps(response, indent=4))


@files.command()
@click.option('--file', help='File ID.')
@click.option('--dest', help='Download file path.', type=click.Path())
@click.option('--force', '-f', help="Flag which enables the command to create directory if it doesnt exist.",
              is_flag=True)
@click.pass_context
def download(cntx, file, dest, force):
    url = FILES_DOWNLOAD_URL.format(file_id=file)
    headers = {'X-SBG-Auth-Token': cntx.obj.get('auth_token')}
    response = send_api_request(url=url, verb='GET', headers=headers)
    download_url = response.get('url')

    if not download_url:
        click.echo("Could not retrieve download url!")
        return  # or raise

    if force:
        check_dir(dest)

    with requests.get(download_url, stream=True) as r:
        with open(dest, 'wb') as f:
            file_size, unit = normalize_file_size(int(r.headers['content-length']))
            click.confirm(
                click.style(FILE_DOWNLOAD_PROMPT_MESSAGE.format(size="%.2f" % file_size, unit=unit, file_path=dest),
                            **cntx.obj.get('STYLE')), abort=True)
            with click.progressbar(length=int(r.headers['content-length']), label='Downloading file') as bar:
                for chunk in r.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)
                        bar.update(len(chunk))

    click.echo('Download done!')
