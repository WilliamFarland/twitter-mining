import requests  # library for making api calls
import json  # library for easy json manipulation
import codecs  # provides access to the internal Python codec registry
import re  # regex library
from set_env import *  # to hide api key from code
import os  # library for interacting w/ os


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

    def create_auth(self):
        """
        Init auth header
        :return: auth header in json/dict format
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

        # Add data to response dict
        return response.json()


class Tweet:
    def __init__(self, id, text, author_id, referenced_tweets, reply_user=None):
        # Init Vars
        self.id = id
        self.in_reply_to_user_id = reply_user
        self.author_id = author_id
        self.referenced_tweets = referenced_tweets

        # Modify vars if needed
        self.text = re.sub(r"[^a-zA-Z0-9@ \t]", "", text)

        # Create out json
        self.out = json.dumps({
            'text': self.text,
            'in_reply_to_user_id': self.in_reply_to_user_id,
            'author_id': self.author_id,

        })

    def __str__(self):
        return f'{self.text}'


def main():
    # Tweet Collection
    tweet_data = {}
    # Put keywords here
    keywords = "healthcare lang:en"
    # Put bearer_token here, you could just use plaintext but be careful about leaking it
    bearer_token = DS501_BEARER_TOKEN
    # Initialize base twitter class
    twitter = TwitterAPI(bearer_token, keywords, max_results=10)
    # Try connecting to endpoint
    json_response = twitter.connect_to_endpoint()

    data = json_response['data']
    for entries in data:
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

    # check if file exists, if it doesn't create header line
    if not os.path.isfile('out.txt'):
        with codecs.open("out.txt", 'a', 'utf-8') as outfile:
            outfile.write("key, author id, in reply to user id, tweet type, text\n")

    with codecs.open("out.txt", 'a', 'utf-8') as outfile:
        for key in tweet_data.keys():

            outfile.write(f'{key}, '
                          f'{tweet_data[key].author_id}, '
                          f'{tweet_data[key].in_reply_to_user_id}, '
                          f'{tweet_data[key].referenced_tweets}, '
                          f'{tweet_data[key].text} \n'
                          )


if __name__ == '__main__':
    main()
