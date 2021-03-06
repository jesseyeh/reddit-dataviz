import praw
import re

import config 

def get_reddit_instance():
    return praw.Reddit(client_id=config.client_id,
                       client_secret=config.client_secret,
                       username=config.reddit_username,
                       password=config.reddit_password,
                       user_agent="Reddit DavaViz App by /u/devjyeh")

def get_subreddit_instance(subreddit_name):
    reddit = get_reddit_instance()
    return reddit.subreddit(subreddit_name)

def get_posts(subreddit_name, limit=None, time_filter="year"):
    subreddit = get_subreddit_instance(subreddit_name)
    return list(subreddit.top(limit=limit, time_filter=time_filter))

def is_valid_subreddit_name(subreddit_name):
    match = re.search(r"\A^[A-Za-z0-9][A-Za-z0-9_]{1,20}\Z", subreddit_name)
    if match:
        return True
    return False
