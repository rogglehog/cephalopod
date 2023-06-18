### CLI podcast management tool written in python

commands:

- sync: parse rss feeds and write episode info to db, also read config and create necssary directories
- list: read episode info from db and print in friendly readable format
- download: get content_url from db, download and write to correct directory
- prune: remove episodes older than certain age
