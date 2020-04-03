#!/usr/bin/env python3
import ciso8601
import re


def parseLine(line):
    fields = [
        "type",
        "timestamp",
        "alb",
        "client_ip",
        "client_port",
        "backend_ip",
        "backend_port",
        "request_processing_time",
        "backend_processing_time",
        "response_processing_time",
        "lb_status_code",
        "backend_status_code",
        "received_bytes",
        "sent_bytes",
        "request_verb",
        "request_url",
        "request_proto",
        "user_agent",
        "ssl_cipher",
        "ssl_protocol",
        "target_group_arn",
        "trace_id",
        "domain_name",
        "chosen_cert_arn",
        "matched_rule_priority",
        "request_creation_time",
        "actions_executed",
        "redirect_url",
        "last_field",
    ]
    # credit: https://gist.github.com/jweyrich/8d53a7bf5bad7b5958423cb4e538ab20
    regex = r"([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" ($|\"[^ ]*\")(.*)"

    matches = re.search(regex, line)
    res = {}
    if matches:
        for i, field in enumerate(fields):
            value = matches.group(i+1)
            if field == "timestamp":
                res['timestamp'] = ciso8601.parse_datetime(value)
                continue

            if field == "redirect_url":
                value = value.replace('"', '')
                continue

            if field == "last_field":
                res['error_reason'] = value.split('"')[1]
                res['target_ip'] = value.split('"')[3].split(":")[0]
                res['target_port'] = value.split('"')[3].split(":")[1]
                res['target_status_code_list'] = str(value.split('"')[5])
                continue

            res[field] = value

    return res
