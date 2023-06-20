from db import Podcast, Episode, db_session

from time import mktime
from feedparser import parse

session = db_session()

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
def parse_feeds(args):
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
