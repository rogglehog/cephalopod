from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship, declarative_base
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
    
    podcast_id = Column(Integer, ForeignKey('podcasts.id'))
    podcast = relationship(Podcast, backref='episodes')

# Create an engine and connect to the database
engine = create_engine('sqlite:///podcasts.db')
Base.metadata.create_all(engine)

# from sqlalchemy.orm import sessionmaker
# from time import time
# Session = sessionmaker(bind=engine)
# session = Session()

# # add podcasts
# session.add(Podcast(
#     name = 'Lanterne Rouge',
#     rss_feed = 'https://anchor.fm/s/1311c8b8/podcast/rss'
# ))
# session.commit()

# # Create posts
# session.add(Episode(
#     title = 'podcast',
#     time = time(),
#     content_url = 'https://pickles.com/content.mp3',
#     podcast = Podcast.query.filter_by(name = podcast).first().id
# ))
# session.commit()

# # Retrieve user's posts
# podcast = session.query(Podcast).filter_by(name='Lanterne Rouge').first()
# print(podcast.name)
# print("Posts:")
# for episode in podcast.episodes:
#     print(f"Title: {episode.title}, Content: {episode.content_url}")
