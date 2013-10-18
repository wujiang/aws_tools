#!/usr/bin/env python

import argparse
from syslog import syslog
from datetime import datetime, timedelta
from boto.s3.connection import S3Connection

parser = argparse.ArgumentParser()
parser.add_argument("bucket", help="bucket name")
parser.add_argument("--days", "-d", type=int, default=7,
                    help="clean files older than how many days (default is 7)")

args = parser.parse_args()

conn = S3Connection()
bucket = conn.get_bucket(args.bucket)

keys_to_delete = []
now = datetime.now()
offset = timedelta(days=args.days)

for key in bucket.get_all_keys():
    last_modified = datetime.strptime(key.last_modified[:19],
                                      "%Y-%m-%dT%H:%M:%S")

    if now - last_modified > offset:
        keys_to_delete.append(key)

results = bucket.delete_keys(keys_to_delete)

syslog("Deleted {} camera snapshots older than {} days"
       .format(len(results.deleted), args.days))


