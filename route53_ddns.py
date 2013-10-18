#!/usr/bin/env python

import argparse
import os
import urllib2

import boto
from boto.route53.record import ResourceRecordSets

parser = argparse.ArgumentParser()
parser.add_argument("zoneid", help="Route 53 Zone ID")
parser.add_argument("ip_keeper", help="A file to keep the old IP record")
parser.add_argument("ip_echo_host", help="IP echo host url")
parser.add_argument("domain", help="Name of the domain you want to change")

args = parser.parse_args()


def change_record(conn, hosted_zone_id, name, type, values, ttl=600):
    """Delete and then add a record to a zone"""

    changes = ResourceRecordSets(conn, hosted_zone_id)
    response = conn.get_all_rrsets(hosted_zone_id, type, name, maxitems=1)[0]
    change1 = changes.add_change("DELETE", name, type, response.ttl)
    for old_value in response.resource_records:
        change1.add_value(old_value)
    change2 = changes.add_change("CREATE", name, type, ttl)
    for new_value in values.split(','):
        change2.add_value(new_value)
    print changes.commit()

# connection
conn = boto.connect_route53()

changes = ResourceRecordSets(conn, args.zoneid)

try:
    url = urllib2.urlopen(args.ip_echo_host)
    ip = url.readline()
    ip = ip.strip()
except:
    print "{} seems to be down.".format(args.ip_echo_host)
    exit(1)

with open(args.ip_keeper, "r+") as ip_keeper:
    old_ip = ip_keeper.readline()
    if old_ip:
        old_ip = old_ip.strip()

    if old_ip != ip:
        change_record(conn, args.zoneid, args.domain, "A", ip, ttl=60)
        ip_keeper.write(ip)

