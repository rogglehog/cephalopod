from config import load_config
from db import Podcast

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from os.path import expanduser, join
from os import listdir, makedirs
from shutil import rmtree

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


db_import()
db_prune()
create_directories()
prune_directories()
            

        
