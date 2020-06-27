import click
from .src.launcher import hash_file
from .src.validate import validate_path, validate_thread_count


@click.command()
@click.argument('path')
@click.option('--threads', default=1, help='The number of threads to use to hash the file')
def main(path, threads):
    '''
    path : str : the absolute or relative path to the file to hash
    '''
    try:
        validate_path(path)
        validate_thread_count(threads)
    except Exception as e:
        print(str(e))

    hash_file(threads, path)


if __name__ == '__main__':
    main()
