import os
from twitter_helper import download_tweets, generate_tweets_text
import logging
import argparse


def parse_args():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(dest="command")
    download_parser = subparsers.add_parser("download")
    download_parser.add_argument('-u', '--users', nargs="+", help="usernames to download and process tweets for")
    download_parser.add_argument("--data-dir", help="directory to read/write data from")
    download_parser.add_argument("--exclude-replies", action='store_true', help="don't even download replies")
    process_parser = subparsers.add_parser("process")
    process_parser.add_argument('-u', '--users', nargs="+", help="usernames to download and process tweets for")
    process_parser.add_argument("--data-dir", help="directory to read/write data from")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.command == 'download':
        download(args.data_dir, args.users)
    elif args.command == 'process':
        process(args.data_dir, args.users)


def download(samples_dir, handles):
    for handle in handles:
        raw_file = os.path.join(samples_dir, f'{handle}.raw')
        download_tweets(handle, raw_file, 10000)


def process(samples_dir, handles):
    for handle in handles:
        raw_file = os.path.join(samples_dir, f'{handle}.raw')
        tweets_file = os.path.join(samples_dir, f'{handle}.tweets.txt')
        replies_file = os.path.join(samples_dir, f'{handle}.replies.txt')
        generate_tweets_text(raw_file, tweets_file, replies_file)


if __name__ == '__main__':
    main()
