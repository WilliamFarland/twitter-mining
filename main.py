import requests
import json
import os
import codecs
import re


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
            'expansions': 'author_id,in_reply_to_user_id,geo.place_id',
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
    def __init__(self, id, text):
        self.id = id

        self.text = re.sub(r"[^a-zA-Z0-9 ]", "", text)

        self.out = json.dumps({
            'text': self.text
        })

    def __str__(self):
        return f'{self.text}'


def main():
    # Tweet Collection
    tweet_data = {}
    # Put keywords here
    keywords = "xbox lang:en"
    bearer_token = os.environ.get('TWITTER-BEARER-TOKEN')
    # Initialize base twitter class
    twitter = TwitterAPI(bearer_token, keywords, max_results=10)
    # Try connecting to endpoint
    json_response = twitter.connect_to_endpoint()

    data = json_response['data']
    for entries in data:
        id = entries['id']
        text = entries['text']
        new_tweet = Tweet(id, text)
        tweet_data[id] = new_tweet

    # print(json.dumps(json_response, indent=4, sort_keys=True))
    with codecs.open("out.txt", 'w', 'utf-8') as outfile:
        for key in tweet_data.keys():

            outfile.write(f'{key}, {tweet_data[key]} \n')


if __name__ == '__main__':
    main()
