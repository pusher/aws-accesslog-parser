#!/usr/bin/env python3

import gzip
import ciso8601
# from datetime import datetime, date
import sys
import argparse
from elasticsearch import helpers
import es
import parse
from tqdm import tqdm

def getOpts(args=sys.argv[1:]):
    parser = argparse.ArgumentParser(
        description="munches a aws log file into elasticsearch")
    parser.add_argument("-f", "--file",
        dest="file", help="(relative) path to the file to munch", required=True)
    res = parser.parse_args(args)
    return res




def parseAccessLog(line):
    """
    processes a single log line and returns a k/v dict of objects
    REF: https://docs.aws.amazon.com/elasticloadbalancing/latest/application/load-balancer-access-logs.html
    """
    # TODO.. check some sample log files and ensure we can rely on space splitting being consistent
    # print(line.split(" ")[19:-1])
    spaceSplit = line.split(" ")
    spaceCount = len(spaceSplit)
    extraSpaces = spaceCount - 29  # typically there are 29 (no spaces in useragent/URL.. TODO.. use regex?)
    lb_type = spaceSplit[0]
    timestamp = ciso8601.parse_datetime(spaceSplit[1])
    elb = spaceSplit[2] #TODO optional: extract the TG
    client_ip = spaceSplit[3].split(":")[0]
    client_port = spaceSplit[3].split(":")[1]
    target_ip = spaceSplit[4].split(":")[0]
    target_port = spaceSplit[4].split(":")[1]
    request_processing_time = spaceSplit[5]   # in sec with ms precision
    target_processing_time = spaceSplit[6]    # in sec with ms precision
    response_processing_time = spaceSplit[7]  # in sec with ms precision
    elb_status_code = spaceSplit[8]
    target_status_code = spaceSplit[9]
    received_bytes = spaceSplit[10]
    sent_bytes = int(spaceSplit[11])
    requestRaw = line.split('"')[1]
    method = requestRaw.split(" ")[0]
    url = requestRaw.split(" ")[1]
    # uaRaw = line.split('"')[3+extraSpaces]
    ssl_cipher = spaceSplit[16+extraSpaces]
    ssl_protocol = spaceSplit[17+extraSpaces]
    target_group_arn = spaceSplit[18+extraSpaces] # TODO: split maybe arn:aws:elasticloadbalancing:us-east-1:008815156580:targetgroup/api-gateway-mt1/203ecbef7fb8612b
    trace_id = spaceSplit[19+extraSpaces]
    domain_name = spaceSplit[20+extraSpaces]
    chosen_cert_arn = spaceSplit[21+extraSpaces]
    matched_rule_priority = spaceSplit[22+extraSpaces]
    request_creation_time = spaceSplit[23+extraSpaces]
    actions_executed = spaceSplit[24+extraSpaces]
    redirect_url = spaceSplit[25+extraSpaces]
    error_reason = spaceSplit[26+extraSpaces]
    targetIP = spaceSplit[27+extraSpaces].split(":")[0]
    targetPort = spaceSplit[27+extraSpaces].split(":")[1]
    target_status_code_list = spaceSplit[28+extraSpaces]

    res = {
        "ts": timestamp,
        "lb_type": lb_type,
        "timestamp": timestamp,
        "elb": elb,
        "client_ip": client_ip,
        "client_port": client_port,
        "target_ip": target_ip,
        "target_port": target_port,
        "request_processing_time": request_processing_time,
        "target_processing_time": target_processing_time,
        "response_processing_time": response_processing_time,
        "elb_status_code": elb_status_code,
        "target_status_code": target_status_code,
        "received_bytes": received_bytes,
        "sent_bytes": sent_bytes,
        "method": method,
        "url": url,
        # "uaRaw": uaRaw,
        "ssl_cipher": ssl_cipher,
        "ssl_protocol": ssl_protocol,
        "target_group_arn": target_group_arn,
        "trace_id": trace_id,
        "domain_name": domain_name,
        "chosen_cert_arn": chosen_cert_arn,
        "matched_rule_priority": matched_rule_priority,
        "request_creation_time": request_creation_time,
        "actions_executed": actions_executed,
        "redirect_url": redirect_url,
        "error_reason": error_reason,
        "targetIP": targetIP,
        "targetPort": targetPort,
        "target_status_code_list": target_status_code_list,
    }
    return res

def countLinesInGzippedFile(gzipedFileName):
    with gzip.open(gzipedFileName, "rt") as fh:
        count = 0
        for x in fh:
            count += 1
    # print(gzipedFileName, "has", count, "lines")
    return count


def flushToElastic(elastic, inputList):
    # print("flushing", len(inputList), "objects")
    try:
        # make the bulk call, and get a response
        response = helpers.bulk(elastic, inputList)
        # print("RESPONSE:", response)
    except Exception as e:
        print("ERROR:", e)


def prepForBulk(prefixName, body):
    # https://elasticsearch-py.readthedocs.io/en/master/helpers.html

    iso_time = body['timestamp'].isoformat()
    timeYear = body['timestamp'].strftime('%Y')
    timeMonth = body['timestamp'].strftime('%m')
    timeDay = body['timestamp'].strftime('%d')
    del body['timestamp']
    # del body['ts']
    indexName = "{}-{}.{}.{}".format(
            prefixName,
            timeYear,
            timeMonth,
            timeDay,
        )
    # hashMe = "{}-{}".format(iso_time, body)

    id = es.predicablehash(iso_time, body['trace_id'])  # TODO: make this useful and hash specific data
    result = {
        '_index': indexName,
        '_type': 'document',
        '_id': id,
        "@timestamp": iso_time,
        **body
    }
    return result


if __name__ == "__main__":

    opts = getOpts(sys.argv[1:])
    esConn = es.newElasticConnect()
    file = opts.file
    print("processing: {}".format(file))

    # TODO exclude list can possibly be a comma seperated arg
    excludeList = [
        "200",
        "202",
        "400",
        "401",
        "403",
        "404",
        "413",
        "460", # This error occurs when the load balancer received a request from a client, but the client closed the connection with the load balancer before the idle timeout period elapses.
    ]

    # these four are crucial to the loop
    buf = []
    flushFreq = 1000
    lineNumber = 0
    lineCountTotal = countLinesInGzippedFile(file)
    #################################################
    to_write = 0


    pbar = tqdm(total=lineCountTotal)


    with gzip.open(file, "rt") as fh:
        for line in fh:
            lineNumber += 1
            pbar.update(1)

            ## before doing a full parse.. quickly check for the status code so we can only do a full parse on lines we care about
            quickCheckElbStatus  = line.split(" ")[8]

            if quickCheckElbStatus not in str(excludeList):
                to_write += 1
                x = parse.parseLine(line)
                y = prepForBulk("foo", x)
                buf.append(y)

            # on the final line of the file (or when buffer is filled)
            if len(buf) % flushFreq == 0 or lineNumber == lineCountTotal:
            # if lineNumber % flushFreq == 0 or lineNumber == lineCountTotal:
                if len(buf) > 0:
                    # print(len(buf))
                    # print(lineNumber)
                    flushToElastic(esConn, buf)
                buf = []

    # print("done searching.. total matches: ", to_write)
    pbar.close()
