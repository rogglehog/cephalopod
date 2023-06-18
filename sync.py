from config import load_config
from db import Podcast, Episode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from os.path import expanduser, join
from os import listdir, makedirs
from shutil import rmtree
from feedparser import parse
from time import time, mktime, strftime, localtime

# three sources of truth for podcasts:
# db, config, and directory tree
# this tries to keep them in sync

engine = create_engine('sqlite:///podcasts.db')
Session = sessionmaker(bind=engine)
session = Session()

config = load_config()
pod_dir = expanduser(config['general']['podcast_directory'])

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
            print('Added podcast',podcast,'to database.')


# read config and remove dangling podcasts from db
def db_prune():
    for podcast in db_podcasts():
        if podcast in config_podcasts():
            pass
        else:
            delete_podcast = session.query(Podcast).filter_by(name = podcast).first()
            session.delete(delete_podcast)
            session.commit()
            print('Removed podcast',podcast,'from database.')

# check database and ensure all podcasts have a corresponding directory
def create_directories():
    for podcast in db_podcasts():
        if podcast in listdir(pod_dir):
            pass
        else:
            makedirs(join(pod_dir,podcast))
            print('Created directory for',podcast)

# check databse and remove dangling directories
def prune_directories():
    for podcast in listdir(pod_dir):
        if podcast in db_podcasts():
            pass
        else:
            rmtree(join(pod_dir,podcast))
            print('Removed directory for',podcast)

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
                local = False
            )

            if is_duplicate(title, time, url):
                pass
            else:
                session.add(new_episode)
                session.commit()
                print('Added', episode.title, 'from', podcast.name, 'to database.')

db_import()
db_prune()
create_directories()
prune_directories()
parse_feeds()
            

        
