import os

GCP_PROJECT_ID_ENV_VAR = 'GOOGLE_CLOUD_PROJECT'
DEFAULT_PROJECT = "festive-tiger-469222-c0"

def get_gcp_project_id() -> str:
    return os.getenv(GCP_PROJECT_ID_ENV_VAR) or DEFAULT_PROJECT