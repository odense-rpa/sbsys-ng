import os

import pytest
from dotenv import load_dotenv

from sbsys import SbsysClient

load_dotenv()


@pytest.fixture
def client():
    base_url = os.environ.get("SBSYS_BASE_URL")
    token_url = os.environ.get("SBSYS_TOKEN_URL")
    client_id = os.environ.get("SBSYS_CLIENT_ID")
    client_secret = os.environ.get("SBSYS_CLIENT_SECRET")
    username = os.environ.get("SBSYS_USERNAME")
    password = os.environ.get("SBSYS_PASSWORD")

    required = {
        "SBSYS_BASE_URL": base_url,
        "SBSYS_TOKEN_URL": token_url,
        "SBSYS_CLIENT_ID": client_id,
        "SBSYS_CLIENT_SECRET": client_secret,
        "SBSYS_USERNAME": username,
        "SBSYS_PASSWORD": password,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        pytest.skip(f"Missing environment variables: {', '.join(missing)}")

    return SbsysClient(
        base_url=base_url,
        token_url=token_url,
        client_id=client_id,
        client_secret=client_secret,
        username=username,
        password=password,
    )
