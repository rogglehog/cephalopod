from config import load_config
from db import Podcast, Episode

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from requests import get
from os.path import expanduser, join
from time import time, strftime, localtime

engine = create_engine('sqlite:///podcasts.db')
Session = sessionmaker(bind=engine)
session = Session()

config = load_config()
pod_dir = expanduser(config['general']['podcast_directory'])
ep_format = config['general']['episode_format']
date_format = config['general']['date_format']

def sort_by_age(x):
    return x.time

def download(age):    
    db_eps = session.query(Episode)
    approved_eps = []
    for ep in db_eps:
        downloaded = session.query(Episode).filter_by(id = ep.id).first().local
        if not downloaded:
            if ep.time > (time() - (age * 86400)):
                approved_eps.append(ep)
        approved_eps.sort(key=sort_by_age,reverse=True)

    for ep in approved_eps:
        content = ep.content_url
        dl = get(content)

        title = ep.title
        date = strftime(date_format, localtime(ep.time))
        podcast = ep.podcast.name

        ep_name = f'{date}.{title}.mp3'

        pth = join(pod_dir,ep.podcast.name,ep_name)
        with open(pth, 'wb') as w:
            w.write(dl.content)

        print('Downloaded', title, 'from', podcast, 'to', pth)

        update = session.query(Episode).filter_by(id = ep.id).first()
        update.local = True
        session.commit()

download(7)
