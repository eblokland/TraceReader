import gzip
import pickle
from typing import Dict, Union, Type, Optional

from parsers.parser_args import ParserArgs
from trace_reader_utils.file_utils import get_filename


def gzip_pickle(obj, file_name: Union[str, ParserArgs], overwrite: bool = False):
    if file_name is None:
        raise ValueError(f'need a file path')
    output_file = get_filename(file_name, 'pickle.gz', overwrite)
    with gzip.open(output_file, 'wb') as pickle_file:
        pickle.dump(obj, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)


# will use the file extension to determine whether to use gzip or regular pickle
def gzip_unpickle(input_file: str):
    if input_file.endswith('.gz'):
        with gzip.open(input_file, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    elif input_file.endswith('.pickle'):
        with open(input_file, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    else:
        return None


def get_dict_from_pickle(input_file: str) -> Dict:
    obj = gzip_unpickle(input_file)
    if obj is None:
        raise ValueError(f'File not found or invalid file')
    if not isinstance(obj, Dict):
        raise TypeError(f'Pickle does not contain a dict')
    return obj

