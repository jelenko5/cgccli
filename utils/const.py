
DICT_KEY_STANDARD_LEN = 25

ITEMS_PER_SCREEN = 15  # TODO: this should be set in `config` command

DOWNLOAD_CHUNK_SIZE = 8192

STYLE = {
            'fg': 'red',
            'bold': True,
            'underline': True
        }

DEBUG_STYLE = {
        'fg': 'green',
        'bold': True,
        'underline': True
    }

# ============================================ Files consts: ==================================================

PROJECT_PARENT_ERROR_MESSAGE = """`project` should not be used together with `parent`. 
If parent is used, the call will list the content of the specified folder, within the project to which the folder 
belongs. If project is used, the call will list the content at the root of the project's files."""

FILE_DETAIL_SUCCESS_MESSAGE = '\nDetails for selected file(ID: {file_id}):\n'
FILE_DETAIL_FAILURE_MESSAGE = '\nSorry! Looks like file (ID: {file_id}) doesnt exist. Please try again.\n'
FILE_PROMPT_MESSAGE = '\nInsert `file_id` for file details or `exit` to abort'
FILE_UPDATE_SUCCESS_MESSAGE = '\nDetails for updated file(ID: {file_id}):\n'
FILE_DOWNLOAD_PROMPT_MESSAGE = '\nDownload is ready. Are you sure you want to download {size}{unit} of data to ' \
                               'file {file_path}'

PROJECT_LIST_REPLACEMENTS = {
    'origin_task': 'origin.task',
    'origin_dataset': 'origin.dataset'
}


# ============================================ Projects consts: ==================================================

PROJECT_DETAIL_SUCCESS_MESSAGE = '\nDetails for selected project(ID: {project_id}):\n'
PROJECT_DETAIL_FAILURE_MESSAGE = '\nSorry! Looks like project (ID: {project_id}) doesnt exist. Please try again.\n'
PROJECT_PROMPT_MESSAGE = '\nInsert `project_id` for project details or `exit` to abort'
