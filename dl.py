from config import load_config
from db import Podcast, Episode, db_session

from requests import get
from os.path import expanduser, join
from time import time, strftime, localtime

session = db_session()

config = load_config()
pod_dir = expanduser(config['general']['podcast_directory'])

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
