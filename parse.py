#!/usr/bin/env python3

import re


def parse_line(line):
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
        "alb_status_code",
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
        "new_field",
    ]
    # Note: for Python 2.7 compatibility, use ur"" to prefix the regex and u"" to prefix the test string and substitution.
    # REFERENCE: https://docs.aws.amazon.com/athena/latest/ug/application-load-balancer-logs.html#create-alb-table
    regex = r"([^ ]*) ([^ ]*) ([^ ]*) ([^ ]*):([0-9]*) ([^ ]*)[:-]([0-9]*) ([-.0-9]*) ([-.0-9]*) ([-.0-9]*) (|[-0-9]*) (-|[-0-9]*) ([-0-9]*) ([-0-9]*) \"([^ ]*) ([^ ]*) (- |[^ ]*)\" \"([^\"]*)\" ([A-Z0-9-]+) ([A-Za-z0-9.-]*) ([^ ]*) \"([^\"]*)\" \"([^\"]*)\" \"([^\"]*)\" ([-.0-9]*) ([^ ]*) \"([^\"]*)\" ($|\"[^ ]*\")(.*)"

    matches = re.search(regex, line)
    res = { "foo": "bar" }
    if matches:
        for i, field in enumerate(fields):
            value = matches.group(i+1)
            if field == "redirect_url":
                value = value.replace('"', '')

            res[field] = value

            # print(i, field)
            # end = ", " if i < len(fields)-1 else "\n"
            # print("%s=\"%s\"" % (field, matches.group(i+1)), end=end)
    return res

if __name__ == "__main__":

    with open("foo.txt", 'r') as file:
        for line in file:
            result = parse_line(line)
            print(result)

            # # print(result)
            # for (key, value) in result.items() :
            #     print(key , " :: ", value )
            # #     print(key , " :: ", value )
