import pytest

from app.service.config.config_provider import ConfigProvider

class TestConfigProvider():
     
    def setup_method(self):
        self.subject = ConfigProvider()
        self.config = {}
        
        self.valid_key_simple = "valid_key_simple"
        self.config[self.valid_key_simple] = 1

        self.valid_key_multi_1 = "valid_key_multi"
        self.valid_key_multi_2 = "valid_key_multi_1"
        self.config[self.valid_key_multi_1] = {}
        self.config[self.valid_key_multi_1][self.valid_key_multi_2] = 2

        self.invalid_key = "asdf"

    def test_get_searches_for_all_provided_keys_in_current_app_config(self, mocker):
        mocker.patch.object(
            self.subject, 
            '_get_config', 
            return_value=self.config
        )

        res = self.subject.get(self.valid_key_simple)
        assert res == self.config[self.valid_key_simple]

        res = self.subject.get(
            self.valid_key_multi_1, self.valid_key_multi_2
        )
        assert res == self.config[self.valid_key_multi_1][self.valid_key_multi_2]

    def test_get_throws_key_error_if_provided_key_does_not_exist(self, mocker):
        mocker.patch.object(
            self.subject, 
            '_get_config', 
            return_value=self.config
        )

        with pytest.raises(KeyError) as _:
            self.subject.get(self.invalid_key)

