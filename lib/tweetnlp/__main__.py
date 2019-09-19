import os
from tweetnlp import download_tweets, generate_tweets_text, log, model
import logging
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='print debug logs')
    subparsers = parser.add_subparsers(dest="command")

    # download args
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("user",
                                 help="user name to download and process tweets for")
    download_parser.add_argument("data_dir",
                                 help="directory to read/write data from")
    download_parser.add_argument("-l", "--limit", type=int, default=10000,
                                 help="limit the number of tweets to download")
    download_parser.add_argument("--exclude-replies", action='store_true',
                                 help="don't even download replies")

    # process args
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("user", help="user name to download and process tweets for")
    process_parser.add_argument("data_dir",
                                help="directory to read/write data from")

    # model args
    model_parser = subparsers.add_parser("model")
    model_parser.add_argument("user", help="input tweets file")
    model_parser.add_argument("data_dir",
                              help="directory to read/write data from")
    model_parser.add_argument('--epochs', type=int, default=50)
    model_parser.add_argument('--pre-trained', action='store_true')

    # tweet args
    tweet_parser = subparsers.add_parser("tweet")
    tweet_parser.add_argument("user", help="input tweets file")
    tweet_parser.add_argument("data_dir",
                              help="directory to read/write data from")
    tweet_parser.add_argument('--pre-trained', action='store_true')

    # predict args
    predict_parser = subparsers.add_parser("predict")
    predict_parser.add_argument("model_file")
    predict_parser.add_argument("tokenizer_file")
    predict_parser.add_argument('--pre-trained', action='store_true')

    return parser.parse_args()


def main():
    args = parse_args()
    log.setup_logging(args.verbose)

    if args.command == 'download':
        raw_file = os.path.join(args.data_dir, 'tweets', f'{args.user}.raw')
        download_tweets(args.user, raw_file, limit=args.limit, exclude_replies=args.exclude_replies)
    elif args.command == 'process':
        raw_file = os.path.join(args.data_dir, 'tweets', f'{args.user}.raw')
        tweets_file = os.path.join(args.data_dir, 'tweets', f'{args.user}.tweets.txt')
        generate_tweets_text(raw_file, tweets_file)
    elif args.command == 'model':
        tweets_file = os.path.join(args.data_dir, 'tweets', f'{args.user}.tweets.txt')
        model_file = os.path.join(args.data_dir, 'models', f'{args.user}.model.hdf5')
        tokenizer_file = os.path.join(args.data_dir, 'models', f'{args.user}.tokenizer')
        model.build_tweet_model(tweets_file, model_file, tokenizer_file, pre_trained_embedding=args.pre_trained,
                                epochs=args.epochs)
    elif args.command == 'tweet':
        model_file = os.path.join(args.data_dir, 'models', f'{args.user}.model.hdf5')
        tokenizer_file = os.path.join(args.data_dir, 'models', f'{args.user}.tokenizer')
        print(model.tweet_from_model(model_file, tokenizer_file, args.pre_trained))
    elif args.command == 'predict':
        model.predict(args.model_file, args.tokenizer_file, args.pre_trained)


if __name__ == '__main__':
    main()
