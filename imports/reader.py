#!/bin/python3

import os, tempfile, shutil, zipfile, configparser
from distutils.util import strtobool
from gi.repository import GLib
from pathlib import Path

class ConfigReader:
    def __init__(self, config_file=None, access_rights=0o755):
        self.access_rights = access_rights
        self.general_section = 'DEFAULT'
        self._set_config_dir()
        self._set_config_file(config_file)
        self._set_config()

    def _set_config_dir(self):
        self.config_dir = os.path.join(GLib.get_user_config_dir(), 'snr/')
        if not os.path.exists(self.config_dir):
            try:
                os.mkdir(self.config_dir, self.access_rights)
            except OSError:
                print ("Creation of the directory %s failed" % self.config_dir)

    def _set_config_file(self, config_file):
        if not config_file:
            self.config_file = os.path.join(self.config_dir + 'config.ini')

    def _set_config(self):
        self.config = configparser.ConfigParser()
        if os.path.isfile(self.config_file):
            self.config.read(self.config_file)
        else:
            self.config[self.general_section] = {
                'dark_mode': 'on',
                'highlight': 'on',
                'horizontal_padding': '2',
                'vertical_padding': '2'
            }
            with open(self.config_file, 'w') as f:
                self.config.write(f)

    def get_dark_mode(self):
        return bool(strtobool(self.config[self.general_section]['dark_mode']))

    def get_highlight(self):
        return bool(strtobool(self.config[self.general_section]['highlight']))

    def get_horizontal_padding(self):
        return int(self.config[self.general_section]['horizontal_padding'])

    def get_vertical_padding(self):
        return int(self.config[self.general_section]['vertical_padding'])

class FileReader:
    def __init__(self, file_path, path='/tmp/reader', access_rights=0o755):
        self.path = path
        self.file_path = file_path
        self.access_rights = access_rights
        self.content_list = []
        self.create_temp_dir()
        self.unzip_file()

    def create_temp_dir(self):
        if not os.path.exists(self.path):
            try:
                os.mkdir(self.path, self.access_rights)
            except OSError:
                print ("Creation of the directory %s failed" % self.path)
        else:
            for filename in os.listdir(self.path):
                file_path = os.path.join(self.path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except OSError as e:
                    print('Failed to delete %s, because of %s' % (file_path, e))

    def unzip_file(self):
        with zipfile.ZipFile(self.file_path, 'r') as zip_ref:
            zip_ref.extractall(self.path)

    def get_content_list(self):
        for path in Path(self.path).rglob('*.html'):
            self.content_list.append(str(path))
        self.content_list.sort()
        return self.content_list

    def get_toc_file(self):
        for path in Path(self.path).rglob('*.ncx'):
            return str(path)

    def get_content_file(self):
        for path in Path(self.path).rglob('*.opf'):
            return str(path)

    def get_directory_path(self, toc_path):
        return toc_path[:toc_path.rfind('/')]
