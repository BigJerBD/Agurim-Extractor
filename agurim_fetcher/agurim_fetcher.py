import argparse
import csv
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path

from progress.bar import Bar
from retry_decorator import retry

from webdriver import get_chrome_driver, create_fetcher

current_time = round(time.time())

"""
args parser configs
"""

parser = argparse.ArgumentParser(description='Agurim traffic data web fetcher',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("dst",
                    help="destination of the extracted files")

# # special use args
parser.add_argument("-u", "--url", default="http://mawi.wide.ad.jp/~agurim/detail.html",
                    help="url of agurim  API")
parser.add_argument("-p", "--pair_csv",
                    help="csv of begin and end time to use for the fetching")
parser.add_argument("--csv_dst", default=None,
                    help="destination for csv_converted files (if None -> uses the same destination as the txt file)")

# request arguments
parser.add_argument("-s", "--start_time", type=int, default=1360249200,
                    help="starting unix timestamp of data fetching")
parser.add_argument("-e", "--end_time", type=int, default=current_time - (current_time % 60),
                    help="ending unix timestamp of data fetching")
parser.add_argument("-i", "--interval", default="600",
                    help="intervals for each point (default is minimum interval)")
parser.add_argument("-d", "--duration", type=int, default=86400,
                    help="duration of a csv fetch")
parser.add_argument("-c", '--criteria', choices=['byte', 'packet'], default="byte",
                    help="data type")
parser.add_argument("-v", '--view', choices=['addr', 'proto'], default="proto",
                    help="view mode")
parser.add_argument("-n", '--nflows', default="9999",
                    help="maximum number of flow in the received csv")
# togglable
parser.add_argument("--show", action="store_true",
                    help="show the browser while extracting data")
parser.add_argument("--skip_retry", action="store_true",
                    help="show the browser while extracting data")
parser.add_argument("--skip_csv_conversion", action="store_true",
                    help="skips the conversion of the files into a csv format at the end of the extraction")

"""
logger configs
"""
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agurim_fetcher")

"""
Main Function
"""


def execute(args):
    logger.info("handling configuration")
    request_args = make_request_args(args)
    driver = get_chrome_driver(args.dst, show=args.show)
    fetcher = create_fetcher(args.url, driver)

    if args.pair_csv:
        timestep = list(csv.reader(open(args.pair_csv, "rt", encoding='ascii')))
    else:
        timestep = [(step, step + args.duration) for step in range(args.start_time, args.end_time, args.duration)]

    extract_from_agurim(fetcher, timestep, request_args, args)

    if not args.skip_csv_conversion:
        csv_conversion(args.dst, args.csv_dst or args.dst, len(timestep))


"""
Extraction from Agurim
"""


def make_request_args(args):
    return {
        "interval": args.interval,
        "duration": args.duration,
        "criteria": args.criteria,
        "view": args.view,
        "nflows": args.nflows
    }


def agurim_filename(begin, end):
    frmt = "%Y%m%d%H%M"
    begin, end = datetime.fromtimestamp(begin), datetime.fromtimestamp(end)
    return f"{begin.strftime(frmt)}to{end.strftime(frmt)}.txt"


def extract_from_agurim(fetcher, timestep, request_args, args):
    logger.info(f"Starting extraction (number of file {len(timestep)})")
    progress = Bar("File extraction Progress", max=len(timestep))

    @retry(FileNotFoundError, tries=3)
    def fetch_proc(begin, end):
        file_dst = Path(args.dst, agurim_filename(begin, end))
        logger.debug(f"extracting from {begin} to {end}")
        if file_dst.is_file():
            return

        fetcher.get({**request_args, "startTime": begin, "endTime": end})

        if not args.skip_retry and not file_dst.is_file:
            logger.info(f"{file_dst} is missing, retrying")
            raise FileNotFoundError(f"{file_dst} not found")

    # execution
    for begin_time, end_time in timestep:
        fetch_proc(begin_time, end_time)
        progress.next()


"""
Conversion of Agurim txt file to csv
"""


def csv_conversion(src, dst, nb_of_file):
    logger.info(f"Converting file to csv (number of file {nb_of_file})")
    progress = Bar("File Conversion Progress", max=nb_of_file)

    for file_name in os.listdir(src):
        file_path = Path(file_name)
        with open(Path(src, file_name)) as f:
            content = list(f.readlines())

        content = content[1:]
        header = "unix_timestamp," + ",".join(format_header(content.pop(0)))
        content = filter(lambda x: bool("".join(x.split())), content)

        with open(Path(dst, file_path.stem).with_suffix(".csv"), "w") as f:
            print(header, file=f)
            list(map(
                lambda line: print(line.replace(" ", ""), file=f, end=""),
                content)
            )

        progress.next()


def format_header(header):
    header = header.replace("# labels:", "")
    parts = header.split(",")
    yield from (
        re.sub(r"(\[[0-9 ]+\] )", "", part.strip(" ").strip("\n").strip('"'))
        for part in parts
    )


if __name__ == "__main__":
    execute(parser.parse_args())
