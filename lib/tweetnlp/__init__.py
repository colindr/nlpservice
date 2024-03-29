import twitter
import json
import logging

from . import utils

logger = logging.getLogger(__name__)


def download_tweets(username: str, output_file: str, limit: int = None, exclude_replies: bool = False):
    """
    Download up to `limit` tweets from twitter user `username`. Then
    save to the supplied output path.

    :param username: twitter screen_name to donwload tweets from
    :param output_file: file to write the raw data to
    :param limit: optionally limit the number of tweets to download
    :param exclude_replies: whether or not to exclude replies
    """
    creds = utils.creds()

    with open(output_file, 'w') as fp:

        # connect to twitter API
        api = twitter.Api(**creds, tweet_mode='extended', sleep_on_rate_limit=True)

        earliest_tweet = None
        count = 0

        while limit is None or count < limit:
            # get 200 tweets at a time
            logger.info(f"getting tweets before: {earliest_tweet}")
            all_tweets = api.GetUserTimeline(
                screen_name=username, max_id=earliest_tweet, count=200,
                exclude_replies=False, trim_user=True,
            )

            new_earliest = min(all_tweets, key=lambda x: x.id).id

            if exclude_replies:
                tweets = [t for t in all_tweets if not t.in_reply_to_screen_name]
            else:
                tweets = all_tweets

            count += len(tweets)

            # if we haven't gotten any tweets, or the new tweets are the same
            # as the old, break
            if not all_tweets or new_earliest == earliest_tweet:
                logger.info(f'count: {count} tweetlen:{len(all_tweets)} new_earliest:{new_earliest} earliest:{earliest_tweet}')
                break
            else:
                # write the tweets separated by newlines
                fp.write('\n'.join([json.dumps(t.AsDict()) for t in tweets]) + '\n')
                earliest_tweet = new_earliest


def generate_tweets_text(raw_file: str, tweet_text_file: str):
    """
    The raw file format is a series of lines  of json, so we load the raw_file
    line-by-line, decode the json, read the fields we care about, and write out
    two separate files; one that contains the full text of all tweets, the other
    that contains the full text of all replies.

    We also do some pre-processing of the full_text to remove some junk, which
    calls the clean_tweet_text function.

    :param raw_file:
    :param tweet_text_file:
    """

    with open(raw_file, 'r') as raw_fp:
        with open(tweet_text_file, 'w') as tweet_fp:
            line = raw_fp.readline()
            while line:
                if not line.strip():
                    line = raw_fp.readline()
                    continue

                data = json.loads(line.strip())

                logger.debug(data)
                # full_text only exists if you instantiate your twitter
                # connection with the tweet_mode='extended'
                full_text = data.get('full_text') or data.get('text')
                full_text = clean_tweet_text(full_text)
                tweet_fp.write(full_text + '\n')
                line = raw_fp.readline()


def clean_tweet_text(text: str) -> str:
    """
    Return a cleaned version of text where we:
      - removing urls
      - removing mentions

    :param text:
    :return:
    """

    words = text.split()
    goodwords = []
    for word in words:
        if word.startswith('http'):
            continue
        if word.startswith('@'):
            continue

        goodwords.append(word)
    return ' '.join(goodwords)
