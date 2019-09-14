
import os

def test_process_tweets(sample_dir):
    from nlpservice import tweetmodeler
    wrd_input = os.path.join(sample_dir, 'weratedocs.txt')
    rtn = tweetmodeler.process_tweets(wrd_input)
