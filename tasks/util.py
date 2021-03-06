import errno
import os

from invoke import run


REPO_DIRECTORY = os.path.dirname(os.path.dirname(__file__))
DOTFILES_DIRECTORY = os.path.join(REPO_DIRECTORY, 'dotfiles')
RESOURCES_DIRECTORY = os.path.join(REPO_DIRECTORY, 'resources')


def command_exists(command, run=run):
    return run("hash {0}".format(command), warn=True, hide=True).exited == 0


def ensure_path_exists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise
