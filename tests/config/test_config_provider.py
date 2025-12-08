import pytest
import os 
import shutil
import sys 
import json
from basketball_stats_config.config.config_provider import SECRET_PREFIX
from basketball_stats_config.config.config_provider import ConfigProvider
from basketball_stats_config.secret.google_secret_provider import GoogleSecretProvider
class TestConfigProvider():
     
    def setup_method(self):
        self.config = {
            "secret": f"{SECRET_PREFIX}secret",
            "secret_list": [f"{SECRET_PREFIX}secret", f"{SECRET_PREFIX}secret", "1"],
            "secret_dict": {
                "secret": f"{SECRET_PREFIX}secret",
                "secret_list": [f"{SECRET_PREFIX}secret", f"{SECRET_PREFIX}secret", "1"],
                "secret_dict": {
                    "secret": f"{SECRET_PREFIX}secret",
                    "secret_list": [f"{SECRET_PREFIX}secret", f"{SECRET_PREFIX}secret", "1"]
                }
            }
        }

        self.secret_word = "secrret"
        self.expected_config = {
            "secret": self.secret_word,
            "secret_list": [self.secret_word, self.secret_word, "1"],
            "secret_dict": {
                "secret": self.secret_word,
                "secret_list": [self.secret_word, self.secret_word, "1"],
                "secret_dict": {
                    "secret": self.secret_word,
                    "secret_list": [self.secret_word, self.secret_word, "1"]
                }
            }
        }
        
        self.valid_key_simple = "valid_key_simple"
        self.config[self.valid_key_simple] = 1
        self.expected_config[self.valid_key_simple] = 1

        self.valid_key_multi_1 = "valid_key_multi"
        self.valid_key_multi_2 = "valid_key_multi_1"
        self.config[self.valid_key_multi_1] = {}
        self.config[self.valid_key_multi_1][self.valid_key_multi_2] = 2
        self.expected_config[self.valid_key_multi_1] = {}
        self.expected_config[self.valid_key_multi_1][self.valid_key_multi_2] = 2

        self.invalid_key = "asdf"

    @pytest.fixture
    def secret_provider(self, mocker):
        secret_provider = mocker.Mock(spec=GoogleSecretProvider)

        mocker.patch.object(
            secret_provider,
            'get_secret',
            return_value=self.secret_word
        )

        yield secret_provider

    @pytest.fixture 
    def subject(self, mocker, secret_provider):
        assert self.config is not None 
        
        subject = ConfigProvider(
            self.config, secret_provider=secret_provider
        )

        yield subject

    def test_init_raises_value_error_if_no_valid_config_provided(self, mocker):
        with pytest.raises(ValueError) as _:
            ConfigProvider()

    def test_init_sets_config_if_valid_config_provided(self, mocker, secret_provider):
        subject = ConfigProvider(self.config, secret_provider=secret_provider)
        assert subject._get_config() == self.expected_config

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

    def test_init_decorates_config_with_secrets(self, mocker, subject):
        assert subject._get_config() == self.expected_config

    def test_get_searches_for_all_provided_keys_in_current_app_config(self, mocker, subject):
        res = subject.get(self.valid_key_simple)
        assert res == self.config[self.valid_key_simple]

        res = subject.get(
            self.valid_key_multi_1, self.valid_key_multi_2
        )
        assert res == self.config[self.valid_key_multi_1][self.valid_key_multi_2]

    def test_get_throws_key_error_if_provided_key_does_not_exist(self, mocker, subject):
        with pytest.raises(KeyError) as _:
            subject.get(self.invalid_key)

    def test_is_secret_returns_true_if_value_is_secret_format(self, subject):
        secret_val = "secret://my_secret"
        assert subject.is_secret(secret_val) is True

    def test_is_secret_returns_false_if_value_is_not_in_secret_format(self, subject):
        secret_val = "secrets://my_secret"
        assert subject.is_secret(secret_val) is False

    def test_is_secret_returns_false_if_value_is_null(self, subject):
        secret_val = None
        assert subject.is_secret(secret_val) is False



