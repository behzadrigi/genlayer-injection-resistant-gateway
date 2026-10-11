import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0x2276b99e6E5077D8c1B541486947C953abb5D771"  # Studio
SCANNER_ADDRESS = "0xD74259618a5e5022c4186342eD78b50B8A0828C5"  # Studio
CLAIM = "Python is a programming language"
GOOD = "https://www.python.org/about"
UNSCANNED = "https://www.nasa.gov"
POISON = "https://gist.githubusercontent.com/behzadrigi/5dc494f79b96ae16c4abbfa7f0fc13a1/raw/8d403823159b3e91a307b6727e213d9918604bb2/poison.txt"


@pytest.fixture(scope="module")
def client():
    return create_client(chain=localnet, account=create_account())


def _write(client, fn, args, address=CONTRACT_ADDRESS):
    tx = client.write_contract(address=address, function_name=fn, args=args, value=0)
    return client.wait_for_transaction_receipt(transaction_hash=tx, status="ACCEPTED")


def _read(client, fn, args=None):
    return client.read_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args or [])


def last_claim_id(client):
    return int(_read(client, "list_claims").split(",")[-1].split(":")[0])


def ensure_scanned(client, url):
    try:
        _write(client, "scan_source", [url], address=SCANNER_ADDRESS)
    except Exception as e:
        assert "Already scanned" in str(e)


def test_empty_claim_rejected(client):
    with pytest.raises(Exception, match="Claim cannot be empty"):
        _write(client, "submit_claim", ["", GOOD])


def test_invalid_url_rejected(client):
    with pytest.raises(Exception, match="Invalid source URL"):
        _write(client, "submit_claim", [CLAIM, "not_a_url"])


def test_unscanned_source_cannot_be_reviewed(client):
    _write(client, "submit_claim", [CLAIM, UNSCANNED])
    cid = last_claim_id(client)
    with pytest.raises(Exception, match="has not been integrity-scanned yet"):
        _write(client, "review_claim", [cid])


def test_poisoned_source_is_blocked(client):
    ensure_scanned(client, POISON)
    _write(client, "submit_claim", [CLAIM, POISON])
    cid = last_claim_id(client)
    with pytest.raises(Exception, match="Source failed the integrity scan"):
        _write(client, "review_claim", [cid])


def test_safe_source_is_reviewed_once(client):
    ensure_scanned(client, GOOD)
    _write(client, "submit_claim", [CLAIM, GOOD])
    cid = last_claim_id(client)
    _write(client, "review_claim", [cid])
    data = json.loads(_read(client, "get_claim_data", [cid]))
    assert data["verdict"] in ("SUPPORTED", "UNSUPPORTED")
    assert data["status"] == "REVIEWED"
    with pytest.raises(Exception, match="Already reviewed"):
        _write(client, "review_claim", [cid])


def test_review_nonexistent_claim(client):
    with pytest.raises(Exception, match="Claim not found"):
        _write(client, "review_claim", [999999])
