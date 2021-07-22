#!/usr/bin/python3
import argparse
import time
import urllib.request
import sys


def printnow(s):
    sys.stdout.write(s)
    sys.stdout.flush()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('host')
    parser.add_argument('port', nargs='?', default=80)
    args = parser.parse_args()
    path = f'http://{args.host}:{args.port}'
    while True:
        try:
            with urllib.request.urlopen(path) as r:
                if 200 <= r.status < 300:
                    print(f"{path} is live!")
                    break
        except Exception as he:
            print(f"Waiting for {path} to start.")
            time.sleep(2)
