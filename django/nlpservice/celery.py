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
def post_create_tasks(username, limit, epochs, exclude_replies, raw_file, tweets_file,
                      model_file, tokenizer_file, do_download=True):
    from celery import chain
    tasks = []
    if do_download:
        tasks += [download.si(username, raw_file, limit, exclude_replies)]

    tasks += [generate_tweets_files.si(username, raw_file, tweets_file),
              create_model.si(username, tweets_file, model_file, tokenizer_file, epochs)]

    chain(*tasks)()


@app.task()
def download(username, raw_file, limit, exclude_replies):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'downloading'
    t.save()
    tweetnlp.download_tweets(username, raw_file, limit=limit, exclude_replies=exclude_replies)
    t.status = 'downloaded'
    t.save()

    send_to_elasticsearch(raw_file)


@app.task()
def generate_tweets_files(username, raw_file, tweets_file):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'processing'
    t.save()
    tweetnlp.generate_tweets_text(raw_file, tweets_file)
    t.status = 'processed'
    t.save()


@app.task()
def create_model(username, tweets_file, model_file, tokenizer_file, epochs):
    from nlptwitter.models import Tweeter
    t = Tweeter.objects.all().get(username=username)
    t.status = 'modeling'
    t.save()
    tweetnlp.model.build_tweet_model(tweets_file, model_file, tokenizer_file, epochs)
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


def send_to_elasticsearch(raw_file):
    from django.conf import settings
    import redis

    r = redis.Redis(host=settings.NLPSERVICE_REDIS_HOST, port=int(settings.NLPSERVICE_REDIS_PORT))
    key = os.getenv('NLPSERVICE_REDIS_TWEETS_QUEUE_KEY')
    with open(raw_file, 'r') as fp:
        line = fp.readline()
        while line:
            r.rpush(key, line)
            line = fp.readline()
