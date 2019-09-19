from django.db import models


class TweeterModel(models.Model):
    username = models.CharField(max_length=30)
    limit = models.IntegerField(default=10000)
    epochs = models.IntegerField(default=50)
    embedding_dimensions = models.IntegerField(default=25)
    exclude_replies = models.BooleanField(default=True)
    pre_trained_embedding = models.BooleanField(default=False)
    status = models.CharField(max_length=30, default="pending")
    raw_file = models.CharField(max_length=512)
    tweets_file = models.CharField(max_length=512)
    model_file = models.CharField(max_length=512)
    tokenizer_file = models.CharField(max_length=512)


class Tweet(models.Model):
    tweeter = models.ForeignKey(TweeterModel, on_delete=models.CASCADE)
    text = models.CharField(max_length=280, default="")
    status = models.CharField(max_length=30, default="pending")
