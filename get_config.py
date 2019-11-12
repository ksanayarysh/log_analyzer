"""config funcs"""
import configparser
import logging
import os
import sys
import traceback


def get_conf(config_file_name):
    """getting config file
    if it doesn't exists, return None
    if it it, return merge of default config with file config,
    file config is more important
    if we can not parse config file return None
    """
    if not os.path.exists(config_file_name):
        logging.error("No such file %s", config_file_name)
        return None

    default_config = {
        "REPORT_SIZE": 1000,
        "REPORT_DIR": "reports",
        "LOG_DIR": "log",
        "LOGGING_FILE_NAME": None,
        "TEMPLATE_FILE": "log/report.html",
        "PERCENT_FAILS": 50
    }
    try:
        file_config = configparser.ConfigParser()
        file_config.read(config_file_name)
        config = dict()
        try:
            config['REPORT_DIR'] = file_config['config']['REPORT_DIR']
        except KeyError:
            config['REPORT_DIR'] = default_config['REPORT_DIR']
        try:
            config['LOG_DIR'] = file_config['config']['LOG_DIR']
        except KeyError:
            config['LOG_DIR'] = default_config['LOG_DIR']
        try:
            config['REPORT_SIZE'] = file_config['config']['REPORT_SIZE']
        except KeyError:
            config['REPORT_SIZE'] = default_config['REPORT_SIZE']
        try:
            config['LOGGING_FILE_NAME'] = file_config['config']['LOGGING_FILE_NAME']
        except KeyError:
            config['LOGGING_FILE_NAME'] = default_config['LOGGING_FILE_NAME']
        try:
            config['TEMPLATE_FILE'] = file_config['config']['TEMPLATE_FILE']
        except KeyError:
            config['TEMPLATE_FILE'] = default_config['TEMPLATE_FILE']
        try:
            config['PERCENT_FAILS'] = file_config['config']['PERCENT_FAILS']
        except KeyError:
            config['PERCENT_FAILS'] = default_config['PERCENT_FAILS']
        return config
    except Exception as e:
        logging.error("Can not parse config file %s",
                      traceback.format_exception(sys.exc_info()[0],
                                                 sys.exc_info()[1],
                                                 sys.exc_info()[2], )
                      )
        return None
