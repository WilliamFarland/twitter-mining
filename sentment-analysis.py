import pandas as pd
import numpy as np
from nltk.sentiment import SentimentIntensityAnalyzer

"""
Script to read tweets mined by homemade twitter mining script for api v2
After tweets are read, library use to generate sentiment analysis
"""

# Set global vars here
# Path to output file for prev mining script
FILE_PATH = 'Data/out.csv'
# Rename headers, I should have added this to prev. script so it's a fix of my mistake
headers = ['tweet_id', 'data_mined', 'author_id', 'tweet_type', 'retweets', 'replies', 'likes',
           'quotes', 'none', 'data']


def read_data(hed, path_to_csv):
    """
    Reads CSV file into pandas data frame and renames columns to set values.
    :param hed: Headers to rename data for easier manipulation
    :param path_to_csv: Path to CSV file
    :return: Data frame read from pandas csv
    """
    # Map headers to their index for renaming dict format
    cols = {headers.index(col): col for col in hed}
    # Read CSV file into data frame
    df = pd.read_csv(path_to_csv, header=None)
    # Rename columns of data frame to headers defined in global variable
    df = df.rename(columns=cols)
    # Return data frame
    return df


def get_sentiment(frame):
    """
    Takes a data frame and uses NLTK's library sentiment intensity analyzer to get score for each tweet.
    :param frame: Data frame to run sentiment analysis on
    :return: Data frame, w/ 2 new cols, original sentiment score, and threshold sentiment values pos, neutral, negative
    """
    # Init sentiment intensity analyzer
    sia = SentimentIntensityAnalyzer()
    # Run sentiment score, can take a few minutes depending on file size
    frame["sentiment_score"] = frame['data'].apply(lambda x: sia.polarity_scores(x)["compound"] - 0.5)
    # Rename columns to threshold percentages
    frame["sentiment"] = np.select([frame["sentiment_score"] < 0, frame["sentiment_score"] == 0,
                                   frame["sentiment_score"] > 0], ['neg', 'neu', 'pos'])

    return frame


def main():
    # Read data into memory
    data = read_data(headers, FILE_PATH)
    # Defining important cols for filtering in two lines
    important_cols = ['tweet_id', 'data']
    # selecting for cols I care about here, modify as needed
    data = data[important_cols]
    # Get sentiment for each row
    sentiment = get_sentiment(data)
    # Output sentiment data frame to new CSV
    sentiment.to_csv(path_or_buf='Data/sentiment.csv')


if __name__ == '__main__':
    main()
