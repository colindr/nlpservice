from django.db import models


class Tweeter(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    limit = models.IntegerField(default=10000)
    epochs = models.IntegerField(default=50)
    exclude_replies = models.BooleanField(default=True)
    status = models.CharField(max_length=30, default="pending")
    raw_file = models.CharField(max_length=512)
    tweets_file = models.CharField(max_length=512)
    model_file = models.CharField(max_length=512)
    tokenizer_file = models.CharField(max_length=512)


class Tweet(models.Model):
    tweeter = models.ForeignKey(Tweeter, on_delete=models.CASCADE)
    text = models.CharField(max_length=280, default="")
    status = models.CharField(max_length=30, default="pending")
