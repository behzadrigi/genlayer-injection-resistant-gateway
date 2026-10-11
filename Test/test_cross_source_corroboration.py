import json
import pytest
from genlayer_py import create_client, create_account
from genlayer_py.chains import localnet

CONTRACT_ADDRESS = "0x506dEC231a78F1e0BE02E2Fe0115928cA709662f"  # Studio

# These tests assume the Studio state from the recorded run: claims 0 (python.org),
# 1 (w3schools.com) and 3 (python.org) are reviewed SUPPORTED with the same text,
# claim 4 is still pending, and the pair (0, 1) has been corroborated.


@pytest.fixture(scope="module")
def client():
    return create_client(chain=localnet, account=create_account())


def _write(client, fn, args):
    tx = client.write_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args, value=0)
    return client.wait_for_transaction_receipt(transaction_hash=tx, status="ACCEPTED")


def _read(client, fn, args=None):
    return client.read_contract(address=CONTRACT_ADDRESS, function_name=fn, args=args or [])


def test_two_distinct_ids_required(client):
    with pytest.raises(Exception, match="Must provide two distinct claim ids"):
        _write(client, "corroborate", [0, 0])


def test_missing_claim_rejected(client):
    with pytest.raises(Exception, match="Claim B not found"):
        _write(client, "corroborate", [0, 999])


def test_unreviewed_claim_rejected(client):
    with pytest.raises(Exception, match="Claim B has not been reviewed yet"):
        _write(client, "corroborate", [0, 4])


def test_same_domain_rejected(client):
    with pytest.raises(Exception, match="Sources must come from independent domains"):
        _write(client, "corroborate", [0, 3])


def test_corroborated_pair_and_no_repeat(client):
    data = json.loads(_read(client, "get_corroboration_data", [0]))
    assert data["status"] == "CORROBORATED"
    assert {data["domain_a"], data["domain_b"]} == {"python.org", "w3schools.com"}
    with pytest.raises(Exception, match="This pair has already been corroborated"):
        _write(client, "corroborate", [1, 0])
