#!/usr/bin/env python

import argparse
import time
from syslog import syslog

import boto.ec2


parser = argparse.ArgumentParser()
parser.add_argument("description_prefix",
                    help="prefix for snapshot description")
args = parser.parse_args()

conn = boto.ec2.connect_to_region("us-east-1")
volumns = conn.get_all_volumes()

if volumns:
    volumn = volumns[0]
else:
    msg = "No volumns were found."
    syslog(msg)
    raise Exception(msg)

# all the old snapshots
syslog("Retrieve all snapshots...")
snapshots = conn.get_all_snapshots(owner="self")

syslog("Existing snapshots:")
for snapshot in snapshots:
    syslog("{}: {}".format(snapshot.id, snapshot.tags["Name"]))

now = str(time.time())
now = now.split(".")[0]
name = "{}_{}".format(volumn.id, now)

syslog("Creating new snapshot: {}".format(name))
snapshot = conn.create_snapshot(volumn.id,
                                "{} at {}".format(args.description_prefix,
                                                  time.ctime(float(now))))
snapshot.add_tag("Name", name)

while True:
    # need to manually update status
    snapshot.update()

    if snapshot.status == "completed":
        syslog("Snapshot {} is complete".format(name))
        break

    syslog("Snapshot is under status: {}".format(snapshot.status))
    time.sleep(30)

# delete all the old snapshots
for s in snapshots:
    syslog("Delete old snapshot: {} ({})".format(s.id, s.tags["Name"]))
    conn.delete_snapshot(s.id)
