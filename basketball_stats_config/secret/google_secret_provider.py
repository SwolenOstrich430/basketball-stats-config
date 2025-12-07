import re 
from basketball_stats_config.secret.isecret_provider import ISecretProvider
from google.api_core.exceptions import NotFound
from google.cloud.secretmanager import SecretVersion
from google.cloud.secretmanager import SecretManagerServiceClient
from google.cloud.secretmanager_v1.types.resources import Secret
from basketball_stats_config.common.env import get_gcp_project_id

DEFAULT_ENCODING = "UTF-8"
DEFAULT_VERSION_NAME = "latest"

class GoogleSecretProvider(ISecretProvider):

    def __init__(self):
        self._set_client()

    # RIGHT NOW THIS IS ONLY GOING TO SUPPORT STRINGS 
    # IN THE FUTURE MAY BE NEED TO DO DYNAMIC TYPING 
    # OR AT LEAST SUPPORT DICTS/JSON
    # TODO: add retry logic with max_attempts and backoff
    def get_secret(self, secret_key: str) -> str:
        secret_version = None 
        
        try: 
            secret_version = self._get_client().access_secret_version(
                name=self._get_version_name(secret_key)
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
    
    def create_secret(self, secret_key: str, secret_val: str): 
        formatted_key = self._get_formatted_secret_key(secret_key)

        if not self._secret_exists(secret_key):
            self._get_client().create_secret(
                request={
                    "parent": self._get_parent(), 
                    "secret_id": secret_key, 
                    "secret": self._get_secret_config()
                }
            )
            assert self._secret_exists(secret_key)

        payload_bytes = secret_val.encode(DEFAULT_ENCODING)

        self._get_client().add_secret_version(
            request={
                "parent": formatted_key,
                "payload": {"data": payload_bytes},
            }
        )

        assert secret_val == self.get_secret(secret_key)

        self._disable_secret_versions(secret_key)

    def delete_secret(self, secret_key: str):
        formatted_key = self._get_formatted_secret_key(secret_key)

        if not self._secret_exists(formatted_key):
            return 
        
        self._get_client().delete_secret(
            request={"name": formatted_key}
        )

        assert not self._secret_exists(formatted_key)
    
    def _disable_secret_versions(self, secret_key: str):
        formatted_key = self._get_formatted_secret_key(secret_key)
        versions = self.client.list_secret_versions(
            request={"parent": formatted_key}
        )

        latest_version = None 
        latest_version_number = 0

        versions = list(filter(
            lambda vrs: vrs.state == SecretVersion.State.ENABLED, 
            versions
        ))

        if len(versions) <= 1:
            return 

        for version in versions:
            version_number = int(version.name.split('/')[-1])
            if version_number > latest_version_number:
                latest_version = version.name 
                latest_version_number = version_number

        if not latest_version:
            return 
        
        for version in versions:
            if version.name == latest_version:
                continue 
            
            self.client.disable_secret_version(
                request={"name": version.name}
            )

    def _secret_exists(self, secret_key: str) -> bool:
        try:
            self._get_secret_raw(secret_key)
            return True  
        except NotFound:
            return False 

    def _get_secret_raw(self, secret_key: str) -> Secret:
        formatted_name = self._get_formatted_secret_key(secret_key)

        return self._get_client().get_secret(
            request={"name": formatted_name}
        )
    
    def _version_has_data(
        self, 
        secret_version
    ) -> bool:
        return secret_version is not None and \
            secret_version.payload is not None and \
            secret_version.payload.data is not None and \
            hasattr(secret_version.payload.data, "decode")
    
    def _get_secret_config(self):
        return {"replication": {"automatic": {}}}
    
    def _get_version_name(self, secret_key: str, version: str = None) -> str:
        if version is None:
            version = DEFAULT_VERSION_NAME 

        formatted_key = self._get_formatted_secret_key(secret_key)
        return f"{formatted_key}/versions/{version}"
    
    def _get_formatted_secret_key(self, secret_key: str) -> str:
        if re.match("^projects\\/.*/secrets\\/", str(secret_key)):
            return secret_key

        return f"{self._get_parent()}/secrets/{secret_key}"
    
    def _get_parent(self):
        return f"projects/{get_gcp_project_id()}"
    
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
        # TODO: add test that client is actually set 
        self.client = client
    def _get_client(self) -> SecretManagerServiceClient:
        return None if not hasattr(self, 'client') else self.client
    
    def _init_client(self) -> SecretManagerServiceClient:
        return SecretManagerServiceClient()
    
            