from db import Episode, db_session
from config import load_config, test_config

from time import time, strftime, localtime
from subprocess import Popen, PIPE

session = db_session()

config = load_config()

player = test_config('media_player')

# query db for episodes
# filter for age (in days)
# orde by age
# print info

def sort_by_age(x):
    return x.time

def fiddle_input(inp):
    try:
        inp = int(inp)
    except ValueError:
        print('Invalid input')
        exit()

    return inp - 1


def main(args):
    db_eps = session.query(Episode)
    approved_eps = []
    for ep in db_eps:
        if ep.time > (time() - (args.a * 86400)):
            approved_eps.append(ep)
    approved_eps.sort(key=sort_by_age,reverse=True)

    for count, ep in enumerate(approved_eps):
        title = ep.title
        podcast = ep.podcast.name
        date = strftime('%d/%m/%Y', localtime(ep.time))
        print(f'[{count + 1}] {title} | {podcast} | {date}')

    # get user choice, handle weird input
    inp = input('\nSelect episode. 1,2,3 etc. ')
    inp = fiddle_input(inp)
    try:
        url = approved_eps[inp].content_url
    except KeyError:
        print('Invalid input')
        exit()
    cmd = [ player, url ]
    process = Popen(cmd, stdout=PIPE)
    exit()
