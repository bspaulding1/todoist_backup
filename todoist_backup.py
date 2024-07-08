#! /usr/bin/env python

# TODO: verify zip file integrity https://www.perplexity.ai/search/what-is-the-python-code-to-ver-OCVGtUmrR0y2899FJ4vZDQ
# TODO: handle API errors (unavailable, 503, etc.)

import os
import sys
import subprocess
import configparser
import datetime


# get variables from a configuration file using a python library
config = configparser.ConfigParser()
config.read('config.ini')
token = config.get('keys', 'token')
src_dir = config.get('directories', 'src')
dest_dir = config.get('directories', 'dest')
prefix = config.get('files', 'prefix')
retention_days = config.getint('dates', 'retention_days')
# create datetime object as cutoff date that is retention_days ago
cutoff = datetime.datetime.now() - datetime.timedelta(days=retention_days)
cutoff = cutoff.date()


def run_todoist_backup():
    # print('Running todoist backup')
    env = os.environ.copy()
    env['TODOIST_TOKEN'] = token
    subprocess.run(['python3', '-m', 'full_offline_backup_for_todoist', 'download'], cwd=src_dir, env=env)


# move files within the specified directory and with the specified prefix to another directory
def move_files(src_dir, dest_dir, prefix):
    if not os.path.exists(dest_dir):
        sys.exit('ERROR: Destination directory does not exist')

    # print('Moving files to destination directory')
    for file_name in os.listdir(src_dir):
        if file_name.startswith(prefix):
            src_path = os.path.join(src_dir, file_name)
            dest_path = os.path.join(dest_dir, file_name)
            os.rename(src_path, dest_path)


# delete files in directory whose file suffixes have date information older than specified date using date object
def delete_old_files(dest_dir, date):
    for file_name in os.listdir(dest_dir):
        if file_name.startswith(prefix):
            file_path = os.path.join(dest_dir, file_name)
            file_suffix = file_name.split('_')[-1]
            date_string = file_suffix.split('.')[0]
            file_date = datetime.datetime.strptime(date_string, '%Y-%m-%d %H%M%S').date()
            if file_date < date:
                # print(f'Deleting {file_name}')
                os.remove(file_path)


def main():
    run_todoist_backup()
    move_files(src_dir, dest_dir, prefix)
    delete_old_files(dest_dir, cutoff)


if __name__ == '__main__':
    main()