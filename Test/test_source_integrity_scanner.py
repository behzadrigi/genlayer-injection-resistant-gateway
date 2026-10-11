import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0xD74259618a5e5022c4186342eD78b50B8A0828C5"  # Studio
GOOD = "https://www.python.org/about"
POISON = "https://gist.githubusercontent.com/behzadrigi/5dc494f79b96ae16c4abbfa7f0fc13a1/raw/8d403823159b3e91a307b6727e213d9918604bb2/poison.txt"


@pytest.fixture(scope="module")
def client():
    return create_client(chain=localnet, account=create_account())


def _write(client, fn, args):
    tx = client.write_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args, value=0)
    return client.wait_for_transaction_receipt(transaction_hash=tx, status="ACCEPTED")


def _read(client, fn, args=None):
    return client.read_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args or [])


def ensure_scanned(client, url):
    try:
        _write(client, "scan_source", [url])
    except Exception as e:
        assert "Already scanned" in str(e)


def test_invalid_url_rejected(client):
    with pytest.raises(Exception, match="Invalid source URL"):
        _write(client, "scan_source", ["not_a_url"])


def test_healthy_page_is_safe(client):
    ensure_scanned(client, GOOD)
    assert _read(client, "get_scan_status", [GOOD]) == "SAFE"


def test_cannot_scan_twice(client):
    ensure_scanned(client, GOOD)
    with pytest.raises(Exception, match="Already scanned"):
        _write(client, "scan_source", [GOOD])


def test_poisoned_page_is_suspicious(client):
    ensure_scanned(client, POISON)
    assert _read(client, "get_scan_status", [POISON]) == "SUSPICIOUS"


def test_unscanned_url_reports_not_scanned(client):
    assert _read(client, "get_scan_status", ["https://www.example.org/never-scanned"]) == "NOT_SCANNED"
