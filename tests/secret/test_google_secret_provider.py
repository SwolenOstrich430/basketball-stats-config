import pytest
from basketball_stats_config.secret.google_secret_provider import DEFAULT_ENCODING
from basketball_stats_config.secret.google_secret_provider import GoogleSecretProvider
from google.cloud.secretmanager import SecretManagerServiceClient

class TestGoogleSecretProvider():

    @pytest.fixture
    def subject(self, mocker):
        self.client = mocker.Mock(spec=SecretManagerServiceClient)

        mocker.patch.object(
            GoogleSecretProvider, 
            '_get_client',
            return_value=self.client 
        )
        mocker.patch.object(
            GoogleSecretProvider, 
            '_init_client',
            return_value=self.client
        )

        subject = GoogleSecretProvider()

        mocker.patch.object(
            subject, 
            '_get_formatted_secret_key',
            return_value=self.formatted_secret_name
        )

        yield subject

    def setup_method(self):
        self.secret = "secret"
        self.encoded_secret_value = "\xc3\xb1"
        self.secret_value = "\xc3\xb1"
        self.encoded_secret_value = self.secret_value.encode(DEFAULT_ENCODING)
        self.formatted_secret_name = "secret_formatted"

    def test_get_secret_raises_exception_if_unable_to_access_secret_version(
        self, mocker, subject
    ):
        mocker.patch.object(
            self.client, 
            'access_secret_version',
            side_effect=AttributeError
        )

        with pytest.raises(ValueError):
            subject.get_secret(self.secret)

    def test_get_secret_raises_value_error_if_secret_version_has_no_data(
        self, mocker, subject
    ):
        self.client.access_secret_version.return_value = None

        with pytest.raises(ValueError):
            subject.get_secret(self.secret)
 

    def test_get_secret_returns_decoded_secret_data_if_secret_version_has_data(
        self, mocker, subject
    ):
        payload_mock = mocker.Mock()
        payload_mock.payload = payload_mock
        payload_mock.data = payload_mock
        payload_mock.decode.return_value = self.secret_value
        
        self.client.access_secret_version.return_value = payload_mock

        assert subject.get_secret(self.secret) == self.secret_value

    def test_get_secret_decodes_payload_with_default_encoding(
        self, mocker, subject
    ):
        payload_mock = mocker.Mock()
        payload_mock.payload = payload_mock
        payload_mock.data = payload_mock
        payload_mock.decode.return_value = self.secret_value
        
        self.client.access_secret_version.return_value = payload_mock

        subject.get_secret(self.secret) 

        payload_mock.decode.assert_called_with(DEFAULT_ENCODING)

    def test_set_client_sets_the_client_if_current_client_is_null(
        self, mocker, subject
    ):
        mocker.patch.object(
            GoogleSecretProvider, 
            '_init_client',
            return_value=self.client
        )

        sub = GoogleSecretProvider()
        assert sub.client == self.client

    def test_create_secret_raises_if_the_raw_secret_cant_be_created(
        self, mocker, subject):
        mthd = mocker.patch.object(
            subject, 
            '_secret_exists', 
            return_value=False
        )

        self.client.create_secret.return_value = None

        with pytest.raises(AssertionError):
            subject.create_secret(self.secret, self.secret_value)
            mthd.assert_called_with(self.secret)
            self.client.create_secret.assert_called_with(self.secret)

    def test_create_secret_calls_raises_if_the_new_secret_version_not_same_value_as_provided(
        self, mocker, subject):
        mocker.patch.object(
            subject, 
            '_secret_exists', 
            return_value=True
        )
        mocker.patch.object(
            subject, 
            'get_secret',
            return_value="nope"
        )

        self.client.create_secret.return_value = None
        self.client.add_secret_version.return_value = None

        with pytest.raises(AssertionError):
            subject.create_secret(self.secret, self.secret_value)
            
            self.client.add_secret_version.assert_called_with({
                "parent": self.formatted_secret_name, 
                "payload": {"data": self.secret_value}
            })

    def test_create_secret_encodes_the_provided_secret_val_to_default_encoding(
        self, mocker, subject):
        mocker.patch.object(
            subject, 
            '_secret_exists', 
            return_value=True
        )
        mocker.patch.object(
            subject, 
            'get_secret',
            return_value=self.secret_value
        )
        mocker.patch.object(
            subject,
            '_disable_secret_versions',
            return_value=None
        )

        self.client.create_secret.return_value = None
        self.client.add_secret_version.return_value = None

        subject.create_secret(self.secret, self.secret_value)
        
        self.client.add_secret_version.assert_called_with(
            request={
                "parent": self.formatted_secret_name, 
                "payload": {"data": self.encoded_secret_value}
            }
        ) 

    def test_create_secret_returns_void_if_created_secret_val_equals_provided(
        self, mocker, subject):
        mocker.patch.object(
            subject, 
            '_secret_exists', 
            return_value=True
        )
        mocker.patch.object(
            subject, 
            'get_secret',
            return_value=self.secret_value
        )
        mocker.patch.object(
            subject,
            '_disable_secret_versions',
            return_value=None
        )

        self.client.create_secret.return_value = None
        self.client.add_secret_version.return_value = None

        res = subject.create_secret(self.secret, self.secret_value)
        assert res is None

    def test_delete_secret_does_nothing_if_secret_does_not_exist(self, mocker, subject):
        mthd = mocker.patch.object(
            subject, 
            '_secret_exists',
            return_value=False 
        )
        mocker.patch.object(
            subject, 
            '_get_formatted_secret_key',
            return_value=self.formatted_secret_name 
        )

        subject.delete_secret(self.secret)

        mthd.assert_called_with(self.formatted_secret_name)
        self.client.delete_secret.assert_not_called()

    def test_delete_secret_deletes_the_secret_if_it_exists(self, mocker, subject):
        mocker.patch.object(
            subject, 
            '_secret_exists',
            side_effect=[True, False] 
        )
        mocker.patch.object(
            subject, 
            '_get_formatted_secret_key',
            return_value=self.formatted_secret_name 
        )

        subject.delete_secret(self.secret)

        self.client.delete_secret.assert_called_with(
            request={"name": self.formatted_secret_name}
        )

    def test_delete_secret_uses_formatted_secret_name(self, mocker, subject):
        mthd1 = mocker.patch.object(
            subject, 
            '_secret_exists',
            side_effect=[True, False] 
        )
        mthd = mocker.patch.object(
            subject, 
            '_get_formatted_secret_key',
            return_value=self.formatted_secret_name 
        )

        subject.delete_secret(self.secret)

        mthd1.assert_called_with(self.formatted_secret_name)
        mthd.assert_called_with(self.secret)

    def test_delete_secret_raises_if_secret_still_exists_after_delete(self, mocker, subject):
        mocker.patch.object(
            subject, 
            '_secret_exists',
            side_effect=[True, False] 
        )
        mthd = mocker.patch.object(
            subject, 
            '_get_formatted_secret_key',
            return_value=self.formatted_secret_name 
        )

        subject.delete_secret(self.secret)

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
