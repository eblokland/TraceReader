import os
from functools import singledispatch

from parsers.parser_args import ParserArgs


@singledispatch
def get_filename(arg, ext: str, overwrite: bool = False):
    raise TypeError(f'unknown type {type(arg)}')


@get_filename.register
def _get_filename_parserargs(arg: ParserArgs, ext: str, overwrite: bool = False):
    if not ext.startswith('.'):
        ext = f'.{ext}'
    root = arg.output_dir + arg.shared_filename
    return root + ext if overwrite else _get_unique(root, ext)


@get_filename.register
def _get_filename_str(arg: str, ext: str, overwrite: bool = False):
    if not ext.startswith('.'):
        ext = f'.{ext}'
    root = arg.removesuffix(ext)
    return root + ext if overwrite else _get_unique(root, ext)


def _get_unique(root: str, ext: str):
    if not os.path.exists(root + ext):
        return root+ext

    i = 1
    while os.path.exists(f'{root}-{i}{ext}'):
        i += 1

    output_file = f'{root}-{i}{ext}'
    return output_file