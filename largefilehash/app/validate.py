from .providers import PathProvider


def validate_path(path: str, path_provider=PathProvider()):
    if not path_provider.is_file(path):
        raise Exception(f'Could not find file at specified path: {path}')


def validate_thread_count(number_of_threads: int):
    if number_of_threads <= 0 or number_of_threads > 12:
        raise Exception(f'Number of threads must be greater than 0 and less than 12')
