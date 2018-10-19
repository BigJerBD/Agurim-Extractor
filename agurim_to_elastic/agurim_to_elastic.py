import argparse
import itertools
import os
from pathlib import Path

import ndjson
from elasticsearch import Elasticsearch, helpers
from progress.bar import Bar

from agurim_csv_parsing import parse_agurim_file
from data_elastic_generation import elastic_ndjson_generator, elastic_json_query_generator

ELASTIC_TAG = "elastic"
NDJSON_TAG = "ndjson"
BOTH_TAG = "both"

parser = argparse.ArgumentParser(description='Transfer a folder of agurim csv to an elasticsearch database',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)

parser.add_argument("src", help="path to the agurim csv file folder")
parser.add_argument("output_type", choices=[ELASTIC_TAG, NDJSON_TAG, BOTH_TAG],
                    help="write output type")

parser.add_argument("--ndjson_dst", help="location to write ndjson")

parser.add_argument("--index", default="", help="index where to put data in elastic")
parser.add_argument("--type", default="", help="document type to be used with those data")
parser.add_argument("--host", default="localhost", help="host to the elasticsearch url")
parser.add_argument("--port", default="9200", help="host to the elasticsearch url")
parser.add_argument("--chunk_size", default=3000, help="chunk size for every bulk transaction")
# todo  add togglable option : --no_id, --no_progressbar
parser.add_argument("--no_progressbar", action="store_true",
                    help="toggle off progress bar")
parser.add_argument("--no_id", action="store_true",
                    help="toggle off datapoint ids")

"""
util functions
"""


def grouper(n, iterable):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk


def parse_agurim_files(file_paths, no_progressbar=False, *args, **kwargs):
    if no_progressbar:
        for file in file_paths:
            yield from parse_agurim_file(file, *args, **kwargs)
    else:
        progress = Bar("number_of_file_processed", max=len(file_paths))
        for file in file_paths:
            yield from parse_agurim_file(file, *args, **kwargs)
            progress.next()


"""
execution
"""


def execute():
    args = parser.parse_args()
    files = list(Path(args.src, file) for file in os.listdir(args.src) if file.endswith('.csv'))

    el_jsons = itertools.chain(parse_agurim_files(files))
    nd_jsons = itertools.chain(parse_agurim_files(files))

    if args.output_type in [NDJSON_TAG, BOTH_TAG]:
        print("Writing data in a ndjson file")
        write_in_ndjson(nd_jsons, args)

    if args.output_type in [ELASTIC_TAG, BOTH_TAG]:
        print("Writing data in elasticsearch")
        write_in_elastic(el_jsons, args)


def write_in_ndjson(jsons, args):
    result_ndjsons = elastic_ndjson_generator(jsons, doc_type=args.type, index=args.index, no_id=args.no_id)
    with open(args.ndjson_dst, 'w') as f:
        ndjson.dump(result_ndjsons, f)


def write_in_elastic(jsons, args):
    json_queries = elastic_json_query_generator(jsons, doc_type=args.type, index=args.index, no_id=args.no_id)
    es = Elasticsearch(hosts=[
        {"host": args.host, "port": args.port}
    ])
    for chunk in grouper(args.chunk_size, json_queries):
        helpers.bulk(es, chunk)


if __name__ == "__main__":
    execute()
