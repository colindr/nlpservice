# Generated by Django 2.2.5 on 2019-09-15 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweeter',
            fields=[
                ('username', models.CharField(max_length=30, primary_key=True, serialize=False)),
                ('raw_file', models.CharField(max_length=512)),
                ('tweets_file', models.CharField(max_length=512)),
                ('replies_file', models.CharField(max_length=512)),
                ('model_file', models.CharField(max_length=512)),
                ('tokenizer_file', models.CharField(max_length=512)),
            ],
        ),
    ]