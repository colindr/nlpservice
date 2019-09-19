import os

from rest_framework import viewsets
from rest_framework import status
from rest_framework.response import Response
from django.conf import settings

from .models import TweeterModel, Tweet
from .serializers import TweeterModelSerializer, TweetSerializer

from nlpservice.celery import post_create_tasks, generate_tweet


class TweeterModelViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = TweeterModel.objects.all()
    serializer_class = TweeterModelSerializer

    def create(self, request, *args, **kwargs):

        data = request.data.copy()
        username = data['username']
        user_path = os.path.join(settings.DATA_ROOT, username)

        try:
            os.mkdir(user_path)
        except FileExistsError:
            pass

        # validate input
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        t = TweeterModel(raw_file=os.path.join(user_path, f'{username}.raw'),
                    tweets_file=os.path.join(user_path, f'{username}.tweets.txt'),
                    model_file=os.path.join(user_path, f'{username}.model.hdf5'),
                    tokenizer_file=os.path.join(user_path, f'{username}.tokenizer'),
                    **serializer.validated_data
                    )

        t.save()

        post_create_tasks.delay(
            t.id,
            t.username,
            t.limit,
            t.epochs,
            t.exclude_replies,
            t.pre_trained_embedding,
            t.raw_file,
            t.tweets_file,
            t.model_file,
            t.tokenizer_file,
        )

        serializer = TweeterModelSerializer(t, context={'request': request})
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class TweetViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer

    def create(self, request, *args, **kwargs):

        # validate input
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        t = serializer.save()

        generate_tweet.delay(t.id, t.tweeter.model_file, t.tweeter.tokenizer_file, t.tweeter.pre_trained_embedding)

        headers = self.get_success_headers(request.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

