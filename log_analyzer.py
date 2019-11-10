#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""log analyzer"""
import gzip
import logging
import os
import re
import sys
from collections import namedtuple
from string import Template

from get_config import get_conf
from parser import get_config_name

conf = get_conf(get_config_name())
logging.basicConfig(level=logging.INFO,
                    format="[%(asctime)s] %(levelname).1s %(message)s",
                    datefmt="%Y.%m.%d %H:%M:%S",
                    filename=conf["LOGGING_FILE_NAME"])
LOG_ANALYZE_LOGGER = logging.getLogger("logger_parse")


def median(input_list):
    """getting median of list"""
    input_list_len = len(input_list)
    input_list_sorted = sorted(input_list)
    return (sum(input_list_sorted[input_list_len // 2 - 1:input_list_len // 2 + 1]) / 2.0,
            input_list_sorted[input_list_len // 2])[input_list_len % 2] if input_list_len else None


def get_last_file(log_dir):
    """getting last file in log_dir"""
    last_date = 0
    last_ext = ""
    last_filename = ""
    FileInfo = namedtuple('FileInfo', 'path date ext')
    file_mask = r"^nginx-access-ui\.(log-(\d{8})$|log-(\d{8}).gz$)"
    try:
        for file in os.listdir(log_dir):
            match = re.search(file_mask, file)
            if match:
                file_date = match.group(1).split("-")[1].split('.')
                if int(file_date[0]) > last_date:
                    last_date = int(file_date[0])
                    try:
                        last_ext = match.group(1).split('.')[1]
                    except:
                        last_ext = ''
                    last_filename = match.group(0)
    except:
        LOG_ANALYZE_LOGGER.error("No such directory %s", log_dir)
        return None

    if not last_filename:
        LOG_ANALYZE_LOGGER.info("no files to parse")
        return None

    LOG_ANALYZE_LOGGER.info("got last file")
    return FileInfo(os.path.join(os.path.dirname(__file__), log_dir, last_filename),
                    str(last_date), last_ext)


def gen_parse_log(file_info, fails_percent):
    """
    generator function that parse log file
    file_info - named tuple with log info
    returns list of dictionary
    """
    logging.info("parsing log %s started", file_info.path)
    url_time_re = re.compile(r'.*?(?:GET|POST)\s+(.*?)\s+.*?(\d+\.\d*)(?:$|\n|\r)')
    log_file = open(file_info.path, "r") if not file_info.ext else gzip.open(file_info.path, "r")

    fails = 0
    count = 0
    urls = {}
    all_time = 0

    for log_line in log_file:
        if not isinstance(log_line, str):
            log_line = log_line.decode()
        count += 1
        match = url_time_re.match(log_line)
        if match:
            if match.group(1).strip() in urls:
                urls[match.group(1).strip()].append(float(match.group(2)))
            else:
                urls[match.group(1).strip()] = [float(match.group(2))]
            all_time += float(match.group(2))
        else:
            fails += 1

    LOG_ANALYZE_LOGGER.info("%f fails", round(fails / count * 100, 2))

    if (fails / count * 100) > float(fails_percent):
        LOG_ANALYZE_LOGGER.error("can not parse file")
        return None

    log_file.close()
    res_list = []
    for url in urls:
        entries = urls[url]
        res_list.append(
            {"url": url,
             "count": len(entries),
             "count_perc": round(float(len(entries)) / float(count) * 100, 3),
             "time_avg": round(float(sum(entries)) / len(entries), 3),
             "time_max": round(max(entries), 3),
             "time_med": round(median(entries), 3),
             "time_perc": round(float(sum(entries)) / float(all_time) * 100, 3),
             "time_sum": round(sum(entries), 3),
             }
        )

    sorted_res = list(sorted(res_list, key=lambda string: string["time_sum"], reverse=True))
    for log_line in sorted_res:
        yield log_line


def save_report(res, pattern_name, file_name):
    """saving report file"""
    with open(pattern_name, "r") as template_file:
        rep_text = template_file.read()
    file_template = Template(rep_text)
    sub_template = file_template.safe_substitute(table_json=res)
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    with open(file_name, mode="w", encoding="UTF-8") as result_file:
        result_file.write(sub_template)


def main():
    """getting config
    parsing it
    saving results"""
    config_file = get_conf(get_config_name())
    if not config_file:
        sys.exit(1)
    log = get_last_file(config_file["LOG_DIR"])
    LOG_ANALYZE_LOGGER.info("we've got log file named %s", log.path)
    file_name = os.path.join(os.path.dirname(__file__), config_file['REPORT_DIR'],
                             "report-{}.html".format(log.date))
    if os.path.exists(file_name):
        LOG_ANALYZE_LOGGER.info("%s already exists", file_name)
        sys.exit()
    res = gen_parse_log(log, config_file['PERCENT_FAILS'])
    if not res:
        sys.exit(1)
    LOG_ANALYZE_LOGGER.info("log parsed")
    report = []
    for _ in range(int(config_file["REPORT_SIZE"])):
        try:
            report.append(next(res))
        except StopIteration:
            pass
    LOG_ANALYZE_LOGGER.info("report file name %s", file_name)

    if report:
        save_report(report, config_file['SAMPLE_FILE'], file_name)


if __name__ == "__main__":
    main()
