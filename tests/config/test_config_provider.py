import pytest
import os 
import shutil
import sys 
import json
from basketball_stats_config.config.config_provider import ConfigProvider

class TestConfigProvider():
     
    def setup_method(self):
        self.config = {}
        
        self.valid_key_simple = "valid_key_simple"
        self.config[self.valid_key_simple] = 1

        self.valid_key_multi_1 = "valid_key_multi"
        self.valid_key_multi_2 = "valid_key_multi_1"
        self.config[self.valid_key_multi_1] = {}
        self.config[self.valid_key_multi_1][self.valid_key_multi_2] = 2

        self.invalid_key = "asdf"
        self.subject = ConfigProvider(self.config)

    def test_init_raises_value_error_if_no_valid_config_provided(self, mocker):
        with pytest.raises(ValueError) as _:
            ConfigProvider()

    def test_init_sets_config_if_valid_config_provided(self, mocker):
        subject = ConfigProvider(self.config)
        assert subject._get_config() == self.config

    def test_init_sets_config_from_file_if_valid_config_file_provided(self, mocker):
        mock_config = {
            self.valid_key_simple: 1
        }

        other_package_name = "other_package"
        parent_dir = os.path.dirname(os.path.dirname(__file__))
        package_dir = os.path.join(parent_dir, other_package_name)

        try:
            os.makedirs(package_dir, exist_ok=True)
            file_name = os.path.join(package_dir, 'file.txt')    
            f = open(os.path.join(package_dir, '__init__.py'), 'w')
            f.close()

            with open(file_name, 'w') as file:
                file.write(json.dumps(mock_config))

            sys.path.append(parent_dir)
            subject = ConfigProvider(package=other_package_name, config_file=file_name)
            assert subject._get_config() == mock_config
        finally:
            shutil.rmtree(package_dir)

    def test_get_searches_for_all_provided_keys_in_current_app_config(self, mocker):
        res = self.subject.get(self.valid_key_simple)
        assert res == self.config[self.valid_key_simple]

        res = self.subject.get(
            self.valid_key_multi_1, self.valid_key_multi_2
        )
        assert res == self.config[self.valid_key_multi_1][self.valid_key_multi_2]

    def test_get_throws_key_error_if_provided_key_does_not_exist(self, mocker):
        with pytest.raises(KeyError) as _:
            self.subject.get(self.invalid_key)

