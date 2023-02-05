import requests  # library for making api calls
import codecs  # provides access to the internal Python codec registry
import re  # regex library
from set_env import *  # to hide api key from code
import os  # library for interacting w/ os
import time  # use for keeping track of time to api
from datetime import datetime  # use for making out file

# Specify output file here
OUT_FIlE = 'Data/out.txt'
# Put bearer_token here, you could just use plaintext but be careful about leaking it
BEARER_TOKEN = DS501_BEARER_TOKEN
# Put keywords for searching here
KEYWORDS = "optum lang:en"
# Set max results here
MAX_RESULTS = 10


class TwitterAPI:
    """
    Twitter class for connecting to search v2 api, making request, and exporting results
    """
    def __init__(self, token, keyword, max_results):
        # Init bearer token for authorization
        self.bearer_token = token
        # Take token and make it a dict in json format for header auth argument
        self.auth = self.create_auth()
        # Init keywords, and max results
        self.keyword = keyword
        # Init max_results
        self.max_results = max_results
        # Create search url, based on auth, keywords, and any other parameters
        self.search_url, self.query_params = self.create_url()
        # Data holder, default empty before calling api
        self.data = None

    def create_auth(self):
        """
        Init auth header
        """
        auth = {"Authorization": f"Bearer {self.bearer_token}"}
        return auth

    def create_url(self):
        """
        Create base url for query
        :return: url
        """
        search_url = "https://api.twitter.com/2/tweets/search/recent"

        query_params = {
            'query': self.keyword,
            'expansions': 'author_id,in_reply_to_user_id,geo.place_id,referenced_tweets.id',
             }

        return search_url, query_params

    def connect_to_endpoint(self):
        """
        Use above params to connect to endpoint
        :return: Response from twitter endpoint
        """
        response = requests.request("GET", self.search_url, headers=self.auth, params=self.query_params)
        print("Endpoint Response Code: " + str(response.status_code))
        # If request response is not OK code
        if response.status_code != 200:
            raise Exception(response.status_code, response.text)

        self.data = response.json()['data']
        return

    def create_tweets(self):
        tweet_data = {}
        for entries in self.data:
            id = entries['id']
            text = entries['text']
            author_id = entries['author_id']
            referenced_tweets = entries.get('referenced_tweets', None)
            if referenced_tweets:
                referenced_tweets = referenced_tweets[0]['type']
            else:
                referenced_tweets = 'regular tweet'
            new_tweet = Tweet(id, text, author_id, referenced_tweets)
            tweet_data[id] = new_tweet

        return tweet_data


class Tweet:
    """
    Nice little storage class for tweets
    """
    def __init__(self, id, text, author_id, referenced_tweets, reply_user=None):
        # Init Vars
        self.id = id
        self.in_reply_to_user_id = reply_user
        self.author_id = author_id
        self.referenced_tweets = referenced_tweets

        # Modify vars if needed
        self.text = re.sub(r"[^a-zA-Z0-9@ \t]", "", text)

    def __str__(self):
        return f'{self.text}'


def write_to_file(tweet_data):
    """
    Simple func, for writing tweet data to text file
    """
    # check if file exists, if it doesn't create header line
    if not os.path.isfile(OUT_FIlE):
        with codecs.open(OUT_FIlE, 'a', 'utf-8') as outfile:
            outfile.write("key, mined time, author id, tweet type, text\n")

    with codecs.open(OUT_FIlE, 'a', 'utf-8') as outfile:
        for key in tweet_data.keys():

            outfile.write(f'{key}, '
                          f'{datetime.now()}, '
                          f'{tweet_data[key].author_id}, '
                          f'{tweet_data[key].referenced_tweets}, '
                          f'{tweet_data[key].text} \n'
                          )


def main():
    # Initialize base twitter class
    twitter = TwitterAPI(BEARER_TOKEN, KEYWORDS, max_results=MAX_RESULTS)
    # Try getting data
    twitter.connect_to_endpoint()
    # Add data to tweet struct format
    tweet_data = twitter.create_tweets()
    # Write data to out file by calling function
    write_to_file(tweet_data)


if __name__ == '__main__':
    main()
