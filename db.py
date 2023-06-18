from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
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
    path = Column(String(200))
    
    podcast_id = Column(Integer, ForeignKey('podcasts.id'))
    podcast = relationship(Podcast, backref='episodes')

# Create an engine and connect to the database
engine = create_engine('sqlite:///podcasts.db')
Base.metadata.create_all(engine)
