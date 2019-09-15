from .models import Tweeter, Tweet
from rest_framework import serializers


class TweeterSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweeter
        fields = ['url', 'username', 'status', 'limit', 'epochs', 'exclude_replies',
                  'raw_file', 'tweets_file', 'model_file', 'tokenizer_file']
        read_only_fields = ['raw_file', 'tweets_file',
                            'model_file', 'tokenizer_file']


class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = ['url', 'tweeter', 'status', 'text']
