import os
from twitter_helper import download_tweets, generate_tweets_text, log
import logging
import argparse


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true', help='print debug logs')
    subparsers = parser.add_subparsers(dest="command")

    # download args
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("-u", "--users", nargs="+",
                                 help="user names to download and process tweets for")
    download_parser.add_argument("-l", "--limit", type=int, default=10000,
                                 help="limit the number of tweets to download")
    download_parser.add_argument("--data-dir",
                                 help="directory to read/write data from")
    download_parser.add_argument("--exclude-replies", action='store_true',
                                 help="don't even download replies")

    # process args
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument("-u", "--users", nargs="+",
                                help="user names to download and process tweets for")
    process_parser.add_argument("--data-dir",
                                help="directory to read/write data from")

    # model args
    model_parser = subparsers.add_parser("model")
    model_parser.add_argument("-f", "--file", help="input text file")

    return parser.parse_args()


def main():
    args = parse_args()
    log.setup_logging(args.verbose)

    if args.command == 'download':
        download(args.data_dir, args.users, limit=args.limit, exclude_replies=args.exclude_replies)
    elif args.command == 'process':
        process(args.data_dir, args.users)


def download(samples_dir, handles, limit=None, exclude_replies=False):
    for handle in handles:
        raw_file = os.path.join(samples_dir, f'{handle}.raw')
        download_tweets(handle, raw_file, limit=limit, exclude_replies=exclude_replies)


def process(samples_dir, handles):
    for handle in handles:
        raw_file = os.path.join(samples_dir, f'{handle}.raw')
        tweets_file = os.path.join(samples_dir, f'{handle}.tweets.txt')
        replies_file = os.path.join(samples_dir, f'{handle}.replies.txt')
        generate_tweets_text(raw_file, tweets_file, replies_file)


if __name__ == '__main__':
    main()
