"""tests"""
import os
import sys
import unittest
from _decimal import Decimal

from get_config import get_conf
from log_analyzer import get_last_file, gen_parse_log
from parser import create_parser, get_mistakes_count, get_config_name


class TestLog(unittest.TestCase):
    """tests for log analyzer"""
    def test_last_file(self):
        """test that last file info is getting correctly
        no files with another ext
        no files not matching template"""
        last_file_info = get_last_file("log")
        self.assertEqual(os.path.join(os.path.dirname(__file__), "log", "nginx-access-ui.log-20190630"),
                         last_file_info.path)
        self.assertEqual(last_file_info.ext, "")
        self.assertEqual(last_file_info.date, "20190630")

    def test_correct_count(self):
        """check that we got the correct number of lines"""
        conf = get_conf(get_config_name())
        if not conf:
            sys.exit(1)
        log = get_last_file(conf["LOG_DIR"])
        if log:
            gen_parsed_log = gen_parse_log(log)
            result_list = []
            for _ in range(int(conf['REPORT_SIZE'])):
                result_list.append(next(gen_parsed_log))
            self.assertEqual(len(result_list), int(conf['REPORT_SIZE']))

    def test_correct_filename(self):
        config = get_conf(get_config_name())
        file_name = os.path.join(os.path.dirname(__file__), config['LOG_DIR'],
                                 "report{}.html".format('20190630'))
        print(file_name)

    def test_conf(self):
        config = get_conf(get_config_name())
        print(config)

    def test_config_func(self):
        """check that config func works correctly"""
        config = get_conf(get_config_name())
        self.assertIsNotNone(config)
        self.assertEqual(config['REPORT_DIR'], "rep")
        self.assertEqual(int(config['REPORT_SIZE']), 25)

        config = get_conf("no_conf")
        self.assertIsNone(config)

    def test_mistakes_count(self):
        """check getting cl arguments"""
        mk = get_mistakes_count()
        self.assertEqual(mk, 50)

    def test_config_name(self):
        """check getting cl arguments"""
        cn = get_config_name()
        self.assertEqual(cn, "config.ini")

