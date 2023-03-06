import pickle
import gzip

from parser_args import ParserArgs


def gzip_pickle(obj, args: ParserArgs = None, output_file=None):
    if args is not None:
        output_file = args.output_dir + args.shared_filename + '.pickle.gz'
    elif output_file is None:
        raise ValueError('Need one of args or output file')
    with gzip.open(output_file, 'wb') as pickle_file:
        pickle.dump(obj, pickle_file, protocol=pickle.HIGHEST_PROTOCOL)

#will use the file extension to determine whether to use gzip or regular pickle
def gzip_unpickle(input_file: str):
    if input_file.endswith('.gz'):
        with gzip.open(input_file, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    elif input_file.endswith('.pickle'):
        with open(input_file, 'rb') as pickle_file:
            return pickle.load(pickle_file)
    else:
        return None