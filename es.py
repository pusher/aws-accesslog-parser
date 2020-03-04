import hashlib
# from datetime import datetime
# from datetime import datetime, date
from elasticsearch import Elasticsearch
import os


def predicablehash(*input):
    """
    returns a predicable hash of whatever the input string is
    """
    foo = str(input)
    hash_object = hashlib.md5(foo.encode())
    return(hash_object.hexdigest())


def newElasticConnect():
    elasticHost = os.getenv("ELASTIC_HOST", default="localhost")
    elasticPort = int(os.getenv("ELASTIC_PORT", default="9200"))
    elasticScheme = os.getenv("ELASTIC_PREFIX", default="http")

    try:
        conn = Elasticsearch(
            [elasticHost],
            scheme=elasticScheme,
            port=elasticPort,
            verify_certs=None,
            # sniff before doing anything
            sniff_on_start=True,
            # refresh nodes after a node fails to respond
            sniff_on_connection_fail=True,
            # and also every 60 seconds
            sniffer_timeout=60
        )
        # print("connected to elastic {}".format(elasticHost))
        return conn


    except Exception as ex:
        print("Error: {}".format(ex))

