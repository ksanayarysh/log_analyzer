import argparse


def create_parser():
    """adding arg -c, --conf for getting .ini file """
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--conf', default="config.ini")
    parser.add_argument('-m', '--mistakes', default=50)
    return parser


def get_max_fails():
    """getting mistakes count"""
    parser = create_parser()
    return parser.parse_args().mistakes


def get_config_name():
    """getting config name"""
    parser = create_parser()
    return parser.parse_args().conf
