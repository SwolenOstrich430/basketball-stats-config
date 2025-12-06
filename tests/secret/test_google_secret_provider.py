import pytest
from basketball_stats_config.secret.google_secret_provider import DEFAULT_ENCODING
from basketball_stats_config.secret.google_secret_provider import GoogleSecretProvider
from google.cloud.secretmanager import SecretManagerServiceClient

class TestGoogleSecretProvider():

    def setup_method(self):
        self.secret = "secret"
        self.secret_value = "value"

    def test_get_secret_raises_exception_if_unable_to_access_secret_version(
        self, mocker
    ):
        client = mocker.Mock(spec=SecretManagerServiceClient)
        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value=client
        )

        mocker.patch.object(
            client, 
            'access_secret_version',
            side_effect=AttributeError
        )

        with pytest.raises(ValueError):
            sub = GoogleSecretProvider()
            sub.get_secret(self.secret)

    def test_get_secret_raises_value_error_if_secret_version_has_no_data(
        self, mocker
    ):
        client = mocker.Mock(spec=SecretManagerServiceClient)
        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value = client
        )

        client.access_secret_version.return_value = None

        with pytest.raises(ValueError):
            sub = GoogleSecretProvider()
            sub.get_secret(self.secret)
 

    def test_get_secret_returns_decoded_secret_data_if_secret_version_has_data(
        self, mocker
    ):
        client = mocker.Mock(spec=SecretManagerServiceClient)
        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value = client
        )

        payload_mock = mocker.Mock()
        payload_mock.payload = payload_mock
        payload_mock.data = payload_mock
        payload_mock.decode.return_value = self.secret_value
        
        client.access_secret_version.return_value = payload_mock

        sub = GoogleSecretProvider()
        assert sub.get_secret(self.secret) == self.secret_value

    def test_get_secret_decodes_payload_with_default_encoding(self, mocker):
        client = mocker.Mock(spec=SecretManagerServiceClient)
        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value = client
        )

        payload_mock = mocker.Mock()
        payload_mock.payload = payload_mock
        payload_mock.data = payload_mock
        payload_mock.decode.return_value = self.secret_value
        client.access_secret_version.return_value = payload_mock

        sub = GoogleSecretProvider()
        sub.get_secret(self.secret) 

        payload_mock.decode.assert_called_with(DEFAULT_ENCODING)

    def test_set_client_sets_the_client_if_current_client_is_null(self, mocker):
        client = mocker.Mock(spec=SecretManagerServiceClient)

        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value = None 
        )
        
        mocker.patch.object(
            GoogleSecretProvider, 
            '_init_client',
            return_value=client
        )

        subject = GoogleSecretProvider()
        assert subject.client == client

    def test_set_client_sets_the_client_if_current_client_is_not_a_secret_manager_service_client(
        self, mocker
    ):
        client = mocker.Mock(spec=SecretManagerServiceClient)

        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value = {} 
        )
        
        mocker.patch.object(
            GoogleSecretProvider, 
            '_init_client',
            return_value=client
        )

        subject = GoogleSecretProvider()
        assert subject.client == client

    

    # def test_set_client_sets_the_client_if_current_client_is_expired(
    #     self, mocker
    # ):
    #     client = mocker.Mock(spec=SecretManagerServiceClient)

    #     mocker.patch.object(
    #         GoogleSecretProvider, 
    #         '_get_client',
    #         return_value = client
    #     )
        
    #     mocker.patch.object(
    #         client,    
    #         'is_expired',
    #         return_value = True
    #     )

    #     mocker.patch.object(
    #         GoogleSecretProvider, 
    #         '_init_client',
    #         return_value=client
    #     )

    #     subject = GoogleSecretProvider()
    #     assert subject.client == client

    # def test_set_client_does_not_set_client_if_correct_type_and_not_expired(
    #     self, mocker
    # ):
    #     client = mocker.Mock(spec=SecretManagerServiceClient)
    #     client_1 = mocker.Mock(spec=SecretManagerServiceClient)

    #     mocker.patch.object(
    #         GoogleSecretProvider, 
    #         '_get_client',
    #         return_value = client
    #     )
        
    #     mocker.patch.object(
    #         client,    
    #         'is_expired',
    #         return_value = False
    #     )
        
    #     mocker.patch.object(
    #         GoogleSecretProvider, 
    #         '_init_client',
    #         return_value=client_1
    #     )

    #     subject = GoogleSecretProvider()
    #     assert subject.client == client
    #     assert subject.client != client_1
