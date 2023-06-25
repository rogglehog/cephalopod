from sync import update
from dl import download
from prune import prune_eps
from stream import pretty_list
from config import load_config, test_config

from argparse import ArgumentParser

# load config
# parse args (argparse module)
# call relevant functions

config = load_config()

list_age = test_config('list_age')
download_age = test_config('download_age')
prune_age = test_config('prune_age')

parser = ArgumentParser(
    prog='cephalopod',
    description='CLI podcast management tool',
)

subparsers = parser.add_subparsers()

# update
update_parser = subparsers.add_parser('update')
update_parser.set_defaults(func=update)

# stream
list_parser = subparsers.add_parser('stream')
list_parser.add_argument(
    '-a',
    type=int,
    default=list_age
)
list_parser.set_defaults(func=pretty_list)

# download
dl_parser = subparsers.add_parser('download')
dl_parser.add_argument(
    '-a',
    type=int,
    default=download_age
)
dl_parser.set_defaults(func=download)

# prune
prune_parser = subparsers.add_parser('prune')
prune_parser.add_argument(
    '-a',
    type=int,
    default=prune_age
)
prune_parser.set_defaults(func=prune_eps)


args = parser.parse_args()
args.func(args)
