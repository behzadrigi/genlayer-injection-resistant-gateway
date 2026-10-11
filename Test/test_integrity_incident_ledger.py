import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0xD883AB591d2cd208122C28402530dB9D12375535"  # Studio
GOOD = "https://www.python.org/about"
UNSCANNED = "https://www.nasa.gov"
POISON = "https://gist.githubusercontent.com/behzadrigi/5dc494f79b96ae16c4abbfa7f0fc13a1/raw/8d403823159b3e91a307b6727e213d9918604bb2/poison.txt"


@pytest.fixture(scope="module")
def client():
    return create_client(chain=localnet, account=create_account())


def _write(client, fn, args):
    tx = client.write_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args, value=0)
    return client.wait_for_transaction_receipt(transaction_hash=tx, status="ACCEPTED")


def _read(client, fn, args=None):
    return client.read_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args or [])


def test_unscanned_source_cannot_be_logged(client):
    with pytest.raises(Exception, match="Source has not been scanned yet"):
        _write(client, "record_incident", [UNSCANNED])


def test_safe_source_cannot_be_logged(client):
    with pytest.raises(Exception, match="Only SUSPICIOUS sources can be logged as incidents"):
        _write(client, "record_incident", [GOOD])


def test_poisoned_source_is_logged_once(client):
    try:
        _write(client, "record_incident", [POISON])
    except Exception as e:
        assert "Already logged" in str(e)
    data = json.loads(_read(client, "get_incident_data", [0]))
    assert data["status"] == "LOGGED"
    assert data["scan_requester"] != "" and data["reported_by"] != ""
    assert POISON.split("/")[2] in _read(client, "list_incidents")
    with pytest.raises(Exception, match="Already logged"):
        _write(client, "record_incident", [POISON])
