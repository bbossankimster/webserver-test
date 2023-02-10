
from .json_files import read_json, write_json
from .default_conf import DEFAULTS


class WtestSettings:
    def __init__(self, config_path) -> None:
        self.config_path = config_path
        self.is_default = True
        self.read_config()

    def load_deafaults(self):
        self.conf = DEFAULTS
        self.is_default = True
        write_json(self.config_path, DEFAULTS)

    def read_config(self):
        try:
            self.conf = read_json(self.config_path)
        except FileNotFoundError:
            self.load_deafaults()
        self._set_separate_attrs()
        if self.conf != DEFAULTS:
            self.is_default = False

    def input_from_console(self):
        new_conf = {}
        for key, val in self.conf.items():
            if type(val) == dict:
                new_val = {}
                for inner_key, inner_val in val.items():
                    new_inner_val = input(">>> Input '{}' (default '{}'):\n    ".format(inner_key, inner_val))
                    new_val[inner_key] = new_inner_val
                new_conf[key] = new_val
            else:
                new_val = input(">>> Enter2 {}:\n    ".format(key))
                new_conf[key] = new_val
        if new_conf != DEFAULTS:
            self.conf = new_conf
            write_json(self.config_path, self.conf)
            self.is_default = False

    def _set_separate_attrs(self):
        for key, val in self.conf.items():
            setattr(self, key, val)
