# Imports
import monitorTweets as mt
from unshortenit import UnshortenIt
import re 

def analyseTweet(twitterAccount, tweet: str):
    # Link extraction
    unshortener = UnshortenIt()
    blockexplorers = ['polygonscan.com', 'etherscan.io', 'snowtrace', 'bscscan.com']
    regex = re.compile(r"[a-zA-Z]+://t\.co/[A-Za-z0-9]+", re.IGNORECASE)
    for eachWord in regex.finditer(tweet):
        uri = unshortener.unshorten(uri=str(eachWord.group()))
        print(uri)