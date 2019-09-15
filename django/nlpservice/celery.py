import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nlpservice.settings')

app = Celery('nlpservice')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

import tweetnlp.model


@app.task()
def post_create_tasks(username, raw_file, tweets_file, replies_file,  model_file, tokenizer_file):
    from celery import chain
    chain(download.si(username, raw_file),
          generate_tweets_files.si(username, raw_file, tweets_file, replies_file),
          create_model.si(username, tweets_file, model_file, tokenizer_file))()


@app.task()
def download(username, raw_file):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'downloading'
    t.save()
    tweetnlp.download_tweets(username, raw_file, limit=100)
    t.status = 'downloaded'
    t.save()


@app.task()
def generate_tweets_files(username, raw_file, tweets_file, replies_file):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'processing'
    t.save()
    tweetnlp.generate_tweets_text(raw_file, tweets_file, replies_file)
    t.status = 'processed'
    t.save()


@app.task()
def create_model(username, tweets_file, model_file, tokenizer_file):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'modeling'
    t.save()
    tweetnlp.model.build_tweet_model(tweets_file, model_file, tokenizer_file)
    t.status = 'ready'
    t.save()


@app.task()
def generate_tweet(tweet_id, model_file, tokenizer_file):
    from nlptwitter.models import Tweet
    tweet = Tweet.objects.all().get(id=tweet_id)
    tweet.status = 'generating'
    tweet.save()
    text = tweetnlp.model.tweet_from_model(model_file, tokenizer_file)
    tweet.text = text
    tweet.status = 'complete'
    tweet.save()
