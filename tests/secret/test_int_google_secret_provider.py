import uuid
from google.cloud.secretmanager import SecretManagerServiceClient
from basketball_stats_config.secret.google_secret_provider import GoogleSecretProvider

class TestGoogleSecretProvider():
    
    def setup_method(self):
        self.secrets = {}
        self.secrets[str(uuid.uuid4())] = str(uuid.uuid4())
        self.secrets[str(uuid.uuid4())] = str(uuid.uuid4())

        self.subject = GoogleSecretProvider()
        assert isinstance(
            self.subject._get_client(),
            SecretManagerServiceClient
        )

    def test_crud(self):
        new_val = None 

        for key, value in self.secrets.items():
            assert not self.subject._secret_exists(key)
            self.subject.create_secret(key, value)
            assert self.subject._secret_exists(key)
            
            found_value = self.subject.get_secret(key)
            assert found_value == value 

            new_val = str(uuid.uuid4())
            self.subject.create_secret(key, new_val)
            found_value = self.subject.get_secret(key)
            assert found_value == new_val 

            self.subject.delete_secret(key)
            assert not self.subject._secret_exists(key)

