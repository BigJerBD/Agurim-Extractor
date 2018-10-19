import csv
import re
import string
from enum import Enum


class DataType(Enum):
    IP = 0
    PROTO = 1


def parse_agurim_file(file, datatype=DataType.PROTO, *args, **kwargs):
    """ file parsing method
    :param datatype:
    :param file:
    :return:
    """
    for point in iter_file_point(file, *args, **kwargs):

        if point["header"] != "TOTAL":
            # merge the point coordinate with the header information for each header info
            yield from (
                _json_merge(
                    part,
                    timestamp=point["timestamp"],
                    value=float(point["value"]) * percent)
                for percent, part in _split_header_subparts(point["header"], datatype)
            )


def iter_file_point(file, delimiter=",", quotechar=None):
    """iterator that iterate on cell of
    :param file:
    :param delimiter:
    :param quotechar:
    :return iterator
    """
    with open(file, "r") as f:
        reader = csv.reader(f, delimiter=delimiter, quotechar=quotechar)
        header, *rows = reader
        corner, *header = header
        for row in rows:
            timestamp, *points = row
            for column, value in zip(header, points):
                yield {
                    "timestamp": timestamp,
                    "header": column.strip(" "),
                    "value": value
                }


def _split_header_subparts(header, datatype=DataType.PROTO):
    parts = re.findall(r"([^%]+%) *", header)
    main_part, *sub_parts = parts
    sub_parts = [prt_str.replace("[", "").replace("]", "") for prt_str in sub_parts]

    main_extract = _extract_ip_info if datatype == DataType.IP else _extract_port_info
    sub_extract = _extract_ip_info if main_extract != _extract_ip_info else _extract_ip_info

    _, main_info = main_extract(main_part)
    for sub_part in sub_parts:
        sub_percent, sub_info = sub_extract(sub_part)
        yield sub_percent, _json_merge(main_info, sub_info)

    if not sub_parts:
        yield 1., main_info


"""
Data Generation
"""


def _extract_port_info(part):
    info, percent = part.split(" ")
    protocol, src, dst = info.split(":")
    return _percent2float(percent), {
        "port_string": info,
        "protocol": protocol,
        "port_src": src,
        "port_dst": dst
    }


def _extract_ip_info(part):
    src_ip, dst_ip, percent = part.split(" ")
    percent = _percent2float(percent)

    if any(c in string.ascii_lowercase for c in src_ip):
        return percent, {
            "ip_string": f"{src_ip} {dst_ip}",
            "ipv6_src": src_ip, "ipv6_dst": dst_ip,
            "ipv4_src": "", "ipv4_dst": "",
        }
    else:
        return percent, {
            "ip_string": f"{src_ip} {dst_ip}",
            "ipv6_src": "", "ipv6_dst": "",
            "ipv4_src": src_ip, "ipv4_dst": dst_ip,
        }


def _json_merge(*dicts, **args):
    result_json = {}
    for dct in dicts:
        result_json = {**result_json, **dct}
    return {**result_json, **args}


def _percent2float(percent):
    return float(percent.strip("%")) / 100
