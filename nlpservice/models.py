from django.db import models


class Tweeter(models.Model):
    username = models.CharField(max_length=30, primary_key=True)
    source_file = models.CharField(max_length=512)
    model_file = models.CharField(max_length=512)

