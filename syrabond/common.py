import json
from datetime import datetime
import logging
from os import chdir, path

"""Common functions to be used in modules and classes of Syrabond."""


def log(line, log_type='info'):
    """Wrapper for logging. Writes line to log adding datetime."""
    time_string = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(time_string, line)
    if log_type == 'info':
        logging.info(' {} {}'.format(time_string, line))
    elif log_type == 'error':
        logging.error(' {} {}'.format(time_string, line))
    elif log_type == 'debug':
        logging.debug(' {} {}'.format(time_string, line))
    elif log_type == 'warning':
        logging.warning(' {} {}'.format(time_string, line))


def extract_config(file_name):
    # type: (str) -> dict
    """
    Opens file and extracting json to dict.
    :rtype: dict
    :param file_name: path to config file
    """
    try:
        f = open(path.join(confs_dir, file_name), 'r')
        items = json.loads(f.read())
        f.close()
    except Exception as e:
        log(f'Unable to open config file {file_name}: {e}', 'error')
        return {}
    return items


def rewrite_config(file_name, content):
    try:
        with open(confs_dir+file_name, 'w') as f:
             f.write(json.dumps(content, ensure_ascii=False, indent=4, sort_keys=True))
    except Exception as e:
        print(e)
        return False
    return True


logging_levels = {
    'CRITICAL': 50,
    'ERROR': 40,
    'WARNING': 30,
    'INFO': 20,
    'DEBUG': 10
}

working_dir = path.split(path.dirname(path.abspath(__file__)))[0]
chdir(working_dir)
confs_dir = working_dir
conf = extract_config('global.json')
log_file = path.join(working_dir, conf['log_file'])
confs_dir = path.join(working_dir, conf['confs_dir'])
logging.basicConfig(filename=log_file, level=logging_levels[conf['log_level']])
conf.clear()