import argparse
import pathlib

import boto3

"""
Example usage:

export AWS_ACCESS_KEY_ID=<key_id>
export AWS_SECRET_ACCESS_KEY=<secret_key>
export AWS_DEFAULT_REGION=us-east-1

<<<<<<< HEAD
python main.py --bucket movies-189895028386 --filename ../sample-data/girl-showing-rainbow.mp4 --folder assets
"""

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--filename", help="file to copy", required=True)
    parser.add_argument("--bucket", help="s3 bucket name", required=True)
    parser.add_argument("--folder", help="prefix or 'folder'", default="")
    parser.add_argument("--targetname", help="the new name for the file")
    args = parser.parse_args()

    if not args.targetname:
        args.targetname = pathlib.Path(args.filename).name

    s3 = boto3.client("s3")
    with open(args.filename, "rb") as file:
        s3.upload_fileobj(file, args.bucket, args.folder + "/" + args.targetname)
