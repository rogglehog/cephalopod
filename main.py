from parse import parse_feeds
from dl import download
from prune import prune_eps
from list import pretty_list

from argparse import ArgumentParser

# load config
# parse args (argparse module)
# call relevant functions

parser = ArgumentParser(
    prog='cephalopod',
    description='CLI podcast management tool',
)

subparsers = parser.add_subparsers()

# update
update_parser = subparsers.add_parser('update')
update_parser.set_defaults(func=parse_feeds)

# list
list_parser = subparsers.add_parser('list')
list_parser.add_argument(
    '-a',
    type=int,
    default=7
)
list_parser.set_defaults(func=pretty_list)

# download
dl_parser = subparsers.add_parser('download')
dl_parser.add_argument(
    '-a',
    type=int,
    default=7
)
dl_parser.set_defaults(func=download)

# prune
prune_parser = subparsers.add_parser('prune')
prune_parser.add_argument(
    '-a',
    type=int,
    default=7
)
prune_parser.set_defaults(func=prune_eps)

args = parser.parse_args()
args.func(args)
