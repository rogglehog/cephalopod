# CONFIG
# try to read config file

from yaml import safe_load
from os.path import expanduser

config_path = expanduser('~/.config/cephalopod/config.yaml')

def load_config():
    try:
        with open(config_path, 'r') as config:
            return safe_load(config)
    except FileNotFoundError:
        print('No config file found.')

def test_config(key):
    config = load_config()
    try:
        return config['general'][key]
    except KeyError:
        print('Problem reading config.', key, 'missing from ', config_path)

config = load_config()

#DATABASE
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy import create_engine

Base = declarative_base()

class Podcast(Base):
    __tablename__ = 'podcasts'
    id = Column(Integer, primary_key=True)
    name = Column(String(200))
    rss_feed = Column(String(200))

class Episode(Base):
    __tablename__ = 'episodes'
    id = Column(Integer, primary_key=True)
    title = Column(String(200))
    time = Column(Integer)
    content_url = Column(String(200))
    path = Column(String(200))

    podcast_id = Column(Integer, ForeignKey('podcasts.id'))
    podcast = relationship(Podcast, backref='episodes')

# Create an engine and connect to the database
path = expanduser('~/.config/cephalopod/cephalopod.db')
engine = create_engine('sqlite:///' + path)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session=Session()

# SYNC
# three sources of truth for podcasts:
# db, config, and directory tree
# this tries to keep them in sync

from os.path import expanduser, join, exists
from os import listdir, makedirs
from shutil import rmtree
from time import mktime
from feedparser import parse

pod_dir = test_config('podcast_directory')
pod_dir = expanduser(pod_dir)

# check if directory for podcasts exists
def test_pod_dir():
    if not exists(pod_dir):
        makedirs(pod_dir)
        print('Created directory ',pod_dir)

# get list of podcast names from databse
def db_podcasts():
    db = session.query(Podcast).all()
    podcasts = []
    for podcast in db:
        podcasts.append(podcast.name)
    return podcasts

# get list of podcast names from config
def config_podcasts():
    podcasts = []
    for podcast in config['podcasts']:
        podcasts.append(podcast)
    return podcasts

# read config and add missing podcasts to db
def db_import():
    for podcast in config['podcasts']:
        podcast_exists = session.query(Podcast).filter_by(name = podcast).first()
        if podcast_exists:
            pass
        else:
            new_podcast = Podcast(
                name = podcast,
                rss_feed = config['podcasts'][podcast]['rss'],
            )
            session.add(new_podcast)
            session.commit()
            print('Added',podcast,'to database.')


# read config and remove dangling podcasts from db
def db_prune():
    for podcast in db_podcasts():
        if podcast in config_podcasts():
            pass
        else:
            delete_podcast = session.query(Podcast).filter_by(name = podcast).first()
            session.delete(delete_podcast)
            session.commit()
            print('Removed',podcast,'from database.')

# check database and ensure all podcasts have a corresponding directory
def create_directories():
    for podcast in db_podcasts():
        if podcast in listdir(pod_dir):
            pass
        else:
            pth = join(pod_dir,podcast)
            makedirs(pth)
            print('Created directory',pth)

# check databse and remove dangling directories
def prune_directories():
    for podcast in listdir(pod_dir):
        if podcast in db_podcasts():
            pass
        else:
            pth = join(pod_dir,podcast)
            rmtree(pth)
            print('Removed directory',pth)

# check path to downloaded episodes
# null databse entries if user has removed eps manually
def check_local():
    db = session.query(Episode).all()
    for episode in db:
        pth = episode.path
        if pth != None:
            if exists(pth):
                pass
            else:
                update = session.query(Episode).filter_by(id = episode.id).first()
                update.path = None
                session.commit()

def is_duplicate(title, time, url):
    existing_episode = session.query(Episode).filter_by(
        title=title,
        time=time,
        content_url=url
    ).first()
    return existing_episode is not None

# get rss feeds from db
# parse feeds
# check if duplicate
# write episode info to db
def parse_feeds():
    podcasts = session.query(Podcast).all()
    for podcast in podcasts:
        f = parse(podcast.rss_feed)
        for episode in f.entries:

            title = episode.title
            time = mktime(episode.published_parsed)
            url = episode.enclosures[0].href

            new_episode = Episode(
                title = title,
                time = time,
                content_url = url,
                podcast_id = session.query(Podcast).filter_by(name = podcast.name).first().id,
            )

            if is_duplicate(title, time, url):
                pass
            else:
                session.add(new_episode)
                session.commit()
                print('Added', episode.title, 'from', podcast.name, 'to database.')

def update(args):
    test_pod_dir()
    db_import()
    db_prune()
    create_directories()
    prune_directories()
    check_local()
    parse_feeds()

#DOWNLOAD
from requests import get
from os.path import expanduser, join
from time import time, strftime, localtime

def sort_by_age(x):
    return x.time

def download(args):    
    db_eps = session.query(Episode)
    approved_eps = []
    for ep in db_eps:
        # check if filesystem path exists in db
        if ep.path == None:
            # filter old eps
            if ep.time > (time() - (args.a * 86400)):
                approved_eps.append(ep)
        approved_eps.sort(key=sort_by_age,reverse=True)

    for ep in approved_eps:
        content = ep.content_url
        dl = get(content)

        title = ep.title
        date = strftime('%d/%m/%Y', localtime(ep.time))
        podcast = ep.podcast.name

        ep_name = f'{title}.mp3'

        pth = join(pod_dir,ep.podcast.name,ep_name)
        with open(pth, 'wb') as w:
            w.write(dl.content)

        # add ep path to db
        update = session.query(Episode).filter_by(id = ep.id).first()
        update.path = pth
        session.commit()
        print('Downloaded', title, 'from', podcast, 'to', pth)

#STREAM
from time import time, strftime, localtime
from subprocess import Popen, PIPE

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


def stream(args):
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

#PRUNE
# check db for downloaded eps (where path column is not None)
# check if ep time is older than prune age
# remove ep using path, update db

from os import remove
from time import time

def prune(args):
    db_eps = session.query(Episode)
    prune_eps = []
    for ep in db_eps:
        if ep.path != None:
            if ep.time < (time() - (args.a * 86400)):
                prune_eps.append(ep)

    for ep in prune_eps:
        # attempt to remove episode from filesystem
        try:
            remove(ep.path)
        except FileNotFoundError:
            print(ep.title, 'cannot be removed, file does not exist')

        # remove ep path from db 
        update = session.query(Episode).filter_by(id = ep.id).first()
        update.path = None
        session.commit()

        print('Deleted', ep.title, 'from', ep.path)

#ARGS
# load config
# parse args (argparse module)
# call relevant functions

from argparse import ArgumentParser

stream_age = test_config('stream_age')
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
stream_parser = subparsers.add_parser('stream')
stream_parser.add_argument(
    '-a',
    type=int,
    default=stream_age
)
stream_parser.set_defaults(func=stream)

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
prune_parser.set_defaults(func=prune)


args = parser.parse_args()
args.func(args)
