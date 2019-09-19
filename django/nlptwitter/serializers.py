from .models import TweeterModel, Tweet
from rest_framework import serializers


class TweeterModelSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TweeterModel
        fields = ['url', 'username', 'status', 'limit', 'epochs', 'embedding_dimensions',
                  'exclude_replies','pre_trained_embedding', 'raw_file', 'tweets_file',
                  'model_file', 'tokenizer_file']
        read_only_fields = ['raw_file', 'tweets_file',
                            'model_file', 'tokenizer_file']


class TweetSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tweet
        fields = ['url', 'tweeter', 'status', 'text']
