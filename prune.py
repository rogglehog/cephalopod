# check db for downloaded eps (where path column is not None)
# check if ep time is older than prune age
# remove ep using path, update db

from config import load_config
from db import Episode, db_session

from os import remove
from time import time

session = db_session()

def prune_eps(args):
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

        print('Deleted', ep.title)
    
        
    
