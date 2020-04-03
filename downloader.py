#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime
import boto3
import os


def getOpts(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="Downloads/Syncs LB access logs for a specific hour (from S3 -> local disk)")
    parser.add_argument("-t", "--time",
        dest="time", help="hour you want to download in for format: 'YYYYMMDD-HH'", required=True)
    parser.add_argument("-l", "--loadbalancer",
        dest="lb", help="loadbalancer name", required=True)
    parser.add_argument("-n", "--dry-run",
        dest='dryrun',action='store_true', help="Dry Run")
    parser.add_argument("-b", "--bucket",
        help="s3 bucket + search path", default="alb-logs-foo")
    parser.add_argument("-p", "--prefix",
        help="prefix (subdir in s3). eg: api-alb/AWSLogs/123123123123/elasticloadbalancing",
        default="api-foo/AWSLogs/123123123123/elasticloadbalancing")
    parser.add_argument("-r", "--region",
        dest="region", help="AWS region", default="us-east-1")
    res = parser.parse_args(args)
    return res

# crude AF
def parseArgTime(input):
    return datetime.strptime(input, '%Y%m%d-%H')


def makeDir(path):
    if os.path.isdir(path):
        print("no need to create dir: {}".format(path))
    else:
        try:
            os.makedirs(path)
        except OSError:
            print("creating directory {} failed".format(path))
        else:
            print("created the directory {}".format(path))


opts = getOpts(sys.argv[1:])

hourDatetime = parseArgTime(opts.time)
year = hourDatetime.strftime("%Y")
month = hourDatetime.strftime("%m")
day = hourDatetime.strftime("%d")
hour = hourDatetime.strftime("%H")
# subdir = "{}/{}/{}/{}".format(opts.region, year, month, day)

cwd = os.getcwd()
localDir = "{}/logs/{}/{}/{}".format(cwd, year, month, day)

if not opts.dryrun:
    makeDir(localDir)


s3 = boto3.resource("s3")
s3Client = boto3.client("s3")
s3Bucket = s3.Bucket(opts.bucket)
objectList = []

prefix = "{}/{}/{}/{}/{}/".format(
    opts.prefix,
    opts.region,
    year,
    month,
    day,
)
print("searching in: s3://{}/{}".format(opts.bucket, prefix))

matchString1 = "elasticloadbalancing_{}".format(opts.region)
matchString2 = "{}{}{}T{}".format(year, month, day, hour)
current_objects = list(s3Bucket.objects.filter(Prefix=prefix))
for i in current_objects:
    objectList.append(i)

print("raw objects to search thru: ", len(current_objects))

matchedObjects = []
for x in objectList:
    objectName = x.key.split("/")[-1]
    if matchString1 in objectName \
        and matchString2 in objectName \
        and opts.lb in objectName:
        matchedObjects.append(x)

print("matched ", len(matchedObjects))
for i in matchedObjects:
    fname = i.key.split("/")[-1]
    fullDest = "{}/{}".format(localDir, fname)

    if not opts.dryrun:
        print("downloading {} -> {}/.".format(fname, localDir))
        s3Client.download_file(opts.bucket, i.key, fullDest)
    else:
        print("DRYRUN: downloading {} -> {}/.".format(fname, localDir))
