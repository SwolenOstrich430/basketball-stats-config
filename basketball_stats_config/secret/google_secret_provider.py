from basketball_stats_config.secret.isecret_provider import ISecretProvider
from google.cloud.secretmanager import SecretManagerServiceClient
# from common.env import get_gcp_project_id

DEFAULT_ENCODING = "UTF-8"

class GoogleSecretProvider(ISecretProvider):

    def __init__(self):
        self.client = self._set_client()

     # RIGHT NOW THIS IS ONLY GOING TO SUPPORT STRINGS 
    # IN THE FUTURE MAY BE NEED TO DO DYNAMIC TYPING 
    # OR AT LEAST SUPPORT DICTS/JSON
    # TODO: add retry logic with max_attempts and backoff
    def get_secret(self, secret_key: str) -> str:
        secret_version = None 
        
        try: 
            secret_version = self._get_client().access_secret_version(
                name=secret_key
            )
        except Exception as e:
            raise ValueError("Unable to access secret version " + \
                f"for key: {secret_key}. Error: {str(e)}")
        
        if self._version_has_data(secret_version):
            secret_version = secret_version.payload.data.decode(
                DEFAULT_ENCODING
            )
        else: 
            raise ValueError(
                f"Secret version has no data for key: {secret_key}"
            )
        
        return secret_version
    
    def _version_has_data(
        self, 
        secret_version
    ) -> bool:
        return secret_version is not None and \
            secret_version.payload is not None and \
            secret_version.payload.data is not None and \
            hasattr(secret_version.payload.data, "decode")
    
    def _set_client(self) -> SecretManagerServiceClient:
        client = self._get_client()
        # can't use None in isinstance (TypeError)
        if client is None or not isinstance(
            client, SecretManagerServiceClient
        ):
            client = self._init_client()
        # TODO: need to handle later -- currently can't find a check for this
        # elif client.is_expired():
        #     client = self._init_client()
        
        return client

    def _get_client(self) -> SecretManagerServiceClient:
        return self.client
    
    def _init_client(self) -> SecretManagerServiceClient:
        return SecretManagerServiceClient()
    
            