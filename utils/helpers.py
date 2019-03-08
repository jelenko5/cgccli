import os
import re
import urllib

import click
import requests

from cli_exceptions import BadAPIResponse
from utils import logger
from utils.const import DICT_KEY_STANDARD_LEN, STYLE, DEBUG_STYLE


# ===================================== API REQUEST HELPERS: =============================================


def send_api_request(url, verb, data=None, headers={}):
    """Send request and do basic check of response status code. Raise exception if bad response."""

    logger.debug('Sending {verb} request to url: {url}'.format(verb=verb, url=url))
    logger.debug('Data: {data}'.format(data=data))

    response = requests.request(verb, headers=headers, url=url, data=data)
    logger.debug('Got response code: {code}'.format(code=response.status_code))
    if response:  # response.status_code == 2xx
        return response.json()

    response = response.json()
    raise BadAPIResponse(response, error_code=response.get('code'))


def get_next_page_link(links):
    for l in links:
        if l.get('rel') == 'next':
            return l.get('href')
    return None


def send_paginated_api_request(url, verb='GET', headers={}):
    """Send request, yield response and send request for the next page(if exists)"""
    response = send_api_request(url=url, verb=verb, headers=headers)
    next_page = True

    while 'links' in response.keys() and next_page:
        next_page = get_next_page_link(response.get('links'))
        yield response, next_page
        if next_page:
            logger.debug('Sending next page request: {url}'.format(url=next_page))
            response = send_api_request(url=next_page, verb=verb, headers=headers)


def normalize_query_params(param_name, value, replacements=None):
    """Turns `True`->`true`, `False`->`false` and replaces param name if needed."""
    if replacements and param_name in replacements.keys():
        param_name = replacements[param_name]

    return param_name, 'true' if value == True else 'false' if value == False else value


def parse_query_params(query_params, base_url, replacements=None):
    """Creates request url by appending `&key=value` pairs from :param:query_params to :param:base_url"""

    logger.debug('Parsing query params')
    for key, value in query_params.items():
        if value is not None:  # Allows `False`/`True` values, ignores `None`
            if isinstance(value, tuple):
                for v in value:
                    key, v = normalize_query_params(param_name=key, value=v, replacements=replacements)
                    base_url += '&{}={}'.format(urllib.parse.quote_plus(key), urllib.parse.quote_plus(v))
            else:
                key, value = normalize_query_params(param_name=key, value=value, replacements=replacements)
                base_url += '&{}={}'.format(urllib.parse.quote_plus(key), urllib.parse.quote_plus(value))

    return base_url


# ===================================== CONFIG HELPERS: =============================================

def check_auth_token(cntx, token):
    logger.debug('Checking auth for token: {token}'.format(token=token))

    # TODO: maybe some request to check if token is valid
    cntx.ensure_object(dict)

    cntx.obj['auth_token'] = token


def set_debug(debug):
    """Enable debug messages."""
    if debug:
        logger.enable_debug()


def set_color(cntx, no_color):
    """Set style components in context.object if style is allowed"""
    cntx.ensure_object(dict)
    style = STYLE
    debug_style = DEBUG_STYLE

    if no_color:
        style = dict()
        debug_style = dict()

    cntx.obj['STYLE'] = style
    logger.set_debug_style(debug_style)

    logger.debug('Style set.')


# ===================================== PARSE INPUT/OUTPUT HELPERS: =============================================

def parse_unknown_params(params):
    """Purpose of this function is to parse multiple `--metadata.{field}=value` arguments.
    :arg:params: tuple of unknown params
    """

    structured_params = dict()
    for param in params:
        param = param.strip('--')
        key, value = param.split('=')
        if key in structured_params.keys():
            structured_params[key] = structured_params[key] + (value,)
        else:
            structured_params[key] = (value,)

    return structured_params


def format_dict(data):
    """Helper func for creating structured output out of `dict`"""
    output = str()
    for k, v in data.items():
        output += '{key} {dots}: {value}'.format(key=k, value=v, dots='.'*(DICT_KEY_STANDARD_LEN-len(k))) + '\n'

    return output


def normalize_file_size(size):
    """Turns bytes to KB, MB, GB or TB"""
    step = 1000  # Recommended by the International System of Units(SI). Also Linux uses it,so I just went with the flow
    scale = ['', 'K', 'M', 'G', 'T']
    n = 0
    while size > step:
        size /= step
        n += 1
    return size, scale[n] + 'B'


class UpdateFileType(click.ParamType):
    """Custom param type for handling update file data."""

    name = 'update_file_type'
    UPDATE_ARGUMENTS_ERROR_MESSAGE = """
Arguments are `{key}={value}` pairs of fields to be updated. Pairs should be separated by whitespace character. 
Command accepts multiple `{key}={value} pairs for `metadata` and `tags`.
For nested fields use `.` delimiter in `key` to navigate levels, e.g.: \n 
    metadata.some_field="blah blah" or "metadata.some_field=blah blah"  \n  
For list values should be inside square brackets, delimited by coma, e.g.: \n
    tags="[new_tag,new-tag2, new tag3]" """

    def convert(self, arg, param, ctx):
        data = ctx.obj['update_file_data']
        if not '=' in arg:
            raise click.BadArgumentUsage(message=self.UPDATE_ARGUMENTS_ERROR_MESSAGE)
        key, value = arg.split('=')
        if '.' in key:  # metadata
            metadata_field, subfield = key.split('.')
            if metadata_field != 'metadata':
                raise click.BadArgumentUsage(message=self.UPDATE_ARGUMENTS_ERROR_MESSAGE)

            if 'metadata' in data.keys():
                data['metadata'].update({subfield: value})
            else:
                data['metadata'] = {subfield: value}

        elif re.match(r'\[([A-Za-z1-9 _-]+,*)+\]', value) and key == 'tags':  # tags
            tags_list = value.strip('[').strip(']').split(',')
            for t in tags_list:
                t.strip()
            if 'tags' in data.keys():
                data['tags'].update(tags_list)
            else:
                data['tags'] = tags_list

        elif key == 'name':  # name
            data['name'] = value

        else:
            raise click.BadArgumentUsage(message=self.UPDATE_ARGUMENTS_ERROR_MESSAGE)


def check_dir(path):
    directory, file = os.path.split(path)
    if not os.path.isdir("/home/el"):
        os.mkdir(directory)
